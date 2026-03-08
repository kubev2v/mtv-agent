import { LitElement, html, css } from "lit";
import { customElement, state } from "lit/decorators.js";
import { appState } from "../state/app-state.js";

@customElement("top-bar")
export class TopBar extends LitElement {
  static styles = css`
    :host {
      display: flex;
      align-items: center;
      height: var(--topbar-height);
      min-height: var(--topbar-height);
      padding: 0 12px;
      background: var(--bg-sidebar);
      border-bottom: none;
      gap: 8px;
    }

    .toggle-btn {
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
      flex-shrink: 0;
    }

    .toggle-btn:hover {
      background: var(--bg-hover);
      color: var(--text-primary);
    }

    .toggle-btn svg {
      width: 18px;
      height: 18px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .hat-icon {
      width: 28px;
      height: 22px;
      flex-shrink: 0;
    }

    .title {
      font-size: var(--font-size-lg);
      font-weight: var(--font-weight-bold);
      color: var(--text-primary);
      white-space: nowrap;
    }

    .spacer {
      flex: 1;
    }
  `;

  @state() private sidebarOpen = appState.state.sidebarOpen;

  private unsubscribe?: () => void;

  connectedCallback() {
    super.connectedCallback();
    this.unsubscribe = appState.subscribe(() => {
      this.sidebarOpen = appState.state.sidebarOpen;
    });
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.unsubscribe?.();
  }

  private toggleSidebar() {
    appState.update({ sidebarOpen: !this.sidebarOpen });
  }

  render() {
    return html`
      <button
        class="toggle-btn"
        @click=${this.toggleSidebar}
        title=${this.sidebarOpen ? "Close sidebar" : "Open sidebar"}
        aria-label=${this.sidebarOpen ? "Close sidebar" : "Open sidebar"}
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>

      <div class="brand">
        <svg class="hat-icon" viewBox="0 0 136 103" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path
            d="m 90.6538,59.2537 c 8.9312,0 21.8512,-1.8412 21.8512,-12.4662 0.029,-0.82 -0.045,-1.64 -0.22,-2.4413 l -5.3175,-23.1 C 105.7363,16.1575 104.6575,13.8525 95.7363,9.39 88.8075,5.85 73.725,0 69.2625,0 65.1075,0 63.9013,5.3575 58.945,5.3575 c -4.7712,0 -8.3112,-4 -12.7737,-4 -4.2825,0 -7.075,2.92 -9.2338,8.9262 0,0 -6,16.9338 -6.7725,19.39 -0.1262,0.4538 -0.18,0.9175 -0.16,1.3863 0,6.5825 25.9175,28.1687 60.6488,28.1687 m 23.2225,-8.125 c 1.235,5.845 1.235,6.46 1.235,7.2313 0,9.995 -11.235,15.5425 -26.01,15.5425 -33.3838,0.02 -62.6275,-19.5413 -62.6275,-32.4713 0,-1.8012 0.3612,-3.5837 1.075,-5.2337 C 15.5413,36.7725 0,38.9162 0,52.6375 c 0,22.475 53.2513,50.175 95.42,50.175 32.3288,0 40.4825,-14.6188 40.4825,-26.1663 0,-9.0825 -7.8512,-19.39 -22.0112,-25.5425"
            fill="var(--hat-color)"
          />
          <path
            d="m 113.8763,51.1037 c 1.235,5.845 1.235,6.46 1.235,7.2313 0,9.995 -11.235,15.5425 -26.01,15.5425 -33.3838,0.02 -62.6275,-19.5413 -62.6275,-32.4713 0,-1.8012 0.3612,-3.5837 1.075,-5.2337 l 2.6162,-6.47 c -0.1212,0.445 -0.175,0.8987 -0.16,1.3575 0,6.5825 25.9175,28.1687 60.6488,28.1687 8.9312,0 21.8512,-1.845 21.8512,-12.47 0.029,-0.8162 -0.045,-1.6362 -0.22,-2.4412 l 1.5913,6.7862 z"
            fill="rgba(0,0,0,0.2)"
          />
        </svg>
        <span class="title">Forklift</span>
      </div>

      <div class="spacer"></div>

      <theme-picker></theme-picker>
    `;
  }
}
