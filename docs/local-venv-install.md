# Install with a user-local venv (no root / sudo needed)

If you can't run `pip install` system-wide — for example because of a
managed Python installation, restricted permissions, or company policy — you
can install `mtv-agent` into a dedicated virtual environment using
[uv](https://docs.astral.sh/uv/) and add it to your shell PATH.

## Steps

### 1. Create a venv and install mtv-agent

```bash
uv venv ~/.mtv-agent-venv
uv pip install --python ~/.mtv-agent-venv/bin/python mtv-agent
```

### 2. Add the venv to your PATH

Add the venv `bin` directory to your shell startup file so the `mtv-agent`
command is available in every new terminal session.

**Bash** (`~/.bashrc`):

```bash
echo 'export PATH="$HOME/.mtv-agent-venv/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Zsh** (`~/.zshrc`):

```bash
echo 'export PATH="$HOME/.mtv-agent-venv/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Verify

```bash
mtv-agent --version
```

## Upgrading

```bash
uv pip install --python ~/.mtv-agent-venv/bin/python --upgrade mtv-agent
```

## Uninstalling

1. Remove the `export PATH=...` line from your `~/.bashrc` or `~/.zshrc`.
2. Delete the venv:

```bash
rm -rf ~/.mtv-agent-venv
```

## Notes

- The venv lives entirely under `~/.mtv-agent-venv` — no root access is
  required and it won't interfere with your system Python.
- All dependencies (including `claude-openai-proxy`) are installed inside the
  venv automatically.
- After installation, continue with
  [Initialise a workspace](installation.md#initialise-a-workspace) and the
  [Quick Start](quickstart.md) guide.
