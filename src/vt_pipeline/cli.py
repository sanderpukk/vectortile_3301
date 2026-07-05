from __future__ import annotations

import argparse
import os
from pathlib import Path

from .config import DEFAULT_CONFIG, load_config, mvt_conf_json
from .generate import generate
from .pipeline import run_all
from .prepare import prepare
from .preprocess import preprocess
from .timing import timed_step
from .viewer import viewer_config_js, write_viewer_config_js


def main() -> None:
    parser = argparse.ArgumentParser(description="Python GDAL pipeline for Estonia EPSG:3301 vector tiles")
    parser.add_argument("--config", default=os.environ.get("VT_CONFIG", str(DEFAULT_CONFIG)))
    sub = parser.add_subparsers(dest="command", required=True)

    p_prepare = sub.add_parser("prepare", help="download ETAK/EHAK sources")
    p_prepare.add_argument("--sources-dir", default=os.environ.get("SOURCES_DIR", "/data/sources"))

    p_preprocess = sub.add_parser("preprocess", help="build basemap.gpkg")
    p_preprocess.add_argument("--sources-dir", default=os.environ.get("SOURCES_DIR", "/data/sources"))
    p_preprocess.add_argument("--output", default=os.environ.get("OUTPUT", "/data/basemap.gpkg"))

    p_generate = sub.add_parser("generate", help="generate MVT directory tiles")
    p_generate.add_argument("--mode", default=os.environ.get("MODE", "tallinn"))
    p_generate.add_argument("--data-dir", default=os.environ.get("DATA_DIR", "/data"))
    p_generate.add_argument("--out-dir", default=os.environ.get("OUT_DIR", "/out"))
    p_generate.add_argument("--tmp-dir", default=os.environ.get("TMP_DIR", "/gdaltmp"))

    sub.add_parser("config-json", help="print GDAL MVT CONF JSON generated from Python config")

    p_viewer = sub.add_parser("viewer-config", help="write viewer/config.js generated from Python config")
    p_viewer.add_argument("--output", default=os.environ.get("VIEWER_CONFIG", "/app/viewer/config.js"))

    p_run_all = sub.add_parser("run-all", help="run prepare, preprocess, generate, and viewer-config with one total timer")
    p_run_all.add_argument("--mode", default=os.environ.get("MODE", "tallinn"))
    p_run_all.add_argument("--sources-dir", default=os.environ.get("SOURCES_DIR", "/data/sources"))
    p_run_all.add_argument("--data-dir", default=os.environ.get("DATA_DIR", "/data"))
    p_run_all.add_argument("--out-dir", default=os.environ.get("OUT_DIR", "/out"))
    p_run_all.add_argument("--tmp-dir", default=os.environ.get("TMP_DIR", "/gdaltmp"))
    p_run_all.add_argument("--viewer-config", default=os.environ.get("VIEWER_CONFIG", "/app/viewer/config.js"))

    args = parser.parse_args()
    config_path = Path(args.config)

    if args.command == "prepare":
        with timed_step("prepare"):
            prepare(args.sources_dir)
    elif args.command == "preprocess":
        with timed_step("preprocess"):
            preprocess(args.sources_dir, args.output)
    elif args.command == "generate":
        with timed_step(f"generate {args.mode}"):
            generate(mode=args.mode, config_path=config_path, data_dir=args.data_dir, out_dir=args.out_dir, tmp_dir=args.tmp_dir)
    elif args.command == "config-json":
        print(mvt_conf_json(load_config(config_path)), end="")
    elif args.command == "viewer-config":
        with timed_step("viewer-config"):
            write_viewer_config_js(load_config(config_path), args.output)
            print(f"Wrote viewer config: {args.output}")
    elif args.command == "run-all":
        run_all(
            mode=args.mode,
            config_path=config_path,
            sources_dir=args.sources_dir,
            data_dir=args.data_dir,
            out_dir=args.out_dir,
            tmp_dir=args.tmp_dir,
            viewer_config=args.viewer_config,
        )
