# src/transpolibre/lib/trans_tsfile.py

import gettext
import logging
import os
import tempfile
import shutil
from typing import Optional

from translate.storage import ts2 as ts

from transpolibre.lib.trans_msg import trans_msg

LOCALE_DIR = "locale"

gettext.bindtextdomain("transpolibre", LOCALE_DIR)
gettext.textdomain("transpolibre")
_ = gettext.gettext


def trans_tsfile(
    SRCISO: str,
    TARGETISO: str,
    URL: str,
    APIKEY: Optional[str],
    TSFILE: str,
    OVERWRITE: bool,
) -> None:
    """
    Translate a Qt .ts file using the specified translation engine.

    Args:
        SRCISO: Source language ISO code
        TARGETISO: Target language ISO code
        URL: Translation service URL
        APIKEY: API key for translation service (optional)
        TSFILE: Path to the .ts file to translate
        OVERWRITE: Whether to overwrite existing translations
    """
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
                # Qt uses numerus forms like: %n file(s)
                source_forms = (
                    unit.source if isinstance(unit.source, list) else [str(unit.source)]
                )
                translated_forms = []

                for source_text in source_forms:
                    if source_text and source_text.strip():
                        # Translate each plural form
                        trans_str = trans_msg(
                            str(source_text), SRCISO, TARGETISO, URL, APIKEY
                        )
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

        # Translate the message
        trans_str = trans_msg(source_text, SRCISO, TARGETISO, URL, APIKEY)

        # Log the translation
        logging.debug(f"Source: {source_text}\nTranslation: {trans_str}\n")
        logging.info(_("Original:    ") + source_text)
        logging.info(_("Translation: ") + trans_str + "\n")

        # Set the translation
        unit.target = trans_str
        translated_count += 1

    # Save the file atomically using a temporary file
    # This prevents corruption if the process is interrupted
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
