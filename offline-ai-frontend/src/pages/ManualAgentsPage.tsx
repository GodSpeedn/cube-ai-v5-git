import React from 'react';
import ManualAgentCanvas from '../components/ManualAgentCanvas';
import { useTheme } from '../hooks/useTheme';
import '../styles/manual-agents.css';

export default function ManualAgentsPage() {
  const { isDark } = useTheme();
  
  return (
    <div className={`manual-agents-canvas h-full ${isDark ? 'dark-theme' : ''}`} data-theme={isDark ? 'dark' : 'light'}>
      <ManualAgentCanvas isDark={isDark} />
    </div>
  );
} 