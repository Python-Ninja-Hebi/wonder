# Configuration file for the Sphinx documentation builder.
# sphinx-apidoc -f -o docs/source .
# sphinx-build -b html ./docs/source/ ./docs/builds/

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information

project = 'wonder - python game engine'
copyright = '2021, python ninja hebi'
author = 'hebi@python-ninja.com'

release = version = '0.1.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc', #grabs documentation from inside code
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon', #supports google-style docstrings
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode', #packages text source with generated docs
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'
