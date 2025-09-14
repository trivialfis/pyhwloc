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
    "sphinx.ext.intersphinx",
    "sphinx_gallery.gen_gallery",
    "breathe",
]

templates_path = ["_templates"]
exclude_patterns: list[str] = []

# See the war: https://github.com/sphinx-doc/sphinx/issues/10785#issuecomment-1321100925
autodoc_type_aliases = {
    "ExportXmlFlags": "pyhwloc.topology.ExportXmlFlags",
    "ExportSyntheticFlags": "pyhwloc.topology.ExportSyntheticFlags",
}

autodoc_typehints_format = "short"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]

intersphinx_mapping = {"python": ("https://docs.python.org/3.10", None)}

# -- Breathe
breathe_default_project = "pyhwloc"
breathe_domain_by_extension = {"h": "c"}

CURR_PATH = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))  # source
PROJECT_ROOT = os.path.normpath(os.path.join(CURR_PATH, os.path.pardir, os.path.pardir))

hwloc_xml_path = os.environ.get("PYHWLOC_XML_PATH", None)
if hwloc_xml_path is None:
    hwloc_xml_path = os.path.join(
        PROJECT_ROOT, os.path.pardir, "hwloc/doc/doxygen-doc/xml"
    )
breathe_projects = {"pyhwloc": hwloc_xml_path}
print("beathe projects", breathe_projects)

# -- Build environment

os.environ["PYHWLOC_SPHINX"] = "1"

# -- Gallery
sphinx_gallery_conf = {
    # path to your example scripts
    "examples_dirs": ["../../examples/"],
    # path to where to save gallery generated output
    "gallery_dirs": ["examples"],
}
