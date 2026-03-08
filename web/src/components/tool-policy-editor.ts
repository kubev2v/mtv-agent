import { LitElement, html, css, nothing } from "lit";
import { customElement, state } from "lit/decorators.js";
import { appState, defaultPolicyForTool, type ToolPolicy } from "../state/app-state.js";
import type { ToolInfo } from "../services/api-client.js";

const POLICY_OPTIONS: { value: ToolPolicy; label: string }[] = [
  { value: "auto-accept", label: "Accept" },
  { value: "ask", label: "Ask" },
  { value: "auto-reject", label: "Reject" },
];

@customElement("tool-policy-editor")
export class ToolPolicyEditor extends LitElement {
  static styles = css`
    :host {
      display: block;
    }

    .bulk-actions {
      display: flex;
      gap: 6px;
      margin-bottom: 8px;
    }

    .bulk-btn {
      padding: 3px 10px;
      border-radius: var(--radius-full);
      font-size: var(--font-size-xs);
      font-weight: var(--font-weight-medium);
      border: 1px solid var(--border-primary);
      background: var(--bg-primary);
      color: var(--text-secondary);
      cursor: pointer;
      transition: all var(--transition-fast);
    }

    .bulk-btn:hover {
      background: var(--bg-hover);
      color: var(--text-primary);
    }

    .bulk-btn.active {
      background: var(--accent-primary);
      color: var(--text-inverse);
      border-color: var(--accent-primary);
    }

    .tool-list {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .tool-row {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 4px 0;
    }

    .tool-name-wrap {
      flex: 1;
      min-width: 0;
      position: relative;
    }

    .tool-name {
      font-size: var(--font-size-xs);
      color: var(--text-primary);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      cursor: default;
    }

    .tool-tip {
      display: none;
      position: absolute;
      bottom: calc(100% + 6px);
      left: 0;
      z-index: 100;
      max-width: 280px;
      padding: 6px 10px;
      border-radius: var(--radius-sm);
      background: var(--bg-tertiary);
      border: 1px solid var(--border-primary);
      color: var(--text-secondary);
      font-size: var(--font-size-xs);
      line-height: 1.4;
      white-space: normal;
      word-wrap: break-word;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      pointer-events: none;
    }

    .tool-name-wrap:hover .tool-tip {
      display: block;
    }

    .policy-toggle {
      display: flex;
      border-radius: var(--radius-full);
      border: 1px solid var(--border-primary);
      overflow: hidden;
      flex-shrink: 0;
    }

    .policy-btn {
      padding: 2px 8px;
      font-size: 10px;
      font-weight: var(--font-weight-medium);
      border: none;
      background: var(--bg-primary);
      color: var(--text-tertiary);
      cursor: pointer;
      transition: all var(--transition-fast);
      line-height: 1.4;
    }

    .policy-btn:not(:last-child) {
      border-right: 1px solid var(--border-primary);
    }

    .policy-btn:hover {
      background: var(--bg-hover);
      color: var(--text-primary);
    }

    .policy-btn.selected-auto-accept {
      background: var(--accent-success);
      color: white;
    }

    .policy-btn.selected-ask {
      background: var(--accent-info);
      color: white;
    }

    .policy-btn.selected-auto-reject {
      background: var(--accent-danger);
      color: white;
    }

    .empty {
      font-size: var(--font-size-sm);
      color: var(--text-tertiary);
      padding: 4px 0;
    }
  `;

  @state() private tools: ToolInfo[] = [];
  @state() private policies: Record<string, ToolPolicy> = {};

  private unsubscribe?: () => void;

  connectedCallback() {
    super.connectedCallback();
    this.unsubscribe = appState.subscribe(() => {
      this.tools = appState.state.availableTools;
      this.policies = appState.state.toolPolicies;
    });
    this.tools = appState.state.availableTools;
    this.policies = appState.state.toolPolicies;
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.unsubscribe?.();
  }

  private setPolicy(toolName: string, policy: ToolPolicy) {
    appState.setToolPolicy(toolName, policy);
  }

  private setAll(policy: ToolPolicy) {
    appState.setAllToolPolicies(policy);
  }

  private get allPolicy(): ToolPolicy | null {
    const vals = Object.values(this.policies);
    if (vals.length === 0) return null;
    const first = vals[0];
    return vals.every((v) => v === first) ? first : null;
  }

  render() {
    if (!this.tools.length) {
      return html`<div class="empty">No tools available</div>`;
    }

    const uniformPolicy = this.allPolicy;

    return html`
      <div class="bulk-actions">
        ${POLICY_OPTIONS.map(
          (opt) => html`
            <button
              class="bulk-btn ${uniformPolicy === opt.value ? "active" : ""}"
              @click=${() => this.setAll(opt.value)}
            >
              All ${opt.label}
            </button>
          `,
        )}
      </div>
      <div class="tool-list">
        ${this.tools.map((tool) => {
          const current = this.policies[tool.name] ?? defaultPolicyForTool(tool.name);
          return html`
            <div class="tool-row">
              <div class="tool-name-wrap">
                <div class="tool-name">${tool.name}</div>
                ${tool.description
                  ? html`<div class="tool-tip">${tool.description}</div>`
                  : nothing}
              </div>
              <div class="policy-toggle">
                ${POLICY_OPTIONS.map(
                  (opt) => html`
                    <button
                      class="policy-btn ${current === opt.value ? `selected-${opt.value}` : ""}"
                      @click=${() => this.setPolicy(tool.name, opt.value)}
                      title=${opt.label}
                    >
                      ${opt.label}
                    </button>
                  `,
                )}
              </div>
            </div>
          `;
        })}
      </div>
    `;
  }
}
