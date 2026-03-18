import type { ToolHandler } from "../types.js";
import { parseMarkdown } from "../parsers/markdown-parser.js";

const webFetch: ToolHandler = {
  server: "builtin",
  tool: "web_fetch",
  category: "web-fetch",
  renderer: "markdown",
  canPin: true,
  canPinGraph: false,

  match() {
    return true;
  },
  parse: parseMarkdown,
};

export const webFetchHandlers: ToolHandler[] = [webFetch];
