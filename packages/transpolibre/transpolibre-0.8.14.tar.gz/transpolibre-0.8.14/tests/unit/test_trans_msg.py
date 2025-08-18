"""
Unit tests for the trans_msg module.
"""

import pytest
from unittest.mock import Mock, patch

from transpolibre.lib.trans_msg import trans_msg


class TestTransMsg:
    """Test message translation logic."""

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_simple_text_translation(self, mock_lt_class):
        """Test basic text translation without special patterns."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.translate.return_value = "Hola Mundo"
        mock_lt_class.return_value = mock_instance

        # Test translation
        result = trans_msg("Hello World", "en", "es", "http://localhost:8000", None)

        # Verify
        assert result == "Hola Mundo"
        mock_lt_class.assert_called_once_with("http://localhost:8000", None)
        mock_instance.translate.assert_called_once_with("Hello World", "en", "es")

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_url_preservation(self, mock_lt_class):
        """Test URL detection and preservation in reStructuredText format."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.translate.return_value = "Documentación"
        mock_lt_class.return_value = mock_instance

        # Test with URL
        msg = "`Documentation <https://example.com/docs>`_"
        result = trans_msg(msg, "en", "es", "http://localhost:8000", None)

        # The URL should be preserved, only text translated
        assert result == "`Documentación <https://example.com/docs>`_"
        mock_instance.translate.assert_called_once_with("Documentation", "en", "es")

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_multiple_urls(self, mock_lt_class):
        """Test handling of multiple URLs in a message."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.translate.side_effect = ["Sitio web", "documentación"]
        mock_lt_class.return_value = mock_instance

        # Test with multiple URLs
        msg = "Visit `our website <https://example.com>`_ and `documentation <https://docs.example.com>`_"
        result = trans_msg(msg, "en", "es", "http://localhost:8000", None)

        # Both URLs should be preserved with translated text
        assert "`Sitio web <https://example.com>`_" in result
        assert "`documentación <https://docs.example.com>`_" in result

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_email_detection_skips_translation(self, mock_lt_class):
        """Test that email detection prevents translation."""
        # Setup mock
        mock_instance = Mock()
        mock_lt_class.return_value = mock_instance

        # Test with email
        msg = "Contact us at <support@example.com>"
        result = trans_msg(msg, "en", "es", "http://localhost:8000", None)

        # Should return original message unchanged
        assert result == msg
        # translate should not be called
        mock_instance.translate.assert_not_called()

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_mixed_url_email(self, mock_lt_class):
        """Test message with both URL and email."""
        # Setup mock
        mock_instance = Mock()
        mock_lt_class.return_value = mock_instance

        # Test with both URL and email - email takes precedence
        msg = "Visit `our site <https://example.com>`_ or email <admin@example.com>"
        result = trans_msg(msg, "en", "es", "http://localhost:8000", None)

        # Should return original message unchanged due to email
        assert result == msg
        mock_instance.translate.assert_not_called()

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_api_key_handling(self, mock_lt_class):
        """Test API key authentication is passed correctly."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.translate.return_value = "Traducido"
        mock_lt_class.return_value = mock_instance

        # Test with API key
        api_key = "test-api-key-123"
        result = trans_msg("Test", "en", "es", "http://localhost:8000", api_key)

        # Verify API key was passed
        mock_lt_class.assert_called_once_with("http://localhost:8000", api_key)
        assert result == "Traducido"

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_none_api_key(self, mock_lt_class):
        """Test handling of None API key."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.translate.return_value = "Traducido"
        mock_lt_class.return_value = mock_instance

        # Test with None API key
        result = trans_msg("Test", "en", "es", "http://localhost:8000", None)

        # Verify None was passed
        mock_lt_class.assert_called_once_with("http://localhost:8000", None)
        assert result == "Traducido"

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_empty_message(self, mock_lt_class):
        """Test translation of empty message."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.translate.return_value = ""
        mock_lt_class.return_value = mock_instance

        # Test empty string
        result = trans_msg("", "en", "es", "http://localhost:8000", None)

        assert result == ""
        mock_instance.translate.assert_called_once_with("", "en", "es")

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_whitespace_message(self, mock_lt_class):
        """Test translation of whitespace-only message."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.translate.return_value = "   "
        mock_lt_class.return_value = mock_instance

        # Test whitespace
        result = trans_msg("   ", "en", "es", "http://localhost:8000", None)

        assert result == "   "
        mock_instance.translate.assert_called_once_with("   ", "en", "es")

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_multiline_message(self, mock_lt_class):
        """Test translation of multiline message."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.translate.return_value = "Línea 1\nLínea 2\nLínea 3"
        mock_lt_class.return_value = mock_instance

        # Test multiline
        msg = "Line 1\nLine 2\nLine 3"
        result = trans_msg(msg, "en", "es", "http://localhost:8000", None)

        assert result == "Línea 1\nLínea 2\nLínea 3"
        mock_instance.translate.assert_called_once_with(msg, "en", "es")

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_special_characters(self, mock_lt_class):
        """Test translation with special characters."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.translate.return_value = "¡Hola! ¿Cómo estás?"
        mock_lt_class.return_value = mock_instance

        # Test special characters
        msg = "Hello! How are you?"
        result = trans_msg(msg, "en", "es", "http://localhost:8000", None)

        assert result == "¡Hola! ¿Cómo estás?"

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_unicode_handling(self, mock_lt_class):
        """Test translation with Unicode characters."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.translate.return_value = "你好世界 🌍"
        mock_lt_class.return_value = mock_instance

        # Test Unicode
        msg = "Hello World 🌍"
        result = trans_msg(msg, "en", "zh", "http://localhost:8000", None)

        assert result == "你好世界 🌍"

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_url_with_query_params(self, mock_lt_class):
        """Test URL with query parameters."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.translate.return_value = "Enlace"
        mock_lt_class.return_value = mock_instance

        # Test URL with query params
        msg = "`Link <https://example.com/page?param1=value&param2=test>`_"
        result = trans_msg(msg, "en", "es", "http://localhost:8000", None)

        assert result == "`Enlace <https://example.com/page?param1=value&param2=test>`_"

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_malformed_url_pattern(self, mock_lt_class):
        """Test handling of malformed URL patterns."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.translate.return_value = "Texto traducido"
        mock_lt_class.return_value = mock_instance

        # Test malformed pattern (missing closing >)
        msg = "`Link <https://example.com`_"
        result = trans_msg(msg, "en", "es", "http://localhost:8000", None)

        # Should translate as normal text since pattern doesn't match
        assert result == "Texto traducido"

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_email_variations(self, mock_lt_class):
        """Test various email formats."""
        # Setup mock
        mock_instance = Mock()
        mock_lt_class.return_value = mock_instance

        # Test different email formats
        emails = [
            "Contact: <user@example.com>",
            "Email <admin@test.org> for support",
            "Send to <user.name@company.co.uk>",
            "Reply to <user+tag@example.com>",
        ]

        for email_msg in emails:
            result = trans_msg(email_msg, "en", "es", "http://localhost:8000", None)
            assert result == email_msg  # Should not translate

        # Verify no translations were attempted
        mock_instance.translate.assert_not_called()

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_api_exception_propagation(self, mock_lt_class):
        """Test that API exceptions are propagated."""
        # Setup mock to raise exception
        mock_instance = Mock()
        mock_instance.translate.side_effect = Exception("API Error")
        mock_lt_class.return_value = mock_instance

        # Test that exception is propagated
        with pytest.raises(Exception) as exc_info:
            trans_msg("Test", "en", "es", "http://localhost:8000", None)

        assert str(exc_info.value) == "API Error"

    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_different_language_pairs(self, mock_lt_class):
        """Test various language pair combinations."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.translate.return_value = "Translated"
        mock_lt_class.return_value = mock_instance

        # Test different language pairs
        pairs = [
            ("en", "es"),
            ("fr", "de"),
            ("ja", "ko"),
            ("ar", "hi"),
            ("pt", "ru"),
        ]

        for src, tgt in pairs:
            result = trans_msg("Test", src, tgt, "http://localhost:8000", None)
            assert result == "Translated"

        # Verify all translations were called with correct languages
        assert mock_instance.translate.call_count == len(pairs)
