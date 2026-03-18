import { LitElement, html, css, nothing } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { appState, type ToolCallEntry, type PinCard } from "../state/app-state.js";
import { sendApproval } from "../services/api-client.js";
import {
  identify,
  parseResult,
  cardId,
  parseTimeSeriesData,
  type CardDisplayType,
  type ToolIdentification,
} from "../utils/tool-registry/index.js";

@customElement("tool-call-card")
export class ToolCallCard extends LitElement {
  static styles = css`
    :host {
      display: block;
    }

    .card {
      border: 1px solid var(--border-secondary);
      border-radius: var(--radius-sm);
      background: var(--bg-tool);
      overflow: hidden;
      font-size: var(--font-size-sm);
    }

    .header {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      background: var(--bg-tool-header);
      cursor: pointer;
      user-select: none;
      transition: background var(--transition-fast);
    }

    .header:hover {
      background: var(--bg-hover);
    }

    .chevron {
      width: 14px;
      height: 14px;
      color: var(--text-tertiary);
      transition: transform var(--transition-fast);
      flex-shrink: 0;
    }

    .chevron.open {
      transform: rotate(90deg);
    }

    .icon {
      width: 16px;
      height: 16px;
      flex-shrink: 0;
    }

    .icon.call {
      color: var(--accent-warning);
    }

    .icon.result {
      color: var(--accent-success);
    }

    .icon.denied {
      color: var(--accent-danger);
    }

    .icon.pending {
      color: var(--accent-info);
    }

    .name {
      font-weight: var(--font-weight-medium);
      color: var(--text-primary);
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .badge {
      font-size: var(--font-size-xs);
      padding: 2px 6px;
      border-radius: var(--radius-full);
      font-weight: var(--font-weight-medium);
      white-space: nowrap;
    }

    .badge.category {
      background: rgba(50, 102, 173, 0.1);
      color: var(--text-tertiary);
      font-family: var(--font-mono);
    }

    .badge.running {
      background: rgba(59, 130, 246, 0.1);
      color: var(--accent-info);
    }

    .badge.done {
      background: rgba(34, 197, 94, 0.1);
      color: var(--accent-success);
    }

    .badge.error,
    .badge.denied {
      background: rgba(239, 68, 68, 0.1);
      color: var(--accent-danger);
    }

    .badge.waiting {
      background: rgba(59, 130, 246, 0.1);
      color: var(--accent-info);
    }

    .body {
      padding: 10px 12px;
      border-top: 1px solid var(--border-secondary);
    }

    .section-label {
      font-size: var(--font-size-xs);
      font-weight: var(--font-weight-bold);
      color: var(--text-tertiary);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 4px;
    }

    .code-block {
      font-family: var(--font-mono);
      font-size: var(--font-size-xs);
      padding: 8px 10px;
      background: var(--bg-code);
      border-radius: var(--radius-xs);
      white-space: pre-wrap;
      word-break: break-all;
      overflow-x: auto;
      max-height: 300px;
      overflow-y: auto;
      color: var(--text-primary);
      line-height: 1.5;
    }

    .result-section {
      margin-top: 10px;
    }

    .approval-bar {
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding: 10px 12px;
      border-top: 1px solid var(--border-secondary);
    }

    .deny-reason-input {
      width: 100%;
      box-sizing: border-box;
      padding: 6px 10px;
      font-size: var(--font-size-sm);
      font-family: inherit;
      color: var(--text-primary);
      background: var(--bg-code);
      border: 1px solid var(--border-primary);
      border-radius: var(--radius-xs);
      outline: none;
      transition: border-color var(--transition-fast);
    }

    .deny-reason-input::placeholder {
      color: var(--text-tertiary);
    }

    .deny-reason-input:focus {
      border-color: var(--accent-info);
    }

    .approval-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .approval-actions span {
      flex: 1;
      font-size: var(--font-size-sm);
      color: var(--text-secondary);
    }

    .approve-btn,
    .deny-btn {
      padding: 6px 14px;
      border-radius: var(--radius-sm);
      font-size: var(--font-size-sm);
      font-weight: var(--font-weight-medium);
      cursor: pointer;
      transition: background var(--transition-fast);
    }

    .approve-btn {
      background: var(--accent-success);
      color: white;
    }

    .approve-btn:hover {
      filter: brightness(1.1);
    }

    .deny-btn {
      background: var(--bg-tertiary);
      color: var(--text-secondary);
      border: 1px solid var(--border-primary);
    }

    .deny-btn:hover {
      background: var(--bg-hover);
      color: var(--accent-danger);
    }

    .pin-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 24px;
      height: 24px;
      padding: 0;
      border: none;
      border-radius: var(--radius-xs);
      background: transparent;
      color: var(--text-tertiary);
      cursor: pointer;
      flex-shrink: 0;
      transition: all var(--transition-fast);
    }

    .pin-btn:hover {
      background: var(--bg-hover);
      color: var(--accent-primary);
    }

    .pin-btn.pinned {
      color: var(--accent-primary);
    }

    .pin-btn svg {
      width: 14px;
      height: 14px;
    }
  `;

