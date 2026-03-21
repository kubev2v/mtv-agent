"""mtv-agent -- AI agent for MTV/Forklift VM migrations."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("mtv-agent")
except PackageNotFoundError:
    __version__ = "0.0.0"
