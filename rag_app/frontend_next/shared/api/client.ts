import type { LlmConfig } from "../types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function updateLlmConfig(sessionId: string, config: LlmConfig): Promise<void> {
  const response = await fetch(`${API_BASE}/api/sessions/${sessionId}/llm/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config)
  });
  if (!response.ok) {
    throw new Error("LLM config request failed");
  }
}
