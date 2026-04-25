import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import { ChatPanel } from "./chat-panel";

describe("ChatPanel", () => {
  test("отправляет сообщение", async () => {
    const onSend = vi.fn().mockResolvedValue(undefined);
    render(<ChatPanel messages={[]} onSend={onSend} />);

    fireEvent.change(screen.getByPlaceholderText("Введите вопрос по документам"), {
      target: { value: "Что в документе?" }
    });
    fireEvent.click(screen.getByRole("button", { name: "Отправить" }));

    await waitFor(() => expect(onSend).toHaveBeenCalledWith("Что в документе?"));
  });

  test("рендерит сообщение ошибки", () => {
    render(
      <ChatPanel
        onSend={vi.fn()}
        messages={[{ role: "assistant", state: "error", content: "timeout", sources: [] }]}
      />
    );

    expect(screen.getByText("Ошибка запроса: timeout")).toBeInTheDocument();
  });
});
