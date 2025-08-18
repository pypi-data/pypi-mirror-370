# src/transpolibre/lib/parse_arguments.py

import argparse
import gettext
import os
from dotenv import load_dotenv

from transpolibre._version import __version__

load_dotenv()

LOCALE_DIR = "locale"

gettext.bindtextdomain("transpolibre", LOCALE_DIR)
gettext.textdomain("transpolibre")
_ = gettext.gettext


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=_("Translate PO files"))

    engine_choices = ["libretranslate", "ollama", "local"]
    device_choices = ["auto", "cpu", "gpu"]

    def engine_choice(value: str) -> str:
        value_lower = value.lower()
        if value_lower not in engine_choices:
            raise argparse.ArgumentTypeError(
                f"invalid engine: '{value}' (choose from {', '.join(engine_choices)})"
            )
        return value_lower

    def device_choice(value: str) -> str:
        value_lower = value.lower()
        if value_lower not in device_choices:
            raise argparse.ArgumentTypeError(
                f"invalid device: '{value}' (choose from {', '.join(device_choices)})"
            )
        return value_lower

    parser.add_argument(
        "-a",
        "--api-key",
        help=_("LibreTranslate API key"),
        type=str,
        default=os.getenv("LT_API_KEY"),
    )

    parser.add_argument(
        "-c",
        "--cuda-device",
        help=_("Local CUDA device number (Default 0)"),
        type=int,
        default=0,
    )

    parser.add_argument(
        "-d",
        "--debug",
        help=_("Debugging"),
        action="store_true",
    )

    parser.add_argument(
        "-D",
        "--device",
        help=_("Device to use for local translation: auto, cpu, gpu (Default auto)"),
        default="auto",
        type=device_choice,
        metavar="{auto,cpu,gpu}",
    )

    parser.add_argument(
        "-e",
        "--engine",
        help=_("Translation engine (Default: LibreTranslate)"),
        default="libretranslate",
        type=engine_choice,
        metavar="{LibreTranslate,Ollama,Local}",
    )

    parser.add_argument(
        "-f",
        "--file",
        help=_("PO file to translate"),
        type=str,
    )

    parser.add_argument(
        "-l",
        "--list",
        help=_("List available languages"),
        action="store_true",
    )

    parser.add_argument(
        "-m",
        "--model",
        help=_(
            "Model for Local or Ollama (Default local: ModelSpace/GemmaX2-28-9B-v0.1, default Ollama: aya-expanse:32b)"
        ),
        type=str,
    )

    parser.add_argument(
        "-o",
        "--overwrite",
        help=_("Overwrite existing translations"),
        action="store_true",
    )

    parser.add_argument(
        "-s",
        "--source-lang",
        help=_("Source Language ISO 639 code (Default en)"),
        default="en",
        type=str,
    )

    parser.add_argument(
        "-t",
        "--target-lang",
        help=_("Target Language ISO 639 code (Default es)"),
        default="es",
        type=str,
    )

    parser.add_argument(
        "-u",
        "--url",
        help=_(
            "Engine URL (Default LibreTranslate: http://127.0.0.1:8000, default Ollama: http://127.0.0.1:11434)"
        ),
        type=str,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help=_("Increase output verbosity"),
        action="count",
        default=0,
    )

    parser.add_argument(
        "-V",
        "--version",
        help=_("Show version"),
        action="version",
        version=f"{__version__}",
    )

    args = parser.parse_args()

    if args.engine == "libretranslate":
        args.url = args.url or os.getenv("LT_URL", "http://127.0.0.1:8000")
    elif args.engine == "ollama":
        args.url = args.url or os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
        args.model = args.model or os.getenv("OLLAMA_MODEL", "aya-expanse:32b")
    elif args.engine == "local":
        args.model = args.model or os.getenv(
            "LOCAL_MODEL", "ModelSpace/GemmaX2-28-9B-v0.1"
        )

    return args
