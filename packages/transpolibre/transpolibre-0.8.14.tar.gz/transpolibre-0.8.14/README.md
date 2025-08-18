# transpolibre
`transpolibre` is a Python program to automate translation of `gettext` PO files
using LibreTranslate, Ollama, or local models.

* https://transpolibre.org

# Install
# PyPI Installation

* https://pypi.org/project/transpolibre/

To install with pip from PyPI, you can do something like this:

```
python -m venv venv
source venv/bin/activate
pip install -U setuptools pip wheel
pip install transpolibre
# For Ollama
pip install transpolibre[ollama]
# For Local Engine
pip install transpolibre[local]
# For all engines
pip install transpolibre[all]
```

## Source Installation
Thusly, suit to taste:

```
git clone https://spacecruft.org/deepcrayon/transpolibre
cd transpolibre/
python -m venv venv
source venv/bin/activate
pip install -U setuptools pip wheel
pip install -e .
```

# Help
```
$ transpolibre --help
usage: transpolibre [-h] [-a API_KEY] [-c CUDA_DEVICE] [-d] [-D {auto,cpu,gpu}] [-e {LibreTranslate,Ollama,Local}] [-f FILE] [-l] [-m MODEL] [-o] [-s SOURCE_LANG] [-t TARGET_LANG] [-u URL] [-v] [-V]

Translate PO files

options:
  -h, --help            show this help message and exit
  -a API_KEY, --api-key API_KEY
                        LibreTranslate API key
  -c CUDA_DEVICE, --cuda-device CUDA_DEVICE
                        Local CUDA device number (Default 0)
  -d, --debug           Debugging
  -D {auto,cpu,gpu}, --device {auto,cpu,gpu}
                        Device to use for local translation: auto, cpu, gpu (Default auto)
  -e {LibreTranslate,Ollama,Local}, --engine {LibreTranslate,Ollama,Local}
                        Translation engine (Default: LibreTranslate)
  -f FILE, --file FILE  PO file to translate
  -l, --list            List available languages
  -m MODEL, --model MODEL
                        Model for Local or Ollama (Default local: ModelSpace/GemmaX2-28-9B-v0.1, default Ollama: aya-expanse:32b)
  -o, --overwrite       Overwrite existing translations
  -s SOURCE_LANG, --source-lang SOURCE_LANG
                        Source Language ISO 639 code (Default en)
  -t TARGET_LANG, --target-lang TARGET_LANG
                        Target Language ISO 639 code (Default es)
  -u URL, --url URL     Engine URL (Default LibreTranslate: http://127.0.0.1:8000, default Ollama: http://127.0.0.1:11434)
  -v, --verbose         Increase output verbosity
  -V, --version         Show version
```

# Status
Beta.

# AI
"Open Source" AI models are used to generate and edit some code.

# Upstream
Projects used by `transpolibre`.

* https://libretranslate.com/
* https://www.gnu.org/software/gettext/manual/gettext.html
* https://polib.readthedocs.io
* https://github.com/argosopentech/LibreTranslate-py
* https://ollama.com/

# License
Apache 2.0 or Creative Commons CC by SA 4.0 International.
You may use this code, files, and text under either license.

Unofficial project, not related to upstream projects.

Upstream sources under their respective copyrights.

*Copyright &copy; 2025 Jeff Moe.*
