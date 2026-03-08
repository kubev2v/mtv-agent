export type ServerName =
  | "user-kubectl-mtv"
  | "user-kubectl-metrics"
  | "user-kubectl-debug-queries"
  | "unknown";

export type ToolCategory =
  | "resource-list"
  | "inventory-list"
  | "resource-get"
  | "resource-describe"
  | "health"
  | "settings"
  | "query"
  | "query-range"
  | "discover"
  | "logs"
  | "events"
  | "help"
  | "write"
  | "unknown";

export type RendererType = "table" | "graph" | "markdown" | "text" | "log" | "raw";

/** The display component used in the detail pane for a pinned card. */
export type CardDisplayType = "markdown" | "graph" | "text";

const RENDERER_TO_CARD: Record<RendererType, CardDisplayType> = {
  table: "markdown",
  graph: "graph",
  markdown: "markdown",
  text: "text",
  log: "text",
  raw: "text",
};

/** Map a handler's RendererType to the card display component type. */
export function cardDisplayType(renderer: RendererType): CardDisplayType {
  return RENDERER_TO_CARD[renderer];
}

export interface ToolIdentification {
  identified: boolean;
  server: ServerName;
  tool: string;
  command: string;
  category: ToolCategory;
  renderer: RendererType;
  outputFlag?: string;
  canPin: boolean;
  canPinGraph: boolean;
}

export interface ParsedResult {
  hasError: boolean;
  errorMessage?: string;
  content: string;
  displayType: CardDisplayType;
  raw: string;
}

export interface UnwrapResult {
  text: string;
  hasError: boolean;
  errorMessage?: string;
}

export interface ToolHandler {
  server: ServerName;
  tool: string;
  match(args: Record<string, unknown>): boolean;
  category: ToolCategory;
  renderer: RendererType;
  canPin: boolean;
  canPinGraph: boolean;
  parse(text: string): string;
}
