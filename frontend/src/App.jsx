// import { useState } from 'react'
// import heroImg from './assets/hero.png'
// import reactLogo from './assets/react.svg'
// import viteLogo from './assets/vite.svg'
// import './App.css'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <section id="center">
//         <div className="hero">
//           <img src={heroImg} className="base" width="170" height="179" alt="" />
//           <img src={reactLogo} className="framework" alt="React logo" />
//           <img src={viteLogo} className="vite" alt="Vite logo" />
//         </div>
//         <div>
//           <h1>Get started</h1>
//           <p>
//             Edit <code>src/App.jsx</code> and save to test <code>HMR</code>
//           </p>
//         </div>
//         <button
//           type="button"
//           className="counter"
//           onClick={() => setCount((count) => count + 1)}
//         >
//           Count is {count}
//         </button>
//       </section>

//       <div className="ticks"></div>

//       <section id="next-steps">
//         <div id="docs">
//           <svg className="icon" role="presentation" aria-hidden="true">
//             <use href="/icons.svg#documentation-icon"></use>
//           </svg>
//           <h2>Documentation</h2>
//           <p>Your questions, answered</p>
//           <ul>
//             <li>
//               <a href="https://vite.dev/" target="_blank">
//                 <img className="logo" src={viteLogo} alt="" />
//                 Explore Vite
//               </a>
//             </li>
//             <li>
//               <a href="https://react.dev/" target="_blank">
//                 <img className="button-icon" src={reactLogo} alt="" />
//                 Learn more
//               </a>
//             </li>
//           </ul>
//         </div>
//         <div id="social">
//           <svg className="icon" role="presentation" aria-hidden="true">
//             <use href="/icons.svg#social-icon"></use>
//           </svg>
//           <h2>Connect with us</h2>
//           <p>Join the Vite community</p>
//           <ul>
//             <li>
//               <a href="https://github.com/vitejs/vite" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#github-icon"></use>
//                 </svg>
//                 GitHub
//               </a>
//             </li>
//             <li>
//               <a href="https://chat.vite.dev/" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#discord-icon"></use>
//                 </svg>
//                 Discord
//               </a>
//             </li>
//             <li>
//               <a href="https://x.com/vite_js" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#x-icon"></use>
//                 </svg>
//                 X.com
//               </a>
//             </li>
//             <li>
//               <a href="https://bsky.app/profile/vite.dev" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#bluesky-icon"></use>
//                 </svg>
//                 Bluesky
//               </a>
//             </li>
//           </ul>
//         </div>
//       </section>

//       <div className="ticks"></div>
//       <section id="spacer"></section>
//     </>
//   )
// }

// export default App










import { useEffect, useRef, useState } from "react";
import {
  FileText,
  UploadCloud,
  Send,
  Sparkles,
  Plus,
  LoaderCircle,
  MessageSquare,
} from "lucide-react";

import {
  getDocuments,
  uploadDocument,
  askQuestion,
  deleteDocument,
} from "./services/api";

