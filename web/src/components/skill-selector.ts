import { LitElement, html } from "lit";
import { customElement, state } from "lit/decorators.js";
import { appState } from "../state/app-state.js";
import { chipListStyles } from "../styles/shared.js";

@customElement("skill-selector")
export class SkillSelector extends LitElement {
  static styles = chipListStyles;

  @state() private available: { name: string; description: string }[] = [];
  @state() private active: string[] = [];

  private unsubscribe?: () => void;

  connectedCallback() {
    super.connectedCallback();
    this.unsubscribe = appState.subscribe(() => {
      this.available = appState.state.availableSkills;
      this.active = appState.state.activeSkills;
    });
    this.available = appState.state.availableSkills;
    this.active = appState.state.activeSkills;
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.unsubscribe?.();
  }

  private toggle(name: string) {
    appState.toggleSkill(name);
  }

  render() {
    if (!this.available.length) {
      return html`<div class="empty">No skills loaded</div>`;
    }
    return html`
      <div class="chips">
        ${this.available.map((s) => {
          const isActive = this.active.includes(s.name);
          return html`
            <button
              class="chip ${isActive ? "active" : ""}"
              @click=${() => this.toggle(s.name)}
              title=${s.description}
            >
              ${isActive ? html`<span class="dot"></span>` : ""} ${s.name}
            </button>
          `;
        })}
      </div>
    `;
  }
}
