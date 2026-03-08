# agent-web

Single-page chat UI for
[mtv-agent](../README.md), built with
[Lit](https://lit.dev/) web components, TypeScript, and
[Vite](https://vite.dev/).

## Tech stack

| Layer | Library |
|---|---|
| Components | [Lit 3](https://lit.dev/) (web components) |
| Build | [Vite 6](https://vite.dev/) |
| Language | TypeScript 5 (strict, ES2021 target) |
| Design tokens | [@rhds/tokens](https://github.com/RedHat-UX/red-hat-design-tokens) (Red Hat Design System) |
| Markdown | [marked](https://marked.js.org/) + [marked-highlight](https://github.com/markedjs/marked-highlight) |
| Syntax highlight | [highlight.js](https://highlightjs.org/) |
| Charts | [Chart.js](https://www.chartjs.org/) + [chartjs-plugin-zoom](https://www.chartjs.org/chartjs-plugin-zoom/) |
| Sanitisation | [DOMPurify](https://github.com/cure53/DOMPurify) |
| Lint | ESLint + Prettier |

## Prerequisites

- **Node.js 18+** and npm

## Getting started

Install dependencies:

```bash
npm ci
```

### Development (with hot-module reload)

Run the Vite dev server alongside the API server. In two terminals:

```bash
# Terminal 1 -- API server without static file serving
make dev          # from the repo root

# Terminal 2 -- Vite dev server on port 5173
npm run dev       # from web/
```

Vite proxies `/api` requests to the API server at `http://localhost:8000`
(configured in `vite.config.ts`).

Open `http://localhost:5173` in your browser.

### Production build

```bash
npm run build
```

Output goes to `dist/`. The Python API server auto-detects `web/dist/` and
serves it at `http://localhost:8000`.

## npm scripts

| Script | Description |
|---|---|
| `npm run dev` | Start Vite dev server (port 5173) |
| `npm run build` | Type-check with tsc, then build with Vite |
| `npm run preview` | Preview the production build locally |
| `npm run lint` | Lint with ESLint |
| `npm run format` | Format with Prettier |
| `npm run format:check` | Check formatting without writing |

## Project structure

```
web/
├── index.html                  Entry point
├── vite.config.ts              Vite config (proxy, chunking)
├── tsconfig.json               TypeScript config
├── eslint.config.js            ESLint config
├── package.json
└── src/
    ├── index.ts                Component registration
    ├── components/             Lit web components
    │   ├── agent-app.ts        Root shell (sidebar + chat + detail pane)
    │   ├── agent-sidebar.ts    Left sidebar (chat history, playbooks)
    │   ├── agent-chat.ts       Main chat message list
    │   ├── chat-composer.ts    Message input area
    │   ├── chat-message.ts     Single message bubble
    │   ├── tool-call-card.ts   Expandable tool call/result card
    │   ├── chart-card.ts       Chart.js time-series visualisation
    │   ├── detail-pane.ts      Right-side pinned-cards panel
    │   ├── markdown-renderer.ts Markdown-to-HTML with syntax highlighting
    │   ├── text-renderer.ts    Plain-text / table renderer
    │   ├── top-bar.ts          Header bar with model and status
    │   ├── model-selector.ts   LLM model switcher dropdown
    │   ├── skill-selector.ts   Skill activation panel
    │   ├── context-editor.ts   Key-value context editor
    │   ├── mcp-manager.ts      MCP server connect/disconnect UI
    │   ├── tool-policy-editor.ts Per-tool approval policy editor
    │   ├── theme-picker.ts     Theme switcher
    │   ├── thinking-indicator.ts Streaming "thinking" animation
    │   ├── card-search-bar.ts  Search bar for pinned cards
    │   └── resize-handle.ts    Draggable pane resize handle
    ├── services/               API and streaming
    │   ├── api-client.ts       REST calls to /api/*
    │   ├── stream-client.ts    SSE stream reader
    │   ├── stream-handler.ts   Maps SSE events to app state
    │   └── chat-utils.ts       Message conversion helpers
    ├── state/
    │   └── app-state.ts        Centralised reactive state store
    ├── styles/
    │   ├── themes.ts           Theme definitions and ThemeManager
    │   ├── shared.ts           Shared CSS helpers
    │   └── reset.css           CSS reset
    └── utils/
        ├── highlight-utils.ts  highlight.js language registration
        ├── table/              Detect and render tabular data
        │   ├── detectors/      Format detectors (JSON, markdown, fixed-width)
        │   └── parsers/        Format parsers
        ├── timeseries/         Time-series data extraction for charts
        └── tool-registry/      Per-tool card rendering
            ├── handlers/       Tool-specific display handlers
            └── parsers/        Result format parsers
```

## Components

The UI is composed of Lit custom elements. The root element is `<agent-app>`,
which lays out the sidebar, chat area, and detail pane.

| Component | Element | Role |
|---|---|---|
| AgentApp | `<agent-app>` | Root layout, orchestrates data loading and message dispatch |
| AgentSidebar | `<agent-sidebar>` | Chat history list, playbook browser, new-chat button |
| AgentChat | `<agent-chat>` | Scrollable message list with auto-scroll |
| ChatComposer | `<chat-composer>` | Text input with send button and skill/context controls |
| ChatMessage | `<chat-message>` | Renders a single user or assistant message |
| ToolCallCard | `<tool-call-card>` | Collapsible card showing a tool invocation and its result |
| ChartCard | `<chart-card>` | Chart.js line/bar chart for time-series metric data |
| DetailPane | `<detail-pane>` | Right panel displaying pinned cards from the conversation |
| MarkdownRenderer | `<markdown-renderer>` | Renders markdown with syntax-highlighted code blocks |
| TopBar | `<top-bar>` | Header with model name, token usage, and sidebar toggle |
| ModelSelector | `<model-selector>` | Dropdown to hot-swap the active LLM model |
| McpManager | `<mcp-manager>` | Connect/disconnect MCP servers |
| ToolPolicyEditor | `<tool-policy-editor>` | Set per-tool approval policies (auto, ask, deny) |
| ThemePicker | `<theme-picker>` | Cycle through available themes |

## Themes

Four built-in themes are defined in `src/styles/themes.ts`:

| ID | Name |
|---|---|
| `light` | Light |
| `dark` | Dark |
| `rh-light` | Red Hat Light |
| `rh-dark` | Red Hat Dark |

Themes are applied as CSS custom properties on `:root`. The `ThemeManager`
singleton persists the user's choice to `localStorage` and falls back to the
system `prefers-color-scheme` preference.

The Red Hat themes (`rh-light`, `rh-dark`) use
[@rhds/tokens](https://github.com/RedHat-UX/red-hat-design-tokens) design
tokens for colours, typography, spacing, and border radii. The global token
stylesheet is loaded in `index.html`
(`@rhds/tokens/css/global.css`) so that every `var(--rh-*)` reference resolves
to the official Red Hat Design System values. Shared layout properties (e.g.
`--radius-xs`, `--font-size-*`) also fall back to `--rh-*` tokens, keeping
all themes visually consistent with the Red Hat design language.

To add a theme, define a new `Theme` object in `themes.ts` and add it to the
`allThemes` array.

## API communication

The frontend communicates with the mtv-agent API server over two channels:

- **REST** (`api-client.ts`) -- status, models, skills, playbooks, MCP servers,
  chat CRUD
- **SSE** (`stream-client.ts` / `stream-handler.ts`) -- real-time streaming of
  agent responses, tool calls, and tool results during a conversation turn

During development, Vite's built-in proxy forwards all `/api` requests to
`http://localhost:8000`. In production, the Python server serves both the API
and the built static files from `dist/`.
