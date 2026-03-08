const STYLE_ID = "highlight-utils-style";

/**
 * Inject `<mark>` / `mark.active` styles into a shadow root (idempotent).
 * Call once per shadow root before applying highlights.
 */
export function injectHighlightStyles(root: ShadowRoot): void {
  if (root.getElementById(STYLE_ID)) return;
  const style = document.createElement("style");
  style.id = STYLE_ID;
  style.textContent = `
    mark[data-hl] {
      background: var(--accent-warning, #e8a817);
      color: inherit;
      border-radius: 2px;
      padding: 0;
    }
    mark[data-hl].active {
      background: var(--accent-primary, #2563eb);
      color: #fff;
    }
  `;
  root.appendChild(style);
}

/**
 * Walk every text node inside `container`, wrap case-insensitive matches
 * of `query` in `<mark data-hl>` elements.
 * Returns the total number of matches found.
 */
export function applyHighlights(container: HTMLElement, query: string): number {
  clearHighlights(container);
  if (!query) return 0;

  const lower = query.toLowerCase();
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
  const textNodes: Text[] = [];

  while (walker.nextNode()) {
    textNodes.push(walker.currentNode as Text);
  }

  let count = 0;

  for (const node of textNodes) {
    const text = node.nodeValue ?? "";
    const parts = splitByQuery(text, lower);
    if (parts.length <= 1) continue;

    const frag = document.createDocumentFragment();
    for (const part of parts) {
      if (part.match) {
        const mark = document.createElement("mark");
        mark.setAttribute("data-hl", "");
        mark.textContent = part.text;
        frag.appendChild(mark);
        count++;
      } else {
        frag.appendChild(document.createTextNode(part.text));
      }
    }
    node.parentNode!.replaceChild(frag, node);
  }

  return count;
}

/**
 * Remove all `<mark data-hl>` wrappers and restore plain text nodes.
 */
export function clearHighlights(container: HTMLElement): void {
  const marks = container.querySelectorAll("mark[data-hl]");
  for (const mark of marks) {
    const parent = mark.parentNode!;
    const text = document.createTextNode(mark.textContent ?? "");
    parent.replaceChild(text, mark);
    parent.normalize();
  }
}

/**
 * Set `.active` on the `index`-th `<mark data-hl>` inside `container`
 * and scroll it into view. Removes `.active` from all others.
 */
export function activateMatch(container: HTMLElement, index: number): void {
  const marks = container.querySelectorAll("mark[data-hl]");
  for (let i = 0; i < marks.length; i++) {
    const m = marks[i] as HTMLElement;
    if (i === index) {
      m.classList.add("active");
      m.scrollIntoView({ block: "nearest", behavior: "smooth" });
    } else {
      m.classList.remove("active");
    }
  }
}

/* ------------------------------------------------------------------ */

interface TextPart {
  text: string;
  match: boolean;
}

/** Split `text` into alternating non-match / match segments (case-insensitive). */
function splitByQuery(text: string, lowerQuery: string): TextPart[] {
  const parts: TextPart[] = [];
  const lowerText = text.toLowerCase();
  let cursor = 0;

  while (cursor < text.length) {
    const idx = lowerText.indexOf(lowerQuery, cursor);
    if (idx === -1) {
      parts.push({ text: text.slice(cursor), match: false });
      break;
    }
    if (idx > cursor) {
      parts.push({ text: text.slice(cursor, idx), match: false });
    }
    parts.push({ text: text.slice(idx, idx + lowerQuery.length), match: true });
    cursor = idx + lowerQuery.length;
  }

  return parts;
}
