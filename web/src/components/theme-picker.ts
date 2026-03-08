import { LitElement, html, css } from "lit";
import { customElement, state } from "lit/decorators.js";
import { themeManager } from "../styles/themes.js";

@customElement("theme-picker")
export class ThemePicker extends LitElement {
  static styles = css`
    :host {
      display: inline-flex;
      position: relative;
    }

    button.trigger {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 36px;
      height: 36px;
      border-radius: var(--radius-sm);
      background: transparent;
      color: var(--text-secondary);
      border: none;
      cursor: pointer;
      transition:
        background var(--transition-fast),
        color var(--transition-fast);
    }

    button.trigger:hover {
      background: var(--bg-hover);
      color: var(--text-primary);
    }

    svg {
      width: 18px;
      height: 18px;
    }

    .dropdown {
      position: absolute;
      top: 100%;
      right: 0;
      margin-top: 4px;
      min-width: 160px;
      background: var(--bg-input);
      border: 1px solid var(--border-primary);
      border-radius: var(--radius-sm);
      box-shadow: var(--shadow-md);
      z-index: 200;
      padding: 4px;
      opacity: 0;
      transform: translateY(-4px);
      pointer-events: none;
      transition:
        opacity var(--transition-fast),
        transform var(--transition-fast);
    }

    .dropdown.open {
      opacity: 1;
      transform: translateY(0);
      pointer-events: auto;
    }

    .dropdown button {
      display: flex;
      align-items: center;
      gap: 8px;
      width: 100%;
      padding: 8px 10px;
      border: none;
      border-radius: var(--radius-xs);
      background: transparent;
      color: var(--text-primary);
      font-size: var(--font-size-sm);
      font-family: var(--font-sans);
      cursor: pointer;
      transition: background var(--transition-fast);
    }

    .dropdown button:hover {
      background: var(--bg-hover);
    }

    .dropdown button.active {
      background: var(--bg-tertiary);
      font-weight: var(--font-weight-medium);
    }

    .swatch {
      width: 14px;
      height: 14px;
      border-radius: var(--radius-xs);
      border: 1px solid var(--border-primary);
      flex-shrink: 0;
    }

    .check {
      margin-left: auto;
      font-size: 13px;
      opacity: 0;
    }

    .active .check {
      opacity: 1;
    }
  `;

  @state() private open = false;
  @state() private currentTheme = themeManager.name;

  private outsideClickHandler = (e: MouseEvent) => {
    if (!this.open) return;
    if (!e.composedPath().includes(this)) {
      this.open = false;
    }
  };

  connectedCallback() {
    super.connectedCallback();
    document.addEventListener("click", this.outsideClickHandler, true);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    document.removeEventListener("click", this.outsideClickHandler, true);
  }

  private toggleDropdown() {
    this.open = !this.open;
  }

  private selectTheme(id: string) {
    themeManager.setTheme(id);
    this.currentTheme = themeManager.name;
    this.open = false;
    this.dispatchEvent(
      new CustomEvent("theme-changed", {
        detail: { theme: themeManager.name },
        bubbles: true,
        composed: true,
      }),
    );
  }

  private swatchColors: Record<string, [string, string]> = {
    light: ["#FAF9F5", "#AE5630"],
    dark: ["#1A1918", "#D4703C"],
    "rh-light": ["#ffffff", "#a60000"],
    "rh-dark": ["#151515", "#f56e6e"],
  };

  render() {
    const isDark = themeManager.isDark;
    const themes = themeManager.themes;

    return html`
      <button
        class="trigger"
        @click=${this.toggleDropdown}
        title="Change theme"
        aria-label="Change theme"
        aria-expanded=${this.open}
      >
        ${isDark
          ? html`<svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="12" cy="12" r="5" />
              <line x1="12" y1="1" x2="12" y2="3" />
              <line x1="12" y1="21" x2="12" y2="23" />
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
              <line x1="1" y1="12" x2="3" y2="12" />
              <line x1="21" y1="12" x2="23" y2="12" />
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
            </svg>`
          : html`<svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>`}
      </button>

      <div class="dropdown ${this.open ? "open" : ""}">
        ${themes.map(
          (t) => html`
            <button
              class=${t.id === this.currentTheme ? "active" : ""}
              @click=${() => this.selectTheme(t.id)}
            >
              <span
                class="swatch"
                style="background: linear-gradient(135deg, ${this.swatchColors[t.id]?.[0] ??
                "#888"} 50%, ${this.swatchColors[t.id]?.[1] ?? "#444"} 50%)"
              ></span>
              ${t.label}
              <span class="check">&#10003;</span>
            </button>
          `,
        )}
      </div>
    `;
  }
}
