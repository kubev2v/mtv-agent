import { LitElement, html, css } from "lit";
import { customElement, state } from "lit/decorators.js";
import { appState, type PinCard } from "../state/app-state.js";
import { callTool } from "../services/api-client.js";
import {
  identify,
  parseResult,
  cardId,
  type CardDisplayType,
} from "../utils/tool-registry/index.js";

interface TablePanelDef {
  label: string;
  kind: "table";
  toolName: string;
  buildArgs: () => Record<string, unknown>;
}

interface QueryGraphPanelDef {
  label: string;
  kind: "query-graph";
  buildQueries: () => { queries: string[]; names: string[] };
  start: string;
  step: string;
}

type PanelDef = TablePanelDef | QueryGraphPanelDef;

function nsFlags(): Record<string, unknown> {
  const ctx = appState.state.context;
  if (ctx["namespace"]) return { namespace: ctx["namespace"] };
  return { all_namespaces: true };
}

function ctxNamespace(): string | undefined {
  return appState.state.context["namespace"] || undefined;
}

function buildMetricItems(start: string, step: string): QueryGraphPanelDef[] {
  return [
    {
      label: "Network RX/TX",
      kind: "query-graph",
      buildQueries: () => {
        const ns = ctxNamespace();
        const group = ns ? "pod" : "namespace";
        const filter = ns ? `{namespace="${ns}"}` : "";
        return {
          queries: [
            `topk(10, sum by (${group})(rate(container_network_receive_bytes_total${filter}[5m])))`,
            `topk(10, sum by (${group})(rate(container_network_transmit_bytes_total${filter}[5m])))`,
          ],
          names: ["rx", "tx"],
        };
      },
      start,
      step,
    },
    {
      label: "CPU / Memory",
      kind: "query-graph",
      buildQueries: () => {
        const ns = ctxNamespace();
        const group = ns ? "pod" : "namespace";
        const filter = ns ? `{namespace="${ns}"}` : "";
        return {
          queries: [
            `topk(10, sum by (${group})(rate(container_cpu_usage_seconds_total${filter}[5m])))`,
            `topk(10, sum by (${group})(container_memory_working_set_bytes${filter}))`,
          ],
          names: ["cpu", "memory"],
        };
      },
      start,
      step,
    },
    {
      label: "Network Total",
      kind: "query-graph",
      buildQueries: () => {
        const ns = ctxNamespace();
        const scope = ns ?? "all";
        const filter = ns ? `{namespace="${ns}"}` : "";
        return {
          queries: [
            `sum(rate(container_network_receive_bytes_total${filter}[5m]))`,
            `sum(rate(container_network_transmit_bytes_total${filter}[5m]))`,
          ],
          names: [`total rx (${scope})`, `total tx (${scope})`],
        };
      },
      start,
      step,
    },
    {
      label: "CPU / Mem Total",
      kind: "query-graph",
      buildQueries: () => {
        const ns = ctxNamespace();
        const scope = ns ?? "all";
        const filter = ns ? `{namespace="${ns}"}` : "";
        return {
          queries: [
            `sum(rate(container_cpu_usage_seconds_total${filter}[5m]))`,
            `sum(container_memory_working_set_bytes${filter})`,
          ],
          names: [`total cpu (${scope})`, `total mem (${scope})`],
        };
      },
      start,
      step,
    },
  ];
}

const SECTIONS: { heading: string; items: PanelDef[] }[] = [
  {
    heading: "Resources",
    items: [
      {
        label: "Health",
        kind: "table",
        toolName: "mtv_read",
        buildArgs: () => ({ command: "health" }),
      },
      {
        label: "Providers",
        kind: "table",
        toolName: "mtv_read",
        buildArgs: () => ({
          command: "get provider",
          flags: { ...nsFlags(), output: "markdown" },
        }),
      },
      {
        label: "Plans",
        kind: "table",
        toolName: "mtv_read",
        buildArgs: () => ({
          command: "get plan",
          flags: { ...nsFlags(), output: "markdown" },
        }),
      },
      {
        label: "Plans (VMs)",
        kind: "table",
        toolName: "mtv_read",
        buildArgs: () => ({
          command: "get plan",
          flags: { ...nsFlags(), "vms-table": true, output: "markdown" },
        }),
      },
    ],
  },
  {
    heading: "Metrics (2 h)",
    items: [...buildMetricItems("-2h", "60s")],
  },
  {
    heading: "Metrics (24 h)",
    items: [...buildMetricItems("-24h", "300s")],
  },
];

