# Development
```
git clone https://spacecruft.org/deepcrayon/transpolibre
cd transpolibre/
python -m venv venv
source venv/bin/activate
pip install -U setuptools pip wheel
pip install -e .[dev]
```

## Python formatting

```
black src/transpolibre/main.py src/transpolibre/lib/*py
```

## Application Translation Strings
Howto set up translation strings for the `transpolibre` script
itself. This doesn't cover the Sphinx documentation, which is
handled seperately (see the `Makefile` for the documentation).

```
mkdir -p locale/es/LC_MESSAGES
xgettext --from-code=UTF-8 -o locale/transpolibre.pot src/transpolibre/transpolibre.py
sed -i -e 's/charset=CHARSET/charset=UTF-8/g' locale/transpolibre.pot
msginit --input=locale/transpolibre.pot --output-file=locale/es/LC_MESSAGES/transpolibre.po --locale=es_ES.UTF-8 --no-translator
transpolibre -o -s en -t es -f locale/es/LC_MESSAGES/transpolibre.po
msgfmt -o locale/es/LC_MESSAGES/transpolibre.mo locale/es/LC_MESSAGES/transpolibre.po
```

## Documentation Translation Strings
To automatically translate the documentation, run this (may need to run
twice the first time):
```
make translations
```

Then update the html:
```
make html
```

## Build for PyPI
```
pip install -e .[dev]
pip install -e .[all]
make all
pip install --upgrade build
python3 -m build
```

## Upload to PyPI
Log into test.pypi.org and pypi.org. Create an API token.
Save token to with formatting to `$HOME/.pypirc`, such as:
```[testpypi]
  username = __token__
  password = pypi-foooooooooooooooooooooooooooooooooooooo
```

Test repo:
```
python3 -m twine upload --repository testpypi dist/*
```

Main repo:
```
python3 -m twine upload dist/*
```

## Release
Move needed files to `dist/` then upload to server.

```
mv docs/_build/latex/en/transpolibre-prepress-en.pdf dist/transpolibre-`transpolibre --version`-en.pdf
mv docs/_build/latex/es/transpolibre-prepress-es.pdf dist/transpolibre-`transpolibre --version`-es.pdf
```

Upload these files to https://spacecruft.org/deepcrayon/transpolibre/releases
```
transpolibre-VERSION-py3-none-any.whl
transpolibre-VERSION.tar.gz
transpolibre-VERSION-en.pdf
transpolibre-VERSION-es.pdf
```

