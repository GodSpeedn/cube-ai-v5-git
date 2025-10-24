
# =============================================================================
# ONLINE AGENT SERVICE WITH LANGCHAIN INTEGRATION
# =============================================================================



 # This service provides online model integration for manual agent workflows
# It uses LangChain for conversation tracking and online models (OpenAI, Anthropic, etc.)

import os
import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request

# Add git-integration to path for GitHub upload
sys.path.append(str(Path(__file__).parent.parent / "git-integration"))

# Try to import GitHub integration
try:
    from online_agent_github_integration import online_agent_github
    GITHUB_AVAILABLE = True
    logging.info("[OK] GitHub integration available")
except ImportError as e:
    GITHUB_AVAILABLE = False
    logging.warning(f"[WARN] GitHub integration not available: {e}")

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# LangChain imports for online models and conversation tracking
from langchain_openai import ChatOpenAI
from langchain_mistralai import ChatMistralAI
# Try to import Gemini, fallback gracefully if not available
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: Gemini integration not available. Install with: pip install langchain-google-genai google-generativeai")
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# Removed unused imports: RunnableWithMessageHistory, PromptTemplate, StreamingStdOutCallbackHandler, CallbackManager

# Database integration (reusing existing structure)
from database import SafeDatabaseIntegration, ConversationRequest, ConversationResponse

# =============================================================================
# CONFIGURATION
# =============================================================================

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Load API keys from keys.txt
try:
    from load_keys import load_keys_from_file
    load_keys_from_file()
    print("[OK] API keys loaded from keys.txt")
except ImportError:
    print("[WARN] load_keys.py not found, using environment variables only")
except Exception as e:
    print(f"[ERROR] Error loading keys.txt: {e}")

# Import API key manager for file-based key management
from health_monitoring.api_key_manager import APIKeyManager, APIProvider

# Initialize API key manager
api_key_manager = APIKeyManager()

# API Keys - Declare at module level first
OPENAI_API_KEY: Optional[str] = None
MISTRAL_API_KEY: Optional[str] = None
GEMINI_API_KEY: Optional[str] = None

# API Keys - Get from file-based system; can be overridden per-request via headers
def get_api_key(provider: APIProvider) -> str:
    """Get API key from the file-based system"""
    return api_key_manager.get_key(provider)

def refresh_api_keys():
    """Refresh API keys from the file system"""
    global OPENAI_API_KEY, MISTRAL_API_KEY, GEMINI_API_KEY
    OPENAI_API_KEY = get_api_key(APIProvider.OPENAI)
    MISTRAL_API_KEY = get_api_key(APIProvider.MISTRAL)
    GEMINI_API_KEY = get_api_key(APIProvider.GEMINI)
    
    # Debug logging with key preview
    print(f"Refreshed API keys:")
    print(f"  OpenAI: {bool(OPENAI_API_KEY)} - {OPENAI_API_KEY[:15] if OPENAI_API_KEY else 'None'}...")
    print(f"  Mistral: {bool(MISTRAL_API_KEY)} - {MISTRAL_API_KEY[:10] if MISTRAL_API_KEY else 'None'}...")
    print(f"  Gemini: {bool(GEMINI_API_KEY)} - {GEMINI_API_KEY[:15] if GEMINI_API_KEY else 'None'}...")

# Initialize API keys
refresh_api_keys()

# Model configurations
ONLINE_MODEL_CONFIGS = {
    "gpt-4": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.3,
        "max_tokens": 4000,
        "streaming": True
    },
    "gpt-3.5-turbo": {
        "provider": "openai", 
        "model": "gpt-3.5-turbo",
        "temperature": 0.3,
        "max_tokens": 4000,
        "streaming": True
    },
    "gpt-4-turbo": {
        "provider": "openai",
        "model": "gpt-4-turbo-preview",
        "temperature": 0.3,
        "max_tokens": 4000,
        "streaming": True
    },
    "mistral-large": {
        "provider": "mistral",
        "model": "mistral-large-latest",
        "temperature": 0.3,
        "max_tokens": 4000,
        "streaming": True
    },
    "mistral-medium": {
        "provider": "mistral",
        "model": "mistral-medium-latest",
        "temperature": 0.3,
        "max_tokens": 4000,
        "streaming": True
    },
    "mistral-small": {
        "provider": "mistral",
        "model": "mistral-small-latest",
        "temperature": 0.3,
        "max_tokens": 4000,
        "streaming": False
    },
    "gemini-pro": {
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "temperature": 0.3,
        "max_tokens": 4000,
        "streaming": False
    },
    "gemini-2.5-flash": {
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "temperature": 0.3,
        "max_tokens": 4000,
        "streaming": False
    }
}

# Default model
DEFAULT_ONLINE_MODEL = "gemini-pro" if GEMINI_AVAILABLE else "mistral-small"

# =============================================================================
# DATA MODELS
# =============================================================================

class MessageType(Enum):
    """Message types for agent communication"""
    TASK = "task"
    DATA = "data" 
    REQUEST = "request"
    RESPONSE = "response"
    COORDINATION = "coordination"
    ERROR = "error"
    STATUS = "status"
    REVIEW = "review"

class OnlineAgentMessage(BaseModel):
    """Message structure for online agent communication"""
    id: str = Field(default_factory=lambda: f"msg_{datetime.now().timestamp()}")
    from_agent: str
    to_agent: str
    message_type: MessageType
    content: str
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)
    conversation_id: Optional[str] = None

class OnlineAgent(BaseModel):
    """Online agent configuration"""
    id: str
    name: str
    role: str
    model: str = DEFAULT_ONLINE_MODEL
    system_prompt: str = ""
    memory_enabled: bool = True
    conversation_id: Optional[str] = None

class OnlineAgentStatus(Enum):
    """Agent status tracking"""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"

class OnlineWorkflowRequest(BaseModel):
    """Request for running online agent workflow"""
    task: str
    agents: List[OnlineAgent]
    conversation_id: Optional[str] = None
    enable_streaming: bool = True

class OnlineWorkflowResponse(BaseModel):
    """Response from online agent workflow"""
    workflow_id: str
    status: str
    agents: Dict[str, OnlineAgentStatus]
    message_history: List[OnlineAgentMessage]
    total_messages: int
    conversation_id: str
    github_upload: Optional[Dict[str, Any]] = None

# =============================================================================
# LANGCHAIN AGENT MANAGER
# =============================================================================

