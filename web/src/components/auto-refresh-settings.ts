import { LitElement, html, css } from "lit";
import { customElement, state } from "lit/decorators.js";
import { autoRefreshManager } from "../state/auto-refresh-state.js";

@customElement("auto-refresh-settings")
export class AutoRefreshSettings extends LitElement {
  static styles = css`
    :host {
      display: block;
    }

    .row {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: var(--font-size-sm);
    }

    label {
      color: var(--text-secondary);
      white-space: nowrap;
    }

    .interval-input {
      width: 64px;
      padding: 4px 8px;
      border: 1px solid var(--border-primary);
      border-radius: var(--radius-xs);
      background: var(--bg-input);
      color: var(--text-primary);
      font-size: var(--font-size-sm);
      text-align: center;
    }

    .unit {
      color: var(--text-tertiary);
      font-size: var(--font-size-xs);
    }

    .hint {
      margin-top: 6px;
      font-size: var(--font-size-xs);
      color: var(--text-tertiary);
      line-height: 1.4;
    }
  `;

  @state() private intervalSec = autoRefreshManager.intervalSec;

  private unsubscribe?: () => void;

  connectedCallback() {
    super.connectedCallback();
    this.unsubscribe = autoRefreshManager.subscribe(() => {
      this.intervalSec = autoRefreshManager.intervalSec;
    });
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.unsubscribe?.();
  }

  private onIntervalChange(e: Event) {
    const value = Number((e.target as HTMLInputElement).value);
    if (!Number.isNaN(value) && value > 0) {
      autoRefreshManager.setInterval(value);
    }
  }

  render() {
    return html`
      <div class="row">
        <label for="interval-input">Refresh every</label>
        <input
          id="interval-input"
          class="interval-input"
          type="number"
          min="5"
          max="3600"
          aria-describedby="interval-hint"
          .value=${String(this.intervalSec)}
          @change=${this.onIntervalChange}
        />
        <span class="unit">sec</span>
      </div>
      <div class="hint" id="interval-hint">
        Use the timer button on each card to enable auto-refresh.
      </div>
    `;
  }
}
