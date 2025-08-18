# src/transpolibre/main.py

import gettext
import logging
from typing import Callable
from dotenv import load_dotenv

from transpolibre.lib.parse_arguments import parse_arguments
from transpolibre.lib.trans_list import trans_list

LOCALE_DIR = "locale"


def initialize_app() -> Callable[[str], str]:
    """Initialize application settings."""
    load_dotenv()

    gettext.bindtextdomain("transpolibre", LOCALE_DIR)
    gettext.textdomain("transpolibre")
    return gettext.gettext


def main() -> None:
    # Initialize app settings
    _ = initialize_app()

    args = parse_arguments()

    if args.debug:
        log_level = logging.DEBUG
    elif args.verbose > 0:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    if args.list:
        trans_list(args.url, args.api_key)
    else:
        if not args.file:
            print(_("Error: file is required."))
            exit(1)

        # Determine file type and route accordingly (case-insensitive)
        file_lower = args.file.lower()
        if file_lower.endswith(".ts"):
            # Handle Qt .ts files
            if args.engine == "libretranslate":
                from transpolibre.lib.trans_tsfile import trans_tsfile

                try:
                    trans_tsfile(
                        args.source_lang,
                        args.target_lang,
                        args.url,
                        args.api_key,
                        args.file,
                        args.overwrite,
                    )
                except (FileNotFoundError, ValueError, IOError) as e:
                    print(str(e))
                    exit(1)
            elif args.engine == "local":
                from transpolibre.lib.trans_tsfile_local import trans_tsfile_local

                try:
                    trans_tsfile_local(
                        args.source_lang,
                        args.target_lang,
                        args.file,
                        args.overwrite,
                        args.model,
                        args.cuda_device,
                        args.device,
                    )
                except Exception as e:
                    logging.error(f"An error occurred: {e}")
                    exit(1)
            elif args.engine == "ollama":
                from transpolibre.lib.trans_tsfile_ollama import trans_tsfile_ollama

                try:
                    trans_tsfile_ollama(
                        args.source_lang,
                        args.target_lang,
                        args.url,
                        args.api_key,
                        args.file,
                        args.overwrite,
                        args.model,
                    )
                except Exception as e:
                    logging.error(f"An error occurred: {e}")
                    exit(1)
        elif file_lower.endswith(".po"):
            # Handle gettext .po files
            if args.engine == "libretranslate":
                from transpolibre.lib.trans_pofile import trans_pofile

                try:
                    trans_pofile(
                        args.source_lang,
                        args.target_lang,
                        args.url,
                        args.api_key,
                        args.file,
                        args.overwrite,
                    )
                except FileNotFoundError as e:
                    print(str(e))
            elif args.engine == "local":
                from transpolibre.lib.trans_local import trans_local

                try:
                    trans_local(
                        args.source_lang,
                        args.target_lang,
                        args.file,
                        args.overwrite,
                        args.model,
                        args.cuda_device,
                        args.device,
                    )
                except Exception as e:
                    logging.error(f"An error occurred: {e}")
            elif args.engine == "ollama":
                from transpolibre.lib.trans_ollama import trans_ollama

                try:
                    trans_ollama(
                        args.source_lang,
                        args.target_lang,
                        args.url,
                        args.api_key,
                        args.file,
                        args.overwrite,
                        args.model,
                    )
                except Exception as e:
                    logging.error(f"An error occurred: {e}")
        else:
            print(_("Error: Unsupported file format. Use .po or .ts files."))
            exit(1)


if __name__ == "__main__":
    main()
