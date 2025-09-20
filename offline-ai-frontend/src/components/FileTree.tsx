import { useEffect, useState } from "react";
import { getGeneratedFiles, getFileContent } from "../services/api";
import { useTheme } from "../hooks/useTheme";
import FolderTree from "./FolderTree";

interface Conversation {
  id: string;
  title: string;
  type: 'offline' | 'online' | 'manual' | 'workflow';
  created_at: string;
  updated_at: string;
  is_active: boolean;
  metadata: Record<string, any>;
}

interface Message {
  id: string;
  conversation_id: string;
  type: 'user' | 'agent' | 'system' | 'error' | 'status';
  content: string;
  agent_id?: string;
  agent_role?: string;
  timestamp: string;
  metadata: Record<string, any>;
}

interface FileItem {
  name: string;
  path: string;
  type: 'file' | 'folder';
  size?: number;
  modified?: number;
  content?: string;
  is_test?: boolean;
  extension?: string;
  error?: string;
  file_count?: number;
  children?: FileItem[];
}

export default function FileTree() {
  const { isDark } = useTheme();
  const [activeTab, setActiveTab] = useState<'files' | 'conversations' | 'projects'>('files');
  
  // File-related states
  const [files, setFiles] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [newFiles, setNewFiles] = useState<Set<string>>(new Set());
  const [notification, setNotification] = useState<string | null>(null);
  const [showProjects, setShowProjects] = useState(false);
  
  // Conversation-related states
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [conversationMessages, setConversationMessages] = useState<Message[]>([]);
  const [conversationLoading, setConversationLoading] = useState(false);
  const [newConversationTitle, setNewConversationTitle] = useState('');
  const [newConversationType, setNewConversationType] = useState<'offline' | 'online' | 'manual' | 'workflow'>('offline');
  
  // Project-related states
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProject, setSelectedProject] = useState<any>(null);
  const [projectFiles, setProjectFiles] = useState<FileItem[]>([]);
  const [projectFolderStructure, setProjectFolderStructure] = useState<FileItem[]>([]);
  const [projectLoading, setProjectLoading] = useState(false);
  const [showFolderView, setShowFolderView] = useState(true);

  // Load conversations
  const loadConversations = async () => {
    try {
      setConversationLoading(true);
      const response = await fetch('http://localhost:8000/conversations');
      if (response.ok) {
        const data = await response.json();
        setConversations(data.conversations);
      } else {
        console.error('Failed to load conversations');
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setConversationLoading(false);
    }
  };

  // Load conversation messages
  const loadConversationMessages = async (conversationId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/conversations/${conversationId}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedConversation(data.conversation);
        setConversationMessages(data.messages);
      }
    } catch (error) {
      console.error('Failed to load conversation messages:', error);
    }
  };

  // Create new conversation
  const createConversation = async () => {
    if (!newConversationTitle.trim()) return;
    
    try {
      const response = await fetch('http://localhost:8000/conversations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newConversationTitle,
          type: newConversationType
        })
      });

      if (response.ok) {
        setNewConversationTitle('');
        await loadConversations();
      }
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  // Load projects
  const loadProjects = async () => {
    try {
      setProjectLoading(true);
      const response = await fetch('http://localhost:8000/projects');
      if (response.ok) {
        const data = await response.json();
        setProjects(data.projects);
      } else {
        console.error('Failed to load projects');
      }
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setProjectLoading(false);
    }
  };

  // Load project files
  const loadProjectFiles = async (projectName: string) => {
    try {
      const response = await fetch(`http://localhost:8000/projects/${projectName}/files`);
      if (response.ok) {
        const data = await response.json();
        setSelectedProject({ name: projectName, ...data });
        setProjectFiles(data.files || []);
        setProjectFolderStructure(data.folder_structure || []);
        console.log('📁 Project folder structure loaded:', data.folder_structure);
      }
    } catch (error) {
      console.error('Failed to load project files:', error);
    }
  };

  useEffect(() => {
    // Load saved files when component mounts
    const loadFiles = async () => {
      try {
        const data = await getGeneratedFiles();
        setFiles(data.files || []);
        setError(null);
      } catch (error) {
        console.error('Failed to load files:', error);
        setError('Failed to load files');
      }
    };

    loadFiles();
    loadConversations();
    loadProjects();

    // Reload files when a new one is generated
    const refresh = async () => {
      try {
        setIsRefreshing(true);
        const data = await getGeneratedFiles();
        setFiles(prevFiles => {
          const newFilesList = data.files || [];
          // Only update if files have actually changed
          if (JSON.stringify(prevFiles.sort()) !== JSON.stringify(newFilesList.sort())) {
            console.log('🔄 Files updated:', newFilesList);
            setLastUpdate(new Date());
            
            // Track new files
            const prevFilesSet = new Set(prevFiles);
            const newFilesSet = new Set(newFilesList);
            const actuallyNewFiles = newFilesList.filter(file => !prevFilesSet.has(file));
            
            if (actuallyNewFiles.length > 0) {
              console.log('🆕 New files detected:', actuallyNewFiles);
              setNewFiles(prev => {
                const updated = new Set(prev);
                actuallyNewFiles.forEach(file => updated.add(file));
                return updated;
              });
              
              // Show notification
              setNotification(`🆕 ${actuallyNewFiles.length} new file(s) detected!`);
              setTimeout(() => setNotification(null), 3000);
              
              // Clear new file indicators after 5 seconds
              setTimeout(() => {
                setNewFiles(prev => {
                  const updated = new Set(prev);
                  actuallyNewFiles.forEach(file => updated.delete(file));
                  return updated;
                });
              }, 5000);
            }
            
            return newFilesList;
          }
          return prevFiles;
        });
        setError(null);
      } catch (error) {
        console.error('Failed to refresh files:', error);
        setError('Failed to refresh files');
      } finally {
        setIsRefreshing(false);
      }
    };

    // Listen for file generation events
    window.addEventListener("ai:file-generate", refresh);
    
    // Poll for new files every 2 seconds when component is visible
    const pollInterval = setInterval(refresh, 2000);
    
    return () => {
      window.removeEventListener("ai:file-generate", refresh);
      clearInterval(pollInterval);
    };
  }, []);

  // Load projects when toggle is enabled
  useEffect(() => {
    if (showProjects) {
      loadProjects();
    }
  }, [showProjects]);

  const handleFileClick = async (file: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      const code = await getFileContent(file);
      window.dispatchEvent(new CustomEvent("ai:file-select", {
        detail: {
          file: file,
          code: code
        }
      }));
      setError(null);
    } catch (error) {
      console.error('Failed to load file content:', error);
      setError(`Failed to load ${file}`);
    }
  };

  const handleProjectFileClick = (file: FileItem) => {
    if (file.type === 'file' && file.content) {
      window.dispatchEvent(new CustomEvent("ai:file-select", {
        detail: {
          file: file.path,
          code: file.content
        }
      }));
      setError(null);
    }
  };

  return (
    <div className={`w-80 p-4 border-r overflow-y-auto ${
      isDark ? 'bg-gray-900 text-white border-gray-700' : 'bg-gray-100 text-gray-900 border-gray-300'
    }`}>
      {/* Tab Navigation */}
      <div className="flex mb-4 border-b border-gray-600">
        <button
          onClick={() => setActiveTab('files')}
          className={`px-3 py-2 text-sm font-medium ${
            activeTab === 'files'
              ? (isDark ? 'text-blue-400 border-b-2 border-blue-400' : 'text-blue-600 border-b-2 border-blue-600')
              : (isDark ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900')
          }`}
        >
          📁 Files
        </button>
        <button
          onClick={() => setActiveTab('conversations')}
          className={`px-3 py-2 text-sm font-medium ${
            activeTab === 'conversations'
              ? (isDark ? 'text-blue-400 border-b-2 border-blue-400' : 'text-blue-600 border-b-2 border-blue-600')
              : (isDark ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900')
          }`}
        >
          💬 Conversations
        </button>
        <button
          onClick={() => setActiveTab('projects')}
          className={`px-3 py-2 text-sm font-medium ${
            activeTab === 'projects'
              ? (isDark ? 'text-blue-400 border-b-2 border-blue-400' : 'text-blue-600 border-b-2 border-blue-600')
              : (isDark ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900')
          }`}
        >
          🚀 Projects
        </button>
      </div>

      {/* Files Tab */}
      {activeTab === 'files' && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-bold">Generated Files</h2>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowProjects(!showProjects)}
                className={`px-2 py-1 text-xs rounded ${
                  showProjects 
                    ? (isDark ? 'bg-blue-600 text-white' : 'bg-blue-600 text-white')
                    : (isDark ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'bg-gray-200 text-gray-700 hover:bg-gray-300')
                }`}
                title="Toggle projects view"
              >
                🚀 Projects
              </button>
              <button
                onClick={async () => {
                  try {
                    setIsRefreshing(true);
                    const data = await getGeneratedFiles();
                    setFiles(data.files || []);
                    setLastUpdate(new Date());
                    setError(null);
                    if (showProjects) {
                      await loadProjects();
                    }
                  } catch (error) {
                    console.error('Failed to refresh files:', error);
                    setError('Failed to refresh files');
                  } finally {
                    setIsRefreshing(false);
                  }
                }}
                className={`${isDark ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors`}
                title="Refresh files"
                disabled={isRefreshing}
              >
                {isRefreshing ? (
                  <div className="animate-spin">⟳</div>
                ) : (
                  <span>🔄</span>
                )}
              </button>
              <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                {lastUpdate.toLocaleTimeString()}
              </span>
            </div>
          </div>
          {error && (
            <div className={`text-sm mb-2 p-2 rounded ${
              isDark ? 'text-red-400 bg-red-900/20' : 'text-red-600 bg-red-100'
            }`}>
              {error}
            </div>
          )}
          {notification && (
            <div className={`text-sm mb-2 p-2 rounded animate-pulse ${
              isDark ? 'text-green-400 bg-green-900/20' : 'text-green-600 bg-green-100'
            }`}>
              {notification}
            </div>
          )}
          <ul className="space-y-1 text-sm">
            {/* Regular Files */}
            {files.map(file => (
              <li
                key={file}
                className={`cursor-pointer hover:underline p-1 rounded transition-all duration-300 ${
                  newFiles.has(file) 
                    ? (isDark ? 'bg-green-900/30 border-l-2 border-green-400' : 'bg-green-100 border-l-2 border-green-400')
                    : (isDark ? 'hover:bg-gray-800' : 'hover:bg-gray-200')
                }`}
                onClick={(e) => handleFileClick(file, e)}
              >
                <div className="flex items-center space-x-2">
                  <span>📄 {file}</span>
                  {newFiles.has(file) && (
                    <span className={`text-xs animate-pulse ${
                      isDark ? 'text-green-400' : 'text-green-600'
                    }`}>🆕</span>
                  )}
                </div>
              </li>
            ))}
            
            {/* Projects (when toggle is enabled) */}
            {showProjects && projects.map(project => (
              <li
                key={project.name}
                className={`cursor-pointer hover:underline p-1 rounded transition-all duration-300 ${
                  isDark ? 'hover:bg-gray-800' : 'hover:bg-gray-200'
                }`}
                onClick={() => loadProjectFiles(project.name)}
              >
                <div className="flex items-center space-x-2">
                  <span>🚀 {project.name}</span>
                  <span className={`text-xs ${
                    isDark ? 'text-gray-400' : 'text-gray-500'
                  }`}>
                    ({project.file_count} files)
                  </span>
                  {project.github_repo && (
                    <span className={`text-xs ${
                      isDark ? 'text-green-400' : 'text-green-600'
                    }`}>
                      🐙
                    </span>
                  )}
                </div>
              </li>
            ))}
          </ul>
          
          {/* Project Files Detail (when project is selected) */}
          {showProjects && selectedProject && (
            <div className={`mt-4 p-3 rounded ${
              isDark ? 'bg-gray-800' : 'bg-gray-200'
            }`}>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold">
                  Files in {selectedProject.name}
                </h3>
                <button
                  onClick={() => setShowFolderView(!showFolderView)}
                  className={`px-2 py-1 text-xs rounded ${
                    showFolderView 
                      ? (isDark ? 'bg-blue-600 text-white' : 'bg-blue-600 text-white')
                      : (isDark ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'bg-gray-200 text-gray-700 hover:bg-gray-300')
                  }`}
                  title="Toggle folder view"
                >
                  {showFolderView ? '📁' : '📄'}
                </button>
              </div>
              
              <div className="max-h-64 overflow-y-auto">
                {showFolderView && projectFolderStructure.length > 0 ? (
                  <FolderTree
                    items={projectFolderStructure}
                    onFileClick={handleProjectFileClick}
                    isDark={isDark}
                  />
                ) : (
                  <div className="space-y-1">
                    {projectFiles.map((file) => (
                      <div
                        key={file.name}
                        className={`p-2 rounded text-xs cursor-pointer hover:bg-opacity-50 ${
                          file.is_test 
                            ? (isDark ? 'bg-green-900/20 hover:bg-green-900/30' : 'bg-green-100 hover:bg-green-200')
                            : (isDark ? 'bg-blue-900/20 hover:bg-blue-900/30' : 'bg-blue-100 hover:bg-blue-200')
                        }`}
                        onClick={() => handleProjectFileClick(file)}
                      >
                        <div className="flex justify-between items-center">
                          <span className="font-medium flex items-center space-x-1">
                            <span>{file.extension === '.py' ? '🐍' : '📄'}</span>
                            <span>{file.name}</span>
                            {file.is_test && <span title="Test file">🧪</span>}
                          </span>
                          <span className={`${
                            isDark ? 'text-gray-400' : 'text-gray-500'
                          }`}>
                            {file.extension}
                          </span>
                        </div>
                        <div className={`text-xs ${
                          isDark ? 'text-gray-400' : 'text-gray-500'
                        }`}>
                          {file.size ? Math.round(file.size / 1024) + 'KB' : '0KB'} • {file.modified ? new Date(file.modified * 1000).toLocaleDateString() : 'Unknown date'}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Conversations Tab */}
      {activeTab === 'conversations' && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-bold">Conversations</h2>
            <button
              onClick={loadConversations}
              className={`${isDark ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors`}
              title="Refresh conversations"
              disabled={conversationLoading}
            >
              {conversationLoading ? (
                <div className="animate-spin">⟳</div>
              ) : (
                <span>🔄</span>
              )}
            </button>
          </div>

          {/* Create New Conversation */}
          <div className={`mb-4 p-3 rounded ${
            isDark ? 'bg-gray-800' : 'bg-gray-200'
          }`}>
            <h3 className="text-sm font-semibold mb-2">New Conversation</h3>
            <div className="space-y-2">
              <input
                type="text"
                value={newConversationTitle}
                onChange={(e) => setNewConversationTitle(e.target.value)}
                placeholder="Conversation title"
                className={`w-full px-2 py-1 text-sm rounded border ${
                  isDark ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
                }`}
              />
              <select
                value={newConversationType}
                onChange={(e) => setNewConversationType(e.target.value as any)}
                className={`w-full px-2 py-1 text-sm rounded border ${
                  isDark ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
                }`}
              >
                <option value="offline">Offline</option>
                <option value="online">Online</option>
                <option value="manual">Manual</option>
                <option value="workflow">Workflow</option>
              </select>
              <button
                onClick={createConversation}
                className="w-full px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Create
              </button>
            </div>
          </div>

          {/* Conversations List */}
          <div className="space-y-2">
            {conversations.map((conv) => (
              <div
                key={conv.id}
                className={`p-2 rounded cursor-pointer transition-colors ${
                  selectedConversation?.id === conv.id
                    ? (isDark ? 'bg-blue-900/30 border border-blue-600' : 'bg-blue-100 border border-blue-300')
                    : (isDark ? 'bg-gray-800 hover:bg-gray-700' : 'bg-gray-200 hover:bg-gray-300')
                }`}
                onClick={() => loadConversationMessages(conv.id)}
              >
                <div className="text-sm font-medium">{conv.title}</div>
                <div className={`text-xs ${
                  isDark ? 'text-gray-400' : 'text-gray-500'
                }`}>
                  {conv.type} • {new Date(conv.updated_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>

          {/* Selected Conversation Messages */}
          {selectedConversation && (
            <div className={`mt-4 p-3 rounded ${
              isDark ? 'bg-gray-800' : 'bg-gray-200'
            }`}>
              <h3 className="text-sm font-semibold mb-2">
                Messages in {selectedConversation.title}
              </h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {conversationMessages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`p-2 rounded text-xs ${
                      msg.type === 'user' 
                        ? (isDark ? 'bg-blue-900/20' : 'bg-blue-100')
                        : msg.type === 'agent'
                        ? (isDark ? 'bg-green-900/20' : 'bg-green-100')
                        : (isDark ? 'bg-gray-700' : 'bg-gray-100')
                    }`}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-medium">
                        {msg.agent_role || msg.type}
                      </span>
                      <span className={`${
                        isDark ? 'text-gray-400' : 'text-gray-500'
                      }`}>
                        {new Date(msg.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="text-xs">{msg.content}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Projects Tab */}
      {activeTab === 'projects' && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-bold">AI Projects</h2>
            <button
              onClick={loadProjects}
              className={`${isDark ? 'text-gray-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'} transition-colors`}
              title="Refresh projects"
              disabled={projectLoading}
            >
              {projectLoading ? (
                <div className="animate-spin">⟳</div>
              ) : (
                <span>🔄</span>
              )}
            </button>
          </div>

          {/* Projects List */}
          <div className="space-y-2">
            {projects.map((project) => (
              <div
                key={project.name}
                className={`p-2 rounded cursor-pointer transition-colors ${
                  selectedProject?.name === project.name
                    ? (isDark ? 'bg-blue-900/30 border border-blue-600' : 'bg-blue-100 border border-blue-300')
                    : (isDark ? 'bg-gray-800 hover:bg-gray-700' : 'bg-gray-200 hover:bg-gray-300')
                }`}
                onClick={() => loadProjectFiles(project.name)}
              >
                <div className="text-sm font-medium">{project.name}</div>
                <div className={`text-xs ${
                  isDark ? 'text-gray-400' : 'text-gray-500'
                }`}>
                  {project.file_count} files • {new Date(project.created_at).toLocaleDateString()}
                </div>
                {project.github_repo && (
                  <div className={`text-xs ${
                    isDark ? 'text-green-400' : 'text-green-600'
                  }`}>
                    🐙 GitHub: {project.github_repo.split('/').pop()}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Selected Project Files */}
          {selectedProject && (
            <div className={`mt-4 p-3 rounded ${
              isDark ? 'bg-gray-800' : 'bg-gray-200'
            }`}>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold">
                  Files in {selectedProject.name}
                </h3>
                <button
                  onClick={() => setShowFolderView(!showFolderView)}
                  className={`px-2 py-1 text-xs rounded ${
                    showFolderView 
                      ? (isDark ? 'bg-blue-600 text-white' : 'bg-blue-600 text-white')
                      : (isDark ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'bg-gray-200 text-gray-700 hover:bg-gray-300')
                  }`}
                  title="Toggle folder view"
                >
                  {showFolderView ? '📁' : '📄'}
                </button>
              </div>
              
              <div className="max-h-64 overflow-y-auto">
                {showFolderView && projectFolderStructure.length > 0 ? (
                  <FolderTree
                    items={projectFolderStructure}
                    onFileClick={handleProjectFileClick}
                    isDark={isDark}
                  />
                ) : (
                  <div className="space-y-1">
                    {projectFiles.map((file) => (
                      <div
                        key={file.name}
                        className={`p-2 rounded text-xs cursor-pointer hover:bg-opacity-50 ${
                          file.is_test 
                            ? (isDark ? 'bg-green-900/20 hover:bg-green-900/30' : 'bg-green-100 hover:bg-green-200')
                            : (isDark ? 'bg-blue-900/20 hover:bg-blue-900/30' : 'bg-blue-100 hover:bg-blue-200')
                        }`}
                        onClick={() => handleProjectFileClick(file)}
                      >
                        <div className="flex justify-between items-center">
                          <span className="font-medium flex items-center space-x-1">
                            <span>{file.extension === '.py' ? '🐍' : '📄'}</span>
                            <span>{file.name}</span>
                            {file.is_test && <span title="Test file">🧪</span>}
                          </span>
                          <span className={`${
                            isDark ? 'text-gray-400' : 'text-gray-500'
                          }`}>
                            {file.extension}
                          </span>
                        </div>
                        <div className={`text-xs ${
                          isDark ? 'text-gray-400' : 'text-gray-500'
                        }`}>
                          {file.size ? Math.round(file.size / 1024) + 'KB' : '0KB'} • {file.modified ? new Date(file.modified * 1000).toLocaleDateString() : 'Unknown date'}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
