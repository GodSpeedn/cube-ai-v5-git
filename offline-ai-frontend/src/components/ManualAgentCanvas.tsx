import React, { useState, useRef, useEffect, useMemo } from 'react';
import { runManualFlow, testOnlineServiceConnection, getOnlineModels, runOnlineWorkflow, getOnlineWorkflowStatus, OnlineAgent, OnlineWorkflowRequest, OnlineWorkflowResponse } from '../services/api';
import websocketService from '../services/websocket';
import '../styles/manual-agents.css';

export type AgentType = 'coordinator' | 'coder' | 'tester' | 'runner' | 'custom';

interface AgentMessage {
  id: string;
  agentId: string;
  agentType: string;
  agentName: string;
  content: string;
  timestamp: string;
  fromAgent: string;
  toAgent: string;
}

type BoxSide = 'left' | 'right' | 'top' | 'bottom';

interface ManualAgentBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  agentType: AgentType;
  role: string;
  roleDescription: string;
  model?: string;
}

interface ManualAgentConnection {
  id: string;
  fromId: string;
  fromSide: BoxSide;
  toId: string;
  toSide: BoxSide;
}

interface ManualAgentCanvasProps {
  isDark: boolean;
}

const agentTypeOptions = [
  { value: 'coordinator', label: 'Coordinator' },
  { value: 'coder', label: 'Coder' },
  { value: 'tester', label: 'Tester' },
  { value: 'runner', label: 'Runner' },
  { value: 'custom', label: 'Custom' },
];

const offlineModelOptions = [
  { value: 'codellama', label: 'CodeLlama' },
  { value: 'mistral', label: 'Mistral' },
  { value: 'phi', label: 'Phi' },
  { value: 'llama3.2:3b', label: 'Llama3.2:3b' },
  { value: 'llama3.2:1b', label: 'Llama3.2:1b' },
  { value: 'gemma2:2b', label: 'Gemma2:2b' },
  { value: 'qwen2.5:3b', label: 'Qwen2.5:3b' },
  { value: 'deepseek-coder', label: 'DeepSeek Coder' },
  { value: 'custom', label: 'Custom' },
];

const DEFAULT_BOX = { width: 300, height: 100 };
const DEFAULT_POPUP = { width: 400, height: 300 };

const handleOffsets = {
  left:  { x: 0, y: 0.5 },
  right: { x: 1, y: 0.5 },
  top:   { x: 0.5, y: 0 },
  bottom:{ x: 0.5, y: 1 },
};

// Connection points on the actual box borders (for drawing lines)
const connectionOffsets = {
  left:  { x: 0, y: 0.5 },
  right: { x: 1, y: 0.5 },
  top:   { x: 0.5, y: 0 },
  bottom:{ x: 0.5, y: 1 },
};

