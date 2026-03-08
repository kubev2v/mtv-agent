import { LitElement, html, css } from "lit";
import { customElement } from "lit/decorators.js";

@customElement("thinking-indicator")
export class ThinkingIndicator extends LitElement {
  static styles = css`
    :host {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 12px 0;
    }

    .dots {
      display: flex;
      gap: 4px;
    }

    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent-primary);
      opacity: 0.3;
      animation: pulse 1.4s ease-in-out infinite;
    }

    .dot:nth-child(2) {
      animation-delay: 0.2s;
    }

    .dot:nth-child(3) {
      animation-delay: 0.4s;
    }

    @keyframes pulse {
      0%,
      80%,
      100% {
        opacity: 0.3;
        transform: scale(0.8);
      }
      40% {
        opacity: 1;
        transform: scale(1);
      }
    }

    .label {
      font-size: var(--font-size-sm);
      color: var(--text-tertiary);
    }
  `;

  render() {
    return html`
      <div class="dots">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </div>
      <span class="label">Thinking...</span>
    `;
  }
}
