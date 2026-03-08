import type { ToolHandler } from "../types.js";
import { parseMarkdown } from "../parsers/markdown-parser.js";

const help: ToolHandler = {
  server: "user-kubectl-mtv",
  tool: "mtv_help",
  category: "help",
  renderer: "markdown",
  canPin: false,
  canPinGraph: false,

  match() {
    return true;
  },
  parse: parseMarkdown,
};

export const mtvHelpHandlers: ToolHandler[] = [help];
