import { LitElement, html, css, nothing } from "lit";
import { customElement, state } from "lit/decorators.js";
import { appState, type PinCard } from "../state/app-state.js";
import { autoRefreshManager } from "../state/auto-refresh-state.js";
import { callTool } from "../services/api-client.js";
import { identify, parseResult, type CardDisplayType } from "../utils/tool-registry/index.js";
import { formatTimeAgo } from "../utils/format-time-ago.js";
import { TimeTicker } from "../utils/time-ticker.js";
import {
  applyHighlights,
  clearHighlights,
  activateMatch,
  injectHighlightStyles,
} from "../utils/highlight-utils.js";
import "./card-search-bar.js";
import "./text-renderer.js";

interface SearchState {
  query: string;
  count: number;
  index: number;
}

@customElement("detail-pane")
export class DetailPane extends LitElement {
  static styles = css`
    :host {
      display: flex;
      flex-direction: column;
      height: 100%;
      overflow: hidden;
      background: var(--bg-secondary);
      box-sizing: border-box;
    }

    .cards {
      flex: 1;
      overflow-y: auto;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .card {
      border: 1px solid var(--border-secondary);
      border-radius: var(--radius-sm);
      background: var(--bg-primary);
      overflow: hidden;
    }

    .card.drag-over {
      border-color: var(--accent-primary);
      box-shadow: 0 0 0 1px var(--accent-primary);
    }

    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      background: var(--bg-tertiary);
      cursor: grab;
      user-select: none;
    }

    .card-header:active {
      cursor: grabbing;
    }

    .card-title {
      flex: 1;
      font-size: var(--font-size-sm);
      font-weight: var(--font-weight-medium);
      color: var(--text-primary);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .timestamp {
      font-size: var(--font-size-xs);
      color: var(--text-tertiary);
      white-space: nowrap;
      flex-shrink: 0;
      font-variant-numeric: tabular-nums;
    }

    .header-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 22px;
      height: 22px;
      padding: 0;
      border: none;
      border-radius: var(--radius-xs);
      background: transparent;
      color: var(--text-tertiary);
      cursor: pointer;
      flex-shrink: 0;
      transition: all var(--transition-fast);
    }

    .header-btn:hover {
      background: var(--bg-hover);
      color: var(--accent-primary);
    }

    .header-btn.search {
      color: var(--text-tertiary);
    }

    .header-btn.minimize:hover {
      color: var(--accent-warning);
    }

    .header-btn.close:hover {
      color: var(--accent-danger);
    }

    .header-btn.rerun:hover {
      color: var(--accent-success);
    }

    .header-btn.rerunning {
      color: var(--accent-info);
      animation: spin 1s linear infinite;
    }

    .header-btn.auto-refresh {
      color: var(--text-tertiary);
    }

    .header-btn.auto-refresh:hover {
      color: var(--accent-info);
    }

    .header-btn.auto-refresh.active {
      color: var(--accent-info);
      animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
      0%,
      100% {
        opacity: 1;
      }
      50% {
        opacity: 0.5;
      }
    }

    .header-btn.copy.copied {
      color: var(--accent-success);
    }

    @keyframes spin {
      from {
        transform: rotate(0deg);
      }
      to {
        transform: rotate(360deg);
      }
    }

    .header-btn svg {
      width: 14px;
      height: 14px;
    }

    /* --- tool-call info strip ------------------------------------------- */

    .tool-strip {
      border-top: 1px solid var(--border-secondary);
      background: var(--bg-tool-header, var(--bg-tertiary));
      font-size: var(--font-size-xs);
      overflow: hidden;
    }

    .tool-strip-header {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      cursor: pointer;
      user-select: none;
      transition: background var(--transition-fast);
    }

    .tool-strip-header:hover {
      background: var(--bg-hover);
    }

    .tool-chevron {
      width: 12px;
      height: 12px;
      color: var(--text-tertiary);
      transition: transform var(--transition-fast);
      flex-shrink: 0;
    }

    .tool-chevron.open {
      transform: rotate(90deg);
    }

    .tool-icon {
      width: 12px;
      height: 12px;
      color: var(--accent-warning);
      flex-shrink: 0;
    }

    .tool-name {
      font-family: var(--font-mono);
      color: var(--text-secondary);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .tool-summary {
      color: var(--text-tertiary);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      flex: 1;
    }

    .tool-detail {
      padding: 6px 12px;
      border-top: 1px solid var(--border-secondary);
    }

    .tool-detail-label {
      font-size: var(--font-size-xs);
      font-weight: var(--font-weight-bold);
      color: var(--text-tertiary);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 2px;
    }

    .tool-code {
      font-family: var(--font-mono);
      font-size: var(--font-size-xs);
      padding: 6px 8px;
      background: var(--bg-code);
      border-radius: var(--radius-xs);
      white-space: pre-wrap;
      word-break: break-all;
      overflow-x: auto;
      max-height: 200px;
      overflow-y: auto;
      color: var(--text-primary);
      line-height: 1.4;
    }

    /* --- card body ------------------------------------------------------- */

    .card-body {
      padding: 10px 12px;
      overflow: auto;
      user-select: text;
      cursor: auto;
    }

    .card-body.no-scroll {
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-sizing: border-box;
    }

    .resize-grip {
      height: 6px;
      cursor: ns-resize;
      background: var(--bg-tertiary);
      display: flex;
      align-items: center;
      justify-content: center;
      user-select: none;
      flex-shrink: 0;
      transition: background var(--transition-fast);
    }

    .resize-grip:hover,
    .resize-grip.active {
      background: var(--accent-primary);
    }

    .resize-grip::after {
      content: "";
      display: block;
      width: 32px;
      height: 2px;
      border-radius: 1px;
      background: var(--text-tertiary);
      opacity: 0.5;
    }

    .resize-grip:hover::after,
    .resize-grip.active::after {
      background: var(--bg-primary);
      opacity: 0.8;
    }

    .placeholder {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--text-tertiary);
      font-size: var(--font-size-sm);
      font-family: var(--font-sans);
      padding: 16px;
      text-align: center;
      user-select: none;
    }

    .card-loading {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 24px 12px;
      color: var(--text-tertiary);
      font-size: var(--font-size-sm);
      font-family: var(--font-sans);
    }

    .card-loading-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--text-tertiary);
      animation: loadPulse 1.2s ease-in-out infinite;
    }

    .card-loading-dot:nth-child(2) {
      animation-delay: 0.15s;
    }

    .card-loading-dot:nth-child(3) {
      animation-delay: 0.3s;
    }

    @keyframes loadPulse {
      0%,
      80%,
      100% {
        opacity: 0.25;
        transform: scale(0.8);
      }
      40% {
        opacity: 1;
        transform: scale(1);
      }
    }
  `;

