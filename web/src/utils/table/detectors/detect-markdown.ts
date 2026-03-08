/** True when text contains a markdown pipe table (rows + separator). */
export function hasMarkdownTable(text: string): boolean {
  if (!text || text.length < 5) return false;
  const lines = text.split("\n");
  return (
    lines.some((l) => /^\|.*\|.*\|/.test(l.trim())) &&
    lines.some((l) => /^\|[\s\-:|]+\|/.test(l.trim()))
  );
}

/** True when text contains a markdown heading (`#` through `####`). */
export function hasMarkdownHeading(text: string): boolean {
  if (!text) return false;
  return text.split("\n").some((l) => /^#{1,4}\s/.test(l.trim()));
}
