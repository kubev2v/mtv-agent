import { LitElement, html } from "lit";
import { customElement, state } from "lit/decorators.js";
import {
  appState,
  BUILTIN_TOOLS,
  defaultPolicyForTool,
  type ToolPolicy,
} from "../state/app-state.js";
import {
  connectMcpServer,
  disconnectMcpServer,
  getTools,
  type MCPServerInfo,
} from "../services/api-client.js";
import { chipListStyles } from "../styles/shared.js";

@customElement("mcp-manager")
export class McpManager extends LitElement {
  static styles = chipListStyles;

  @state() private servers: MCPServerInfo[] = [];
  @state() private busy = false;

  private unsubscribe?: () => void;

  connectedCallback() {
    super.connectedCallback();
    this.unsubscribe = appState.subscribe(() => {
      this.servers = appState.state.mcpServers;
    });
    this.servers = appState.state.mcpServers;
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.unsubscribe?.();
  }

  private async toggle(server: MCPServerInfo) {
    if (this.busy) return;
    this.busy = true;
    try {
      const result = server.connected
        ? await disconnectMcpServer(server.name)
        : await connectMcpServer(server.name);
      appState.update({
        mcpServers: result.servers,
        toolCount: result.tools,
      });
      const tools = await getTools();
      const allTools = [...tools, ...BUILTIN_TOOLS];
      const oldPolicies = appState.state.toolPolicies;
      const policies: Record<string, ToolPolicy> = {};
      for (const t of allTools) {
        policies[t.name] = oldPolicies[t.name] ?? defaultPolicyForTool(t.name);
      }
      appState.update({ availableTools: allTools, toolPolicies: policies });
    } catch (err) {
      appState.update({ error: (err as Error).message });
    } finally {
      this.busy = false;
    }
  }

  render() {
    if (!this.servers.length) {
      return html`<div class="empty">No MCP servers configured</div>`;
    }
    return html`
      <div class="chips">
        ${this.servers.map(
          (s) => html`
            <button
              class="chip ${s.connected ? "active" : ""}"
              ?disabled=${this.busy}
              @click=${() => this.toggle(s)}
              title=${s.url}
            >
              ${s.connected ? html`<span class="dot"></span>` : ""} ${s.name}
            </button>
          `,
        )}
      </div>
    `;
  }
}
