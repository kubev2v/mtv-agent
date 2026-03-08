import { parseTable } from "./parsers/index.js";
import { normalizeTable } from "./normalize.js";
import { renderToMarkdown } from "./render.js";

/**
 * Full table pipeline: detect -> parse -> normalize -> render.
 * Returns the original text unchanged if no table is found.
 */
export function normalizeTableText(text: string): string {
  if (!text?.trim()) return text;

  const table = parseTable(text);
  if (!table) return text;

  return renderToMarkdown(normalizeTable(table));
}
