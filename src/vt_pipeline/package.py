from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path

from .config import load_config
from .gdal import require_file


def package(
    *,
    mode: str,
    config_path: str | Path,
    out_dir: str | Path,
    dist_dir: str | Path,
) -> None:
    config = load_config(config_path)
    modes = config["modes"]
    if mode not in modes:
        raise SystemExit(f"Unknown mode {mode!r}. Valid modes: {', '.join(sorted(modes))}")

    output_name = modes[mode]["output"]
    tiles = require_file(Path(out_dir) / output_name, f"run `python -m vt_pipeline generate --mode {mode}` first")

    dist_dir = Path(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    archive = dist_dir / f"{output_name}.zip"
    if archive.exists():
        print(f"{archive} already exists, skipping. Delete it to rebuild.")
        return

    # The pbf tiles are already gzip-compressed, so entries are stored
    # uncompressed. Build the archive inside the tile volume first, then copy
    # one finished file to the host-mounted dist dir. This avoids thousands of
    # small zip writes across Docker Desktop's bind-mount boundary.
    staging_dir = Path(out_dir) / ".package-tmp"
    staging_dir.mkdir(parents=True, exist_ok=True)
    partial = staging_dir / f"{archive.name}.partial"
    dist_partial = archive.with_name(archive.name + ".partial")
    partial.unlink(missing_ok=True)
    dist_partial.unlink(missing_ok=True)

    count = 0
    with zipfile.ZipFile(partial, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as zf:
        for root, dirs, files in os.walk(tiles):
            dirs.sort()
            for name in sorted(files):
                path = Path(root) / name
                zf.write(path, path.relative_to(tiles))
                count += 1
    if count == 0:
        partial.unlink()
        raise SystemExit(f"No files found under {tiles}; run `python -m vt_pipeline generate --mode {mode}` first")
    shutil.copyfile(partial, dist_partial)
    dist_partial.replace(archive)
    partial.unlink()

    size_mb = archive.stat().st_size / (1024 * 1024)
    print(f"Datapackage ready: {archive} ({count} files, {size_mb:.1f} MB)")


