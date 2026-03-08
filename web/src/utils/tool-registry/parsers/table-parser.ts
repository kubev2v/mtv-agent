import { normalizeTableText } from "../../table/index.js";

/**
 * Parse tabular tool output into normalized markdown tables.
 * Delegates to the existing table pipeline (detect -> parse -> normalize -> render).
 * Returns the original text unchanged when no table structure is found.
 */
export function parseTable(text: string): string {
  if (!text?.trim()) return text;
  return normalizeTableText(text);
}
