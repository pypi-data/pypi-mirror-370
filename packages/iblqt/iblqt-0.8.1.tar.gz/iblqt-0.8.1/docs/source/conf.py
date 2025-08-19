import os
import sys
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join('..', '..')))

from iblqt import __version__

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'iblqt'
author = 'International Brain Laboratory'
copyright = f'{date.today().year}, International Brain Laboratory'
version = '.'.join(__version__.split('.')[:3])
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx_copybutton',
    'sphinx_design',
    'sphinx_qt_documentation',
    'myst_parser',
]
source_suffix = ['.rst', '.md']
templates_path = ['_templates']
exclude_patterns = []
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'one': ('https://int-brain-lab.github.io/ONE/', None),
    'iblrig': ('https://int-brain-lab.github.io/iblrig/', None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
    'display_version': True,
}

# -- Settings for automatic API generation -----------------------------------
autodoc_mock_imports = ["PySpin"]
autodoc_class_signature = 'separated'  # 'mixed', 'separated'
autodoc_member_order = 'groupwise'  # 'alphabetical', 'groupwise', 'bysource'
autodoc_inherit_docstrings = False
autodoc_typehints = 'description'  # 'description', 'signature', 'none', 'both'
autodoc_typehints_description_target = 'all'  # 'all', 'documented', 'documented_params'
autodoc_typehints_format = 'short'  # 'fully-qualified', 'short'

autosummary_generate = True
autosummary_imported_members = False

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
napoleon_preprocess_types = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

copybutton_exclude = '.linenos, .gp'
