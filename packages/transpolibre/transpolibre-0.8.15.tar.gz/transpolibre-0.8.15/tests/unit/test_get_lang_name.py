"""
Unit tests for the get_lang_name module.
"""

import pytest
from unittest.mock import patch, Mock

from transpolibre.lib.get_lang_name import get_lang_name


class TestGetLangName:
    """Test language code to name conversion."""

    def test_iso_639_1_codes(self):
        """Test 2-letter ISO 639-1 codes."""
        # Test common language codes
        assert get_lang_name("en") == "English"
        assert get_lang_name("es") == "Spanish"
        assert get_lang_name("fr") == "French"
        assert get_lang_name("de") == "German"
        assert get_lang_name("it") == "Italian"
        assert get_lang_name("pt") == "Portuguese"
        assert get_lang_name("ru") == "Russian"
        assert get_lang_name("zh") == "Chinese"
        assert get_lang_name("ja") == "Japanese"
        assert get_lang_name("ko") == "Korean"
        assert get_lang_name("ar") == "Arabic"
        assert get_lang_name("hi") == "Hindi"

    def test_iso_639_2_codes(self):
        """Test 3-letter ISO 639-2/3 codes."""
        assert get_lang_name("eng") == "English"
        assert get_lang_name("spa") == "Spanish"
        assert get_lang_name("fra") == "French"
        assert get_lang_name("deu") == "German"
        assert get_lang_name("ita") == "Italian"
        assert get_lang_name("por") == "Portuguese"
        assert get_lang_name("rus") == "Russian"
        assert get_lang_name("zho") == "Chinese"
        assert get_lang_name("jpn") == "Japanese"
        assert get_lang_name("kor") == "Korean"
        assert get_lang_name("ara") == "Arabic"
        assert get_lang_name("hin") == "Hindi"

    def test_invalid_code_length(self):
        """Test invalid code lengths cause exit."""
        # Single character
        with pytest.raises(SystemExit) as exc_info:
            get_lang_name("e")
        assert exc_info.value.code == 1

        # Four characters
        with pytest.raises(SystemExit) as exc_info:
            get_lang_name("engl")
        assert exc_info.value.code == 1

        # Empty string
        with pytest.raises(SystemExit) as exc_info:
            get_lang_name("")
        assert exc_info.value.code == 1

    def test_unknown_language_codes(self):
        """Test unknown but valid-length codes cause exit."""
        # Unknown 2-letter code
        with pytest.raises(SystemExit) as exc_info:
            get_lang_name("xx")
        assert exc_info.value.code == 1

        # Unknown 3-letter code
        with pytest.raises(SystemExit) as exc_info:
            get_lang_name("xxx")
        assert exc_info.value.code == 1

    def test_case_sensitivity(self):
        """Test that language codes are now case-insensitive."""
        # After our fix, all case variations should work
        assert get_lang_name("en") == "English"
        assert get_lang_name("EN") == "English"
        assert get_lang_name("En") == "English"
        assert get_lang_name("eN") == "English"

        # Test with 3-letter codes too
        assert get_lang_name("eng") == "English"
        assert get_lang_name("ENG") == "English"
        assert get_lang_name("Eng") == "English"

    def test_error_message_output(self, capsys):
        """Test error message is printed before exit."""
        with pytest.raises(SystemExit):
            get_lang_name("invalid")

        captured = capsys.readouterr()
        assert "Error: unknown language code: invalid" in captured.out

    def test_special_language_codes(self):
        """Test special or less common language codes."""
        # Test some less common but valid codes
        assert get_lang_name("pl") == "Polish"
        assert get_lang_name("tr") == "Turkish"
        assert get_lang_name("id") == "Indonesian"
        assert get_lang_name("bn") == "Bengali"

        # Test 3-letter versions
        assert get_lang_name("pol") == "Polish"
        assert get_lang_name("tur") == "Turkish"
        assert get_lang_name("ind") == "Indonesian"
        assert get_lang_name("ben") == "Bengali"

    def test_none_input(self):
        """Test None input causes appropriate error."""
        with pytest.raises((SystemExit, TypeError)):
            get_lang_name(None)

    def test_numeric_input(self):
        """Test numeric input causes error."""
        with pytest.raises((SystemExit, TypeError, AttributeError)):
            get_lang_name(123)

        with pytest.raises((SystemExit, TypeError, AttributeError)):
            get_lang_name(12)

    def test_language_variants(self):
        """Test language variants and regional codes."""
        # Note: pycountry handles main language codes, not regional variants
        # These should fail as they're not standard ISO 639 codes
        with pytest.raises(SystemExit):
            get_lang_name("en-US")

        with pytest.raises(SystemExit):
            get_lang_name("pt-BR")

        with pytest.raises(SystemExit):
            get_lang_name("zh-CN")

    @patch("transpolibre.lib.get_lang_name.languages")
    def test_pycountry_exception_handling(self, mock_languages):
        """Test handling of pycountry exceptions."""
        # Simulate pycountry raising an exception
        mock_languages.get.side_effect = KeyError("Language not found")

        with pytest.raises(SystemExit) as exc_info:
            get_lang_name("en")
        assert exc_info.value.code == 1

    @patch("transpolibre.lib.get_lang_name.languages")
    def test_none_return_from_pycountry(self, mock_languages):
        """Test handling when pycountry returns None."""
        mock_languages.get.return_value = None

        with pytest.raises(SystemExit) as exc_info:
            get_lang_name("en")
        assert exc_info.value.code == 1

    @patch("transpolibre.lib.get_lang_name.languages")
    def test_attribute_error_handling(self, mock_languages):
        """Test handling of AttributeError from pycountry."""
        # Create a mock object without 'name' attribute
        mock_lang = Mock(spec=[])  # Empty spec means no attributes
        mock_languages.get.return_value = mock_lang

        with pytest.raises(SystemExit) as exc_info:
            get_lang_name("en")
        assert exc_info.value.code == 1
