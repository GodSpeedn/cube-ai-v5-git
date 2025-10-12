/**
 * API Service for Multi-Agent System
 * 
 * This service handles all communication with the backend multi-agent system.
 * It provides a unified interface for all agent interactions and workflow management.
 */

const API_BASE_URL = 'http://localhost:8000';

export interface ChatRequest {
  prompt: string;
  code_history?: string[];
  error_history?: string[];
  conversation_id?: string;
}

export interface ChatResponse {
  type: 'coding' | 'error';
  message: string;
  code?: string;
  tests?: string;
  test_results?: string;
  tests_passed?: boolean;
  files_created?: string[];
  workflow_result?: any;
  success?: boolean;
}

export interface WorkflowRequest {
  task: string;
  agents: Array<{
    id: string;
    type: string;
    role: string;
    model?: string;
    model_config?: any;
  }>;
}

export interface WorkflowResponse {
  success: boolean;
  results?: any;
  message: string;
  error?: string;
}

export interface AgentMessage {
  id: string;
  from_agent: string;
  to_agent: string;
  message_type: 'task' | 'data' | 'request' | 'response' | 'error' | 'status';
  content: string;
  metadata?: any;
  timestamp: string;
}

export interface AgentStatus {
  agent_id: string;
  status: 'idle' | 'working' | 'waiting' | 'completed' | 'error';
  memory_size: number;
}

export interface WorkflowResult {
  workflow_id: string;
  status: string;
  agents: Record<string, AgentStatus>;
  message_history: AgentMessage[];
  total_messages: number;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationMessage {
  id: string;
  from_agent: string;
  to_agent: string;
  message_type: string;
  content: string;
  timestamp: string;
  metadata: any;
}

export interface ConversationDetail {
  conversation: {
    id: string;
    title: string;
    created_at: string;
    updated_at: string;
    is_active: boolean;
  };
  messages: ConversationMessage[];
}

/**
 * Test backend connection
 */
export async function testBackendConnection(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (response.ok) {
      const data = await response.json();
      console.log('Backend connection test passed:', data);
      return true;
    } else {
      console.error('Backend connection test failed:', response.status);
      return false;
    }
  } catch (error) {
    console.error('Backend connection test error:', error);
    return false;
  }
}

/**
 * Main chat endpoint - uses the new multi-agent system
 */
export async function chatWithAgents(request: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Chat request failed: ${response.status} - ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Chat API error:', error);
    throw error;
  }
}

/**
 * Run a custom workflow with specific agents
 */
export async function runWorkflow(request: WorkflowRequest): Promise<WorkflowResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/run-workflow`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Workflow request failed: ${response.status} - ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Workflow API error:', error);
    throw error;
  }
}

/**
 * Update an agent's model
 */
export async function updateAgentModel(agentId: string, modelName: string, modelConfig?: any): Promise<{ message: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/update-agent-model`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        agent_id: agentId,
        model_name: modelName,
        model_config: modelConfig
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to update agent model: ${response.status} - ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Update agent model API error:', error);
    throw error;
  }
}

/**
 * Get list of generated files
 */
export async function getGeneratedFiles(): Promise<{ files: string[] }> {
  try {
    const response = await fetch(`${API_BASE_URL}/list-files`);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to get files: ${response.status} - ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Get files API error:', error);
    throw error;
  }
}

/**
 * Get file content
 */
export async function getFileContent(filename: string): Promise<string> {
  try {
    const response = await fetch(`${API_BASE_URL}/generated/${filename}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to get file content: ${response.status} - ${errorText}`);
    }

    return await response.text();
  } catch (error) {
    console.error('Get file content API error:', error);
    throw error;
  }
}

/**
 * Delete a generated file
 */
export async function deleteGeneratedFile(filename: string): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/generated/${filename}`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to delete file: ${response.status} - ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Delete file API error:', error);
    throw error;
  }
}

/**
 * Run manual workflow
 */
export async function runManualFlow(prompt: string, boxes: any[], connections: any[]): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/run-manual-flow`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt,
        boxes,
        connections
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Manual flow failed: ${response.status} - ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Manual flow API error:', error);
    throw error;
  }
}

/**
 * Get example workflow configuration
 */
export async function getExampleWorkflow(): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/example-workflow`);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to get example workflow: ${response.status} - ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Get example workflow API error:', error);
    throw error;
  }
}

/**
 * Conversation Management Functions
 */

export async function getConversations(): Promise<Conversation[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/conversations`);
    if (!response.ok) throw new Error('Failed to fetch conversations');
    return await response.json();
  } catch (error) {
    console.error('Get conversations error:', error);
    throw error;
  }
}

export async function createConversation(title: string): Promise<{ conversation_id: string; title: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title })
    });
    if (!response.ok) throw new Error('Failed to create conversation');
    return await response.json();
  } catch (error) {
    console.error('Create conversation error:', error);
    throw error;
  }
}

