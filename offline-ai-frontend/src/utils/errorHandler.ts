/**
 * Error handling utilities for the application
 */

export interface AppError {
  message: string;
  code?: string;
  details?: any;
  timestamp: string;
}

export class ErrorHandler {
  private static instance: ErrorHandler;
  private errorLog: AppError[] = [];

  static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }

  /**
   * Handle API errors gracefully
   */
  handleApiError(error: any, context: string = 'API'): AppError {
    const appError: AppError = {
      message: this.getErrorMessage(error),
      code: this.getErrorCode(error),
      details: this.getErrorDetails(error),
      timestamp: new Date().toISOString()
    };

    this.logError(appError, context);
    return appError;
  }

  /**
   * Handle React component errors
   */
  handleComponentError(error: Error, errorInfo: any, componentName: string): AppError {
    const appError: AppError = {
      message: `Component ${componentName} crashed: ${error.message}`,
      code: 'COMPONENT_ERROR',
      details: {
        component: componentName,
        stack: error.stack,
        errorInfo
      },
      timestamp: new Date().toISOString()
    };

    this.logError(appError, 'COMPONENT');
    return appError;
  }

  /**
   * Get user-friendly error message
   */
  private getErrorMessage(error: any): string {
    if (error instanceof Error) {
      return error.message;
    }
    
    if (typeof error === 'string') {
      return error;
    }
    
    if (error?.message) {
      return error.message;
    }
    
    if (error?.status) {
      return `HTTP ${error.status}: ${error.statusText || 'Request failed'}`;
    }
    
    return 'An unexpected error occurred';
  }

  /**
   * Get error code for categorization
   */
  private getErrorCode(error: any): string {
    if (error?.status) {
      return `HTTP_${error.status}`;
    }
    
    if (error?.code) {
      return error.code;
    }
    
    if (error?.name) {
      return error.name;
    }
    
    return 'UNKNOWN_ERROR';
  }

  /**
   * Get additional error details
   */
  private getErrorDetails(error: any): any {
    return {
      originalError: error,
      userAgent: navigator.userAgent,
      url: window.location.href,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Log error for debugging
   */
  private logError(error: AppError, context: string): void {
    console.error(`[${context}] ${error.message}`, error);
    this.errorLog.push(error);
    
    // Keep only last 100 errors
    if (this.errorLog.length > 100) {
      this.errorLog = this.errorLog.slice(-100);
    }
  }

  /**
   * Get recent errors for debugging
   */
  getRecentErrors(count: number = 10): AppError[] {
    return this.errorLog.slice(-count);
  }

  /**
   * Clear error log
   */
  clearErrorLog(): void {
    this.errorLog = [];
  }
}

// Export singleton instance
export const errorHandler = ErrorHandler.getInstance();

// Export utility functions
export const handleApiError = (error: any, context?: string) => 
  errorHandler.handleApiError(error, context);

export const handleComponentError = (error: Error, errorInfo: any, componentName: string) => 
  errorHandler.handleComponentError(error, errorInfo, componentName);
