"""
Environment utilities for consistent project-wide behavior.
"""

from pathlib import Path
from typing import Optional


def load_project_dotenv(override: bool = False) -> Optional[str]:
    """
    Load .env from the project root in a consistent way.

    Returns the resolved path if a .env was found and loaded, otherwise None.
    """
    try:
        from dotenv import find_dotenv
        from dotenv import load_dotenv

        dotenv_path = find_dotenv(filename=".env", usecwd=True)
        if dotenv_path:
            load_dotenv(dotenv_path, override=override)
            return dotenv_path

        # Fallback: resolve relative to this file (app/core/ -> app -> project root)
        project_root = Path(__file__).resolve().parents[2]
        env_path = project_root / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=override)
            return str(env_path)
    except Exception:
        # Silently ignore dotenv loading issues; rely on existing environment
        return None

    return None
