import type { TableData } from "../table/types.js";
import type { TimeSeriesPoint } from "./types.js";

const SI_MULT: Record<string, number> = {
  k: 1e3,
  K: 1e3,
  M: 1e6,
  G: 1e9,
  T: 1e12,
};

/** Parse a numeric string that may carry an SI suffix (k, M, G, T). */
export function parseSINumber(s: string): number {
  const t = s.trim();
  if (!t) return NaN;
  const m = t.match(/^([+-]?\d+(?:\.\d+)?)\s*([kKMGT])?$/);
  if (!m) return NaN;
  return parseFloat(m[1]) * (m[2] ? (SI_MULT[m[2]] ?? 1) : 1);
}

/**
 * Extract time-series data from a TableData.
 * Expects a TIMESTAMP column (case-insensitive) and one or more value columns.
 */
export function extractSeries(
  table: TableData,
  nameOverride?: string,
): { name: string; data: TimeSeriesPoint[] }[] {
  const { headers, rows } = table;
  const tsIdx = headers.findIndex((h) => /^timestamp$/i.test(h));
  if (tsIdx < 0) return [];

  const valueCols = headers.map((name, idx) => ({ name, idx })).filter(({ idx }) => idx !== tsIdx);
  if (valueCols.length === 0) return [];

  const result: { name: string; data: TimeSeriesPoint[] }[] = [];

  for (const vc of valueCols) {
    const label = nameOverride ?? vc.name;
    const points: TimeSeriesPoint[] = [];

    for (const row of rows) {
      const tsRaw = row[tsIdx]?.trim();
      const valRaw = row[vc.idx]?.trim();
      if (!tsRaw || !valRaw) continue;

      let ts = Date.parse(tsRaw);
      if (isNaN(ts)) {
        const num = Number(tsRaw);
        if (!isNaN(num)) ts = num < 1e12 ? num * 1000 : num;
      }
      const val = parseSINumber(valRaw);
      if (isNaN(ts) || isNaN(val)) continue;
      points.push({ x: ts, y: val });
    }

    if (points.length > 0) {
      points.sort((a, b) => a.x - b.x);
      result.push({ name: label, data: points });
    }
  }

  return result;
}
