// rag_app/frontend_next/shared/api/client.ts
import { QueryRequest, QueryResponse, LlmConfig, DocumentItem } from '../shared/types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = {
  async queryLLM(request: QueryRequest): Promise<QueryResponse> {
    const res = await fetch(`${BASE_URL}/query_llm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
  },

  async uploadDocument(file: File, sessionId: string): Promise<{ doc_id: string; status: string }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);
    const res = await fetch(`${BASE_URL}/upload_document`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error(`Upload Error: ${res.status}`);
    return res.json();
  },

  async getDocuments(sessionId: string): Promise<DocumentItem[]> {
    const res = await fetch(`${BASE_URL}/get_documents?session_id=${sessionId}`);
    if (!res.ok) throw new Error(`Docs Error: ${res.status}`);
    return res.json();
  },

  async setLlmConfig(sessionId: string, config: LlmConfig): Promise<{ status: string }> {
    const res = await fetch(`${BASE_URL}/set_llm_config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, config }),
    });
    if (!res.ok) throw new Error(`Config Error: ${res.status}`);
    return res.json();
  },

  async deleteDocument(sessionId: string, docId: string): Promise<{ status: string }> {
    const res = await fetch(`${BASE_URL}/delete_document`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, doc_id: docId }),
    });
    if (!res.ok) throw new Error(`Delete Error: ${res.status}`);
    return res.json();
  },
};
