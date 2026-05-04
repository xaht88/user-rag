// rag_app/frontend_next/shared/api/client.ts
import { QueryRequest, QueryResponse, LlmConfig, DocumentItem } from '../shared/types';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = {
  async queryLLM(sessionId: string, query: string, documentIds?: string[]): Promise<QueryResponse> {
    const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, query, document_ids: documentIds }),
    });
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
  },

  async uploadDocument(file: File, sessionId: string): Promise<{ session_id: string; document_id: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error(`Upload Error: ${res.status}`);
    return res.json();
  },

  async getDocuments(sessionId: string): Promise<DocumentItem[]> {
    const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/documents`);
    if (!res.ok) throw new Error(`Docs Error: ${res.status}`);
    const data = await res.json();
    return data.documents || [];
  },

  async updateLlmConfig(sessionId: string, config: LlmConfig): Promise<{ message: string }> {
    const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/llm/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    if (!res.ok) throw new Error(`Config Error: ${res.status}`);
    return res.json();
  },

  async deleteDocument(sessionId: string, docId: string): Promise<{ message: string }> {
    const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/documents/${docId}/delete`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error(`Delete Error: ${res.status}`);
    return res.json();
  },

  async toggleDocument(sessionId: string, docId: string): Promise<{ selected: boolean }> {
    const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}/documents/${docId}/toggle`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error(`Toggle Error: ${res.status}`);
    return res.json();
  },
};