  private static readonly DEFAULT_CARD_HEIGHT = 400;
  private static readonly MIN_CARD_HEIGHT = 80;

  private ticker = new TimeTicker(this);

  @state() private cards: PinCard[] = [];
  @state() private expandedToolStrips = new Set<string>();
  @state() private rerunningCards = new Set<string>();
  @state() private copiedCards = new Set<string>();
  @state() private searchOpen = new Set<string>();
  @state() private searchState = new Map<string, SearchState>();
  @state() private minimizedCards = new Set<string>();

  private dragId: string | null = null;
  private resizeCardId: string | null = null;
  private resizeStartY = 0;
  private resizeStartHeight = 0;
  private unsubscribe?: () => void;
  private unsubscribeRefresh?: () => void;
  private refreshTimers = new Map<string, ReturnType<typeof setInterval>>();

  connectedCallback() {
    super.connectedCallback();
    this.unsubscribe = appState.subscribe(() => {
      this.cards = appState.state.pinCards;
      this.reconcileRefreshTimers();
    });
    this.unsubscribeRefresh = autoRefreshManager.subscribe(() => {
      this.restartAllRefreshTimers();
    });
    this.cards = appState.state.pinCards;
    this.reconcileRefreshTimers();
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.unsubscribe?.();
    this.unsubscribeRefresh?.();
    this.clearAllRefreshTimers();
    document.removeEventListener("mousemove", this.onResizeMove);
    document.removeEventListener("mouseup", this.onResizeEnd);
  }

