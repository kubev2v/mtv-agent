import type { TableData } from "../types.js";
import { parseMarkdownTable } from "./parse-markdown.js";
import { parseFixedWidthTable } from "./parse-fixed-width.js";
import { parseJsonTable } from "./parse-json.js";

export { parseMarkdownTable, parseMarkdownSections } from "./parse-markdown.js";
export { parseFixedWidthTable } from "./parse-fixed-width.js";
export { parseJsonTable } from "./parse-json.js";

/** Try all parsers in priority order: markdown, fixed-width, JSON fallback. */
export function parseTable(text: string): TableData | null {
  return parseMarkdownTable(text) ?? parseFixedWidthTable(text) ?? parseJsonTable(text);
}
