import type { ChatMessage } from "../../shared/types";

export const initialMessages: ChatMessage[] = [
  {
    role: "assistant",
    content: "Загрузите документ и задайте вопрос.",
    state: "success"
  }
];
