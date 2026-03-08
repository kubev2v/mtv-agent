import type { TableData } from "./types.js";

const TRUTHY = new Set(["true", "yes"]);
const FALSY = new Set(["false", "no"]);

/** Normalize a single cell value: booleans and numbers get canonical forms. */
export function normalizeCell(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) return trimmed;

  const lower = trimmed.toLowerCase();
  if (TRUTHY.has(lower)) return "true";
  if (FALSY.has(lower)) return "false";

  if (/^[+-]?\d+(\.\d+)?$/.test(trimmed)) {
    const n = parseFloat(trimmed);
    if (!isNaN(n)) return String(n);
  }

  return trimmed;
}

/** Normalize all row cells in a table (headers are left as-is). */
export function normalizeTable(table: TableData): TableData {
  return {
    headers: table.headers,
    rows: table.rows.map((row) => row.map(normalizeCell)),
  };
}
