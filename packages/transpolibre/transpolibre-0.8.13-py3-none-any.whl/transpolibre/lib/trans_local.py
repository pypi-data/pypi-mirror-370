# src/transpolibre/lib/trans_local.py

import gettext
import logging
import os
from typing import List, Tuple, Any

import polib

from transpolibre.lib.get_lang_name import get_lang_name
from transpolibre.lib.update_pofile import update_pofile

LOCALE_DIR = "locale"

gettext.bindtextdomain("transpolibre", LOCALE_DIR)
gettext.textdomain("transpolibre")
_ = gettext.gettext


def trans_local(
    SRCISO: str,
    TARGETISO: str,
    POFILE: str,
    OVERWRITE: bool,
    MODEL: str,
    CUDA_DEVICE: int,
    DEVICE: str,
) -> None:
    logging.info(_("Local Torch"))

    if not os.path.isfile(POFILE):
        raise FileNotFoundError(
            _("The specified PO file does not exist or is not a file: " + POFILE)
        )

    logging.debug(_("Read PO file: ") + POFILE)

    pofile = polib.pofile(POFILE, encoding="utf-8")

    entries_to_translate: List[Tuple[str, Any]] = [
        (entry.msgid, entry) for entry in pofile if not entry.msgstr or OVERWRITE
    ]

    if not entries_to_translate:
        logging.info(_("No translations needed."))
        return

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    device: torch.device
    if DEVICE == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    elif DEVICE == "cpu":
        device = torch.device("cpu")
    elif DEVICE == "gpu":
        # Check CUDA availability before creating device
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

        batch_size: int = 16

        for i in range(0, len(entries_to_translate), batch_size):
            batch_entries = entries_to_translate[i : i + batch_size]

            prompts: List[str] = [
                f"Translate this text from {get_lang_name(SRCISO)} to {get_lang_name(TARGETISO)}. {get_lang_name(SRCISO)}:\n{msgid}\n{get_lang_name(TARGETISO)}:"
                for msgid, _ in batch_entries
            ]

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

            for (msgid, entry), translation in zip(batch_entries, translations):
                translation = translation.strip()

                try:
                    prompt_prefix = f"Translate this text from {get_lang_name(SRCISO)} to {get_lang_name(TARGETISO)}. {get_lang_name(SRCISO)}:\n{msgid}\n{get_lang_name(TARGETISO)}:"
                    start_index = translation.index(prompt_prefix) + len(prompt_prefix)
                    translation = translation[start_index:].strip()
                except ValueError:
                    logging.error(
                        f"Translation does not contain the expected format for target language {TARGETISO}: {translation}"
                    )
                    continue

                entry.msgstr = translation

                logging.info(f"Original:    {msgid}")
                logging.info(f"Translation: {translation}\n")

                update_pofile(POFILE, msgid, translation)

            del inputs
            del outputs
            torch.cuda.empty_cache()

    finally:
        # Clean up model and tokenizer to prevent memory leak
        if model is not None:
            del model
        if tokenizer is not None:
            del tokenizer
        # Final cache clear
        torch.cuda.empty_cache()
