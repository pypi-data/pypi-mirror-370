# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

import django
from sphinxawesome_theme.postprocess import Icons

sys.path.insert(0, os.path.abspath("../.."))
os.environ["DJANGO_SETTINGS_MODULE"] = "terminusgps.django.settings"
django.setup()

project = "python-terminusgps"
copyright = "2025, Terminus GPS, LLC"
author = "Terminus GPS, LLC"
release = "41.2.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "autoclasstoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": (
        "http://docs.djangoproject.com/en/stable/",
        "http://docs.djangoproject.com/en/stable/_objects/",
    ),
}

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinxawesome_theme"
html_permalinks_icon = Icons.permalinks_icon
pygments_style = "sas"
pygments_style_dark = "lightbulb"
html_static_path = ["_static"]
