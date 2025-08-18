# src/transpolibre/lib/trans_ollama.py

import gettext
import logging
import os
import re
from typing import Dict, List, Tuple, Any, Optional

import polib
from dotenv import load_dotenv

from transpolibre.lib.get_lang_name import get_lang_name
from transpolibre.lib.update_pofile import update_pofile

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


def trans_ollama(
    SRCISO: str,
    TARGETISO: str,
    URL: str,
    APIKEY: Optional[str],
    POFILE: str,
    OVERWRITE: bool,
    MODEL: str,
) -> None:
    from ollama import Client

    # Prepare headers with API key if provided
    headers: Dict[str, str] = {}
    if APIKEY:
        # Standard authorization header for API key
        headers["Authorization"] = f"Bearer {APIKEY}"

    client = Client(host=URL, headers=headers if headers else None)

    if not os.path.isfile(POFILE):
        raise FileNotFoundError(
            _("The specified PO file does not exist or is not a file: " + POFILE)
        )

    logging.debug(_("Read PO file: ") + POFILE)

    pofile = polib.pofile(POFILE, encoding="utf-8")

    entries_to_translate: List[Tuple[str, Any]] = [
        (entry.msgid, entry) for entry in pofile if not entry.msgstr or OVERWRITE
    ]

    for msgid, entry in entries_to_translate:
        # Create translation prompt with thinking mode disabled
        prompt = f"/set nothink\nTranslate from {get_lang_name(SRCISO)} to {get_lang_name(TARGETISO)}:\n{msgid}"

        try:
            # Try with system message and temperature control
            response = client.chat(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a translator. Output only the translation, no explanations.",
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

        raw_translation = response["message"]["content"]
        translation = clean_ollama_response(raw_translation, msgid)

        entry.msgstr = translation

        logging.info(f"Original:    {msgid}")
        logging.info(f"Translation: {translation}\n")

        update_pofile(POFILE, msgid, translation)
