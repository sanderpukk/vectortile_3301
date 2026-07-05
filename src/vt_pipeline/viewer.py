from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def viewer_config(config: dict[str, Any]) -> dict[str, Any]:
    tile_grid = config["tile_grid"]
    modes = config["modes"]
    mvt = config["mvt"]

    sources = {
        name: f"/tiles/{mode['output']}/{{z}}/{{x}}/{{y}}.pbf"
        for name, mode in modes.items()
    }

    return {
        "projection": tile_grid["crs"],
        "extent": tile_grid["extent"],
        "origin": tile_grid["origin"],
        "tileSize": tile_grid["tile_size"],
        "maxzoom": mvt["maxzoom"],
        "baseResolution": tile_grid["size"] / tile_grid["tile_size"],
        "defaultSource": "tallinn" if "tallinn" in sources else next(iter(sources)),
        "sources": sources,
    }


def viewer_config_js(config: dict[str, Any]) -> str:
    data = json.dumps(viewer_config(config))
    return "window.VT_PIPELINE_CONFIG = " + data + ";\n"


def write_viewer_config_js(config: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(viewer_config_js(config), encoding="utf-8")
