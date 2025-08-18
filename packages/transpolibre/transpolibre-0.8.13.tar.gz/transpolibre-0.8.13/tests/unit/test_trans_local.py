"""
Unit tests for the trans_local module.
"""

import sys
from unittest.mock import MagicMock

# Mock transformers module to avoid import issues
sys.modules["transformers"] = MagicMock()

import pytest  # noqa: E402
from unittest.mock import Mock, patch  # noqa: E402

from transpolibre.lib.trans_local import trans_local  # noqa: E402


class TestTransLocal:
    """Test local model translation."""

    def test_file_not_found(self):
        """Test FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError) as exc_info:
            trans_local(
                "en",
                "es",
                "/non/existent/file.po",
                False,
                "ModelSpace/GemmaX2-28-9B-v0.1",
                0,
                "auto",
            )

        assert "does not exist" in str(exc_info.value)
        assert "/non/existent/file.po" in str(exc_info.value)

    @patch("transpolibre.lib.trans_local.update_pofile")
    @patch("torch.cuda.empty_cache")
    @patch("torch.cuda.set_device")
    @patch("torch.cuda.is_available")
    @patch("torch.device")
    @patch("torch.set_float32_matmul_precision")
    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    @patch("transpolibre.lib.trans_local.polib")
    @patch("os.path.isfile")
    def test_device_auto_cuda_available(
        self,
        mock_isfile,
        mock_polib,
        mock_tokenizer_class,
        mock_model_class,
        mock_set_precision,
        mock_device,
        mock_cuda_available,
        mock_cuda_set_device,
        mock_cuda_empty_cache,
        mock_update,
    ):
        """Test auto device selection with CUDA available."""
        # Setup mocks
        mock_isfile.return_value = True
        mock_cuda_available.return_value = True
        mock_device.return_value = Mock()

        # Setup PO file mock
        mock_po = Mock()
        mock_entry = Mock(msgid="Hello", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        # Setup tokenizer and model mocks
        mock_tokenizer = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        # Create a mock tensor-like object with a to() method and keys() for unpacking
        mock_tensor = Mock()
        mock_tensor.to = Mock(return_value=mock_tensor)
        mock_tensor.keys = Mock(return_value=["input_ids", "attention_mask"])
        mock_tensor.__getitem__ = Mock(side_effect=lambda x: Mock())
        mock_tokenizer.return_value = mock_tensor

        mock_tokenizer.batch_decode.return_value = [
            "Translate this text from English to Spanish. English:\nHello\nSpanish: Hola"
        ]

        mock_model = Mock()
        mock_model.to.return_value = mock_model
        mock_model.generate.return_value = Mock()
        mock_model_class.from_pretrained.return_value = mock_model

        # Test auto device selection
        trans_local("en", "es", "test.po", False, "test-model", 0, "auto")

        # Verify CUDA device was selected
        mock_cuda_available.assert_called_once()
        mock_device.assert_called_with("cuda")

    @patch("transpolibre.lib.trans_local.update_pofile")
    @patch("torch.cuda.empty_cache")
    @patch("torch.cuda.set_device")
    @patch("torch.cuda.is_available")
    @patch("torch.device")
    @patch("torch.set_float32_matmul_precision")
    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    @patch("transpolibre.lib.trans_local.polib")
    @patch("os.path.isfile")
    def test_device_auto_cuda_unavailable(
        self,
        mock_isfile,
        mock_polib,
        mock_tokenizer_class,
        mock_model_class,
        mock_set_precision,
        mock_device,
        mock_cuda_available,
        mock_cuda_set_device,
        mock_cuda_empty_cache,
        mock_update,
    ):
        """Test auto device selection with CUDA unavailable."""
        # Setup mocks
        mock_isfile.return_value = True
        mock_cuda_available.return_value = False
        mock_device.return_value = Mock()

        # Setup PO file mock
        mock_po = Mock()
        mock_entry = Mock(msgid="Hello", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        # Setup tokenizer and model mocks
        mock_tokenizer = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        # Create a mock tensor-like object with a to() method and keys() for unpacking
        mock_tensor = Mock()
        mock_tensor.to = Mock(return_value=mock_tensor)
        mock_tensor.keys = Mock(return_value=["input_ids", "attention_mask"])
        mock_tensor.__getitem__ = Mock(side_effect=lambda x: Mock())
        mock_tokenizer.return_value = mock_tensor

        mock_tokenizer.batch_decode.return_value = [
            "Translate this text from English to Spanish. English:\nHello\nSpanish: Hola"
        ]

        mock_model = Mock()
        mock_model.to.return_value = mock_model
        mock_model.generate.return_value = Mock()
        mock_model_class.from_pretrained.return_value = mock_model

        # Test auto device selection
        trans_local("en", "es", "test.po", False, "test-model", 0, "auto")

        # Verify CPU device was selected
        mock_cuda_available.assert_called_once()
        mock_device.assert_called_with("cpu")

    @patch("transpolibre.lib.trans_local.update_pofile")
    @patch("torch.cuda.empty_cache")
    @patch("torch.cuda.set_device")
    @patch("torch.cuda.is_available")
    @patch("torch.device")
    @patch("torch.set_float32_matmul_precision")
    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    @patch("transpolibre.lib.trans_local.polib")
    @patch("os.path.isfile")
    @patch("transpolibre.lib.trans_local.logging")
    def test_device_gpu_cuda_unavailable(
        self,
        mock_logging,
        mock_isfile,
        mock_polib,
        mock_tokenizer_class,
        mock_model_class,
        mock_set_precision,
        mock_device,
        mock_cuda_available,
        mock_cuda_set_device,
        mock_cuda_empty_cache,
        mock_update,
    ):
        """Test GPU device selection when CUDA is unavailable."""
        # Setup mocks
        mock_isfile.return_value = True
        mock_cuda_available.return_value = False
        mock_device.return_value = Mock()

        # Setup PO file mock
        mock_po = Mock()
        mock_entry = Mock(msgid="Hello", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        # Setup tokenizer and model mocks
        mock_tokenizer = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        # Create a mock tensor-like object with a to() method and keys() for unpacking
        mock_tensor = Mock()
        mock_tensor.to = Mock(return_value=mock_tensor)
        mock_tensor.keys = Mock(return_value=["input_ids", "attention_mask"])
        mock_tensor.__getitem__ = Mock(side_effect=lambda x: Mock())
        mock_tokenizer.return_value = mock_tensor

        mock_tokenizer.batch_decode.return_value = [
            "Translate this text from English to Spanish. English:\nHello\nSpanish: Hola"
        ]

        mock_model = Mock()
        mock_model.to.return_value = mock_model
        mock_model.generate.return_value = Mock()
        mock_model_class.from_pretrained.return_value = mock_model

        # Test GPU device with no CUDA
        trans_local("en", "es", "test.po", False, "test-model", 0, "gpu")

        # Verify warning and fallback to CPU
        mock_logging.warning.assert_called_once()
        assert "GPU requested but CUDA is not available" in str(
            mock_logging.warning.call_args
        )
        mock_device.assert_called_with("cpu")

    @patch("transpolibre.lib.trans_local.update_pofile")
    @patch("torch.cuda.empty_cache")
    @patch("torch.cuda.set_device")
    @patch("torch.cuda.is_available")
    @patch("torch.device")
    @patch("torch.set_float32_matmul_precision")
    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    @patch("transpolibre.lib.trans_local.polib")
    @patch("os.path.isfile")
    def test_batch_processing(
        self,
        mock_isfile,
        mock_polib,
        mock_tokenizer_class,
        mock_model_class,
        mock_set_precision,
        mock_device,
        mock_cuda_available,
        mock_cuda_set_device,
        mock_cuda_empty_cache,
        mock_update,
    ):
        """Test batch translation processing."""
        # Setup mocks
        mock_isfile.return_value = True
        mock_cuda_available.return_value = False
        mock_device.return_value = Mock()

        # Create 20 entries to test batching (batch_size=16)
        mock_po = Mock()
        entries = [Mock(msgid=f"Message {i}", msgstr="") for i in range(20)]
        mock_po.__iter__ = Mock(return_value=iter(entries))
        mock_polib.pofile.return_value = mock_po

        # Setup tokenizer and model mocks
        mock_tokenizer = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        # Create a mock tensor-like object with a to() method and keys() for unpacking
        mock_tensor = Mock()
        mock_tensor.to = Mock(return_value=mock_tensor)
        mock_tensor.keys = Mock(return_value=["input_ids", "attention_mask"])
        mock_tensor.__getitem__ = Mock(side_effect=lambda x: Mock())
        mock_tokenizer.return_value = mock_tensor

        # Return translations for both batches
        translations_batch1 = [
            f"Translate this text from English to Spanish. English:\nMessage {i}\nSpanish: Mensaje {i}"
            for i in range(16)
        ]
        translations_batch2 = [
            f"Translate this text from English to Spanish. English:\nMessage {i}\nSpanish: Mensaje {i}"
            for i in range(16, 20)
        ]
        mock_tokenizer.batch_decode.side_effect = [
            translations_batch1,
            translations_batch2,
        ]

        mock_model = Mock()
        mock_model.to.return_value = mock_model
        mock_model.generate.return_value = Mock()
        mock_model_class.from_pretrained.return_value = mock_model

        # Test batch processing
        trans_local("en", "es", "test.po", False, "test-model", 0, "cpu")

        # Verify two batches were processed
        assert mock_tokenizer.call_count == 2  # Two batches
        assert mock_model.generate.call_count == 2
        # Now expects 3 calls: 2 from batches + 1 from finally block
        assert mock_cuda_empty_cache.call_count == 3

        # Verify all 20 entries were updated
        assert mock_update.call_count == 20

    @patch("transpolibre.lib.trans_local.update_pofile")
    @patch("torch.cuda.empty_cache")
    @patch("torch.cuda.set_device")
    @patch("torch.cuda.is_available")
    @patch("torch.device")
    @patch("torch.set_float32_matmul_precision")
    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    @patch("transpolibre.lib.trans_local.polib")
    @patch("os.path.isfile")
    def test_prompt_formatting(
        self,
        mock_isfile,
        mock_polib,
        mock_tokenizer_class,
        mock_model_class,
        mock_set_precision,
        mock_device,
        mock_cuda_available,
        mock_cuda_set_device,
        mock_cuda_empty_cache,
        mock_update,
    ):
        """Test translation prompt generation."""
        # Setup mocks
        mock_isfile.return_value = True
        mock_cuda_available.return_value = False
        mock_device.return_value = Mock()

        # Setup PO file mock
        mock_po = Mock()
        mock_entry = Mock(msgid="Hello World", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        # Setup tokenizer mock to capture prompts
        mock_tokenizer = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        tokenizer_inputs = []

        def capture_prompts(prompts, **kwargs):
            tokenizer_inputs.extend(prompts)
            # Return a mock tensor-like object with a to() method and keys() for unpacking
            mock_tensor = Mock()
            mock_tensor.to = Mock(return_value=mock_tensor)
            mock_tensor.keys = Mock(return_value=["input_ids", "attention_mask"])
            mock_tensor.__getitem__ = Mock(side_effect=lambda x: Mock())
            # Store the prompts as an attribute for later access
            mock_tensor.__dict__.update(kwargs)
            return mock_tensor

        mock_tokenizer.side_effect = capture_prompts
        mock_tokenizer.batch_decode.return_value = [
            "Translate this text from English to Spanish. English:\nHello World\nSpanish: Hola Mundo"
        ]

        mock_model = Mock()
        mock_model.to.return_value = mock_model
        mock_model.generate.return_value = Mock()
        mock_model_class.from_pretrained.return_value = mock_model

        # Test prompt formatting
        trans_local("en", "es", "test.po", False, "test-model", 0, "cpu")

        # Verify prompt format
        assert len(tokenizer_inputs) == 1
        expected_prompt = "Translate this text from English to Spanish. English:\nHello World\nSpanish:"
        assert tokenizer_inputs[0] == expected_prompt

    @patch("transpolibre.lib.trans_local.update_pofile")
    @patch("torch.cuda.empty_cache")
    @patch("torch.cuda.set_device")
    @patch("torch.cuda.is_available")
    @patch("torch.device")
    @patch("torch.set_float32_matmul_precision")
    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    @patch("transpolibre.lib.trans_local.polib")
    @patch("os.path.isfile")
    def test_skip_already_translated(
        self,
        mock_isfile,
        mock_polib,
        mock_tokenizer_class,
        mock_model_class,
        mock_set_precision,
        mock_device,
        mock_cuda_available,
        mock_cuda_set_device,
        mock_cuda_empty_cache,
        mock_update,
    ):
        """Test skipping already translated entries without overwrite."""
        # Setup mocks
        mock_isfile.return_value = True
        mock_cuda_available.return_value = False
        mock_device.return_value = Mock()

        # Setup PO file with mixed entries
        mock_po = Mock()
        mock_entry1 = Mock(msgid="Hello", msgstr="Hola")  # Already translated
        mock_entry2 = Mock(msgid="World", msgstr="")  # Not translated
        mock_po.__iter__ = Mock(return_value=iter([mock_entry1, mock_entry2]))
        mock_polib.pofile.return_value = mock_po

        # Setup tokenizer and model mocks
        mock_tokenizer = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        # Create a mock tensor-like object with a to() method and keys() for unpacking
        mock_tensor = Mock()
        mock_tensor.to = Mock(return_value=mock_tensor)
        mock_tensor.keys = Mock(return_value=["input_ids", "attention_mask"])
        mock_tensor.__getitem__ = Mock(side_effect=lambda x: Mock())
        mock_tokenizer.return_value = mock_tensor

        mock_tokenizer.batch_decode.return_value = [
            "Translate this text from English to Spanish. English:\nWorld\nSpanish: Mundo"
        ]

        mock_model = Mock()
        mock_model.to.return_value = mock_model
        mock_model.generate.return_value = Mock()
        mock_model_class.from_pretrained.return_value = mock_model

        # Test without overwrite
        trans_local("en", "es", "test.po", False, "test-model", 0, "cpu")

        # Should only translate the empty one
        assert mock_update.call_count == 1
        mock_update.assert_called_once_with("test.po", "World", "Mundo")

    @patch("transpolibre.lib.trans_local.update_pofile")
    @patch("torch.cuda.empty_cache")
    @patch("torch.cuda.set_device")
    @patch("torch.cuda.is_available")
    @patch("torch.device")
    @patch("torch.set_float32_matmul_precision")
    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    @patch("transpolibre.lib.trans_local.polib")
    @patch("os.path.isfile")
    def test_overwrite_mode(
        self,
        mock_isfile,
        mock_polib,
        mock_tokenizer_class,
        mock_model_class,
        mock_set_precision,
        mock_device,
        mock_cuda_available,
        mock_cuda_set_device,
        mock_cuda_empty_cache,
        mock_update,
    ):
        """Test overwrite mode retranslates existing entries."""
        # Setup mocks
        mock_isfile.return_value = True
        mock_cuda_available.return_value = False
        mock_device.return_value = Mock()

        # Setup PO file with translated entry
        mock_po = Mock()
        mock_entry = Mock(msgid="Hello", msgstr="Hola")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        # Setup tokenizer and model mocks
        mock_tokenizer = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        # Create a mock tensor-like object with a to() method and keys() for unpacking
        mock_tensor = Mock()
        mock_tensor.to = Mock(return_value=mock_tensor)
        mock_tensor.keys = Mock(return_value=["input_ids", "attention_mask"])
        mock_tensor.__getitem__ = Mock(side_effect=lambda x: Mock())
        mock_tokenizer.return_value = mock_tensor

        mock_tokenizer.batch_decode.return_value = [
            "Translate this text from English to Spanish. English:\nHello\nSpanish: Saludos"
        ]

        mock_model = Mock()
        mock_model.to.return_value = mock_model
        mock_model.generate.return_value = Mock()
        mock_model_class.from_pretrained.return_value = mock_model

        # Test with overwrite
        trans_local("en", "es", "test.po", True, "test-model", 0, "cpu")

        # Should retranslate
        assert mock_update.call_count == 1
        mock_update.assert_called_once_with("test.po", "Hello", "Saludos")

    @patch("transpolibre.lib.trans_local.update_pofile")
    @patch("torch.cuda.empty_cache")
    @patch("torch.cuda.set_device")
    @patch("torch.cuda.is_available")
    @patch("torch.device")
    @patch("torch.set_float32_matmul_precision")
    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    @patch("transpolibre.lib.trans_local.polib")
    @patch("os.path.isfile")
    @patch("transpolibre.lib.trans_local.logging")
    def test_no_translations_needed(
        self,
        mock_logging,
        mock_isfile,
        mock_polib,
        mock_tokenizer_class,
        mock_model_class,
        mock_set_precision,
        mock_device,
        mock_cuda_available,
        mock_cuda_set_device,
        mock_cuda_empty_cache,
        mock_update,
    ):
        """Test when no translations are needed."""
        # Setup mocks
        mock_isfile.return_value = True

        # Setup PO file with all translated entries
        mock_po = Mock()
        mock_entry1 = Mock(msgid="Hello", msgstr="Hola")
        mock_entry2 = Mock(msgid="World", msgstr="Mundo")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry1, mock_entry2]))
        mock_polib.pofile.return_value = mock_po

        # Test without overwrite
        trans_local("en", "es", "test.po", False, "test-model", 0, "cpu")

        # Should not load model or tokenizer
        mock_tokenizer_class.from_pretrained.assert_not_called()
        mock_model_class.from_pretrained.assert_not_called()

        # Should log no translations needed
        mock_logging.info.assert_any_call("No translations needed.")

    @patch("transpolibre.lib.trans_local.update_pofile")
    @patch("torch.cuda.empty_cache")
    @patch("torch.cuda.set_device")
    @patch("torch.cuda.is_available")
    @patch("torch.device")
    @patch("torch.set_float32_matmul_precision")
    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    @patch("transpolibre.lib.trans_local.polib")
    @patch("os.path.isfile")
    @patch("transpolibre.lib.trans_local.logging")
    def test_malformed_translation_output(
        self,
        mock_logging,
        mock_isfile,
        mock_polib,
        mock_tokenizer_class,
        mock_model_class,
        mock_set_precision,
        mock_device,
        mock_cuda_available,
        mock_cuda_set_device,
        mock_cuda_empty_cache,
        mock_update,
    ):
        """Test handling of malformed model output."""
        # Setup mocks
        mock_isfile.return_value = True
        mock_cuda_available.return_value = False
        mock_device.return_value = Mock()

        # Setup PO file mock
        mock_po = Mock()
        mock_entry = Mock(msgid="Hello", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        # Setup tokenizer and model mocks with malformed output
        mock_tokenizer = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        # Create a mock tensor-like object with a to() method and keys() for unpacking
        mock_tensor = Mock()
        mock_tensor.to = Mock(return_value=mock_tensor)
        mock_tensor.keys = Mock(return_value=["input_ids", "attention_mask"])
        mock_tensor.__getitem__ = Mock(side_effect=lambda x: Mock())
        mock_tokenizer.return_value = mock_tensor

        mock_tokenizer.batch_decode.return_value = [
            "This is malformed output without the expected format"
        ]

        mock_model = Mock()
        mock_model.to.return_value = mock_model
        mock_model.generate.return_value = Mock()
        mock_model_class.from_pretrained.return_value = mock_model

        # Test malformed output handling
        trans_local("en", "es", "test.po", False, "test-model", 0, "cpu")

        # Should log error
        mock_logging.error.assert_called_once()
        assert "does not contain the expected format" in str(
            mock_logging.error.call_args
        )

        # Should not update the file
        mock_update.assert_not_called()

    @patch("transpolibre.lib.trans_local.update_pofile")
    @patch("torch.cuda.empty_cache")
    @patch("torch.cuda.set_device")
    @patch("torch.cuda.is_available")
    @patch("torch.device")
    @patch("torch.set_float32_matmul_precision")
    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    @patch("transpolibre.lib.trans_local.polib")
    @patch("os.path.isfile")
    def test_cuda_device_selection(
        self,
        mock_isfile,
        mock_polib,
        mock_tokenizer_class,
        mock_model_class,
        mock_set_precision,
        mock_device,
        mock_cuda_available,
        mock_cuda_set_device,
        mock_cuda_empty_cache,
        mock_update,
    ):
        """Test specific CUDA device selection."""
        # Setup mocks
        mock_isfile.return_value = True
        mock_cuda_available.return_value = True
        mock_device.return_value = Mock()

        # Setup PO file mock
        mock_po = Mock()
        mock_entry = Mock(msgid="Hello", msgstr="")
        mock_po.__iter__ = Mock(return_value=iter([mock_entry]))
        mock_polib.pofile.return_value = mock_po

        # Setup tokenizer and model mocks
        mock_tokenizer = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        # Create a mock tensor-like object with a to() method and keys() for unpacking
        mock_tensor = Mock()
        mock_tensor.to = Mock(return_value=mock_tensor)
        mock_tensor.keys = Mock(return_value=["input_ids", "attention_mask"])
        mock_tensor.__getitem__ = Mock(side_effect=lambda x: Mock())
        mock_tokenizer.return_value = mock_tensor

        mock_tokenizer.batch_decode.return_value = [
            "Translate this text from English to Spanish. English:\nHello\nSpanish: Hola"
        ]

        mock_model = Mock()
        mock_model.to.return_value = mock_model
        mock_model.generate.return_value = Mock()
        mock_model_class.from_pretrained.return_value = mock_model

        # Test with specific CUDA device
        trans_local("en", "es", "test.po", False, "test-model", 2, "gpu")

        # Verify specific CUDA device was set
        mock_device.assert_called_with("cuda:2")
        mock_cuda_set_device.assert_called_with(2)
