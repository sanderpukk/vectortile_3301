from __future__ import annotations

import tempfile
from pathlib import Path

from .config import load_config, write_mvt_conf_json
from .gdal import require_file, run


def generate(
    *,
    mode: str,
    config_path: str | Path,
    data_dir: str | Path,
    out_dir: str | Path,
    tmp_dir: str | Path,
) -> None:
    config = load_config(config_path)
    data_dir = Path(data_dir)
    out_dir = Path(out_dir)
    tmp_dir = Path(tmp_dir)
    basemap = require_file(data_dir / "basemap.gpkg", "run `python -m vt_pipeline preprocess` first")

    modes = config["modes"]
    if mode not in modes:
        raise SystemExit(f"Unknown mode {mode!r}. Valid modes: {', '.join(sorted(modes))}")

    mode_config = modes[mode]
    output_name = mode_config["output"]
    output = out_dir / output_name
    if output.exists():
        print(f"{output} already exists, skipping. Delete it to rebuild.")
        return

    tile_grid = config["tile_grid"]
    mvt = config["mvt"]
    tmp_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    # GDAL's MVT driver wants its layer mapping as JSON. Users edit the Python
    # config; this temporary JSON file is only a compatibility bridge.
    with tempfile.TemporaryDirectory(prefix="mvt-conf-") as conf_tmp:
        conf_path = Path(conf_tmp) / "mvt_conf.json"
        write_mvt_conf_json(config, conf_path)

        args = [
            "ogr2ogr",
            "-f",
            "MVT",
            "-dsco",
            "FORMAT=DIRECTORY",
            "-dsco",
            f"TILING_SCHEME={tile_grid['crs']},{tile_grid['origin'][0]},{tile_grid['origin'][1]},{tile_grid['size']}",
            "-dsco",
            f"MINZOOM={mvt['minzoom']}",
            "-dsco",
            f"MAXZOOM={mvt['maxzoom']}",
            "-dsco",
            f"EXTENT={mvt['extent']}",
            "-dsco",
            f"BUFFER={mvt['buffer']}",
            "-dsco",
            f"COMPRESS={'YES' if mvt['compress'] else 'NO'}",
            "-dsco",
            f"MAX_SIZE={mvt['max_size']}",
            "-dsco",
            f"TEMPORARY_DB={tmp_dir / 'mvt_tmp.db'}",
            "-dsco",
            f"CONF={conf_path}",
            "-progress",
            str(output),
            str(basemap),
        ]
        bbox = mode_config.get("bbox")
        if bbox:
            args.extend(["-spat", *(str(v) for v in bbox)])
        run(args)

    print(f"Tiles ready: {output}")
    sanity = output / "8" / "125" / "107.pbf"
    if sanity.exists():
        print(f"Sanity tile exists: {sanity}")
    else:
        print("WARNING: sanity tile 8/125/107.pbf is missing; check mode/grid alignment.")

