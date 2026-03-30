# Install with a user-local venv (no root / sudo needed)

If you can't run `pip install` system-wide — for example because of a
managed Python installation, restricted permissions, or company policy — you
can install `mtv-agent` in an isolated environment using
[uv](https://docs.astral.sh/uv/).

## Recommended: `uv tool install`

`uv tool install` creates an isolated virtual environment behind the scenes
and exposes only the `mtv-agent` command in `~/.local/bin/` — no other
executables leak onto your PATH.

### 1. Install

```bash
uv tool install mtv-agent
```

If `~/.local/bin` is not already on your PATH, `uv` will print a warning
with the command to add it. Follow those instructions, then open a new
terminal.

### 2. Verify

```bash
mtv-agent --version
```

### Upgrading

```bash
uv tool upgrade mtv-agent
```

### Uninstalling

```bash
uv tool uninstall mtv-agent
```

## Alternative: manual venv with a symlink

If you need full control over where the venv lives, you can create one
manually and symlink only the `mtv-agent` binary. This avoids prepending
the entire venv `bin/` directory to PATH, which would shadow system
executables like `python`, `pip`, and others.

### 1. Create a venv and install mtv-agent

```bash
uv venv ~/.mtv-agent-venv
uv pip install --python ~/.mtv-agent-venv/bin/python mtv-agent
```

### 2. Symlink the binary

```bash
mkdir -p ~/.local/bin
ln -sf ~/.mtv-agent-venv/bin/mtv-agent ~/.local/bin/mtv-agent
```

Make sure `~/.local/bin` is on your PATH. If it isn't, add it to your
shell startup file:

**Bash** (`~/.bashrc`):

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Zsh** (`~/.zshrc`):

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Verify

```bash
mtv-agent --version
```

### Upgrading

```bash
uv pip install --python ~/.mtv-agent-venv/bin/python --upgrade mtv-agent
```

### Uninstalling

1. Remove the symlink:

```bash
rm ~/.local/bin/mtv-agent
```

2. Delete the venv:

```bash
rm -rf ~/.mtv-agent-venv
```

## Notes

- Both methods keep all dependencies (including `claude-openai-proxy`)
  inside an isolated venv — no root access is required and your system
  Python is unaffected.
- Only the `mtv-agent` entry point ends up on your PATH; dependency
  binaries like `python`, `pip`, and `uvicorn` stay inside the venv.
- After installation, continue with
  [Initialise a workspace](installation.md#initialise-a-workspace) and the
  [Quick Start](quickstart.md) guide.
