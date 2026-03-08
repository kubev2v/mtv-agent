import type { TableData } from "../types.js";

/**
 * Try to extract the first JSON object or array from the text.
 * Handles cases where JSON is preceded by plain-text (e.g. error preambles).
 */
function extractJson(text: string): unknown | null {
  const start = text.search(/[[{]/);
  if (start < 0) return null;

  const candidate = text.slice(start);
  try {
    return JSON.parse(candidate);
  } catch {
    return null;
  }
}

/** Flatten a value to a display string. */
function cellValue(v: unknown): string {
  if (v === null || v === undefined) return "";
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}

/**
 * Parse a JSON object or array of objects into a TableData.
 *
 * - Array of objects → headers = union of all keys, rows = values per object.
 * - Single object    → headers = keys, one row of values.
 * - Anything else    → null.
 */
export function parseJsonTable(text: string): TableData | null {
  const data = extractJson(text);
  if (data === null || typeof data !== "object") return null;

  const objects: Record<string, unknown>[] = [];

  if (Array.isArray(data)) {
    for (const item of data) {
      if (item !== null && typeof item === "object" && !Array.isArray(item)) {
        objects.push(item as Record<string, unknown>);
      }
    }
  } else {
    objects.push(data as Record<string, unknown>);
  }

  if (objects.length === 0) return null;

  const headerSet = new Set<string>();
  for (const obj of objects) {
    for (const key of Object.keys(obj)) headerSet.add(key);
  }
  const headers = [...headerSet];
  if (headers.length === 0) return null;

  const rows = objects.map((obj) => headers.map((h) => cellValue(obj[h])));

  return { headers, rows };
}