export async function getConversation(conversationId: string): Promise<ConversationDetail> {
  try {
    const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}`);
    if (!response.ok) throw new Error('Failed to get conversation');
    return await response.json();
  } catch (error) {
    console.error('Get conversation error:', error);
    throw error;
  }
}

export async function deleteConversation(conversationId: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to delete conversation');
  } catch (error) {
    console.error('Delete conversation error:', error);
    throw error;
  }
}

// =============================================================================
// ONLINE AGENT SERVICE API FUNCTIONS
// =============================================================================

const ONLINE_API_BASE_URL = 'http://localhost:8001';

// Simple headers - API keys are managed in the backend
function getOnlineApiHeaders(): HeadersInit {
  return {
    'Content-Type': 'application/json'
  };
}

export interface OnlineAgent {
  id: string;
  name: string;
  role: string;
  model: string;
  system_prompt: string;
  memory_enabled: boolean;
  conversation_id?: string;
}

export interface OnlineWorkflowRequest {
  task: string;
  agents: OnlineAgent[];
  conversation_id?: string;
  enable_streaming: boolean;
}

export interface OnlineWorkflowResponse {
  workflow_id: string;
  status: string;
  agents: Record<string, string>;
  message_history: any[];
  total_messages: number;
  conversation_id: string;
}

/**
 * Test online agent service connection
 */
export async function testOnlineServiceConnection(): Promise<boolean> {
  try {
    const response = await fetch(`${ONLINE_API_BASE_URL}/health`, {
      method: 'GET',
      headers: getOnlineApiHeaders()
    });

    if (response.ok) {
      const data = await response.json();
      console.log('Online service connection test passed:', data);
      return true;
    } else {
      console.error('Online service connection test failed:', response.status);
      return false;
    }
  } catch (error) {
    console.error('Online service connection test error:', error);
    return false;
  }
}

/**
 * Get available online models
 */
export async function getOnlineModels(): Promise<any> {
  const endpoints = [
    `${ONLINE_API_BASE_URL}/models` // online service on port 8001
  ];
  
  for (const endpoint of endpoints) {
    try {
      console.log('Trying endpoint:', endpoint);
      const response = await fetch(endpoint, { headers: getOnlineApiHeaders() });
      console.log('Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Successfully got models from:', endpoint);
        console.log('Models data:', data);
        
        // Handle different response formats
        if (data.available_models) {
          return data;
        } else if (data.models) {
          return { available_models: data.models };
        } else if (Array.isArray(data)) {
          // Convert array to object format
          const modelsObj: any = {};
          data.forEach((model: any) => {
            if (typeof model === 'string') {
              modelsObj[model] = { name: model };
            } else if (model.id || model.name) {
              modelsObj[model.id || model.name] = model;
            }
          });
          return { available_models: modelsObj };
        } else {
          return { available_models: data };
        }
      }
    } catch (error) {
      console.log('Failed to fetch from:', endpoint, error instanceof Error ? error.message : String(error));
      continue;
    }
  }
  
  console.error('All endpoints failed, using fallback models');
  // Return a comprehensive fallback
  return {
    available_models: {
      'mistral-small': { name: 'Mistral Small', provider: 'mistral' },
      'mistral-medium': { name: 'Mistral Medium', provider: 'mistral' },
      'mistral-large': { name: 'Mistral Large', provider: 'mistral' },
      'gpt-3.5-turbo': { name: 'GPT-3.5 Turbo', provider: 'openai' },
      'gpt-4': { name: 'GPT-4', provider: 'openai' },
      'gpt-4-turbo': { name: 'GPT-4 Turbo', provider: 'openai' },
      'claude-3-sonnet': { name: 'Claude 3 Sonnet', provider: 'anthropic' },
      'claude-3-opus': { name: 'Claude 3 Opus', provider: 'anthropic' },
      'gemini-pro': { name: 'Gemini Pro', provider: 'google' },
      'gemini-pro-vision': { name: 'Gemini Pro Vision', provider: 'google' }
    }
  };
}

/**
 * Run online agent workflow
 */
export async function runOnlineWorkflow(request: OnlineWorkflowRequest): Promise<OnlineWorkflowResponse> {
  try {
    const response = await fetch(`${ONLINE_API_BASE_URL}/run-workflow`, {
      method: 'POST',
      headers: getOnlineApiHeaders(),
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Online workflow failed: ${response.status} - ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Online workflow API error:', error);
    throw error;
  }
}

/**
 * Get online workflow status
 */
export async function getOnlineWorkflowStatus(workflowId: string): Promise<any> {
  try {
    const response = await fetch(`${ONLINE_API_BASE_URL}/workflow-status/${workflowId}`, { headers: getOnlineApiHeaders() });
    if (!response.ok) throw new Error('Failed to get workflow status');
    return await response.json();
  } catch (error) {
    console.error('Get workflow status error:', error);
    throw error;
  }
}

/**
 * Get online conversations
 */
export async function getOnlineConversations(): Promise<Conversation[]> {
  try {
    const response = await fetch(`${ONLINE_API_BASE_URL}/conversations`);
    if (!response.ok) throw new Error('Failed to fetch online conversations');
    return await response.json();
  } catch (error) {
    console.error('Get online conversations error:', error);
    throw error;
  }
}

/**
 * Get online conversation details
 */
export async function getOnlineConversation(conversationId: string): Promise<ConversationDetail> {
  try {
    const response = await fetch(`${ONLINE_API_BASE_URL}/conversations/${conversationId}`);
    if (!response.ok) throw new Error('Failed to get online conversation');
    return await response.json();
  } catch (error) {
    console.error('Get online conversation error:', error);
    throw error;
  }
}

// =============================================================================
// GIT INTEGRATION API FUNCTIONS
// =============================================================================

export interface GitConfig {
  token: string;
  username: string;
  email?: string;
}

export interface GitStatus {
  configured: boolean;
  user?: {
    login: string;
    name: string;
    email: string;
  };
  repositories?: Repository[];
  error?: string;
  message?: string;
}

export interface Repository {
  name: string;
  full_name: string;
  description: string;
  private: boolean;
  html_url: string;
  clone_url: string;
  created_at: string;
  updated_at: string;
}

export interface GitUploadResult {
  success: boolean;
  message: string;
  repository_url?: string;
  commit_sha?: string;
  files_pushed?: number;
  error?: string;
}

/**
 * Get Git integration status
 */
export async function getGitStatus(): Promise<GitStatus> {
  try {
    const response = await fetch(`${API_BASE_URL}/git/status`);
    if (!response.ok) throw new Error('Failed to get Git status');
    return await response.json();
  } catch (error) {
    console.error('Get Git status error:', error);
    throw error;
  }
}

/**
 * Configure Git integration with GitHub
 */
export async function configureGit(config: GitConfig): Promise<{ success: boolean; message: string; user?: any; repositories?: Repository[] }> {
  try {
    const response = await fetch(`${API_BASE_URL}/git/configure`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    if (!response.ok) throw new Error('Failed to configure Git');
    return await response.json();
  } catch (error) {
    console.error('Configure Git error:', error);
    throw error;
  }
}

/**
 * Pull from a GitHub repository
 */
export async function pullFromRepository(repository: string): Promise<{ success: boolean; message: string; repository: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/git/pull`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repository })
    });
    if (!response.ok) throw new Error('Failed to pull repository');
    return await response.json();
  } catch (error) {
    console.error('Pull repository error:', error);
    throw error;
  }
}

