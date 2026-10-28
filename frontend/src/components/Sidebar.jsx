
import { FileText, Trash2, UploadCloud, FolderOpen } from "lucide-react";

export default function Sidebar({
  documents,
  selectedId,
  onSelect,
  onDelete,
  onUpload,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">
          <FolderOpen size={20} />
        </div>
        <div>
          <h2>DocuMind <span>AI</span></h2>
          <p>YOUR KNOWLEDGE SPACE</p>
        </div>
      </div>

      <button className="sidebar-upload" onClick={onUpload}>
        <UploadCloud size={17} /> Upload document
      </button>

      <div className="sidebar-heading">
        YOUR DOCUMENTS <span>{documents.length}</span>
      </div>

      <div className="document-list">
        {documents.length === 0 ? (
          <p className="sidebar-empty">
            No documents uploaded yet.
          </p>
        ) : (
          documents.map((doc) => (
            <div
              key={doc.document_id}
              className={`document-row ${
                selectedId === doc.document_id ? "selected" : ""
              }`}
            >
              <button
                className="document-select"
                onClick={() => onSelect(doc.document_id)}
              >
                <FileText size={18} />
                <span>{doc.filename}</span>
              </button>

              <button
                className="delete-button"
                title="Delete document"
                onClick={() => onDelete(doc.document_id)}
              >
                <Trash2 size={15} />
              </button>
            </div>
          ))
        )}
      </div>

      <div className="sidebar-bottom">
        <div className="sidebar-avatar">AI</div>
        <div>
          <strong>Personal workspace</strong>
          <p>AI Document Intelligence</p>
        </div>
      </div>
    </aside>
  );
}
