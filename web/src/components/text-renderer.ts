import { LitElement, html, css } from "lit";
import { customElement, property } from "lit/decorators.js";

/**
 * Renders preformatted plain text in a styled monospace block.
 * Used for structured CLI output (health reports, etc.) where
 * whitespace alignment must be preserved exactly.
 */
@customElement("text-renderer")
export class TextRenderer extends LitElement {
  static styles = css`
    :host {
      display: block;
      color: var(--text-primary);
    }

    .text {
      font-family: var(--font-mono);
      font-size: var(--font-size-xs);
      line-height: 1.5;
      white-space: pre;
      overflow-x: auto;
      padding: 4px 0;
      margin: 0;
    }
  `;

  @property({ type: String }) content = "";

  render() {
    return html`<pre class="text">${this.content}</pre>`;
  }
}
