export interface Citation {
  title: string;
  guest?: string;
  source_type: 'podcast' | 'newsletter' | string;
  url?: string;
  timestamp_str?: string;
  speaker?: string;
  excerpt: string;
  relevance_score: number;
}

export interface Artifact {
  id: string;
  session_id: string;
  message_id?: string;
  title: string;
  artifact_type: 'html' | 'markdown' | string;
  content: string;
  description?: string;
  created_at: string;
  updated_at?: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations?: Citation[];
  artifact_id?: string;
  artifact?: Artifact;
  created_at: string;
}

export interface Session {
  id: string;
  title: string;
  model_provider: string;
  model_name: string;
  message_count: number;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface ModelInfo {
  id: string;
  name: string;
  provider: 'ollama' | 'anthropic' | 'openai' | 'mock' | string;
  is_local: boolean;
  is_available: boolean;
  context_length: number;
  description?: string;
}

export interface ModelsResponse {
  active_provider: string;
  active_model: string;
  models: ModelInfo[];
  ollama_status: {
    available: boolean;
    message: string;
    models?: string[];
  };
  cloud_providers: {
    anthropic: boolean;
    openai: boolean;
  };
}

export interface KnowledgeStatus {
  is_indexed: boolean;
  total_sources: number;
  total_chunks: number;
  vocab_size: number;
  sources: Array<{
    title: string;
    guest?: string;
    type: string;
    url?: string;
    word_count: number;
    chunks: number;
    filename: string;
  }>;
}

export interface ChatResponse {
  message: Message;
  citations: Citation[];
  artifact?: Artifact;
  session_id: string;
  model_used: string;
  duration_seconds: number;
}
