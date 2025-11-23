import unittest
import os
import json
from types import SimpleNamespace
from unittest.mock import patch
import config
import tempfile

class TestConfig(unittest.TestCase):

    def setUp(self):
        config._config = None
        for k in list(os.environ.keys()):
            if k.startswith("TEST_") or k.startswith("arg_"):
                del os.environ[k]

    def tearDown(self):
        config._config = None
        for k in list(os.environ.keys()):
            if k.startswith("TEST_") or k.startswith("arg_"):
                del os.environ[k]

    def test_get_default_path_not_found(self):
        with patch("os.getcwd", return_value="/unlikely/path"), \
             patch("os.path.isfile", return_value=False):
            path = config._get_default_path()
            self.assertIsNone(path)

    def test_get_default_path_found(self):
        with tempfile.TemporaryDirectory() as tmp_path:
            cfg_file = os.path.join(tmp_path, "config.json")
            with open(cfg_file, "w") as f:
                f.write('{"x":1}')

            with patch("os.getcwd", return_value=tmp_path), \
                 patch("os.path.isfile", side_effect=lambda p: os.path.basename(p) == "config.json"):
                path = config._get_default_path()
                self.assertTrue(path.endswith("config.json"))

    def test_init_config_empty(self):
        with patch("config._get_default_path", return_value=None):
            config._init_config()
            self.assertEqual(config._config, {})

    def test_init_config_loads_file(self):
        with tempfile.TemporaryDirectory() as tmp_path:
            cfg_file = os.path.join(tmp_path, "config.json")
            with open(cfg_file, "w") as f:
                f.write('{"alpha":10}')

            with patch("config._get_default_path", return_value=cfg_file):
                config._init_config()
                self.assertEqual(config._config, {"alpha": 10})

    def test_convert_to_typed_value_json(self):
        self.assertEqual(config.convert_to_typed_value('{"a":1}'), {"a":1})

    def test_convert_to_typed_value_number(self):
        self.assertEqual(config.convert_to_typed_value("5"), 5)

    def test_convert_to_typed_value_invalid_json(self):
        self.assertEqual(config.convert_to_typed_value("hello"), "hello")

    def test_convert_to_typed_value_none(self):
        self.assertIsNone(config.convert_to_typed_value(None))

    def test_set_parameter_string(self):
        config.set_parameter("TEST_KEY1", "value")
        self.assertEqual(os.environ["TEST_KEY1"], "value")

    def test_set_parameter_non_string(self):
        config.set_parameter("TEST_KEY2", {"x":1})
        self.assertTrue(os.environ["TEST_KEY2"].startswith("json:"))

    def test_get_parameter_from_env(self):
        os.environ["TEST_ENV"] = "5"
        self.assertEqual(config.get_parameter("TEST_ENV"), 5)

    def test_get_parameter_default(self):
        self.assertEqual(config.get_parameter("MISSING_KEY", default="fallback"), "fallback")

    def test_get_parameter_from_file(self):
        config._config = {"abc": 99}
        if "abc" in os.environ:
            del os.environ["abc"]
        self.assertEqual(config.get_parameter("abc"), 99)

    def test_get_parameter_missing_logs(self):
        config._config = {}
        with patch("logging.Logger.info") as mock_log:
            val = config.get_parameter("missing_key")
            self.assertIsNone(val)
            mock_log.assert_called()

    def test_overwrite_from_args_items(self):
        args = SimpleNamespace(a=1, b="hi", c=None)
        config.overwrite_from_args(args)
        self.assertEqual(os.environ["a"], "json:1")
        self.assertEqual(os.environ["b"], "hi")
        self.assertNotIn("c", os.environ)

    def test_overwrite_from_args_iteritems_fallback(self):
        class Args:
            def __init__(self):
                self.a = 1
                self.b = "hi"
        args = Args()
        config.overwrite_from_args(args)
        self.assertEqual(os.environ["a"], "json:1")
        self.assertEqual(os.environ["b"], "hi")


if __name__ == "__main__":
    unittest.main()