  @property({ type: Object }) entry!: ToolCallEntry;
  @property({ type: String }) sessionId = "";

  @state() private expanded = false;
  @state() private pinned = false;
  @state() private graphPinned = false;
  @state() private denyReasonInput = "";

  private unsubscribe?: () => void;
  private _idCacheKey: string | undefined;
  private _idCacheValue: ToolIdentification | undefined;
  private _graphCacheKey: string | undefined;
  private _graphCacheValue = false;

  private get identification(): ToolIdentification {
    const e = this.entry;
    const key = e.name + JSON.stringify(e.arguments);
    if (this._idCacheKey === key && this._idCacheValue) return this._idCacheValue;
    this._idCacheKey = key;
    this._idCacheValue = identify(e.name, e.arguments as Record<string, unknown>);
    return this._idCacheValue;
  }

  connectedCallback() {
    super.connectedCallback();
    this.unsubscribe = appState.subscribe(() => this.syncPinned());
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.unsubscribe?.();
  }

  private syncPinned() {
    const e = this.entry;
    if (e.result && !e.denied) {
      this.pinned = appState.hasCard(cardId(e.name, e.arguments));
      this.graphPinned = appState.hasCard(`graph-${cardId(e.name, e.arguments)}`);
    }
  }

  private toggle() {
    this.expanded = !this.expanded;
  }

  private pinCard(ev: Event) {
    ev.stopPropagation();
    const e = this.entry;
    const id = cardId(e.name, e.arguments);
    if (appState.hasCard(id)) {
      appState.removeCard(id);
      return;
    }

    const command = (e.arguments as Record<string, unknown>).command;
    const title = command ? `${e.name}: ${command}` : e.name;
    const rawResult = e.result!;
    const card: PinCard = {
      id,
      title,
      content: "",
      timestamp: Date.now(),
      toolName: e.name,
      toolArgs: e.arguments as Record<string, unknown>,
      loading: true,
    };

    this.dispatchEvent(
      new CustomEvent("pin-card", {
        detail: { card },
        bubbles: true,
        composed: true,
      }),
    );

    setTimeout(() => {
      const parsed = parseResult(this.identification, rawResult);
      const type = this.identification.canPinGraph
        ? ("text" as CardDisplayType)
        : parsed.displayType;
      appState.updateCard(id, {
        content: parsed.content,
        type,
        loading: false,
      });
    }, 0);
  }

  private async approve() {
    const sid = appState.state.sessionId;
    if (!sid) return;
    appState.updateLastToolCall((tc) => ({ ...tc, pending: false }));
    try {
      await sendApproval(sid, true);
    } catch {
      // best-effort
    }
  }

  private async deny() {
    const sid = appState.state.sessionId;
    if (!sid) return;
    const reason = this.denyReasonInput.trim() || "denied by user";
    this.denyReasonInput = "";
    appState.updateLastToolCall((tc) => ({
      ...tc,
      pending: false,
      denied: true,
      denyReason: reason,
    }));
    try {
      await sendApproval(sid, false, reason);
    } catch {
      // best-effort
    }
  }

  private get hasResultError(): boolean {
    if (!this.entry.result) return false;
    return parseResult(this.identification, this.entry.result).hasError;
  }

  private get statusBadge() {
    const e = this.entry;
    if (e.denied) return html`<span class="badge denied">denied</span>`;
    if (e.pending) return html`<span class="badge waiting">waiting</span>`;
    if (e.result !== undefined) {
      if (this.hasResultError) return html`<span class="badge error">error</span>`;
      return html`<span class="badge done">done</span>`;
    }
    return html`<span class="badge running">running</span>`;
  }

  private get iconClass(): string {
    const e = this.entry;
    if (e.denied) return "denied";
    if (e.pending) return "pending";
    if (e.result !== undefined) return "result";
    return "call";
  }

