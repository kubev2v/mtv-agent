import type { ToolHandler } from "../types.js";
import { parseTable } from "../parsers/table-parser.js";
import { parseMarkdown } from "../parsers/markdown-parser.js";

const TOOL = "mtv_read";
const SERVER = "user-kubectl-mtv" as const;

const RESOURCE_LIST_PREFIXES = ["get plan", "get provider", "get hook", "get host", "get mapping"];

function getCommand(args: Record<string, unknown>): string {
  return typeof args.command === "string" ? args.command.trim() : "";
}

const resourceList: ToolHandler = {
  server: SERVER,
  tool: TOOL,
  category: "resource-list",
  renderer: "table",
  canPin: true,
  canPinGraph: false,

  match(args) {
    const cmd = getCommand(args);
    return RESOURCE_LIST_PREFIXES.some((p) => cmd === p || cmd.startsWith(p + " "));
  },
  parse: parseTable,
};

const inventoryList: ToolHandler = {
  server: SERVER,
  tool: TOOL,
  category: "inventory-list",
  renderer: "table",
  canPin: true,
  canPinGraph: false,

  match(args) {
    return getCommand(args).startsWith("get inventory");
  },
  parse: parseTable,
};

const resourceDescribe: ToolHandler = {
  server: SERVER,
  tool: TOOL,
  category: "resource-describe",
  renderer: "markdown",
  canPin: true,
  canPinGraph: false,

  match(args) {
    return getCommand(args).startsWith("describe");
  },
  parse: parseMarkdown,
};

const health: ToolHandler = {
  server: SERVER,
  tool: TOOL,
  category: "health",
  renderer: "text",
  canPin: true,
  canPinGraph: false,

  match(args) {
    return getCommand(args) === "health";
  },
  parse: parseMarkdown,
};

const settings: ToolHandler = {
  server: SERVER,
  tool: TOOL,
  category: "settings",
  renderer: "table",
  canPin: true,
  canPinGraph: false,

  match(args) {
    const cmd = getCommand(args);
    return cmd === "settings" || cmd === "settings get";
  },
  parse: parseTable,
};

export const mtvReadHandlers: ToolHandler[] = [
  inventoryList,
  resourceDescribe,
  health,
  settings,
  resourceList,
];
