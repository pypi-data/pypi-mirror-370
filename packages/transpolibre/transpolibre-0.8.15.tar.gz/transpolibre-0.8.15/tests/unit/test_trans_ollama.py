"""
Unit tests for the trans_ollama module.
"""

import pytest
from unittest.mock import Mock, patch

from transpolibre.lib.trans_ollama import trans_ollama


class TestTransOllama:
    """Test Ollama translation functionality."""

    def test_file_not_found(self):
        """Test FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError) as exc_info:
            trans_ollama(
                "en",
                "es",
                "http://localhost:11434",
                None,
                "/non/existent/file.po",
                False,
                "aya-expanse:32b",
            )

        assert "does not exist" in str(exc_info.value)
        assert "/non/existent/file.po" in str(exc_info.value)

    @patch("transpolibre.lib.trans_ollama.update_pofile")
    @patch("ollama.Client")
    @patch("transpolibre.lib.trans_ollama.polib")
    @patch("os.path.isfile")
    def test_client_initialization_no_api_key(
        self, mock_isfile, mock_polib, mock_client_class, mock_update
    ):
        """Test Ollama client initialization without API key."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Hello", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        mock_client = Mock()
        mock_client.chat.return_value = {"message": {"content": "Hola"}}
        mock_client_class.return_value = mock_client

        # Test without API key
        trans_ollama(
            "en", "es", "http://localhost:11434", None, "test.po", False, "test-model"
        )

        # Verify client initialized without headers
        mock_client_class.assert_called_once_with(
            host="http://localhost:11434", headers=None
        )

    @patch("transpolibre.lib.trans_ollama.update_pofile")
    @patch("ollama.Client")
    @patch("transpolibre.lib.trans_ollama.polib")
    @patch("os.path.isfile")
    def test_client_initialization_with_api_key(
        self, mock_isfile, mock_polib, mock_client_class, mock_update
    ):
        """Test Ollama client initialization with API key."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Hello", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        mock_client = Mock()
        mock_client.chat.return_value = {"message": {"content": "Hola"}}
        mock_client_class.return_value = mock_client

        # Test with API key
        api_key = "test-api-key-123"
        trans_ollama(
            "en",
            "es",
            "http://localhost:11434",
            api_key,
            "test.po",
            False,
            "test-model",
        )

        # Verify client initialized with Bearer token header
        expected_headers = {"Authorization": "Bearer test-api-key-123"}
        mock_client_class.assert_called_once_with(
            host="http://localhost:11434", headers=expected_headers
        )

    @patch("transpolibre.lib.trans_ollama.update_pofile")
    @patch("ollama.Client")
    @patch("transpolibre.lib.trans_ollama.polib")
    @patch("os.path.isfile")
    def test_prompt_engineering(
        self, mock_isfile, mock_polib, mock_client_class, mock_update
    ):
        """Test translation prompt format."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Hello World", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        mock_client = Mock()
        chat_calls = []

        def capture_chat_call(**kwargs):
            chat_calls.append(kwargs)
            return {"message": {"content": "Hola Mundo"}}

        mock_client.chat.side_effect = capture_chat_call
        mock_client_class.return_value = mock_client

        # Test prompt format
        trans_ollama(
            "en", "es", "http://localhost:11434", None, "test.po", False, "test-model"
        )

        # Verify prompt structure
        assert len(chat_calls) == 1
        call_args = chat_calls[0]
        assert call_args["model"] == "test-model"
        # Now we have 2 messages: system and user
        assert len(call_args["messages"]) == 2
        assert call_args["messages"][0]["role"] == "system"
        assert call_args["messages"][1]["role"] == "user"

        system_msg = call_args["messages"][0]["content"]
        user_prompt = call_args["messages"][1]["content"]

        # Check system message
        assert "translator" in system_msg.lower()
        assert "only the translation" in system_msg.lower()

        # Check user prompt format
        assert "Translate from English to Spanish" in user_prompt
        assert "Hello World" in user_prompt

    @patch("transpolibre.lib.trans_ollama.update_pofile")
    @patch("ollama.Client")
    @patch("transpolibre.lib.trans_ollama.polib")
    @patch("os.path.isfile")
    def test_skip_already_translated(
        self, mock_isfile, mock_polib, mock_client_class, mock_update
    ):
        """Test skipping already translated entries without overwrite."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry1 = Mock(msgid="Hello", msgstr="Hola")  # Already translated
        mock_entry2 = Mock(msgid="World", msgstr="")  # Not translated
        mock_po.__iter__ = Mock(return_value=iter([mock_entry1, mock_entry2]))
        mock_polib.pofile.return_value = mock_po

        mock_client = Mock()
        mock_client.chat.return_value = {"message": {"content": "Mundo"}}
        mock_client_class.return_value = mock_client

        # Test without overwrite
        trans_ollama(
            "en", "es", "http://localhost:11434", None, "test.po", False, "test-model"
        )

        # Should only translate the empty one
        mock_client.chat.assert_called_once()
        mock_update.assert_called_once_with("test.po", "World", "Mundo")

    @patch("transpolibre.lib.trans_ollama.update_pofile")
    @patch("ollama.Client")
    @patch("transpolibre.lib.trans_ollama.polib")
    @patch("os.path.isfile")
    def test_overwrite_mode(
        self, mock_isfile, mock_polib, mock_client_class, mock_update
    ):
        """Test overwrite mode retranslates existing entries."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry1 = Mock(msgid="Hello", msgstr="Hola")
        mock_entry2 = Mock(msgid="World", msgstr="Mundo")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry1, mock_entry2]))
        mock_polib.pofile.return_value = mock_po

        mock_client = Mock()
        mock_client.chat.side_effect = [
            {"message": {"content": "Saludos"}},
            {"message": {"content": "Tierra"}},
        ]
        mock_client_class.return_value = mock_client

        # Test with overwrite
        trans_ollama(
            "en", "es", "http://localhost:11434", None, "test.po", True, "test-model"
        )

        # Should translate all entries
        assert mock_client.chat.call_count == 2
        assert mock_update.call_count == 2
        mock_update.assert_any_call("test.po", "Hello", "Saludos")
        mock_update.assert_any_call("test.po", "World", "Tierra")

    @patch("transpolibre.lib.trans_ollama.update_pofile")
    @patch("ollama.Client")
    @patch("transpolibre.lib.trans_ollama.polib")
    @patch("os.path.isfile")
    def test_response_parsing(
        self, mock_isfile, mock_polib, mock_client_class, mock_update
    ):
        """Test parsing of Ollama responses."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Test", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        mock_client = Mock()
        # Test various response formats
        mock_client.chat.return_value = {
            "message": {"content": "  Prueba  "},  # With whitespace
            "other_field": "ignored",
        }
        mock_client_class.return_value = mock_client

        # Test response parsing
        trans_ollama(
            "en", "es", "http://localhost:11434", None, "test.po", False, "test-model"
        )

        # Verify content extracted correctly (whitespace is now trimmed by clean_ollama_response)
        mock_update.assert_called_once_with("test.po", "Test", "Prueba")

    @patch("transpolibre.lib.trans_ollama.update_pofile")
    @patch("ollama.Client")
    @patch("transpolibre.lib.trans_ollama.polib")
    @patch("os.path.isfile")
    def test_unicode_handling(
        self, mock_isfile, mock_polib, mock_client_class, mock_update
    ):
        """Test handling of Unicode in messages."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Hello 世界 🌍", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        mock_client = Mock()
        mock_client.chat.return_value = {"message": {"content": "Hola 世界 🌍"}}
        mock_client_class.return_value = mock_client

        # Test Unicode
        trans_ollama(
            "en", "es", "http://localhost:11434", None, "test.po", False, "test-model"
        )

        # Verify Unicode preserved in prompt and response
        call_args = mock_client.chat.call_args[1]
        # Check in user message (index 1, after system message)
        assert "Hello 世界 🌍" in call_args["messages"][1]["content"]
        mock_update.assert_called_once_with("test.po", "Hello 世界 🌍", "Hola 世界 🌍")

    @patch("transpolibre.lib.trans_ollama.update_pofile")
    @patch("ollama.Client")
    @patch("transpolibre.lib.trans_ollama.polib")
    @patch("os.path.isfile")
    def test_multiline_entries(
        self, mock_isfile, mock_polib, mock_client_class, mock_update
    ):
        """Test handling of multiline entries."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Line 1\nLine 2\nLine 3", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        mock_client = Mock()
        mock_client.chat.return_value = {
            "message": {"content": "Línea 1\nLínea 2\nLínea 3"}
        }
        mock_client_class.return_value = mock_client

        # Test multiline
        trans_ollama(
            "en", "es", "http://localhost:11434", None, "test.po", False, "test-model"
        )

        # Verify multiline preserved
        call_args = mock_client.chat.call_args[1]
        # Check in user message (index 1, after system message)
        assert "Line 1\nLine 2\nLine 3" in call_args["messages"][1]["content"]
        mock_update.assert_called_once_with(
            "test.po", "Line 1\nLine 2\nLine 3", "Línea 1\nLínea 2\nLínea 3"
        )

    @patch("transpolibre.lib.trans_ollama.update_pofile")
    @patch("ollama.Client")
    @patch("transpolibre.lib.trans_ollama.polib")
    @patch("os.path.isfile")
    @patch("transpolibre.lib.trans_ollama.logging")
    def test_logging_output(
        self, mock_logging, mock_isfile, mock_polib, mock_client_class, mock_update
    ):
        """Test proper logging of translations."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Test", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        mock_client = Mock()
        mock_client.chat.return_value = {"message": {"content": "Prueba"}}
        mock_client_class.return_value = mock_client

        # Test logging
        trans_ollama(
            "en", "es", "http://localhost:11434", None, "test.po", False, "test-model"
        )

        # Check logs
        mock_logging.debug.assert_any_call("Read PO file: test.po")
        mock_logging.info.assert_any_call("Original:    Test")
        mock_logging.info.assert_any_call("Translation: Prueba\n")

    @patch("transpolibre.lib.trans_ollama.update_pofile")
    @patch("ollama.Client")
    @patch("transpolibre.lib.trans_ollama.polib")
    @patch("os.path.isfile")
    def test_connection_error(
        self, mock_isfile, mock_polib, mock_client_class, mock_update
    ):
        """Test handling of Ollama connection failures."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Test", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        # Make client initialization fail
        mock_client_class.side_effect = Exception("Connection refused")

        # Test connection error
        with pytest.raises(Exception) as exc_info:
            trans_ollama(
                "en",
                "es",
                "http://localhost:11434",
                None,
                "test.po",
                False,
                "test-model",
            )

        assert "Connection refused" in str(exc_info.value)

    @patch("transpolibre.lib.trans_ollama.update_pofile")
    @patch("ollama.Client")
    @patch("transpolibre.lib.trans_ollama.polib")
    @patch("os.path.isfile")
    def test_chat_error(self, mock_isfile, mock_polib, mock_client_class, mock_update):
        """Test handling of chat API errors."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Test", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        mock_client = Mock()
        mock_client.chat.side_effect = Exception("Model not found")
        mock_client_class.return_value = mock_client

        # Test chat error
        with pytest.raises(Exception) as exc_info:
            trans_ollama(
                "en",
                "es",
                "http://localhost:11434",
                None,
                "test.po",
                False,
                "test-model",
            )

        assert "Model not found" in str(exc_info.value)

    @patch("transpolibre.lib.trans_ollama.update_pofile")
    @patch("ollama.Client")
    @patch("transpolibre.lib.trans_ollama.polib")
    @patch("os.path.isfile")
    def test_different_models(
        self, mock_isfile, mock_polib, mock_client_class, mock_update
    ):
        """Test using different Ollama models."""
        # Test different models
        models = ["llama2", "mistral", "aya-expanse:32b", "custom-model:latest"]

        for model in models:
            # Setup mocks fresh for each iteration
            mock_isfile.return_value = True

            mock_po = Mock()
            mock_entry = Mock(msgid="Test", msgstr="")
            mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
            mock_polib.pofile.return_value = mock_po

            mock_client = Mock()
            mock_client.chat.return_value = {"message": {"content": "Translated"}}
            mock_client_class.return_value = mock_client

            # Reset the update mock for each iteration
            mock_update.reset_mock()

            trans_ollama(
                "en", "es", "http://localhost:11434", None, "test.po", False, model
            )

            # Verify correct model was used
            mock_client.chat.assert_called_once()
            call_args, call_kwargs = mock_client.chat.call_args
            assert call_kwargs.get("model") == model

    @patch("transpolibre.lib.trans_ollama.update_pofile")
    @patch("ollama.Client")
    @patch("transpolibre.lib.trans_ollama.polib")
    @patch("os.path.isfile")
    def test_different_language_pairs(
        self, mock_isfile, mock_polib, mock_client_class, mock_update
    ):
        """Test various language pair combinations."""
        # Test different language pairs
        pairs = [("en", "es"), ("fr", "de"), ("ja", "ko"), ("ar", "hi")]

        for src, tgt in pairs:
            # Setup mocks fresh for each iteration
            mock_isfile.return_value = True

            mock_po = Mock()
            mock_entry = Mock(msgid="Test", msgstr="")
            mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
            mock_polib.pofile.return_value = mock_po

            mock_client = Mock()
            mock_client.chat.return_value = {"message": {"content": "Translated"}}
            mock_client_class.return_value = mock_client

            # Reset the update mock for each iteration
            mock_update.reset_mock()

            trans_ollama(
                src, tgt, "http://localhost:11434", None, "test.po", False, "test-model"
            )

            # Verify languages in prompt
            mock_client.chat.assert_called_once()
            call_args, call_kwargs = mock_client.chat.call_args
            messages = call_kwargs.get("messages", [])
            assert len(messages) > 0
            # Check the user message (after system message)
            user_prompt = (
                messages[1].get("content", "")
                if len(messages) > 1
                else messages[0].get("content", "")
            )
            # The prompt should contain language information
            assert "Translate from" in user_prompt
            assert (
                "Test" in user_prompt
            )  # The text to translate should be in the prompt

    @patch("transpolibre.lib.trans_ollama.update_pofile")
    @patch("ollama.Client")
    @patch("transpolibre.lib.trans_ollama.polib")
    @patch("os.path.isfile")
    def test_empty_response(
        self, mock_isfile, mock_polib, mock_client_class, mock_update
    ):
        """Test handling of empty response from Ollama."""
        # Setup mocks
        mock_isfile.return_value = True

        mock_po = Mock()
        mock_entry = Mock(msgid="Test", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        mock_client = Mock()
        mock_client.chat.return_value = {"message": {"content": ""}}
        mock_client_class.return_value = mock_client

        # Test empty response
        trans_ollama(
            "en", "es", "http://localhost:11434", None, "test.po", False, "test-model"
        )

        # Should still update with empty string
        mock_update.assert_called_once_with("test.po", "Test", "")
