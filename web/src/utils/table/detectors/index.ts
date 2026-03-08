export { hasMarkdownTable, hasMarkdownHeading } from "./detect-markdown.js";
export { hasFixedWidthTable } from "./detect-fixed-width.js";
export { hasJsonContent } from "./detect-json.js";

import { hasMarkdownTable, hasMarkdownHeading } from "./detect-markdown.js";
import { hasFixedWidthTable } from "./detect-fixed-width.js";
import { hasJsonContent } from "./detect-json.js";

/** True when text contains any table or markdown heading worth pinning. */
export function hasTableContent(text: string): boolean {
  return (
    hasMarkdownTable(text) ||
    hasFixedWidthTable(text) ||
    hasMarkdownHeading(text) ||
    hasJsonContent(text)
  );
}
