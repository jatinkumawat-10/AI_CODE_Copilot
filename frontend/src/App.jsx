import { useRef, useState } from "react";

const API_BASE = "http://localhost:8000/api/v1";

function App() {
  const [mode, setMode] = useState("paste"); // "paste" | "upload"
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

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

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

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
          <ul>
            {result.issues.length === 0 ? (
              <li>None found</li>
            ) : (
              result.issues.map((issue, i) => <li key={i}>{issue}</li>)
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