/**
 * Push generated code to a GitHub repository
 */
export async function pushToRepository(repository: string, commitMessage?: string): Promise<GitUploadResult> {
  try {
    const response = await fetch(`${API_BASE_URL}/git/push`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        repository, 
        commit_message: commitMessage 
      })
    });
    if (!response.ok) throw new Error('Failed to push to repository');
    return await response.json();
  } catch (error) {
    console.error('Push to repository error:', error);
    throw error;
  }
}

/**
 * List GitHub repositories
 */
export async function listGitRepositories(): Promise<{ success: boolean; repositories: Repository[]; count: number }> {
  try {
    const response = await fetch(`${API_BASE_URL}/git/repositories`);
    if (!response.ok) throw new Error('Failed to list repositories');
    return await response.json();
  } catch (error) {
    console.error('List repositories error:', error);
    throw error;
  }
}

// =============================================================================
// PROJECT MANAGEMENT API FUNCTIONS
// =============================================================================

export interface Project {
  name: string;
  path: string;
  file_count: number;
  structure: {
    src_files: string[];
    test_files: string[];
    other_files: string[];
  };
  created: number;
  modified: number;
}

export interface ProjectFile {
  name: string;
  path: string;
  type: 'file' | 'folder';
  size: number;
  modified: number;
  content: string;
  is_test: boolean;
  extension: string;
  error?: string;
}

/**
 * List all projects
 */
export async function listProjects(): Promise<{ success: boolean; projects: Project[]; count: number }> {
  try {
    const response = await fetch(`${API_BASE_URL}/projects`);
    if (!response.ok) throw new Error('Failed to list projects');
    return await response.json();
  } catch (error) {
    console.error('List projects error:', error);
    throw error;
  }
}

/**
 * Get files in a specific project
 */
export async function getProjectFiles(projectName: string): Promise<{ success: boolean; project_name: string; files: ProjectFile[]; count: number }> {
  try {
    const response = await fetch(`${API_BASE_URL}/projects/${projectName}/files`);
    if (!response.ok) throw new Error('Failed to get project files');
    return await response.json();
  } catch (error) {
    console.error('Get project files error:', error);
    throw error;
  }
}

/**
 * Delete a project
 */
export async function deleteProject(projectName: string): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/projects/${projectName}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to delete project');
    return await response.json();
  } catch (error) {
    console.error('Delete project error:', error);
    throw error;
  }
} 