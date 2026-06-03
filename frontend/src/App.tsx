import { useState, useRef } from "react";
import { speakText, readFileApi, audioUrl } from "./api/voxread";
import Controls from "./components/Controls";
import AudioPlayer from "./components/AudioPlayer";
import type { Backend } from "./api/voxread";

type Mode = "text" | "file";
type Status = "idle" | "loading" | "done" | "error";

export default function App() {
  const [mode, setMode] = useState<Mode>("text");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [backend, setBackend] = useState<Backend>("gtts");
  const [lang, setLang] = useState("en");
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState("");
  const [audioUrls, setAudioUrls] = useState<string[]>([]);
  const [wordCount, setWordCount] = useState(0);
  const [chunks, setChunks] = useState(1);
  const [dragging, setDragging] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  async function handleSubmit() {
    setStatus("loading");
    setError("");
    setAudioUrls([]);

    try {
      if (mode === "text") {
        if (!text.trim()) throw new Error("Enter some text first.");
        const res = await speakText(text, backend, lang);
        setAudioUrls(res.downloads.map(audioUrl));
        setWordCount(res.words);
        setChunks(1);
      } else {
        if (!file) throw new Error("Select a file first.");
        const res = await readFileApi(file, backend, lang);
        setAudioUrls(res.downloads.map(audioUrl));
        setWordCount(res.words);
        setChunks(res.chunks);
      }
      setStatus("done");
    } catch (e) {
      setError((e as Error).message);
      setStatus("error");
    }
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) setFile(f);
  }

  const wordCountDisplay = text.trim() ? text.trim().split(/\s+/).length : 0;

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      padding: "48px 24px",
      maxWidth: "680px",
      margin: "0 auto",
      gap: "32px",
    }}>

      {/* Header */}
      <div style={{ textAlign: "center", width: "100%" }}>
        <div style={{
          fontSize: "11px",
          letterSpacing: "0.2em",
          color: "var(--accent)",
          fontFamily: "var(--mono)",
          marginBottom: "12px",
          textTransform: "uppercase",
        }}>
          by Elijah Ngocho
        </div>
        <h1 style={{
          fontSize: "clamp(2.5rem, 8vw, 4rem)",
          fontWeight: 800,
          letterSpacing: "-0.03em",
          lineHeight: 1,
          background: "linear-gradient(135deg, var(--text) 0%, var(--accent) 60%, var(--accent2) 100%)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
        }}>
          voxread
        </h1>
        <p style={{ color: "var(--muted)", marginTop: "8px", fontSize: "14px", fontFamily: "var(--mono)" }}>
          text-to-speech · python + typescript
        </p>
      </div>

      {/* Mode tabs */}
      <div style={{
        display: "flex",
        gap: "4px",
        background: "var(--surface)",
        padding: "4px",
        borderRadius: "10px",
        border: "1px solid var(--border)",
        width: "100%",
      }}>
        {(["text", "file"] as Mode[]).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            style={{
              flex: 1,
              padding: "10px",
              borderRadius: "8px",
              fontSize: "14px",
              fontWeight: 600,
              background: mode === m ? "var(--accent)" : "transparent",
              color: mode === m ? "#fff" : "var(--muted)",
              transition: "all 0.15s",
            }}
          >
            {m === "text" ? "✏ Text" : "📄 File"}
          </button>
        ))}
      </div>

      {/* Input area */}
      <div style={{ width: "100%", display: "flex", flexDirection: "column", gap: "16px" }}>
        {mode === "text" ? (
          <div style={{ position: "relative" }}>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Type or paste text here..."
              rows={6}
              style={{
                width: "100%",
                background: "var(--surface)",
                border: "1px solid var(--border)",
                borderRadius: "var(--radius)",
                padding: "16px",
                color: "var(--text)",
                fontSize: "15px",
                lineHeight: 1.6,
                resize: "vertical",
                transition: "border-color 0.15s",
              }}
              onFocus={(e) => e.target.style.borderColor = "var(--accent)"}
              onBlur={(e) => e.target.style.borderColor = "var(--border)"}
            />
            <span style={{
              position: "absolute",
              bottom: "10px",
              right: "14px",
              fontSize: "11px",
              color: "var(--muted)",
              fontFamily: "var(--mono)",
            }}>
              {wordCountDisplay} words
            </span>
          </div>
        ) : (
          <div
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileRef.current?.click()}
            style={{
              border: `2px dashed ${dragging ? "var(--accent)" : file ? "var(--accent3)" : "var(--border)"}`,
              borderRadius: "var(--radius)",
              padding: "48px 24px",
              textAlign: "center",
              cursor: "pointer",
              background: dragging ? "rgba(124,106,255,0.05)" : "var(--surface)",
              transition: "all 0.15s",
            }}
          >
            <input
              ref={fileRef}
              type="file"
              accept=".txt,.pdf,.docx"
              style={{ display: "none" }}
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
            {file ? (
              <>
                <div style={{ fontSize: "24px", marginBottom: "8px" }}>📄</div>
                <div style={{ color: "var(--accent3)", fontFamily: "var(--mono)", fontSize: "14px" }}>
                  {file.name}
                </div>
                <div style={{ color: "var(--muted)", fontSize: "12px", marginTop: "4px" }}>
                  {(file.size / 1024).toFixed(1)} KB
                </div>
              </>
            ) : (
              <>
                <div style={{ fontSize: "32px", marginBottom: "12px" }}>↑</div>
                <div style={{ color: "var(--text)", fontSize: "15px", marginBottom: "4px" }}>
                  Drop a file or click to browse
                </div>
                <div style={{ color: "var(--muted)", fontSize: "13px", fontFamily: "var(--mono)" }}>
                  .txt · .pdf · .docx
                </div>
              </>
            )}
          </div>
        )}

        {/* Controls */}
        <Controls
          backend={backend}
          lang={lang}
          onBackendChange={setBackend}
          onLangChange={setLang}
        />

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={status === "loading"}
          style={{
            width: "100%",
            padding: "14px",
            borderRadius: "var(--radius)",
            fontSize: "15px",
            fontWeight: 700,
            letterSpacing: "0.05em",
            background: status === "loading"
              ? "var(--surface2)"
              : "linear-gradient(135deg, var(--accent), var(--accent2))",
            color: status === "loading" ? "var(--muted)" : "#fff",
            transition: "all 0.2s",
            transform: status === "loading" ? "scale(0.99)" : "scale(1)",
          }}
        >
          {status === "loading" ? "synthesising..." : "▶  speak"}
        </button>
      </div>

      {/* Error */}
      {status === "error" && (
        <div style={{
          width: "100%",
          padding: "14px 16px",
          background: "rgba(255,106,106,0.08)",
          border: "1px solid var(--error)",
          borderRadius: "var(--radius)",
          color: "var(--error)",
          fontSize: "13px",
          fontFamily: "var(--mono)",
        }}>
          ✗ {error}
        </div>
      )}

      {/* Audio player */}
      {status === "done" && audioUrls.length > 0 && (
        <div style={{ width: "100%" }}>
          <AudioPlayer urls={audioUrls} wordCount={wordCount} chunks={chunks} />
        </div>
      )}

      {/* Footer */}
      <footer style={{
        marginTop: "auto",
        fontSize: "11px",
        color: "var(--muted)",
        fontFamily: "var(--mono)",
        textAlign: "center",
      }}>
        voxread · python + typescript ·{" "}
        <a href="https://github.com/ngocho24/voxread" style={{ color: "var(--accent)", textDecoration: "none" }}>
          github.com/ngocho24
        </a>
      </footer>
    </div>
  );
}
