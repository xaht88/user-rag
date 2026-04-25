"use client";

import { useState } from "react";
import { AppLayout } from "../components/app-layout";
import { ChatPanel } from "../components/chat-panel";
import { DocumentPanel } from "../components/document-panel";
import { LLMSelector } from "../components/llm-selector";
import { initialMessages } from "../features/chat/mock-messages";
import { mockDocuments } from "../features/documents/mock-documents";
import { defaultLlmConfig } from "../features/llm/default-config";
import { updateLlmConfig } from "../shared/api/client";
import type { ChatMessage, LlmConfig, ViewState } from "../shared/types";

const DEMO_SESSION_ID = "demo-session";

export default function HomePage() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [llmConfig, setLlmConfig] = useState<LlmConfig>(defaultLlmConfig);
  const [llmState, setLlmState] = useState<ViewState>("success");

  const handleSend = async (query: string): Promise<void> => {
    setMessages((prev) => [...prev, { role: "user", content: query, state: "success" }]);
    setMessages((prev) => [...prev, { role: "assistant", content: "", state: "loading" }]);

    try {
      await new Promise((resolve) => setTimeout(resolve, 700));
      setMessages((prev) => {
        const next = [...prev];
        next[next.length - 1] = {
          role: "assistant",
          state: "success",
          content: `Демо-ответ по запросу: ${query}`,
          sources: [
            {
              filename: "technical_specification.md",
              page: 1,
              snippet: "Фрагмент источника для проверки ответа."
            }
          ]
        };
        return next;
      });
    } catch {
      setMessages((prev) => {
        const next = [...prev];
        next[next.length - 1] = { role: "assistant", state: "error", content: "Сбой при обработке запроса." };
        return next;
      });
    }
  };

  const handleLlmChange = async (nextConfig: LlmConfig): Promise<void> => {
    setLlmConfig(nextConfig);
    setLlmState("loading");
    try {
      await updateLlmConfig(DEMO_SESSION_ID, nextConfig);
      setLlmState("success");
    } catch {
      setLlmState("error");
    }
  };

  return (
    <AppLayout
      header={<LLMSelector config={llmConfig} state={llmState} onChange={handleLlmChange} />}
      documents={<DocumentPanel items={mockDocuments} />}
      chat={<ChatPanel messages={messages} onSend={handleSend} />}
    />
  );
}
