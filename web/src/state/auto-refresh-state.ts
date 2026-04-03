const STORAGE_KEY_INTERVAL = "auto-refresh-interval";

const DEFAULT_INTERVAL_SEC = 30;
const MIN_INTERVAL_SEC = 5;
const MAX_INTERVAL_SEC = 3600;

type Listener = () => void;

class AutoRefreshManager {
  private _intervalSec: number;
  private listeners = new Set<Listener>();

  constructor() {
    this._intervalSec = this.loadInterval();
  }

  get intervalSec(): number {
    return this._intervalSec;
  }

  setInterval(sec: number): void {
    const clamped = Math.max(MIN_INTERVAL_SEC, Math.min(MAX_INTERVAL_SEC, Math.round(sec)));
    if (clamped === this._intervalSec) return;
    this._intervalSec = clamped;
    this.saveInterval();
    this.notify();
  }

  subscribe(fn: Listener): () => void {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }

  private notify(): void {
    for (const fn of this.listeners) fn();
  }

  private loadInterval(): number {
    try {
      const raw = localStorage.getItem(STORAGE_KEY_INTERVAL);
      if (raw !== null) {
        const parsed = Number(raw);
        if (!Number.isNaN(parsed) && parsed >= MIN_INTERVAL_SEC && parsed <= MAX_INTERVAL_SEC) {
          return parsed;
        }
      }
    } catch {
      // localStorage may be unavailable
    }
    return DEFAULT_INTERVAL_SEC;
  }

  private saveInterval(): void {
    try {
      localStorage.setItem(STORAGE_KEY_INTERVAL, String(this._intervalSec));
    } catch {
      // ignore
    }
  }
}

export const autoRefreshManager = new AutoRefreshManager();
