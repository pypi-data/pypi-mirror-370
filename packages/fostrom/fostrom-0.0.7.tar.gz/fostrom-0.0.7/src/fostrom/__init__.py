import subprocess
import warnings
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .fostrom import Fostrom, FostromError, Mail

try:
    __version__ = version("fostrom")
except PackageNotFoundError:
    __version__ = "unknown"


PACKAGE_DIR = Path(__file__).parent
AGENT_PATH = PACKAGE_DIR / ".agent" / "fostrom-device-agent"
SCRIPT_PATH = PACKAGE_DIR / "dl-agent.sh"


def ensure_agent() -> None:
    if not AGENT_PATH.exists():
        print("Downloading Fostrom Device Agent...")
        subprocess.run(["sh", str(SCRIPT_PATH), ".agent"], cwd=PACKAGE_DIR, check=True)


try:
    ensure_agent()
except Exception as e:
    warnings.warn(f"Failed to download Fostrom Device Agent: {e}", stacklevel=2)

__all__ = ["__version__", "Fostrom", "FostromError", "Mail"]
