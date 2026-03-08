import { LitElement, html, css } from "lit";
import { customElement } from "lit/decorators.js";

/**
 * A reusable vertical drag divider that emits resize events.
 *
 * Events:
 *   "handle-resize" – fires continuously during drag with { delta: number }
 *                     (positive = cursor moved right, negative = moved left).
 *   "resize-end"   – fires once when the drag finishes.
 */
@customElement("resize-handle")
export class ResizeHandle extends LitElement {
  static styles = css`
    :host {
      display: block;
      width: 4px;
      min-width: 4px;
      cursor: col-resize;
      background: var(--border-secondary);
      transition: background var(--transition-fast);
      position: relative;
      z-index: 2;
    }

    :host(:hover),
    :host([active]) {
      background: var(--accent-primary);
    }

    .overlay {
      display: none;
      position: fixed;
      inset: 0;
      z-index: 9999;
      cursor: col-resize;
    }

    :host([active]) .overlay {
      display: block;
    }
  `;

  private startX = 0;

  private emitResize(delta: number) {
    this.dispatchEvent(
      new CustomEvent("handle-resize", {
        detail: { delta },
        bubbles: true,
        composed: true,
      }),
    );
  }

  private emitResizeEnd() {
    this.dispatchEvent(new CustomEvent("resize-end", { bubbles: true, composed: true }));
  }

  private onMouseDown = (e: MouseEvent) => {
    e.preventDefault();
    this.startX = e.clientX;
    this.setAttribute("active", "");
    document.addEventListener("mousemove", this.onMouseMove);
    document.addEventListener("mouseup", this.onMouseUp);
  };

  private onMouseMove = (e: MouseEvent) => {
    this.emitResize(e.clientX - this.startX);
  };

  private onMouseUp = () => {
    this.removeAttribute("active");
    document.removeEventListener("mousemove", this.onMouseMove);
    document.removeEventListener("mouseup", this.onMouseUp);
    this.emitResizeEnd();
  };

  render() {
    return html`<div class="overlay"></div>`;
  }

  connectedCallback() {
    super.connectedCallback();
    this.addEventListener("mousedown", this.onMouseDown);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.removeEventListener("mousedown", this.onMouseDown);
    document.removeEventListener("mousemove", this.onMouseMove);
    document.removeEventListener("mouseup", this.onMouseUp);
  }
}
