# src/transpolibre/lib/trans_tsfile_ollama.py

import gettext
import logging
import os
import re
import tempfile
import shutil
from typing import Optional, Dict

from translate.storage import ts2 as ts
from dotenv import load_dotenv

from transpolibre.lib.get_lang_name import get_lang_name
from transpolibre.lib.qt_translator import QtTranslator

load_dotenv()

LOCALE_DIR = "locale"

gettext.bindtextdomain("transpolibre", LOCALE_DIR)
gettext.textdomain("transpolibre")
_ = gettext.gettext


def clean_ollama_response(response: str, original_text: str) -> str:
    """Safely remove extra text from Ollama responses without breaking valid translations."""
    cleaned = response.strip()

    # Only remove obvious prefixes with safety checks
    prefixes = [
        "Here is the translation:",
        "Here's the translation:",
        "The translation is:",
        "Translation:",
    ]

    for prefix in prefixes:
        if cleaned.startswith(prefix):
            after = cleaned[len(prefix) :]
            # Only remove if there's actual content after (not just whitespace)
            if after.strip():  # Has non-whitespace content
                cleaned = after.lstrip()
                break
            # If only whitespace or empty after prefix, keep original

    # Remove thinking tags - handle multiple occurrences at start
    # Use a loop to handle multiple consecutive thinking tags
    while True:
        original_len = len(cleaned)
        # Remove any thinking tag at the start
        cleaned = re.sub(
            r"^<think>.*?</think>\s*", "", cleaned, count=1, flags=re.DOTALL
        )
        cleaned = re.sub(
            r"^<\|thinking\|>.*?<\|/thinking\|>\s*",
            "",
            cleaned,
            count=1,
            flags=re.DOTALL,
        )
        # If nothing was removed, break
        if len(cleaned) == original_len:
            break

    # Remove thinking tags at end
    cleaned = re.sub(r"\s*<think>.*?</think>$", "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(
        r"\s*<\|thinking\|>.*?<\|/thinking\|>$", "", cleaned, flags=re.DOTALL
    )

    return cleaned.strip()


