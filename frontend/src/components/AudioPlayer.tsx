interface Props {
  urls: string[];
  wordCount: number;
  chunks: number;
}

export default function AudioPlayer({ urls, wordCount, chunks }: Props) {
  return (
    <div style={{ background: "var(--surface)", border: "1px solid var(--accent)", borderRadius: "var(--radius)", padding: "20px", display: "flex", flexDirection: "column", gap: "12px", boxShadow: "0 0 30px rgba(124,106,255,0.1)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: "13px", color: "var(--accent)", fontFamily: "var(--mono)", fontWeight: 600 }}>✓ READY</span>
        <span style={{ fontSize: "12px", color: "var(--muted)", fontFamily: "var(--mono)" }}>{wordCount} words · {chunks} chunk{chunks !== 1 ? "s" : ""}</span>
      </div>
      {urls.map((url, i) => (
        <div key={url} style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
          {chunks > 1 && <span style={{ fontSize: "11px", color: "var(--muted)", fontFamily: "var(--mono)" }}>Part {i + 1}</span>}
          <audio controls src={url} style={{ width: "100%", height: "36px" }} />
          <a href={url} download style={{ fontSize: "12px", color: "var(--accent2)", fontFamily: "var(--mono)", textDecoration: "none" }}>↓ download</a>
        </div>
      ))}
    </div>
  );
}
