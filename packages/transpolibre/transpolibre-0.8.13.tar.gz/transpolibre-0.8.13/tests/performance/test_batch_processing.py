"""
Performance and benchmark tests for batch processing.
"""

import time
import tempfile
import os
import pytest
import polib
from unittest.mock import patch, Mock
import psutil
import gc

from transpolibre.lib.trans_local import trans_local
from transpolibre.lib.trans_pofile import trans_pofile


class TestBatchPerformance:
    """Test batch processing performance."""

    @pytest.mark.performance
    def test_large_po_file_processing_time(self):
        """Test processing time for large PO files."""
        # Create a large PO file with 1000+ entries
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".po", delete=False, encoding="utf-8"
        ) as f:
            po = polib.POFile()
            po.metadata = {"Language": "en"}

            # Add 1000 entries
            for i in range(1000):
                po.append(
                    polib.POEntry(
                        msgid=f"Test message number {i} with some content", msgstr=""
                    )
                )

            po.save(f.name)
            temp_file = f.name

        try:
            with patch("transpolibre.lib.trans_msg.LibreTranslateAPI") as mock_api:
                # Mock fast translations
                mock_instance = Mock()
                mock_instance.translate.return_value = "Translated"
                mock_api.return_value = mock_instance

                # Measure translation time
                start_time = time.time()
                trans_pofile(
                    "en", "es", "http://localhost:8000", None, temp_file, False
                )
                end_time = time.time()

                processing_time = end_time - start_time
                entries_per_second = 1000 / processing_time

                # Assert performance threshold (at least 90 entries per second with mocked API)
                # Allow 10% tolerance for system variations and test suite overhead
                assert (
                    entries_per_second > 90
                ), f"Processing too slow: {entries_per_second:.2f} entries/sec"

                # Verify all entries were processed
                assert mock_instance.translate.call_count == 1000

        finally:
            os.unlink(temp_file)

    @pytest.mark.performance
    def test_memory_usage_during_batch(self):
        """Test memory usage doesn't grow unbounded during batch processing."""
        # Create a PO file with 500 entries
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".po", delete=False, encoding="utf-8"
        ) as f:
            po = polib.POFile()
            po.metadata = {"Language": "en"}

            for i in range(500):
                po.append(
                    polib.POEntry(
                        msgid=f"Message {i}" * 10, msgstr=""  # Longer messages
                    )
                )

            po.save(f.name)
            temp_file = f.name

        try:
            with patch("transpolibre.lib.trans_msg.LibreTranslateAPI") as mock_api:
                mock_instance = Mock()
                mock_instance.translate.return_value = "Translated" * 10
                mock_api.return_value = mock_instance

                # Get initial memory usage
                process = psutil.Process()
                gc.collect()
                initial_memory = process.memory_info().rss / 1024 / 1024  # MB

                # Process file
                trans_pofile(
                    "en", "es", "http://localhost:8000", None, temp_file, False
                )

                # Get final memory usage
                gc.collect()
                final_memory = process.memory_info().rss / 1024 / 1024  # MB

                memory_increase = final_memory - initial_memory

                # Assert memory increase is reasonable (less than 100MB for 500 entries)
                assert (
                    memory_increase < 100
                ), f"Memory usage increased by {memory_increase:.2f}MB"

        finally:
            os.unlink(temp_file)

    @pytest.mark.performance
    @pytest.mark.requires_cuda
    @patch("torch.cuda.empty_cache")
    @patch("torch.cuda.set_device")
    @patch("torch.cuda.is_available")
    @patch("torch.device")
    @patch("torch.set_float32_matmul_precision")
    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    def test_local_model_batch_size_efficiency(
        self,
        mock_tokenizer_class,
        mock_model_class,
        mock_set_precision,
        mock_device,
        mock_cuda_available,
        mock_cuda_set_device,
        mock_cuda_empty_cache,
    ):
        """Test that local model processes in efficient batch sizes."""
        # Create PO file with 100 entries
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".po", delete=False, encoding="utf-8"
        ) as f:
            po = polib.POFile()
            po.metadata = {"Language": "en"}

            for i in range(100):
                po.append(polib.POEntry(msgid=f"Message {i}", msgstr=""))

            po.save(f.name)
            temp_file = f.name

        try:
            # Setup mocks
            mock_cuda_available.return_value = True
            mock_device_instance = Mock()
            mock_device.return_value = mock_device_instance

            mock_tokenizer = Mock()
            mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

            # Track batch sizes
            batch_sizes = []

            def track_batch_size(prompts, **kwargs):
                batch_sizes.append(len(prompts))
                # Return a mock tensor-like object with a to() method and keys() for unpacking
                mock_tensor = Mock()
                mock_tensor.to = Mock(return_value=mock_tensor)
                mock_tensor.keys = Mock(return_value=["input_ids", "attention_mask"])
                mock_tensor.__getitem__ = Mock(side_effect=lambda x: Mock())
                return mock_tensor

            mock_tokenizer.side_effect = track_batch_size

            # Mock translations - need to provide enough batches
            all_translations = []
            for batch_num in range(7):  # 100 entries / 16 per batch = 7 batches
                batch_size = 16 if batch_num < 6 else 4  # Last batch has 4 entries
                batch_translations = [
                    f"Translate this text from English to Spanish. English:\nMessage {i}\nSpanish: Mensaje {i}"
                    for i in range(
                        batch_num * 16, min(batch_num * 16 + batch_size, 100)
                    )
                ]
                all_translations.append(batch_translations)

            mock_tokenizer.batch_decode.side_effect = all_translations

            mock_model = Mock()
            mock_model.to.return_value = mock_model
            mock_model.generate.return_value = Mock()
            mock_model_class.from_pretrained.return_value = mock_model

            # Process file
            start_time = time.time()
            trans_local("en", "es", temp_file, False, "test-model", 0, "gpu")
            end_time = time.time()

            # Verify batch sizes are optimal (16 except possibly last batch)
            expected_batches = 100 // 16 + (1 if 100 % 16 else 0)
            assert len(batch_sizes) == expected_batches

            # All complete batches should be size 16
            for batch_size in batch_sizes[:-1]:
                assert batch_size == 16

            # Last batch should be remainder
            if 100 % 16:
                assert batch_sizes[-1] == 100 % 16

            # Check processing time is reasonable
            processing_time = end_time - start_time
            assert processing_time < 5.0  # Should be fast with mocks

        finally:
            os.unlink(temp_file)

    @pytest.mark.performance
    def test_concurrent_file_processing(self):
        """Test processing multiple files doesn't cause race conditions."""
        import threading
        import queue

        # Create multiple PO files
        temp_files = []
        for file_idx in range(5):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=f"_{file_idx}.po", delete=False, encoding="utf-8"
            ) as f:
                po = polib.POFile()
                po.metadata = {"Language": "en"}

                for i in range(20):
                    po.append(
                        polib.POEntry(msgid=f"File {file_idx} Message {i}", msgstr="")
                    )

                po.save(f.name)
                temp_files.append(f.name)

        try:
            with patch("transpolibre.lib.trans_msg.LibreTranslateAPI") as mock_api:
                mock_instance = Mock()

                # Thread-safe counter for translations
                translation_count = {"count": 0}
                lock = threading.Lock()

                def translate_with_count(text, src, tgt):
                    with lock:
                        translation_count["count"] += 1
                    return f"Translated: {text}"

                mock_instance.translate.side_effect = translate_with_count
                mock_api.return_value = mock_instance

                # Process files concurrently
                errors = queue.Queue()

                def process_file(filepath):
                    try:
                        trans_pofile(
                            "en", "es", "http://localhost:8000", None, filepath, False
                        )
                    except Exception as e:
                        errors.put(e)

                threads = []
                start_time = time.time()

                for temp_file in temp_files:
                    thread = threading.Thread(target=process_file, args=(temp_file,))
                    thread.start()
                    threads.append(thread)

                for thread in threads:
                    thread.join(timeout=10)

                end_time = time.time()

                # Check no errors occurred
                assert (
                    errors.empty()
                ), f"Errors during concurrent processing: {list(errors.queue)}"

                # Verify all translations were done (5 files * 20 entries)
                assert translation_count["count"] == 100

                # Check performance (should complete in reasonable time)
                assert end_time - start_time < 10.0

                # Verify all files were updated correctly
                for temp_file in temp_files:
                    po = polib.pofile(temp_file)
                    for entry in po:
                        assert entry.msgstr.startswith("Translated:")

        finally:
            for temp_file in temp_files:
                os.unlink(temp_file)

    @pytest.mark.performance
    def test_translation_caching_efficiency(self):
        """Test that duplicate messages are handled efficiently."""
        # Create PO file with many duplicate messages
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".po", delete=False, encoding="utf-8"
        ) as f:
            po = polib.POFile()
            po.metadata = {"Language": "en"}

            # Add 100 entries, but only 10 unique messages
            unique_messages = [f"Unique message {i}" for i in range(10)]
            for i in range(100):
                po.append(polib.POEntry(msgid=unique_messages[i % 10], msgstr=""))

            po.save(f.name)
            temp_file = f.name

        try:
            with patch("transpolibre.lib.trans_msg.LibreTranslateAPI") as mock_api:
                mock_instance = Mock()

                # Track unique translations
                translated_messages = set()

                def track_translations(text, src, tgt):
                    translated_messages.add(text)
                    return f"Translated: {text}"

                mock_instance.translate.side_effect = track_translations
                mock_api.return_value = mock_instance

                # Process file
                start_time = time.time()
                trans_pofile(
                    "en", "es", "http://localhost:8000", None, temp_file, False
                )
                end_time = time.time()

                # In current implementation, each message is translated separately
                # This test documents current behavior (100 API calls for 100 entries)
                assert mock_instance.translate.call_count == 100

                # But we can verify processing is still fast
                processing_time = end_time - start_time
                assert processing_time < 2.0  # Should be very fast with mocks

                # Future optimization: implement caching to reduce API calls
                # assert len(translated_messages) == 10  # Only 10 unique translations needed

        finally:
            os.unlink(temp_file)

    @pytest.mark.performance
    def test_error_recovery_performance(self):
        """Test performance impact of error recovery."""
        # Create PO file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".po", delete=False, encoding="utf-8"
        ) as f:
            po = polib.POFile()
            po.metadata = {"Language": "en"}

            for i in range(50):
                po.append(polib.POEntry(msgid=f"Message {i}", msgstr=""))

            po.save(f.name)
            temp_file = f.name

        try:
            with patch("transpolibre.lib.trans_msg.LibreTranslateAPI") as mock_api:
                mock_instance = Mock()

                # Simulate intermittent failures
                call_count = {"count": 0}

                def translate_with_failures(text, src, tgt):
                    call_count["count"] += 1
                    # Fail every 10th call
                    if call_count["count"] % 10 == 0:
                        raise Exception("Simulated API error")
                    return f"Translated: {text}"

                mock_instance.translate.side_effect = translate_with_failures
                mock_api.return_value = mock_instance

                # Process file (will fail on some translations)
                start_time = time.time()

                # We expect this to raise an exception
                with pytest.raises(Exception):
                    trans_pofile(
                        "en", "es", "http://localhost:8000", None, temp_file, False
                    )

                end_time = time.time()

                # Even with errors, should fail fast
                assert end_time - start_time < 2.0

                # Verify partial progress was made
                po = polib.pofile(temp_file)
                translated_count = sum(1 for entry in po if entry.msgstr)

                # Should have translated some entries before first failure
                assert translated_count > 0
                assert translated_count < 50  # But not all

        finally:
            os.unlink(temp_file)
