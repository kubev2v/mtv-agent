# Publishing

How to release a new version of mtv-agent to PyPI.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed
- Node.js (v18+) and npm installed (for the web UI build)
- A [PyPI API token](https://pypi.org/help/#apitoken) configured for `uv publish`
  (via `UV_PUBLISH_TOKEN` or `~/.pypirc`)

## Release checklist

1. **Make sure all changes are merged and CI is green on `main`.**

2. **Bump the version** in `pyproject.toml`:

   ```toml
   [project]
   version = "0.1.23"   # <- update this
   ```

3. **Build and publish** in a single step:

   ```bash
   make publish
   ```

   This target chains the following steps automatically:

   | Step | What happens |
   |---|---|
   | `web-build` | Runs `npm ci && npm run build` inside `web/`, producing `web/dist/` |
   | `package` | Copies `web/dist/` into `mtv_agent/web_dist/`, then runs `uv build` to produce the wheel in `dist/` |
   | `publish` | Runs `uv publish` to upload the wheel to PyPI |

4. **Verify the release:**

   ```bash
   uv tool upgrade mtv-agent
   mtv-agent --version
   ```

## Common mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| Running `uv build` instead of `make package` | Wheel ships without the web UI (or with a stale build) because `mtv_agent/web_dist/` is gitignored | Always use `make publish` or `make package` |
| Forgetting to bump the version | PyPI rejects the upload (duplicate version) | Update `version` in `pyproject.toml` before publishing |
| Publishing from a dirty tree | Unintended changes end up in the wheel | Commit or stash first; publish from a clean `main` |

## How the web UI is bundled

The web UI source lives in `web/` and is **not** included in the Python
package directly. During `make package`:

1. `web/dist/` is built by Vite from the TypeScript/Lit sources.
2. The built assets are copied to `mtv_agent/web_dist/`.
3. `pyproject.toml` declares `mtv_agent/web_dist/**` as a hatch
   [build artifact](https://hatch.pypa.io/latest/config/build/#artifacts),
   so hatchling includes it in the wheel even though it is gitignored.

At runtime, the FastAPI server mounts `mtv_agent/web_dist/` (or falls back
to `web/dist/` for local development).
