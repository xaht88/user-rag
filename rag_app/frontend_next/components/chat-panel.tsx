import type { ChatMessage } from "../shared/types";
import { SourceCard } from "./source-card";

interface ChatPanelProps {
  messages: ChatMessage[];
  onSend: (query: string) => Promise<void>;
}

export function ChatPanel({ messages, onSend }: ChatPanelProps) {
  return (
    <section className="flex h-full flex-col rounded-lg border border-slate-200 bg-white">
      <div className="flex-1 space-y-3 overflow-auto p-4">
        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className="space-y-2">
            <p className="text-sm font-semibold text-slate-700">{message.role === "user" ? "Вы" : "Ассистент"}</p>
            {message.state === "loading" ? <p className="text-sm text-amber-600">Генерация ответа...</p> : null}
            {message.state === "error" ? <p className="text-sm text-red-600">Ошибка запроса: {message.content}</p> : null}
            {message.state !== "loading" ? <p className="text-sm text-slate-700">{message.content}</p> : null}
            {message.sources?.length ? (
              <div className="grid gap-2">
                {message.sources.map((source, sourceIndex) => (
                  <SourceCard key={`${source.filename}-${sourceIndex}`} source={source} />
                ))}
              </div>
            ) : null}
          </div>
        ))}
      </div>
      <form
        className="border-t border-slate-200 p-3"
        onSubmit={async (event) => {
          event.preventDefault();
          const formData = new FormData(event.currentTarget);
          const query = String(formData.get("query") ?? "").trim();
          if (!query) {
            return;
          }
          await onSend(query);
          event.currentTarget.reset();
        }}
      >
        <div className="flex gap-2">
          <input
            name="query"
            placeholder="Введите вопрос по документам"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <button type="submit" className="rounded-md bg-accent px-3 py-2 text-sm font-medium text-white">
            Отправить
          </button>
        </div>
      </form>
    </section>
  );
}
