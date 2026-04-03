import { LitElement, html } from "lit";
import { customElement, state } from "lit/decorators.js";
import { appState } from "../../state/app-state.js";
import { fetchNamespaces } from "./fetch-namespaces.js";
import { namespacePickerStyles } from "./namespace-picker.styles.js";

const ALL_NS = "All Namespaces";

@customElement("namespace-picker")
export class NamespacePicker extends LitElement {
  static styles = namespacePickerStyles;

  @state() private open = false;
  @state() private namespaces: string[] = [];
  @state() private loading = false;
  @state() private search = "";
  @state() private selected = "";
  @state() private fetchError = false;
  @state() private errorMessage = "";

  private fetched = false;
  private unsubscribe?: () => void;

  connectedCallback() {
    super.connectedCallback();
    this.syncFromContext();
    this.unsubscribe = appState.subscribe(() => this.syncFromContext());
    document.addEventListener("click", this.onOutsideClick, true);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.unsubscribe?.();
    document.removeEventListener("click", this.onOutsideClick, true);
  }

  private syncFromContext() {
    const ctx = appState.state.context;
    if (ctx["all-namespaces"]) {
      this.selected = "";
    } else if (ctx["namespace"]) {
      this.selected = ctx["namespace"];
    } else {
      this.selected = "";
    }
  }

  private onOutsideClick = (e: MouseEvent) => {
    if (this.open && !e.composedPath().includes(this)) {
      this.open = false;
      this.search = "";
    }
  };

  private async toggleDropdown() {
    this.open = !this.open;
    if (this.open) {
      this.search = "";
      if (!this.fetched) await this.loadNamespaces();
    }
  }

  private async loadNamespaces() {
    this.loading = true;
    this.fetchError = false;
    this.errorMessage = "";
    try {
      this.namespaces = await fetchNamespaces();
      this.fetched = true;
    } catch (err) {
      console.error("Failed to load namespaces:", err);
      this.fetchError = true;
      this.errorMessage = err instanceof Error ? err.message : String(err);
    } finally {
      this.loading = false;
    }
  }

  private selectNamespace(ns: string) {
    this.selected = ns;
    this.open = false;
    this.search = "";

    if (ns === "") {
      appState.setContext("all-namespaces", "true");
      appState.removeContext("namespace");
    } else {
      appState.setContext("namespace", ns);
      appState.removeContext("all-namespaces");
    }
  }

  private onSearchInput(e: InputEvent) {
    this.search = (e.target as HTMLInputElement).value;
  }

  private get filtered(): string[] {
    const q = this.search.toLowerCase();
    if (!q) return this.namespaces;
    return this.namespaces.filter((ns) => ns.toLowerCase().includes(q));
  }

  render() {
    const label = this.selected || ALL_NS;

    return html`
      <button
        class="trigger"
        @click=${this.toggleDropdown}
        title="Select namespace"
        aria-label="Select namespace"
        aria-expanded=${this.open}
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <rect x="2" y="2" width="20" height="20" rx="2" />
          <line x1="2" y1="12" x2="22" y2="12" />
          <line x1="12" y1="2" x2="12" y2="22" />
        </svg>
        <span class="trigger-label">${label}</span>
        <svg
          class="caret ${this.open ? "open" : ""}"
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

      <div class="dropdown ${this.open ? "open" : ""}">
        ${this.open
          ? html`
              <input
                class="search-input"
                type="text"
                placeholder="Search namespaces…"
                .value=${this.search}
                @input=${this.onSearchInput}
              />
              ${this.renderList()}
            `
          : ""}
      </div>
    `;
  }

  private renderList() {
    if (this.loading) {
      return html`<div class="status">Loading…</div>`;
    }
    if (this.fetchError) {
      return html`<div class="status">
        Failed to load namespaces${this.errorMessage ? `: ${this.errorMessage}` : ""}
      </div>`;
    }

    const items = this.filtered;

    return html`
      <div class="ns-list">
        ${!this.search
          ? html`
              <button
                class="ns-item ${this.selected === "" ? "active" : ""}"
                @click=${() => this.selectNamespace("")}
              >
                ${ALL_NS}
                <span class="check">&#10003;</span>
              </button>
            `
          : ""}
        ${items.length
          ? items.map(
              (ns) => html`
                <button
                  class="ns-item ${ns === this.selected ? "active" : ""}"
                  @click=${() => this.selectNamespace(ns)}
                >
                  ${ns}
                  <span class="check">&#10003;</span>
                </button>
              `,
            )
          : html`<div class="status">No matches</div>`}
      </div>
    `;
  }
}
