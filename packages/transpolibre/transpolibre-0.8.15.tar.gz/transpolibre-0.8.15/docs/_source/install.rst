============
Installation
============
PyPI Install
------------
This is the "regular" way to install.

* https://pypi.org/project/transpolibre/

.. code-block:: bash

  python -m venv venv
  source venv/bin/activate
  pip install -U setuptools pip wheel
  pip install transpolibre

Source Install
--------------
To install from the source code repository.

* https://spacecruft.org/deepcrayon/transpolibre

.. code-block:: bash

  git clone https://spacecruft.org/deepcrayon/transpolibre
  cd transpolibre/
  python -m venv venv
  source venv/bin/activate
  pip install -U setuptools pip wheel
  pip install -e .

Development Install
-------------------
To install for development.

* https://spacecruft.org/deepcrayon/transpolibre

.. code-block:: bash

  git clone https://spacecruft.org/deepcrayon/transpolibre
  cd transpolibre/
  python -m venv venv
  source venv/bin/activate
  pip install -U setuptools pip wheel
  pip install -e .[dev]
