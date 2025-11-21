/**
 * ARGO - API Client
 * REST API + WebSocket client for backend communication
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

// ============================================================================
// TYPES
// ============================================================================

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: Source[];
  confidence?: number;
}

export interface Source {
  source: string;
  score: number;
  rerank_score?: number;
  is_library: boolean;
}

export interface ChatRequest {
  message: string;
  project_id?: string;
  use_hyde?: boolean;
  use_reranker?: boolean;
  include_library?: boolean;
}

export interface ChatResponse {
  message: string;
  sources: Source[];
  confidence?: number;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface ProjectInfo {
  id: string;
  name: string;
  project_type: string;
  status: string;
  created_at: string;
}

export interface DocumentInfo {
  filename: string;
  file_type: string;
  chunk_count: number;
  indexed_at: string;
  file_size: number;
}

export interface AnalyticsData {
  monthly_cost: number;
  total_tokens: number;
  total_requests: number;
  daily_average_cost: number;
  budget_remaining: number;
  daily_usage: Array<{
    day: string;
    tokens: number;
    cost: number;
  }>;
  project_distribution: Array<{
    name: string;
    value: number;
    color: string;
  }>;
}

export interface HealthCheck {
  status: string;
  version: string;
  timestamp: string;
  components: Record<string, boolean>;
}

// ============================================================================
// API ERROR HANDLING
// ============================================================================

export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text();
    let errorData;

    try {
      errorData = JSON.parse(errorText);
    } catch {
      errorData = { detail: errorText };
    }

    throw new APIError(
      errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      errorData
    );
  }

  return response.json();
}

// ============================================================================
// HEALTH & STATUS API
// ============================================================================

export const healthAPI = {
  async check(): Promise<HealthCheck> {
    const response = await fetch(`${API_BASE_URL}/health`);
    return handleResponse(response);
  },

  async getStatus(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/status`);
    return handleResponse(response);
  }
};

// ============================================================================
// PROJECT API
// ============================================================================

export const projectAPI = {
  async getProject(): Promise<ProjectInfo> {
    const response = await fetch(`${API_BASE_URL}/api/project`);
    return handleResponse(response);
  }
};

// ============================================================================
// CHAT API
// ============================================================================

export const chatAPI = {
  /**
   * Send chat message via REST API
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    return handleResponse(response);
  },

  /**
   * Create WebSocket connection for real-time chat
   */
  createWebSocket(
    onMessage: (response: ChatResponse) => void,
    onError?: (error: any) => void,
    onClose?: () => void
  ): WebSocket {
    const ws = new WebSocket(`${WS_BASE_URL}/ws/chat`);

    ws.onopen = () => {
      console.log('✅ WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'error') {
          console.error('WebSocket error:', data.error);
          onError?.(data);
        } else {
          onMessage(data);
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
        onError?.(error);
      }
    };

    ws.onerror = (event) => {
      console.error('WebSocket error:', event);
      onError?.(event);
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
      onClose?.();
    };

    return ws;
  },

  /**
   * Send message via WebSocket
   */
  sendWebSocketMessage(ws: WebSocket, request: ChatRequest): void {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(request));
    } else {
      throw new Error('WebSocket is not connected');
    }
  }
};

// ============================================================================
// DOCUMENTS API
// ============================================================================

export const documentsAPI = {
  /**
   * Get all documents
   */
  async getDocuments(): Promise<DocumentInfo[]> {
    const response = await fetch(`${API_BASE_URL}/api/documents`);
    return handleResponse(response);
  },

  /**
   * Upload document
   */
  async uploadDocument(
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    // Create XMLHttpRequest for progress tracking
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) {
          const progress = (e.loaded / e.total) * 100;
          onProgress(progress);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(new APIError('Failed to parse response', xhr.status));
          }
        } else {
          try {
            const error = JSON.parse(xhr.responseText);
            reject(new APIError(error.detail || 'Upload failed', xhr.status, error));
          } catch {
            reject(new APIError('Upload failed', xhr.status));
          }
        }
      });

      xhr.addEventListener('error', () => {
        reject(new APIError('Network error'));
      });

      xhr.addEventListener('abort', () => {
        reject(new APIError('Upload aborted'));
      });

      xhr.open('POST', `${API_BASE_URL}/api/documents/upload`);
      xhr.send(formData);
    });
  }
};

// ============================================================================
// ANALYTICS API
// ============================================================================

export const analyticsAPI = {
  /**
   * Get analytics data
   */
  async getAnalytics(): Promise<AnalyticsData> {
    const response = await fetch(`${API_BASE_URL}/api/analytics`);
    return handleResponse(response);
  }
};

// ============================================================================
// COMBINED API EXPORT
// ============================================================================

export const api = {
  health: healthAPI,
  project: projectAPI,
  chat: chatAPI,
  documents: documentsAPI,
  analytics: analyticsAPI,
};

export default api;
