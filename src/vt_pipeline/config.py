from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config" / "settings.py"


def load_config(path: str | Path = DEFAULT_CONFIG) -> dict[str, Any]:
    path = Path(path)
    if path.suffix != ".py":
        raise ValueError("Config must be a Python settings file, for example config/settings.py")
    ns = runpy.run_path(str(path))
    data = {
        "tile_grid": ns.get("TILE_GRID"),
        "mvt": ns.get("MVT"),
        "modes": ns.get("MODES"),
        "layers": ns.get("LAYERS"),
    }
    if not isinstance(data, dict):
        raise ValueError(f"Config {path} must contain a settings mapping")
    missing = [key for key, value in data.items() if value is None]
    if missing:
        raise ValueError(f"Config {path} is missing: {', '.join(missing)}")
    return data


def mvt_conf(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    layers = config.get("layers")
    if not isinstance(layers, dict):
        raise ValueError("Config must contain a 'layers' mapping")
    return layers


def mvt_conf_json(config: dict[str, Any]) -> str:
    return json.dumps(mvt_conf(config), indent=2, sort_keys=False) + "\n"


def write_mvt_conf_json(config: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(mvt_conf_json(config), encoding="utf-8")
