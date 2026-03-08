import type { ToolHandler } from "../types.js";
import { parseTable } from "../parsers/table-parser.js";
import { parseTimeseries } from "../parsers/timeseries-parser.js";

const TOOL = "metrics_read";
const SERVER = "user-kubectl-metrics" as const;

function getCommand(args: Record<string, unknown>): string {
  return typeof args.command === "string" ? args.command.trim() : "";
}

const queryRange: ToolHandler = {
  server: SERVER,
  tool: TOOL,
  category: "query-range",
  renderer: "graph",
  canPin: true,
  canPinGraph: true,

  match(args) {
    const cmd = getCommand(args);
    return cmd === "query_range" || cmd === "preset";
  },
  parse: parseTimeseries,
};

const query: ToolHandler = {
  server: SERVER,
  tool: TOOL,
  category: "query",
  renderer: "table",
  canPin: true,
  canPinGraph: false,

  match(args) {
    return getCommand(args) === "query";
  },
  parse: parseTable,
};

const discover: ToolHandler = {
  server: SERVER,
  tool: TOOL,
  category: "discover",
  renderer: "table",
  canPin: true,
  canPinGraph: false,

  match(args) {
    const cmd = getCommand(args);
    return cmd === "discover" || cmd === "labels";
  },
  parse: parseTable,
};

export const metricsReadHandlers: ToolHandler[] = [queryRange, query, discover];
