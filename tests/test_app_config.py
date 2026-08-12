import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("app_config", ROOT / "scripts" / "app_config.py")
app_config = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(app_config)


class AppConfigTests(unittest.TestCase):
    def setUp(self):
        self.config = app_config.load_config()

    def test_repository_config_is_valid(self):
        app_config.validate_config(self.config)

    def test_version_string(self):
        self.assertEqual(app_config.get_value(self.config, "version_string"), "1.0.0")

    def test_rejects_window_id_underscore(self):
        invalid = copy.deepcopy(self.config)
        invalid["window_id"] = "org.example.bad_id"
        with self.assertRaises(app_config.ConfigError):
            app_config.validate_config(invalid)

    def test_rejects_unknown_target(self):
        invalid = copy.deepcopy(self.config)
        invalid["targets"] = ["kindlehf", "future-device"]
        with self.assertRaises(app_config.ConfigError):
            app_config.validate_config(invalid)


if __name__ == "__main__":
    unittest.main()
