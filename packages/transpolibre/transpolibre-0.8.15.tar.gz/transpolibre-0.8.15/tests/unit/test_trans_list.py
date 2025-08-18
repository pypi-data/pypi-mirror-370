"""
Unit tests for the trans_list module.
"""

import pytest
from unittest.mock import Mock, patch

from transpolibre.lib.trans_list import trans_list


class TestTransList:
    """Test language listing functionality."""

    @patch("transpolibre.lib.trans_list.LibreTranslateAPI")
    @patch("builtins.print")
    def test_list_languages_basic(self, mock_print, mock_lt_class):
        """Test basic language listing functionality."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.languages.return_value = [
            {"code": "en", "name": "English", "targets": ["es", "fr", "de"]},
            {"code": "es", "name": "Spanish", "targets": ["en", "fr", "de"]},
        ]
        mock_lt_class.return_value = mock_instance

        # Test listing
        with pytest.raises(SystemExit) as exc_info:
            trans_list("http://localhost:8000", None)

        # Verify exit code
        assert exc_info.value.code == 0

        # Verify API was called
        mock_lt_class.assert_called_once_with("http://localhost:8000", None)
        mock_instance.languages.assert_called_once()

        # Verify output format
        calls = mock_print.call_args_list
        assert any("Language: English" in str(call) for call in calls)
        assert any("Code: en" in str(call) for call in calls)
        assert any("Targets: es, fr, de" in str(call) for call in calls)
        assert any("Language: Spanish" in str(call) for call in calls)
        assert any("Code: es" in str(call) for call in calls)
        assert any("Targets: en, fr, de" in str(call) for call in calls)

    @patch("transpolibre.lib.trans_list.LibreTranslateAPI")
    @patch("builtins.print")
    def test_list_languages_with_api_key(self, mock_print, mock_lt_class):
        """Test language listing with API key."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.languages.return_value = [
            {"code": "en", "name": "English", "targets": ["es"]}
        ]
        mock_lt_class.return_value = mock_instance

        # Test with API key
        api_key = "test-api-key"
        with pytest.raises(SystemExit):
            trans_list("http://localhost:8000", api_key)

        # Verify API key was passed
        mock_lt_class.assert_called_once_with("http://localhost:8000", api_key)

    @patch("transpolibre.lib.trans_list.LibreTranslateAPI")
    @patch("builtins.print")
    def test_list_empty_languages(self, mock_print, mock_lt_class):
        """Test handling of empty language list."""
        # Setup mock with empty list
        mock_instance = Mock()
        mock_instance.languages.return_value = []
        mock_lt_class.return_value = mock_instance

        # Test empty list
        with pytest.raises(SystemExit) as exc_info:
            trans_list("http://localhost:8000", None)

        assert exc_info.value.code == 0
        # Should not print any language info
        # Only empty lines or no language-specific output

    @patch("transpolibre.lib.trans_list.LibreTranslateAPI")
    @patch("builtins.print")
    def test_list_missing_fields(self, mock_print, mock_lt_class):
        """Test handling of missing fields in language data."""
        # Setup mock with missing fields
        mock_instance = Mock()
        mock_instance.languages.return_value = [
            {"code": "en"},  # Missing name and targets
            {"name": "Spanish"},  # Missing code and targets
            {"code": "fr", "name": "French"},  # Missing targets
            {"code": "de", "name": "German", "targets": []},  # Empty targets
        ]
        mock_lt_class.return_value = mock_instance

        # Test with missing fields
        with pytest.raises(SystemExit):
            trans_list("http://localhost:8000", None)

        # Verify N/A is used for missing fields
        calls = mock_print.call_args_list
        assert any("N/A" in str(call) for call in calls)

    @patch("transpolibre.lib.trans_list.LibreTranslateAPI")
    @patch("builtins.print")
    def test_list_many_targets(self, mock_print, mock_lt_class):
        """Test formatting of many target languages."""
        # Setup mock with many targets
        mock_instance = Mock()
        many_targets = ["es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar"]
        mock_instance.languages.return_value = [
            {"code": "en", "name": "English", "targets": many_targets}
        ]
        mock_lt_class.return_value = mock_instance

        # Test
        with pytest.raises(SystemExit):
            trans_list("http://localhost:8000", None)

        # Verify all targets are shown
        calls = mock_print.call_args_list
        expected_targets = ", ".join(many_targets)
        assert any(expected_targets in str(call) for call in calls)

    @patch("transpolibre.lib.trans_list.LibreTranslateAPI")
    def test_api_connection_error(self, mock_lt_class):
        """Test handling of API connection errors."""
        # Setup mock to raise exception
        mock_lt_class.side_effect = Exception("Connection failed")

        # Test connection error
        with pytest.raises(Exception) as exc_info:
            trans_list("http://localhost:8000", None)

        assert "Connection failed" in str(exc_info.value)

    @patch("transpolibre.lib.trans_list.LibreTranslateAPI")
    def test_api_languages_error(self, mock_lt_class):
        """Test handling of errors from languages() method."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.languages.side_effect = Exception("API Error")
        mock_lt_class.return_value = mock_instance

        # Test API error
        with pytest.raises(Exception) as exc_info:
            trans_list("http://localhost:8000", None)

        assert "API Error" in str(exc_info.value)

    @patch("transpolibre.lib.trans_list.LibreTranslateAPI")
    @patch("builtins.print")
    def test_unicode_language_names(self, mock_print, mock_lt_class):
        """Test handling of Unicode in language names."""
        # Setup mock with Unicode names
        mock_instance = Mock()
        mock_instance.languages.return_value = [
            {"code": "zh", "name": "中文", "targets": ["en"]},
            {"code": "ar", "name": "العربية", "targets": ["en"]},
            {"code": "ru", "name": "Русский", "targets": ["en"]},
        ]
        mock_lt_class.return_value = mock_instance

        # Test Unicode handling
        with pytest.raises(SystemExit):
            trans_list("http://localhost:8000", None)

        # Verify Unicode names are printed correctly
        calls = mock_print.call_args_list
        assert any("中文" in str(call) for call in calls)
        assert any("العربية" in str(call) for call in calls)
        assert any("Русский" in str(call) for call in calls)

    @patch("transpolibre.lib.trans_list.LibreTranslateAPI")
    @patch("builtins.print")
    def test_output_format(self, mock_print, mock_lt_class):
        """Test the exact output format."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.languages.return_value = [
            {"code": "test", "name": "Test Language", "targets": ["t1", "t2"]}
        ]
        mock_lt_class.return_value = mock_instance

        # Test
        with pytest.raises(SystemExit):
            trans_list("http://localhost:8000", None)

        # Check exact format
        calls = [str(call) for call in mock_print.call_args_list]

        # Should have these exact lines (with translations)
        assert any(
            "Language: Test Language" in call
            or "Language: " in call
            and "Test Language" in call
            for call in calls
        )
        assert any(
            "Code: test" in call or "Code: " in call and "test" in call
            for call in calls
        )
        assert any(
            "Targets: t1, t2" in call or "Targets: " in call and "t1, t2" in call
            for call in calls
        )

        # Should have empty line between languages
        assert any("call()" in call for call in calls)  # Empty print() call

    @patch("transpolibre.lib.trans_list.LibreTranslateAPI")
    @patch("builtins.print")
    def test_different_urls(self, mock_print, mock_lt_class):
        """Test with different API URLs."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.languages.return_value = []
        mock_lt_class.return_value = mock_instance

        urls = [
            "http://localhost:8000",
            "https://api.example.com",
            "http://192.168.1.100:5000",
            "https://translate.local:443",
        ]

        for url in urls:
            mock_lt_class.reset_mock()

            with pytest.raises(SystemExit):
                trans_list(url, None)

            mock_lt_class.assert_called_once_with(url, None)

    @patch("transpolibre.lib.trans_list.LibreTranslateAPI")
    @patch("builtins.print")
    def test_special_characters_in_targets(self, mock_print, mock_lt_class):
        """Test handling of special characters in target codes."""
        # Setup mock with special target codes
        mock_instance = Mock()
        mock_instance.languages.return_value = [
            {
                "code": "en",
                "name": "English",
                "targets": ["zh-CN", "pt-BR", "en-US", "fr_CA"],
            }
        ]
        mock_lt_class.return_value = mock_instance

        # Test
        with pytest.raises(SystemExit):
            trans_list("http://localhost:8000", None)

        # Verify targets with special characters are handled
        calls = mock_print.call_args_list
        assert any("zh-CN, pt-BR, en-US, fr_CA" in str(call) for call in calls)