const ManualAgentCanvas: React.FC<ManualAgentCanvasProps> = ({ isDark }) => {
  const [boxes, setBoxes] = useState<ManualAgentBox[]>([]);
  const [connections, setConnections] = useState<ManualAgentConnection[]>([]);
  const [connectDrag, setConnectDrag] = useState<null | {
    fromId: string;
    fromSide: BoxSide;
    mouse: { x: number; y: number };
  }>(null);
  const [dragId, setDragId] = useState<string | null>(null);
  const [resizeId, setResizeId] = useState<string | null>(null);
  const [offset, setOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [resizeStart, setResizeStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [resizeBox, setResizeBox] = useState<{ width: number; height: number }>({ width: 0, height: 0 });
  const [hoveredBoxId, setHoveredBoxId] = useState<string | null>(null);
  const [dragOverHandle, setDragOverHandle] = useState<{ boxId: string; side: BoxSide } | null>(null);
  const [selectedConnectionId, setSelectedConnectionId] = useState<string | null>(null);
  const [selectedBoxId, setSelectedBoxId] = useState<string | null>(null);
  const [connectMode, setConnectMode] = useState(false);
  const [pinnedBoxes, setPinnedBoxes] = useState<Record<string, boolean>>({});
  const [agentMessages, setAgentMessages] = useState<AgentMessage[]>([]);
  const [showConversation, setShowConversation] = useState(false);
  const [isOnlineMode, setIsOnlineMode] = useState(false);
  const [onlineServiceConnected, setOnlineServiceConnected] = useState(false);
  const [geminiAvailable, setGeminiAvailable] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [canvasScale, setCanvasScale] = useState(1);
  const [canvasOffset, setCanvasOffset] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const [canvasBoundsOffset, setCanvasBoundsOffset] = useState({ x: 0, y: 0 });
  const [onlineModels, setOnlineModels] = useState<any>(null);
  const [modelsLoading, setModelsLoading] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [wsStatus, setWsStatus] = useState('CLOSED');
  const [prompt, setPrompt] = useState('');
  const [popupStates, setPopupStates] = useState<Record<string, { x?: number; y?: number; width?: number; height?: number }>>({});
  const [resizingPopup, setResizingPopup] = useState<{ id: string; startX: number; startY: number; startW: number; startH: number } | null>(null);
  const [draggingPopup, setDraggingPopup] = useState<{ id: string; offsetX: number; offsetY: number }>();
  
  // GitHub upload modal state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadProjectInfo, setUploadProjectInfo] = useState<any>(null);
  const [uploadingToGithub, setUploadingToGithub] = useState(false);
  const [projectFiles, setProjectFiles] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<any>(null);
  const [loadingFiles, setLoadingFiles] = useState(false);
  
  const canvasRef = useRef<HTMLDivElement>(null);
  const scrollableCanvasRef = useRef<HTMLDivElement>(null);
  const importInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Calculate dynamic canvas bounds based on box positions
  const calculateCanvasBounds = () => {
    if (boxes.length === 0) {
      // Default reasonable canvas size
      return { minX: -200, minY: -200, maxX: 1200, maxY: 800 };
    }
    
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    
    boxes.forEach(box => {
      // Ensure box coordinates are finite numbers
      const x = Number.isFinite(box.x) ? box.x : 0;
      const y = Number.isFinite(box.y) ? box.y : 0;
      const width = Number.isFinite(box.width) ? box.width : 200;
      const height = Number.isFinite(box.height) ? box.height : 100;
      
      minX = Math.min(minX, x);
      minY = Math.min(minY, y);
      maxX = Math.max(maxX, x + width);
      maxY = Math.max(maxY, y + height);
    });
    
    // Ensure we have valid bounds
    if (!Number.isFinite(minX)) minX = -200;
    if (!Number.isFinite(minY)) minY = -200;
    if (!Number.isFinite(maxX)) maxX = 1200;
    if (!Number.isFinite(maxY)) maxY = 800;
    
    // Add reasonable padding around the content
    const padding = 200;
    const boundsWidth = maxX - minX + (2 * padding);
    const boundsHeight = maxY - minY + (2 * padding);
    
    // Ensure minimum canvas size for scrolling (reasonable size)
    const minCanvasWidth = 1200;
    const minCanvasHeight = 800;
    
    return {
      minX: minX - padding,
      minY: minY - padding,
      maxX: minX - padding + Math.max(boundsWidth, minCanvasWidth),
      maxY: minY - padding + Math.max(boundsHeight, minCanvasHeight)
    };
  };


  // Memoize canvas bounds to avoid recalculation
  const canvasBounds = useMemo(() => {
    const bounds = calculateCanvasBounds();
    console.log('Canvas bounds:', bounds);
    console.log('Canvas size:', {
      width: bounds.maxX - bounds.minX,
      height: bounds.maxY - bounds.minY
    });
    return bounds;
  }, [boxes]);

  
  // Convert screen coordinates to canvas coordinates
  const screenToCanvasCoords = (screenX: number, screenY: number) => {
    const canvasArea = scrollableCanvasRef.current;
    if (!canvasArea) return { x: 0, y: 0 };
    
    const canvasRect = canvasArea.getBoundingClientRect();
    
    // Simple conversion: screen position relative to canvas + scroll offset
    const canvasX = screenX - canvasRect.left + canvasArea.scrollLeft;
    const canvasY = screenY - canvasRect.top + canvasArea.scrollTop;
    
    return { x: canvasX, y: canvasY };
  };
  
  // Update canvas bounds offset when boxes move to negative coordinates
  useEffect(() => {
    const newOffsetX = Math.max(0, -canvasBounds.minX);
    const newOffsetY = Math.max(0, -canvasBounds.minY);
    
    // Ensure offsets are finite numbers
    setCanvasBoundsOffset({
      x: Number.isFinite(newOffsetX) ? newOffsetX : 0,
      y: Number.isFinite(newOffsetY) ? newOffsetY : 0
    });
  }, [canvasBounds]);

  // Generate online model options dynamically based on available models
  const getOnlineModelOptions = () => {
    if (!onlineModels || !onlineModels.available_models) {
      return [{ value: 'mistral-small', label: 'Mistral Small (Default)' }];
    }

    const availableModels = onlineModels.available_models;
    const options: Array<{ value: string; label: string }> = [];

    // Dynamically generate options from available models
    Object.entries(availableModels).forEach(([modelId, modelConfig]: [string, any]) => {
      const modelName = modelConfig.name || modelId;
      const provider = modelConfig.provider || 'unknown';
      
      let label = modelName;
      if (provider === 'google') {
        label += ' (Google) ✨';
      } else if (provider === 'openai') {
        label += ' (OpenAI)';
      } else if (provider === 'mistral') {
        label += ' (Mistral)';
      }
      
      // Add special indicators
      if (modelId === 'gemini-pro') {
        label += ' - Recommended';
      } else if (provider === 'openai') {
        label += ' - Quota Limited';
      }
      
      options.push({ value: modelId, label });
    });

    // Sort options by provider and name
    options.sort((a, b) => {
      const aProvider = availableModels[a.value]?.provider || '';
      const bProvider = availableModels[b.value]?.provider || '';
      
      // Google first, then Mistral, then OpenAI
      const providerOrder: Record<string, number> = { 'google': 0, 'mistral': 1, 'openai': 2 };
      const aOrder = providerOrder[aProvider] ?? 3;
      const bOrder = providerOrder[bProvider] ?? 3;
      
      if (aOrder !== bOrder) {
        return aOrder - bOrder;
      }
      
      return a.label.localeCompare(b.label);
    });

    if (options.length === 0) {
      options.push({ value: 'mistral-small', label: 'Mistral Small (Fallback)' });
    }

    return options;
  };

  const onlineModelOptions = getOnlineModelOptions();
  
  // Debug logging for model options
  console.log('=== Model Debug Info ===');
  console.log('isOnlineMode:', isOnlineMode);
  console.log('onlineServiceConnected:', onlineServiceConnected);
  console.log('modelsLoading:', modelsLoading);
  console.log('onlineModels:', onlineModels);
  console.log('onlineModelOptions (processed):', onlineModelOptions);
  console.log('offlineModelOptions:', offlineModelOptions);
  console.log('========================');

  // WebSocket event handlers
  useEffect(() => {
    const handleConnected = () => {
      setWsConnected(true);
      setWsStatus('OPEN');
      console.log('🔗 WebSocket connected to ManualAgentCanvas');
    };

    const handleDisconnected = () => {
      setWsConnected(false);
      setWsStatus('CLOSED');
      console.log('🔌 WebSocket disconnected from ManualAgentCanvas');
    };

    const handleAgentMessage = (data: any) => {
      console.log('📨 Received agent message via WebSocket:', data);
      if (data.content && data.from_agent && data.to_agent) {
        const newMessage = {
          id: `ws-${Date.now()}-${Math.random()}`,
          agentId: data.from_agent,
          agentType: data.from_agent,
          agentName: data.from_agent,
          content: data.content,
          timestamp: data.timestamp || new Date().toISOString(),
          fromAgent: data.from_agent,
          toAgent: data.to_agent
        };
        setAgentMessages(prev => [...prev, newMessage]);
        setShowConversation(true);
      }
    };

    const handleWorkflowStatus = (data: any) => {
      console.log('📊 Received workflow status via WebSocket:', data);
      if (data.status === 'completed' || data.status === 'error') {
        setIsRunning(false);
        setAgentMessages(prev => [...prev, {
          id: `status-${Date.now()}`,
          agentId: 'system',
          agentType: 'system',
          agentName: 'System',
          content: data.status === 'completed' ? '✅ Workflow completed successfully!' : '❌ Workflow failed',
          timestamp: new Date().toISOString(),
          fromAgent: 'System',
          toAgent: 'Workflow'
        }]);
      }
    };

    const handleTestMessage = (data: any) => {
      console.log('🧪 Received test message via WebSocket:', data);
      setAgentMessages(prev => [...prev, {
        id: `test-${Date.now()}`,
        agentId: 'system',
        agentType: 'system',
        agentName: 'System',
        content: `🧪 WebSocket Test: ${data.message || 'Connection working!'}`,
        timestamp: new Date().toISOString(),
        fromAgent: 'System',
        toAgent: 'Test'
      }]);
      setShowConversation(true);
    };

    websocketService.on('connected', handleConnected);
    websocketService.on('disconnected', handleDisconnected);
    websocketService.on('agent_message', handleAgentMessage);
    websocketService.on('workflow_status', handleWorkflowStatus);
    websocketService.on('test_response', handleTestMessage);

    websocketService.connect();

    return () => {
      websocketService.off('connected', handleConnected);
      websocketService.off('disconnected', handleDisconnected);
      websocketService.off('agent_message', handleAgentMessage);
      websocketService.off('workflow_status', handleWorkflowStatus);
      websocketService.off('test_response', handleTestMessage);
    };
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [agentMessages]);

  // Check online service connection and model availability
  useEffect(() => {
    if (isOnlineMode) {
      setModelsLoading(true);
      testOnlineServiceConnection().then(connected => {
        setOnlineServiceConnected(connected);
        if (connected) {
          getOnlineModels().then(models => {
            console.log('Successfully fetched online models:', models);
            setOnlineModels(models);
            const hasGemini = models.available_models && (
              'gemini-pro' in models.available_models || 
              'gemini-pro-vision' in models.available_models ||
              'gemini-1.5-flash' in models.available_models
            );
            setGeminiAvailable(hasGemini);
            setModelsLoading(false);
          }).catch(err => {
            console.error('Failed to get online models:', err);
            console.log('Setting fallback models due to error...');
            // Set fallback models when API fails
            setOnlineModels({
              available_models: {
                'mistral-small': { name: 'Mistral Small', provider: 'mistral' },
                'mistral-medium': { name: 'Mistral Medium', provider: 'mistral' },
                'mistral-large': { name: 'Mistral Large', provider: 'mistral' },
                'gpt-3.5-turbo': { name: 'GPT-3.5 Turbo', provider: 'openai' },
                'gpt-4': { name: 'GPT-4', provider: 'openai' },
                'gpt-4-turbo': { name: 'GPT-4 Turbo', provider: 'openai' },
                'gemini-pro': { name: 'Gemini Pro', provider: 'google' },
                'gemini-1.5-flash': { name: 'Gemini 1.5 Flash', provider: 'google' },
                'gemini-pro-vision': { name: 'Gemini Pro Vision', provider: 'google' }
              }
            });
            setGeminiAvailable(true);
            setModelsLoading(false);
          });
        } else {
          setModelsLoading(false);
        }
      }).catch(err => {
        console.error('Failed to test online service connection:', err);
        setOnlineServiceConnected(false);
        setGeminiAvailable(false);
        setModelsLoading(false);
      });
    } else {
      setModelsLoading(false);
    }
  }, [isOnlineMode]);

  // Handle running the flow
  const handleRunFlow = async () => {
    if (!prompt.trim()) {
      alert('Please enter a prompt');
      return;
    }

    if (boxes.length === 0) {
      alert('Please create at least one agent box');
      return;
    }

    setIsRunning(true);
    setAgentMessages([]);
    setShowConversation(true);

    try {
      let data: OnlineWorkflowResponse | any;
      
      if (isOnlineMode) {
        const onlineAgents: OnlineAgent[] = boxes.map(box => {
          let systemPrompt = box.roleDescription;
          
          if (!systemPrompt) {
            const role = box.role || box.agentType;
                const availableAgents = boxes.map(box => box.role || box.agentType).filter(role => role.toLowerCase() !== 'coordinator');
                const agentList = availableAgents.length > 0 ? availableAgents.join(', ') : 'none';
                
            switch (role.toLowerCase()) {
              case 'coordinator':
                systemPrompt = `You are a Coordinator agent responsible for task delegation and workflow management.

Your responsibilities:
1. Analyze incoming tasks and break them down into actionable steps
2. Delegate specific tasks to appropriate agents (${agentList})
3. Monitor progress and coordinate between agents
4. Provide clear, specific instructions to each agent
5. Compile final results and present them clearly

When delegating tasks:
- Be specific about what you want each agent to do
- Provide clear requirements and expectations
- Ask for concrete deliverables
- Follow up on completed tasks

Available agents: ${agentList}

Always provide clear, actionable instructions to agents.`;
                break;
              case 'coder':
                systemPrompt = `You are a Coder agent responsible for writing high-quality, functional code.

Your responsibilities:
1. Write clean, well-documented code
2. Follow best practices and coding standards
3. Include proper error handling where appropriate
4. Provide complete, runnable code examples
5. Explain your code when necessary

When writing code:
- Always provide complete, functional code
- Include proper imports and dependencies
- Add comments for complex logic
- Test your code mentally before presenting it
- Format code properly with appropriate indentation

Always end your response with "CODE COMPLETE:" followed by the complete code in a code block.`;
                break;
              case 'tester':
                systemPrompt = `You are a Tester agent responsible for creating comprehensive tests and validating code quality.

Your responsibilities:
1. Create unit tests for provided code
2. Test edge cases and error conditions
3. Validate code functionality and correctness
4. Provide test results and feedback
5. Suggest improvements when needed

When testing code:
- Write comprehensive test cases
- Test both normal and edge cases
- Verify expected outputs
- Check for potential bugs or issues
- Provide clear test results

Always provide detailed test results and any recommendations.`;
                break;
              case 'runner':
                systemPrompt = `You are a Runner agent responsible for executing code and providing execution results.

Your responsibilities:
1. Execute provided code safely
2. Capture and report execution results
3. Handle errors and exceptions
4. Provide output analysis
5. Report execution status

When running code:
- Execute code in a safe environment
- Capture all output (stdout, stderr)
- Report any errors or exceptions
- Analyze results and provide insights
- Document execution performance if relevant

Always provide complete execution results and analysis.`;
                break;
              default:
                systemPrompt = `You are a ${role} agent with specialized expertise in your domain.

Your responsibilities:
1. Perform your specific role effectively and efficiently
2. Provide high-quality outputs and deliverables
3. Collaborate with other agents when needed
4. Follow best practices in your field
5. Communicate clearly and professionally

Available agents: ${agentList}

Always provide clear, actionable results and communicate effectively with other agents.`;
            }
          }
          
          return {
            id: box.id,
            name: box.role || box.agentType,
            role: box.role || box.agentType,
            model: box.model || 'mistral-small',
            system_prompt: systemPrompt,
            memory_enabled: true
          };
        });

        const onlineRequest: OnlineWorkflowRequest = {
          task: prompt.trim(),
          agents: onlineAgents,
          enable_streaming: true,
          conversation_id: undefined
        };

        data = await runOnlineWorkflow(onlineRequest);
        
        if (data.message_history && data.message_history.length > 0) {
        const agentIdToName = new Map();
        boxes.forEach(box => {
          agentIdToName.set(box.id, box.role || box.agentType);
        });
          
          const initialMessages = data.message_history.map((msg: any) => ({
            id: msg.id,
            agentId: msg.from_agent,
            agentType: agentIdToName.get(msg.from_agent) || msg.from_agent,
            agentName: agentIdToName.get(msg.from_agent) || msg.from_agent,
            content: msg.content,
            timestamp: msg.timestamp,
            fromAgent: agentIdToName.get(msg.from_agent) || msg.from_agent,
            toAgent: agentIdToName.get(msg.to_agent) || msg.to_agent
          }));
          setAgentMessages(initialMessages);
          
          // Check if project is ready for GitHub upload and show confirmation
          if (data.github_upload && data.github_upload.ready_for_upload) {
            const projectInfo = data.github_upload.project_info;
            
            // Small delay to ensure UI is updated
            setTimeout(async () => {
              // Show modal instead of window.confirm
              const projectInfoWithId = {
                ...projectInfo,
                conversation_id: data.conversation_id  // Add conversation_id from response
              };
              setUploadProjectInfo(projectInfoWithId);
              setShowUploadModal(true);
              
              // Fetch project files
              setLoadingFiles(true);
              try {
                const filesResponse = await fetch(`http://localhost:8001/get-project-files/${data.conversation_id}`);
                if (filesResponse.ok) {
                  const filesData = await filesResponse.json();
                  setProjectFiles(filesData.files || []);
                  // Auto-select first file
                  if (filesData.files && filesData.files.length > 0) {
                    setSelectedFile(filesData.files[0]);
                  }
                }
              } catch (error) {
                console.error('Failed to load project files:', error);
              } finally {
                setLoadingFiles(false);
              }
            }, 500); // 500ms delay to ensure UI is ready
          }
        } else {
          setAgentMessages([{
            id: 'loading-1',
            agentId: 'system',
            agentType: 'system',
            agentName: 'System',
            content: '🤖 Starting workflow...',
            timestamp: new Date().toISOString(),
            fromAgent: 'System',
            toAgent: 'Workflow'
          }]);
        }
      } else {
        const offlineBoxes = boxes.map(box => ({
          ...box,
          agentType: box.role || box.agentType,
          role: box.role || box.agentType,
          description: box.roleDescription || `You are a ${box.role || box.agentType} agent.`
        }));
        
        setAgentMessages([{
          id: 'loading-1',
          agentId: 'system',
          agentType: 'system',
          agentName: 'System',
          content: '🤖 Starting offline workflow...',
          timestamp: new Date().toISOString(),
          fromAgent: 'System',
          toAgent: 'Workflow'
        }]);
        
        data = await runManualFlow(prompt.trim(), offlineBoxes, connections);
        
        if (data.messages && data.messages.length > 0) {
          setAgentMessages(data.messages.filter((msg: any) => msg.id !== 'loading-1'));
        }
      }

    } catch (error) {
      console.error('Error running flow:', error);
      alert('Error running flow: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setIsRunning(false);
    }
  };

  // Zoom functions
  const handleZoomIn = () => {
    setCanvasScale(prev => Math.min(prev * 1.2, 3)); // Max 3x zoom
  };

  const handleZoomOut = () => {
    setCanvasScale(prev => Math.max(prev / 1.2, 0.1)); // Min 0.1x zoom
  };

  const handleResetZoom = () => {
    setCanvasScale(1);
    setCanvasOffset({ x: 0, y: 0 });
  };

  // Add box at default position
  const handleCreateBox = () => {
    const boxCount = boxes.length;
    // Spread boxes out more to test horizontal scrolling
    const xOffset = (boxCount % 5) * 350; // 5 boxes per row
    const yOffset = Math.floor(boxCount / 5) * 250;
    
    setBoxes(prev => [
      ...prev,
      {
        id: Date.now().toString() + Math.random().toString(36).slice(2),
        x: 200 + xOffset,
        y: 200 + yOffset,
        width: DEFAULT_BOX.width,
        height: DEFAULT_BOX.height,
        agentType: 'coordinator',
        role: '',
        roleDescription: '',
      },
    ]);
  };

  // Update box fields
  const handleBoxChange = (id: string, field: keyof ManualAgentBox, value: any) => {
    setBoxes(prev => prev.map(box => box.id === id ? { ...box, [field]: value } : box));
  };

  // Drag logic
  const handleBoxMouseDown = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    const box = boxes.find(b => b.id === id);
    if (box) {
      setDragId(id);
      const canvasCoords = screenToCanvasCoords(e.clientX, e.clientY);
      setOffset({ x: canvasCoords.x - box.x, y: canvasCoords.y - box.y });
      setSelectedBoxId(id);
      setSelectedConnectionId(null);
    }
  };

  // Resize logic
  const handleResizeMouseDown = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    const box = boxes.find(b => b.id === id);
    if (box) {
      setResizeId(id);
      setResizeStart({ x: e.clientX, y: e.clientY });
      setResizeBox({ width: box.width, height: box.height });
    }
  };

  // Connection handle drag start
  const handleHandleMouseDown = (e: React.MouseEvent, boxId: string, side: BoxSide) => {
    e.stopPropagation();
    if (!connectMode) return;
    const box = boxes.find(b => b.id === boxId);
    if (!box) return;
    const { x, y, width, height } = box;
    const handleX = x + width * connectionOffsets[side].x;
    const handleY = y + height * connectionOffsets[side].y;
    setConnectDrag({ fromId: boxId, fromSide: side, mouse: { x: handleX, y: handleY } });
  };

  // Mouse move for drag/resize/connect/pan
  const handleCanvasMouseMove = (e: React.MouseEvent) => {
    if (resizeId) {
      const dx = e.clientX - resizeStart.x;
      const dy = e.clientY - resizeStart.y;
      setBoxes(prev => prev.map(box =>
        box.id === resizeId
          ? { ...box, width: Math.max(120, resizeBox.width + dx), height: Math.max(60, resizeBox.height + dy) }
          : box
      ));
      return;
    }
    if (dragId) {
      const canvasCoords = screenToCanvasCoords(e.clientX, e.clientY);
      setBoxes(prev => prev.map(box => {
        if (box.id === dragId) {
          // Box should follow mouse precisely - no sensitivity adjustment needed
          const newX = Math.max(-10000, Math.min(10000, canvasCoords.x - offset.x));
          const newY = Math.max(-10000, Math.min(10000, canvasCoords.y - offset.y));
          return { ...box, x: newX, y: newY };
        }
        return box;
      }));
      return;
    }
    // Disable panning for now to prevent background movement
    // if (isPanning) {
    //   // Handle canvas panning by scrolling
    //   const canvasArea = scrollableCanvasRef.current;
    //   if (canvasArea) {
    //     const dx = e.clientX - panStart.x;
    //     const dy = e.clientY - panStart.y;
    //     canvasArea.scrollLeft = canvasArea.scrollLeft - dx;
    //     canvasArea.scrollTop = canvasArea.scrollTop - dy;
    //     setPanStart({ x: e.clientX, y: e.clientY });
    //   }
    // }
    if (connectDrag) {
      const canvasCoords = screenToCanvasCoords(e.clientX, e.clientY);
      setConnectDrag({ ...connectDrag, mouse: canvasCoords });
    }
  };

  // Improved Bezier curve for connections
  const getSmartBezierPath = (x1: number, y1: number, x2: number, y2: number) => {
    const dx = x2 - x1;
    const dy = y2 - y1;
    const absDx = Math.abs(dx);
    const absDy = Math.abs(dy);
    let c1x = x1, c1y = y1, c2x = x2, c2y = y2;
    if (absDx > absDy) {
      c1x = x1 + dx * 0.5;
      c2x = x2 - dx * 0.5;
    } else {
      c1y = y1 + dy * 0.5;
      c2y = y2 - dy * 0.5;
    }
    return `M ${x1} ${y1} C ${c1x} ${c1y}, ${c2x} ${c2y}, ${x2} ${y2}`;
  };

  // Mouse up to stop drag/resize/connect/pan
  const handleCanvasMouseUp = (e: React.MouseEvent) => {
    if (connectDrag) {
      if (dragOverHandle && dragOverHandle.boxId !== connectDrag.fromId) {
        setConnections(prev => [
          ...prev,
          {
            id: connectDrag.fromId + '-' + dragOverHandle.boxId + '-' + connectDrag.fromSide + '-' + dragOverHandle.side,
            fromId: connectDrag.fromId,
            fromSide: connectDrag.fromSide,
            toId: dragOverHandle.boxId,
            toSide: dragOverHandle.side,
          },
        ]);
      }
      setConnectDrag(null);
      setDragOverHandle(null);
      return;
    }
    
    setDragId(null);
    setResizeId(null);
    setIsPanning(false);
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      const tag = (target?.tagName || '').toLowerCase();
      const isTyping = tag === 'input' || tag === 'textarea' || (target?.isContentEditable ?? false) || tag === 'select';
      if (isTyping) return;

      if (e.key === 'Escape') {
        setConnectDrag(null);
        setDragOverHandle(null);
        if (connectMode) setConnectMode(false);
        setSelectedConnectionId(null);
        setSelectedBoxId(null);
      }
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (selectedBoxId) {
          setBoxes(prev => prev.filter(b => b.id !== selectedBoxId));
          setConnections(prev => prev.filter(c => c.fromId !== selectedBoxId && c.toId !== selectedBoxId));
          setSelectedBoxId(null);
        } else if (selectedConnectionId) {
          setConnections(prev => prev.filter(c => c.id !== selectedConnectionId));
          setSelectedConnectionId(null);
        }
      }
      
      // Keyboard navigation for canvas panning
      if (e.key === 'ArrowUp' || e.key === 'ArrowDown' || e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
        const canvasArea = scrollableCanvasRef.current;
        if (canvasArea) {
          const scrollAmount = e.shiftKey ? 100 : 50; // Faster with Shift
          switch (e.key) {
            case 'ArrowUp':
              canvasArea.scrollTop -= scrollAmount;
              break;
            case 'ArrowDown':
              canvasArea.scrollTop += scrollAmount;
              break;
            case 'ArrowLeft':
              canvasArea.scrollLeft -= scrollAmount;
              break;
            case 'ArrowRight':
              canvasArea.scrollLeft += scrollAmount;
              break;
          }
          e.preventDefault();
        }
      }
      
      // Zoom keyboard shortcuts
      if (e.key === '=' || e.key === '+') {
        if (e.ctrlKey || e.metaKey) {
          handleZoomIn();
          e.preventDefault();
        }
      }
      if (e.key === '-' || e.key === '_') {
        if (e.ctrlKey || e.metaKey) {
          handleZoomOut();
          e.preventDefault();
        }
      }
      if (e.key === '0') {
        if (e.ctrlKey || e.metaKey) {
          handleResetZoom();
          e.preventDefault();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [connectMode, selectedBoxId, selectedConnectionId]);

  // Mouse wheel zoom
  useEffect(() => {
    const handleWheel = (e: WheelEvent) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        if (e.deltaY < 0) {
          handleZoomIn();
        } else {
          handleZoomOut();
        }
      }
    };

    const canvasArea = scrollableCanvasRef.current;
    if (canvasArea) {
      canvasArea.addEventListener('wheel', handleWheel, { passive: false });
      return () => canvasArea.removeEventListener('wheel', handleWheel);
    }
  }, []);

  // Cancel connection drag on canvas click
  const handleCanvasClick = (e: React.MouseEvent) => {
    if (e.target === scrollableCanvasRef.current || e.target === canvasRef.current) {
      setSelectedBoxId(null);
      setSelectedConnectionId(null);
      if (connectDrag) {
        setConnectDrag(null);
        setDragOverHandle(null);
      }
    }
  };

  // Export/Import Handlers
  const handleExport = () => {
    try {
      const exportData = {
        version: 1,
        prompt,
        boxes,
        connections,
        pinnedBoxes,
        canvasScale,
        canvasOffset,
        timestamp: new Date().toISOString(),
      };
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `manual_agents_${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert('Failed to export configuration.');
    }
  };

  const handleImportClick = () => {
    importInputRef.current?.click();
  };

  const handleImportChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const text = String(reader.result || '');
        const data = JSON.parse(text);
        if (!data || !Array.isArray(data.boxes) || !Array.isArray(data.connections)) {
          throw new Error('Invalid file format.');
        }
        setBoxes(data.boxes || []);
        setConnections(data.connections || []);
        setPinnedBoxes(data.pinnedBoxes || {});
        if (typeof data.prompt === 'string') setPrompt(data.prompt);
        if (typeof data.canvasScale === 'number') setCanvasScale(data.canvasScale);
        if (data.canvasOffset && typeof data.canvasOffset.x === 'number' && typeof data.canvasOffset.y === 'number') {
          setCanvasOffset({ x: data.canvasOffset.x, y: data.canvasOffset.y });
        }
        setAgentMessages([]);
        setSelectedBoxId(null);
                setSelectedConnectionId(null);
        setConnectDrag(null);
        setDragOverHandle(null);
        setConnectMode(false);
        setPopupStates({});
        alert('Configuration imported successfully.');
      } catch (err) {
        console.error('Import error:', err);
        alert('Failed to import configuration. Make sure the JSON is valid.');
      } finally {
        e.target.value = '';
      }
    };
    reader.readAsText(file);
  };

  const handleGitHubUpload = async () => {
    if (!uploadProjectInfo?.conversation_id) return;
    
    setUploadingToGithub(true);
    
    try {
      const uploadResponse = await fetch('http://localhost:8001/upload-project-to-github', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversation_id: uploadProjectInfo.conversation_id })
      });
      
      if (uploadResponse.ok) {
        const uploadResult = await uploadResponse.json();
        setAgentMessages(prev => [...prev, {
          id: `github-${Date.now()}`,
          agentId: 'system',
          agentType: 'system',
          agentName: 'GitHub',
          content: `✅ Successfully uploaded to GitHub!\n\n🔗 Repository: ${uploadResult.repo_url}\n📦 Files: ${uploadResult.files_uploaded}`,
          timestamp: new Date().toISOString(),
          fromAgent: 'System',
          toAgent: 'User'
        }]);
        setShowUploadModal(false);
        setUploadProjectInfo(null);
      } else {
        const errorData = await uploadResponse.json();
        setAgentMessages(prev => [...prev, {
          id: `github-error-${Date.now()}`,
          agentId: 'system',
          agentType: 'system',
          agentName: 'GitHub',
          content: `❌ Upload failed: ${errorData.detail}`,
          timestamp: new Date().toISOString(),
          fromAgent: 'System',
          toAgent: 'User'
        }]);
      }
    } catch (error) {
      console.error('GitHub upload error:', error);
      setAgentMessages(prev => [...prev, {
        id: `github-error-${Date.now()}`,
        agentId: 'system',
        agentType: 'system',
        agentName: 'GitHub',
        content: `❌ Upload error: ${error}`,
        timestamp: new Date().toISOString(),
        fromAgent: 'System',
        toAgent: 'User'
      }]);
    } finally {
      setUploadingToGithub(false);
    }
  };

  const handleClearCanvas = () => {
    const ok = window.confirm('Clear canvas? This will remove all agents, connections, and messages.');
    if (!ok) return;
    setBoxes([]);
    setConnections([]);
    setAgentMessages([]);
    setSelectedBoxId(null);
                setSelectedConnectionId(null);
    setConnectDrag(null);
    setDragOverHandle(null);
    setConnectMode(false);
    setPopupStates({});
  };

  // Render connection handles for a box
  const renderHandles = (box: ManualAgentBox) => {
    if (!connectMode) return null;
    const show = hoveredBoxId === box.id || (connectDrag && connectDrag.fromId === box.id);
    return (
      (['left', 'right', 'top', 'bottom'] as BoxSide[]).map(side => {
        const hx = box.x + box.width * handleOffsets[side].x;
        const hy = box.y + box.height * handleOffsets[side].y;
        const isDragOver = dragOverHandle && dragOverHandle.boxId === box.id && dragOverHandle.side === side;
        
        // Position handles outside the box with padding for full visibility
        let handleLeft, handleTop;
        const handleSize = 28; // 1.75rem = 28px
        const offset = handleSize / 2;
        const padding = 8; // Additional padding from the border
        
        switch(side) {
          case 'left':
            handleLeft = -(offset + padding); // Fully outside left border
            handleTop = box.height * 0.5 - offset;
            break;
          case 'right':
            handleLeft = box.width + padding - offset; // Fully outside right border  
            handleTop = box.height * 0.5 - offset;
            break;
          case 'top':
            handleLeft = box.width * 0.5 - offset;
            handleTop = -(offset + padding); // Fully outside top border
            break;
          case 'bottom':
            handleLeft = box.width * 0.5 - offset;
            handleTop = box.height + padding - offset; // Fully outside bottom border
            break;
        }
        
        return (
          <div
            key={side}
            className={`connection-handle ${show || isDragOver ? 'show' : ''} ${isDragOver ? 'drag-over' : ''}`}
            style={{
              left: handleLeft,
              top: handleTop,
            }}
            onMouseDown={e => handleHandleMouseDown(e, box.id, side)}
            onMouseEnter={() => connectDrag && setDragOverHandle({ boxId: box.id, side })}
            onMouseLeave={() => connectDrag && setDragOverHandle(null)}
          />
        );
      })
    );
  };

  // Render connections as SVG paths
  const renderConnections = () => {
    
    return (
    <svg 
        className="connections-svg"
        width="100%"
        height="100%"
      style={{ 
        position: 'absolute', 
        top: 0,
          left: 0,
          zIndex: 10,
          pointerEvents: 'none',
          overflow: 'visible'
        }}

    >
      {connections.map(conn => {
        const from = boxes.find(b => b.id === conn.fromId);
        const to = boxes.find(b => b.id === conn.toId);
        if (!from || !to) return null;
        const fromX = from.x + from.width * connectionOffsets[conn.fromSide].x;
        const fromY = from.y + from.height * connectionOffsets[conn.fromSide].y;
        const toX = to.x + to.width * connectionOffsets[conn.toSide].x;
        const toY = to.y + to.height * connectionOffsets[conn.toSide].y;
        return (
          <g key={conn.id}>
            <path
              className={`connection-path ${selectedConnectionId === conn.id ? 'selected' : ''}`}
              d={getSmartBezierPath(fromX, fromY, toX, toY)}
              markerEnd="url(#arrowhead)"
              fill="none"
              style={{ 
                cursor: 'pointer', 
                pointerEvents: 'stroke'
              }}
              onClick={e => { 
                e.stopPropagation(); 
                setSelectedBoxId(null); 
                setSelectedConnectionId(conn.id); 
              }}
            />
          </g>
        );
      })}
      {/* Temporary connection line while dragging */}
      {connectDrag && (() => {
        const from = boxes.find(b => b.id === connectDrag.fromId);
        if (!from) return null;
        const fromX = from.x + from.width * connectionOffsets[connectDrag.fromSide].x;
        const fromY = from.y + from.height * connectionOffsets[connectDrag.fromSide].y;
        return (
          <path
            className="connection-temp"
            d={getSmartBezierPath(fromX, fromY, connectDrag.mouse.x, connectDrag.mouse.y)}
            strokeDasharray="6 4"
            fill="none"
            style={{ pointerEvents: 'none' }}
          />
        );
      })()}
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill={isDark ? '#ffffff' : '#1f2937'} />
        </marker>
      </defs>
    </svg>
    );
  };

  // Get messages for a specific agent box
  const getBoxMessages = (boxId: string): AgentMessage[] => {
    return agentMessages.filter(message => message.agentId === boxId)
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  };

  // Render agent boxes
  const renderBoxes = () => {
    return boxes.map(box => {
      const boxMessages = getBoxMessages(box.id);
      const hasMessages = boxMessages.length > 0;
      const isActive = isRunning && hasMessages;
      
      return (
        <div
          key={box.id}
          className={`agent-box ${selectedBoxId === box.id ? 'selected' : ''} ${isActive ? 'active' : ''} ${dragId === box.id ? 'dragging' : ''}`}
          style={{
            left: box.x,
            top: box.y,
            width: box.width,
            height: box.height,
          }}
          onMouseDown={e => !pinnedBoxes[box.id] && handleBoxMouseDown(e, box.id)}
          onMouseEnter={() => setHoveredBoxId(box.id)}
          onMouseLeave={() => setHoveredBoxId(null)}
        >
          {renderHandles(box)}
          
          {/* Pin and Delete buttons */}
          <div className="box-controls">
            <button
              className="box-control-btn pin"
              title={pinnedBoxes[box.id] ? 'Unpin' : 'Pin'}
              onClick={e => { e.stopPropagation(); setPinnedBoxes(prev => ({ ...prev, [box.id]: !prev[box.id] })); }}
            >
              {pinnedBoxes[box.id] ? '📌' : '📍'}
            </button>
            
            <button
              className="box-control-btn delete"
              title="Delete Box"
              onClick={e => { 
                e.stopPropagation(); 
                setBoxes(prev => prev.filter(b => b.id !== box.id));
                setConnections(prev => prev.filter(c => c.fromId !== box.id && c.toId !== box.id));
              }}
            >
              🗑️
            </button>
          </div>
          
          {/* Role Dropdown */}
            <select
            className="box-select"
              value={box.role || ''}
              onChange={e => handleBoxChange(box.id, 'role', e.target.value)}
            >
              <option value="">Select Role</option>
              <option value="coordinator">Coordinator</option>
              <option value="coder">Coder</option>
              <option value="tester">Tester</option>
              <option value="runner">Runner</option>
              <option value="reviewer">Reviewer</option>
              <option value="analyst">Analyst</option>
              <option value="custom">Custom</option>
            </select>
          
          {/* Role Description Textarea */}
            <textarea
            className="box-textarea"
              placeholder="Describe the agent's role and responsibilities..."
              value={box.roleDescription}
              onChange={e => handleBoxChange(box.id, 'roleDescription', e.target.value)}
          />
          
          {/* Model Selection */}
            <select
            className="box-select"
            value={box.model || (isOnlineMode ? (onlineModelOptions[0]?.value || 'mistral-small') : 'codellama')}
              onChange={e => handleBoxChange(box.id, 'model', e.target.value)}
              disabled={isOnlineMode && modelsLoading}
            >
              {isOnlineMode && modelsLoading ? (
                <option value="">Loading models...</option>
              ) : (
                (isOnlineMode ? onlineModelOptions : offlineModelOptions).map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))
              )}
            </select>
          
          {/* Output Display Area */}
          {boxMessages.length > 0 && (
            <div className="output-display">
              <div className="output-header">
                Latest Output:
              </div>
              <div className="output-content">
                {(() => {
                  const lastMessage = boxMessages[boxMessages.length - 1];
                  const content = lastMessage?.content || '';
                  const isLongMessage = content.length > 100;
                  const displayContent = isLongMessage 
                    ? content.substring(0, 100) + '...' 
                    : content;
                  
                  // Determine message direction
                  const isOutgoing = lastMessage?.fromAgent === box.agentType || lastMessage?.fromAgent === 'system';
                  const directionIcon = isOutgoing ? '📤' : '📥';
                  
                  return (
                    <div className="message-container">
                      <div className="message-header">
                        <span className="direction-icon" title={isOutgoing ? 'Outgoing' : 'Incoming'}>{directionIcon}</span>
                        <span className="message-preview">{displayContent}</span>
                      </div>
                      {isLongMessage && (
                        <div className="message-tooltip" title={content}>
                          <span className="tooltip-icon">ⓘ</span>
                        </div>
                      )}
                    </div>
                  );
                })()}
              </div>
              <div className="output-meta">
                <span className="message-count">{boxMessages.length} msg{boxMessages.length !== 1 ? 's' : ''}</span>
                <span className="message-time">{new Date(boxMessages[boxMessages.length - 1]?.timestamp || Date.now()).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
              </div>
            </div>
          )}
          
          {/* Resize handle */}
          <div
            className="resize-handle"
            onMouseDown={e => handleResizeMouseDown(e, box.id)}
          />
        </div>
      );
    });
  };

  return (
    <div style={{ 
      width: '100%', 
      height: '100%', 
      overflow: 'hidden',
      position: 'relative'
    }}>
      <div
        ref={canvasRef}
        className="manual-agents-canvas"
        data-theme={isDark ? 'dark' : 'light'}
        onMouseMove={handleCanvasMouseMove}
        onMouseUp={handleCanvasMouseUp}
        onClick={handleCanvasClick}
        style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          height: '100%',
          width: '100%',
          overflow: 'hidden'
        }}
      >
      {/* Top controls bar */}
      <div className="controls-bar">
        {/* Hidden input for Import */}
        <input
          type="file"
          accept="application/json,.json"
          ref={importInputRef}
          style={{ display: 'none' }}
          onChange={handleImportChange}
        />
        
        <div className="control-group">
          <button className="btn-control btn-primary" onClick={handleCreateBox}>
            <span style={{ fontSize: '14px' }}>➕</span>
          Add Agent
        </button>

        <button
            className={`btn-control ${connectMode ? 'btn-secondary' : 'btn-outline'}`}
          onClick={() => setConnectMode(prev => !prev)}
          title="Toggle Connect Mode (Esc to cancel)"
        >
            <span style={{ fontSize: '14px' }}>🕸️</span>
            {connectMode ? 'Connecting' : 'Connect'}
        </button>

          <button className="btn-control btn-danger" onClick={handleClearCanvas} title="Clear canvas">
            <span style={{ fontSize: '14px' }}>🧹</span>
          Clear
        </button>
        </div>

        <div className="control-group">
          <button className="btn-control btn-info" onClick={handleExport} title="Export canvas to JSON">
            <span style={{ fontSize: '14px' }}>📤</span>
          Export
        </button>
          
          <button className="btn-control btn-success" onClick={handleImportClick} title="Import canvas from JSON">
            <span style={{ fontSize: '14px' }}>📥</span>
          Import
        </button>
        </div>

        <div className="control-group">
          <button className="btn-control btn-outline" onClick={handleZoomOut} title="Zoom Out">
            <span style={{ fontSize: '16px' }}>🔍➖</span>
          </button>
          
          <button className="btn-control btn-outline" onClick={handleResetZoom} title={`Reset Zoom (${Math.round(canvasScale * 100)}%)`}>
            <span style={{ fontSize: '12px', fontWeight: 'bold' }}>{Math.round(canvasScale * 100)}%</span>
          </button>
          
          <button className="btn-control btn-outline" onClick={handleZoomIn} title="Zoom In">
            <span style={{ fontSize: '16px' }}>🔍➕</span>
          </button>
        </div>
        
        {/* Online/Offline Mode Toggle */}
          <div className="mode-toggle">
            <span style={{ fontSize: 12, fontWeight: 500, color: isDark ? '#ccc' : '#666', marginRight: 4 }}>
            Mode:
          </span>
          <button
              className={!isOnlineMode ? 'active' : ''}
            onClick={() => setIsOnlineMode(false)}
          >
            Offline
          </button>
          <button
              className={isOnlineMode ? 'active' : ''}
            onClick={() => setIsOnlineMode(true)}
          >
            Online
              {!onlineServiceConnected && <span style={{ marginLeft: 4, fontSize: 10, color: '#ef4444', fontWeight: 'bold' }}>!</span>}
              {onlineServiceConnected && geminiAvailable && <span style={{ marginLeft: 4, fontSize: 10, color: '#10b981', fontWeight: 'bold' }}>✨</span>}
          </button>
        </div>

        <div className="control-group" style={{ flex: 1, minWidth: 300 }}>
          {/* Status Indicators */}
          <div className={`status-indicator ${wsConnected ? 'status-live' : 'status-connecting'}`} style={{ display: 'none' }}>
            <span>{wsConnected ? '🔗' : '⏳'}</span>
            <span>{wsConnected ? 'Live' : 'Connecting'}</span>
          </div>
          
          {isOnlineMode && onlineServiceConnected && (
            <div className="status-indicator status-connected" style={{ display: 'none' }}>
              <span>🟢</span>
              <span>Online</span>
            </div>
          )}
          
          {/* Prompt Input */}
          <input
            className="input-control"
            type="text"
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            placeholder={isRunning ? "Workflow in progress..." : "Enter your prompt or command..."}
            disabled={isRunning}
            style={{ flex: 1, minWidth: 200 }}
          />
          
          <button
            className="btn-control btn-primary"
            onClick={handleRunFlow}
            disabled={isRunning}
          >
            {isRunning ? 'Running...' : 'Run Flow'}
          </button>
        </div>
      </div>

      {/* Canvas Area with proper scrolling */}
      <div 
        ref={scrollableCanvasRef}
        className="canvas-area" 
        style={{ 
          width: '100%', 
          flex: 1, // Take up remaining space after controls bar
          overflow: 'scroll',
          position: 'relative',
          minHeight: 0 // Important for flexbox
        }}>
        <div className="canvas-content" style={{
          position: 'relative',
          width: `${canvasBounds.maxX - canvasBounds.minX}px`,
          height: `${canvasBounds.maxY - canvasBounds.minY}px`,
          minWidth: `${canvasBounds.maxX - canvasBounds.minX}px`,
          minHeight: `${canvasBounds.maxY - canvasBounds.minY}px`,
          padding: '20px'
        }}>
          {/* Render agent boxes */}
          {renderBoxes()}
          
          {/* SVG Container to prevent overflow */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            overflow: 'hidden',
            pointerEvents: 'none',
            zIndex: 1
          }}>
            {/* Render connections */}
            {renderConnections()}
            
            {/* Connection drag preview */}
            {connectDrag && (
              <svg className="connections-svg" style={{ 
                position: 'absolute', 
                top: 0, 
                left: 0, 
                width: '100%', 
                height: '100%', 
                pointerEvents: 'none'
              }}>
                <path
                  d={getSmartBezierPath(
                    connectDrag.mouse.x,
                    connectDrag.mouse.y,
                    connectDrag.mouse.x,
                    connectDrag.mouse.y
                  )}
                  className="connection-path"
                  stroke="var(--secondary-color)"
                  strokeWidth="3"
                  fill="none"
                  strokeDasharray="5,5"
                />
              </svg>
            )}
          </div>
        </div>
      </div>
      
      {/* Live Conversation Display */}
      {(showConversation || agentMessages.length > 0) && (
        <div className="conversation-panel animate-slide-in-right" style={{ position: 'fixed', top: 150, right: 20, width: 380, maxHeight: 'calc(100vh - 180px)', minHeight: '250px', zIndex: 999 }}>
          <div className="conversation-header">
            <h3 className="conversation-title">
              <span>🗨️</span>
              <span>Live Conversation</span>
              {isRunning && (
                <div className="running-indicator">
                  <span className="running-dot"></span>
                  Running...
                </div>
              )}
            </h3>
            <button
              onClick={() => setAgentMessages([])}
              style={{
                background: 'transparent',
                color: isDark ? '#ccc' : '#666',
                border: 'none',
                cursor: 'pointer',
                fontSize: '14px',
                padding: '4px 8px',
                borderRadius: '4px',
              }}
              title="Clear messages"
            >
              ✕
            </button>
          </div>
          <div className="conversation-messages">
            {agentMessages.map((message, index) => (
              <div key={message.id || index} className="message-item">
                <div className="message-header">
                  <span className="message-sender">
                    {message.fromAgent} → {message.toAgent}
                  </span>
                  <span className="message-time">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="message-content">
                  {message.content}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>
      )}
      
      {/* Connection Details Popup */}
      {selectedConnectionId && (() => {
        const connection = connections.find(c => c.id === selectedConnectionId);
        if (!connection) return null;
        
        const fromBox = boxes.find(b => b.id === connection!.fromId);
        const toBox = boxes.find(b => b.id === connection!.toId);
        if (!fromBox || !toBox) return null;
        
        return (
          <div 
            className="connection-popup"
        style={{
              position: 'fixed',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              background: isDark ? 'rgba(24, 26, 32, 0.95)' : 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(20px)',
              border: `2px solid ${isDark ? '#374151' : '#e5e7eb'}`,
              borderRadius: '1rem',
              padding: '1.5rem',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
              zIndex: 1000,
              minWidth: '300px',
              maxWidth: '400px'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0, color: isDark ? '#fff' : '#1f2937', fontSize: '1.125rem', fontWeight: 600 }}>
                🔗 Agent Connection Flow
              </h3>
              <button
                onClick={() => setSelectedConnectionId(null)}
                style={{
                  background: 'transparent',
                  color: isDark ? '#ccc' : '#666',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '18px',
                  padding: '4px 8px',
                  borderRadius: '4px'
                }}
                title="Close"
              >
                ✕
              </button>
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                padding: '0.75rem',
                background: isDark ? 'rgba(55, 65, 81, 0.5)' : 'rgba(243, 244, 246, 0.5)',
                borderRadius: '0.5rem',
                marginBottom: '0.75rem'
              }}>
                <div style={{ flex: 1, textAlign: 'center' }}>
                  <div style={{ fontSize: '1rem', fontWeight: 600, color: isDark ? '#fff' : '#1f2937', marginBottom: '0.25rem' }}>
                    {fromBox!.role}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#f97316', marginBottom: '0.25rem', fontWeight: 500 }}>
                    {fromBox!.model || 'No model set'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: isDark ? '#9ca3af' : '#6b7280' }}>
                    ({connection!.fromSide} output)
                  </div>
                </div>
                <div style={{ margin: '0 1rem', fontSize: '1.5rem', color: '#f97316', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div>→</div>
                  <div style={{ fontSize: '0.6rem', color: isDark ? '#9ca3af' : '#6b7280', marginTop: '0.25rem' }}>sends to</div>
                </div>
                <div style={{ flex: 1, textAlign: 'center' }}>
                  <div style={{ fontSize: '1rem', fontWeight: 600, color: isDark ? '#fff' : '#1f2937', marginBottom: '0.25rem' }}>
                    {toBox!.role}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#f97316', marginBottom: '0.25rem', fontWeight: 500 }}>
                    {toBox!.model || 'No model set'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: isDark ? '#9ca3af' : '#6b7280' }}>
                    ({connection!.toSide} input)
                  </div>
                </div>
              </div>
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ 
                padding: '0.75rem',
                background: isDark ? 'rgba(79, 70, 229, 0.1)' : 'rgba(79, 70, 229, 0.05)',
                borderLeft: '3px solid #4f46e5',
                borderRadius: '0.375rem',
                fontSize: '0.8rem',
                color: isDark ? '#c7d2fe' : '#4338ca',
                lineHeight: 1.4
              }}>
                <strong>Data Flow:</strong> When {fromBox!.role} completes its task, the output will be automatically sent to {toBox!.role} for further processing. This creates a seamless workflow between the agents.
              </div>
            </div>
            
            {/* Agent-to-Agent Conversation */}
            {(() => {
              // Filter messages between the two connected agents
              // Match by role name (primary) or box ID (fallback)
              const connectionMessages = agentMessages.filter(msg => {
                const fromRole = fromBox!.role || fromBox!.agentType;
                const toRole = toBox!.role || toBox!.agentType;
                
                // Check if message is between these two agents (in either direction)
                // Try matching by role name first, then by box ID
                return (
                  (msg.fromAgent === fromRole && msg.toAgent === toRole) ||
                  (msg.fromAgent === toRole && msg.toAgent === fromRole) ||
                  (msg.fromAgent === fromBox!.id && msg.toAgent === toBox!.id) ||
                  (msg.fromAgent === toBox!.id && msg.toAgent === fromBox!.id)
                );
              });
              
              return (
                <div style={{ marginBottom: '1rem' }}>
                  <div style={{ 
                    fontSize: '0.875rem', 
                    color: isDark ? '#9ca3af' : '#6b7280', 
                    marginBottom: '0.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    💬 Agent Conversation
                    <span style={{ 
                      fontSize: '0.75rem', 
                      background: isDark ? 'rgba(55, 65, 81, 0.8)' : 'rgba(243, 244, 246, 0.8)',
                      padding: '0.125rem 0.375rem',
                      borderRadius: '0.25rem',
                      color: isDark ? '#d1d5db' : '#4b5563'
                    }}>
                      {connectionMessages.length} message{connectionMessages.length !== 1 ? 's' : ''}
                    </span>
                  </div>
                  
                  {connectionMessages.length > 0 ? (
                    <div style={{ 
                      maxHeight: '200px',
                      overflowY: 'auto',
                      background: isDark ? 'rgba(55, 65, 81, 0.3)' : 'rgba(243, 244, 246, 0.3)',
                      borderRadius: '0.5rem',
                      padding: '0.5rem',
                      border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`
                    }}>
                      {connectionMessages.map((message, index) => (
                        <div key={message.id || index} style={{ 
                          marginBottom: index < connectionMessages.length - 1 ? '0.75rem' : '0',
                          padding: '0.5rem',
                          background: isDark ? 'rgba(31, 41, 55, 0.5)' : 'rgba(255, 255, 255, 0.5)',
                          borderRadius: '0.375rem',
                          border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`
                        }}>
                          <div style={{ 
                            display: 'flex', 
                            justifyContent: 'space-between', 
                            alignItems: 'center',
                            marginBottom: '0.25rem'
                          }}>
                            <span style={{ 
                              fontSize: '0.75rem', 
                              fontWeight: 600,
                              color: isDark ? '#fbbf24' : '#d97706'
                            }}>
                              {message.fromAgent} → {message.toAgent}
                            </span>
                            <span style={{ 
                              fontSize: '0.625rem', 
                              color: isDark ? '#9ca3af' : '#6b7280'
                            }}>
                              {new Date(message.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                            </span>
                          </div>
                          <div style={{ 
                            fontSize: '0.75rem',
                            lineHeight: 1.4,
                            color: isDark ? '#e5e7eb' : '#374151',
                            wordWrap: 'break-word',
                            maxHeight: '60px',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            display: '-webkit-box',
                            WebkitLineClamp: 3,
                            WebkitBoxOrient: 'vertical'
                          }}>
                            {message.content}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div style={{ 
                      padding: '1rem',
                      textAlign: 'center',
                      background: isDark ? 'rgba(55, 65, 81, 0.3)' : 'rgba(243, 244, 246, 0.3)',
                      borderRadius: '0.5rem',
                      border: `1px dashed ${isDark ? '#374151' : '#e5e7eb'}`,
                      color: isDark ? '#9ca3af' : '#6b7280',
                      fontSize: '0.8rem'
                    }}>
                      No messages yet between these agents
                      <div style={{ fontSize: '0.7rem', marginTop: '0.25rem', opacity: 0.8 }}>
                        Messages will appear here when agents communicate
                      </div>
                    </div>
                  )}
                </div>
              );
            })()}
            
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ fontSize: '0.875rem', color: isDark ? '#9ca3af' : '#6b7280', marginBottom: '0.5rem' }}>Connection ID</div>
              <div style={{ 
                fontSize: '0.75rem', 
                fontFamily: 'monospace', 
                background: isDark ? 'rgba(55, 65, 81, 0.5)' : 'rgba(243, 244, 246, 0.5)',
                padding: '0.5rem',
                borderRadius: '0.25rem',
                color: isDark ? '#d1d5db' : '#4b5563'
              }}>
                {connection!.id}
              </div>
            </div>
            
            <div style={{ marginTop: '1rem' }}>
              <button
                onClick={() => {
                  setConnections(prev => prev.filter(c => c.id !== selectedConnectionId));
                  setSelectedConnectionId(null);
                }}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: '#ef4444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  transition: 'background 0.15s ease'
                }}
                onMouseOver={(e) => e.currentTarget.style.background = '#dc2626'}
                onMouseOut={(e) => e.currentTarget.style.background = '#ef4444'}
              >
                🗑️ Remove Connection
              </button>
            </div>
          </div>
        );
      })()}

      
      {/* Empty state when no agents */}
      {boxes.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🤖</div>
          <div className="empty-title">No Agents Created</div>
          <div className="empty-description">
            Click "Add Agent" to create your first agent and start building workflows
          </div>
        </div>
      )}

      {/* GitHub Upload Confirmation Modal */}
      {showUploadModal && uploadProjectInfo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Upload to GitHub
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Review your generated files before uploading
              </p>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-hidden flex flex-col">
              {/* Project Info */}
              <div className="px-6 pt-4 pb-2">
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-1 text-sm">
                    Project: {uploadProjectInfo.project_name}
                  </h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    {projectFiles.length} files ready to upload
                  </p>
                </div>
              </div>

              {/* File Explorer */}
              <div className="flex-1 flex overflow-hidden px-6 pb-4">
                {/* File List */}
                <div className="w-1/3 border-r border-gray-200 dark:border-gray-700 pr-4">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2 text-sm">
                    Files
                  </h3>
                  <div className="space-y-1 overflow-y-auto max-h-96">
                    {loadingFiles ? (
                      <div className="text-sm text-gray-500 dark:text-gray-400">Loading files...</div>
                    ) : projectFiles.length === 0 ? (
                      <div className="text-sm text-gray-500 dark:text-gray-400">No files found</div>
                    ) : (
                      projectFiles.map((file, index) => (
                        <button
                          key={index}
                          onClick={() => setSelectedFile(file)}
                          className={`w-full text-left px-3 py-2 rounded text-sm flex items-center space-x-2 transition-colors ${
                            selectedFile?.path === file.path
                              ? 'bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100'
                              : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                          }`}
                        >
                          <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"/>
                          </svg>
                          <div className="flex-1 min-w-0">
                            <div className="font-medium truncate">{file.name}</div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">{file.path}</div>
                          </div>
                        </button>
                      ))
                    )}
                  </div>
                </div>

                {/* File Content Preview */}
                <div className="flex-1 pl-4">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2 text-sm">
                    Preview
                  </h3>
                  {selectedFile ? (
                    <div className="h-96 overflow-auto bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-700 p-4">
                      <div className="mb-2 pb-2 border-b border-gray-200 dark:border-gray-700">
                        <div className="text-xs font-mono text-gray-600 dark:text-gray-400">{selectedFile.path}</div>
                        <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                          {selectedFile.size} bytes • {selectedFile.type}
                        </div>
                      </div>
                      <pre className="text-xs font-mono whitespace-pre-wrap break-words text-gray-800 dark:text-gray-200">
                        {selectedFile.content}
                      </pre>
                    </div>
                  ) : (
                    <div className="h-96 flex items-center justify-center bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-700">
                      <div className="text-center text-gray-500 dark:text-gray-400">
                        <svg className="w-12 h-12 mx-auto mb-2 opacity-50" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"/>
                        </svg>
                        <p className="text-sm">Select a file to preview</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Warning Notice */}
              <div className="px-6 pb-4">
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-700">
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-yellow-600 dark:text-yellow-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"/>
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                      Repository Visibility
                    </p>
                    <p className="text-xs text-yellow-700 dark:text-yellow-300 mt-1">
                      This will create a <strong>public</strong> repository visible to everyone on GitHub.
                    </p>
                  </div>
                </div>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowUploadModal(false);
                  setUploadProjectInfo(null);
                  setProjectFiles([]);
                  setSelectedFile(null);
                }}
                disabled={uploadingToGithub}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleGitHubUpload}
                disabled={uploadingToGithub}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium disabled:opacity-50 flex items-center"
              >
                {uploadingToGithub ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    Uploading...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd"/>
                    </svg>
                    Upload to GitHub
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
};

export default ManualAgentCanvas; 