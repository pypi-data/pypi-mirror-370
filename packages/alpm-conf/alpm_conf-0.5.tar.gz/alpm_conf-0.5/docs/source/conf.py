# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from pathlib import PosixPath

__version__ = 'Unknown version'
def conf_py_setup():
    global __version__, __doc__

    cur_dir = PosixPath(__file__).parent
    root_dir = cur_dir.parent.parent
    try:
        sys.path.append(str(root_dir))
        from alpm_conf import __version__, __doc__
    finally:
        sys.path.pop()

    with open(cur_dir / 'README.rst', 'w') as fdest:
        fdest.write('alpm-conf |version|\n')
        fdest.write('===================\n\n')
        with open(root_dir / 'README.rst') as fsrc:
            content = fsrc.read()
            fdest.write(content)

conf_py_setup()

project = 'alpm-conf'
copyright = '2025, Xavier de Gaye'
author = ''

# The short X.Y version
version = __version__
# The full version, including alpha/beta/rc tags
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []
templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['images']

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('alpm-conf', 'alpm-conf', __doc__[:-1], [author], 8),
]
