import type { DocumentItem } from "../../shared/types";

export const mockDocuments: DocumentItem[] = [
  {
    id: "doc-1",
    filename: "technical_specification.md",
    status: "success",
    chunksCount: 24,
    pagesCount: 12
  },
  {
    id: "doc-2",
    filename: "project_notes.pdf",
    status: "loading"
  }
];
