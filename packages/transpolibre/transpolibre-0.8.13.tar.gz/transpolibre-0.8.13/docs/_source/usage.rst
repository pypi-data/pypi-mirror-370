=====
Usage
=====
Thusly.

Help
----

.. code-block:: bash

  usage: transpolibre [-h] [-a API_KEY] [-c CUDA_DEVICE] [-d]
                      [-D {auto,cpu,gpu}] [-e {LibreTranslate,Ollama,Local}]
                      [-f FILE] [-l] [-m MODEL] [-o] [-s SOURCE_LANG]
                      [-t TARGET_LANG] [-u URL] [-v] [-V]

  Translate PO files

  options:
    -h, --help            show this help message and exit
    -a API_KEY, --api-key API_KEY
                          LibreTranslate API key
    -c CUDA_DEVICE, --cuda-device CUDA_DEVICE
                          Local CUDA device number (Default 0)
    -d, --debug           Debugging
    -D {auto,cpu,gpu}, --device {auto,cpu,gpu}
                          Device to use for local translation: auto, cpu, gpu
                          (Default auto)
    -e {LibreTranslate,Ollama,Local}, --engine {LibreTranslate,Ollama,Local}
                          Translation engine (Default: LibreTranslate)
    -f FILE, --file FILE  PO file to translate
    -l, --list            List available languages
    -m MODEL, --model MODEL
                          Model for Local or Ollama (Default local:
                          ModelSpace/GemmaX2-28-9B-v0.1, default Ollama: aya-
                          expanse:32b)
    -o, --overwrite       Overwrite existing translations
    -s SOURCE_LANG, --source-lang SOURCE_LANG
                          Source Language ISO 639 code (Default en)
    -t TARGET_LANG, --target-lang TARGET_LANG
                          Target Language ISO 639 code (Default es)
    -u URL, --url URL     Engine URL (Default LibreTranslate:
                          http://127.0.0.1:8000, default Ollama:
                          http://127.0.0.1:11434)
    -v, --verbose         Increase output verbosity
    -V, --version         Show version



Examples
--------
To translate a single PO file:

.. code-block:: bash

  transpolibre -f locale/es/myprogram.po

To translate specifying to/from language:

.. code-block:: bash

  transpolibre -s en -t fr -f locale/fr/myprogram.po

To use a particular LibreTranslate server:

.. code-block:: bash

  transpolibre -u http://192.168.1.100:8000 -s en -t it -f locale/it/myprogram.po

To list languages available on a LibreTranslate server:

.. code-block:: bash

  transpolibre -u http://192.168.1.100:8000 --list

To translate all the PO files in a directory:

.. code-block:: bash

  for i in locale/eo/*.po
      do transpolibre -u http://192.168.1.100:8000 -s en -t eo -f $i
  done

To translate with Ollama:

.. code-block:: bash

  transpolibre -e ollama -t it -f locale/it/myprogram.po

To tranlate with a local model:

.. code-block:: bash

  transpolibre -e local -m ModelSpace/GemmaX2-28-9B-v0.1 -t de -f locale/it/myprogram.po

Dotenv
------
The LibreTranslate URL and API key can be stored using dotenv, so it doesn't
need to be specified on the command line. For instance instead of doing this:

.. code-block:: bash

  transpolibre --url http://192.168.1.100:8000

You can add the URL adding the ``LT_URL`` variable to an ``.env``
file in the base directory:

.. code-block:: bash

  LT_URL="http://192.168.1.100:8000"

The same can be done with the API key, such as:

.. code-block:: bash

  LT_API_KEY="00000000000000000000000000000"

A default Ollama model:

.. code-block:: bash

  OLLAMA_MODEL="aya-expanse:32b"

A default Ollama URL:

.. code-block:: bash

  OLLAMA_URL="http://192.168.1.100:11434"
