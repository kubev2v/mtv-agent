export interface Theme {
  [key: string]: string;
}

const sharedLayout: Theme = {
  "--radius-xs": "var(--rh-border-radius-default, 3px)",
  "--radius-sm": "8px",
  "--radius-md": "12px",
  "--radius-lg": "16px",
  "--radius-xl": "24px",
  "--radius-full": "var(--rh-border-radius-pill, 64px)",

  "--sidebar-width": "280px",
  "--topbar-height": "48px",
  "--chat-max-width": "768px",
  "--detail-pane-width": "340px",
  "--detail-pane-min-width": "200px",
  "--chat-area-min-width": "320px",
  "--transition-fast": "150ms ease",
  "--transition-normal": "250ms ease",

  "--font-size-xs": "var(--rh-font-size-body-text-xs, 0.75rem)",
  "--font-size-sm": "var(--rh-font-size-body-text-sm, 0.875rem)",
  "--font-size-base": "var(--rh-font-size-body-text-md, 1rem)",
  "--font-size-lg": "var(--rh-font-size-body-text-lg, 1.125rem)",
  "--font-size-xl": "var(--rh-font-size-body-text-2xl, 1.5rem)",
  "--font-weight-normal": "var(--rh-font-weight-body-text-regular, 400)",
  "--font-weight-medium": "var(--rh-font-weight-body-text-medium, 500)",
  "--font-weight-bold": "var(--rh-font-weight-heading-bold, 700)",
  "--line-height": "var(--rh-line-height-body-text, 1.5)",
};

export const lightTheme: Theme = {
  ...sharedLayout,

  "--bg-primary": "#F8F6FB",
  "--bg-secondary": "#F0ECF5",
  "--bg-tertiary": "#E4DEF0",
  "--bg-user-bubble": "#DCE8DC",
  "--bg-assistant": "transparent",
  "--bg-sidebar": "#F2F5F2",
  "--bg-input": "#FFFFFF",
  "--bg-code": "#F3EEF8",
  "--bg-hover": "rgba(90, 70, 140, 0.06)",
  "--bg-tool": "#F0ECF5",
  "--bg-tool-header": "#E4DEF0",

  "--text-primary": "#2D2B3D",
  "--text-secondary": "#6B6880",
  "--text-tertiary": "#9895AA",
  "--text-inverse": "#FFFFFF",
  "--text-code": "#7C5CBF",

  "--border-primary": "rgba(80, 60, 120, 0.15)",
  "--border-secondary": "rgba(80, 60, 120, 0.08)",

  "--accent-primary": "#5B9EA6",
  "--accent-hover": "#4A8A93",
  "--accent-success": "#6B9F6B",
  "--accent-danger": "#C27070",
  "--accent-warning": "#C4966E",
  "--accent-info": "#7B9EC9",
  "--hat-color": "#E06060",

  "--font-sans": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  "--font-mono": "'SF Mono', 'Fira Code', 'Fira Mono', 'Roboto Mono', monospace",

  "--shadow-sm": "0 1px 2px rgba(60, 40, 100, 0.06)",
  "--shadow-md": "0 2px 8px rgba(60, 40, 100, 0.10)",
  "--shadow-lg": "0 4px 16px rgba(60, 40, 100, 0.14)",
};

export const darkTheme: Theme = {
  ...sharedLayout,

  "--bg-primary": "#1E1B2E",
  "--bg-secondary": "#262340",
  "--bg-tertiary": "#352F54",
  "--bg-user-bubble": "#3A3458",
  "--bg-assistant": "transparent",
  "--bg-sidebar": "#151324",
  "--bg-input": "#262340",
  "--bg-code": "#262340",
  "--bg-hover": "rgba(180, 160, 255, 0.08)",
  "--bg-tool": "#1C1930",
  "--bg-tool-header": "#2E2A48",

  "--text-primary": "#E8E4F0",
  "--text-secondary": "#ACA8C0",
  "--text-tertiary": "#7E7A96",
  "--text-inverse": "#1E1B2E",
  "--text-code": "#E8A8C0",

  "--border-primary": "rgba(200, 180, 255, 0.15)",
  "--border-secondary": "rgba(200, 180, 255, 0.08)",

  "--accent-primary": "#A78BFA",
  "--accent-hover": "#B89FF8",
  "--accent-success": "#86D9A8",
  "--accent-danger": "#F08080",
  "--accent-warning": "#E8C06A",
  "--accent-info": "#88B8E8",
  "--hat-color": "#F07888",

  "--font-sans": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  "--font-mono": "'SF Mono', 'Fira Code', 'Fira Mono', 'Roboto Mono', monospace",

  "--shadow-sm": "0 1px 2px rgba(10, 8, 30, 0.3)",
  "--shadow-md": "0 2px 8px rgba(10, 8, 30, 0.4)",
  "--shadow-lg": "0 4px 16px rgba(10, 8, 30, 0.5)",
};

