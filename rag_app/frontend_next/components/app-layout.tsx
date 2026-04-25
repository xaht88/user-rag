import type { ReactNode } from "react";

interface AppLayoutProps {
  header: ReactNode;
  documents: ReactNode;
  chat: ReactNode;
}

export function AppLayout({ header, documents, chat }: AppLayoutProps) {
  return (
    <div className="mx-auto flex min-h-screen max-w-7xl flex-col gap-4 p-4">
      <header>{header}</header>
      <main className="grid flex-1 gap-4 lg:grid-cols-[340px_1fr]">
        <aside className="rounded-lg border border-slate-200 bg-slate-50 p-3">{documents}</aside>
        <div className="min-h-[560px]">{chat}</div>
      </main>
    </div>
  );
}
