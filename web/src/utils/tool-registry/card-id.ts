import { unwrapToolResult } from "./unwrap.js";
import { parseTimeSeriesTable } from "../timeseries/index.js";

/** Deterministic short id from tool name + args (djb2 hash). */
export function cardId(tool: string, args: Record<string, unknown>): string {
  const raw = tool + JSON.stringify(args);
  let h = 5381;
  for (let i = 0; i < raw.length; i++) h = ((h << 5) + h + raw.charCodeAt(i)) >>> 0;
  return `card-${h.toString(36)}`;
}

/**
 * Parse a metrics tool result into time-series data for Chart.js.
 * Unwraps the JSON envelope, then delegates to the timeseries table parser.
 */
export function parseTimeSeriesData(raw: string): ReturnType<typeof parseTimeSeriesTable> {
  const text = unwrapToolResult(raw).text;
  if (!text?.trim()) return null;
  return parseTimeSeriesTable(text);
}
