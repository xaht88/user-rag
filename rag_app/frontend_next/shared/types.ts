export type ViewState = "idle" | "loading" | "error" | "success";

export interface DocumentItem {
  id: string;
  filename: string;
  status: ViewState;
  chunksCount?: number;
  pagesCount?: number;
}

export interface SourceItem {
  filename: string;
  page: number;
  snippet: string;
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  state: ViewState;
  sources?: SourceItem[];
}

export interface LlmConfig {
  provider: "openai" | "ollama";
  model: string;
}
