"""
Integration tests for the main entry point.
"""

import logging
import pytest
from unittest.mock import patch, Mock

from transpolibre.main import main


class TestMainEntry:
    """Test main entry point functionality."""

    @patch("transpolibre.main.trans_list")
    @patch("transpolibre.main.parse_arguments")
    def test_list_languages_command(self, mock_parse_args, mock_trans_list):
        """Test --list flag functionality."""
        # Setup mock arguments
        mock_args = Mock(
            list=True, debug=False, verbose=0, url="http://localhost:8000", api_key=None
        )
        mock_parse_args.return_value = mock_args

        # Test list command
        main()

        # Verify trans_list was called
        mock_trans_list.assert_called_once_with("http://localhost:8000", None)

    @patch("builtins.print")
    @patch("transpolibre.main.parse_arguments")
    def test_file_required_error(self, mock_parse_args, mock_print):
        """Test error when file not provided for translation."""
        # Setup mock arguments without file
        mock_args = Mock(list=False, file=None, debug=False, verbose=0)
        mock_parse_args.return_value = mock_args

        # Test missing file
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        mock_print.assert_called_once()
        assert "Error: file is required" in str(mock_print.call_args)

    @patch("transpolibre.lib.trans_pofile.trans_pofile")
    @patch("transpolibre.main.parse_arguments")
    def test_libretranslate_engine_routing(self, mock_parse_args, mock_trans_pofile):
        """Test routing to LibreTranslate engine."""
        # Setup mock arguments
        mock_args = Mock(
            list=False,
            file="test.po",
            engine="libretranslate",
            source_lang="en",
            target_lang="es",
            url="http://localhost:8000",
            api_key="test-key",
            overwrite=False,
            debug=False,
            verbose=0,
        )
        mock_parse_args.return_value = mock_args

        # Test LibreTranslate routing
        main()

        # Verify correct function called
        mock_trans_pofile.assert_called_once_with(
            "en", "es", "http://localhost:8000", "test-key", "test.po", False
        )

    @patch("transpolibre.lib.trans_local.trans_local")
    @patch("transpolibre.main.parse_arguments")
    def test_local_engine_routing(self, mock_parse_args, mock_trans_local):
        """Test routing to local engine."""
        # Setup mock arguments
        mock_args = Mock(
            list=False,
            file="test.po",
            engine="local",
            source_lang="en",
            target_lang="es",
            overwrite=True,
            model="test-model",
            cuda_device=1,
            device="gpu",
            debug=False,
            verbose=0,
        )
        mock_parse_args.return_value = mock_args

        # Test local engine routing
        main()

        # Verify correct function called
        mock_trans_local.assert_called_once_with(
            "en", "es", "test.po", True, "test-model", 1, "gpu"
        )

    @patch("transpolibre.lib.trans_ollama.trans_ollama")
    @patch("transpolibre.main.parse_arguments")
    def test_ollama_engine_routing(self, mock_parse_args, mock_trans_ollama):
        """Test routing to Ollama engine."""
        # Setup mock arguments
        mock_args = Mock(
            list=False,
            file="test.po",
            engine="ollama",
            source_lang="fr",
            target_lang="de",
            url="http://localhost:11434",
            api_key=None,
            overwrite=False,
            model="llama2",
            debug=False,
            verbose=0,
        )
        mock_parse_args.return_value = mock_args

        # Test Ollama routing
        main()

        # Verify correct function called
        mock_trans_ollama.assert_called_once_with(
            "fr", "de", "http://localhost:11434", None, "test.po", False, "llama2"
        )

    @patch("transpolibre.main.logging.basicConfig")
    @patch("transpolibre.main.parse_arguments")
    def test_debug_logging_configuration(self, mock_parse_args, mock_basicConfig):
        """Test debug flag sets correct log level."""
        # Setup mock arguments with debug
        mock_args = Mock(
            list=True, debug=True, verbose=0, url="http://localhost:8000", api_key=None
        )
        mock_parse_args.return_value = mock_args

        # Mock trans_list to avoid actual execution
        with patch("transpolibre.main.trans_list"):
            main()

        # Verify DEBUG log level set
        mock_basicConfig.assert_called_once()
        call_args = mock_basicConfig.call_args[1]
        # Check that logging.DEBUG (10) was passed
        assert call_args["level"] == logging.DEBUG

    @patch("transpolibre.main.logging.basicConfig")
    @patch("transpolibre.main.parse_arguments")
    def test_verbose_logging_configuration(self, mock_parse_args, mock_basicConfig):
        """Test verbose flag sets correct log level."""
        # Setup mock arguments with verbose
        mock_args = Mock(
            list=True, debug=False, verbose=2, url="http://localhost:8000", api_key=None
        )
        mock_parse_args.return_value = mock_args

        # Mock trans_list to avoid actual execution
        with patch("transpolibre.main.trans_list"):
            main()

        # Verify INFO log level set
        mock_basicConfig.assert_called_once()
        call_args = mock_basicConfig.call_args[1]
        # Check that logging.INFO (20) was passed
        assert call_args["level"] == logging.INFO

    @patch("transpolibre.main.logging.basicConfig")
    @patch("transpolibre.main.parse_arguments")
    def test_default_logging_configuration(self, mock_parse_args, mock_basicConfig):
        """Test default log level without debug or verbose."""
        # Setup mock arguments
        mock_args = Mock(
            list=True, debug=False, verbose=0, url="http://localhost:8000", api_key=None
        )
        mock_parse_args.return_value = mock_args

        # Mock trans_list to avoid actual execution
        with patch("transpolibre.main.trans_list"):
            main()

        # Verify WARNING log level set
        mock_basicConfig.assert_called_once()
        call_args = mock_basicConfig.call_args[1]
        # Check that logging.WARNING (30) was passed
        assert call_args["level"] == logging.WARNING

    @patch("builtins.print")
    @patch("transpolibre.lib.trans_pofile.trans_pofile")
    @patch("transpolibre.main.parse_arguments")
    def test_libretranslate_file_not_found_error(
        self, mock_parse_args, mock_trans_pofile, mock_print
    ):
        """Test FileNotFoundError handling for LibreTranslate."""
        # Setup mock arguments
        mock_args = Mock(
            list=False,
            file="missing.po",
            engine="libretranslate",
            source_lang="en",
            target_lang="es",
            url="http://localhost:8000",
            api_key=None,
            overwrite=False,
            debug=False,
            verbose=0,
        )
        mock_parse_args.return_value = mock_args

        # Make trans_pofile raise FileNotFoundError
        mock_trans_pofile.side_effect = FileNotFoundError("File not found: missing.po")

        # Test error handling
        main()  # Should not raise, just print

        # Verify error was printed
        mock_print.assert_called_once_with("File not found: missing.po")

    @patch("transpolibre.main.logging")
    @patch("transpolibre.lib.trans_local.trans_local")
    @patch("transpolibre.main.parse_arguments")
    def test_local_engine_error_handling(
        self, mock_parse_args, mock_trans_local, mock_logging
    ):
        """Test error handling for local engine."""
        # Setup mock arguments
        mock_args = Mock(
            list=False,
            file="test.po",
            engine="local",
            source_lang="en",
            target_lang="es",
            overwrite=False,
            model="test-model",
            cuda_device=0,
            device="auto",
            debug=False,
            verbose=0,
        )
        mock_parse_args.return_value = mock_args

        # Make trans_local raise exception
        mock_trans_local.side_effect = Exception("CUDA out of memory")

        # Test error handling
        main()  # Should not raise

        # Verify error was logged
        mock_logging.error.assert_called_once()
        assert "An error occurred: CUDA out of memory" in str(
            mock_logging.error.call_args
        )

    @patch("transpolibre.main.logging")
    @patch("transpolibre.lib.trans_ollama.trans_ollama")
    @patch("transpolibre.main.parse_arguments")
    def test_ollama_engine_error_handling(
        self, mock_parse_args, mock_trans_ollama, mock_logging
    ):
        """Test error handling for Ollama engine."""
        # Setup mock arguments
        mock_args = Mock(
            list=False,
            file="test.po",
            engine="ollama",
            source_lang="en",
            target_lang="es",
            url="http://localhost:11434",
            api_key=None,
            overwrite=False,
            model="test-model",
            debug=False,
            verbose=0,
        )
        mock_parse_args.return_value = mock_args

        # Make trans_ollama raise exception
        mock_trans_ollama.side_effect = Exception("Connection refused")

        # Test error handling
        main()  # Should not raise

        # Verify error was logged
        mock_logging.error.assert_called_once()
        assert "An error occurred: Connection refused" in str(
            mock_logging.error.call_args
        )

    @patch("transpolibre.main.load_dotenv")
    @patch("transpolibre.main.parse_arguments")
    def test_dotenv_loading(self, mock_parse_args, mock_load_dotenv):
        """Test that .env file is loaded when main() is called."""
        # Setup mock arguments
        mock_args = Mock(list=True, debug=False, verbose=0, url="test", api_key=None)
        mock_parse_args.return_value = mock_args

        with patch("transpolibre.main.trans_list"):
            # Call main which should trigger initialization
            main()

            # Verify load_dotenv was called
            mock_load_dotenv.assert_called_once()

    @patch("gettext.bindtextdomain")
    @patch("gettext.textdomain")
    @patch("transpolibre.main.parse_arguments")
    def test_gettext_initialization(
        self, mock_parse_args, mock_textdomain, mock_bindtextdomain
    ):
        """Test gettext initialization when main() is called."""
        # Setup mock arguments
        mock_args = Mock(list=True, debug=False, verbose=0, url="test", api_key=None)
        mock_parse_args.return_value = mock_args

        with patch("transpolibre.main.trans_list"):
            # Call main which should trigger initialization
            main()

            # Verify gettext was set up
            mock_bindtextdomain.assert_called_with("transpolibre", "locale")
            mock_textdomain.assert_called_with("transpolibre")

    def test_main_as_script(self):
        """Test main() can be called as script entry point."""
        with patch("transpolibre.main.parse_arguments") as mock_parse_args:
            mock_args = Mock(
                list=True, debug=False, verbose=0, url="test", api_key=None
            )
            mock_parse_args.return_value = mock_args

            with patch("transpolibre.main.trans_list"):
                # Should not raise any exceptions
                main()

    @patch("transpolibre.lib.trans_pofile.trans_pofile")
    @patch("transpolibre.main.logging.basicConfig")
    @patch("transpolibre.main.parse_arguments")
    def test_multiple_verbose_levels(
        self, mock_parse_args, mock_basicConfig, mock_trans_pofile
    ):
        """Test different verbose levels."""
        for verbose_level in [0, 1, 2, 3]:
            mock_basicConfig.reset_mock()
            mock_args = Mock(
                list=False,
                file="test.po",
                engine="libretranslate",
                source_lang="en",
                target_lang="es",
                url="http://localhost:8000",
                api_key=None,
                overwrite=False,
                debug=False,
                verbose=verbose_level,
            )
            mock_parse_args.return_value = mock_args

            main()

            # Verify correct log level
            expected_level = logging.INFO if verbose_level > 0 else logging.WARNING
            call_args = mock_basicConfig.call_args[1]
            assert call_args["level"] == expected_level
