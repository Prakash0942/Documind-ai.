
import { FileText, Trash2, Upload, File } from "lucide-react";

function DocumentList({
  documents = [],
  selectedId,
  onSelect,
  onDelete,
  onUpload,
  uploading = false,
}) {
  return (
    <div className="document-list">
      <div className="document-list-header">
        <div>
          <h2>My Documents</h2>
          <p>{documents.length} document(s) uploaded</p>
        </div>

        <button
          type="button"
          className="upload-button"
          onClick={onUpload}
          disabled={uploading}
        >
          <Upload size={16} />
          {uploading ? "Uploading..." : "Upload"}
        </button>
      </div>

      {documents.length === 0 ? (
        <div className="empty-documents">
          <FileText size={36} />
          <p>No documents uploaded yet.</p>
          <span>Upload a PDF, DOCX, or TXT file to get started.</span>
        </div>
      ) : (
        <ul className="document-items">
          {documents.map((document) => {
            const documentId =
              document.document_id ?? document.id;

            const filename =
              document.filename ??
              document.document ??
              document.name ??
              "Untitled document";

            const isSelected = documentId === selectedId;

            return (
              <li
                key={documentId}
                className={`document-item ${
                  isSelected ? "selected" : ""
                }`}
              >
                <button
                  type="button"
                  className="document-select"
                  onClick={() => onSelect(documentId)}
                  title={filename}
                >
                  <File size={20} />

                  <span className="document-filename">
                    {filename}
                  </span>
                </button>

                <button
                  type="button"
                  className="delete-button"
                  onClick={() => onDelete(documentId)}
                  aria-label={`Delete ${filename}`}
                  title="Delete document"
                >
                  <Trash2 size={16} />
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export default DocumentList;
