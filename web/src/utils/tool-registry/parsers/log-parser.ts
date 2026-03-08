/**
 * Format container log output for display.
 * Wraps the text in a fenced code block so the markdown renderer
 * displays it with monospace font and preserves whitespace.
 */
export function parseLogs(text: string): string {
  if (!text?.trim()) return text;
  return "```\n" + text.trimEnd() + "\n```";
}
