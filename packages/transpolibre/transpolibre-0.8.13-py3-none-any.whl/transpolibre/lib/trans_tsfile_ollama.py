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

    # Statistics
    translated_count = 0
    skipped_count = 0
    plural_translated_count = 0

    # Process each translation unit
    for unit in store.units:
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
                        # Use more direct prompt for plural form translation with thinking disabled
                        prompt = (
                            f"/set nothink\nTranslate from {get_lang_name(SRCISO)} to {get_lang_name(TARGETISO)}. "
                            f"Keep %n placeholders unchanged:\n{source_text}\n"
                        )

                        try:
                            # Try with system message and temperature control
                            response = client.chat(
                                model=MODEL,
                                messages=[
                                    {
                                        "role": "system",
                                        "content": "You are a translator. Output only the translation. Preserve all %n placeholders exactly.",
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
                        translation = clean_ollama_response(
                            raw_translation, source_text
                        )
                        translated_forms.append(translation)
                        logging.debug(
                            f"Plural source: {source_text}\nTranslation: {translation}"
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

        # Use more direct prompt for translation with thinking disabled
        prompt = (
            f"/set nothink\nTranslate from {get_lang_name(SRCISO)} to {get_lang_name(TARGETISO)}. "
            f"Keep %1, %2, & placeholders unchanged:\n{source_text}\n"
        )

        try:
            # Try with system message and temperature control
            try:
                response = client.chat(
                    model=MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a translator. Output only the translation. Preserve all placeholders (%1, %2, &) exactly.",
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

            # Process the response regardless of which API format was used
            raw_translation = response["message"]["content"].strip()
            translation = clean_ollama_response(raw_translation, source_text)

            # Log the translation
            logging.debug(f"Source: {source_text}\nTranslation: {translation}\n")
            logging.info(_("Original:    ") + source_text)
            logging.info(_("Translation: ") + translation + "\n")

            # Set the translation
            unit.target = translation
            translated_count += 1

        except Exception as e:
            logging.error(f"Failed to translate '{source_text}': {e}")
            skipped_count += 1

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

        logging.info(
            _("Translation complete. ")
            + f"Translated: {translated_count}, "
            + f"Plurals: {plural_translated_count}, "
            + f"Skipped: {skipped_count}"
        )

    except Exception as e:
        # Clean up temporary file if it exists
        if "temp_path" in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise IOError(_("Failed to save TS file: ") + str(e))
