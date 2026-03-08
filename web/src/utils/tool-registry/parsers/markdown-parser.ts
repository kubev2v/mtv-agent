/**
 * Pass-through parser for content that is already markdown-friendly.
 * Used for describe, health, help, and write results.
 */
export function parseMarkdown(text: string): string {
  return text;
}
