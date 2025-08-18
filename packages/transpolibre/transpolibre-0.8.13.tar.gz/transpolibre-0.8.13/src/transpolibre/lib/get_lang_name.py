# src/transpolibre/lib/get_lang_name.py

import gettext
from typing import Any

from dotenv import load_dotenv
from pycountry import languages


load_dotenv()

LOCALE_DIR = "locale"

gettext.bindtextdomain("transpolibre", LOCALE_DIR)
gettext.textdomain("transpolibre")
_ = gettext.gettext


def get_lang_name(iso_code: str) -> str:
    try:
        # Normalize language code to lowercase for case-insensitive matching
        # This follows ISO 639 standard practice where codes are lowercase
        normalized_code = iso_code.lower() if isinstance(iso_code, str) else iso_code

        lang: Any = None
        if len(normalized_code) == 2:
            lang = languages.get(alpha_2=normalized_code)
        elif len(normalized_code) == 3:
            lang = languages.get(alpha_3=normalized_code)
        else:
            raise KeyError

        if lang is None:
            raise KeyError

        return str(lang.name)
    except (KeyError, TypeError, AttributeError):
        # Use the original iso_code in error message for clarity
        print(_("Error: unknown language code: ") + str(iso_code))
        exit(1)
