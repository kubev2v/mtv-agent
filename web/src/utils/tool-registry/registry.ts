import type { ToolIdentification, ParsedResult, ToolHandler, CardDisplayType } from "./types.js";
import { cardDisplayType } from "./types.js";
import { allHandlers } from "./handlers/index.js";
import { unwrapToolResult } from "./unwrap.js";
import { parseRaw } from "./parsers/raw-parser.js";

const STRUCTURED_FLAGS = new Set(["json", "yaml"]);

/** Wrap text in a fenced code block with the given language tag. */
function fenceCode(text: string, lang: string): string {
  return "```" + lang + "\n" + text.trimEnd() + "\n```";
}

/**
 * Build a lookup map keyed by tool name for O(1) first-pass filtering.
 * Each tool name maps to the ordered list of handlers that belong to it.
 */
const handlersByTool = new Map<string, ToolHandler[]>();
for (const h of allHandlers) {
  const list = handlersByTool.get(h.tool) ?? [];
  list.push(h);
  handlersByTool.set(h.tool, list);
}

function extractOutputFlag(args: Record<string, unknown>): string | undefined {
  const flags = args.flags;
  if (flags && typeof flags === "object" && !Array.isArray(flags)) {
    const output = (flags as Record<string, unknown>).output;
    if (typeof output === "string") return output;
  }
  if (typeof args.output === "string") return args.output;
  return undefined;
}

function extractCommand(args: Record<string, unknown>): string {
  return typeof args.command === "string" ? args.command.trim() : "";
}

/**
 * Identify a tool call by matching it against all known handlers.
 *
 * Returns a ToolIdentification with `identified: true` when a handler
 * matches, or a fallback identification with `identified: false`.
 */
export function identify(toolName: string, args: Record<string, unknown>): ToolIdentification {
  const candidates = handlersByTool.get(toolName);
  if (candidates) {
    for (const h of candidates) {
      if (h.match(args)) {
        return {
          identified: true,
          server: h.server,
          tool: h.tool,
          command: extractCommand(args),
          category: h.category,
          renderer: h.renderer,
          outputFlag: extractOutputFlag(args),
          canPin: h.canPin,
          canPinGraph: h.canPinGraph,
        };
      }
    }
  }

  return {
    identified: false,
    server: "unknown",
    tool: toolName,
    command: extractCommand(args),
    category: "unknown",
    renderer: "raw",
    outputFlag: extractOutputFlag(args),
    canPin: false,
    canPinGraph: false,
  };
}

/**
 * Find the handler that produced a given identification.
 * Returns undefined for unidentified tool calls.
 */
function findHandler(id: ToolIdentification): ToolHandler | undefined {
  if (!id.identified) return undefined;
  const candidates = handlersByTool.get(id.tool);
  return candidates?.find((h) => h.category === id.category);
}

/**
 * Parse a raw tool result using the identification from `identify()`.
 *
 * Steps:
 *  1. Unwrap the JSON envelope and detect errors.
 *  2. If outputFlag requests a structured format (json/yaml), wrap the
 *     text in a fenced code block and use the markdown renderer for
 *     syntax highlighting.
 *  3. Otherwise delegate to the matching handler's parser and resolve
 *     the display type from the handler's renderer.
 */
export function parseResult(id: ToolIdentification, raw: string): ParsedResult {
  const unwrapped = unwrapToolResult(raw);
  const fallbackDisplay: CardDisplayType = "text";

  if (unwrapped.hasError) {
    return {
      hasError: true,
      errorMessage: unwrapped.errorMessage,
      content: unwrapped.text || unwrapped.errorMessage || raw,
      displayType: fallbackDisplay,
      raw,
    };
  }

  const handler = findHandler(id);
  const text = unwrapped.text;
  const flag = id.outputFlag?.toLowerCase();

  if (flag && STRUCTURED_FLAGS.has(flag)) {
    return {
      hasError: false,
      content: fenceCode(text, flag),
      displayType: "markdown",
      raw,
    };
  }

  if (flag === "markdown") {
    const content = handler ? handler.parse(text) : text;
    return { hasError: false, content, displayType: "markdown", raw };
  }

  const content = handler ? handler.parse(text) : parseRaw(text);
  const displayType = handler ? cardDisplayType(handler.renderer) : fallbackDisplay;

  return { hasError: false, content, displayType, raw };
}
