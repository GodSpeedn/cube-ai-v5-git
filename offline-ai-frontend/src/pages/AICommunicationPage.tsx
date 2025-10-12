import React, { useState, useEffect, useRef } from 'react';
import AgentVisualization from '../components/AgentVisualization';
import ConversationHistory, { ConversationHistoryRef } from '../components/ConversationHistory';
import { testBackendConnection, createConversation, getConversation, chatWithAgents } from '../services/api';
import { useTheme } from '../hooks/useTheme';
import websocketService from '../services/websocket';

interface AIBlock {
  id: string;
  name: string;
  type: 'coordinator' | 'coder' | 'tester' | 'runner';
  content: string;
  timestamp: string;
  iteration: number;
}

export default function AICommunicationPage() {
  const { isDark } = useTheme();
  const [interactions, setInteractions] = useState<AIBlock[]>([]);
  const [backendConnected, setBackendConnected] = useState<boolean | null>(null);
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>(undefined);
  const [selectedConversation, setSelectedConversation] = useState<any>(null);
  const [isHistoryCollapsed, setIsHistoryCollapsed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // WebSocket state for real-time updates
  const [wsConnected, setWsConnected] = useState(false);
  const [realTimeMessages, setRealTimeMessages] = useState<AIBlock[]>([]);
  
  // Ref to ConversationHistory component for refreshing
  const conversationHistoryRef = useRef<ConversationHistoryRef>(null);

  // Test backend connection on component mount
  useEffect(() => {
    const testConnection = async () => {
      try {
        setError(null);
        const connected = await testBackendConnection();
        setBackendConnected(connected);
      } catch (error) {
        console.error('Backend connection test failed:', error);
        setBackendConnected(false);
        setError('Backend connection failed');
      }
    };

    testConnection();
    
    // Test connection every 30 seconds
    const interval = setInterval(testConnection, 30000);
    return () => clearInterval(interval);
  }, []);


  // WebSocket event handlers for real-time updates
  useEffect(() => {
    const handleConnected = () => {
      console.log('🔗 WebSocket connected');
      setWsConnected(true);
    };

    const handleDisconnected = () => {
      console.log('🔌 WebSocket disconnected');
      setWsConnected(false);
    };

    const handleAgentUpdate = (data: any) => {
      console.log('📨 Received agent update:', data);
      
      // Create agent block for real-time display
      const agentBlock: AIBlock = {
        id: `realtime-${Date.now()}-${Math.random()}`,
        name: `${data.agent_id} (${data.status})`,
        type: data.agent_id === 'coder' ? 'coder' : 
              data.agent_id === 'tester' ? 'tester' : 
              data.agent_id === 'runner' ? 'runner' : 'coordinator',
        content: data.message,
        timestamp: data.timestamp,
        iteration: realTimeMessages.length + 1
      };

      setRealTimeMessages(prev => [...prev, agentBlock]);
      setInteractions(prev => [...prev, agentBlock]);
    };

    const handlePong = (data: any) => {
      console.log('🏓 Received pong:', data);
      // WebSocket is working!
    };

    const handleError = (data: any) => {
      console.error('❌ WebSocket error:', data);
      setError(`WebSocket connection failed: ${data.error?.message || 'Unknown error'}`);
    };

    // Register event listeners
    websocketService.on('connected', handleConnected);
    websocketService.on('disconnected', handleDisconnected);
    websocketService.on('agent_update', handleAgentUpdate);
    websocketService.on('pong', handlePong);
    websocketService.on('error', handleError);

    // Connect to WebSocket
    websocketService.connect();

    // Cleanup
    return () => {
      websocketService.off('connected', handleConnected);
      websocketService.off('disconnected', handleDisconnected);
      websocketService.off('agent_update', handleAgentUpdate);
      websocketService.off('pong', handlePong);
      websocketService.off('error', handleError);
    };
  }, [realTimeMessages.length]);

  // Conversation handlers
  const handleNewConversation = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const title = prompt('Enter conversation title:') || 'New Conversation';
      const result = await createConversation(title);
      setCurrentConversationId(result.conversation_id);
      setSelectedConversation(null);
      
      // Refresh the conversation list to show the new conversation
      if (conversationHistoryRef.current) {
        conversationHistoryRef.current.refresh();
      }
    } catch (error) {
      console.error('Failed to create conversation:', error);
      setError('Failed to create conversation');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectConversation = async (conversationId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      setCurrentConversationId(conversationId);
      const conversation = await getConversation(conversationId);
      setSelectedConversation(conversation);
      
      if (conversation.messages && conversation.messages.length > 0) {
        const conversationInteractions: AIBlock[] = conversation.messages.map((msg: any, index: number) => {
          let agentType: 'coordinator' | 'coder' | 'tester' | 'runner' = 'coordinator';
          let agentName = msg.from_agent || 'User';
          
          if (agentName.toLowerCase().includes('coder') || agentName.toLowerCase().includes('mistral')) {
            agentType = 'coder';
          } else if (agentName.toLowerCase().includes('tester') || agentName.toLowerCase().includes('phi')) {
            agentType = 'tester';
          } else if (agentName.toLowerCase().includes('runner') || agentName.toLowerCase().includes('llama')) {
            agentType = 'runner';
          } else if (agentName.toLowerCase().includes('coordinator') || agentName.toLowerCase().includes('coordinator')) {
            agentType = 'coordinator';
          }
          
          return {
            id: `conv-${conversationId}-${index}`,
            name: agentName,
            type: agentType,
            content: msg.content,
            timestamp: msg.timestamp || new Date().toISOString(),
            iteration: index + 1
          };
        });
        
        setInteractions(conversationInteractions);
      } else {
        setInteractions([]);
      }
    } catch (error) {
      console.error('Failed to select conversation:', error);
      setError('Failed to load conversation');
    } finally {
      setIsLoading(false);
    }
  };

  // Example interaction data
  useEffect(() => {
    const exampleInteractions: AIBlock[] = [
      {
        id: '1',
        name: 'Coordinator Agent',
        type: 'coordinator',
        content: 'Ready to coordinate AI tasks...',
        timestamp: new Date(Date.now() - 5000).toISOString(),
        iteration: 1
      },
      {
        id: '2',
        name: 'Coder Agent (Mistral)',
        type: 'coder',
        content: 'Ready to generate and refine code...',
        timestamp: new Date(Date.now() - 4000).toISOString(),
        iteration: 1
      },
      {
        id: '3',
        name: 'Tester Agent (Phi)',
        type: 'tester',
        content: 'Ready to generate unit tests...',
        timestamp: new Date(Date.now() - 3000).toISOString(),
        iteration: 1
      },
      {
        id: '4',
        name: 'Runner Agent (Llama3.2)',
        type: 'runner',
        content: 'Ready to run tests and report outcomes...',
        timestamp: new Date(Date.now() - 2000).toISOString(),
        iteration: 1
      }
    ];
    setInteractions(exampleInteractions);
  }, []);

  const handlePromptSubmit = async (prompt: string) => {
    try {
      // Only show loading if WebSocket is not connected
      if (!wsConnected) {
        setIsLoading(true);
      }
      setError(null);
      
      // Clear real-time messages for new conversation
      setRealTimeMessages([]);
      
      // Create user interaction block
      const userInteraction: AIBlock = {
        id: `user-${Date.now()}`,
        name: 'User',
        type: 'coordinator',
        content: prompt,
        timestamp: new Date().toISOString(),
        iteration: 1
      };

      // Add user message to real-time messages and interactions
      setRealTimeMessages([userInteraction]);
      setInteractions(prev => [...prev, userInteraction]);

      // If WebSocket is connected, use real-time updates
      if (wsConnected) {
        console.log('🔗 WebSocket connected - using real-time communication');
        // The WebSocket will handle real-time updates
        // We still need to call the API to start the workflow
      } else {
        console.log('⚠️ WebSocket not connected - using API fallback');
      }
      const response = await chatWithAgents({
        prompt,
        conversation_id: currentConversationId
      });

      // Create AI interaction blocks based on response
      const aiInteractions: AIBlock[] = [];

      if (response.code) {
        aiInteractions.push({
          id: `coder-${Date.now()}`,
          name: 'Coder Agent (CodeLlama)',
          type: 'coder',
          content: response.code,
          timestamp: new Date().toISOString(),
          iteration: 2
        });
      }

      if (response.tests) {
        aiInteractions.push({
          id: `tester-${Date.now()}`,
          name: 'Tester Agent (Mistral)',
          type: 'tester',
          content: response.tests,
          timestamp: new Date().toISOString(),
          iteration: 3
        });
      }

      if (response.test_results) {
        aiInteractions.push({
          id: `runner-${Date.now()}`,
          name: 'Runner Agent (Llama2)',
          type: 'runner',
          content: response.test_results,
          timestamp: new Date().toISOString(),
          iteration: 4
        });
      }
      
      // Update interactions with new blocks
      setInteractions(prev => [...prev, ...aiInteractions]);
      
      // Refresh conversation list to show updated conversation
      if (conversationHistoryRef.current) {
        conversationHistoryRef.current.refresh();
      }
      
    } catch (error) {
      console.error('Failed to submit prompt:', error);
      setError('Failed to submit prompt');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSidebarToggle = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsHistoryCollapsed(!isHistoryCollapsed);
  };

  return (
    <div className="h-full relative flex overflow-hidden">
      {/* Error Display */}
      {error && (
        <div className={`absolute top-16 left-4 right-4 z-50 p-3 rounded text-sm ${
          isDark ? 'bg-red-900/90 text-red-200' : 'bg-red-100 text-red-800'
        }`}>
          {error}
        </div>
      )}

      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-black/20 z-40 flex items-center justify-center">
          <div className={`p-4 rounded ${
            isDark ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'
          }`}>
            Loading...
          </div>
        </div>
      )}

      {/* Main AI Visualization Area */}
      <div className={`flex-1 min-w-0 ${isHistoryCollapsed ? '' : 'mr-80'}`}>
        <AgentVisualization 
          isDark={isDark}
          interactions={interactions}
          onPromptSubmit={handlePromptSubmit}
        />
      </div>

      {/* Collapsible Conversation History Sidebar */}
      <div className={`absolute right-0 top-0 h-full border-l shadow-lg transition-all duration-300 ${
        isDark ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'
      } ${isHistoryCollapsed ? 'w-12' : 'w-80'}`}>
        {/* Collapse Toggle Button */}
        <button
          type="button"
          onClick={handleSidebarToggle}
          className="absolute -left-3 top-4 bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center hover:bg-blue-700 transition-colors"
        >
          {isHistoryCollapsed ? '›' : '‹'}
        </button>

        {/* Conversation History Content */}
        {!isHistoryCollapsed && (
          <div className="h-full p-4 overflow-hidden">
            <ConversationHistory
              ref={conversationHistoryRef}
              onSelectConversation={handleSelectConversation}
              onNewConversation={handleNewConversation}
              currentConversationId={currentConversationId}
            />
          </div>
        )}
      </div>

      {/* Backend Connection Status */}
      {backendConnected !== null && (
        <div className={`absolute top-4 left-4 flex items-center space-x-2 px-3 py-1 rounded text-sm ${
          backendConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          <div className={`w-2 h-2 rounded-full ${
            backendConnected ? 'bg-green-500' : 'bg-red-500'
          }`}></div>
          <span>
            {backendConnected ? 'Backend Connected' : 'Backend Disconnected'}
          </span>
        </div>
      )}

      {/* WebSocket Status */}
      <div className={`absolute top-4 left-64 flex items-center space-x-2 px-3 py-1 rounded text-sm ${
        wsConnected ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
      }`} style={{ display: 'none' }}>
        <div className={`w-2 h-2 rounded-full ${
          wsConnected ? 'bg-green-500' : 'bg-yellow-500'
        }`}></div>
        <span>
          {wsConnected ? 'Real-time Updates' : 'API Mode'}
        </span>
        <button
          onClick={() => websocketService.ping()}
          className="ml-2 px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Test WS
        </button>
      </div>
    </div>
  );
} 