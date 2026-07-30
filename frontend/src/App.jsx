import { useEffect, useRef, useState } from "react";

const API_BASE = "https://ai-code-copilot-o12g.onrender.com/api/v1";

function App() {
  const [mode, setMode] = useState("paste"); // "paste" | "upload"
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [items, setItems] = useState([]);
  const [itemsError, setItemsError] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!result?.review_run_id) return;

    async function fetchItems() {
      try {
        const response = await fetch(
          `${API_BASE}/review-runs/${result.review_run_id}/items`
        );
        if (!response.ok) throw new Error(`Failed to load items (${response.status})`);
        const data = await response.json();
        setItems(data);
      } catch (err) {
        setItemsError(err.message);
      }
    }

    fetchItems();
  }, [result]);

  function handleDragOver(e) {
    e.preventDefault(); // required, or the browser's default (open file in tab) takes over
    setIsDragging(true);
  }

  function handleDragLeave() {
    setIsDragging(false);
  }

  function handleDrop(e) {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) setFile(droppedFile);
  }

  async function handleStatusChange(itemId, newStatus) {
    try {
      const response = await fetch(`${API_BASE}/review-items/${itemId}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.detail || `Request failed (${response.status})`);
      }

      const updated = await response.json();

      // Update just this one item in place, rather than refetching the
      // whole list -- cheaper, and avoids a visible flicker.
      setItems((prev) =>
        prev.map((item) => (item.id === itemId ? updated : item))
      );
    } catch (err) {
      alert(`Could not update status: ${err.message}`);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setItems([]);
    setItemsError(null);

    try {
      let response;

      if (mode === "paste") {
        response = await fetch(`${API_BASE}/review`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code, language }),
        });
      } else {
        const formData = new FormData();
        formData.append("file", file);

        // No Content-Type header here — the browser sets it automatically
        // with the correct multipart boundary. Setting it manually would
        // break the upload.
        response = await fetch(`${API_BASE}/review/file`, {
          method: "POST",
          body: formData,
        });
      }

      if (!response.ok) {
        const errBody = await response.json().catch(() => null);
        throw new Error(errBody?.message || `Request failed (${response.status})`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 700, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>AI Code Review</h1>

      <details style={{ marginBottom: "1.5rem", fontSize: "0.9rem" }}>
        <summary style={{ cursor: "pointer", fontWeight: "bold" }}>
          GitHub Integration Setup & API Reference
        </summary>

        <div style={{ marginTop: "1rem", lineHeight: 1.6 }}>
          <h3>Set up automatic PR reviews</h3>
          <p>
            In your repo: <strong>Settings → Webhooks → Add webhook</strong>
          </p>
          <ul>
            <li>
              <strong>Payload URL:</strong>{" "}
              <code>{API_BASE}/webhooks/github</code>
            </li>
            <li>
              <strong>Content type:</strong> <code>application/json</code>
            </li>
            <li>
              <strong>Secret:</strong> must match the{" "}
              <code>GITHUB_WEBHOOK_SECRET</code> configured on this backend
            </li>
            <li>
              <strong>Events:</strong> select "Let me select individual
              events" → check only <strong>Pull requests</strong>
            </li>
          </ul>
          <p>
            Once configured, opening or updating a PR triggers an automatic
            AI review posted as a PR comment. Merging a PR auto-approves any
            issues still marked "proposed" from that PR's reviews.
          </p>

          <h3>API Endpoints</h3>
          <ul>
            <li>
              <code>POST /review</code> — review pasted code (JSON:{" "}
              <code>{"{code, language}"}</code>)
            </li>
            <li>
              <code>POST /review/file</code> — review an uploaded file
              (multipart form, field name <code>file</code>)
            </li>
            <li>
              <code>GET /review-runs/{"{id}"}/items</code> — list a
              specific review's strengths/issues/suggestions with their IDs
            </li>
            <li>
              <code>PATCH /review-items/{"{id}"}/status</code> — transition
              an issue's status (<code>proposed → approved/rejected</code>,{" "}
              <code>approved → applied</code>)
            </li>
          </ul>
        </div>
      </details>

      <form onSubmit={handleSubmit}>
        <label>
          <input
            type="radio"
            checked={mode === "paste"}
            onChange={() => setMode("paste")}
          />
          Paste code
        </label>
        <label style={{ marginLeft: "1rem" }}>
          <input
            type="radio"
            checked={mode === "upload"}
            onChange={() => setMode("upload")}
          />
          Upload file
        </label>

        <br />
        <br />

        {mode === "paste" ? (
          <>
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="typescript">TypeScript</option>
              <option value="java">Java</option>
              <option value="cpp">C++</option>
            </select>

            <br />
            <br />

            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              rows={12}
              style={{ width: "100%", fontFamily: "monospace" }}
              placeholder="Paste code to review..."
            />
          </>
        ) : (
          <div
            onClick={() => fileInputRef.current.click()}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            style={{
              border: `2px dashed ${isDragging ? "#4a9eff" : "#666"}`,
              borderRadius: 8,
              padding: "3rem 1rem",
              textAlign: "center",
              cursor: "pointer",
              backgroundColor: isDragging ? "rgba(74, 158, 255, 0.08)" : "transparent",
              transition: "border-color 0.15s, background-color 0.15s",
            }}
          >
            <p style={{ margin: 0 }}>
              {file
                ? `Selected: ${file.name}`
                : "Drag & drop a file here, or click to browse"}
            </p>
            <p style={{ margin: "0.5rem 0 0", fontSize: "0.8rem", opacity: 0.6 }}>
              .py, .js, .ts, .java, .cpp
            </p>

            <input
              ref={fileInputRef}
              type="file"
              accept=".py,.js,.ts,.java,.cpp"
              onChange={(e) => setFile(e.target.files[0] || null)}
              style={{ display: "none" }}
            />
          </div>
        )}

        <br />
        <br />

        <button
          type="submit"
          disabled={loading || (mode === "paste" ? !code.trim() : !file)}
        >
          {loading ? "Reviewing..." : "Review Code"}
        </button>
      </form>

      {error && (
        <p style={{ color: "red", marginTop: "1rem" }}>Error: {error}</p>
      )}

      {result && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Summary</h2>
          <p>{result.summary}</p>

          <h2>Strengths</h2>
          <ul>
            {result.strengths.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>

          <h2>Issues</h2>
          {itemsError && (
            <p style={{ color: "red" }}>Could not load items: {itemsError}</p>
          )}
          <ul style={{ listStyle: "none", padding: 0 }}>
            {items.filter((item) => item.kind === "issue").length === 0 ? (
              <li>None found</li>
            ) : (
              items
                .filter((item) => item.kind === "issue")
                .map((item) => (
                  <li
                    key={item.id}
                    style={{
                      marginBottom: "0.75rem",
                      padding: "0.5rem",
                      border: "1px solid #444",
                      borderRadius: 6,
                    }}
                  >
                    <div>{item.content}</div>
                    <div style={{ marginTop: "0.4rem", fontSize: "0.85rem" }}>
                      Status: <strong>{item.approval_status}</strong>
                      {item.approval_status === "proposed" && (
                        <>
                          {" "}
                          <button onClick={() => handleStatusChange(item.id, "approved")}>
                            Approve
                          </button>{" "}
                          <button onClick={() => handleStatusChange(item.id, "rejected")}>
                            Reject
                          </button>
                        </>
                      )}
                      {item.approval_status === "approved" && (
                        <>
                          {" "}
                          <button onClick={() => handleStatusChange(item.id, "applied")}>
                            Mark Applied
                          </button>
                        </>
                      )}
                    </div>
                  </li>
                ))
            )}
          </ul>

          <h2>Suggestions</h2>
          <ul>
            {result.suggestions.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>

          <h2>Verdict</h2>
          <p>{result.verdict}</p>
        </div>
      )}
    </div>
  );
}

export default App;