  // --- auto-refresh timer management ----------------------------------------

  private reconcileRefreshTimers() {
    const intervalMs = autoRefreshManager.intervalSec * 1000;
    const wanted = new Map(
      this.cards.filter((c) => c.autoRefresh && c.toolName).map((c) => [c.id, intervalMs] as const),
    );

    for (const [id, timer] of this.refreshTimers) {
      if (!wanted.has(id)) {
        clearInterval(timer);
        this.refreshTimers.delete(id);
      }
    }

    for (const [id] of wanted) {
      if (this.refreshTimers.has(id)) continue;
      const timer = setInterval(() => {
        const card = appState.state.pinCards.find((c) => c.id === id);
        if (card?.autoRefresh && card.toolName) {
          this.rerunTool(card);
        }
      }, intervalMs);
      this.refreshTimers.set(id, timer);
    }
  }

  /** Called when the global interval changes -- restart all active timers. */
  private restartAllRefreshTimers() {
    this.clearAllRefreshTimers();
    this.reconcileRefreshTimers();
  }

  private clearAllRefreshTimers() {
    for (const timer of this.refreshTimers.values()) {
      clearInterval(timer);
    }
    this.refreshTimers.clear();
  }

  private toggleAutoRefresh(card: PinCard) {
    appState.updateCard(card.id, { autoRefresh: !card.autoRefresh });
  }

  private close(id: string) {
    appState.removeCard(id);
  }

  private toggleMinimize(id: string) {
    const next = new Set(this.minimizedCards);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    this.minimizedCards = next;
  }

  private async copyCard(card: PinCard) {
    try {
      await navigator.clipboard.writeText(card.content);
      const next = new Set(this.copiedCards);
      next.add(card.id);
      this.copiedCards = next;
      setTimeout(() => {
        const after = new Set(this.copiedCards);
        after.delete(card.id);
        this.copiedCards = after;
      }, 1500);
    } catch {
      // clipboard access denied -- ignore
    }
  }

  private toggleToolStrip(id: string) {
    const next = new Set(this.expandedToolStrips);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    this.expandedToolStrips = next;
  }

  private async rerunTool(card: PinCard) {
    if (!card.toolName || this.rerunningCards.has(card.id)) return;

    const next = new Set(this.rerunningCards);
    next.add(card.id);
    this.rerunningCards = next;

    try {
      appState.updateCard(card.id, { loading: true });

      if (card.type === "graph" && card.graphPresets) {
        const { presets, start } = card.graphPresets;
        const results = await Promise.all(
          presets.map((name) =>
            callTool("metrics_read", {
              command: "preset",
              flags: { name, start, output: "markdown" },
            }),
          ),
        );
        const combined = results.map((r) => r.result).join("\n\n");
        appState.updateCard(card.id, {
          content: combined,
          loading: false,
          timestamp: Date.now(),
        });
      } else {
        const resp = await callTool(card.toolName, card.toolArgs ?? {});
        await new Promise<void>((resolve) =>
          setTimeout(() => {
            if (card.type === "graph") {
              appState.updateCard(card.id, {
                content: resp.result,
                loading: false,
                timestamp: Date.now(),
              });
            } else {
              const id = identify(card.toolName!, card.toolArgs ?? {});
              const parsed = parseResult(id, resp.result);
              const type = id.canPinGraph ? ("text" as CardDisplayType) : parsed.displayType;
              appState.updateCard(card.id, {
                content: parsed.content,
                type,
                loading: false,
                timestamp: Date.now(),
              });
            }
            resolve();
          }, 0),
        );
      }
    } catch (err) {
      appState.updateCard(card.id, {
        content: `**Error re-running tool:** ${(err as Error).message}`,
        loading: false,
      });
    } finally {
      const after = new Set(this.rerunningCards);
      after.delete(card.id);
      this.rerunningCards = after;
    }
  }

