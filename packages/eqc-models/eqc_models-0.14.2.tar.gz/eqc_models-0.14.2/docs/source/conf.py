
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'eqc-models'
# sphinx adds a period after copyright
copyright = '2025 Quantum Computing Inc. All rights reserved'
author = 'Quantum Computing Inc.'

import importlib.metadata as metadata
import tomli

release= metadata.version("eqc_models")
parts = release.split('.')
version = '.'.join(parts[:3])  # Get the first three parts
version = f"{project} v{version}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys
import tomli

sys.path.insert(0, os.path.abspath('../../eqc_models'))

# extract project dependencies
pyproject_path = "../../pyproject.toml"

with open(pyproject_path, "rb") as toml_file:
    pyproject_data = tomli.load(toml_file)

python_req = pyproject_data["project"]["requires-python"]
dependencies = pyproject_data["project"]["dependencies"]
output_rst_path = "dependencies.rst"
rst_content="Dependencies\n=============\n\n"
rst_content+=f"Requires Python: {python_req}\n\n"
rst_content+="Packages\n--------\n\n"

for dependency in dependencies:
    rst_content += f"- ``{dependency}``\n"

with open(output_rst_path, "w") as output_rst_file:
    output_rst_file.write(rst_content)

extensions = [
    'sphinx.ext.autosummary',
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.viewcode',
]

autodoc_member_order = 'bysource'


templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ["custom.css"]
html_logo = "_static/white_logo.png"
html_theme_options={
    "logo_only": True,
#    "display_version": True,
}
