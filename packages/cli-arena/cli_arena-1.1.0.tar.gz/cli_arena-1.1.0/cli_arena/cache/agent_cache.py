import hashlib
import json
import os
import time
from pathlib import Path
from typing import List, Optional


def compute_instruction_key(instruction: str) -> str:
    return hashlib.sha256(instruction.encode("utf-8")).hexdigest()


def get_agent_cache_dir(repo_root: Path, agent_name: str) -> Path:
    return repo_root / ".arena_cache" / "agents" / agent_name


def load_cached_commands(repo_root: Path, agent_name: str, instruction: str) -> Optional[List[str]]:
    if os.getenv("ARENA_LLM_CACHE", "1") == "0":
        return None
    try:
        key = compute_instruction_key(instruction)
        cache_dir = get_agent_cache_dir(repo_root, agent_name)
        cache_file = cache_dir / f"{key}.json"
        if not cache_file.exists():
            return None
        data = json.loads(cache_file.read_text())
        cmds = data.get("commands")
        if isinstance(cmds, list) and all(isinstance(c, str) for c in cmds):
            return cmds
    except Exception:
        return None
    return None


def save_cached_commands(repo_root: Path, agent_name: str, instruction: str, commands: List[str]) -> None:
    if os.getenv("ARENA_LLM_CACHE", "1") == "0":
        return
    try:
        key = compute_instruction_key(instruction)
        cache_dir = get_agent_cache_dir(repo_root, agent_name)
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{key}.json"
        payload = {"commands": commands, "created_at": time.time()}
        cache_file.write_text(json.dumps(payload))
    except Exception:
        pass


