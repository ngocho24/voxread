#!/usr/bin/env tsx
/**
 * voxread — TypeScript CLI wrapper
 *
 * Typed client for the voxread Flask API.
 * Supports speak, read, and health commands.
 *
 * @module voxread-cli
 */

import * as fs from "node:fs";
import * as path from "node:path";

// ------------------------------------------------------------------
// Types
// ------------------------------------------------------------------

/** Supported TTS backends */
type Backend = "gtts" | "pyttsx3";

/** Options for the speak command */
interface SpeakOptions {
  text: string;
  backend: Backend;
  lang: string;
}

/** Options for the read command */
interface ReadOptions {
  filePath: string;
  backend: Backend;
  lang: string;
}

/** Successful API response */
interface VoxResponse {
  status: "ok";
  files?: string[];
  downloads: string[];
  words: number;
  chunks?: number;
}

/** Error response */
interface VoxError {
  error: string;
}

// ------------------------------------------------------------------
// Config
// ------------------------------------------------------------------

const BASE_URL = "http://localhost:5000";

// ------------------------------------------------------------------
// API client
// ------------------------------------------------------------------

/**
 * POST /speak — synthesise raw text.
 *
 * @param options - SpeakOptions
 * @returns VoxResponse
 */
async function speak(options: SpeakOptions): Promise<VoxResponse> {
  const res = await fetch(`${BASE_URL}/speak`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: options.text,
      backend: options.backend,
      lang: options.lang,
    }),
  });

  const data = (await res.json()) as VoxResponse | VoxError;
  if (!res.ok || "error" in data) {
    throw new Error((data as VoxError).error ?? "Unknown error");
  }
  return data as VoxResponse;
}

/**
 * POST /read — upload a file and synthesise its contents.
 *
 * @param options - ReadOptions
 * @returns VoxResponse
 */
async function readFile(options: ReadOptions): Promise<VoxResponse> {
  if (!fs.existsSync(options.filePath)) {
    throw new Error(`File not found: ${options.filePath}`);
  }

  const form = new FormData();
  const blob = new Blob([fs.readFileSync(options.filePath)]);
  form.append("file", blob, path.basename(options.filePath));
  form.append("backend", options.backend);
  form.append("lang", options.lang);

  const res = await fetch(`${BASE_URL}/read`, {
    method: "POST",
    body: form,
  });

  const data = (await res.json()) as VoxResponse | VoxError;
  if (!res.ok || "error" in data) {
    throw new Error((data as VoxError).error ?? "Unknown error");
  }
  return data as VoxResponse;
}

/**
 * GET /health — check if the API is running.
 */
async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

// ------------------------------------------------------------------
// Arg parser
// ------------------------------------------------------------------

function parseArgs(args: string[]): Record<string, string> {
  const result: Record<string, string> = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith("--") && args[i + 1] !== undefined) {
      result[arg.slice(2)] = args[++i] as string;
    } else if (result["_arg"] === undefined) {
      result["_arg"] = arg;
    }
  }
  return result;
}

function printUsage(): void {
  console.log(`
voxread — text-to-speech CLI (TypeScript)

Usage:
  tsx index.ts speak <text> [--backend gtts|pyttsx3] [--lang en]
  tsx index.ts read <file>  [--backend gtts|pyttsx3] [--lang en]
  tsx index.ts health

Examples:
  tsx index.ts speak "Hello from voxread"
  tsx index.ts speak "Habari yako" --lang sw
  tsx index.ts read ../../test_input.txt
  tsx index.ts health
  `);
}

// ------------------------------------------------------------------
// Main
// ------------------------------------------------------------------

async function main(): Promise<void> {
  const argv = process.argv.slice(2);
  const command = argv[0];

  if (!command || command === "--help" || command === "-h") {
    printUsage();
    process.exit(0);
  }

  if (command === "health") {
    const up = await checkHealth();
    if (up) {
      console.log("✓ voxread API is up at", BASE_URL);
    } else {
      console.error("✗ API not running. Start it with: python -m tts_reader.api");
      process.exit(1);
    }
    return;
  }

  const args = parseArgs(argv.slice(1));
  const backend: Backend = (args["backend"] as Backend) ?? "gtts";
  const lang: string = args["lang"] ?? "en";
  const argVal: string = args["_arg"] ?? "";

  if (command === "speak") {
    if (!argVal) {
      console.error('✗ Missing text. Usage: tsx index.ts speak "your text"');
      process.exit(1);
    }
    console.log("→ Synthesising...");
    try {
      const result = await speak({ text: argVal, backend, lang });
      const downloads = Array.isArray(result.downloads)
        ? result.downloads
        : [result.downloads];
      console.log(`✓ Done. ${result.words} words.`);
      downloads.forEach((d) => console.log(`  Download: ${BASE_URL}${d}`));
    } catch (err) {
      console.error("✗ Error:", (err as Error).message);
      process.exit(1);
    }
    return;
  }

  if (command === "read") {
    if (!argVal) {
      console.error("✗ Missing file. Usage: tsx index.ts read <file>");
      process.exit(1);
    }
    console.log(`→ Reading: ${argVal}`);
    try {
      const result = await readFile({ filePath: argVal, backend, lang });
      const downloads = Array.isArray(result.downloads)
        ? result.downloads
        : [result.downloads];
      console.log(`✓ Done. ${result.words} words, ${result.chunks ?? 1} chunk(s).`);
      downloads.forEach((d) => console.log(`  Download: ${BASE_URL}${d}`));
    } catch (err) {
      console.error("✗ Error:", (err as Error).message);
      process.exit(1);
    }
    return;
  }

  console.error(`✗ Unknown command: ${command}`);
  printUsage();
  process.exit(1);
}

main();
