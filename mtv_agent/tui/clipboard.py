"""System clipboard read/write helpers."""

import logging
import subprocess
import sys

logger = logging.getLogger(__name__)


def read_system_clipboard() -> str:
    """Read text from the OS clipboard."""
    try:
        if sys.platform == "darwin":
            r = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=2)
        elif sys.platform == "win32":
            r = subprocess.run(
                ["powershell", "-Command", "Get-Clipboard"],
                capture_output=True,
                text=True,
                timeout=2,
            )
        else:
            r = subprocess.run(
                ["xclip", "-selection", "clipboard", "-o"],
                capture_output=True,
                text=True,
                timeout=2,
            )
        return r.stdout if r.returncode == 0 else ""
    except FileNotFoundError:
        logger.debug("Clipboard tool not found (install xclip on Linux)")
        return ""
    except Exception:
        return ""


def write_system_clipboard(text: str) -> bool:
    """Write text to the OS clipboard. Returns True on success."""
    try:
        if sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text, text=True, timeout=2, check=True)
        elif sys.platform == "win32":
            subprocess.run(
                ["powershell", "-Command", "Set-Clipboard"],
                input=text,
                text=True,
                timeout=2,
                check=True,
            )
        else:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=text,
                text=True,
                timeout=2,
                check=True,
            )
        return True
    except FileNotFoundError:
        logger.debug("Clipboard tool not found (install xclip on Linux)")
        return False
    except Exception:
        return False
