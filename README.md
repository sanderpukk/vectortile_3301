# Estonia EPSG:3301 Python GDAL pipeline

This folder is a shareable, GDAL-only version of the vector tile build. Python
owns the data download, preprocessing layer mapping, classifier SQL, and tile
settings. GDAL still does the heavy geospatial work through CLI subprocesses.

## Layout

| Path | Purpose |
| --- | --- |
| `config/settings.py` | User-editable tile grid, zoom, mode, and layer mapping settings |
| `src/vt_pipeline/prepare.py` | Downloads ETAK and EHAK sources |
| `src/vt_pipeline/layers.py` | OMT-like preprocessing layer definitions and classification SQL |
| `src/vt_pipeline/preprocess.py` | Builds `basemap.gpkg` from the raw source GeoPackages |
| `src/vt_pipeline/generate.py` | Runs GDAL MVT tile generation |
| `src/vt_pipeline/viewer.py` | Generates browser viewer config from the same Python settings |
| `viewer/` | OpenLayers viewer served by nginx |

## Run with Docker Compose

From PowerShell:

```powershell
cd C:\vectortile\python-pipeline
docker compose run --rm pipeline
docker compose up viewer
```

On the first run, Docker may appear to pause after creating the network while it
pulls and extracts the large GDAL base image. To see those Docker build logs,
build the image explicitly first:

```powershell
cd C:\vectortile\python-pipeline
docker compose --progress=plain build pipeline
docker compose run --rm pipeline
```

This Docker Compose version does not support `docker compose run --no-build`.
After the explicit build, a normal `docker compose run --rm pipeline` reuses the
cached image and should start the Python timestamp logs quickly.

Open:

```text
http://localhost:8080
```

By default `pipeline` builds the faster Tallinn prototype. It runs:

1. `prepare` - download ETAK/EHAK source data.
2. `preprocess` - build `/data/basemap.gpkg`.
3. `generate` - create vector tiles in `/out/tallinn`.
4. `viewer-config` - update `viewer/config.js`.

For full Estonia:

```powershell
cd C:\vectortile\python-pipeline
$env:MODE = "full"
docker compose run --rm pipeline
docker compose up viewer
```

In bash-compatible shells, the equivalent is:

```bash
MODE=full docker compose run --rm pipeline
docker compose up viewer
```

Open the full-country tile source explicitly with:

```text
http://localhost:8080/?src=full
```

## Timing and progress

There are two kinds of logs:

- Docker build logs: image pull/extract/build output. Use
  `docker compose --progress=plain build pipeline` to see these.
- Pipeline logs: Python/GDAL runtime output. These start after the image is
  built and the container begins running.

The `pipeline` command logs lightweight UTC timestamps for each major step and
prints the total elapsed time at the end:

```text
[2026-07-05 12:00:00 UTC] START total pipeline
[2026-07-05 12:00:00 UTC] START prepare
...
[2026-07-05 14:12:09 UTC] END total pipeline (2h 12m 9s)
```

GDAL still prints its own tile-generation progress during `generate`. The timing
wrapper only logs step boundaries, so it should not meaningfully affect build
performance.

During source downloads, the pipeline prints when a file starts and when it
finishes. It does not currently print byte-by-byte download progress, so a large
ETAK download can be quiet for a while.

If you run steps separately, each command reports only its own elapsed time. Use
`pipeline` when you want one total for the whole process.

## Run steps separately

You can also run each step separately:

```powershell
cd C:\vectortile\python-pipeline
docker compose run --rm data-prep
docker compose run --rm preprocess
docker compose run --rm generate
docker compose run --rm viewer-config
docker compose up viewer
```

For separate full-generation steps:

```powershell
$env:MODE = "full"
docker compose run --rm generate
docker compose run --rm viewer-config
```

## Outputs

The Docker Compose volumes hold the generated data:

| Output | Location in containers | Description |
| --- | --- | --- |
| Source data | `/data/sources/etak.gpkg`, `/data/sources/ehak.gpkg` | Downloaded/prepared source GeoPackages |
| Preprocessed map | `/data/basemap.gpkg` | OMT-like render layers in EPSG:3301 |
| Tallinn tiles | `/out/tallinn/{z}/{x}/{y}.pbf` | Fast prototype tile set |
| Full Estonia tiles | `/out/estonia/{z}/{x}/{y}.pbf` | Full-country tile set |
| Viewer config | `viewer/config.js` | Browser tile grid/source config generated from Python settings |

Existing outputs are skipped. To rebuild a step, delete that output from the
volume or use a fresh Compose project/volume.

## Local Python commands inside the image

The compose services call these commands:

```bash
python3 -m vt_pipeline prepare
python3 -m vt_pipeline preprocess
python3 -m vt_pipeline generate --mode tallinn
python3 -m vt_pipeline config-json
python3 -m vt_pipeline viewer-config --output viewer/config.js
python3 -m vt_pipeline run-all --mode tallinn
python3 -m vt_pipeline run-all --mode full
```

`config-json` prints the GDAL MVT `CONF` JSON generated from
`config/settings.py`. You normally edit the Python settings file, not the
generated JSON.

`viewer-config` writes `viewer/config.js`, which gives the browser the EPSG:3301
tile grid and tile source URLs from the same Python settings.

## Notes

- All preprocessing and tiling stays in EPSG:3301.
- Layer SQL is intentionally close to the original bash pipeline so the output
  remains comparable.
- `config/settings.py` is the user-facing config. GDAL JSON and viewer JS are
  generated from it.
- The viewer is GDAL-only in this folder. The root repo still contains the
  separate PostGIS/worker pipeline.
