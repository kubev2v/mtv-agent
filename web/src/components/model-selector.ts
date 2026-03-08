import { LitElement, html, css } from "lit";
import { customElement, state } from "lit/decorators.js";
import { appState } from "../state/app-state.js";
import { switchModel } from "../services/api-client.js";

@customElement("model-selector")
export class ModelSelector extends LitElement {
  static styles = css`
    :host {
      display: block;
    }

    select {
      width: 100%;
      padding: 8px 10px;
      border: 1px solid var(--border-primary);
      border-radius: var(--radius-sm);
      background: var(--bg-input);
      color: var(--text-primary);
      font-size: var(--font-size-sm);
      cursor: pointer;
      appearance: auto;
    }

    select:focus {
      outline: 2px solid var(--accent-primary);
      outline-offset: -1px;
    }

    .empty {
      font-size: var(--font-size-sm);
      color: var(--text-tertiary);
      padding: 4px 0;
    }
  `;

  @state() private models: string[] = [];
  @state() private current = "";

  private unsubscribe?: () => void;

  connectedCallback() {
    super.connectedCallback();
    this.unsubscribe = appState.subscribe(() => {
      this.models = appState.state.availableModels;
      this.current = appState.state.model;
    });
    this.models = appState.state.availableModels;
    this.current = appState.state.model;
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.unsubscribe?.();
  }

  private async onChange(e: Event) {
    const select = e.target as HTMLSelectElement;
    const name = select.value;
    if (!name || name === this.current) return;
    try {
      const result = await switchModel(name);
      appState.update({
        model: result.model,
        contextWindow: result.context_window,
      });
    } catch (err) {
      appState.update({ error: (err as Error).message });
    }
  }

  render() {
    if (!this.models.length) {
      return html`<div class="empty">No models available</div>`;
    }
    return html`
      <select .value=${this.current} @change=${this.onChange}>
        ${this.models.map(
          (m) => html`<option value=${m} ?selected=${m === this.current}>${m}</option>`,
        )}
      </select>
    `;
  }
}
