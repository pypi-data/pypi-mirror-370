# src/transpolibre/lib/trans_tsfile_local.py

import gettext
import logging
import os
import re
import tempfile
import shutil
from typing import List, Tuple, Dict, Any, Optional

from translate.storage import ts2 as ts

from transpolibre.lib.get_lang_name import get_lang_name
from transpolibre.lib.qt_translator import QtTranslator

LOCALE_DIR = "locale"

gettext.bindtextdomain("transpolibre", LOCALE_DIR)
gettext.textdomain("transpolibre")
_ = gettext.gettext


def trans_tsfile_local(
    SRCISO: str,
    TARGETISO: str,
    TSFILE: str,
    OVERWRITE: bool,
    MODEL: str,
    CUDA_DEVICE: int,
    DEVICE: str,
) -> None:
    """
    Translate a Qt .ts file using local transformer models.

    Args:
        SRCISO: Source language ISO code
        TARGETISO: Target language ISO code
        TSFILE: Path to the .ts file to translate
        OVERWRITE: Whether to overwrite existing translations
        MODEL: The transformer model to use
        CUDA_DEVICE: CUDA device index
        DEVICE: Device type (auto, cpu, gpu)
    """
    logging.info(_("Local Torch for .ts file"))

    if not os.path.isfile(TSFILE):
        raise FileNotFoundError(
            _("The specified TS file does not exist or is not a file: " + TSFILE)
        )

    logging.debug(_("Read TS file: ") + TSFILE)

    # Parse the .ts file
    try:
        store = ts.tsfile.parsefile(TSFILE)
    except Exception as e:
        raise ValueError(_("Failed to parse TS file: ") + str(e))

    # Preserve the file's existing target language locale
    logging.debug(f"Preserving file's target language: {store.gettargetlanguage()}")

    # Initialize Qt translator
    qt_translator = QtTranslator()

    # Collect all messages that need translation
    units_to_translate: List[Tuple[Any, str, str, bool]] = (
        []
    )  # (unit, text, context, is_menu_item)

    # Track current context
    current_context = None

    for unit in store.units:
        # Get context name if available
        if hasattr(unit, "getcontext"):
            context = unit.getcontext()
            if context != current_context:
                # Reset accelerator tracking for new context
                if context:
                    qt_translator.reset_context(context)
                current_context = context
        else:
            current_context = "default"

        # Skip non-translatable units
        if not unit.istranslatable():
            continue

        # Skip obsolete units
        if unit.isobsolete():
            continue

        # Skip if already translated and not overwriting
        if unit.istranslated() and not OVERWRITE:
            continue

        # Handle plural forms
        if isinstance(unit.source, list) or "multistring" in str(type(unit.source)):
            # For plural forms, we'll translate each form separately
            source_forms = (
                unit.source if isinstance(unit.source, list) else [str(unit.source)]
            )
            for source_text in source_forms:
                if source_text and source_text.strip():
                    is_menu_item = "&" in source_text and "&&" not in source_text
                    units_to_translate.append(
                        (
                            unit,
                            str(source_text),
                            current_context or "default",
                            is_menu_item,
                        )
                    )
        else:
            # Regular message
            source_text = unit.source
            if source_text and source_text.strip():
                is_menu_item = "&" in source_text and "&&" not in source_text
                units_to_translate.append(
                    (unit, source_text, current_context or "default", is_menu_item)
                )

    if not units_to_translate:
        logging.info(_("No translations needed."))
        return

    # Import torch and transformers
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    # Setup device
    device: torch.device
    if DEVICE == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    elif DEVICE == "cpu":
        device = torch.device("cpu")
    elif DEVICE == "gpu":
        if not torch.cuda.is_available():
            logging.warning(
                _("GPU requested but CUDA is not available. Falling back to CPU.")
            )
            device = torch.device("cpu")
        else:
            device = torch.device(f"cuda:{CUDA_DEVICE}")
            torch.cuda.set_device(CUDA_DEVICE)

    torch.set_float32_matmul_precision("high")

    # Initialize model and tokenizer variables for cleanup
    model = None
    tokenizer = None

    try:
        # Load model and tokenizer with error handling
        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL, padding_side="left")
            model = AutoModelForCausalLM.from_pretrained(MODEL)
            model = model.to(device)  # type: ignore[arg-type]
        except Exception as e:
            logging.error(f"Failed to load model '{MODEL}': {e}")
            raise ValueError(
                f"Could not load model '{MODEL}'. Please check the model name and your internet connection."
            )

        # Process in batches
        batch_size: int = 16
        translated_count = 0
        plural_translated_count = 0

        # Create a mapping to track which units have been processed
        processed_units = set()
        plural_translations: Dict[int, List[str]] = {}  # Track plural form translations

        for i in range(0, len(units_to_translate), batch_size):
            batch = units_to_translate[i : i + batch_size]

            # Process each item in batch
            batch_items: List[Tuple[Any, str, str, bool, str, Optional[str]]] = []
            prompts: List[str] = []

            for unit, text, context, is_menu_item in batch:
                # Extract accelerator and protect placeholders
                clean_text, accel_letter = qt_translator.extract_accelerator(text)
                protected = qt_translator.protect_placeholders(clean_text)

                # Build prompt for local model
                # Local models need clear instructions
                if re.search(r"<QT_P\d+/>|<QT_PN/>|<QT_VAR_\w+/>", protected):
                    prompt = (
                        f"Translate from {get_lang_name(SRCISO)} to {get_lang_name(TARGETISO)}. "
                        f"Keep all <QT_*> tokens exactly as they appear:\n{protected}"
                    )
                else:
                    prompt = f"Translate from {get_lang_name(SRCISO)} to {get_lang_name(TARGETISO)}:\n{protected}"

                prompts.append(prompt)
                batch_items.append(
                    (unit, text, context, is_menu_item, protected, accel_letter)
                )

            # Tokenize and generate translations
            inputs = tokenizer(
                prompts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            ).to(device)

            with torch.no_grad():
                outputs = model.generate(**inputs, max_new_tokens=512)

            translations = tokenizer.batch_decode(outputs, skip_special_tokens=True)

            # Apply translations to units
            for (
                unit,
                source_text,
                context,
                is_menu_item,
                protected,
                accel_letter,
            ), translation in zip(batch_items, translations):
                translation = translation.strip()

                # Extract the actual translation from the generated text
                # Local models often include the prompt in their response
                if ":" in translation and get_lang_name(TARGETISO) in translation:
                    # Try to extract after the target language marker
                    parts = translation.split(f"{get_lang_name(TARGETISO)}:")
                    if len(parts) > 1:
                        translation = parts[-1].strip()
                elif ":" in translation:
                    # Fallback: extract after the last colon
                    parts = translation.split(":")
                    if len(parts) > 1:
                        translation = parts[-1].strip()

                # Restore Qt elements
                translation = qt_translator.restore_placeholders(translation)
                if accel_letter:
                    translation = qt_translator.assign_accelerator(
                        translation, accel_letter, context
                    )

                # Validate
                warnings = qt_translator.validate_translation(
                    source_text, translation, context
                )
                for warning in warnings:
                    logging.warning(warning)

                # Handle plural forms specially
                if isinstance(unit.source, list) or "multistring" in str(
                    type(unit.source)
                ):
                    # Store plural translations
                    if id(unit) not in plural_translations:
                        plural_translations[id(unit)] = []
                    plural_translations[id(unit)].append(translation)
                else:
                    # Regular message - apply directly
                    unit.target = translation
                    if id(unit) not in processed_units:
                        translated_count += 1
                        processed_units.add(id(unit))

                logging.debug(f"Source: {source_text}\nTranslation: {translation}\n")
                logging.info(_("Original:    ") + source_text)
                logging.info(_("Translation: ") + translation + "\n")

            # Clean up memory after each batch
            del inputs
            del outputs
            torch.cuda.empty_cache()

        # Apply plural translations
        for unit in store.units:
            if id(unit) in plural_translations:
                unit.target = plural_translations[id(unit)]
                plural_translated_count += 1

    finally:
        # Clean up model and tokenizer to prevent memory leak
        if model is not None:
            del model
        if tokenizer is not None:
            del tokenizer
        # Final cache clear
        torch.cuda.empty_cache()

    # Save the file atomically
    try:
        # Preserve original file permissions
        original_stat = os.stat(TSFILE)

        # Create temporary file in the same directory as the target
        with tempfile.NamedTemporaryFile(
            mode="wb",
            delete=False,
            suffix=".ts",
            dir=os.path.dirname(os.path.abspath(TSFILE)),
        ) as tmp_file:
            temp_path = tmp_file.name

        # Save to temporary file
        store.savefile(temp_path)

        # Preserve the original file's permissions on the temp file
        os.chmod(temp_path, original_stat.st_mode)

        # Atomically replace the original file
        shutil.move(temp_path, TSFILE)

        # Log all accumulated warnings
        all_warnings = qt_translator.get_all_warnings()
        if all_warnings:
            logging.warning(_("Qt translation warnings:"))
            for warning in all_warnings:
                logging.warning(f"  - {warning}")

        logging.info(
            _("Translation complete. ")
            + f"Translated: {translated_count}, "
            + f"Plurals: {plural_translated_count}, "
            + f"Warnings: {len(all_warnings)}"
        )

    except Exception as e:
        # Clean up temporary file if it exists
        if "temp_path" in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise IOError(_("Failed to save TS file: ") + str(e))
