
import { FileText, ChevronDown } from "lucide-react";

export default function SourceCard({ source }) {
  return (
    <details className="source-card">
      <summary>
        <FileText size={15} />
        <span>Page {source.page ?? "—"}</span>

        {typeof source.similarity === "number" && (
          <span className="similarity">
            Match {(source.similarity * 100).toFixed(1)}%
          </span>
        )}

        <ChevronDown size={15} />
      </summary>

      <p>{source.text || "No source text available."}</p>
    </details>
  );
}
