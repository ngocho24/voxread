import type { Backend } from "../api/voxread";

interface Props {
  backend: Backend;
  lang: string;
  onBackendChange: (b: Backend) => void;
  onLangChange: (l: string) => void;
}

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "sw", label: "Swahili" },
  { code: "fr", label: "French" },
  { code: "de", label: "German" },
  { code: "es", label: "Spanish" },
  { code: "ar", label: "Arabic" },
];

export default function Controls({ backend, lang, onBackendChange, onLangChange }: Props) {
  return (
    <div style={{
      display: "flex", gap: "12px", flexWrap: "wrap"
    }}>
      {/* Backend toggle */}
      <div style={{ display: "flex", gap: "4px", background: "var(--surface2)", padding: "4px", borderRadius: "8px", border: "1px solid var(--border)" }}>
        {(["gtts", "pyttsx3"] as Backend[]).map((b) => (
          <button
            key={b}
            onClick={() => onBackendChange(b)}
            style={{
              padding: "6px 14px",
              borderRadius: "6px",
              fontSize: "13px",
              fontFamily: "var(--mono)",
              background: backend === b ? "var(--accent)" : "transparent",
              color: backend === b ? "#fff" : "var(--muted)",
              transition: "all 0.15s",
              fontWeight: backend === b ? 600 : 400,
            }}
          >
            {b}
          </button>
        ))}
      </div>

      {/* Language selector */}
      <select
        value={lang}
        onChange={(e) => onLangChange(e.target.value)}
        style={{
          background: "var(--surface2)",
          color: "var(--text)",
          border: "1px solid var(--border)",
          borderRadius: "8px",
          padding: "6px 12px",
          fontSize: "13px",
          cursor: "pointer",
        }}
      >
        {LANGUAGES.map((l) => (
          <option key={l.code} value={l.code}>{l.label}</option>
        ))}
      </select>
    </div>
  );
}
