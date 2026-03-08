import { LitElement, html, css, nothing } from "lit";
import { customElement, property, query } from "lit/decorators.js";

@customElement("card-search-bar")
export class CardSearchBar extends LitElement {
  static styles = css`
    :host {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      background: var(--bg-tertiary);
      border-top: 1px solid var(--border-secondary);
    }

    input {
      flex: 1;
      min-width: 0;
      padding: 3px 8px;
      border: 1px solid var(--border-secondary);
      border-radius: var(--radius-xs);
      background: var(--bg-input, var(--bg-primary));
      color: var(--text-primary);
      font-family: inherit;
      font-size: var(--font-size-xs);
      outline: none;
      transition: border-color var(--transition-fast);
    }

    input:focus {
      border-color: var(--accent-primary);
    }

    .count {
      font-size: var(--font-size-xs);
      color: var(--text-tertiary);
      white-space: nowrap;
      min-width: 40px;
      text-align: center;
      font-variant-numeric: tabular-nums;
    }

    .nav-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 20px;
      height: 20px;
      padding: 0;
      border: none;
      border-radius: var(--radius-xs);
      background: transparent;
      color: var(--text-tertiary);
      cursor: pointer;
      flex-shrink: 0;
      transition: all var(--transition-fast);
    }

    .nav-btn:hover {
      background: var(--bg-hover);
      color: var(--accent-primary);
    }

    .nav-btn:disabled {
      opacity: 0.3;
      cursor: default;
    }

    .nav-btn svg {
      width: 12px;
      height: 12px;
    }
  `;

  @property({ type: Number }) matchCount = 0;
  @property({ type: Number }) activeIndex = -1;

  @query("input") private input!: HTMLInputElement;

  protected firstUpdated() {
    this.input?.focus();
  }

  private onInput(ev: Event) {
    const value = (ev.target as HTMLInputElement).value;
    this.emit("search-input", value);
  }

  private onKeyDown(ev: KeyboardEvent) {
    if (ev.key === "Escape") {
      this.emit("search-close");
    } else if (ev.key === "Enter") {
      if (ev.shiftKey) this.emit("search-prev");
      else this.emit("search-next");
    }
  }

  private emit(name: string, detail?: string) {
    this.dispatchEvent(
      new CustomEvent(name, {
        detail,
        bubbles: true,
        composed: true,
      }),
    );
  }

  private get countLabel() {
    if (this.matchCount === 0) return nothing;
    return html`<span class="count">${this.activeIndex + 1} / ${this.matchCount}</span>`;
  }

  render() {
    const disabled = this.matchCount === 0;
    return html`
      <input
        type="text"
        placeholder="Search…"
        spellcheck="false"
        @input=${this.onInput}
        @keydown=${this.onKeyDown}
      />
      ${this.countLabel}
      <button
        class="nav-btn"
        title="Previous (Shift+Enter)"
        ?disabled=${disabled}
        @click=${() => this.emit("search-prev")}
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="18 15 12 9 6 15" />
        </svg>
      </button>
      <button
        class="nav-btn"
        title="Next (Enter)"
        ?disabled=${disabled}
        @click=${() => this.emit("search-next")}
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>
    `;
  }
}