  // --- drag & drop --------------------------------------------------------

  private onDragStart(id: string, ev: DragEvent) {
    this.dragId = id;
    ev.dataTransfer!.effectAllowed = "move";
  }

  private onDragOver(ev: DragEvent) {
    ev.preventDefault();
    ev.dataTransfer!.dropEffect = "move";
  }

  private onDragEnter(ev: DragEvent) {
    const card = (ev.currentTarget as HTMLElement).closest(".card");
    card?.classList.add("drag-over");
  }

  private onDragLeave(ev: DragEvent) {
    const card = (ev.currentTarget as HTMLElement).closest(".card");
    const related = ev.relatedTarget as Node | null;
    if (card && !card.contains(related)) {
      card.classList.remove("drag-over");
    }
  }

  private onDrop(targetId: string, ev: DragEvent) {
    ev.preventDefault();
    const card = (ev.currentTarget as HTMLElement).closest(".card");
    card?.classList.remove("drag-over");

    if (!this.dragId || this.dragId === targetId) return;
    const to = this.cards.findIndex((c) => c.id === targetId);
    if (to >= 0) appState.moveCard(this.dragId, to);
    this.dragId = null;
  }

  private onDragEnd() {
    this.dragId = null;
    this.shadowRoot?.querySelectorAll(".drag-over").forEach((el) => {
      el.classList.remove("drag-over");
    });
  }

  // --- resize -------------------------------------------------------------

  private onResizeStart(cardId: string, ev: MouseEvent) {
    ev.preventDefault();
    this.resizeCardId = cardId;
    this.resizeStartY = ev.clientY;
    const card = this.cards.find((c) => c.id === cardId);
    this.resizeStartHeight = card?.height ?? DetailPane.DEFAULT_CARD_HEIGHT;

    const grip = ev.currentTarget as HTMLElement;
    grip.classList.add("active");

    document.addEventListener("mousemove", this.onResizeMove);
    document.addEventListener("mouseup", this.onResizeEnd);
  }

  private onResizeMove = (ev: MouseEvent) => {
    if (!this.resizeCardId) return;
    const delta = ev.clientY - this.resizeStartY;
    const clamped = Math.max(DetailPane.MIN_CARD_HEIGHT, this.resizeStartHeight + delta);

    const body = this.shadowRoot?.querySelector(
      `.card-body[data-card-id="${this.resizeCardId}"]`,
    ) as HTMLElement | null;
    if (body) body.style.height = `${clamped}px`;
  };

  private onResizeEnd = () => {
    if (!this.resizeCardId) return;

    const body = this.shadowRoot?.querySelector(
      `.card-body[data-card-id="${this.resizeCardId}"]`,
    ) as HTMLElement | null;
    const finalHeight = body ? parseInt(body.style.height, 10) : this.resizeStartHeight;

    appState.updateCardHeight(this.resizeCardId, finalHeight);

    this.shadowRoot?.querySelectorAll(".resize-grip.active").forEach((el) => {
      el.classList.remove("active");
    });

    this.resizeCardId = null;
    document.removeEventListener("mousemove", this.onResizeMove);
    document.removeEventListener("mouseup", this.onResizeEnd);
  };

  // --- card search --------------------------------------------------------

  private getRendererRoot(cardId: string): HTMLElement | null {
    const body = this.shadowRoot?.querySelector(`.card-body[data-card-id="${cardId}"]`);

    const mdRenderer = body?.querySelector("markdown-renderer");
    if (mdRenderer) {
      const inner = mdRenderer.shadowRoot?.querySelector(".md") as HTMLElement | null;
      if (inner && mdRenderer.shadowRoot) {
        injectHighlightStyles(mdRenderer.shadowRoot);
      }
      return inner;
    }

    const textRenderer = body?.querySelector("text-renderer");
    if (textRenderer) {
      const inner = textRenderer.shadowRoot?.querySelector(".text") as HTMLElement | null;
      if (inner && textRenderer.shadowRoot) {
        injectHighlightStyles(textRenderer.shadowRoot);
      }
      return inner;
    }

    return null;
  }

