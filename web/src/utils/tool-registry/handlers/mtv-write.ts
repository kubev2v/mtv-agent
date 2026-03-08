import type { ToolHandler } from "../types.js";
import { parseMarkdown } from "../parsers/markdown-parser.js";

const write: ToolHandler = {
  server: "user-kubectl-mtv",
  tool: "mtv_write",
  category: "write",
  renderer: "markdown",
  canPin: false,
  canPinGraph: false,

  match() {
    return true;
  },
  parse: parseMarkdown,
};

export const mtvWriteHandlers: ToolHandler[] = [write];
