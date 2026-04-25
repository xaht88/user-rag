import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";
import { DocumentPanel } from "./document-panel";

describe("DocumentPanel", () => {
  test("показывает loading состояние", () => {
    render(
      <DocumentPanel
        items={[
          { id: "1", filename: "doc.pdf", status: "loading" }
        ]}
      />
    );

    expect(screen.getByText("Обработка документа...")).toBeInTheDocument();
  });

  test("показывает error состояние", () => {
    render(
      <DocumentPanel
        items={[
          { id: "1", filename: "doc.pdf", status: "error" }
        ]}
      />
    );

    expect(screen.getByText("Ошибка обработки документа")).toBeInTheDocument();
  });
});
