# src/transpolibre/lib/trans_pofile.py

import gettext
import logging
import os
from typing import Optional

import polib

from transpolibre.lib.trans_msg import trans_msg
from transpolibre.lib.update_pofile import update_pofile


LOCALE_DIR = "locale"

gettext.bindtextdomain("transpolibre", LOCALE_DIR)
gettext.textdomain("transpolibre")
_ = gettext.gettext


def trans_pofile(
    SRCISO: str,
    TARGETISO: str,
    URL: str,
    APIKEY: Optional[str],
    POFILE: str,
    OVERWRITE: bool,
) -> None:
    if not os.path.isfile(POFILE):
        raise FileNotFoundError(
            _("The specified PO file does not exist or is not a file: " + POFILE)
        )

    logging.debug(_("Read PO file: ") + POFILE)

    pofile = polib.pofile(POFILE, encoding="utf-8")

    for entry in pofile:
        pomsgid: str = entry.msgid
        pomsgstr: str = entry.msgstr
        pomsg: str = f"msgid: {pomsgid}\nmsgstr: {pomsgstr}\n"

        if not pomsgstr or OVERWRITE:
            trans_str: str = trans_msg(pomsgid, SRCISO, TARGETISO, URL, APIKEY)
            logging.debug(pomsg)
            logging.info(_("Original:    ") + pomsgid)
            logging.info(_("Translation: ") + trans_str + ("\n"))

            update_pofile(POFILE, pomsgid, trans_str)
