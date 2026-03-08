import { LitElement, html, css } from "lit";
import { customElement, state } from "lit/decorators.js";
import { appState } from "../state/app-state.js";

@customElement("context-editor")
export class ContextEditor extends LitElement {
  static styles = css`
    :host {
      display: block;
    }

    .entries {
      display: flex;
      flex-direction: column;
      gap: 4px;
      margin-bottom: 8px;
    }

    .entry {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: var(--font-size-sm);
      padding: 4px 8px;
      border-radius: var(--radius-xs);
      background: var(--bg-tertiary);
    }

    .entry-key {
      font-weight: var(--font-weight-medium);
      color: var(--text-primary);
    }

    .entry-value {
      color: var(--text-secondary);
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .remove-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 20px;
      height: 20px;
      border: none;
      background: none;
      border-radius: var(--radius-xs);
      color: var(--text-tertiary);
      cursor: pointer;
      flex-shrink: 0;
      transition:
        color var(--transition-fast),
        background var(--transition-fast);
    }

    .remove-btn:hover {
      color: var(--accent-danger);
      background: var(--bg-hover);
    }

    .remove-btn svg {
      width: 12px;
      height: 12px;
    }

    .add-row {
      display: flex;
      gap: 6px;
    }

    .add-row input {
      flex: 1;
      padding: 6px 8px;
      border: 1px solid var(--border-primary);
      border-radius: var(--radius-xs);
      background: var(--bg-input);
      font-size: var(--font-size-sm);
      min-width: 0;
    }

    .add-row input::placeholder {
      color: var(--text-tertiary);
    }

    .add-btn {
      padding: 6px 10px;
      border: none;
      border-radius: var(--radius-xs);
      background: var(--bg-tertiary);
      color: var(--text-secondary);
      font-size: var(--font-size-sm);
      cursor: pointer;
      white-space: nowrap;
      transition:
        background var(--transition-fast),
        color var(--transition-fast);
    }

    .add-btn:hover {
      background: var(--bg-hover);
      color: var(--text-primary);
    }

    .empty {
      font-size: var(--font-size-sm);
      color: var(--text-tertiary);
      padding: 4px 0;
    }
  `;

  @state() private context: Record<string, string> = {};
  @state() private newKey = "";
  @state() private newValue = "";

  private unsubscribe?: () => void;

  connectedCallback() {
    super.connectedCallback();
    this.unsubscribe = appState.subscribe(() => {
      this.context = appState.state.context;
    });
    this.context = appState.state.context;
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.unsubscribe?.();
  }

  private removeKey(key: string) {
    appState.removeContext(key);
  }

  private add() {
    const key = this.newKey.trim();
    const value = this.newValue.trim();
    if (!key || !value) return;
    appState.setContext(key, value);
    this.newKey = "";
    this.newValue = "";
  }

  private onKeyDown(e: KeyboardEvent) {
    if (e.key === "Enter") this.add();
  }

  render() {
    const entries = Object.entries(this.context);

    return html`
      ${entries.length
        ? html`
            <div class="entries">
              ${entries.map(
                ([k, v]) => html`
                  <div class="entry">
                    <span class="entry-key">${k}</span>
                    <span class="entry-value">${v}</span>
                    <button
                      class="remove-btn"
                      @click=${() => this.removeKey(k)}
                      title="Remove ${k}"
                    >
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      >
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                      </svg>
                    </button>
                  </div>
                `,
              )}
            </div>
          `
        : html`<div class="empty">No context set</div>`}

      <div class="add-row">
        <input
          type="text"
          placeholder="key"
          .value=${this.newKey}
          @input=${(e: InputEvent) => (this.newKey = (e.target as HTMLInputElement).value)}
          @keydown=${this.onKeyDown}
        />
        <input
          type="text"
          placeholder="value"
          .value=${this.newValue}
          @input=${(e: InputEvent) => (this.newValue = (e.target as HTMLInputElement).value)}
          @keydown=${this.onKeyDown}
        />
        <button class="add-btn" @click=${this.add}>Add</button>
      </div>
    `;
  }
}
