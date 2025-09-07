# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from __future__ import annotations

import os

project = "pyhwloc"
copyright = "2025, Jiaming Yuan"
author = "Jiaming Yuan"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "breathe",
]

templates_path = ["_templates"]
exclude_patterns: list[str] = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]

# Breathe
breathe_default_project = "pyhwloc"
DOX_DIR = "/home/jiamingy/ws/pyhwloc_dev/"
CURR_PATH = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))  # source
PROJECT_ROOT = os.path.normpath(os.path.join(CURR_PATH, os.path.pardir, os.path.pardir))
breathe_projects = {
    "pyhwloc": os.path.join(PROJECT_ROOT, os.path.pardir, "hwloc/doc/doxygen-doc/xml")
}
print("beathe projects", breathe_projects)
