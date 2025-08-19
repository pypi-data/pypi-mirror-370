import os
from pathlib import Path
from typing import List


def _load_dotenv_safe(path: Path) -> bool:
    try:
        from dotenv import load_dotenv
        if path.exists():
            load_dotenv(dotenv_path=path, override=False)
            return True
    except Exception:
        pass
    return False


def ensure_env_loaded() -> List[Path]:
    """Load environment variables from common .env locations.

    Order (first found wins unless override=True is needed by caller):
    - Project root .env (current working directory)
    - Repository root .env (by walking up from CWD until a .git or cli_arena is found)
    - User config: ~/.config/cli-arena/.env
    - User home: ~/.env

    Returns a list of files that were successfully loaded.
    """
    loaded: List[Path] = []

    # 1) CWD .env
    cwd_env = Path.cwd() / ".env"
    if _load_dotenv_safe(cwd_env):
        loaded.append(cwd_env)

    # 2) Walk up to find a likely repo root .env
    try:
        cur = Path.cwd()
        for _ in range(6):  # limit ascent
            maybe = cur / ".env"
            if maybe.exists() and maybe not in loaded:
                if _load_dotenv_safe(maybe):
                    loaded.append(maybe)
                    break
            # stop if we reach a marker
            if (cur / ".git").exists() or (cur / "cli_arena").exists():
                break
            cur = cur.parent
    except Exception:
        pass

    # 3) ~/.config/cli-arena/.env
    cfg_env = Path.home() / ".config" / "cli-arena" / ".env"
    if _load_dotenv_safe(cfg_env):
        loaded.append(cfg_env)

    # 4) ~/.env
    home_env = Path.home() / ".env"
    if _load_dotenv_safe(home_env):
        loaded.append(home_env)

    return loaded


def find_env_files() -> List[Path]:
    """Return a list of env files we consider for docker --env-file usage."""
    files: List[Path] = []
    for p in [Path.cwd() / ".env", Path.home() / ".config" / "cli-arena" / ".env", Path.home() / ".env"]:
        if p.exists():
            files.append(p)
    return files


