import { parseMarkdownSections, parseTable } from "../table/parsers/index.js";
import { extractSeries } from "./extract.js";
import type { TimeSeriesData } from "./types.js";

/**
 * Parse table text into time-series data suitable for Chart.js.
 *
 * Tries multi-section markdown first (heading + table pairs),
 * then falls back to a single table (markdown or fixed-width).
 */
export function parseTimeSeriesTable(text: string): TimeSeriesData | null {
  if (!text?.trim()) return null;

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
