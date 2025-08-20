import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "ltcodecs"
copyright = "2023, Woods Hole Oceanographic Institution"
author = "Woods Hole Oceanographic Institution — Acomms Group"

release = os.getenv('CI_COMMIT_REF_NAME', 'latest')

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Napoleon allows using numpy- or Google-style docstrings
extensions = ["myst_parser", "sphinx.ext.autodoc", "sphinx.ext.napoleon"]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for LaTeX output ------------------------------------------------
# Disable index page
latex_elements = {
'makeindex': '',
'printindex': '',
} 

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "sphinx_book_theme"

add_function_parentheses = True
add_module_names = True
