import type { ToolHandler } from "../types.js";
import { parseMarkdown } from "../parsers/markdown-parser.js";

const help: ToolHandler = {
  server: "user-kubectl-metrics",
  tool: "metrics_help",
  category: "help",
  renderer: "markdown",
  canPin: false,
  canPinGraph: false,

  match() {
    return true;
  },
  parse: parseMarkdown,
};

export const metricsHelpHandlers: ToolHandler[] = [help];
