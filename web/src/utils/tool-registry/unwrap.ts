import type { UnwrapResult } from "./types.js";

/**
 * Unwrap a JSON-encoded tool result envelope and detect errors.
 *
 * MCP tool results typically arrive as:
 *   { output: "...", return_value: 0, stderr?: "...", data?: ... }
 *
 * This function extracts the text payload and flags errors when
 * return_value !== 0, or when stderr is non-empty and no explicit
 * return_value is present (CLI tools often write info logs to stderr).
 */
export function unwrapToolResult(raw: string): UnwrapResult {
  if (!raw?.trim()) {
    return { text: "", hasError: true, errorMessage: "Empty tool result" };
  }

  try {
    const obj = JSON.parse(raw);
    if (!obj || typeof obj !== "object") {
      return { text: raw, hasError: false };
    }

    const returnValue = obj.return_value;
    const output = typeof obj.output === "string" ? obj.output : "";
    const stderr = typeof obj.stderr === "string" ? obj.stderr.trim() : "";

    if (typeof returnValue === "number" && returnValue !== 0) {
      const message = stderr || output || `Tool exited with code ${returnValue}`;
      return { text: output || stderr, hasError: true, errorMessage: message };
    }

    if (stderr && typeof returnValue !== "number") {
      return { text: output, hasError: true, errorMessage: stderr };
    }

    if (typeof obj.output === "string") {
      return { text: output, hasError: false };
    }

    return { text: raw, hasError: false };
  } catch {
    return { text: raw, hasError: false };
  }
}
