import { LitElement, html, css } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import zoomPlugin from "chartjs-plugin-zoom";
import { parseTimeSeriesData, type TimeSeriesData } from "../utils/tool-registry/index.js";

Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend,
  Filler,
  zoomPlugin,
);

const PALETTE = [
  "#3b82f6",
  "#ef4444",
  "#10b981",
  "#f59e0b",
  "#8b5cf6",
  "#ec4899",
  "#06b6d4",
  "#84cc16",
  "#f97316",
  "#6366f1",
];

type ZoomPreset = { label: string; ms: number | null };

const ZOOM_PRESETS: ZoomPreset[] = [
  { label: "5m", ms: 5 * 60_000 },
  { label: "15m", ms: 15 * 60_000 },
  { label: "1h", ms: 60 * 60_000 },
  { label: "6h", ms: 6 * 60 * 60_000 },
  { label: "All", ms: null },
];

@customElement("chart-card")
export class ChartCard extends LitElement {
  static styles = css`
    :host {
      display: flex;
      flex-direction: column;
      flex: 1;
      min-height: 0;
      user-select: none;
    }

    .toolbar {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 2px 2px;
      flex-wrap: wrap;
    }

    .legend-area {
      display: flex;
      align-items: center;
      gap: 4px;
      flex-wrap: wrap;
      flex: 1;
      min-width: 0;
    }

    .legend-item {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2px 6px;
      border-radius: var(--radius-xs, 4px);
      cursor: pointer;
      font-size: 11px;
      font-family: var(--font-sans, sans-serif);
      color: var(--text-secondary, #999);
      background: transparent;
      border: 1px solid transparent;
      transition:
        opacity 0.15s,
        background 0.15s;
      user-select: none;
    }

    .legend-item:hover {
      background: var(--bg-hover, rgba(128, 128, 128, 0.1));
    }

    .legend-item.hidden {
      opacity: 0.4;
    }

    .legend-item.hidden .legend-swatch {
      background: var(--text-tertiary, #666) !important;
    }

    .legend-swatch {
      width: 10px;
      height: 3px;
      border-radius: 1px;
      flex-shrink: 0;
    }

    .zoom-controls {
      display: flex;
      align-items: center;
      gap: 2px;
      flex-shrink: 0;
    }

    .zoom-btn {
      padding: 2px 7px;
      border-radius: var(--radius-xs, 4px);
      cursor: pointer;
      font-size: 10px;
      font-family: var(--font-mono, monospace);
      color: var(--text-secondary, #999);
      background: transparent;
      border: 1px solid var(--border-secondary, rgba(128, 128, 128, 0.15));
      transition:
        background 0.15s,
        color 0.15s,
        border-color 0.15s;
      user-select: none;
      line-height: 1.5;
    }

    .zoom-btn:hover {
      background: var(--bg-hover, rgba(128, 128, 128, 0.1));
      color: var(--text-primary, #ccc);
    }

    .zoom-btn.active {
      background: var(--accent-primary, #3b82f6);
      color: var(--text-inverse, #fff);
      border-color: var(--accent-primary, #3b82f6);
    }

    .zoom-hint {
      font-size: 10px;
      color: var(--text-tertiary, #666);
      font-family: var(--font-sans, sans-serif);
      padding: 0 4px;
    }

    .chart-wrap {
      position: relative;
      width: 100%;
      flex: 1;
      min-height: 0;
      touch-action: none;
    }

    .fallback {
      padding: 16px;
      color: var(--text-tertiary);
      font-size: var(--font-size-sm);
      font-family: var(--font-mono);
      text-align: center;
    }
  `;

  @property({ type: String }) content = "";

  @state() private hiddenSeries = new Set<number>();
  @state() private activeZoom: string = "All";
  @state() private error = false;

  private chart: Chart | null = null;
  private buildPending = false;
  private _cachedContent = "";
  private _cachedParsed: TimeSeriesData | null = null;
  private _boundWrap: HTMLElement | null = null;

  disconnectedCallback() {
    super.disconnectedCallback();
    this.destroyChart();
    this.detachWrapListeners();
  }

  private destroyChart() {
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
  }

  private attachWrapListeners() {
    this.detachWrapListeners();
    const wrap = this.shadowRoot?.querySelector(".chart-wrap") as HTMLElement | null;
    if (!wrap) return;
    this._boundWrap = wrap;
    wrap.addEventListener("wheel", this.onWrapWheel, { passive: false });
  }

  private detachWrapListeners() {
    if (!this._boundWrap) return;
    this._boundWrap.removeEventListener("wheel", this.onWrapWheel);
    this._boundWrap = null;
  }

  private onWrapWheel = (ev: WheelEvent) => {
    if (this.chart) {
      ev.preventDefault();
      ev.stopPropagation();
    }
  };

  protected updated(changed: Map<string, unknown>) {
    if (changed.has("content")) {
      this.hiddenSeries = new Set();
      this.activeZoom = "All";
      this.error = false;
      this._cachedContent = this.content;
      this._cachedParsed = parseTimeSeriesData(this.content);
      this.scheduleBuild();
    }
  }