import DocumentList from "./components/DocumentList";
import ChatPanel from "./components/ChatPanel";
import "./styles.css";

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const fileRef = useRef(null);

  const selectedDocument = documents.find(
    (doc) => doc.document_id === selectedId
  );

  async function loadDocuments() {
    try {
      const data = await getDocuments();
      const list = data.documents || [];

      setDocuments(list);

      setSelectedId((current) =>
        list.some((doc) => doc.document_id === current)
          ? current
          : list[0]?.document_id || ""
      );
    } catch (err) {
      setError(`Could not load documents: ${err.message}`);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  async function handleUpload(event) {
    const files = Array.from(event.target.files || []);

    if (!files.length) return;

    setError("");
    setUploading(true);

    try {
      for (const file of files) {
        const extension = file.name.split(".").pop().toLowerCase();

        if (!["pdf", "txt", "docx"].includes(extension)) {
          throw new Error(
            "Only PDF, TXT, and DOCX files are supported."
          );
        }

        if (file.size > 20 * 1024 * 1024) {
          throw new Error("Maximum file size is 20 MB.");
        }

        const result = await uploadDocument(file);

        const newDocument = {
          document_id: result.document_id,
          filename: result.filename || file.name,
          details: result.details || {},
        };

        setDocuments((current) => [
          newDocument,
          ...current.filter(
            (doc) => doc.document_id !== result.document_id
          ),
        ]);

        setSelectedId(result.document_id);
        setMessages([]);
      }
    } catch (err) {
      setError(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  async function handleAsk(event) {
    event.preventDefault();

    if (!question.trim() || !selectedId || loading) return;

    const currentQuestion = question.trim();

    setMessages((current) => [
      ...current,
      { role: "user", content: currentQuestion },
    ]);

    setQuestion("");
    setLoading(true);
    setError("");

    try {
      const result = await askQuestion(
        selectedId,
        currentQuestion
      );

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: result.answer,
          sources: result.sources || [],
        },
      ]);
    } catch (err) {
      setError(`Question answering failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(documentId) {
    const document = documents.find(
      (doc) => doc.document_id === documentId
    );

    if (
      !window.confirm(
        `Delete ${document?.filename || "this document"}?`
      )
    ) {
      return;
    }

    try {
      await deleteDocument(documentId);

      setDocuments((current) =>
        current.filter(
          (doc) => doc.document_id !== documentId
        )
      );

      if (selectedId === documentId) {
        setSelectedId("");
        setMessages([]);
      }
    } catch (err) {
      setError(`Delete failed: ${err.message}`);
    }
  }

  return (
    <div className="app-shell">
      {/* Sidebar with document list */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-icon">
            <Sparkles size={20} />
          </div>
          <div>
            <h2>DocuMind AI</h2>
            <p>Document Workspace</p>
          </div>
        </div>

        <DocumentList
          documents={documents}
          selectedId={selectedId}
          onSelect={(id) => {
            setSelectedId(id);
            setMessages([]);
            setError("");
          }}
          onDelete={handleDelete}
          onUpload={() => fileRef.current?.click()}
          uploading={uploading}
        />
      </aside>

      {/* Main chat workspace */}
      <main className="main-panel">
        <header className="topbar">
          <div className="brand">
            <div className="brand-icon">
              <Sparkles size={20} />
            </div>

            <div>
              <h2>DocuMind AI</h2>
              <p>Document Intelligence Workspace</p>
            </div>
          </div>

          <button
            type="button"
            className="primary-button"
            onClick={() => fileRef.current?.click()}
            disabled={uploading}
          >
            {uploading ? (
              <LoaderCircle className="spin" size={17} />
            ) : (
              <UploadCloud size={17} />
            )}

            {uploading
              ? "Processing..."
              : "Upload document"}
          </button>
        </header>

        <section className="workspace">
          <div className="page-heading">
            <span className="eyebrow">
              AI-POWERED RESEARCH
            </span>

            <h1>Understand your documents.</h1>

            <p>
              Ask questions and get answers grounded in your
              document content.
            </p>
          </div>

          {error && (
            <div className="error-banner">
              <span>{error}</span>

              <button
                type="button"
                onClick={() => setError("")}
              >
                Dismiss
              </button>
            </div>
          )}

          <section className="chat-card">
            <div className="chat-header">
              <div>
                <MessageSquare size={20} />

                <div>
                  <h3>Document assistant</h3>

                  <p>
                    {selectedDocument
                      ? selectedDocument.filename
                      : "Select a document to begin"}
                  </p>
                </div>
              </div>

              <span className="status-badge">
                {selectedDocument ? "Ready" : "No document"}
              </span>
            </div>

            {!selectedDocument ? (
              <div className="empty-state">
                <div className="empty-icon">
                  <FileText size={34} />
                </div>

                <h2>Start with a document</h2>

                <p>
                  Upload a PDF, Word document, or text file.
                  Then ask questions about its contents.
                </p>

                <button
                  type="button"
                  className="primary-button"
                  onClick={() => fileRef.current?.click()}
                  disabled={uploading}
                >
                  <Plus size={17} />
                  Upload your first document
                </button>
              </div>
            ) : (
              <ChatPanel
                messages={messages}
                loading={loading}
              />
            )}

            <form
              className="question-form"
              onSubmit={handleAsk}
            >
              <textarea
                rows={2}
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" &&
                    !event.shiftKey
                  ) {
                    event.preventDefault();
                    handleAsk(event);
                  }
                }}
                placeholder={
                  selectedDocument
                    ? "Ask anything about this document..."
                    : "Upload a document first..."
                }
                disabled={!selectedDocument || loading}
              />

              <div className="form-footer">
                <span>
                  {selectedDocument
                    ? "Answers include source passages"
                    : "PDF · DOCX · TXT"}
                </span>

                <button
                  type="submit"
                  className="send-button"
                  disabled={
                    !selectedDocument ||
                    !question.trim() ||
                    loading
                  }
                  aria-label="Send question"
                >
                  {loading ? (
                    <LoaderCircle
                      className="spin"
                      size={17}
                    />
                  ) : (
                    <Send size={17} />
                  )}
                </button>
              </div>
            </form>
          </section>
        </section>

        <footer className="footer">
          DocuMind AI · Verify important answers against the
          cited sources.
        </footer>
      </main>

      {/* Hidden file picker */}
      <input
        ref={fileRef}
        type="file"
        multiple
        accept=".pdf,.txt,.docx"
        hidden
        onChange={handleUpload}
      />
    </div>
  );
}