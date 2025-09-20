import React, { useState } from 'react';
import { useTheme } from '../hooks/useTheme';

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

interface FolderTreeProps {
  items: FileItem[];
  onFileClick: (file: FileItem) => void;
  level?: number;
  isDark?: boolean;
}

const FolderTree: React.FC<FolderTreeProps> = ({ 
  items, 
  onFileClick, 
  level = 0, 
  isDark = false 
}) => {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

  const toggleFolder = (path: string) => {
    setExpandedFolders(prev => {
      const newSet = new Set(prev);
      if (newSet.has(path)) {
        newSet.delete(path);
      } else {
        newSet.add(path);
      }
      return newSet;
    });
  };

  const getFileIcon = (item: FileItem) => {
    if (item.type === 'folder') {
      return expandedFolders.has(item.path) ? '📂' : '📁';
    }
    
    // File icons based on extension
    const ext = item.extension?.toLowerCase();
    if (ext === '.py') return '🐍';
    if (ext === '.js' || ext === '.ts' || ext === '.jsx' || ext === '.tsx') return '📜';
    if (ext === '.html') return '🌐';
    if (ext === '.css') return '🎨';
    if (ext === '.json') return '📋';
    if (ext === '.md') return '📝';
    if (ext === '.txt') return '📄';
    if (item.is_test) return '🧪';
    return '📄';
  };

  const formatFileSize = (size: number) => {
    if (size < 1024) return `${size}B`;
    if (size < 1024 * 1024) return `${Math.round(size / 1024)}KB`;
    return `${Math.round(size / (1024 * 1024))}MB`;
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString();
  };

  return (
    <div className="space-y-1">
      {items.map((item) => (
        <div key={item.path} className="select-none">
          <div
            className={`flex items-center space-x-2 py-1 px-2 rounded cursor-pointer transition-colors ${
              item.type === 'folder'
                ? (isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-200')
                : (isDark ? 'hover:bg-gray-800' : 'hover:bg-gray-100')
            }`}
            style={{ paddingLeft: `${level * 16 + 8}px` }}
            onClick={() => {
              if (item.type === 'folder') {
                toggleFolder(item.path);
              } else {
                onFileClick(item);
              }
            }}
          >
            <span className="text-sm">
              {getFileIcon(item)}
            </span>
            <span className={`text-sm font-medium ${
              item.type === 'folder' 
                ? (isDark ? 'text-blue-300' : 'text-blue-600')
                : (isDark ? 'text-gray-200' : 'text-gray-800')
            }`}>
              {item.name}
            </span>
            
            {item.type === 'folder' && item.file_count !== undefined && (
              <span className={`text-xs ${
                isDark ? 'text-gray-400' : 'text-gray-500'
              }`}>
                ({item.file_count} files)
              </span>
            )}
            
            {item.type === 'file' && item.size && (
              <span className={`text-xs ${
                isDark ? 'text-gray-400' : 'text-gray-500'
              }`}>
                {formatFileSize(item.size)}
              </span>
            )}
            
            {item.type === 'file' && item.modified && (
              <span className={`text-xs ${
                isDark ? 'text-gray-400' : 'text-gray-500'
              }`}>
                {formatDate(item.modified)}
              </span>
            )}
            
            {item.error && (
              <span className="text-xs text-red-400" title={item.error}>
                ⚠️
              </span>
            )}
            
            {item.is_test && (
              <span className="text-xs text-green-400" title="Test file">
                🧪
              </span>
            )}
          </div>
          
          {item.type === 'folder' && 
           item.children && 
           expandedFolders.has(item.path) && (
            <FolderTree
              items={item.children}
              onFileClick={onFileClick}
              level={level + 1}
              isDark={isDark}
            />
          )}
        </div>
      ))}
    </div>
  );
};

export default FolderTree;
