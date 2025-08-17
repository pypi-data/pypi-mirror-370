# Configuration file for the Sphinx documentation builder.
# ruff: noqa: FIX002 PLR0911 ARG001 ERA001

__version__ = "0.12.2"


project = "League Manager"
copyright = "2025, Mario Munoz"
author = "Mario Munoz"
release = __version__
suppress_warnings = [
    "autosectionlabel.*",
    "ref.python",  # remove when https://github.com/sphinx-doc/sphinx/issues/4961 is fixed
]

# -- General configuration ---------------------------------------------------

extensions = [
    "autodoc2",
    "myst_parser",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx_toolbox.collapse",
    "sphinx_togglebutton",
]

myst_enable_extensions = [
    "attrs_inline",
    "colon_fence",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "tasklist",
]

autodoc2_render_plugin = "myst"
autodoc2_packages = [
    {
        "path": "../src/leaguemanager",
        "exclude_files": [r"__.*\.py$"],
    },
]

napoleon_google_docstring = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_attr_annotations = True

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

html_theme = "piccolo_theme"
html_title = "League Manager"
html_short_title = "leaguemanager"
templates_path = ["_templates"]
html_static_path = ["_static"]

html_theme_options = {"source_url": "https://codeberg.org/pythonbynight/leaguemanager", "source_icon": "generic"}
html_css_files = ["custom.css"]