export const redHatLightTheme: Theme = {
  ...sharedLayout,

  "--bg-primary": "#e6e6e6",
  "--bg-secondary": "#f5f5f5",
  "--bg-tertiary": "var(--rh-color-surface-light, #e0e0e0)",
  "--bg-user-bubble": "var(--rh-color-gray-20, #e0e0e0)",
  "--bg-assistant": "transparent",
  "--bg-sidebar": "var(--rh-color-gray-10, #f5f5f5)",
  "--bg-input": "var(--rh-color-surface-lightest, #ffffff)",
  "--bg-code": "var(--rh-color-surface-lighter, #f2f2f2)",
  "--bg-hover": "var(--rh-color-surface-lighter, rgba(21, 21, 21, 0.04))",
  "--bg-tool": "var(--rh-color-gray-10, #f2f2f2)",
  "--bg-tool-header": "var(--rh-color-gray-20, #e0e0e0)",

  "--text-primary": "var(--rh-color-text-primary-on-light, #151515)",
  "--text-secondary": "var(--rh-color-text-secondary-on-light, #4d4d4d)",
  "--text-tertiary": "var(--rh-color-gray-50, #707070)",
  "--text-inverse": "var(--rh-color-text-primary-on-dark, #ffffff)",
  "--text-code": "var(--rh-color-blue-70, #003366)",

  "--border-primary": "var(--rh-color-border-subtle-on-light, #c7c7c7)",
  "--border-secondary": "var(--rh-color-border-subtle-on-light, rgba(21, 21, 21, 0.10))",

  "--accent-primary": "var(--rh-color-interactive-blue-darker, #0066cc)",
  "--accent-hover": "var(--rh-color-interactive-blue-darkest, #003366)",
  "--accent-success": "var(--rh-color-status-success-on-light, #3d7317)",
  "--accent-danger": "var(--rh-color-status-danger-on-light, #b1380b)",
  "--accent-warning": "var(--rh-color-status-warning-on-light, #dca614)",
  "--accent-info": "var(--rh-color-interactive-blue-darker, #0066cc)",
  "--hat-color": "var(--rh-color-brand-red-on-light, #ee0000)",

  "--font-sans": "var(--rh-font-family-body-text, 'Red Hat Text', 'Red Hat Display', sans-serif)",
  "--font-mono": "var(--rh-font-family-code, 'Red Hat Mono', 'Courier New', monospace)",

  "--shadow-sm": "var(--rh-box-shadow-sm, 0 1px 2px rgba(21, 21, 21, 0.1))",
  "--shadow-md": "var(--rh-box-shadow-md, 0 2px 4px rgba(21, 21, 21, 0.12))",
  "--shadow-lg": "var(--rh-box-shadow-lg, 0 4px 8px rgba(21, 21, 21, 0.15))",
};

