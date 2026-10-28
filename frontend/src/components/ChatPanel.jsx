
import { Bot, User, FileText, Sparkles } from "lucide-react";
import SourceCard from "./SourceCard";

export default function ChatPanel({ messages, loading }) {
  if (messages.length === 0 && !loading) {
    return (
      <div className="empty-chat">
        <div className="assistant-icon">
          <Sparkles size={23} />
        </div>
        <h3>What would you like to know?</h3>
        <p>
          Ask a question about your selected document.
          Retrieved passages will appear with the answer.
        </p>
        <div className="example-questions">
          <span>Try asking</span>
          <p>Summarize this document</p>
          <p>What are the key points?</p>
          <p>Explain the main concepts</p>
        </div>
      </div>
    );
  }

  return (
    <div className="messages">
      {messages.map((message, index) => (
        <article
          className={`message ${message.role}`}
          key={`${index}-${message.role}`}
        >
          <div className="message-avatar">
            {message.role === "assistant" ? (
              <Bot size={17} />
            ) : (
              <User size={17} />
            )}
          </div>

          <div className="message-body">
            <strong>
              {message.role === "assistant" ? "DocuMind AI" : "You"}
            </strong>

            <p className="message-content">{message.content}</p>

            {message.role === "assistant" &&
              message.sources?.length > 0 && (
                <div className="sources">
                  <h4>
                    <FileText size={15} /> Sources used
                  </h4>

                  {message.sources.map((source, sourceIndex) => (
                    <SourceCard
                      key={`${source.page}-${sourceIndex}`}
                      source={source}
                    />
                  ))}
                </div>
              )}
          </div>
        </article>
      ))}

      {loading && (
        <div className="loading-answer">
          <span className="loading-dot" />
          Searching your document and generating an answer...
        </div>
      )}
    </div>
  );
}
