import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class TimingTests(unittest.TestCase):
    def test_format_duration_uses_compact_units(self):
        from vt_pipeline.timing import format_duration

        self.assertEqual(format_duration(0.42), "0.4s")
        self.assertEqual(format_duration(65.2), "1m 5s")
        self.assertEqual(format_duration(3725.0), "1h 2m 5s")


if __name__ == "__main__":
    unittest.main()
