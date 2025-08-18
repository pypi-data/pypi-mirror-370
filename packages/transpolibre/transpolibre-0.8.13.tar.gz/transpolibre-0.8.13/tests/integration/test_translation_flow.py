"""
Integration tests for end-to-end translation workflows.
"""

import os
import tempfile
import pytest
import polib
from unittest.mock import patch, Mock

from transpolibre.main import main


class TestTranslationFlow:
    """Test end-to-end translation workflows."""

    @patch("transpolibre.main.parse_arguments")
    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_complete_po_file_translation(
        self, mock_lt_api, mock_parse_args, temp_po_file
    ):
        """Test translating entire PO file end-to-end."""
        # Setup mock arguments
        mock_args = Mock(
            list=False,
            file=temp_po_file,
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

        # Setup LibreTranslate mock
        mock_lt_instance = Mock()
        translations = {
            "Hello World": "Hola Mundo",
            "This is a test message": "Este es un mensaje de prueba",
            "Multi-line\nmessage\nhere": "Mensaje de\nvarias\nlíneas",
        }
        mock_lt_instance.translate.side_effect = (
            lambda text, src, tgt: translations.get(text, "Translated")
        )
        mock_lt_api.return_value = mock_lt_instance

        # Run translation
        main()

        # Verify translations were applied
        po = polib.pofile(temp_po_file)
        assert po.find("Hello World").msgstr == "Hola Mundo"
        assert (
            po.find("This is a test message").msgstr == "Este es un mensaje de prueba"
        )
        assert (
            po.find("Multi-line\nmessage\nhere").msgstr == "Mensaje de\nvarias\nlíneas"
        )
        # Already translated entry should remain unchanged
        assert (
            po.find("Welcome to the application").msgstr == "Bienvenido a la aplicación"
        )

    @patch("transpolibre.main.parse_arguments")
    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_partial_translation_resume(self, mock_lt_api, mock_parse_args):
        """Test resuming partial translations."""
        # Create a partially translated PO file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".po", delete=False, encoding="utf-8"
        ) as f:
            po = polib.POFile()
            po.metadata = {"Language": "en"}

            # Mix of translated and untranslated entries
            po.append(polib.POEntry(msgid="First", msgstr="Primero"))  # Already done
            po.append(polib.POEntry(msgid="Second", msgstr=""))  # Needs translation
            po.append(polib.POEntry(msgid="Third", msgstr="Tercero"))  # Already done
            po.append(polib.POEntry(msgid="Fourth", msgstr=""))  # Needs translation

            po.save(f.name)
            temp_file = f.name

        try:
            # Setup mock arguments
            mock_args = Mock(
                list=False,
                file=temp_file,
                engine="libretranslate",
                source_lang="en",
                target_lang="es",
                url="http://localhost:8000",
                api_key=None,
                overwrite=False,  # Don't overwrite existing
                debug=False,
                verbose=0,
            )
            mock_parse_args.return_value = mock_args

            # Setup LibreTranslate mock
            mock_lt_instance = Mock()
            mock_lt_instance.translate.side_effect = ["Segundo", "Cuarto"]
            mock_lt_api.return_value = mock_lt_instance

            # Run translation
            main()

            # Verify only missing translations were done
            po = polib.pofile(temp_file)
            assert po.find("First").msgstr == "Primero"  # Unchanged
            assert po.find("Second").msgstr == "Segundo"  # Newly translated
            assert po.find("Third").msgstr == "Tercero"  # Unchanged
            assert po.find("Fourth").msgstr == "Cuarto"  # Newly translated

            # Verify API was called only for missing translations
            assert mock_lt_instance.translate.call_count == 2

        finally:
            os.unlink(temp_file)

    @patch("transpolibre.main.parse_arguments")
    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    @patch("ollama.Client")
    def test_engine_switching_workflow(
        self, mock_ollama_client, mock_lt_api, mock_parse_args
    ):
        """Test switching between engines for the same file."""
        # Create a test PO file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".po", delete=False, encoding="utf-8"
        ) as f:
            po = polib.POFile()
            po.metadata = {"Language": "en"}
            po.append(polib.POEntry(msgid="Test message", msgstr=""))
            po.save(f.name)
            temp_file = f.name

        try:
            # First, translate with LibreTranslate
            mock_args = Mock(
                list=False,
                file=temp_file,
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

            mock_lt_instance = Mock()
            mock_lt_instance.translate.return_value = "Mensaje de prueba (LT)"
            mock_lt_api.return_value = mock_lt_instance

            main()

            # Verify LibreTranslate translation
            po = polib.pofile(temp_file)
            assert po.find("Test message").msgstr == "Mensaje de prueba (LT)"

            # Now switch to Ollama and overwrite
            mock_args.engine = "ollama"
            mock_args.url = "http://localhost:11434"
            mock_args.model = "test-model"
            mock_args.overwrite = True  # Overwrite previous translation

            mock_ollama_instance = Mock()
            mock_ollama_instance.chat.return_value = {
                "message": {"content": "Mensaje de prueba (Ollama)"}
            }
            mock_ollama_client.return_value = mock_ollama_instance

            main()

            # Verify Ollama translation overwrote the previous one
            po = polib.pofile(temp_file)
            assert po.find("Test message").msgstr == "Mensaje de prueba (Ollama)"

        finally:
            os.unlink(temp_file)

    @patch("transpolibre.main.parse_arguments")
    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_error_recovery_workflow(self, mock_lt_api, mock_parse_args):
        """Test recovery from errors during translation."""
        # Create a test PO file with multiple entries
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".po", delete=False, encoding="utf-8"
        ) as f:
            po = polib.POFile()
            po.metadata = {"Language": "en"}

            for i in range(5):
                po.append(polib.POEntry(msgid=f"Message {i}", msgstr=""))

            po.save(f.name)
            temp_file = f.name

        try:
            # Setup mock arguments
            mock_args = Mock(
                list=False,
                file=temp_file,
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

            # Setup LibreTranslate mock to fail on third message
            mock_lt_instance = Mock()
            mock_lt_instance.translate.side_effect = [
                "Mensaje 0",
                "Mensaje 1",
                Exception("API Error"),  # Fail on Message 2
                "Mensaje 3",
                "Mensaje 4",
            ]
            mock_lt_api.return_value = mock_lt_instance

            # Run translation (should fail but save partial progress)
            with pytest.raises(Exception):
                main()

            # Verify partial progress was saved
            po = polib.pofile(temp_file)
            assert po.find("Message 0").msgstr == "Mensaje 0"
            assert po.find("Message 1").msgstr == "Mensaje 1"
            assert po.find("Message 2").msgstr == ""  # Failed, not translated
            assert po.find("Message 3").msgstr == ""  # Not reached
            assert po.find("Message 4").msgstr == ""  # Not reached

            # Now fix the API and resume
            mock_lt_instance.translate.side_effect = [
                "Mensaje 2",
                "Mensaje 3",
                "Mensaje 4",
            ]

            # Run again to complete translation
            main()

            # Verify all translations completed
            po = polib.pofile(temp_file)
            for i in range(5):
                assert po.find(f"Message {i}").msgstr == f"Mensaje {i}"

        finally:
            os.unlink(temp_file)

    @patch("transpolibre.main.parse_arguments")
    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_url_email_handling_workflow(
        self,
        mock_lt_api,
        mock_parse_args,
        temp_po_file_with_urls,
        temp_po_file_with_emails,
    ):
        """Test handling of URLs and emails in translation workflow."""
        # Test URL handling
        mock_args = Mock(
            list=False,
            file=temp_po_file_with_urls,
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

        mock_lt_instance = Mock()
        mock_lt_instance.translate.side_effect = ["Documentación", "nuestro sitio web"]
        mock_lt_api.return_value = mock_lt_instance

        main()

        # Verify URLs preserved, text translated
        po = polib.pofile(temp_po_file_with_urls)
        entry1 = po.find("`Documentation <https://example.com/docs>`_")
        assert "`Documentación <https://example.com/docs>`_" in entry1.msgstr

        # Test email handling (should not translate)
        mock_args.file = temp_po_file_with_emails
        mock_lt_instance.translate.reset_mock()
        # When email is detected, trans_msg returns the original message
        # but update_pofile sets it as msgstr. The mock should not be called.
        mock_lt_instance.translate.return_value = "Should not be called"

        main()

        # Verify emails caused no translation
        po = polib.pofile(temp_po_file_with_emails)
        entry1 = po.find("Contact us at <support@example.com>")
        # Email detection returns original message, which gets set as msgstr
        assert entry1.msgstr == "Contact us at <support@example.com>"

        # API should not have been called for emails
        mock_lt_instance.translate.assert_not_called()

    @patch("transpolibre.main.parse_arguments")
    @patch("torch.cuda.empty_cache")
    @patch("torch.cuda.set_device")
    @patch("torch.cuda.is_available")
    @patch("torch.device")
    @patch("torch.set_float32_matmul_precision")
    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    def test_local_model_batch_workflow(
        self,
        mock_tokenizer_class,
        mock_model_class,
        mock_set_precision,
        mock_device,
        mock_cuda_available,
        mock_cuda_set_device,
        mock_cuda_empty_cache,
        mock_parse_args,
    ):
        """Test local model batch processing workflow."""
        # Create PO file with 20 entries (more than batch size of 16)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".po", delete=False, encoding="utf-8"
        ) as f:
            po = polib.POFile()
            po.metadata = {"Language": "en"}

            for i in range(20):
                po.append(polib.POEntry(msgid=f"Message {i}", msgstr=""))

            po.save(f.name)
            temp_file = f.name

        try:
            # Setup mock arguments
            mock_args = Mock(
                list=False,
                file=temp_file,
                engine="local",
                source_lang="en",
                target_lang="es",
                overwrite=False,
                model="test-model",
                cuda_device=0,
                device="cpu",
                debug=False,
                verbose=0,
            )
            mock_parse_args.return_value = mock_args

            # Setup device mocks
            mock_cuda_available.return_value = False
            mock_device_instance = Mock()
            mock_device.return_value = mock_device_instance

            # Setup tokenizer mock
            mock_tokenizer = Mock()
            mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

            # Create a mock tensor-like object with a to() method and keys() for unpacking
            mock_tensor = Mock()
            mock_tensor.to = Mock(return_value=mock_tensor)
            mock_tensor.keys = Mock(return_value=["input_ids", "attention_mask"])
            mock_tensor.__getitem__ = Mock(side_effect=lambda x: Mock())
            mock_tokenizer.return_value = mock_tensor

            # Create translations for both batches
            batch1_translations = [
                f"Translate this text from English to Spanish. English:\nMessage {i}\nSpanish: Mensaje {i}"
                for i in range(16)
            ]
            batch2_translations = [
                f"Translate this text from English to Spanish. English:\nMessage {i}\nSpanish: Mensaje {i}"
                for i in range(16, 20)
            ]
            mock_tokenizer.batch_decode.side_effect = [
                batch1_translations,
                batch2_translations,
            ]

            # Setup model mock
            mock_model = Mock()
            mock_model.to.return_value = mock_model
            mock_model.generate.return_value = Mock()
            mock_model_class.from_pretrained.return_value = mock_model

            # Run translation
            main()

            # Verify all 20 entries were translated
            po = polib.pofile(temp_file)
            for i in range(20):
                assert po.find(f"Message {i}").msgstr == f"Mensaje {i}"

            # Verify batching occurred
            assert mock_tokenizer.call_count == 2  # Two batches
            assert mock_model.generate.call_count == 2

        finally:
            os.unlink(temp_file)

    @patch("transpolibre.main.parse_arguments")
    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_unicode_preservation_workflow(self, mock_lt_api, mock_parse_args):
        """Test Unicode preservation throughout translation workflow."""
        # Create PO file with Unicode content
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".po", delete=False, encoding="utf-8"
        ) as f:
            po = polib.POFile()
            po.metadata = {
                "Language": "en",
                "Content-Type": "text/plain; charset=UTF-8",
            }

            po.append(polib.POEntry(msgid="Hello 世界 🌍", msgstr=""))
            po.append(polib.POEntry(msgid="مرحبا بالعالم", msgstr=""))
            po.append(polib.POEntry(msgid="Привет мир", msgstr=""))

            po.save(f.name)
            temp_file = f.name

        try:
            # Setup mock arguments
            mock_args = Mock(
                list=False,
                file=temp_file,
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

            # Setup LibreTranslate mock
            mock_lt_instance = Mock()
            mock_lt_instance.translate.side_effect = [
                "Hola 世界 🌍",
                "مرحبا بالعالم traducido",
                "Привет мир traducido",
            ]
            mock_lt_api.return_value = mock_lt_instance

            # Run translation
            main()

            # Verify Unicode preserved
            po = polib.pofile(temp_file, encoding="utf-8")
            assert po.find("Hello 世界 🌍").msgstr == "Hola 世界 🌍"
            assert po.find("مرحبا بالعالم").msgstr == "مرحبا بالعالم traducido"
            assert po.find("Привет мир").msgstr == "Привет мир traducido"

            # Verify encoding metadata preserved
            assert po.metadata.get("Content-Type") == "text/plain; charset=UTF-8"

        finally:
            os.unlink(temp_file)

    @patch("transpolibre.main.parse_arguments")
    @patch("transpolibre.lib.trans_msg.LibreTranslateAPI")
    def test_multiline_translation_workflow(self, mock_lt_api, mock_parse_args):
        """Test multiline message translation workflow."""
        # Create PO file with multiline entries
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".po", delete=False, encoding="utf-8"
        ) as f:
            po = polib.POFile()
            po.metadata = {"Language": "en"}

            po.append(
                polib.POEntry(msgid="First line\nSecond line\nThird line", msgstr="")
            )
            po.append(polib.POEntry(msgid="Single line", msgstr=""))

            po.save(f.name)
            temp_file = f.name

        try:
            # Setup mock arguments
            mock_args = Mock(
                list=False,
                file=temp_file,
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

            # Setup LibreTranslate mock
            mock_lt_instance = Mock()
            mock_lt_instance.translate.side_effect = [
                "Primera línea\nSegunda línea\nTercera línea",
                "Línea única",
            ]
            mock_lt_api.return_value = mock_lt_instance

            # Run translation
            main()

            # Verify multiline preserved
            po = polib.pofile(temp_file)
            assert (
                po.find("First line\nSecond line\nThird line").msgstr
                == "Primera línea\nSegunda línea\nTercera línea"
            )
            assert po.find("Single line").msgstr == "Línea única"

        finally:
            os.unlink(temp_file)