  private get canPin(): boolean {
    const e = this.entry;
    if (!e.result || e.denied) return false;
    return this.identification.canPin;
  }

  private get canPinGraph(): boolean {
    const e = this.entry;
    if (!e.result || e.denied) return false;
    if (!this.identification.canPinGraph) return false;
    if (this._graphCacheKey === e.result) return this._graphCacheValue;
    this._graphCacheKey = e.result;
    const parsed = parseTimeSeriesData(e.result);
    this._graphCacheValue = parsed !== null && parsed.series.length > 0;
    return this._graphCacheValue;
  }

  private get pinButton() {
    if (!this.canPin) return nothing;
    return html`
      <button
        class="pin-btn ${this.pinned ? "pinned" : ""}"
        @click=${this.pinCard}
        title=${this.pinned ? "Pinned" : "Pin to detail pane"}
      >
        <svg
          viewBox="0 0 24 24"
          fill="${this.pinned ? "currentColor" : "none"}"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M12 2 L12 12" />
          <path d="M18.5 8.5 C18.5 12 16 14 12 14 C8 14 5.5 12 5.5 8.5" />
          <path d="M12 14 L12 22" />
        </svg>
      </button>
    `;
  }

  private pinGraphCard(ev: Event) {
    ev.stopPropagation();
    const e = this.entry;
    const id = `graph-${cardId(e.name, e.arguments)}`;
    if (appState.hasCard(id)) {
      appState.removeCard(id);
      return;
    }

    const command = (e.arguments as Record<string, unknown>).command;
    const title = command ? `${e.name}: ${command}` : e.name;
    const card: PinCard = {
      id,
      title,
      content: e.result!,
      timestamp: Date.now(),
      toolName: e.name,
      toolArgs: e.arguments as Record<string, unknown>,
      type: "graph",
    };

    this.dispatchEvent(
      new CustomEvent("pin-card", {
        detail: { card },
        bubbles: true,
        composed: true,
      }),
    );
  }

  private get graphPinButton() {
    if (!this.canPinGraph) return nothing;
    return html`
      <button
        class="pin-btn ${this.graphPinned ? "pinned" : ""}"
        @click=${this.pinGraphCard}
        title=${this.graphPinned ? "Graph pinned" : "Pin as graph"}
      >
        <svg
          viewBox="0 0 24 24"
          fill="${this.graphPinned ? "currentColor" : "none"}"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
        </svg>
      </button>
    `;
  }

  render() {
    const e = this.entry;
    const argsStr = JSON.stringify(e.arguments, null, 2);

    return html`
      <div class="card">
        <div class="header" @click=${this.toggle}>
          <svg
            class="chevron ${this.expanded ? "open" : ""}"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="9 18 15 12 9 6" />
          </svg>
          <svg
            class="icon ${this.iconClass}"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path
              d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"
            />
          </svg>
          <span class="name">${e.name}</span>
          ${this.identification.identified
            ? html`<span class="badge category">${this.identification.category}</span>`
            : nothing}
          ${this.statusBadge} ${this.graphPinButton} ${this.pinButton}
        </div>

        ${this.expanded
          ? html`
              <div class="body">
                <div class="section-label">Arguments</div>
                <div class="code-block">${argsStr}</div>

                ${e.result !== undefined
                  ? html`
                      <div class="result-section">
                        <div class="section-label">Result</div>
                        <div class="code-block">${e.result}</div>
                      </div>
                    `
                  : nothing}
                ${e.denied && e.denyReason
                  ? html`
                      <div class="result-section">
                        <div class="section-label">Denial reason</div>
                        <div class="code-block">${e.denyReason}</div>
                      </div>
                    `
                  : nothing}
              </div>
            `
          : nothing}
        ${e.pending
          ? html`
              <div class="approval-bar">
                <input
                  class="deny-reason-input"
                  type="text"
                  placeholder="Reason for denial (optional)"
                  .value=${this.denyReasonInput}
                  @input=${(ev: InputEvent) => {
                    this.denyReasonInput = (ev.target as HTMLInputElement).value;
                  }}
                />
                <div class="approval-actions">
                  <span>Approve this tool call?</span>
                  <button class="deny-btn" @click=${this.deny}>Deny</button>
                  <button class="approve-btn" @click=${this.approve}>Approve</button>
                </div>
              </div>
            `
          : nothing}
      </div>
    `;
  }
}
