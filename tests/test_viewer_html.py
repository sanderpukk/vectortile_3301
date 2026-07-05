import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ViewerHtmlTests(unittest.TestCase):
    def test_viewer_coerces_feature_labels_to_strings(self):
        html = (ROOT / "viewer" / "index.html").read_text(encoding="utf-8")

        self.assertIn("function labelText(value)", html)
        self.assertIn("text: labelText(name)", html)
        self.assertIn("text: labelText(label)", html)


if __name__ == "__main__":
    unittest.main()
