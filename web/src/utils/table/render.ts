import type { TableData } from "./types.js";

/** Render a TableData struct as a markdown pipe table. */
export function renderToMarkdown(table: TableData): string {
  const fmt = (cells: string[]) => "| " + cells.join(" | ") + " |";
  const separator = table.headers.map(() => "---");
  return [fmt(table.headers), fmt(separator), ...table.rows.map(fmt)].join("\n");
}
