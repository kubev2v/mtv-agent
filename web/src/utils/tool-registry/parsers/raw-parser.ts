/**
 * Fallback parser for unrecognised tool output.
 * Wraps the text in a fenced code block for safe display.
 */
export function parseRaw(text: string): string {
  if (!text?.trim()) return text;
  return "```\n" + text.trimEnd() + "\n```";
}
