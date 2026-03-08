import { LitElement, html, css, nothing } from "lit";
import { customElement, state, query } from "lit/decorators.js";
import { repeat } from "lit/directives/repeat.js";
import { appState, type ChatMessage } from "../state/app-state.js";
import type { PlaybookInfo } from "../services/api-client.js";

const CATEGORY_ICONS: Record<string, string> = {
  Health: "monitor_heart",
  Migration: "swap_horiz",
  Setup: "build",
};

function humanize(kebab: string): string {
  return kebab
    .split("-")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

@customElement("agent-chat")
export class AgentChat extends LitElement {
  static styles = css`
    :host {
      display: flex;
      flex-direction: column;
      height: 100%;
      overflow: hidden;
    }

    .messages-scroll {
      flex: 1;
      overflow-y: auto;
      overflow-x: hidden;
      padding: 60px 24px 12px;
      scroll-behavior: smooth;
      scrollbar-width: thin;
      scrollbar-color: var(--border-primary) transparent;
    }

    .messages-scroll::-webkit-scrollbar {
      width: 6px;
    }

    .messages-scroll::-webkit-scrollbar-track {
      background: transparent;
    }

    .messages-scroll::-webkit-scrollbar-thumb {
      background: var(--border-primary);
      border-radius: 3px;
    }

    .messages {
      max-width: var(--chat-max-width);
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .empty-state {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      overflow-y: auto;
      padding: 24px;
      scrollbar-width: thin;
      scrollbar-color: var(--border-primary) transparent;
    }

    .empty-state.compact {
      flex: none;
      justify-content: flex-end;
      min-height: 180px;
    }

    .empty-header {
      text-align: center;
      margin-bottom: 32px;
    }

    .empty-icon {
      font-family: "Material Symbols Outlined";
      font-weight: normal;
      font-style: normal;
      font-size: 48px;
      line-height: 1;
      letter-spacing: normal;
      text-transform: none;
      white-space: nowrap;
      direction: ltr;
      font-feature-settings: "liga";
      -webkit-font-smoothing: antialiased;
      opacity: 0.4;
      color: var(--text-tertiary);
    }

    .empty-title {
      font-size: var(--font-size-lg);
      font-weight: var(--font-weight-medium);
      color: var(--text-secondary);
      margin-top: 12px;
    }

    .empty-hint {
      font-size: var(--font-size-sm);
      color: var(--text-tertiary);
      margin-top: 4px;
    }

    .playbook-section {
      width: 100%;
      max-width: var(--chat-max-width);
      margin-bottom: 24px;
    }

    .playbook-category {
      font-size: var(--font-size-xs, 11px);
      font-weight: var(--font-weight-semibold, 600);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-tertiary);
      margin-bottom: 8px;
      padding-left: 4px;
    }

    .playbook-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 10px;
    }

    .playbook-card {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 14px 16px;
      border-radius: var(--radius-lg, 12px);
      border: 1px solid var(--border-primary);
      background: var(--bg-secondary);
      cursor: pointer;
      transition:
        border-color var(--transition-fast),
        box-shadow var(--transition-fast);
    }

    .playbook-card:hover {
      border-color: var(--accent-primary);
      box-shadow: 0 0 0 1px var(--accent-primary);
    }

    .card-icon {
      font-family: "Material Symbols Outlined";
      font-weight: normal;
      font-style: normal;
      font-size: 22px;
      line-height: 1;
      letter-spacing: normal;
      text-transform: none;
      white-space: nowrap;
      direction: ltr;
      font-feature-settings: "liga";
      -webkit-font-smoothing: antialiased;
      color: var(--accent-primary);
      flex-shrink: 0;
      margin-top: 1px;
    }

    .card-text {
      display: flex;
      flex-direction: column;
      gap: 2px;
      min-width: 0;
    }

    .card-name {
      font-size: var(--font-size-sm);
      font-weight: var(--font-weight-medium);
      color: var(--text-primary);
    }

    .card-desc {
      font-size: var(--font-size-xs, 11px);
      color: var(--text-tertiary);
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .composer-area {
      padding: 8px 24px 24px;
    }

    .composer-inner {
      max-width: var(--chat-max-width);
      margin: 0 auto;
    }

    .playbook-panel {
      max-width: var(--chat-max-width);
      margin: 0 auto;
      overflow: hidden;
      max-height: 0;
      opacity: 0;
      transition:
        max-height 0.3s ease,
        opacity 0.25s ease,
        padding 0.3s ease;
      padding: 0;
    }

    .playbook-panel.open {
      max-height: min(2000px, 60vh);
      opacity: 1;
      padding: 12px 0 0;
      overflow-y: auto;
      scrollbar-width: thin;
      scrollbar-color: var(--border-primary) transparent;
    }
  `;

  @state() private messages: ChatMessage[] = [];
  @state() private playbooks: PlaybookInfo[] = [];
  @state() private showPlaybooks = false;
  @query(".messages-scroll") private scrollContainer!: HTMLElement;

  private unsubscribe?: () => void;

  private hasUserToggledPlaybooks = false;

  connectedCallback() {
    super.connectedCallback();
    this.unsubscribe = appState.subscribe(() => {
      const prev = this.messages;
      this.messages = appState.state.messages;
      this.playbooks = appState.state.availablePlaybooks;
      if (prev.length > 0 && this.messages.length === 0) {
        this.hasUserToggledPlaybooks = false;
      }
      if (!this.hasUserToggledPlaybooks) {
        this.showPlaybooks = this.messages.length === 0;
      }
      if (this.messages !== prev) {
        this.scrollToBottom();
      }
    });
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.unsubscribe?.();
  }

  private scrollToBottom() {
    requestAnimationFrame(() => {
      if (this.scrollContainer) {
        this.scrollContainer.scrollTop = this.scrollContainer.scrollHeight;
      }
    });
  }

  private onTogglePlaybooks() {
    this.hasUserToggledPlaybooks = true;
    this.showPlaybooks = !this.showPlaybooks;
  }

  private onPlaybookClick(playbook: PlaybookInfo) {
    this.showPlaybooks = false;
    this.dispatchEvent(
      new CustomEvent("send-message", {
        detail: { message: playbook.body },
        bubbles: true,
        composed: true,
      }),
    );
  }

  private renderPlaybooks() {
    if (!this.playbooks.length) return nothing;

    const grouped = new Map<string, PlaybookInfo[]>();
    for (const p of this.playbooks) {
      const list = grouped.get(p.category) ?? [];
      list.push(p);
      grouped.set(p.category, list);
    }

    return html`${Array.from(grouped.entries()).map(
      ([category, items]) => html`
        <div class="playbook-section">
          <div class="playbook-category">${category}</div>
          <div class="playbook-grid">
            ${items.map(
              (p) => html`
                <div class="playbook-card" @click=${() => this.onPlaybookClick(p)}>
                  <span class="card-icon">${CATEGORY_ICONS[category] ?? "article"}</span>
                  <div class="card-text">
                    <div class="card-name">${humanize(p.name)}</div>
                    <div class="card-desc">${p.description}</div>
                  </div>
                </div>
              `,
            )}
          </div>
        </div>
      `,
    )}`;
  }

  render() {
    const hasMessages = this.messages.length > 0;

    return html`
      ${hasMessages
        ? html`
            <div class="messages-scroll">
              <div class="messages">
                ${repeat(
                  this.messages,
                  (m) => m.id,
                  (m) => html`<chat-message .msg=${m}></chat-message>`,
                )}
              </div>
            </div>
          `
        : html`
            <div class="empty-state ${this.showPlaybooks ? "compact" : ""}">
              <div class="empty-header">
                <span class="empty-icon">forklift</span>
                <div class="empty-title">Moving your virtual machines?</div>
                <div class="empty-hint">Pick a playbook to get started, or ask me anything.</div>
              </div>
            </div>
          `}

      <div class="composer-area">
        <div class="composer-inner">
          <chat-composer
            .playbooksOpen=${this.showPlaybooks}
            @toggle-playbooks=${this.onTogglePlaybooks}
          ></chat-composer>
          <div class="playbook-panel ${this.showPlaybooks ? "open" : ""}">
            ${this.renderPlaybooks()}
          </div>
        </div>
      </div>
    `;
  }
}