  private toggleSearch(cardId: string) {
    const next = new Set(this.searchOpen);
    if (next.has(cardId)) {
      next.delete(cardId);
      const root = this.getRendererRoot(cardId);
      if (root) clearHighlights(root);
      const s = new Map(this.searchState);
      s.delete(cardId);
      this.searchState = s;
    } else {
      next.add(cardId);
    }
    this.searchOpen = next;
  }

  private onSearchInput(cardId: string, ev: CustomEvent<string>) {
    const query = ev.detail ?? "";
    const root = this.getRendererRoot(cardId);
    if (!root) return;

    const count = applyHighlights(root, query);
    const index = count > 0 ? 0 : -1;
    if (count > 0) activateMatch(root, 0);

    const next = new Map(this.searchState);
    next.set(cardId, { query, count, index });
    this.searchState = next;
  }

  private onSearchNav(cardId: string, direction: 1 | -1) {
    const s = this.searchState.get(cardId);
    if (!s || s.count === 0) return;

    const index = (s.index + direction + s.count) % s.count;
    const root = this.getRendererRoot(cardId);
    if (root) activateMatch(root, index);

    const next = new Map(this.searchState);
    next.set(cardId, { ...s, index });
    this.searchState = next;
  }

  // --- tool strip summary -------------------------------------------------

  private toolSummary(card: PinCard): string {
    if (!card.toolArgs || Object.keys(card.toolArgs).length === 0) return "";
    const cmd = card.toolArgs.command;
    if (typeof cmd === "string") return cmd;
    const vals = Object.values(card.toolArgs)
      .map((v) => (typeof v === "string" ? v : JSON.stringify(v)))
      .join(", ");
    return vals.length > 60 ? vals.slice(0, 57) + "..." : vals;
  }

  // --- render helpers -----------------------------------------------------

  private renderToolStrip(card: PinCard) {
    if (!card.toolName) return nothing;

    const expanded = this.expandedToolStrips.has(card.id);
    const summary = this.toolSummary(card);
    const argsStr = JSON.stringify(card.toolArgs ?? {}, null, 2);

    return html`
      <div class="tool-strip">
        <div class="tool-strip-header" @click=${() => this.toggleToolStrip(card.id)}>
          <svg
            class="tool-chevron ${expanded ? "open" : ""}"
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
            class="tool-icon"
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
          <span class="tool-name">${card.toolName}</span>
          ${summary ? html`<span class="tool-summary">${summary}</span>` : nothing}
        </div>
        ${expanded
          ? html`
              <div class="tool-detail">
                <div class="tool-detail-label">Arguments</div>
                <div class="tool-code">${argsStr}</div>
              </div>
            `
          : nothing}
      </div>
    `;
  }

  private renderRerunButton(card: PinCard) {
    if (!card.toolName) return nothing;
    const spinning = this.rerunningCards.has(card.id);

    return html`
      <button
        class="header-btn rerun ${spinning ? "rerunning" : ""}"
        title="Re-run tool call"
        @click=${(ev: Event) => {
          ev.stopPropagation();
          this.rerunTool(card);
        }}
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="23 4 23 10 17 10" />
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
        </svg>
      </button>
    `;
  }

  private renderAutoRefreshButton(card: PinCard) {
    if (!card.toolName) return nothing;
    const active = card.autoRefresh === true;

    return html`
      <button
        class="header-btn auto-refresh ${active ? "active" : ""}"
        title=${active ? "Stop auto-refresh" : "Start auto-refresh"}
        aria-label=${active ? "Stop auto-refresh" : "Start auto-refresh"}
        aria-pressed=${active ? "true" : "false"}
        @click=${(ev: Event) => {
          ev.stopPropagation();
          this.toggleAutoRefresh(card);
        }}
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="12" cy="12" r="10" />
          <polyline points="12 6 12 12 16 14" />
        </svg>
      </button>
    `;
  }

