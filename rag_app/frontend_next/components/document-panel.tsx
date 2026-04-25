import type { DocumentItem } from "../shared/types";

interface DocumentPanelProps {
  items: DocumentItem[];
}

export function DocumentPanel({ items }: DocumentPanelProps) {
  if (!items.length) {
    return <p className="text-sm text-slate-500">Документы не загружены</p>;
  }

  return (
    <ul className="space-y-2">
      {items.map((item) => (
        <li key={item.id} className="rounded-md border border-slate-200 bg-white p-3">
          <p className="text-sm font-medium text-slate-700">{item.filename}</p>
          {item.status === "loading" ? <p className="text-xs text-amber-600">Обработка документа...</p> : null}
          {item.status === "error" ? <p className="text-xs text-red-600">Ошибка обработки документа</p> : null}
          {item.status === "success" ? (
            <p className="text-xs text-emerald-600">
              Готово: {item.chunksCount ?? 0} чанков, {item.pagesCount ?? 0} стр.
            </p>
          ) : null}
        </li>
      ))}
    </ul>
  );
}
