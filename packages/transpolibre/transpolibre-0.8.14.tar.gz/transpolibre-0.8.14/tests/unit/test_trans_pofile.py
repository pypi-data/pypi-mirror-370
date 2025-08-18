"""
Unit tests for the trans_pofile module.
"""

import pytest
from unittest.mock import Mock, patch

from transpolibre.lib.trans_pofile import trans_pofile


class TestTransPofile:
    """Test LibreTranslate PO file translation."""

    def test_file_not_found(self):
        """Test FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError) as exc_info:
            trans_pofile(
                "en",
                "es",
                "http://localhost:8000",
                None,
                "/non/existent/file.po",
                False,
            )

        assert "does not exist" in str(exc_info.value)
        assert "/non/existent/file.po" in str(exc_info.value)

    @patch("transpolibre.lib.trans_pofile.update_pofile")
    @patch("transpolibre.lib.trans_pofile.trans_msg")
    @patch("transpolibre.lib.trans_pofile.polib")
    @patch("os.path.isfile")
    def test_skip_already_translated(
        self, mock_isfile, mock_polib, mock_trans_msg, mock_update
    ):
        """Test skipping already translated entries without overwrite flag."""
        # Setup mocks
        mock_isfile.return_value = True

        # Create mock PO file with mixed entries
        mock_po = Mock()
        mock_entry1 = Mock(msgid="Hello", msgstr="Hola")  # Already translated
        mock_entry2 = Mock(msgid="World", msgstr="")  # Not translated
        mock_entry3 = Mock(msgid="Test", msgstr="Prueba")  # Already translated
        mock_po.__iter__ = Mock(
            return_value=iter([mock_entry1, mock_entry2, mock_entry3])
        )
        mock_polib.pofile.return_value = mock_po

        mock_trans_msg.return_value = "Mundo"

        # Test without overwrite
        trans_pofile("en", "es", "http://localhost:8000", None, "test.po", False)

        # Should only translate the empty one
        mock_trans_msg.assert_called_once_with(
            "World", "en", "es", "http://localhost:8000", None
        )
        mock_update.assert_called_once_with("test.po", "World", "Mundo")

    @patch("transpolibre.lib.trans_pofile.update_pofile")
    @patch("transpolibre.lib.trans_pofile.trans_msg")
    @patch("transpolibre.lib.trans_pofile.polib")
    @patch("os.path.isfile")
    def test_overwrite_mode(self, mock_isfile, mock_polib, mock_trans_msg, mock_update):
        """Test overwrite mode retranslates existing entries."""
        # Setup mocks
        mock_isfile.return_value = True

        # Create mock PO file with translated entries
        mock_po = Mock()
        mock_entry1 = Mock(msgid="Hello", msgstr="Hola")
        mock_entry2 = Mock(msgid="World", msgstr="Mundo")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry1, mock_entry2]))
        mock_polib.pofile.return_value = mock_po

        mock_trans_msg.side_effect = ["Saludos", "Tierra"]

        # Test with overwrite
        trans_pofile("en", "es", "http://localhost:8000", None, "test.po", True)

        # Should translate all entries
        assert mock_trans_msg.call_count == 2
        mock_trans_msg.assert_any_call(
            "Hello", "en", "es", "http://localhost:8000", None
        )
        mock_trans_msg.assert_any_call(
            "World", "en", "es", "http://localhost:8000", None
        )

        assert mock_update.call_count == 2
        mock_update.assert_any_call("test.po", "Hello", "Saludos")
        mock_update.assert_any_call("test.po", "World", "Tierra")

    @patch("transpolibre.lib.trans_pofile.update_pofile")
    @patch("transpolibre.lib.trans_pofile.trans_msg")
    @patch("transpolibre.lib.trans_pofile.polib")
    @patch("os.path.isfile")
    def test_api_key_passed(self, mock_isfile, mock_polib, mock_trans_msg, mock_update):
        """Test API key is passed to translation function."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Test", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        mock_trans_msg.return_value = "Prueba"

        # Test with API key
        api_key = "test-api-key-123"
        trans_pofile("en", "es", "http://localhost:8000", api_key, "test.po", False)

        # Verify API key passed
        mock_trans_msg.assert_called_once_with(
            "Test", "en", "es", "http://localhost:8000", api_key
        )

    @patch("transpolibre.lib.trans_pofile.update_pofile")
    @patch("transpolibre.lib.trans_pofile.trans_msg")
    @patch("transpolibre.lib.trans_pofile.polib")
    @patch("os.path.isfile")
    def test_empty_po_file(self, mock_isfile, mock_polib, mock_trans_msg, mock_update):
        """Test handling of empty PO file."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_po.__iter__ = Mock(return_value=iter([]))  # Empty file
        mock_polib.pofile.return_value = mock_po

        # Test empty file
        trans_pofile("en", "es", "http://localhost:8000", None, "empty.po", False)

        # Should not call translation
        mock_trans_msg.assert_not_called()
        mock_update.assert_not_called()

    @patch("transpolibre.lib.trans_pofile.update_pofile")
    @patch("transpolibre.lib.trans_pofile.trans_msg")
    @patch("transpolibre.lib.trans_pofile.polib")
    @patch("os.path.isfile")
    def test_unicode_handling(
        self, mock_isfile, mock_polib, mock_trans_msg, mock_update
    ):
        """Test handling of Unicode in messages."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Hello 世界 🌍", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        mock_trans_msg.return_value = "Hola 世界 🌍"

        # Test Unicode
        trans_pofile("en", "es", "http://localhost:8000", None, "test.po", False)

        mock_trans_msg.assert_called_once_with(
            "Hello 世界 🌍", "en", "es", "http://localhost:8000", None
        )
        mock_update.assert_called_once_with("test.po", "Hello 世界 🌍", "Hola 世界 🌍")

    @patch("transpolibre.lib.trans_pofile.update_pofile")
    @patch("transpolibre.lib.trans_pofile.trans_msg")
    @patch("transpolibre.lib.trans_pofile.polib")
    @patch("os.path.isfile")
    def test_multiline_entries(
        self, mock_isfile, mock_polib, mock_trans_msg, mock_update
    ):
        """Test handling of multiline entries."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Line 1\nLine 2\nLine 3", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        mock_trans_msg.return_value = "Línea 1\nLínea 2\nLínea 3"

        # Test multiline
        trans_pofile("en", "es", "http://localhost:8000", None, "test.po", False)

        mock_trans_msg.assert_called_once_with(
            "Line 1\nLine 2\nLine 3", "en", "es", "http://localhost:8000", None
        )
        mock_update.assert_called_once_with(
            "test.po", "Line 1\nLine 2\nLine 3", "Línea 1\nLínea 2\nLínea 3"
        )

    @patch("transpolibre.lib.trans_pofile.update_pofile")
    @patch("transpolibre.lib.trans_pofile.trans_msg")
    @patch("transpolibre.lib.trans_pofile.polib")
    @patch("os.path.isfile")
    @patch("transpolibre.lib.trans_pofile.logging")
    def test_logging_output(
        self, mock_logging, mock_isfile, mock_polib, mock_trans_msg, mock_update
    ):
        """Test proper logging of translations."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Test", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        mock_trans_msg.return_value = "Prueba"

        # Test logging
        trans_pofile("en", "es", "http://localhost:8000", None, "test.po", False)

        # Check debug and info logs
        mock_logging.debug.assert_any_call("Read PO file: test.po")
        mock_logging.info.assert_any_call("Original:    Test")
        mock_logging.info.assert_any_call("Translation: Prueba\n")

    @patch("transpolibre.lib.trans_pofile.update_pofile")
    @patch("transpolibre.lib.trans_pofile.trans_msg")
    @patch("transpolibre.lib.trans_pofile.polib")
    @patch("os.path.isfile")
    def test_translation_error_handling(
        self, mock_isfile, mock_polib, mock_trans_msg, mock_update
    ):
        """Test handling of translation errors."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Test", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        # Make translation fail
        mock_trans_msg.side_effect = Exception("Translation API error")

        # Test error propagation
        with pytest.raises(Exception) as exc_info:
            trans_pofile("en", "es", "http://localhost:8000", None, "test.po", False)

        assert "Translation API error" in str(exc_info.value)

    @patch("transpolibre.lib.trans_pofile.update_pofile")
    @patch("transpolibre.lib.trans_pofile.trans_msg")
    @patch("transpolibre.lib.trans_pofile.polib")
    @patch("os.path.isfile")
    def test_different_language_pairs(
        self, mock_isfile, mock_polib, mock_trans_msg, mock_update
    ):
        """Test various language pair combinations."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Test", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        mock_trans_msg.return_value = "Translated"

        # Test different language pairs
        language_pairs = [
            ("en", "es"),
            ("fr", "de"),
            ("ja", "ko"),
            ("ar", "hi"),
        ]

        for src, tgt in language_pairs:
            mock_trans_msg.reset_mock()
            mock_update.reset_mock()
            # Reset the iterator for each test
            mock_po.__iter__ = Mock(return_value=iter([mock_entry]))

            trans_pofile(src, tgt, "http://localhost:8000", None, "test.po", False)

            mock_trans_msg.assert_called_once_with(
                "Test", src, tgt, "http://localhost:8000", None
            )

    @patch("transpolibre.lib.trans_pofile.update_pofile")
    @patch("transpolibre.lib.trans_pofile.trans_msg")
    @patch("transpolibre.lib.trans_pofile.polib")
    @patch("os.path.isfile")
    def test_special_po_file_paths(
        self, mock_isfile, mock_polib, mock_trans_msg, mock_update
    ):
        """Test handling of various file paths."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Test", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        mock_trans_msg.return_value = "Translated"

        # Test various paths
        paths = [
            "simple.po",
            "/absolute/path/to/file.po",
            "../relative/path/file.po",
            "path with spaces/file.po",
            "unicode/路径/文件.po",
        ]

        for path in paths:
            mock_polib.pofile.reset_mock()
            mock_update.reset_mock()
            # Reset the iterator for each test
            mock_po.__iter__ = Mock(return_value=iter([mock_entry]))

            trans_pofile("en", "es", "http://localhost:8000", None, path, False)

            mock_polib.pofile.assert_called_once_with(path, encoding="utf-8")
            mock_update.assert_called_once_with(path, "Test", "Translated")

    @patch("transpolibre.lib.trans_pofile.update_pofile")
    @patch("transpolibre.lib.trans_pofile.trans_msg")
    @patch("transpolibre.lib.trans_pofile.polib")
    @patch("os.path.isfile")
    def test_empty_msgstr_vs_whitespace(
        self, mock_isfile, mock_polib, mock_trans_msg, mock_update
    ):
        """Test distinction between empty msgstr and whitespace msgstr."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry1 = Mock(msgid="Empty", msgstr="")  # Empty string
        mock_entry2 = Mock(msgid="Whitespace", msgstr="   ")  # Whitespace
        mock_po.__iter__ = Mock(return_value=iter([mock_entry1, mock_entry2]))
        mock_polib.pofile.return_value = mock_po

        mock_trans_msg.return_value = "Translated"

        # Test without overwrite - whitespace is considered "translated"
        trans_pofile("en", "es", "http://localhost:8000", None, "test.po", False)

        # Should only translate the truly empty one
        mock_trans_msg.assert_called_once_with(
            "Empty", "en", "es", "http://localhost:8000", None
        )
        mock_update.assert_called_once_with("test.po", "Empty", "Translated")
