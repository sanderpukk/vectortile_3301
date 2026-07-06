import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class PackageTests(unittest.TestCase):
    def test_package_stages_zip_under_out_dir_before_copying_to_dist(self):
        from vt_pipeline import package as package_module

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out_dir = tmp_path / "out"
            dist_dir = tmp_path / "dist"
            tiles = out_dir / "sample" / "0" / "0"
            tiles.mkdir(parents=True)
            (tiles / "0.pbf").write_bytes(b"already gzipped pbf")
            (out_dir / "sample" / "metadata.json").write_text("{}", encoding="utf-8")

            config_path = tmp_path / "settings.py"
            config_path.write_text(
                "\n".join(
                    [
                        "TILE_GRID = {}",
                        "MVT = {}",
                        "LAYERS = {}",
                        "MODES = {'test': {'output': 'sample'}}",
                    ]
                ),
                encoding="utf-8",
            )

            staged_partials = []
            original_zip_file = package_module.zipfile.ZipFile

            def tracking_zip_file(file, *args, **kwargs):
                staged_partials.append(Path(file))
                return original_zip_file(file, *args, **kwargs)

            package_module.zipfile.ZipFile = tracking_zip_file
            try:
                package_module.package(
                    mode="test",
                    config_path=config_path,
                    out_dir=out_dir,
                    dist_dir=dist_dir,
                )
            finally:
                package_module.zipfile.ZipFile = original_zip_file

            archive = dist_dir / "sample.zip"
            self.assertTrue(archive.exists())
            self.assertEqual(staged_partials, [out_dir / ".package-tmp" / "sample.zip.partial"])
            self.assertFalse(staged_partials[0].exists())

            with zipfile.ZipFile(archive) as zf:
                self.assertEqual(sorted(zf.namelist()), ["0/0/0.pbf", "metadata.json"])


if __name__ == "__main__":
    unittest.main()
