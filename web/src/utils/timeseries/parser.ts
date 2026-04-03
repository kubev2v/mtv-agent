import { parseMarkdownSections, parseTable } from "../table/parsers/index.js";
import type { TableData } from "../table/types.js";
import { extractSeries } from "./extract.js";
import type { TimeSeriesData } from "./types.js";

/** Parse a TSV (tab-separated values) string into a TableData. */
function parseTSV(text: string): TableData | null {
  const lines = text.trim().split("\n");
  if (lines.length < 2) return null;
  const headers = lines[0].split("\t");
  const rows = lines.slice(1).map((line) => line.split("\t"));
  return { headers, rows };
}

/**
 * Parse table text into time-series data suitable for Chart.js.
 *
 * Detects TSV (tab-delimited) first, then tries multi-section markdown
 * (heading + table pairs), then falls back to a single table.
 */
export function parseTimeSeriesTable(text: string): TimeSeriesData | null {
  if (!text?.trim()) return null;

  const firstLine = text.slice(0, text.indexOf("\n")).trim();
  if (firstLine.includes("\t") && /\bTIMESTAMP\b/i.test(firstLine)) {
    const table = parseTSV(text);
    if (table) {
      const series = extractSeries(table);
      if (series.length > 0) return { series };
    }
  }

  const sections = parseMarkdownSections(text);
  if (sections.length > 0) {
    const allSeries = sections.flatMap((s) => extractSeries(s.table, s.heading));
    if (allSeries.length > 0) return { series: allSeries };
  }

  const table = parseTable(text);
  if (!table) return null;

  const series = extractSeries(table);
  return series.length > 0 ? { series } : null;
}