def trans_tsfile_ollama(
    SRCISO: str,
    TARGETISO: str,
    URL: str,
    APIKEY: Optional[str],
    TSFILE: str,
    OVERWRITE: bool,
    MODEL: str,
) -> None:
    """
    Translate a Qt .ts file using Ollama API.

    Args:
        SRCISO: Source language ISO code
        TARGETISO: Target language ISO code
        URL: Ollama API URL
        APIKEY: API key for Ollama (optional)
        TSFILE: Path to the .ts file to translate
        OVERWRITE: Whether to overwrite existing translations
        MODEL: The Ollama model to use
    """
    from ollama import Client

    # Prepare headers with API key if provided
    headers: Dict[str, str] = {}
    if APIKEY:
        headers["Authorization"] = f"Bearer {APIKEY}"

    client = Client(host=URL, headers=headers if headers else None)

    logging.info(_("Ollama for .ts file"))

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

    # Statistics
    translated_count = 0
    skipped_count = 0
    plural_translated_count = 0

    # Track current context for accelerator conflict detection
    current_context = None

    # Process each translation unit
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
            skipped_count += 1
            continue

        # Skip obsolete units
        if unit.isobsolete():
            skipped_count += 1
            logging.debug(_("Skipping obsolete unit: ") + str(unit.source))
            continue

        # Skip if already translated and not overwriting
        if unit.istranslated() and not OVERWRITE:
            skipped_count += 1
            continue

        # Check for plural forms (multistring type)
        if isinstance(unit.source, list) or "multistring" in str(type(unit.source)):
            # Handle plural forms
            try:
                # For Qt plural forms, translate each form separately
                source_forms = (
                    unit.source if isinstance(unit.source, list) else [str(unit.source)]
                )
                translated_forms = []

                for source_text in source_forms:
                    if source_text and source_text.strip():
                        # Check if this is a menu item
                        is_menu_item = "&" in source_text and "&&" not in source_text

                        # Use the same translate_func approach for consistency
                        def translate_plural_func(text_to_translate: str) -> str:
                            # Build appropriate prompt for Ollama
                            has_placeholders = bool(
                                re.search(
                                    r"<QT_P\d+/>|<QT_PN/>|<QT_VAR_\w+/>",
                                    text_to_translate,
                                )
                            )

                            if has_placeholders:
                                prompt = (
                                    f"Translate from {get_lang_name(SRCISO)} to {get_lang_name(TARGETISO)}. "
                                    f"Keep all <QT_*> tokens exactly as they appear:\n{text_to_translate}"
                                )
                            else:
                                prompt = f"Translate from {get_lang_name(SRCISO)} to {get_lang_name(TARGETISO)}:\n{text_to_translate}"

                            try:
                                response = client.chat(
                                    model=MODEL,
                                    messages=[
                                        {
                                            "role": "system",
                                            "content": "You are a translator. Output only the translation.",
                                        },
                                        {
                                            "role": "user",
                                            "content": prompt,
                                        },
                                    ],
                                    options={"temperature": 0.3},
                                )
                            except (TypeError, KeyError) as e:
                                logging.debug(f"Falling back to simple format: {e}")
                                response = client.chat(
                                    model=MODEL,
                                    messages=[
                                        {
                                            "role": "user",
                                            "content": prompt,
                                        },
                                    ],
                                )

                            raw_translation = response["message"]["content"].strip()
                            return clean_ollama_response(
                                raw_translation, text_to_translate
                            )

                        # Use Qt translator for proper handling
                        trans_str, warnings = qt_translator.translate_qt_string(
                            source_text,
                            current_context or "default",
                            get_lang_name(SRCISO),
                            get_lang_name(TARGETISO),
                            translate_plural_func,
                            is_menu_item,
                        )

                        # Log warnings
                        for warning in warnings:
                            logging.warning(warning)

                        translated_forms.append(trans_str)
                        logging.debug(
                            f"Plural source: {source_text}\nTranslation: {trans_str}"
                        )
                    else:
                        translated_forms.append("")

                # Set the translated plural forms
                if translated_forms:
                    unit.target = translated_forms
                    plural_translated_count += 1
                    logging.info(
                        _("Translated plural form with %d variants")
                        % len(translated_forms)
                    )

            except Exception as e:
                logging.warning(_("Failed to translate plural form: ") + str(e))
                skipped_count += 1
            continue

        # Handle regular (non-plural) messages
        source_text = unit.source

        # Skip empty source
        if not source_text or not source_text.strip():
            skipped_count += 1
            continue

        # Check if this is a menu item
        is_menu_item = "&" in source_text and "&&" not in source_text

        # Use Qt-aware translation
        def translate_func(text_to_translate: str) -> str:
            # Build appropriate prompt for Ollama
            # Check if text has protected placeholders
            has_placeholders = bool(
                re.search(r"<QT_P\d+/>|<QT_PN/>|<QT_VAR_\w+/>", text_to_translate)
            )

            if has_placeholders:
                prompt = (
                    f"Translate from {get_lang_name(SRCISO)} to {get_lang_name(TARGETISO)}. "
                    f"Keep all <QT_*> tokens exactly as they appear:\n{text_to_translate}"
                )
            else:
                prompt = f"Translate from {get_lang_name(SRCISO)} to {get_lang_name(TARGETISO)}:\n{text_to_translate}"

            # Handle the Ollama-specific translation
            try:
                # Try with system message and temperature control
                response = client.chat(
                    model=MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a translator. Output only the translation.",
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    options={"temperature": 0.3},
                )
            except (TypeError, KeyError) as e:
                # Fallback if options or system messages not supported
                logging.debug(f"Falling back to simple format: {e}")
                response = client.chat(
                    model=MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                )

            raw_translation = response["message"]["content"].strip()
            return clean_ollama_response(raw_translation, text_to_translate)

        trans_str, warnings = qt_translator.translate_qt_string(
            source_text,
            current_context or "default",
            get_lang_name(SRCISO),
            get_lang_name(TARGETISO),
            translate_func,
            is_menu_item,
        )

        # Log any warnings
        for warning in warnings:
            logging.warning(warning)

        # Log the translation
        logging.debug(f"Source: {source_text}\nTranslation: {trans_str}\n")
        logging.info(_("Original:    ") + source_text)
        logging.info(_("Translation: ") + trans_str + "\n")

        # Set the translation
        unit.target = trans_str
        translated_count += 1

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
            + f"Skipped: {skipped_count}, "
            + f"Warnings: {len(all_warnings)}"
        )

    except Exception as e:
        # Clean up temporary file if it exists
        if "temp_path" in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise IOError(_("Failed to save TS file: ") + str(e))
