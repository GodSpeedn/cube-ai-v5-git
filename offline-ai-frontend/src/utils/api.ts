/**
 * Safe API fetch utility with timeout and error handling
 */

interface ApiFetchOptions extends RequestInit {
  timeout?: number;
}

interface ApiError extends Error {
  status?: number;
  statusText?: string;
  data?: any;
}

export class ApiError extends Error {
  status?: number;
  statusText?: string;
  data?: any;

  constructor(message: string, status?: number, statusText?: string, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.statusText = statusText;
    this.data = data;
  }
}

export const apiFetch = async (url: string, options: ApiFetchOptions = {}): Promise<any> => {
  const { timeout = 8000, ...fetchOptions } = options;
  
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...fetchOptions.headers,
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { message: response.statusText };
      }
      
      throw new ApiError(
        errorData.message || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        response.statusText,
        errorData
      );
    }

    // Try to parse as JSON, fallback to text
    try {
      return await response.json();
    } catch {
      return await response.text();
    }
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error instanceof ApiError) {
      throw error;
    }
    
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new ApiError('Request timeout', 408, 'Request Timeout');
      }
      throw new ApiError(error.message, 0, 'Network Error');
    }
    
    throw new ApiError('Unknown error occurred', 0, 'Unknown Error');
  }
};