export const redHatDarkTheme: Theme = {
  ...sharedLayout,

  "--bg-primary": "#252525",
  "--bg-secondary": "#2a2a2a",
  "--bg-tertiary": "var(--rh-color-gray-60, #4d4d4d)",
  "--bg-user-bubble": "var(--rh-color-gray-70, #3d3d3d)",
  "--bg-assistant": "transparent",
  "--bg-sidebar": "var(--rh-color-surface-darkest, #151515)",
  "--bg-input": "#2a2a2a",
  "--bg-code": "var(--rh-color-gray-70, #333333)",
  "--bg-hover": "var(--rh-color-surface-darker, rgba(255, 255, 255, 0.06))",
  "--bg-tool": "var(--rh-color-surface-darker, #1f1f1f)",
  "--bg-tool-header": "var(--rh-color-surface-dark, #383838)",

  "--text-primary": "var(--rh-color-text-primary-on-dark, #ffffff)",
  "--text-secondary": "var(--rh-color-text-secondary-on-dark, #c7c7c7)",
  "--text-tertiary": "#a0a0a0",
  "--text-inverse": "var(--rh-color-text-primary-on-light, #151515)",
  "--text-code": "var(--rh-color-red-orange-30, #f89b78)",

  "--border-primary": "var(--rh-color-border-subtle-on-dark, #707070)",
  "--border-secondary": "var(--rh-color-border-subtle-on-dark, rgba(242, 242, 242, 0.08))",

  "--accent-primary": "var(--rh-color-interactive-blue-lighter, #92c5f9)",
  "--accent-hover": "var(--rh-color-interactive-blue-lightest, #b9dafc)",
  "--accent-success": "var(--rh-color-status-success-on-dark, #87bb62)",
  "--accent-danger": "var(--rh-color-status-danger-on-dark, #f0561d)",
  "--accent-warning": "var(--rh-color-status-warning-on-dark, #ffcc17)",
  "--accent-info": "var(--rh-color-interactive-blue-lighter, #92c5f9)",
  "--hat-color": "var(--rh-color-brand-red-on-dark, #ee0000)",

  "--font-sans": "var(--rh-font-family-body-text, 'Red Hat Text', 'Red Hat Display', sans-serif)",
  "--font-mono": "var(--rh-font-family-code, 'Red Hat Mono', 'Courier New', monospace)",

  "--shadow-sm": "var(--rh-box-shadow-sm, 0 1px 2px rgba(21, 21, 21, 0.15))",
  "--shadow-md": "var(--rh-box-shadow-md, 0 2px 4px rgba(21, 21, 21, 0.18))",
  "--shadow-lg": "var(--rh-box-shadow-lg, 0 4px 8px rgba(21, 21, 21, 0.22))",
};

export interface ThemeEntry {
  id: string;
  label: string;
  theme: Theme;
  dark: boolean;
}

export const allThemes: ThemeEntry[] = [
  { id: "light", label: "Light", theme: lightTheme, dark: false },
  { id: "dark", label: "Dark", theme: darkTheme, dark: true },
  { id: "rh-light", label: "Red Hat Light", theme: redHatLightTheme, dark: false },
  { id: "rh-dark", label: "Red Hat Dark", theme: redHatDarkTheme, dark: true },
];

const themeMap = new Map(allThemes.map((t) => [t.id, t]));

const STORAGE_KEY = "agent-theme";

class ThemeManager {
  private current: Theme;
  private themeName: string;

  constructor() {
    this.themeName = this.loadPreference();
    const entry = themeMap.get(this.themeName);
    this.current = entry ? entry.theme : lightTheme;
    this.apply();
  }

  get name(): string {
    return this.themeName;
  }

  get isDark(): boolean {
    const entry = themeMap.get(this.themeName);
    return entry ? entry.dark : false;
  }

  get themes(): ThemeEntry[] {
    return allThemes;
  }

  toggle(): void {
    const ids = allThemes.map((t) => t.id);
    const idx = ids.indexOf(this.themeName);
    const next = ids[(idx + 1) % ids.length];
    this.setTheme(next);
  }

  setTheme(name: string, custom?: Theme): void {
    this.themeName = name;
    const entry = themeMap.get(name);
    const base = entry ? entry.theme : lightTheme;
    this.current = custom ? Object.assign({} as Theme, base, custom) : base;
    this.apply();
    this.savePreference();
  }

  private apply(): void {
    const root = document.documentElement;
    for (const [prop, value] of Object.entries(this.current)) {
      root.style.setProperty(prop, value);
    }
  }

  private loadPreference(): string {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved && themeMap.has(saved)) return saved;
    } catch {
      // localStorage may be unavailable
    }
    if (window.matchMedia?.("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }
    return "light";
  }

  private savePreference(): void {
    try {
      localStorage.setItem(STORAGE_KEY, this.themeName);
    } catch {
      // ignore
    }
  }
}

export const themeManager = new ThemeManager();
