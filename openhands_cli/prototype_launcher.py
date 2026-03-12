"""Launcher for the UI prototype app.

The prototype lives in prototype/ at the project root and contains
experimental screens and dummy UX flows for design iteration.
"""

import sys
from pathlib import Path


def launch_prototype() -> None:
    """Run the prototype Textual app with demo/mock data."""
    # Ensure project root is on path so we can import prototype
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from prototype.openhands_cli import OpenHandsCLIApp

    app = OpenHandsCLIApp()
    app.run(inline=False, mouse=True)
