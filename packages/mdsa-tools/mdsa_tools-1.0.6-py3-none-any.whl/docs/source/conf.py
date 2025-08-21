# -- Project info -------------------------------------------------------------

project = "mdsa-tools"
author = "Weir Lab"
release = "0.1.4"

# -- General config -----------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "myst_parser",    
    
]

autosummary_generate = True
napoleon_google_docstring = False
napoleon_numpy_docstring = True

# If heavy libs break RTD/Actions, mock them here:
autodoc_mock_imports = ["mdtraj", "umap", "python_circos", "matplotlib", "seaborn"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "**.ipynb_checkpoints"]


html_theme = "alabaster"   # or "sphinx_rtd_theme" if you install it
html_static_path = ["_static"]

nbsphinx_execute = "never"
nbsphinx_allow_errors = True
