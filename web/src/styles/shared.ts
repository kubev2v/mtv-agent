import { css } from "lit";

/** Toggle-chip list used by skill-selector and mcp-manager. */
export const chipListStyles = css`
  :host {
    display: block;
  }

  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: var(--radius-full);
    font-size: var(--font-size-xs);
    border: 1px solid var(--border-primary);
    background: var(--bg-primary);
    color: var(--text-secondary);
    cursor: pointer;
    transition: all var(--transition-fast);
    white-space: nowrap;
  }

  .chip:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .chip.active {
    background: var(--accent-primary);
    color: var(--text-inverse);
    border-color: var(--accent-primary);
  }

  .chip.active:hover {
    background: var(--accent-hover);
  }

  .chip:disabled {
    opacity: 0.5;
    cursor: wait;
  }

  .chip .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
    opacity: 0.6;
  }

  .empty {
    font-size: var(--font-size-sm);
    color: var(--text-tertiary);
    padding: 4px 0;
  }
`;
