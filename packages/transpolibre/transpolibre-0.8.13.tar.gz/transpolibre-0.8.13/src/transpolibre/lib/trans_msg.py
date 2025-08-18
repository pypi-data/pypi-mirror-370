# src/transpolibre/lib/trans_msg.py

import gettext
import logging
import re
from typing import Optional, Match, Callable

from dotenv import load_dotenv
from libretranslatepy import LibreTranslateAPI


LOCALE_DIR = "locale"

# Module-level variable for gettext function
_gettext_func = None


def _get_gettext() -> Callable[[str], str]:
    """Get or initialize the gettext function."""
    global _gettext_func
    if _gettext_func is None:
        load_dotenv()
        gettext.bindtextdomain("transpolibre", LOCALE_DIR)
        gettext.textdomain("transpolibre")
        _gettext_func = gettext.gettext
    return _gettext_func


def trans_msg(
    msg: str, SRCISO: str, TARGETISO: str, URL: str, APIKEY: Optional[str]
) -> str:
    # Get gettext function
    _ = _get_gettext()

    url_pattern: str = r"`([^`]+) <(https?://[^\s>]+)>`_"
    email_pattern: str = r"<([\w\.\-\+]+@[\w\.\-]+\.\w+)>"

    lt = LibreTranslateAPI(URL, APIKEY)

    def translate_link(match: Match[str]) -> str:
        text, url = match.groups()
        logging.debug(_("Translating link text: %s with URL: %s") % (text, url))
        translated_text = lt.translate(text, SRCISO, TARGETISO)
        return f"`{translated_text} <{url}>`_"

    # Initialize trans_str to handle all cases
    trans_str: str = msg  # Default to original message

    # Check for special patterns
    has_url: Optional[Match[str]] = re.search(url_pattern, msg)
    has_email: Optional[Match[str]] = re.search(email_pattern, msg)

    if has_url and not has_email:
        # Only URL present - translate with URL preservation
        logging.debug(_("URL detected"))
        trans_str = re.sub(url_pattern, translate_link, msg)
    elif has_email:
        # Email present (with or without URL) - don't translate
        logging.debug(_("Email detected"))
        trans_str = msg
    else:
        # No special patterns - translate normally
        logging.debug(_("No URL or Email detected"))
        trans_str = lt.translate(msg, SRCISO, TARGETISO)

    logging.debug(_("LibreTranslate URL: %s") % URL)
    logging.debug(_("API Key: %s") % (str(APIKEY) if APIKEY is not None else _("None")))
    logging.debug(_("Translating: %s") % msg)
    logging.debug(_("Source ISO 639: %s") % SRCISO)
    logging.debug(_("Target ISO 639: %s") % TARGETISO)
    logging.debug(_("Translation: %s") % trans_str)

    return trans_str
