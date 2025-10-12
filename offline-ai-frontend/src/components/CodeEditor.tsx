import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { useTheme } from '../hooks/useTheme';

interface CodeEditorProps {
  file: {
    name: string;
    content: string;
    extension: string;
    path: string;
    is_code: boolean;
  } | null;
  onClose: () => void;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ file, onClose }) => {
  const { isDark } = useTheme();
  const [language, setLanguage] = useState<string>('plaintext');

  useEffect(() => {
    if (file?.extension) {
      // Map file extensions to Monaco Editor languages
      const extensionMap: { [key: string]: string } = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.less': 'less',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.txt': 'plaintext',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.sql': 'sql',
        '.sh': 'shell',
        '.bat': 'bat',
        '.dockerfile': 'dockerfile',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.toml': 'toml'
      };
      
      setLanguage(extensionMap[file.extension.toLowerCase()] || 'plaintext');
    }
  }, [file?.extension]);

  if (!file) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className={`w-full h-full max-w-6xl max-h-[90vh] rounded-lg shadow-2xl ${
        isDark ? 'bg-gray-900' : 'bg-white'
      }`}>
        {/* Header */}
        <div className={`flex items-center justify-between p-4 border-b ${
          isDark ? 'border-gray-700' : 'border-gray-200'
        }`}>
          <div className="flex items-center space-x-3">
            <span className="text-2xl">
              {file.extension === '.py' ? '🐍' : 
               file.extension === '.js' ? '📜' :
               file.extension === '.ts' ? '📘' :
               file.extension === '.html' ? '🌐' :
               file.extension === '.css' ? '🎨' :
               file.extension === '.json' ? '📋' :
               file.extension === '.md' ? '📝' : '📄'}
            </span>
            <div>
              <h3 className={`text-lg font-semibold ${
                isDark ? 'text-white' : 'text-gray-900'
              }`}>
                {file.name}
              </h3>
              <p className={`text-sm ${
                isDark ? 'text-gray-400' : 'text-gray-500'
              }`}>
                {file.path}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className={`p-2 rounded-lg hover:bg-opacity-20 ${
              isDark ? 'hover:bg-gray-600' : 'hover:bg-gray-200'
            }`}
          >
            <span className="text-xl">✕</span>
          </button>
        </div>

        {/* Editor */}
        <div className="h-full">
          <Editor
            height="calc(100vh - 120px)"
            language={language}
            value={file.content}
            theme={isDark ? 'vs-dark' : 'light'}
            options={{
              readOnly: true,
              minimap: { enabled: true },
              scrollBeyondLastLine: false,
              fontSize: 14,
              lineNumbers: 'on',
              wordWrap: 'on',
              automaticLayout: true,
              folding: true,
              foldingStrategy: 'indentation',
              showFoldingControls: 'always',
              bracketPairColorization: { enabled: true },
              guides: {
                bracketPairs: true,
                indentation: true
              }
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default CodeEditor;

