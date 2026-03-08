/** True when text looks like a JSON object or array. */
export function hasJsonContent(text: string): boolean {
  if (!text) return false;
  const start = text.search(/[[{]/);
  if (start < 0) return false;
  const ch = text[start];
  const end = ch === "[" ? "]" : "}";
  return text.lastIndexOf(end) > start;
}
