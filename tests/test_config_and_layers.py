import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class ConfigAndLayerTests(unittest.TestCase):
    def test_python_config_converts_to_gdal_layer_json(self):
        from vt_pipeline.config import load_config, mvt_conf_json

        config = load_config(ROOT / "config" / "settings.py")
        data = json.loads(mvt_conf_json(config))

        self.assertEqual(
            data["transportation_z0_4"],
            {"target_name": "transportation", "minzoom": 0, "maxzoom": 4},
        )
        self.assertEqual(data["poi_z8_13"]["target_name"], "poi")
        self.assertNotIn("tile_grid", data)
        self.assertNotIn("mvt", data)

    def test_preprocess_layer_catalog_matches_current_gdal_layers(self):
        from vt_pipeline.layers import LAYERS

        names = [layer.name for layer in LAYERS]

        self.assertEqual(len(names), 16)
        self.assertIn("transportation_z0_4", names)
        self.assertIn("place_z0_13", names)
        self.assertIn("poi_z8_13", names)
        self.assertEqual(names[-1], "poi_z8_13")

    def test_viewer_config_js_contains_tile_grid_and_sources(self):
        from vt_pipeline.config import load_config
        from vt_pipeline.viewer import viewer_config_js

        config = load_config(ROOT / "config" / "settings.py")
        js = viewer_config_js(config)

        self.assertIn("window.VT_PIPELINE_CONFIG", js)
        self.assertIn('"projection": "EPSG:3301"', js)
        self.assertIn('"extent": [40500, 5993000, 1064500, 7017000]', js)
        self.assertIn('"/tiles/tallinn/{z}/{x}/{y}.pbf"', js)


if __name__ == "__main__":
    unittest.main()
