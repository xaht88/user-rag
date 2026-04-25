import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAG Frontend",
  description: "Frontend for RAG web application"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