@customElement("quick-panels")
export class QuickPanels extends LitElement {
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
      min-width: 200px;
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

    .section-label {
      padding: 6px 10px 2px;
      font-size: var(--font-size-xs);
      font-weight: var(--font-weight-bold);
      color: var(--text-tertiary);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      user-select: none;
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

    .dropdown button .icon {
      width: 14px;
      height: 14px;
      flex-shrink: 0;
      color: var(--text-tertiary);
    }

    .separator {
      height: 1px;
      margin: 4px 0;
      background: var(--border-secondary);
    }
  `;

  @state() private open = false;

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

  private async openPanel(def: PanelDef) {
    this.open = false;

    if (def.kind === "table") {
      await this.openTablePanel(def);
    } else {
      await this.openQueryGraphPanel(def);
    }
  }

  private async openTablePanel(def: TablePanelDef) {
    const args = def.buildArgs();
    const id = cardId(def.toolName, args);
    if (appState.hasCard(id)) return;

    const card: PinCard = {
      id,
      title: `${def.toolName}: ${def.label}`,
      content: "",
      timestamp: Date.now(),
      toolName: def.toolName,
      toolArgs: args,
      loading: true,
    };

    appState.addCard(card);
    if (!appState.state.detailPaneOpen) {
      appState.update({ detailPaneOpen: true });
    }

    try {
      const resp = await callTool(def.toolName, args);
      const identification = identify(def.toolName, args);
      const parsed = parseResult(identification, resp.result);
      appState.updateCard(id, {
        content: parsed.content,
        type: parsed.displayType,
        loading: false,
      });
    } catch (err) {
      appState.updateCard(id, {
        content: `**Error:** ${(err as Error).message}`,
        loading: false,
      });
    }
  }

  /** Single query_range call with multiple PromQL queries -> one line per series. */
  private async openQueryGraphPanel(def: QueryGraphPanelDef) {
    const { queries, names } = def.buildQueries();
    const ns = ctxNamespace();
    const args: Record<string, unknown> = {
      command: "query_range",
      flags: {
        query: queries,
        name: names,
        start: def.start,
        step: def.step,
        output: "tsv",
      },
    };
    const id = `graph-${cardId("metrics_read", args)}`;
    if (appState.hasCard(id)) return;

    const suffix = def.start.replace("-", "");
    const title = ns ? `${def.label} [${ns}] (${suffix})` : `${def.label} (${suffix})`;

    const card: PinCard = {
      id,
      title,
      content: "",
      timestamp: Date.now(),
      toolName: "metrics_read",
      toolArgs: args,
      type: "graph" as CardDisplayType,
      loading: true,
    };

    appState.addCard(card);
    if (!appState.state.detailPaneOpen) {
      appState.update({ detailPaneOpen: true });
    }

    try {
      const resp = await callTool("metrics_read", args);
      appState.updateCard(id, { content: resp.result, loading: false });
    } catch (err) {
      appState.updateCard(id, {
        content: `**Error:** ${(err as Error).message}`,
        loading: false,
      });
    }
  }

  private tableIcon = html`<svg
    class="icon"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <rect x="3" y="3" width="18" height="18" rx="2" />
    <line x1="3" y1="9" x2="21" y2="9" />
    <line x1="3" y1="15" x2="21" y2="15" />
    <line x1="9" y1="3" x2="9" y2="21" />
  </svg>`;

  private chartIcon = html`<svg
    class="icon"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
  </svg>`;

  render() {
    return html`
      <button
        class="trigger"
        @click=${this.toggleDropdown}
        title="Quick panels"
        aria-label="Quick panels"
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
          <rect x="3" y="3" width="7" height="7" rx="1" />
          <rect x="14" y="3" width="7" height="7" rx="1" />
          <rect x="3" y="14" width="7" height="7" rx="1" />
          <rect x="14" y="14" width="7" height="7" rx="1" />
        </svg>
      </button>

      <div class="dropdown ${this.open ? "open" : ""}">
        ${SECTIONS.map(
          (section, si) => html`
            ${si > 0 ? html`<div class="separator"></div>` : ""}
            <div class="section-label">${section.heading}</div>
            ${section.items.map(
              (item) => html`
                <button @click=${() => this.openPanel(item)}>
                  ${item.kind === "table" ? this.tableIcon : this.chartIcon} ${item.label}
                </button>
              `,
            )}
          `,
        )}
      </div>
    `;
  }
}
