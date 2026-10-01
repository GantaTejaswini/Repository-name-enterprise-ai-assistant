import { useEffect, useState } from "react";

import {
  login,
  sendChat,
  getHealth,
  getDiagnostics,
  getDocuments,
  uploadDocument,
  deleteDocument,
} from "./api";

function App() {
  const [email, setEmail] = useState("demo@company.com");
  const [password, setPassword] = useState("password123");

  const [token, setToken] = useState(
    localStorage.getItem("enterprise_ai_token") || "",
  );

  const [activePage, setActivePage] = useState("chat");

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);

  const [documents, setDocuments] = useState([]);
  const [diagnostics, setDiagnostics] = useState(null);
  const [health, setHealth] = useState(null);

  const [loading, setLoading] = useState(false);
  const [loginLoading, setLoginLoading] = useState(false);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    if (token) {
      loadHealth();
    }
  }, [token]);

  useEffect(() => {
    if (token && activePage === "documents") {
      loadDocuments();
    }

    if (token && activePage === "diagnostics") {
      loadDiagnostics();
    }
  }, [token, activePage]);

  async function loadHealth() {
    try {
      const data = await getHealth();
      setHealth(data);
    } catch (err) {
      console.error(err);
      setHealth(null);
    }
  }

  async function loadDocuments() {
    setDocumentsLoading(true);
    setError("");

    try {
      const data = await getDocuments(token);

      if (Array.isArray(data)) {
        setDocuments(data);
      } else if (Array.isArray(data.documents)) {
        setDocuments(data.documents);
      } else {
        setDocuments([]);
      }
    } catch (err) {
      console.error(err);

      if (err.response?.status === 401) {
        handleSessionExpired();
      } else {
        setError(
          err.response?.data?.detail ||
            "Failed to load documents.",
        );
      }
    } finally {
      setDocumentsLoading(false);
    }
  }

  async function loadDiagnostics() {
    setError("");

    try {
      const data = await getDiagnostics(token);
      setDiagnostics(data);
    } catch (err) {
      console.error(err);

      if (err.response?.status === 401) {
        handleSessionExpired();
      } else {
        setError(
          err.response?.data?.detail ||
            "Failed to load diagnostics.",
        );
      }
    }
  }

  async function handleLogin(event) {
    event.preventDefault();

    setError("");
    setSuccess("");
    setLoginLoading(true);

    try {
      const data = await login(email, password);

      localStorage.setItem(
        "enterprise_ai_token",
        data.access_token,
      );

      setToken(data.access_token);
    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Login failed. Please check your credentials.",
      );
    } finally {
      setLoginLoading(false);
    }
  }

  async function handleChat(event) {
    event.preventDefault();

    if (!question.trim()) {
      return;
    }

    setError("");
    setSuccess("");
    setLoading(true);
    setAnswer("");
    setSources([]);

    try {
      const data = await sendChat(
        question.trim(),
        token,
        5,
      );

      setAnswer(
        data.answer || "No answer was returned.",
      );

      setSources(data.sources || []);
    } catch (err) {
      console.error(err);

      if (err.response?.status === 401) {
        handleSessionExpired();
      } else {
        setError(
          err.response?.data?.detail ||
            "Failed to process your question.",
        );
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(event) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (file.type !== "application/pdf") {
      setError("Only PDF files are supported.");
      event.target.value = "";
      return;
    }

    setUploading(true);
    setError("");
    setSuccess("");

    try {
      const data = await uploadDocument(
        file,
        token,
      );

      setSuccess(
        data.message ||
          "Document uploaded and processed successfully.",
      );

      await loadDocuments();
    } catch (err) {
      console.error(err);

      if (err.response?.status === 401) {
        handleSessionExpired();
      } else {
        setError(
          err.response?.data?.detail ||
            "Document upload failed.",
        );
      }
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  async function handleDeleteDocument(documentId) {
    const confirmed = window.confirm(
      "Delete this document and its indexed chunks?",
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setSuccess("");

    try {
      await deleteDocument(documentId, token);

      setSuccess("Document deleted successfully.");

      await loadDocuments();
    } catch (err) {
      console.error(err);

      if (err.response?.status === 401) {
        handleSessionExpired();
      } else {
        setError(
          err.response?.data?.detail ||
            "Failed to delete document.",
        );
      }
    }
  }

  function handleSessionExpired() {
    localStorage.removeItem("enterprise_ai_token");

    setToken("");
    setQuestion("");
    setAnswer("");
    setSources([]);
    setDocuments([]);
    setDiagnostics(null);
    setError("Your session has expired. Please login again.");
  }

  function handleLogout() {
    localStorage.removeItem("enterprise_ai_token");

    setToken("");
    setQuestion("");
    setAnswer("");
    setSources([]);
    setDocuments([]);
    setDiagnostics(null);
    setError("");
    setSuccess("");
  }

  function startNewChat() {
    setActivePage("chat");
    setQuestion("");
    setAnswer("");
    setSources([]);
    setError("");
    setSuccess("");
  }

  function useSuggestion(text) {
    setQuestion(text);
  }

  function openPage(page) {
    setActivePage(page);
    setError("");
    setSuccess("");
  }

  function renderChat() {
    return (
      <>
        <section className="chat-area">
          {!answer && !loading ? (
            <div className="welcome">
              <div className="welcome-icon">✦</div>

              <h2>How can I help you?</h2>

              <p>
                Ask questions about your organization's
                documents and enterprise knowledge.
              </p>

              <div className="suggestions">
                <button
                  onClick={() =>
                    useSuggestion("What is Python?")
                  }
                >
                  What is Python?
                </button>

                <button
                  onClick={() =>
                    useSuggestion(
                      "Summarize the uploaded documents",
                    )
                  }
                >
                  Summarize the uploaded documents
                </button>

                <button
                  onClick={() =>
                    useSuggestion(
                      "What information is available?",
                    )
                  }
                >
                  What information is available?
                </button>
              </div>
            </div>
          ) : (
            <div className="conversation">
              <div className="question-bubble">
                <strong>You</strong>
                <p>{question}</p>
              </div>

              {loading && (
                <div className="answer-card">
                  <div className="loading-indicator">
                    Searching enterprise knowledge...
                  </div>
                </div>
              )}

              {answer && !loading && (
                <>
                  <div className="answer-card">
                    <div className="answer-header">
                      <span className="answer-icon">
                        AI
                      </span>

                      <strong>
                        Enterprise AI
                      </strong>
                    </div>

                    <p className="answer-text">
                      {answer}
                    </p>
                  </div>

                  {sources.length > 0 && (
                    <div className="sources-card">
                      <h3>Sources</h3>

                      {sources.map(
                        (source, index) => (
                          <div
                            className="source-item"
                            key={`${source.chunk_id}-${index}`}
                          >
                            <div className="source-title">
                              {source.document}
                            </div>

                            <div className="source-meta">
                              Page {source.page} •
                              Chunk{" "}
                              {source.chunk_id}
                            </div>

                            <p>
                              {source.content}
                            </p>
                          </div>
                        ),
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {error && (
            <div className="chat-error">
              {error}
            </div>
          )}
        </section>

        <form
          className="input-container"
          onSubmit={handleChat}
        >
          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            placeholder="Ask your enterprise knowledge assistant..."
            rows="1"
            disabled={loading}
          />

          <button
            className="send-button"
            type="submit"
            disabled={
              !question.trim() || loading
            }
          >
            {loading ? "..." : "➤"}
          </button>
        </form>
      </>
    );
  }

  function renderDocuments() {
    return (
      <section className="page-section">
        <div className="page-header">
          <div>
            <h2>Documents</h2>
            <p>
              Upload and manage enterprise knowledge
              documents.
            </p>
          </div>

          <label className="upload-button">
            {uploading
              ? "Processing..."
              : "+ Upload PDF"}

            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleUpload}
              disabled={uploading}
              hidden
            />
          </label>
        </div>

        {success && (
          <div className="success-message">
            {success}
          </div>
        )}

        {error && (
          <div className="chat-error">
            {error}
          </div>
        )}

        {documentsLoading ? (
          <div className="empty-state">
            Loading documents...
          </div>
        ) : documents.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              📄
            </div>

            <h3>No documents yet</h3>

            <p>
              Upload a PDF to build your enterprise
              knowledge base.
            </p>
          </div>
        ) : (
          <div className="document-list">
            {documents.map((document) => (
              <div
                className="document-card"
                key={document.id}
              >
                <div className="document-icon">
                  PDF
                </div>

                <div className="document-info">
                  <h3>
                    {document.filename}
                  </h3>

                  <p>
                    Status:{" "}
                    <strong>
                      {document.status}
                    </strong>
                  </p>

                  <p>
                    Chunks:{" "}
                    {document.chunks_count ??
                      document.chunk_count ??
                      0}
                  </p>
                </div>

                <button
                  className="delete-button"
                  onClick={() =>
                    handleDeleteDocument(
                      document.id,
                    )
                  }
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    );
  }

  function renderDiagnostics() {
    return (
      <section className="page-section">
        <div className="page-header">
          <div>
            <h2>Diagnostics</h2>
            <p>
              Monitor the RAG backend and retrieval
              system.
            </p>
          </div>

          <button
            className="secondary-button"
            onClick={loadDiagnostics}
          >
            Refresh
          </button>
        </div>

        {error && (
          <div className="chat-error">
            {error}
          </div>
        )}

        {diagnostics ? (
          <div className="diagnostic-grid">
            {Object.entries(diagnostics).map(
              ([key, value]) => (
                <div
                  className="diagnostic-card"
                  key={key}
                >
                  <span>
                    {key
                      .replaceAll("_", " ")
                      .replace(
                        /\b\w/g,
                        (letter) =>
                          letter.toUpperCase(),
                      )}
                  </span>

                  <strong>
                    {typeof value === "object"
                      ? JSON.stringify(
                          value,
                          null,
                          2,
                        )
                      : String(value)}
                  </strong>
                </div>
              ),
            )}
          </div>
        ) : (
          <div className="empty-state">
            Loading diagnostics...
          </div>
        )}
      </section>
    );
  }

  function renderSettings() {
    return (
      <section className="page-section">
        <div className="page-header">
          <div>
            <h2>Settings</h2>
            <p>
              Enterprise AI Assistant configuration.
            </p>
          </div>
        </div>

        <div className="settings-grid">
          <div className="setting-card">
            <span>Account</span>
            <strong>
              {email}
            </strong>
          </div>

          <div className="setting-card">
            <span>Role</span>
            <strong>
              Administrator
            </strong>
          </div>

          <div className="setting-card">
            <span>Backend</span>
            <strong>
              {health
                ? "Connected"
                : "Unavailable"}
            </strong>
          </div>

          <div className="setting-card">
            <span>RAG Engine</span>
            <strong>
              Hybrid BM25 + kNN + RRF
            </strong>
          </div>

          <div className="setting-card">
            <span>Embedding Model</span>
            <strong>
              Nemotron Embed 1B
            </strong>
          </div>

          <div className="setting-card">
            <span>LLM Provider</span>
            <strong>
              Extractive / Granite
            </strong>
          </div>
        </div>

        <div className="settings-note">
          <strong>System status</strong>

          <p>
            {health
              ? "The FastAPI backend is reachable."
              : "The FastAPI backend could not be reached."}
          </p>
        </div>
      </section>
    );
  }

  if (!token) {
    return (
      <div className="login-page">
        <div className="login-card">
          <div className="login-icon">
            AI
          </div>

          <h1>Enterprise AI</h1>

          <p className="login-subtitle">
            Secure enterprise knowledge assistant
          </p>

          <form onSubmit={handleLogin}>
            <label>Email</label>

            <input
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              placeholder="Enter your email"
              required
            />

            <label>Password</label>

            <input
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="Enter your password"
              required
            />

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <button
              className="login-button"
              type="submit"
              disabled={loginLoading}
            >
              {loginLoading
                ? "Signing in..."
                : "Sign In"}
            </button>
          </form>

          <div className="demo-login">
            Demo account
            <br />
            demo@company.com
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            AI
          </div>

          <div>
            <h2>Enterprise AI</h2>
            <span>Assistant</span>
          </div>
        </div>

        <button
          className="new-chat"
          onClick={startNewChat}
        >
          + New Chat
        </button>

        <nav className="sidebar-nav">
          <button
            className={
              activePage === "chat"
                ? "active"
                : ""
            }
            onClick={() =>
              openPage("chat")
            }
          >
            💬 Chat
          </button>

          <button
            className={
              activePage === "documents"
                ? "active"
                : ""
            }
            onClick={() =>
              openPage("documents")
            }
          >
            📄 Documents
          </button>

          <button
            className={
              activePage === "diagnostics"
                ? "active"
                : ""
            }
            onClick={() =>
              openPage("diagnostics")
            }
          >
            📊 Diagnostics
          </button>

          <button
            className={
              activePage === "settings"
                ? "active"
                : ""
            }
            onClick={() =>
              openPage("settings")
            }
          >
            ⚙ Settings
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="user-card">
            <div className="avatar">
              D
            </div>

            <div>
              <strong>
                Demo User
              </strong>

              <span>
                Administrator
              </span>
            </div>
          </div>

          <button
            className="logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>
              Enterprise AI Assistant
            </h1>

            <p>
              Secure RAG-powered enterprise
              knowledge assistant
            </p>
          </div>

          <div className="status">
            <span
              className={
                health
                  ? "status-dot"
                  : "status-dot offline"
              }
            ></span>

            {health
              ? "System Ready"
              : "Backend Offline"}
          </div>
        </header>

        {activePage === "chat" &&
          renderChat()}

        {activePage === "documents" &&
          renderDocuments()}

        {activePage === "diagnostics" &&
          renderDiagnostics()}

        {activePage === "settings" &&
          renderSettings()}

        <div className="footer-text">
          Enterprise AI Assistant • Secure
          RAG-powered knowledge search
        </div>
      </main>
    </div>
  );
}

export default App;