import { LitElement, html, css } from "lit";
import { customElement, state } from "lit/decorators.js";
import { appState, type ChatSummary } from "../state/app-state.js";
import { formatTimeAgo } from "../utils/format-time-ago.js";
import { TimeTicker } from "../utils/time-ticker.js";
import "./auto-refresh-settings.js";

@customElement("agent-sidebar")
export class AgentSidebar extends LitElement {
  static styles = css`
    :host {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: var(--bg-sidebar);
      border-right: none;
      overflow: hidden;
    }

    .new-chat-btn {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 14px;
      border-radius: var(--radius-sm);
      background: var(--accent-primary);
      color: var(--text-inverse);
      font-size: var(--font-size-sm);
      font-weight: var(--font-weight-medium);
      border: none;
      cursor: pointer;
      transition: background var(--transition-fast);
    }

    .new-chat-btn:hover:not(:disabled) {
      background: var(--accent-hover);
    }

    .new-chat-btn:disabled {
      background: var(--bg-tertiary);
      color: var(--text-secondary);
      cursor: default;
    }

    .new-chat-btn svg {
      width: 14px;
      height: 14px;
    }

    .body {
      flex: 1;
      overflow-y: auto;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      scrollbar-width: thin;
      scrollbar-color: var(--border-primary) transparent;
    }

    .body::-webkit-scrollbar {
      width: 4px;
    }

    .body::-webkit-scrollbar-track {
      background: transparent;
    }

    .body::-webkit-scrollbar-thumb {
      background: var(--border-primary);
      border-radius: 2px;
    }

    .section {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .section-title {
      font-size: var(--font-size-xs);
      font-weight: var(--font-weight-bold);
      color: var(--text-tertiary);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .status-grid {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 4px 12px;
      font-size: var(--font-size-sm);
    }

    .status-label {
      color: var(--text-tertiary);
    }

    .status-value {
      color: var(--text-primary);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .session-id {
      font-family: var(--font-mono);
      font-size: var(--font-size-xs);
      color: var(--text-tertiary);
      padding: 4px 0;
      word-break: break-all;
    }

    .footer {
      padding: 12px 16px;
      border-top: 1px solid var(--border-secondary);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .error-banner {
      padding: 8px 12px;
      background: var(--accent-danger);
      color: var(--text-inverse);
      font-size: var(--font-size-sm);
      border-radius: var(--radius-xs);
    }

    .warning-banner {
      padding: 8px 12px;
      background: var(--accent-warning, #b45309);
      color: var(--text-inverse, #fff);
      font-size: var(--font-size-sm);
      border-radius: var(--radius-xs);
    }

    .chat-list {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .chat-item {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 6px 10px;
      border-radius: var(--radius-xs);
      cursor: pointer;
      transition: background var(--transition-fast);
    }

    .chat-item:hover {
      background: var(--bg-hover);
    }

    .chat-item.active {
      background: var(--bg-active, var(--bg-hover));
    }

    .chat-item-indicator {
      flex-shrink: 0;
      width: 14px;
      height: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--accent-primary);
    }

    .chat-item-indicator svg {
      width: 14px;
      height: 14px;
    }

    .chat-item-title {
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-size: var(--font-size-sm);
      color: var(--text-primary);
    }

    .chat-item-trailing {
      flex-shrink: 0;
      display: grid;
      place-items: center;
    }

    .chat-item-trailing > * {
      grid-area: 1 / 1;
    }

    .chat-item-time {
      font-size: var(--font-size-xs);
      color: var(--text-tertiary);
      pointer-events: none;
      transition: opacity var(--transition-fast);
    }

    .chat-item-delete {
      z-index: 1;
      background: none;
      border: none;
      cursor: pointer;
      color: var(--text-tertiary);
      padding: 2px;
      border-radius: var(--radius-xs);
      line-height: 1;
      opacity: 0;
      transition:
        opacity var(--transition-fast),
        color var(--transition-fast);
    }

    .chat-item-delete:hover {
      color: var(--accent-danger);
    }

    .chat-item:hover .chat-item-delete {
      opacity: 1;
    }

    .chat-item:hover .chat-item-time {
      opacity: 0;
    }

    .accordion {
      display: flex;
      flex-direction: column;
    }

    .accordion-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      user-select: none;
      padding: 2px 0;
    }

    .accordion-header:hover .accordion-chevron {
      color: var(--text-primary);
    }

    .accordion-chevron {
      width: 14px;
      height: 14px;
      color: var(--text-tertiary);
      transition:
        transform var(--transition-fast),
        color var(--transition-fast);
      flex-shrink: 0;
    }

    .accordion-chevron.open {
      transform: rotate(90deg);
    }

    .accordion-body {
      display: grid;
      grid-template-rows: 0fr;
      transition: grid-template-rows 0.2s ease;
    }

    .accordion-body.open {
      grid-template-rows: 1fr;
    }

    .accordion-body > div {
      overflow: hidden;
      padding-top: 0;
      transition: padding-top 0.2s ease;
    }

    .accordion-body.open > div {
      padding-top: 8px;
    }
  `;

  private ticker = new TimeTicker(this);

