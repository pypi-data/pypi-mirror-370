from pathlib import Path
from unittest import mock
from unittest.case import TestCase

from django.conf import settings

from edc_test_settings.default_test_settings import DefaultTestSettings


class TestUtils(TestCase):
    def test_(self):
        base_dir = settings.BASE_DIR

        with mock.patch("sys.argv", ["tests.py"]):
            default_settings = DefaultTestSettings(
                calling_file=__file__,
                BASE_DIR=base_dir,
                APP_NAME="edc_test_settings",
                ETC_DIR=base_dir / "tests" / "etc",
            ).settings

        self.assertIn(
            "sqlite", default_settings.get("DATABASES").get("default").get("ENGINE")
        )

    def test_3(self):
        base_dir = settings.BASE_DIR
        with mock.patch("sys.argv", ["tests.py"]):
            default_settings = DefaultTestSettings(
                calling_file="tests.py",
                BASE_DIR=base_dir,
                APP_NAME="edc_test_settings",
                ETC_DIR=base_dir / "tests" / "etc",
            ).settings

        self.assertIn(
            "sqlite", default_settings.get("DATABASES").get("default").get("ENGINE")
        )

    def test_encryption_keys(self):
        with mock.patch("sys.argv", ["tests.py"]):
            base_dir = settings.BASE_DIR
            default_settings = DefaultTestSettings(
                calling_file="tests.py",
                app_name="edc_test_settings",
                base_dir=base_dir,
                installed_apps=["django_crypto_fields.apps.AppConfig"],
                ETC_DIR=base_dir / "tests" / "etc",
            ).settings

        self.assertTrue(
            Path(default_settings.get("DJANGO_CRYPTO_FIELDS_KEY_PATH")).exists()
        )
        self.assertIn("AUTO_CREATE_KEYS", default_settings)
