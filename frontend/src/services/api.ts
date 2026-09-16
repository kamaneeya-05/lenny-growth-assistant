import {
  Session,
  Message,
  Artifact,
  ModelsResponse,
  KnowledgeStatus,
  ChatResponse,
} from '../types';

const API_BASE = '/api';

export class ApiService {
  private static async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(options?.headers || {}),
    };

    const response = await fetch(url, { ...options, headers });

    if (!response.ok) {
      let errorMessage = `HTTP error ${response.status}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // Fallback to text
      }
      throw new Error(errorMessage);
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Health
  static async getHealth() {
    return this.request<{
      status: string;
      database: { healthy: boolean };
      knowledge_base: { is_indexed: boolean; total_chunks: number };
      providers: Record<string, any>;
    }>('/health');
  }

  // Sessions
  static async listSessions(): Promise<Session[]> {
    return this.request<Session[]>('/sessions');
  }

  static async getSession(sessionId: string): Promise<Session> {
    return this.request<Session>(`/sessions/${sessionId}`);
  }

  static async createSession(title?: string, modelProvider?: string, modelName?: string): Promise<Session> {
    return this.request<Session>('/sessions', {
      method: 'POST',
      body: JSON.stringify({
        title: title || 'New Conversation',
        model_provider: modelProvider,
        model_name: modelName,
      }),
    });
  }

  static async deleteSession(sessionId: string): Promise<void> {
    await this.request(`/sessions/${sessionId}`, { method: 'DELETE' });
  }

  static async updateSession(sessionId: string, updates: { title?: string; model_provider?: string; model_name?: string }): Promise<Session> {
    return this.request<Session>(`/sessions/${sessionId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  }

  // Chat
  static async sendMessage(
    sessionId: string,
    message: string,
    options?: {
      model_provider?: string;
      model_name?: string;
      generate_ship30_essay?: boolean;
      generate_artifact?: boolean;
      artifact_type?: string;
    }
  ): Promise<ChatResponse> {
    return this.request<ChatResponse>(`/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({
        message,
        ...options,
      }),
    });
  }

  // Artifacts
  static async getArtifact(artifactId: string): Promise<Artifact> {
    return this.request<Artifact>(`/artifacts/${artifactId}`);
  }

  // Models
  static async getModels(): Promise<ModelsResponse> {
    return this.request<ModelsResponse>('/models');
  }

  // Knowledge
  static async getKnowledgeStatus(): Promise<KnowledgeStatus> {
    return this.request<KnowledgeStatus>('/knowledge/status');
  }

  static async searchTranscripts(query: string, topK: number = 10) {
    return this.request<{
      query: string;
      count: number;
      results: Array<{
        title: string;
        guest?: string;
        speaker?: string;
        timestamp_str?: string;
        url?: string;
        excerpt: string;
        score: number;
        is_grounded: boolean;
      }>;
    }>(`/knowledge/search?q=${encodeURIComponent(query)}&top_k=${topK}`);
  }

  static async triggerIngestion(options?: { download_remote?: boolean; force_reindex?: boolean; max_episodes?: number }) {
    return this.request<{ status: string; result: any }>('/knowledge/ingest', {
      method: 'POST',
      body: JSON.stringify(options || {}),
    });
  }
}
