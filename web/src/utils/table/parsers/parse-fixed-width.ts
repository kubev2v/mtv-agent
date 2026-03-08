import type { TableData } from "../types.js";

/**
 * Find column start positions by looking for runs of >= 2 spaces in the
 * header line. Returns the character indices where each column begins.
 */
function columnStarts(header: string): number[] {
  const starts: number[] = [0];
  let spaces = 0;
  for (let i = 0; i < header.length; i++) {
    if (header[i] === " ") {
      spaces++;
    } else {
      if (spaces >= 2) starts.push(i);
      spaces = 0;
    }
  }
  return starts;
}

/** Parse a fixed-width (space-aligned) text table. */
export function parseFixedWidthTable(text: string): TableData | null {
  const lines = text.split("\n").filter((l) => l.trim());
  if (lines.length < 2) return null;

  const starts = columnStarts(lines[0]);
  if (starts.length < 2) return null;

  const extract = (line: string): string[] =>
    starts.map((s, i) => {
      const end = i < starts.length - 1 ? starts[i + 1] : line.length;
      return line.substring(s, end).trim();
    });

  return {
    headers: extract(lines[0]),
    rows: lines.slice(1).map((l) => extract(l)),
  };
}
