/**
 * Hook for centralized status logic
 * Returns consistent icon, color, and label for status strings
 */

import { useMemo } from 'react';
import { StatusInfo } from '../types/health';

export const useStatus = () => {
  const getServiceStatus = useMemo(() => (status: string): StatusInfo => {
    switch (status.toLowerCase()) {
      case 'running':
        return { icon: '✅', color: 'text-green-500', label: 'Running' };
      case 'stopped':
        return { icon: '❌', color: 'text-red-500', label: 'Stopped' };
      case 'starting':
        return { icon: '🔄', color: 'text-yellow-500', label: 'Starting' };
      case 'error':
        return { icon: '❌', color: 'text-red-500', label: 'Error' };
      case 'warning':
        return { icon: '⚠️', color: 'text-yellow-500', label: 'Warning' };
      default:
        return { icon: '❓', color: 'text-gray-500', label: 'Unknown' };
    }
  }, []);

  const getOverallStatus = useMemo(() => (status: string): StatusInfo => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return { icon: '✅', color: 'text-green-500', label: 'Healthy' };
      case 'unhealthy':
        return { icon: '❌', color: 'text-red-500', label: 'Unhealthy' };
      case 'warning':
        return { icon: '⚠️', color: 'text-yellow-500', label: 'Warning' };
      case 'error':
        return { icon: '❌', color: 'text-red-500', label: 'Error' };
      default:
        return { icon: '❓', color: 'text-gray-500', label: 'Unknown' };
    }
  }, []);

  const getApiKeyStatus = useMemo(() => (hasKey: boolean, isValid: boolean): StatusInfo => {
    if (!hasKey) {
      return { icon: '❌', color: 'text-red-500', label: 'Not Set' };
    }
    if (isValid) {
      return { icon: '✅', color: 'text-green-500', label: 'Valid' };
    }
    return { icon: '⚠️', color: 'text-yellow-500', label: 'Invalid' };
  }, []);

  const getModelStatus = useMemo(() => (isAvailable: boolean): StatusInfo => {
    if (isAvailable) {
      return { icon: '✅', color: 'text-green-500', label: 'Available' };
    }
    return { icon: '❌', color: 'text-red-500', label: 'Unavailable' };
  }, []);

  return {
    getServiceStatus,
    getOverallStatus,
    getApiKeyStatus,
    getModelStatus
  };
};
