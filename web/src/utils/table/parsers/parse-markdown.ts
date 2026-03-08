import { marked, type Tokens } from "marked";
import type { TableData, TableSection } from "../types.js";

/** Parse the first markdown pipe table found in text. */
export function parseMarkdownTable(text: string): TableData | null {
  const tokens = marked.lexer(text);
  for (const token of tokens) {
    if (token.type === "table") {
      const t = token as Tokens.Table;
      return {
        headers: t.header.map((c) => c.text),
        rows: t.rows.map((r) => r.map((c) => c.text)),
      };
    }
  }
  return null;
}

function cleanHeading(text: string): string {
  return text
    .replace(/^-+\s*/, "")
    .replace(/\s*-+$/, "")
    .trim();
}

/**
 * Walk marked tokens and group each heading with the table that follows it.
 * Useful for multi-section markdown (e.g. "# Series A" then a pipe table).
 */
export function parseMarkdownSections(text: string): TableSection[] {
  const tokens = marked.lexer(text);
  const sections: TableSection[] = [];
  let pendingHeading: string | undefined;

  for (const token of tokens) {
    if (token.type === "heading") {
      pendingHeading = cleanHeading((token as Tokens.Heading).text);
    } else if (token.type === "table") {
      const t = token as Tokens.Table;
      sections.push({
        heading: pendingHeading,
        table: {
          headers: t.header.map((c) => c.text),
          rows: t.rows.map((r) => r.map((c) => c.text)),
        },
      });
      pendingHeading = undefined;
    } else if (token.type !== "space") {
      pendingHeading = undefined;
    }
  }

  return sections;
}
