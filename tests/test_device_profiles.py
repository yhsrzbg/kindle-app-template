import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "device_profiles", ROOT / "scripts" / "device_profiles.py"
)
device_profiles = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(device_profiles)


class DeviceProfileTests(unittest.TestCase):
    def test_resolves_named_profile(self):
        self.assertEqual(device_profiles.resolve("paperwhite-hd"), (1072, 1448))

    def test_resolves_custom_resolution(self):
        self.assertEqual(device_profiles.resolve("900x1200"), (900, 1200))

    def test_rejects_invalid_resolution(self):
        for value in ("900X1200", "0x800", "200x300", "unknown"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    device_profiles.resolve(value)
