import type { ReactiveController, ReactiveControllerHost } from "lit";
import { appState } from "../state/app-state.js";

export interface HistoryResult {
  handled: boolean;
  text: string;
}

function isCursorOnFirstLine(ta: HTMLTextAreaElement): boolean {
  return !ta.value.substring(0, ta.selectionStart).includes("\n");
}

function isCursorOnLastLine(ta: HTMLTextAreaElement): boolean {
  return !ta.value.substring(ta.selectionEnd).includes("\n");
}

/**
 * Lit reactive controller that provides shell-like arrow-up / arrow-down
 * input history for a textarea.  History entries come from the current
 * chat's user messages (via appState).
 */
export class InputHistory implements ReactiveController {
  private index = -1;
  private draft = "";

  constructor(private host: ReactiveControllerHost) {
    host.addController(this);
  }

  hostConnected() {}
  hostDisconnected() {
    this.reset();
  }

  private entries(): string[] {
    return appState.state.messages
      .filter((m) => m.role === "user")
      .map((m) => m.content)
      .reverse();
  }

  handleKeyDown(
    e: KeyboardEvent,
    textarea: HTMLTextAreaElement,
    currentText: string,
  ): HistoryResult {
    const unchanged: HistoryResult = { handled: false, text: currentText };

    if (e.key === "ArrowUp" && isCursorOnFirstLine(textarea)) {
      const hist = this.entries();
      if (!hist.length) return unchanged;
      if (this.index === -1) this.draft = currentText;
      this.index = Math.min(this.index + 1, hist.length - 1);
      return { handled: true, text: hist[this.index] };
    }

    if (e.key === "ArrowDown" && isCursorOnLastLine(textarea)) {
      if (this.index === -1) return unchanged;
      this.index -= 1;
      const text = this.index === -1 ? this.draft : this.entries()[this.index];
      return { handled: true, text };
    }

    return unchanged;
  }

  reset(): void {
    this.index = -1;
    this.draft = "";
  }
}