  private renderSearchBar(card: PinCard) {
    if (!this.searchOpen.has(card.id)) return nothing;
    const s = this.searchState.get(card.id);
    return html`
      <card-search-bar
        .matchCount=${s?.count ?? 0}
        .activeIndex=${s?.index ?? -1}
        @search-input=${(ev: CustomEvent<string>) => this.onSearchInput(card.id, ev)}
        @search-prev=${() => this.onSearchNav(card.id, -1)}
        @search-next=${() => this.onSearchNav(card.id, 1)}
        @search-close=${() => this.toggleSearch(card.id)}
      ></card-search-bar>
    `;
  }

  private renderMinimizeButton(card: PinCard) {
    const minimized = this.minimizedCards.has(card.id);
    return html`
      <button
        class="header-btn minimize"
        title=${minimized ? "Expand card" : "Minimize card"}
        aria-label=${minimized ? "Expand card" : "Minimize card"}
        aria-expanded=${minimized ? "false" : "true"}
        @click=${() => this.toggleMinimize(card.id)}
      >
        ${minimized
          ? html`<svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polyline points="18 15 12 9 6 15" />
            </svg>`
          : html`<svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>`}
      </button>
    `;
  }

  private renderCard(card: PinCard) {
    const minimized = this.minimizedCards.has(card.id);
    return html`
      <div
        class="card"
        @dragover=${this.onDragOver}
        @dragenter=${this.onDragEnter}
        @dragleave=${this.onDragLeave}
        @drop=${(ev: DragEvent) => this.onDrop(card.id, ev)}
      >
        <div
          class="card-header"
          draggable="true"
          @dragstart=${(ev: DragEvent) => this.onDragStart(card.id, ev)}
          @dragend=${this.onDragEnd}
        >
          <button
            class="header-btn copy ${this.copiedCards.has(card.id) ? "copied" : ""}"
            title=${this.copiedCards.has(card.id) ? "Copied!" : "Copy content"}
            @click=${(ev: Event) => {
              ev.stopPropagation();
              this.copyCard(card);
            }}
          >
            ${this.copiedCards.has(card.id)
              ? html`<svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>`
              : html`<svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                </svg>`}
          </button>
          <span class="card-title" title=${card.title}>${card.title}</span>
          <span class="timestamp" title=${new Date(card.timestamp).toLocaleString()}
            >${formatTimeAgo(card.timestamp)}</span
          >
          ${minimized
            ? nothing
            : html`<button
                class="header-btn search"
                title="Search"
                @click=${() => this.toggleSearch(card.id)}
              >
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
              </button>`}
          ${minimized ? nothing : this.renderRerunButton(card)}
          ${minimized ? nothing : this.renderAutoRefreshButton(card)}
          ${this.renderMinimizeButton(card)}
          <button class="header-btn close" title="Close" @click=${() => this.close(card.id)}>
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
        ${minimized
          ? nothing
          : html`
              ${this.renderSearchBar(card)} ${this.renderToolStrip(card)}
              <div
                class="card-body ${card.type === "graph" ? "no-scroll" : ""}"
                data-card-id=${card.id}
                style="height: ${card.height ?? DetailPane.DEFAULT_CARD_HEIGHT}px"
              >
                ${card.loading
                  ? html`<div class="card-loading">
                      <span class="card-loading-dot"></span>
                      <span class="card-loading-dot"></span>
                      <span class="card-loading-dot"></span>
                      <span>Preparing&hellip;</span>
                    </div>`
                  : card.type === "graph"
                    ? html`<chart-card .content=${card.content}></chart-card>`
                    : card.type === "text"
                      ? html`<text-renderer .content=${card.content}></text-renderer>`
                      : html`<markdown-renderer .content=${card.content}></markdown-renderer>`}
              </div>
              <div
                class="resize-grip"
                @mousedown=${(ev: MouseEvent) => this.onResizeStart(card.id, ev)}
              ></div>
            `}
      </div>
    `;
  }

  render() {
    if (this.cards.length === 0) {
      return html`<div class="placeholder">Pinned results will appear here</div>`;
    }

    return html` <div class="cards">${this.cards.map((c) => this.renderCard(c))}</div> `;
  }
}