class LangChainAgentManager:
    """Manages LangChain agents with conversation tracking"""
    
    def __init__(self):
        self.agents: Dict[str, 'OnlineAgentInstance'] = {}
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.workflow_history: Dict[str, List[OnlineAgentMessage]] = {}
        
    def create_agent(self, agent_config: OnlineAgent) -> 'OnlineAgentInstance':
        """Create a new LangChain agent instance"""
        agent = OnlineAgentInstance(agent_config)
        self.agents[agent_config.id] = agent
        return agent
    
    def get_agent(self, agent_id: str) -> Optional['OnlineAgentInstance']:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def create_conversation_memory(self, conversation_id: str) -> Dict[str, Any]:
        """Create conversation memory for tracking"""
        memory = {
            "messages": [],
            "conversation_id": conversation_id
        }
        self.conversations[conversation_id] = memory
        return memory
    
    def add_message_to_history(self, workflow_id: str, message: OnlineAgentMessage):
        """Add message to workflow history"""
        if workflow_id not in self.workflow_history:
            self.workflow_history[workflow_id] = []
        self.workflow_history[workflow_id].append(message)

# =============================================================================
# ONLINE AGENT INSTANCE
# =============================================================================

class OnlineAgentInstance:
    """Individual online agent with LangChain integration"""
    
    def __init__(self, config: OnlineAgent):
        self.config = config
        self.status = OnlineAgentStatus.IDLE
        self.llm = self._create_llm()
        self.memory = []
        self.github_upload_result = None  # Store GitHub upload result
        self.last_project_saved = None  # Store project info for manual upload
        
        if config.memory_enabled:
            self.memory = []
    
    def _create_llm(self):
        """Create LangChain LLM based on configuration"""
        model_config = ONLINE_MODEL_CONFIGS.get(self.config.model, ONLINE_MODEL_CONFIGS[DEFAULT_ONLINE_MODEL])
        
        if model_config["provider"] == "openai":
            if not OPENAI_API_KEY:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            
            return ChatOpenAI(
                model=model_config["model"],
                temperature=model_config["temperature"],
                max_tokens=model_config["max_tokens"],
                streaming=model_config["streaming"],
                api_key=OPENAI_API_KEY
            )
        
        elif model_config["provider"] == "mistral":
            if not MISTRAL_API_KEY:
                raise ValueError("Mistral API key not found. Set MISTRAL_API_KEY environment variable.")
            
            return ChatMistralAI(
                model=model_config["model"],
                temperature=model_config["temperature"],
                max_tokens=model_config["max_tokens"],
                streaming=model_config["streaming"],
                api_key=MISTRAL_API_KEY
            )
        
        elif model_config["provider"] == "gemini":
            if not GEMINI_AVAILABLE:
                raise ImportError("Gemini integration not available. Install with: pip install langchain-google-genai google-generativeai")
            if not GEMINI_API_KEY:
                raise ValueError("Gemini API key not found. Set GEMINI_API_KEY environment variable.")
            
            return ChatGoogleGenerativeAI(
                model=model_config["model"],
                temperature=model_config["temperature"],
                google_api_key=GEMINI_API_KEY
            )
        
        else:
            raise ValueError(f"Unsupported provider: {model_config['provider']}")
    
    async def process_message(self, message: OnlineAgentMessage, conversation_memory: Optional[Dict[str, Any]] = None) -> str:
        """Process incoming message and return response"""
        try:
            self.status = OnlineAgentStatus.WORKING
            
            # Prepare enhanced system prompt for coordination
            coordination_instructions = f"""
            IMPORTANT: You are {self.config.name}, a {self.config.role} in a multi-agent workflow.
            
            YOUR ROLE: {self.config.role}
            YOUR TASK: {self.config.system_prompt}
            
            WORKFLOW RULES:
            1. Stay STRICTLY within your role and expertise
            2. Complete your specific task completely
            3. When finished, clearly state what you've accomplished
            4. NEVER invent new tasks, roles, or agents
            5. NEVER continue the conversation beyond your responsibility
            6. ONLY respond to direct tasks assigned to you
            7. Do NOT add explanations unless specifically requested
            8. Do NOT delegate tasks if you're not the coordinator
            
            SPECIFIC INSTRUCTIONS BY ROLE:
            - COORDINATOR: You ONLY coordinate and delegate. You do NOT write ANY code.
              Your ONLY job:
              1. Break down the user's task into simple instructions
              2. Delegate to the appropriate agent (coder, tester, runner)
              3. After receiving results from an agent, delegate to the next agent if needed
              4. ONLY say "COORDINATION COMPLETE" when ALL agents have finished their work
              
              CRITICAL RULES:
              - DO NOT write code blocks (no ``` or CODE COMPLETE)
              - DO NOT include Python code in your response
              - ONLY give instructions to agents
              - Keep your message short and clear
              - ALWAYS check if tester needs to test the code after coder finishes
              - ONLY complete when ALL required agents have finished
              
              Example: "Please write a Python function that adds two numbers. Include error handling."
              NOT: "Here's the code: def add(a,b)..." (NEVER DO THIS!)
              
            - CODER: You ONLY write code. You do NOT coordinate or plan.
              Your ONLY job:
              1. Read the coordinator's instructions carefully
              2. Write COMPLETE, WORKING Python code
              3. Put your code in a code block: ```python\n<your code>\n```
              4. Say "CODE COMPLETE:" BEFORE the code block
              
              CRITICAL RULES:
              - ALWAYS include the full code in ```python ... ``` format
              - ALWAYS say "CODE COMPLETE:" before the code
              - Include imports, error handling, and comments
              - Make the code complete and runnable
              - Do NOT just say "CODE COMPLETE" without code
              
              Example response format:
              CODE COMPLETE:
              ```python
              def add(a, b):
                  return a + b
              ```
              
            - TESTER: You ONLY create test code. Do NOT run tests, plan, or coordinate.
              1. CREATE comprehensive test cases for the code provided by the coordinator
              2. Use pytest or unittest framework
              3. Include test functions (test_*), assertions, edge cases
              4. Test ALL functions and methods in the code
              5. Include edge cases: zero, negative numbers, large numbers, empty inputs, None values
              6. Test both valid inputs and invalid inputs (error conditions)
              7. Use descriptive test names that explain what is being tested
              8. Include multiple test functions for complex code
              9. For multi-function code, create separate test functions for each function
              10. Do NOT include the original code in your test file
              11. Do NOT use import statements for the code being tested - functions will be available
              12. When finished, say "TESTING COMPLETE:" followed by test code in ```python ... ```
              13. Return your test code to the coordinator
              IMPORTANT: Do NOT run the tests. Do NOT write the main code. Do NOT suggest improvements.
              
              EXAMPLE for complex code:
              If given code with add(), subtract(), multiply():
              - Create test_add() with multiple test cases
              - Create test_subtract() with multiple test cases  
              - Create test_multiply() with multiple test cases
              - Test edge cases for each function
              
            - RUNNER: You ONLY execute code and report results.
              1. Execute the code provided by the coordinator
              2. Capture all output (stdout, stderr, exceptions)
              3. Report execution status and results
              4. When done, say "EXECUTION COMPLETE: [summary]"
              5. Return execution results to the coordinator
              IMPORTANT: Do NOT write code. Do NOT test code. Do NOT suggest changes.
            
            CURRENT MESSAGE: {message.content}
            
            RESPOND ONLY WITH:
            1. Your specific contribution based on your role (code, tests, or results)
            2. Clear completion statement when done (CODE COMPLETE, TESTING COMPLETE, etc.)
            3. Nothing else - no greetings, no explanations, no suggestions, no continuation
            
            IF YOU ARE NOT THE COORDINATOR:
            - Complete your task and STOP
            - Return your result and WAIT for coordinator
            - Do NOT try to continue the conversation
            - Do NOT suggest what to do next
            """
            
            system_content = f"{coordination_instructions}"
            
            # Create messages for LangChain
            messages = [SystemMessage(content=system_content)]
            
            # Add conversation history if available
            if conversation_memory and "messages" in conversation_memory:
                messages.extend(conversation_memory["messages"])
            
            # Add current message with context
            message_context = f"Message from {message.from_agent}: {message.content}"
            messages.append(HumanMessage(content=message_context))
            
            # Get response from LLM
            response = await self.llm.agenerate([messages])
            response_content = response.generations[0][0].text
            
            # Add to memory
            if conversation_memory and "messages" in conversation_memory:
                conversation_memory["messages"].extend([
                    HumanMessage(content=message_context),
                    AIMessage(content=response_content)
                ])
            
            # Save code to file if this is a coder agent and code is generated
            logging.info(f"[DEBUG] Checking agent role: {self.config.role}")
            if "coder" in self.config.role.lower():
                logging.info(f"[DEBUG] Coder agent confirmed, checking for code...")
                # Check for various completion signals
                completion_signals = ["CODE COMPLETE:", "CODE COMPLETE", "```python", "```", "def ", "class ", "import "]
                has_completion_signal = any(signal in response_content for signal in completion_signals)
                
                # Also check if response contains Python code patterns
                python_patterns = ["def ", "class ", "import ", "if __name__", "print(", "return "]
                has_python_code = any(pattern in response_content for pattern in python_patterns)
                
                logging.info(f"[DEBUG] has_completion_signal: {has_completion_signal}, has_python_code: {has_python_code}")
                
                if has_completion_signal or has_python_code:
                    logging.info(f"[SEARCH] Coder agent detected code in response - calling _save_generated_code")
                    await self._save_generated_code(response_content, message.conversation_id, file_type="src")
                    logging.info(f"[DEBUG] _save_generated_code completed")
                else:
                    logging.info(f"[SEARCH] Coder agent response without code patterns: {response_content[:100]}...")
            else:
                logging.info(f"[DEBUG] Not a coder agent (role: {self.config.role})")
            
            # Save test code to file if this is a tester agent and test code is generated
            if "tester" in self.config.role.lower():
                logging.info(f"[TEST] Tester agent processing response...")
                # Check for test code patterns - expanded list
                test_signals = [
                    "TESTING COMPLETE:", "TESTING COMPLETE", "TEST COMPLETE",
                    "def test_", "class Test", 
                    "import pytest", "import unittest", 
                    "```python", "```",
                    "@pytest", "@unittest"
                ]
                has_test_signal = any(signal in response_content for signal in test_signals)
                
                # Also check if response contains test code patterns - expanded
                test_patterns = [
                    "def test_", "class Test", 
                    "assert ", "self.assert", "self.assertEqual",
                    "pytest", "unittest",
                    "test_case", "TestCase",
                    "def setUp", "def tearDown"
                ]
                has_test_code = any(pattern in response_content for pattern in test_patterns)
                
                logging.info(f"[TEST] Test signal detected: {has_test_signal}, Test code detected: {has_test_code}")
                
                if has_test_signal or has_test_code:
                    logging.info(f"[TEST] Tester agent detected test code - saving to file...")
                    await self._save_generated_code(response_content, message.conversation_id, file_type="tests")
                    logging.info(f"[TEST] Test file save completed")
                else:
                    logging.info(f"[TEST] Tester agent response without test code patterns: {response_content[:100]}...")
            
            self.status = OnlineAgentStatus.COMPLETED
            return response_content
            
        except Exception as e:
            self.status = OnlineAgentStatus.ERROR
            logging.error(f"Error processing message in agent {self.config.id}: {str(e)}")
            return f"Error: {str(e)}"
    
    async def _save_generated_code(self, response_content: str, conversation_id: str, file_type: str = "src"):
        """Save generated code to file and upload to GitHub - supports multi-file projects"""
        try:
            # Import file manager
            from file_manager import get_file_manager
            file_manager = get_file_manager()
            
            # Log GitHub status for debugging
            logging.info(f"[DEBUG] FileManager GitHub status: {file_manager.github_available}")
            if not file_manager.github_available:
                logging.warning("[WARN] GitHub not available - checking credentials")
                # Log environment variable status
                import os
                token_set = bool(os.environ.get('GITHUB_TOKEN'))
                user_set = bool(os.environ.get('GITHUB_USERNAME'))
                logging.info(f"[DEBUG] GITHUB_TOKEN set: {token_set}, GITHUB_USERNAME set: {user_set}")
            
            # Extract all code blocks from response (supports multiple files)
            code_blocks = self._extract_multiple_code_blocks(response_content)
            if not code_blocks:
                # Fallback to single code extraction
                code = self._extract_code_from_response(response_content)
                if not code:
                    logging.warning("No code found in response")
                    return
                code_blocks = [code]
            
            logging.info(f"[MULTIFILE] Found {len(code_blocks)} code block(s) to save")
            
            # Get task description from conversation context with better context
            task_description = self._get_task_description_from_context(conversation_id)
            
            # Save each code block
            saved_files = []
            for idx, code in enumerate(code_blocks, 1):
                # Enhance task description with agent context and file number
                file_type_label = "Test Code" if file_type == "tests" else "Source Code"
                if len(code_blocks) > 1:
                    enhanced_task_description = f"{task_description} - {file_type_label} Part {idx}/{len(code_blocks)} - Generated by {self.config.name} ({self.config.role})"
                else:
                    enhanced_task_description = f"{task_description} - {file_type_label} Generated by {self.config.name} ({self.config.role})"
                
                logging.info(f"[SEARCH] Saving {file_type_label.lower()} {idx}/{len(code_blocks)} from {self.config.name} ({self.config.role})")
                logging.info(f"[NOTE] Task: {enhanced_task_description}")
                logging.info(f"[FOLDER] File type: {file_type}")
                logging.info(f"[CHAT] Conversation ID: {conversation_id}")
                
                # Save code using advanced file manager
                result = file_manager.save_code(
                    code=code,
                    file_type=file_type,
                    conversation_id=conversation_id,
                    task_description=enhanced_task_description
                )
                
                if result.get("success"):
                    logging.info(f"[SAVE] Code {idx}/{len(code_blocks)} saved successfully: {result['filepath']}")
                    logging.info(f"[DIR] Project: {result['project_name']}")
                    saved_files.append(result['filepath'])
                    
                    # Store project info for manual upload (update with latest)
                    self.last_project_saved = {
                        "conversation_id": conversation_id,
                        "project_name": result['project_name'],
                        "filepath": result['filepath'],
                        "total_files": len(code_blocks)
                    }
                else:
                    error_msg = result.get('error', 'Unknown error')
                    logging.error(f"[ERROR] Failed to save code {idx}/{len(code_blocks)}: {error_msg}")
            
            # Log final summary
            if saved_files:
                logging.info(f"[INFO] Successfully saved {len(saved_files)} file(s) to project: {self.last_project_saved.get('project_name')}")
                logging.info(f"[INFO] Project ready for upload")
                
                # Log GitHub result
                if result.get("github_result", {}).get("status") == "pending":
                    logging.info("[INFO] Files saved - ready for manual GitHub upload")
                elif result.get("github_result", {}).get("status") == "github_not_available":
                    logging.info("[INFO] GitHub not available - code saved locally only")
                    logging.info("[TIP] To enable GitHub upload: Configure GitHub in the Git Integration tab")
            else:
                logging.error("[ERROR] No files were saved successfully")
            
        except Exception as e:
            logging.error(f"[ERROR] Error in _save_generated_code: {e}")
            # Fallback to simple file save
            try:
                code = self._extract_code_from_response(response_content)
                if code:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"code_{timestamp}.py"
                    filepath = Path("generated") / filename
                    filepath.parent.mkdir(exist_ok=True)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(code)
                    logging.info(f"[SAVE] Fallback save to: {filepath}")
                    
                    # Try to create a simple project structure
                    project_dir = Path("generated") / f"project_{timestamp}"
                    project_dir.mkdir(exist_ok=True)
                    (project_dir / "src").mkdir(exist_ok=True)
                    
                    # Move file to project structure
                    project_file = project_dir / "src" / filename
                    filepath.rename(project_file)
                    
                    # Create simple README
                    readme_content = f"""# AI Generated Code Project

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Conversation ID: {conversation_id}

## Files
- {filename} - Main code file

## Description
This code was generated by an AI agent workflow.
"""
                    with open(project_dir / "README.md", 'w', encoding='utf-8') as f:
                        f.write(readme_content)
                    
                    logging.info(f"[DIR] Created project structure: {project_dir}")
                    
            except Exception as fallback_error:
                logging.error(f"[ERROR] Fallback save also failed: {fallback_error}")
    
    def _get_task_description_from_context(self, conversation_id: str) -> str:
        """Extract task description from conversation context"""
        try:
            # Try to get the original task from workflow manager if available
            if hasattr(self, '_workflow_manager') and self._workflow_manager:
                workflow = self._workflow_manager.active_workflows.get(conversation_id.replace("manual_workflow_", ""))
                if workflow and workflow.get("message_history"):
                    # Look for the initial task message
                    for message in workflow["message_history"]:
                        if message.message_type.value == "task" and message.from_agent == "system":
                            return message.content[:100]  # Limit length
            
            # Fallback: try to get from conversation memory if available
            if hasattr(self, '_conversation_memory') and self._conversation_memory:
                messages = self._conversation_memory.get("messages", [])
                if messages:
                    # Look for the first human message which is usually the task
                    for msg in messages:
                        if hasattr(msg, 'content') and len(msg.content) > 10:
                            return f"Task: {msg.content[:80]}..."
            
            # Default description with agent context
            return f"AI Generated Code from {self.config.role} Agent"
        except Exception as e:
            logging.warning(f"Could not extract task context: {e}")
            return f"AI Generated Code from {self.config.role} Agent"
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract Python code from response with improved detection"""
        try:
            logging.info(f"[SEARCH] Extracting code from response: {response[:200]}...")
            
            # Clean the response first
            response = response.strip()
            
            # Look for code blocks with python specification
            if "```python" in response:
                start = response.find("```python") + 9
                end = response.find("```", start)
                if end != -1:
                    code = response[start:end].strip()
                    logging.info(f"[OK] Extracted Python code block: {len(code)} characters")
                    return code
            
            # Look for code blocks without language specification
            if "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                if end != -1:
                    code = response[start:end].strip()
                    # Check if it looks like Python code
                    if any(keyword in code for keyword in ["def ", "import ", "class ", "if __name__", "print(", "return "]):
                        logging.info(f"[OK] Extracted generic code block: {len(code)} characters")
                        return code
            
            # If no code blocks, check if the entire response is code
            python_keywords = ["def ", "import ", "class ", "print(", "return ", "if ", "for ", "while ", "try:", "except:", "finally:"]
            if any(keyword in response for keyword in python_keywords):
                logging.info(f"[OK] Extracted entire response as code: {len(response)} characters")
                return response.strip()
            
            # Try to extract code from mixed content (text + code)
            lines = response.split('\n')
            code_lines = []
            in_code_block = False
            
            for line in lines:
                # Skip empty lines and comments at the start
                if not line.strip() or line.strip().startswith('#'):
                    if not in_code_block:
                        continue
                
                # Check if line looks like Python code
                if any(keyword in line for keyword in ["def ", "import ", "class ", "if ", "for ", "while ", "try:", "except:", "finally:", "return ", "print("]):
                    in_code_block = True
                    code_lines.append(line)
                elif in_code_block and (line.strip() == "" or line.startswith("    ") or line.startswith("\t")):
                    # Continue code block (empty line or indented line)
                    code_lines.append(line)
                elif in_code_block and not line.strip():
                    # Empty line in code block
                    code_lines.append(line)
                elif in_code_block:
                    # End of code block
                    break
            
            if code_lines:
                code = '\n'.join(code_lines).strip()
                if len(code) > 10:  # Minimum code length
                    logging.info(f"[OK] Extracted code from mixed content: {len(code)} characters")
                    return code
            
            logging.warning(f"[ERROR] No code found in response")
            return ""
            
        except Exception as e:
            logging.error(f"Failed to extract code: {str(e)}")
            return ""
    
    def _extract_multiple_code_blocks(self, response: str) -> List[str]:
        """Extract multiple code blocks from response for multi-file projects"""
        try:
            logging.info(f"[MULTIFILE] Searching for multiple code blocks...")
            code_blocks = []
            
            # Look for all ```python code blocks
            start_marker = "```python"
            end_marker = "```"
            
            current_pos = 0
            while True:
                start = response.find(start_marker, current_pos)
                if start == -1:
                    break
                
                start += len(start_marker)
                end = response.find(end_marker, start)
                if end == -1:
                    break
                
                code = response[start:end].strip()
                if len(code) > 10:  # Minimum code length
                    code_blocks.append(code)
                    logging.info(f"[MULTIFILE] Found code block {len(code_blocks)}: {len(code)} characters")
                
                current_pos = end + len(end_marker)
            
            # If no ```python blocks, look for generic ``` blocks
            if not code_blocks:
                current_pos = 0
                while True:
                    start = response.find("```", current_pos)
                    if start == -1:
                        break
                    
                    # Skip if this is a closing marker
                    if start > 0 and response[start-1:start+3] == "```":
                        current_pos = start + 3
                        continue
                    
                    start += 3
                    # Skip language identifier if present
                    newline_pos = response.find('\n', start)
                    if newline_pos != -1 and newline_pos - start < 20:
                        start = newline_pos + 1
                    
                    end = response.find("```", start)
                    if end == -1:
                        break
                    
                    code = response[start:end].strip()
                    # Verify it looks like Python code
                    if len(code) > 10 and any(keyword in code for keyword in ["def ", "import ", "class ", "assert ", "test_"]):
                        code_blocks.append(code)
                        logging.info(f"[MULTIFILE] Found generic code block {len(code_blocks)}: {len(code)} characters")
                    
                    current_pos = end + 3
            
            logging.info(f"[MULTIFILE] Total code blocks found: {len(code_blocks)}")
            return code_blocks
            
        except Exception as e:
            logging.error(f"[MULTIFILE] Error extracting multiple code blocks: {e}")
            return []
    
    def get_status(self) -> OnlineAgentStatus:
        """Get current agent status"""
        return self.status

# =============================================================================
# ONLINE WORKFLOW MANAGER
# =============================================================================

class OnlineWorkflowManager:
    """Manages online agent workflows with LangChain integration"""
    
    def __init__(self):
        self.agent_manager = LangChainAgentManager()
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.db_integration = SafeDatabaseIntegration()
    
    async def run_workflow(self, request: OnlineWorkflowRequest) -> OnlineWorkflowResponse:
        """Run a complete workflow with online agents"""
        workflow_id = f"workflow_{datetime.now().timestamp()}"
        
        # Create conversation if needed (only for non-manual flows)
        conversation_id = request.conversation_id
        if conversation_id is None:  # Explicitly None/undefined - don't create DB conversation
            conversation_id = f"manual_workflow_{workflow_id}"  # Use internal ID only
        elif not conversation_id:  # Empty string - create DB conversation
            conversation_id = await self.db_integration.start_conversation(f"Online Workflow: {request.task}")
        
        # Initialize workflow
        self.active_workflows[workflow_id] = {
            "status": "running",
            "agents": {},
            "message_history": [],
            "conversation_id": conversation_id
        }
        
        # Create agents
        agents = {}
        for agent_config in request.agents:
            agent = self.agent_manager.create_agent(agent_config)
            agents[agent_config.id] = agent
            self.active_workflows[workflow_id]["agents"][agent_config.id] = OnlineAgentStatus.IDLE
        
        # Create conversation memory
        conversation_memory = self.agent_manager.create_conversation_memory(conversation_id)
        
        # Start workflow execution
        try:
            # Find coordinator agent or use first agent
            coordinator = next((agent for agent in agents.values() if "coordinator" in agent.config.role.lower()), 
                             list(agents.values())[0])
            
            # Send initial task to coordinator
            initial_message = OnlineAgentMessage(
                from_agent="system",
                to_agent=coordinator.config.id,
                message_type=MessageType.TASK,
                content=request.task,
                conversation_id=conversation_id
            )
            
            # Process workflow
            await self._execute_workflow(workflow_id, agents, initial_message, conversation_memory)
            
            # Update final status
            self.active_workflows[workflow_id]["status"] = "completed"
            
        except Exception as e:
            self.active_workflows[workflow_id]["status"] = "error"
            logging.error(f"Workflow error: {str(e)}")
        
        # Collect project info for manual upload option
        project_info = None
        for agent in agents.values():
            if hasattr(agent, 'last_project_saved') and agent.last_project_saved:
                project_info = agent.last_project_saved
                break  # Use the first saved project
        
        github_info = {
            "uploaded": False,
            "repo_url": None,
            "files_uploaded": 0,
            "project_info": project_info,  # Send project info to frontend
            "ready_for_upload": project_info is not None
        }
        
        if project_info:
            logging.info(f"[INFO] Project ready for manual upload: {project_info['project_name']}")
        
        # Return response
        return OnlineWorkflowResponse(
            workflow_id=workflow_id,
            status=self.active_workflows[workflow_id]["status"],
            agents={agent_id: agent.get_status() for agent_id, agent in agents.items()},
            message_history=self.active_workflows[workflow_id]["message_history"],
            total_messages=len(self.active_workflows[workflow_id]["message_history"]),
            conversation_id=conversation_id,
            github_upload=github_info
        )
    
    async def _execute_workflow(self, workflow_id: str, agents: Dict[str, OnlineAgentInstance], 
                              initial_message: OnlineAgentMessage, conversation_memory: Dict[str, Any]):
        """Execute the workflow step by step with multi-agent coordination"""
        current_message = initial_message
        max_iterations = 20
        iteration = 0
        agent_roles = {agent_id: agent.config.role.lower() for agent_id, agent in agents.items()}
        
        # Track agent completion status
        agent_completion = {agent_id: False for agent_id in agents.keys()}
        workflow_completed = False
        
        while iteration < max_iterations and not workflow_completed:
            # Add message to history
            self.active_workflows[workflow_id]["message_history"].append(current_message)
            self.agent_manager.add_message_to_history(workflow_id, current_message)
            
            # Save to database (only for non-manual workflows)
            if not current_message.conversation_id.startswith("manual_workflow_"):
                await self.db_integration.add_message_to_conversation(
                    current_message.conversation_id,
                    current_message.from_agent,
                    current_message.to_agent,
                    current_message.message_type.value,
                    current_message.content,
                    current_message.metadata
                )
            
            # Get target agent
            target_agent = agents.get(current_message.to_agent)
            if not target_agent:
                break
            
            # Update agent status
            self.active_workflows[workflow_id]["agents"][current_message.to_agent] = OnlineAgentStatus.WORKING
            
            # Process message
            response_content = await target_agent.process_message(current_message, conversation_memory)
            
            # Create response message and add to history with agent metadata
            response_message = OnlineAgentMessage(
                from_agent=current_message.to_agent,
                to_agent=current_message.from_agent,
                message_type=MessageType.RESPONSE,
                content=response_content,
                conversation_id=current_message.conversation_id,
                metadata={
                    "from_agent_role": target_agent.config.role,
                    "from_agent_name": target_agent.config.name,
                    "from_agent_model": target_agent.config.model_name,
                    "to_agent_role": agents.get(current_message.from_agent).config.role if agents.get(current_message.from_agent) else "unknown",
                    "to_agent_name": agents.get(current_message.from_agent).config.name if agents.get(current_message.from_agent) else "unknown"
                }
            )
            self.active_workflows[workflow_id]["message_history"].append(response_message)
            self.agent_manager.add_message_to_history(workflow_id, response_message)
            
            # Mark agent as completed for this iteration
            agent_completion[current_message.to_agent] = True
            
            # Check if workflow is complete based on agent roles and completion
            workflow_completed = self._check_workflow_completion(agent_roles, agent_completion, response_content)
            if workflow_completed:
                break
            
            # Only coordinator can delegate to other agents
            # All other agents return to coordinator
            if current_message.to_agent == "coordinator" or "coordinator" in agent_roles.get(current_message.to_agent, "").lower():
                # Coordinator delegates to next agent
                next_agent = self._get_next_agent(current_message.to_agent, agent_roles, agent_completion)
                if not next_agent:
                    # No more agents to process
                    workflow_completed = True
                    break
                
                # Create message to next agent
                next_message = OnlineAgentMessage(
                    from_agent=current_message.to_agent,
                    to_agent=next_agent,
                    message_type=MessageType.COORDINATION,
                    content=f"Task from coordinator: {response_content}",
                    conversation_id=current_message.conversation_id
                )
                current_message = next_message
            else:
                # Non-coordinator agents return result to coordinator
                coordinator_id = next((aid for aid, role in agent_roles.items() if "coordinator" in role.lower()), None)
                
                if coordinator_id and coordinator_id != current_message.to_agent:
                    # Send result back to coordinator
                    next_message = OnlineAgentMessage(
                        from_agent=current_message.to_agent,
                        to_agent=coordinator_id,
                        message_type=MessageType.RESPONSE,
                        content=f"Task completed. Result: {response_content}",
                        conversation_id=current_message.conversation_id
                    )
                    current_message = next_message
                else:
                    # No coordinator, workflow complete
                    workflow_completed = True
                    break
            
            iteration += 1
        
        # Mark workflow as completed
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id]["status"] = "completed" if workflow_completed else "error"
    
    def _check_workflow_completion(self, agent_roles: Dict[str, str], agent_completion: Dict[str, bool], last_response: str) -> bool:
        """Check if workflow should be completed based on agent roles and responses"""
        # Check for explicit completion signals based on agent roles
        # Only accept completion signals from the appropriate agent type
        current_agent_role = None
        for agent_id, role in agent_roles.items():
            if agent_completion.get(agent_id, False):
                current_agent_role = role.lower()
                break
        
        if current_agent_role == "coordinator":
            # Coordinator can only complete if ALL other agents have completed AND it says complete
            # Check if there are any incomplete agents
            has_incomplete_agents = any(
                not agent_completion.get(agent_id, False) 
                for agent_id, role in agent_roles.items() 
                if agent_id != current_agent_role and role.lower() != "coordinator"
            )
            
            # Only complete if no incomplete agents AND coordinator says complete
            if not has_incomplete_agents and any(phrase in last_response.lower() for phrase in [
                "coordination complete", "workflow complete", "all tasks delegated", "all agents completed"
            ]):
                return True
            
            # If there are incomplete agents, DON'T complete
            return False
        elif current_agent_role == "coder":
            # Coder can complete with code-specific phrases
            if any(phrase in last_response.lower() for phrase in [
                "code complete", "implementation complete"
            ]):
                return True
        elif current_agent_role == "tester":
            # Tester can complete with testing-specific phrases
            if any(phrase in last_response.lower() for phrase in [
                "testing complete", "validation complete"
            ]):
                return True
        elif current_agent_role == "runner":
            # Runner can complete with execution-specific phrases
            if any(phrase in last_response.lower() for phrase in [
                "execution complete", "running complete"
            ]):
                return True
        
        # Check if all agents have completed their roles
        if all(agent_completion.values()):
            return True
        
        # For single agent workflows, only complete if the agent explicitly says it's done
        roles = list(agent_roles.values())
        if len(roles) == 1:
            # Single agent - only complete if agent explicitly indicates completion
            return any(phrase in last_response.lower() for phrase in [
                "code complete", "task complete", "done", "finished", "complete"
            ])
        
        # Check for specific role-based completion patterns for multi-agent workflows
        if len(roles) == 2 and "coordinator" in roles and "coder" in roles:
            # Simple coordinator + coder workflow
            # Only complete if both coordinator and coder have completed their tasks
            coordinator_completed = agent_completion.get("coordinator", False)
            coder_completed = agent_completion.get("coder", False)
            return coordinator_completed and coder_completed
        
        return False
    
    def _get_next_agent(self, current_agent: str, agent_roles: Dict[str, str], agent_completion: Dict[str, bool]) -> Optional[str]:
        """Get the next agent to process based on workflow logic with priority order"""
        current_role = agent_roles.get(current_agent, "").lower()
        
        # Define workflow patterns based on agent roles with priority
        if current_role == "coordinator":
            # Coordinator should delegate in priority order: coder -> tester -> runner
            # 1. First check for coder if not completed
            for agent_id, role in agent_roles.items():
                if "coder" in role.lower() and agent_id != current_agent and not agent_completion.get(agent_id, False):
                    return agent_id
            
            # 2. Then check for tester if coder is done
            for agent_id, role in agent_roles.items():
                if "tester" in role.lower() and agent_id != current_agent and not agent_completion.get(agent_id, False):
                    return agent_id
            
            # 3. Finally check for runner
            for agent_id, role in agent_roles.items():
                if "runner" in role.lower() and agent_id != current_agent and not agent_completion.get(agent_id, False):
                    return agent_id
            
            # No more agents to delegate to
            return None
        
        elif current_role == "coder":
            # Coder should NOT delegate - this code path shouldn't be reached
            # Non-coordinator agents should return to coordinator
            return None
        
        elif current_role == "tester":
            # Tester should NOT delegate
            return None
        
        elif current_role == "runner":
            # Runner should NOT delegate
            return None
        
        # Default: no more agents to process
        return None

# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

# Create FastAPI app for online agent service
online_app = FastAPI(
    title="Online Agent Service",
    description="Online model integration for manual agent workflows with LangChain",
    version="1.0.0"
)

# Add CORS middleware
online_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[
        "*",
        "Content-Type",
        "X-OpenAI-Key",
        "X-Google-Key",
        "X-Mistral-Key",
        "X-Anthropic-Key",
    ],
)

# Initialize workflow manager
workflow_manager = OnlineWorkflowManager()

# =============================================================================
# API ENDPOINTS
# =============================================================================

@online_app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Online Agent Service",
        "version": "1.0.0",
        "description": "Online model integration with LangChain for manual agent workflows",
        "endpoints": {
            "health": "/health",
            "models": "/models",
            "workflow": "/run-workflow",
            "conversations": "/conversations",
            "workflow-status": "/workflow-status/{workflow_id}"
        }
    }

@online_app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "online_agent_service",
        "timestamp": datetime.now().isoformat(),
        "available_models": list(ONLINE_MODEL_CONFIGS.keys()),
        "github_available": GITHUB_AVAILABLE
    }

@online_app.post("/upload-to-github")
async def upload_to_github():
    """Manually upload latest generated code to GitHub"""
    if not GITHUB_AVAILABLE:
        raise HTTPException(status_code=503, detail="GitHub integration not available")
    
    try:
        result = await online_agent_github.upload_latest_generated_code()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub upload failed: {str(e)}")

@online_app.post("/save-code-manually")
async def save_code_manually(request: dict):
    """Manually save code to file system"""
    try:
        code = request.get("code", "")
        filename = request.get("filename")
        task_description = request.get("task_description", "Manual Code Save")
        
        if not code:
            raise HTTPException(status_code=400, detail="Code content is required")
        
        # Import file manager
        from file_manager import get_file_manager
        file_manager = get_file_manager()
        
        # Save code using file manager
        result = file_manager.save_code(
            code=code,
            filename=filename,
            file_type="src",
            conversation_id="manual_save",
            task_description=task_description
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": "Code saved successfully",
                "filepath": result.get("filepath"),
                "project_name": result.get("project_name"),
                "github_result": result.get("github_result", {})
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to save code: {result.get('error')}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Manual save failed: {str(e)}")

@online_app.get("/get-project-files/{conversation_id}")
async def get_project_files(conversation_id: str):
    """Get all files in a project for preview"""
    try:
        from file_manager import get_file_manager
        file_manager = get_file_manager()
        
        if conversation_id not in file_manager.active_projects:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_info = file_manager.active_projects[conversation_id]
        project_dir = project_info["project_dir"]
        
        files = []
        for file_path in project_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    rel_path = file_path.relative_to(project_dir)
                    content = file_path.read_text(encoding='utf-8')
                    files.append({
                        "path": str(rel_path).replace("\\", "/"),
                        "name": file_path.name,
                        "content": content,
                        "size": len(content),
                        "type": file_path.suffix[1:] if file_path.suffix else "txt"
                    })
                except Exception as e:
                    logging.warning(f"Could not read file {file_path}: {e}")
        
        return {"success": True, "files": files}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@online_app.post("/upload-project-to-github")
async def upload_project_manually(request: dict):
    """Manually upload a project to GitHub after user confirmation"""
    try:
        print("=" * 80)
        print("[DEBUG] Upload endpoint called!")
        print(f"[DEBUG] Request data: {request}")
        print("=" * 80)
        
        conversation_id = request.get("conversation_id")
        print(f"[DEBUG] Extracted conversation_id: {conversation_id}")
        
        if not conversation_id:
            raise HTTPException(status_code=400, detail="conversation_id is required")
        
        from file_manager import get_file_manager
        file_manager = get_file_manager()
        
        logging.info(f"[UPLOAD] Manual upload requested for conversation: {conversation_id}")
        print(f"[DEBUG] Calling file_manager.upload_project_to_github({conversation_id})")
        result = file_manager.upload_project_to_github(conversation_id)
        
        if result.get("status") == "success":
            logging.info(f"[OK] Manual upload successful: {result.get('repo_url')}")
            return {
                "success": True,
                "repo_url": result.get('repo_url'),
                "files_uploaded": result.get('files_uploaded', 0)
            }
        else:
            error_msg = result.get('error', 'Upload failed')
            logging.error(f"[ERROR] Manual upload failed: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"[ERROR] Upload exception: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@online_app.get("/github-status")
async def github_status():
    """Check GitHub integration status"""
    if not GITHUB_AVAILABLE:
        return {"available": False, "error": "GitHub integration not available"}
    
    try:
        is_configured = online_agent_github.is_configured()
        return {
            "available": True,
            "configured": is_configured,
            "message": "GitHub integration is ready" if is_configured else "GitHub not configured"
        }
    except Exception as e:
        return {"available": True, "configured": False, "error": str(e)}

def _extract_provider_keys_from_request(request: Request) -> Dict[str, Optional[str]]:
    """Extract provider API keys from incoming request headers."""
    # Normalize header names to lowercase
    headers = {k.lower(): v for k, v in request.headers.items()}
    return {
        "openai": headers.get("x-openai-key"),
        "mistral": headers.get("x-mistral-key"),
        "gemini": headers.get("x-google-key"),
        "anthropic": headers.get("x-anthropic-key"),
    }

from contextlib import contextmanager

@contextmanager
def _override_api_keys_for_request(keys: Dict[str, Optional[str]]):
    """Temporarily override module-level API keys for the duration of a request."""
    global OPENAI_API_KEY, MISTRAL_API_KEY, GEMINI_API_KEY
    old_openai, old_mistral, old_gemini = OPENAI_API_KEY, MISTRAL_API_KEY, GEMINI_API_KEY
    try:
        if keys.get("openai"):
            OPENAI_API_KEY = keys.get("openai")
        if keys.get("mistral"):
            MISTRAL_API_KEY = keys.get("mistral")
        if keys.get("gemini"):
            GEMINI_API_KEY = keys.get("gemini")
        yield
    finally:
        OPENAI_API_KEY, MISTRAL_API_KEY, GEMINI_API_KEY = old_openai, old_mistral, old_gemini


@online_app.get("/models")
async def get_online_models(request: Request):
    """Get available online models filtered by provided API keys (if any)."""
    keys = _extract_provider_keys_from_request(request)

    # Determine which providers are enabled for this request
    provider_enabled = {
        "openai": bool(keys.get("openai") or OPENAI_API_KEY),
        "mistral": bool(keys.get("mistral") or MISTRAL_API_KEY),
        "gemini": bool(keys.get("gemini") or GEMINI_API_KEY),
    }

    # Filter model configs to only include enabled providers
    filtered_models: Dict[str, Any] = {
        model_id: cfg
        for model_id, cfg in ONLINE_MODEL_CONFIGS.items()
        if provider_enabled.get(cfg.get("provider", ""), False)
    }

    return {
        "available_models": filtered_models,
        "default_model": next(iter(filtered_models.keys()), DEFAULT_ONLINE_MODEL),
        "providers": {
            "openai": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"] if provider_enabled["openai"] else [],
            "mistral": ["mistral-large", "mistral-medium", "mistral-small"] if provider_enabled["mistral"] else [],
            "gemini": ["gemini-2.5-flash", "gemini-2.5-pro"] if provider_enabled["gemini"] else [],
        }
    }

@online_app.post("/run-workflow")
async def run_online_workflow(request: OnlineWorkflowRequest, http_request: Request):
    """Run online agent workflow"""
    # Refresh API keys from file system
    refresh_api_keys()
    
    # Override API keys for this request if provided
    keys = _extract_provider_keys_from_request(http_request)
    with _override_api_keys_for_request(keys):
        # Validate request
        if not request.task or not request.task.strip():
            raise HTTPException(status_code=422, detail="Task cannot be empty")
    
        if not request.agents or len(request.agents) == 0:
            raise HTTPException(status_code=422, detail="At least one agent must be specified")
        
        # Check if required API keys are available
        required_providers = set()
        for agent in request.agents:
            model_config = ONLINE_MODEL_CONFIGS.get(agent.model, ONLINE_MODEL_CONFIGS[DEFAULT_ONLINE_MODEL])
            required_providers.add(model_config["provider"])
        
        missing_keys = []
        if "openai" in required_providers and not OPENAI_API_KEY:
            missing_keys.append("OPENAI_API_KEY")
        if "mistral" in required_providers and not MISTRAL_API_KEY:
            missing_keys.append("MISTRAL_API_KEY")
        if "gemini" in required_providers and not GEMINI_API_KEY:
            missing_keys.append("GEMINI_API_KEY")
        
        if missing_keys:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required API keys: {', '.join(missing_keys)}. Please set the environment variables."
            )
        
        try:
            response = await workflow_manager.run_workflow(request)
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@online_app.get("/workflow-status/{workflow_id}")
async def get_workflow_status(workflow_id: str, request: Request):
    """Get workflow status"""
    # Not strictly necessary to override keys here, but allow for provider queries if added later
    keys = _extract_provider_keys_from_request(request)
    with _override_api_keys_for_request(keys):
        workflow = workflow_manager.active_workflows.get(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "workflow_id": workflow_id,
            "status": workflow["status"],
            "agents": workflow["agents"],
            "message_count": len(workflow["message_history"]),
            "conversation_id": workflow["conversation_id"]
        }

@online_app.get("/conversations")
async def get_online_conversations():
    """Get conversation history"""
    try:
        conversations = await workflow_manager.db_integration.get_conversations()
        return [
            ConversationResponse(
                id=conv['id'],
                title=conv['title'],
                created_at=conv['created_at'],
                updated_at=conv['updated_at'],
                message_count=conv['message_count']
            )
            for conv in conversations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {str(e)}")

@online_app.get("/conversations/{conversation_id}")
async def get_online_conversation(conversation_id: str):
    """Get specific conversation"""
    try:
        conversation = await workflow_manager.db_integration.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = workflow_manager.db_integration.db_service.get_conversation_messages(conversation_id)
        return {
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
                "is_active": conversation.is_active
            },
            "messages": [
                {
                    "id": msg.id,
                    "from_agent": msg.from_agent,
                    "to_agent": msg.to_agent,
                    "message_type": msg.message_type,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "metadata": msg.message_metadata
                }
                for msg in messages
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")

# =============================================================================
# STARTUP
# =============================================================================

if __name__ == "__main__":
    print("Starting Online Agent Service...")
    print("LangChain integration enabled")
    print("Online models available:", list(ONLINE_MODEL_CONFIGS.keys()))
    print("API Documentation: http://localhost:8001/docs")
    print("Make sure to set OPENAI_API_KEY, MISTRAL_API_KEY, and GEMINI_API_KEY environment variables")
    
    uvicorn.run(online_app, host="0.0.0.0", port=8001)