  @state() private model = "";
  @state() private toolCount = 0;
  @state() private contextWindow = 0;
  @state() private sessionId: string | null = null;
  @state() private activeChatId: string | null = null;
  @state() private chatList: ChatSummary[] = [];
  @state() private error: string | null = null;
  @state() private warning: string | null = null;
  @state() private openSections: Record<string, boolean> = {
    status: false,
    session: false,
    model: false,
    mcp: false,
    skills: false,
    context: false,
    policies: false,
    settings: false,
  };

  private unsubscribe?: () => void;

  connectedCallback() {
    super.connectedCallback();
    this.unsubscribe = appState.subscribe(() => {
      const s = appState.state;
      this.model = s.model;
      this.toolCount = s.toolCount;
      this.contextWindow = s.contextWindow;
      this.sessionId = s.sessionId;
      this.activeChatId = s.activeChatId;
      this.chatList = s.chatList;
      this.error = s.error;
      this.warning = s.warning;
    });
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.unsubscribe?.();
  }

  private newChat() {
    appState.clearMessages();
  }

  private selectChat(chatId: string) {
    if (chatId === this.activeChatId) return;
    this.dispatchEvent(
      new CustomEvent("load-chat", { detail: { chatId }, bubbles: true, composed: true }),
    );
  }

  private deleteChat(e: Event, chatId: string) {
    e.stopPropagation();
    this.dispatchEvent(
      new CustomEvent("delete-chat", { detail: { chatId }, bubbles: true, composed: true }),
    );
  }

  private toggleSection(key: string) {
    this.openSections = {
      ...this.openSections,
      [key]: !this.openSections[key],
    };
  }

  private renderAccordion(key: string, title: string, content: unknown) {
    const isOpen = this.openSections[key] ?? false;
    return html`
      <div class="accordion">
        <div class="accordion-header" @click=${() => this.toggleSection(key)}>
          <span class="section-title">${title}</span>
          <svg
            class="accordion-chevron ${isOpen ? "open" : ""}"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </div>
        <div class="accordion-body ${isOpen ? "open" : ""}">
          <div>${content}</div>
        </div>
      </div>
    `;
  }

  render() {
    return html`
      <div class="body">
        ${this.error ? html`<div class="error-banner">${this.error}</div>` : ""}
        ${this.warning ? html`<div class="warning-banner">${this.warning}</div>` : ""}

        <div class="section">
          <span class="section-title">Chats</span>
          <button class="new-chat-btn" ?disabled=${!this.activeChatId} @click=${this.newChat}>
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            New Chat
          </button>
          ${this.chatList.length
            ? html`
                <div class="chat-list">
                  ${this.chatList.map(
                    (c) => html`
                      <div
                        class="chat-item ${c.id === this.activeChatId ? "active" : ""}"
                        @click=${() => this.selectChat(c.id)}
                      >
                        <span class="chat-item-indicator">
                          ${c.id === this.activeChatId
                            ? html`<svg
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                              >
                                <path
                                  d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
                                ></path>
                              </svg>`
                            : ""}
                        </span>
                        <span class="chat-item-title">${c.title}</span>
                        <span class="chat-item-trailing">
                          <span class="chat-item-time">${formatTimeAgo(c.updatedAt * 1000)}</span>
                          <button
                            class="chat-item-delete"
                            title="Delete chat"
                            @click=${(e: Event) => this.deleteChat(e, c.id)}
                          >
                            <svg
                              width="14"
                              height="14"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              stroke-width="2"
                              stroke-linecap="round"
                              stroke-linejoin="round"
                            >
                              <polyline points="3 6 5 6 21 6"></polyline>
                              <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"></path>
                              <path d="M10 11v6"></path>
                              <path d="M14 11v6"></path>
                            </svg>
                          </button>
                        </span>
                      </div>
                    `,
                  )}
                </div>
              `
            : ""}
        </div>

        ${this.renderAccordion(
          "status",
          "Status",
          html`
            <div class="status-grid">
              <span class="status-label">Model</span>
              <span class="status-value">${this.model || "—"}</span>
              <span class="status-label">Tools</span>
              <span class="status-value">${this.toolCount}</span>
              <span class="status-label">Context</span>
              <span class="status-value">
                ${this.contextWindow ? `${(this.contextWindow / 1000).toFixed(1)}k tokens` : "—"}
              </span>
            </div>
          `,
        )}
        ${this.sessionId
          ? this.renderAccordion(
              "session",
              "Session",
              html`<div class="session-id">${this.sessionId}</div>`,
            )
          : ""}
        ${this.renderAccordion("model", "Model", html`<model-selector></model-selector>`)}
        ${this.renderAccordion("mcp", "MCP Servers", html`<mcp-manager></mcp-manager>`)}
        ${this.renderAccordion("skills", "Skills", html`<skill-selector></skill-selector>`)}
        ${this.renderAccordion("context", "Context", html`<context-editor></context-editor>`)}
        ${this.renderAccordion(
          "policies",
          "Tool Policies",
          html`<tool-policy-editor></tool-policy-editor>`,
        )}
        ${this.renderAccordion(
          "settings",
          "Settings",
          html`<auto-refresh-settings></auto-refresh-settings>`,
        )}
      </div>
    `;
  }
}
