"""
Unit tests for the parse_arguments module.
"""

import sys
import pytest
from unittest.mock import patch

from transpolibre.lib.parse_arguments import parse_arguments


class TestParseArguments:
    """Test CLI argument parsing functionality."""

    def test_default_values(self):
        """Test default argument values when no args provided."""
        with patch.object(sys, "argv", ["transpolibre"]):
            args = parse_arguments()

            assert args.engine == "libretranslate"
            assert args.source_lang == "en"
            assert args.target_lang == "es"
            assert args.device == "auto"
            assert args.cuda_device == 0
            assert args.overwrite is False
            assert args.debug is False
            assert args.verbose == 0
            assert args.list is False
            assert args.file is None

    def test_engine_validation_valid(self):
        """Test valid engine choices."""
        # Test each valid engine
        for engine in [
            "libretranslate",
            "LibreTranslate",
            "LIBRETRANSLATE",
            "ollama",
            "Ollama",
            "OLLAMA",
            "local",
            "Local",
            "LOCAL",
        ]:
            with patch.object(sys, "argv", ["transpolibre", "-e", engine]):
                args = parse_arguments()
                assert args.engine == engine.lower()

    def test_engine_validation_invalid(self):
        """Test invalid engine choice raises error."""
        with patch.object(sys, "argv", ["transpolibre", "-e", "invalid_engine"]):
            with pytest.raises(SystemExit):
                parse_arguments()

    def test_device_validation_valid(self):
        """Test valid device choices."""
        for device in ["auto", "Auto", "AUTO", "cpu", "CPU", "gpu", "GPU"]:
            with patch.object(sys, "argv", ["transpolibre", "-D", device]):
                args = parse_arguments()
                assert args.device == device.lower()

    def test_device_validation_invalid(self):
        """Test invalid device choice raises error."""
        with patch.object(sys, "argv", ["transpolibre", "-D", "invalid_device"]):
            with pytest.raises(SystemExit):
                parse_arguments()

    def test_environment_variable_loading(self, mock_env_variables):
        """Test loading from environment variables."""
        with patch.object(sys, "argv", ["transpolibre"]):
            args = parse_arguments()

            # API key should be loaded from env
            assert args.api_key == "test-api-key"

            # URLs should have correct defaults based on engine
            assert args.url == "http://test.libretranslate.com"

    def test_libretranslate_defaults(self):
        """Test LibreTranslate engine specific defaults."""
        with patch.object(sys, "argv", ["transpolibre", "-e", "libretranslate"]):
            with patch.dict("os.environ", {}, clear=True):
                args = parse_arguments()

                assert args.engine == "libretranslate"
                assert args.url == "http://127.0.0.1:8000"
                assert args.model is None

    def test_ollama_defaults(self):
        """Test Ollama engine specific defaults."""
        with patch.object(sys, "argv", ["transpolibre", "-e", "ollama"]):
            with patch.dict("os.environ", {}, clear=True):
                args = parse_arguments()

                assert args.engine == "ollama"
                assert args.url == "http://127.0.0.1:11434"
                assert args.model == "aya-expanse:32b"

    def test_local_defaults(self):
        """Test Local engine specific defaults."""
        with patch.object(sys, "argv", ["transpolibre", "-e", "local"]):
            with patch.dict("os.environ", {}, clear=True):
                args = parse_arguments()

                assert args.engine == "local"
                assert args.model == "ModelSpace/GemmaX2-28-9B-v0.1"

    def test_file_argument(self):
        """Test file argument parsing."""
        with patch.object(sys, "argv", ["transpolibre", "-f", "test.po"]):
            args = parse_arguments()
            assert args.file == "test.po"

    def test_language_arguments(self):
        """Test source and target language arguments."""
        with patch.object(sys, "argv", ["transpolibre", "-s", "fr", "-t", "de"]):
            args = parse_arguments()
            assert args.source_lang == "fr"
            assert args.target_lang == "de"

    def test_boolean_flags(self):
        """Test boolean flag arguments."""
        with patch.object(sys, "argv", ["transpolibre", "-l", "-o", "-d"]):
            args = parse_arguments()
            assert args.list is True
            assert args.overwrite is True
            assert args.debug is True

    def test_verbose_counting(self):
        """Test verbose flag counting."""
        with patch.object(sys, "argv", ["transpolibre"]):
            args = parse_arguments()
            assert args.verbose == 0

        with patch.object(sys, "argv", ["transpolibre", "-v"]):
            args = parse_arguments()
            assert args.verbose == 1

        with patch.object(sys, "argv", ["transpolibre", "-vv"]):
            args = parse_arguments()
            assert args.verbose == 2

        with patch.object(sys, "argv", ["transpolibre", "-vvv"]):
            args = parse_arguments()
            assert args.verbose == 3

    def test_cuda_device_argument(self):
        """Test CUDA device number argument."""
        with patch.object(sys, "argv", ["transpolibre", "-c", "2"]):
            args = parse_arguments()
            assert args.cuda_device == 2

    def test_api_key_argument(self):
        """Test API key argument."""
        with patch.object(sys, "argv", ["transpolibre", "-a", "my-api-key"]):
            with patch.dict("os.environ", {}, clear=True):
                args = parse_arguments()
                assert args.api_key == "my-api-key"

    def test_url_argument(self):
        """Test URL argument."""
        with patch.object(
            sys, "argv", ["transpolibre", "-u", "http://custom.url:9000"]
        ):
            args = parse_arguments()
            assert args.url == "http://custom.url:9000"

    def test_model_argument(self):
        """Test model argument."""
        with patch.object(sys, "argv", ["transpolibre", "-m", "custom/model"]):
            args = parse_arguments()
            assert args.model == "custom/model"

    def test_version_flag(self):
        """Test version flag."""
        with patch.object(sys, "argv", ["transpolibre", "-V"]):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code == 0

    def test_help_flag(self):
        """Test help flag."""
        with patch.object(sys, "argv", ["transpolibre", "-h"]):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code == 0

    def test_combined_arguments(self):
        """Test combination of multiple arguments."""
        with patch.object(
            sys,
            "argv",
            [
                "transpolibre",
                "-e",
                "ollama",
                "-f",
                "translations.po",
                "-s",
                "en",
                "-t",
                "fr",
                "-u",
                "http://ollama.local:11434",
                "-m",
                "llama2:13b",
                "-o",
                "-v",
                "-d",
            ],
        ):
            args = parse_arguments()

            assert args.engine == "ollama"
            assert args.file == "translations.po"
            assert args.source_lang == "en"
            assert args.target_lang == "fr"
            assert args.url == "http://ollama.local:11434"
            assert args.model == "llama2:13b"
            assert args.overwrite is True
            assert args.verbose == 1
            assert args.debug is True

    def test_environment_override(self):
        """Test that command line arguments override environment variables."""
        with patch.dict(
            "os.environ", {"LT_API_KEY": "env-key", "LT_URL": "http://env.url"}
        ):
            with patch.object(
                sys, "argv", ["transpolibre", "-a", "cli-key", "-u", "http://cli.url"]
            ):
                args = parse_arguments()

                assert args.api_key == "cli-key"  # CLI overrides env
                assert args.url == "http://cli.url"  # CLI overrides env
