from pathlib import Path

# Read version at runtime
__version__ = Path(__file__).resolve().parent.parent.parent / "VERSION"
__version__ = __version__.read_text().strip()

from .example import add
