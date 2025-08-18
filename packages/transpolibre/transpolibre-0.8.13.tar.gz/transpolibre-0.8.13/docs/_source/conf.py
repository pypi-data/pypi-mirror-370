import sphinx.util.logging

# sys.path.append("../../src/transpolibre")

logger = sphinx.util.logging.getLogger(__name__)

project = "transpolibre"
copyright = "2025, Jeff Moe"
author = "Jeff Moe"
version = "0"
release = "0.8.13"
extensions = [
    "notfound.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    #    "sphinxcontrib.bibtex",
]
# bibtex_bibfiles = ['transpolibre-org.bib']
templates_path = ["_templates"]
exclude_patterns = []
source_suffix = ".rst"
master_doc = "index"
pygments_style = "staroffice"
python_display_short_literal_types = True
todo_include_todos = False
html_show_copyright = False
html_static_path = ["_static"]
html_favicon = "_static/favicon.ico"
html_logo = "_static/logo.png"
html_last_updated_fmt: None
html_show_sphinx = False
html_show_sourcelink = False
html_link_suffix = ".html"
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "style_nav_header_background": "#4fb31f",
    "prev_next_buttons_location": "bottom",
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

html_css_files = [
    "custom.css",
]
html_context = {
    "display_lower_left": True,
}

locale_dirs = ["locale/"]
gettext_compact = False
language = "en"
# languages = ("am", "ar", "bn", "de", "el", "en", "eo", "es", "eu", "fil", "fr", "he", "hi", "id", "it", "ja", "ko", "mr", "ms", "nl", "pl", "pt", "ru", "see", "ta", "te", "th", "tr", "ur", "vi", "zh")
languages = (
    "ar",
    "az",
    "bn",
    "ca",
    "cs",
    "da",
    "de",
    "el",
    "eo",
    "es",
    "et",
    "eu",
    "fa",
    "fr",
    "ga",
    "gl",
    "he",
    "hi",
    "hu",
    "id",
    "it",
    "ja",
    "ko",
    "lt",
    "lv",
    "ms",
    "nb",
    "nl",
    "pl",
    "pt",
    "ro",
    "ru",
    "sk",
    "sl",
    "sq",
    "sv",
    "th",
    "tl",
    "tr",
    "uk",
    "ur",
    "zh",
)
html_search_language = "en"

latex_engine = "xelatex"
latex_elements = {
    "extraclassoptions": "openany,oneside",
    "sphinxsetup": "hmargin={1in,1in}, vmargin={1in,1in}",
    "inputenc": "",
    "utf8extra": "",
    "preamble": r"""
\usepackage{xcolor}
\usepackage{bidi}
\usepackage{polyglossia}
    """,
}

notfound_urls_prefix = "/en/"
