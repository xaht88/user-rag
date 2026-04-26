// rag_app/frontend_next/shared/types.ts
export type ViewState = 'idle' | 'loading' | 'success' | 'error';

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  state: ViewState;
  sources?: SourceItem[];
  timestamp?: number;
  sessionId?: string;
}

export interface DocumentItem {
  id: string;
  filename: string;
  status: ViewState;
  chunksCount?: number;
  pagesCount?: number;
  fileSize?: number;
  lastModified?: number;
}

export interface LlmConfig {
  provider: 'openai' | 'ollama';
  model: string;
  baseUrl?: string;
  apiKey?: string;
}

export interface SourceItem {
  filename: string;
  page: number;
  snippet: string;
  docId: string;
}

export interface QueryRequest {
  query: string;
  sessionId: string;
  docIds?: string[];
  topK?: number;
}

export interface QueryResponse {
  answer: string;
  sources: SourceItem[];
  usage?: { prompt_tokens: number; completion_tokens: number; total_tokens: number };
  latency_ms: number;
}