  private get parsed(): TimeSeriesData | null {
    if (this._cachedContent !== this.content) {
      this._cachedContent = this.content;
      this._cachedParsed = parseTimeSeriesData(this.content);
    }
    return this._cachedParsed;
  }

  private scheduleBuild() {
    if (this.buildPending) return;
    this.buildPending = true;
    setTimeout(() => {
      this.buildPending = false;
      this.buildChart();
    }, 0);
  }

  private getTimeRange(): { min: number; max: number } | null {
    const parsed = this.parsed;
    if (!parsed) return null;
    let min = Infinity,
      max = -Infinity;
    for (const s of parsed.series) {
      for (const pt of s.data) {
        if (pt.x < min) min = pt.x;
        if (pt.x > max) max = pt.x;
      }
    }
    return isFinite(min) && isFinite(max) ? { min, max } : null;
  }

  private buildChart() {
    this.destroyChart();

    const parsed = this.parsed;
    if (!parsed || parsed.series.length === 0) {
      this.error = true;
      return;
    }

    const canvas = this.shadowRoot?.querySelector("canvas") as HTMLCanvasElement | null;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const textColor = getComputedStyle(this).getPropertyValue("--text-secondary").trim() || "#999";
    const gridColor =
      getComputedStyle(this).getPropertyValue("--border-secondary").trim() ||
      "rgba(128,128,128,0.2)";

    this.chart = new Chart(ctx, {
      type: "line",
      data: {
        datasets: parsed.series.map((s, i) => ({
          label: s.name,
          data: s.data,
          borderColor: PALETTE[i % PALETTE.length],
          backgroundColor: PALETTE[i % PALETTE.length] + "22",
          borderWidth: 1.5,
          pointRadius: 0,
          pointHitRadius: 6,
          tension: 0.25,
          fill: false,
          hidden: this.hiddenSeries.has(i),
        })),
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 300 },
        interaction: {
          mode: "index",
          intersect: false,
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: (items) => {
                if (!items.length) return "";
                const raw = items[0].parsed.x as number | null;
                return raw != null ? new Date(raw).toLocaleString() : "";
              },
            },
          },
          zoom: {
            pan: {
              enabled: false,
            },
            zoom: {
              wheel: {
                enabled: true,
              },
              drag: {
                enabled: true,
                backgroundColor: "rgba(59,130,246,0.12)",
                borderColor: "rgba(59,130,246,0.4)",
                borderWidth: 1,
              },
              mode: "x",
              onZoomComplete: () => {
                this.activeZoom = "";
                this.requestUpdate();
              },
            },
          },
        },
        scales: {
          x: {
            type: "linear",
            ticks: {
              color: textColor,
              font: { size: 10 },
              maxTicksLimit: 8,
              callback: (val) => {
                const d = new Date(val as number);
                return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
              },
            },
            grid: { color: gridColor },
          },
          y: {
            ticks: {
              color: textColor,
              font: { size: 10 },
              maxTicksLimit: 6,
            },
            grid: { color: gridColor },
          },
        },
      },
    });

    this.attachWrapListeners();
  }

  private toggleSeries(index: number) {
    const next = new Set(this.hiddenSeries);
    if (next.has(index)) next.delete(index);
    else next.add(index);
    this.hiddenSeries = next;

    if (this.chart) {
      const meta = this.chart.getDatasetMeta(index);
      meta.hidden = next.has(index);
      this.chart.update("none");
    }
  }

  private applyZoom(preset: ZoomPreset) {
    this.activeZoom = preset.label;
    if (!this.chart) return;

    if (preset.ms === null) {
      this.chart.resetZoom("default");
      return;
    }

    const range = this.getTimeRange();
    if (!range) return;

    const end = range.max;
    const start = Math.max(range.min, end - preset.ms);

    this.chart.zoomScale("x", { min: start, max: end }, "default");
  }

  private renderLegend(parsed: TimeSeriesData) {
    return parsed.series.map(
      (s, i) => html`
        <button
          class="legend-item ${this.hiddenSeries.has(i) ? "hidden" : ""}"
          @click=${() => this.toggleSeries(i)}
          title="${this.hiddenSeries.has(i) ? "Show" : "Hide"} ${s.name}"
        >
          <span class="legend-swatch" style="background:${PALETTE[i % PALETTE.length]}"></span>
          ${s.name}
        </button>
      `,
    );
  }

  private renderZoomControls() {
    return html`
      <span class="zoom-hint">Zoom:</span>
      ${ZOOM_PRESETS.map(
        (p) => html`
          <button
            class="zoom-btn ${this.activeZoom === p.label ? "active" : ""}"
            @click=${() => this.applyZoom(p)}
          >
            ${p.label}
          </button>
        `,
      )}
    `;
  }

  render() {
    const parsed = this.parsed;
    if (this.error || !parsed) {
      return html`<div class="fallback">Unable to parse time-series data</div>`;
    }
    return html`
      <div class="toolbar">
        <div class="legend-area">${this.renderLegend(parsed)}</div>
        <div class="zoom-controls">${this.renderZoomControls()}</div>
      </div>
      <div class="chart-wrap">
        <canvas></canvas>
      </div>
    `;
  }
}
