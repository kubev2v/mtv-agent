/**
 * Time-series parser for query_range / preset results.
 *
 * For graph cards the raw result is passed directly to chart-card,
 * which handles its own parsing via the timeseries lib.
 * This parser simply returns the text as-is.
 */
export function parseTimeseries(text: string): string {
  return text;
}
