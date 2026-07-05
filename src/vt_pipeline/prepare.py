from __future__ import annotations

import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from .gdal import run


ETAK_URL = "https://geoportaal.maaamet.ee/index.php?lang_id=2&plugin_act=otsing&andmetyyp=ETAK&dl=1&f=ETAK_EESTI_GPKG.zip&page_id=618"
EHAK_BASE_URL = "https://s3.pilw.io/rp-kemit-kataster/EHAK"


def prepare(sources_dir: str | Path) -> None:
    sources = Path(sources_dir)
    sources.mkdir(parents=True, exist_ok=True)
    _prepare_etak(sources)
    _prepare_ehak(sources)


def _prepare_etak(sources: Path) -> None:
    output = sources / "etak.gpkg"
    if output.exists():
        print(f"ETAK already exists, skipping: {output}")
        return

    with tempfile.TemporaryDirectory(prefix="etak-") as tmp:
        work = Path(tmp)
        archive = work / "ETAK_EESTI_GPKG.zip"
        _download(ETAK_URL, archive)
        _extract(archive, work)
        gpkg = _first(work, "*.gpkg")
        shutil.copyfile(gpkg, output)
    print(f"ETAK ready: {output}")


def _prepare_ehak(sources: Path) -> None:
    output = sources / "ehak.gpkg"
    if output.exists():
        print(f"EHAK already exists, skipping: {output}")
        return

    with tempfile.TemporaryDirectory(prefix="ehak-") as tmp:
        work = Path(tmp)
        archives = ["maakond_shp.zip", "omavalitsus_shp.zip", "asustusyksus_shp.zip"]
        for archive_name in archives:
            archive = work / archive_name
            _download(f"{EHAK_BASE_URL}/{archive_name}", archive)
            _extract(archive, work)

        maakond = _first(work, "maakond*.shp")
        omavalitsus = _first(work, "omavalitsus*.shp")
        asustus = _first(work, "asustusyksus*.shp")

        # EHAK shapefiles may arrive in a different CRS than ETAK. Reproject
        # them here so every later preprocessing and tiling step stays in
        # Estonia's native EPSG:3301 coordinate system.
        run(["ogr2ogr", "-f", "GPKG", "-t_srs", "EPSG:3301", "-nln", "maakond", str(output), str(maakond)])
        run(["ogr2ogr", "-f", "GPKG", "-t_srs", "EPSG:3301", "-append", "-nln", "omavalitsus", str(output), str(omavalitsus)])
        run(["ogr2ogr", "-f", "GPKG", "-t_srs", "EPSG:3301", "-append", "-nln", "asustusyksus", str(output), str(asustus)])
    print(f"EHAK ready: {output}")


def _download(url: str, path: Path) -> None:
    print(f"Downloading {url}")
    urllib.request.urlretrieve(url, path)
    print(f"Downloaded {path} ({path.stat().st_size} bytes)")


def _extract(archive: Path, target: Path) -> None:
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(target)


def _first(root: Path, pattern: str) -> Path:
    matches = sorted(root.rglob(pattern))
    if not matches:
        raise SystemExit(f"Could not find {pattern} under {root}")
    return matches[0]

