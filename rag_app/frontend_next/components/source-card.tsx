import type { SourceItem } from "../shared/types";

interface SourceCardProps {
  source: SourceItem;
}

export function SourceCard({ source }: SourceCardProps) {
  return (
    <div className="rounded-md border border-slate-200 bg-white p-3 text-sm">
      <p className="font-medium text-slate-700">
        {source.filename}, стр. {source.page}
      </p>
      <p className="mt-1 text-slate-600">{source.snippet}</p>
    </div>
  );
}
