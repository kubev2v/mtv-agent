import type { ReactiveController, ReactiveControllerHost } from "lit";

const TICK_MS = 5_000;
const hosts = new Set<ReactiveControllerHost>();
let timer: ReturnType<typeof setInterval> | null = null;

function start() {
  if (timer) return;
  timer = setInterval(() => {
    for (const h of hosts) h.requestUpdate();
  }, TICK_MS);
}

function stop() {
  if (!timer) return;
  clearInterval(timer);
  timer = null;
}

/**
 * Lit reactive controller that triggers a host re-render every 5 seconds.
 * Uses a single shared global interval (ref-counted) so that multiple
 * hosts don't each spin up their own timer.
 */
export class TimeTicker implements ReactiveController {
  constructor(private host: ReactiveControllerHost) {
    host.addController(this);
  }

  hostConnected() {
    hosts.add(this.host);
    start();
  }

  hostDisconnected() {
    hosts.delete(this.host);
    if (!hosts.size) stop();
  }
}
