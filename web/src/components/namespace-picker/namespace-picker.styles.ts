import { css } from "lit";

export const namespacePickerStyles = css`
  :host {
    display: inline-flex;
    position: relative;
  }

  /* ── trigger button ── */

  button.trigger {
    display: flex;
    align-items: center;
    gap: 6px;
    height: 36px;
    padding: 0 10px;
    border-radius: var(--radius-sm);
    background: transparent;
    color: var(--text-secondary);
    border: none;
    cursor: pointer;
    font-size: var(--font-size-sm);
    font-family: var(--font-sans);
    white-space: nowrap;
    transition:
      background var(--transition-fast),
      color var(--transition-fast);
  }

  button.trigger:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  button.trigger svg {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
  }

  .trigger-label {
    max-width: 140px;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .caret {
    width: 10px;
    height: 10px;
    flex-shrink: 0;
    transition: transform var(--transition-fast);
  }

  .caret.open {
    transform: rotate(180deg);
  }

  /* ── dropdown panel ── */

  .dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    margin-top: 4px;
    width: 240px;
    background: var(--bg-input);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-sm);
    box-shadow: var(--shadow-md);
    z-index: 200;
    padding: 6px;
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

  /* ── search input ── */

  .search-input {
    width: 100%;
    box-sizing: border-box;
    padding: 6px 8px;
    margin-bottom: 4px;
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-xs);
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: var(--font-size-sm);
    font-family: var(--font-sans);
    outline: none;
  }

  .search-input::placeholder {
    color: var(--text-tertiary);
  }

  .search-input:focus {
    border-color: var(--accent-primary);
  }

  /* ── namespace list ── */

  .ns-list {
    max-height: 260px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1px;
  }

  .ns-item {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 6px 8px;
    border: none;
    border-radius: var(--radius-xs);
    background: transparent;
    color: var(--text-primary);
    font-size: var(--font-size-sm);
    font-family: var(--font-sans);
    cursor: pointer;
    text-align: left;
    transition: background var(--transition-fast);
  }

  .ns-item:hover {
    background: var(--bg-hover);
  }

  .ns-item.active {
    background: var(--bg-tertiary);
    font-weight: var(--font-weight-medium);
  }

  .ns-item .check {
    margin-left: auto;
    font-size: 13px;
    opacity: 0;
  }

  .ns-item.active .check {
    opacity: 1;
  }

  /* ── status messages ── */

  .status {
    padding: 8px;
    font-size: var(--font-size-sm);
    color: var(--text-tertiary);
    text-align: center;
  }
`;
