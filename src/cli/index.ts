#!/usr/bin/env tsx
/**
 * voxread — TypeScript CLI wrapper
 *
 * Spawns the Python Flask API and provides a typed interface
 * for the /speak and /read endpoints.
 *
 * @module voxread-cli
 */

import { execSync, spawn } from "node:child_process";
import * as fs from "node:fs";
import * as path from "node:path";
import * as readline from "node:readline";

// ------------------------------------------------------------------
// Types
// ------------------------------------------------------------------

/** Supported TTS backends */
type Backend = "gtts" | "pyttsx3";

/** Options for the speak command */
interface SpeakOptions {
  text: string;
  backend?: Backend;
  lang?: string;
}

/** Options for the read command */
interface ReadOptions {
  filePath: string;
  backend?: Backend;
  lang?: string;
}

/** Successful speak/read response from the API */
interface VoxResponse {
  status: "ok";
  file?: string;
  files?: string[];
  downloads: string[] | string;
  words: number;
  chunks?: number;
}

/** Error response from the API */
interface VoxError {
  error: string;
}

// ------------------------------------------------------------------
// API client
// ------------------------------------------------------------------

const BASE_URL = "http://localhost:5000";

/**
 * POST /speak — synthesise raw text.
 *
 * @param options - SpeakOptions containing text, backend, lang
 * @returns VoxResponse with download path
 */
async function speak(options: SpeakOptions): Promise<VoxResponse> {
  const res = await fetch(`${BASE_URL}/speak`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: options.text,
      backend: options.backend ?? "gtts",
      lang: options.lang ?? "en",
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
 * @param options - ReadOptions containing filePath, backend, lang
 * @returns VoxResponse with download paths
 */
async function readFile(options: ReadOptions): Promise<VoxResponse> {
  const { filePath, backend = "gtts", lang = "en" } = options;

  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }

  const form = new FormData();
  const blob = new Blob([fs.readFileSync(filePath)]);
  form.append("file", blob, path.basename(filePath));
  form.append("backend", backend);
  form.append("lang", lang);

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
 * GET /health — check if the API server is running.
 *
 * @returns true if server is up
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
// CLI runner
// ------------------------------------------------------------------

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

function parseArgs(args: string[]): Record<string, string> {
  const result: Record<string, string> = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith("--") && args[i + 1]) {
      result[args[i].slice(2)] = args[++i];
    } else if (!result["_arg"]) {
      result["_arg"] = args[i];
    }
  }
  return result;
}

async function main(): Promise<void> {
  const [command, ...rest] = process.argv.slice(2);

  if (!command || command === "--help" || command === "-h") {
    printUsage();
    process.exit(0);
  }

  // health check
  if (command === "health") {
    const up = await checkHealth();
    if (up) {
      console.log("✓ voxread API is up at", BASE_URL);
    } else {
      console.error("✗ voxread API is not running. Start it with:");
      console.error("  python -m tts_reader.api");
      process.exit(1);
    }
    return;
  }

  const args = parseArgs(rest);
  const backend = (args["backend"] as Backend) ?? "gtts";
  const lang = args["lang"] ?? "en";

  if (command === "speak") {
    if (!args["_arg"]) {
      console.error('✗ Missing text. Usage: tsx index.ts speak "your text"');
      process.exit(1);
    }

    console.log("→ Synthesising...");
    try {
      const result = await speak({ text: args["_arg"], backend, lang });
      console.log(`✓ Done. ${result.words} words.`);
      console.log(`  Download: ${BASE_URL}${result.download}`);
    } catch (err) {
      console.error("✗ Error:", (err as Error).message);
      process.exit(1);
    }
    return;
  }

  if (command === "read") {
    if (!args["_arg"]) {
      console.error("✗ Missing file path. Usage: tsx index.ts read <file>");
      process.exit(1);
    }

    console.log(`→ Reading: ${args["_arg"]}`);
    try {
      const result = await readFile({
        filePath: args["_arg"],
        backend,
        lang,
      });
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