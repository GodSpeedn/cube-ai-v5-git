/**
 * Git Integration Page
 * 
 * This component provides a comprehensive Git integration interface for:
 * - Connecting to GitHub repositories
 * - Pulling from existing repositories
 * - Pushing new commits
 * - Managing repository configurations
 */

import React, { useState, useEffect } from 'react';
import { useTheme } from '../hooks/useTheme';
import { 
  getGitStatus, 
  configureGit, 
  pullFromRepository, 
  pushToRepository,
  listProjects,
  getProjectFiles,
  deleteProject,
  GitConfig,
  GitStatus,
  Repository,
  GitUploadResult,
  Project,
  ProjectFile
} from '../services/api';

// Interfaces are now imported from api.ts

export default function GitIntegrationPage() {
  const { isDark } = useTheme();
  const [activeTab, setActiveTab] = useState<'connect' | 'pull' | 'push' | 'projects'>('connect');
  const [gitStatus, setGitStatus] = useState<GitStatus>({ configured: false });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);

  // Form states
  const [gitConfig, setGitConfig] = useState<GitConfig>({
    token: '',
    username: '',
    email: ''
  });
  const [selectedRepo, setSelectedRepo] = useState<string>('');
  const [newRepoName, setNewRepoName] = useState('');
  const [commitMessage, setCommitMessage] = useState('');
  const [projectName, setProjectName] = useState('');

  // Project management states
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<string>('');
  const [projectFiles, setProjectFiles] = useState<ProjectFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<ProjectFile | null>(null);

  // Load Git status and projects on component mount
  useEffect(() => {
    loadGitStatus();
    loadProjects();
  }, []);

  const loadGitStatus = async () => {
    try {
      setLoading(true);
      const data = await getGitStatus();
      setGitStatus(data);
    } catch (error) {
      console.error('Failed to load Git status:', error);
      showMessage('error', 'Failed to load Git status');
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type: 'success' | 'error' | 'info', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const loadProjects = async () => {
    try {
      const data = await listProjects();
      setProjects(data.projects);
    } catch (error) {
      console.error('Failed to load projects:', error);
      showMessage('error', 'Failed to load projects');
    }
  };

  const loadProjectFiles = async (projectName: string) => {
    try {
      setLoading(true);
      console.log('🔍 Loading files for project:', projectName);
      
      const data = await getProjectFiles(projectName);
      console.log('🔍 API Response:', data);
      console.log('🔍 Files received:', data.files);
      console.log('🔍 Files count:', data.files?.length || 0);
      
      if (data.files && Array.isArray(data.files)) {
        setProjectFiles(data.files);
        console.log('✅ Files set successfully:', data.files.length);
      } else {
        console.log('❌ No files array in response');
        setProjectFiles([]);
      }
      
      setSelectedProject(projectName);
    } catch (error) {
      console.error('❌ Failed to load project files:', error);
      showMessage('error', 'Failed to load project files');
      setProjectFiles([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProject = async (projectName: string) => {
    if (!confirm(`Are you sure you want to delete project "${projectName}"?`)) {
      return;
    }

    try {
      setLoading(true);
      await deleteProject(projectName);
      showMessage('success', `Project "${projectName}" deleted successfully`);
      await loadProjects();
      if (selectedProject === projectName) {
        setSelectedProject('');
        setProjectFiles([]);
        setSelectedFile(null);
      }
    } catch (error) {
      console.error('Failed to delete project:', error);
      showMessage('error', 'Failed to delete project');
    } finally {
      setLoading(false);
    }
  };

  const handleConnectGit = async () => {
    if (!gitConfig.token || !gitConfig.username) {
      showMessage('error', 'Please provide GitHub token and username');
      return;
    }

    try {
      setLoading(true);
      const result = await configureGit(gitConfig);
      
      if (result.success) {
        showMessage('success', 'GitHub connected successfully!');
        await loadGitStatus();
        setActiveTab('pull');
      } else {
        showMessage('error', result.message || 'Failed to connect to GitHub');
      }
    } catch (error) {
      console.error('Git connection error:', error);
      showMessage('error', 'Failed to connect to GitHub');
    } finally {
      setLoading(false);
    }
  };

  const handlePullRepository = async () => {
    if (!selectedRepo) {
      showMessage('error', 'Please select a repository to pull from');
      return;
    }

    try {
      setLoading(true);
      const result = await pullFromRepository(selectedRepo);
      
      if (result.success) {
        showMessage('success', `Successfully pulled from ${selectedRepo}. Project: ${result.project_name}`);
        await loadProjects(); // Refresh projects list
        setActiveTab('projects'); // Switch to projects tab
      } else {
        showMessage('error', result.message || 'Failed to pull repository');
      }
    } catch (error) {
      console.error('Pull error:', error);
      showMessage('error', 'Failed to pull repository');
    } finally {
      setLoading(false);
    }
  };

  const handlePushToRepository = async () => {
    if (!selectedRepo && !newRepoName) {
      showMessage('error', 'Please select a repository or enter a new repository name');
      return;
    }

    const repoName = selectedRepo || newRepoName;
    const commitMsg = commitMessage || `AI Generated Code - ${new Date().toLocaleString()}`;
    const projName = projectName || 'ai-generated-project';

    try {
      setLoading(true);
      const result: GitUploadResult = await pushToRepository(repoName, commitMsg);
      
      if (result.success) {
        const folderInfo = result.folder_structure ? 
          ` (${result.folder_structure.src_files} src files, ${result.folder_structure.test_files} test files)` : '';
        showMessage('success', `Successfully pushed to ${repoName}! ${result.files_pushed} files uploaded${folderInfo}.`);
        if (result.repository_url) {
          // Open repository in new tab
          window.open(result.repository_url, '_blank');
        }
      } else {
        showMessage('error', result.error || 'Failed to push to repository');
      }
    } catch (error) {
      console.error('Push error:', error);
      showMessage('error', 'Failed to push to repository');
    } finally {
      setLoading(false);
    }
  };

  const renderConnectTab = () => (
    <div className="space-y-6">
      <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">🔗 Connect to GitHub</h3>
        <p className="text-sm text-gray-600 dark:text-gray-300">
          Connect your GitHub account to enable repository management, pulling, and pushing code.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">GitHub Personal Access Token</label>
          <input
            type="password"
            value={gitConfig.token}
            onChange={(e) => setGitConfig({ ...gitConfig, token: e.target.value })}
            placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
            className={`w-full p-3 rounded-lg border ${
              isDark 
                ? 'bg-gray-800 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            }`}
          />
          <p className="text-xs text-gray-500 mt-1">
            Create a token at: <a href="https://github.com/settings/tokens" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">github.com/settings/tokens</a>
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">GitHub Username</label>
          <input
            type="text"
            value={gitConfig.username}
            onChange={(e) => setGitConfig({ ...gitConfig, username: e.target.value })}
            placeholder="your-username"
            className={`w-full p-3 rounded-lg border ${
              isDark 
                ? 'bg-gray-800 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            }`}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Email (Optional)</label>
          <input
            type="email"
            value={gitConfig.email}
            onChange={(e) => setGitConfig({ ...gitConfig, email: e.target.value })}
            placeholder="your-email@example.com"
            className={`w-full p-3 rounded-lg border ${
              isDark 
                ? 'bg-gray-800 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            }`}
          />
        </div>

        <button
          onClick={handleConnectGit}
          disabled={loading || !gitConfig.token || !gitConfig.username}
          className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
            loading || !gitConfig.token || !gitConfig.username
              ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
              : 'bg-green-600 hover:bg-green-700 text-white'
          }`}
        >
          {loading ? 'Connecting...' : 'Connect to GitHub'}
        </button>
      </div>

      {gitStatus.configured && gitStatus.user && (
        <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
          <h4 className="font-semibold text-green-800 dark:text-green-200">✅ Connected as {gitStatus.user.login}</h4>
          <p className="text-sm text-green-600 dark:text-green-300">
            Name: {gitStatus.user.name || 'Not set'}
          </p>
          {gitStatus.user.email && (
            <p className="text-sm text-green-600 dark:text-green-300">
              Email: {gitStatus.user.email}
            </p>
          )}
        </div>
      )}
    </div>
  );

  const renderPullTab = () => (
    <div className="space-y-6">
      <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">📥 Pull from Repository</h3>
        <p className="text-sm text-gray-600 dark:text-gray-300">
          Pull the latest code from an existing GitHub repository to work with it locally.
        </p>
      </div>

      {!gitStatus.configured ? (
        <div className="text-center py-8">
          <p className="text-gray-500">Please connect to GitHub first</p>
        </div>
      ) : (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Select Repository</label>
            <select
              value={selectedRepo}
              onChange={(e) => setSelectedRepo(e.target.value)}
              className={`w-full p-3 rounded-lg border ${
                isDark 
                  ? 'bg-gray-800 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              }`}
            >
              <option value="">Choose a repository...</option>
              {gitStatus.repositories?.map((repo) => (
                <option key={repo.full_name} value={repo.full_name}>
                  {repo.name} {repo.private ? '(Private)' : '(Public)'}
                </option>
              ))}
            </select>
          </div>

          {selectedRepo && (
            <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Repository Details</h4>
              {(() => {
                const repo = gitStatus.repositories?.find(r => r.full_name === selectedRepo);
                return repo ? (
                  <div className="space-y-1 text-sm">
                    <p><strong>Name:</strong> {repo.name}</p>
                    <p><strong>Description:</strong> {repo.description || 'No description'}</p>
                    <p><strong>Visibility:</strong> {repo.private ? 'Private' : 'Public'}</p>
                    <p><strong>Updated:</strong> {new Date(repo.updated_at).toLocaleDateString()}</p>
                  </div>
                ) : null;
              })()}
            </div>
          )}

          <button
            onClick={handlePullRepository}
            disabled={loading || !selectedRepo}
            className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
              loading || !selectedRepo
                ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {loading ? 'Pulling...' : 'Pull Repository'}
          </button>
        </div>
      )}
    </div>
  );

  const renderPushTab = () => (
    <div className="space-y-6">
      <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">📤 Push to Repository</h3>
        <p className="text-sm text-gray-600 dark:text-gray-300">
          Push your generated code to a GitHub repository. You can push to an existing repository or create a new one.
        </p>
      </div>

      {!gitStatus.configured ? (
        <div className="text-center py-8">
          <p className="text-gray-500">Please connect to GitHub first</p>
        </div>
      ) : (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Repository</label>
            <div className="space-y-2">
              <select
                value={selectedRepo}
                onChange={(e) => {
                  setSelectedRepo(e.target.value);
                  if (e.target.value) setNewRepoName('');
                }}
                className={`w-full p-3 rounded-lg border ${
                  isDark 
                    ? 'bg-gray-800 border-gray-600 text-white' 
                    : 'bg-white border-gray-300 text-gray-900'
                }`}
              >
                <option value="">Choose existing repository...</option>
                {gitStatus.repositories?.map((repo) => (
                  <option key={repo.full_name} value={repo.full_name}>
                    {repo.name} {repo.private ? '(Private)' : '(Public)'}
                  </option>
                ))}
              </select>
              
              <div className="text-center text-gray-500">OR</div>
              
              <input
                type="text"
                value={newRepoName}
                onChange={(e) => {
                  setNewRepoName(e.target.value);
                  if (e.target.value) setSelectedRepo('');
                }}
                placeholder="Enter new repository name..."
                className={`w-full p-3 rounded-lg border ${
                  isDark 
                    ? 'bg-gray-800 border-gray-600 text-white' 
                    : 'bg-white border-gray-300 text-gray-900'
                }`}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Project Name</label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="Enter project name (optional)"
              className={`w-full p-3 rounded-lg border ${
                isDark 
                  ? 'bg-gray-800 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              }`}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Commit Message</label>
            <input
              type="text"
              value={commitMessage}
              onChange={(e) => setCommitMessage(e.target.value)}
              placeholder="Enter commit message (optional)"
              className={`w-full p-3 rounded-lg border ${
                isDark 
                  ? 'bg-gray-800 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              }`}
            />
          </div>

          <button
            onClick={handlePushToRepository}
            disabled={loading || (!selectedRepo && !newRepoName)}
            className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
              loading || (!selectedRepo && !newRepoName)
                ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            {loading ? 'Pushing...' : 'Push to Repository'}
          </button>
        </div>
      )}
    </div>
  );

  const renderProjectsTab = () => (
    <div className="space-y-6">
      <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">📁 Project Management</h3>
        <p className="text-sm text-gray-600 dark:text-gray-300">
          Manage your pulled projects and view their file structure. Projects are organized in folders with proper src/ and tests/ structure.
        </p>
      </div>

      {projects.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">No projects found. Pull a repository to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Projects List */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Projects ({projects.length})</h4>
            <div className="space-y-3">
              {projects.map((project) => (
                <div
                  key={project.name}
                  className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                    selectedProject === project.name
                      ? (isDark ? 'bg-blue-900 border-blue-600' : 'bg-blue-100 border-blue-300')
                      : (isDark ? 'bg-gray-800 border-gray-600 hover:bg-gray-700' : 'bg-white border-gray-200 hover:bg-gray-50')
                  }`}
                  onClick={() => loadProjectFiles(project.name)}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h5 className="font-semibold">{project.name}</h5>
                      <p className="text-sm text-gray-500">
                        {project.file_count} files • {new Date(project.modified * 1000).toLocaleDateString()}
                      </p>
                      <div className="mt-2 text-xs">
                        <span className="text-green-600">src: {project.structure.src_files.length}</span>
                        <span className="mx-2">•</span>
                        <span className="text-blue-600">tests: {project.structure.test_files.length}</span>
                        <span className="mx-2">•</span>
                        <span className="text-gray-500">other: {project.structure.other_files.length}</span>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteProject(project.name);
                      }}
                      className="text-red-500 hover:text-red-700 text-sm"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Project Files */}
          <div>
            {selectedProject ? (
              <div>
                <h4 className="text-lg font-semibold mb-4">Files in {selectedProject}</h4>
                <div className="text-xs text-gray-500 mb-2">
                  Debug: {projectFiles.length} files loaded
                </div>
                {projectFiles.length === 0 ? (
                  <p className="text-gray-500">No files found in this project.</p>
                ) : (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {projectFiles.map((file) => (
                      <div
                        key={file.path}
                        className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                          selectedFile?.path === file.path
                            ? (isDark ? 'bg-blue-900 border-blue-600' : 'bg-blue-100 border-blue-300')
                            : (isDark ? 'bg-gray-800 border-gray-600 hover:bg-gray-700' : 'bg-white border-gray-200 hover:bg-gray-50')
                        }`}
                        onClick={() => setSelectedFile(file)}
                      >
                        <div className="flex items-center space-x-2">
                          <span className={`text-xs px-2 py-1 rounded ${
                            file.is_test 
                              ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                              : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          }`}>
                            {file.is_test ? 'TEST' : 'SRC'}
                          </span>
                          <span className="font-medium">{file.name}</span>
                          <span className="text-xs text-gray-500">
                            {(file.size / 1024).toFixed(1)}KB
                          </span>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">{file.path}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">Select a project to view its files</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* File Content Viewer */}
      {selectedFile && (
        <div className="mt-6">
          <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <h5 className="font-semibold">{selectedFile.name}</h5>
              <button
                onClick={() => setSelectedFile(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                Close
              </button>
            </div>
            <pre className="bg-white dark:bg-gray-900 p-4 rounded text-sm overflow-x-auto max-h-64">
              <code>{selectedFile.content}</code>
            </pre>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className={`h-full flex flex-col ${isDark ? 'bg-gray-900' : 'bg-gray-100'}`}>
      {/* Header */}
      <div className={`p-6 border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
        <h1 className="text-2xl font-bold mb-2">Git Integration</h1>
        <p className="text-gray-600 dark:text-gray-300">
          Connect to GitHub, pull from repositories, and push your generated code
        </p>
      </div>

      {/* Status Message */}
      {message && (
        <div className={`mx-6 mt-4 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-200' :
          message.type === 'error' ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-200' :
          'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-200'
        }`}>
          {message.text}
        </div>
      )}

      {/* Tab Navigation */}
      <div className={`px-6 py-4 border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
        <div className="flex space-x-1">
          {[
            { id: 'connect', label: 'Connect', icon: '🔗' },
            { id: 'pull', label: 'Pull', icon: '📥' },
            { id: 'push', label: 'Push', icon: '📤' },
            { id: 'projects', label: 'Projects', icon: '📁' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === tab.id
                  ? (isDark ? 'bg-blue-600 text-white' : 'bg-blue-600 text-white')
                  : (isDark ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' : 'bg-gray-200 text-gray-700 hover:bg-gray-300')
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 p-6 overflow-y-auto">
        {activeTab === 'connect' && renderConnectTab()}
        {activeTab === 'pull' && renderPullTab()}
        {activeTab === 'push' && renderPushTab()}
        {activeTab === 'projects' && renderProjectsTab()}
      </div>
    </div>
  );
}
