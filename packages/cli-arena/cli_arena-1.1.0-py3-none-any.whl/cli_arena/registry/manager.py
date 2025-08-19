from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .client import RegistryRow


def load_registry(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        # Allow either array or {datasets:[...]}
        if isinstance(data, dict) and "datasets" in data:
            return list(data["datasets"])  # type: ignore
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def save_registry(path: Path, rows: List[Dict[str, Any]]) -> None:
    # Save as plain JSON array for simplicity and TB-compat
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False))


def upsert_dataset(registry_path: Path, row_json_path: Path) -> int:
    rows = load_registry(registry_path)
    new_row = json.loads(row_json_path.read_text())
    # Validate using RegistryRow schema
    RegistryRow.model_validate(new_row)

    name = new_row.get("name")
    version = new_row.get("version")

    updated = False
    for i, r in enumerate(rows):
        if r.get("name") == name and r.get("version") == version:
            rows[i] = new_row
            updated = True
            break
    if not updated:
        rows.append(new_row)
    save_registry(registry_path, rows)
    return 0 if updated else 1


def list_datasets(registry_path: Path) -> List[RegistryRow]:
    return [RegistryRow.model_validate(r) for r in load_registry(registry_path)]


