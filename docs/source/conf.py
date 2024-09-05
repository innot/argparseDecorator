# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('../../argparsedecorator'))
sys.path.insert(0, os.path.abspath('../../examples'))

# -- Project information -----------------------------------------------------

project = 'argparseDecorator'
project_copyright = '2022,2024 Thomas Holland'
author = 'Thomas Holland'

# The full version, including alpha/beta/rc tags
release = '1.3.0'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.coverage',
    'sphinx.ext.intersphinx'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# Intersphinx mappings
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

default_role = 'py:obj'

# report all broken references
nitpicky = True
nitpick_ignore = [
    ('py:class', 'argparse.ArgumentError'),  # This Exception is not documented in the Python docs.
    ('py:exc', 'ArgumentError'),
    ('py:obj', 'argparsedecorator.annotations.T'),  # Ignore the generic Typedef T
    ('py:class', 'argparsedecorator.argument.T'),
    ('py:class', 'ParserNode'),  # autodoc does not like self refering types.
]
nitpick_ignore_regex = [
    ('py:class', r'prompt_toolkit.*'),  # no referenceable API documentation.
    ('py:class', r'asyncssh.*'),  # no referenceable API documentation.

]

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

autodoc_typehints = "signature"
autodoc_typehints_format = "short"
