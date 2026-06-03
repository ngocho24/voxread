/**
 * voxread API client
 * Typed interface to the Flask REST backend.
 */

const BASE_URL = "http://localhost:5000";

export type Backend = "gtts" | "pyttsx3";

export interface SpeakResponse {
  status: "ok";
  files: string[];
  downloads: string[];
  words: number;
}

export interface ReadResponse {
  status: "ok";
  files: string[];
  downloads: string[];
  words: number;
  chunks: number;
}

export interface ApiError {
  error: string;
}

export async function speakText(
  text: string,
  backend: Backend = "gtts",
  lang: string = "en"
): Promise<SpeakResponse> {
  const res = await fetch(`${BASE_URL}/speak`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, backend, lang }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error ?? "Speak failed");
  return data;
}

export async function readFileApi(
  file: File,
  backend: Backend = "gtts",
  lang: string = "en"
): Promise<ReadResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("backend", backend);
  form.append("lang", lang);

  const res = await fetch(`${BASE_URL}/read`, {
    method: "POST",
    body: form,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error ?? "Read failed");
  return data;
}

export function audioUrl(download: string): string {
  return `${BASE_URL}${download}`;
}
