import type { ToolHandler } from "../types.js";
import { parseTable } from "../parsers/table-parser.js";
import { parseMarkdown } from "../parsers/markdown-parser.js";
import { parseLogs } from "../parsers/log-parser.js";

const TOOL = "debug_read";
const SERVER = "user-kubectl-debug-queries" as const;

function getCommand(args: Record<string, unknown>): string {
  return typeof args.command === "string" ? args.command.trim() : "";
}

const list: ToolHandler = {
  server: SERVER,
  tool: TOOL,
  category: "resource-list",
  renderer: "table",
  canPin: true,
  canPinGraph: false,

  match(args) {
    return getCommand(args) === "list";
  },
  parse: parseTable,
};

const get: ToolHandler = {
  server: SERVER,
  tool: TOOL,
  category: "resource-get",
  renderer: "markdown",
  canPin: true,
  canPinGraph: false,

  match(args) {
    return getCommand(args) === "get";
  },
  parse: parseMarkdown,
};

const logs: ToolHandler = {
  server: SERVER,
  tool: TOOL,
  category: "logs",
  renderer: "log",
  canPin: true,
  canPinGraph: false,

  match(args) {
    return getCommand(args) === "logs";
  },
  parse: parseLogs,
};

const events: ToolHandler = {
  server: SERVER,
  tool: TOOL,
  category: "events",
  renderer: "table",
  canPin: true,
  canPinGraph: false,

  match(args) {
    return getCommand(args) === "events";
  },
  parse: parseTable,
};

export const debugReadHandlers: ToolHandler[] = [list, get, logs, events];
