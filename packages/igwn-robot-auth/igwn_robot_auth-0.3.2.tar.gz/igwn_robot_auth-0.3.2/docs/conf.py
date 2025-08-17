# Copyright (c) 2024-2025 Cardiff University

import os
from datetime import (
    datetime,
    timezone,
)

import sphinx_github_style

from igwn_robot_auth import __version__ as igwn_robot_auth_version

# -- Project information -------------

project = "igwn-robot-auth"
copyright = f"{datetime.now(tz=timezone.utc).date().year}, Cardiff University"
author = "Duncan Macleod"

# The full version, including alpha/beta/rc tags
release = igwn_robot_auth_version
version = release.split("+", 1)[0]

# The version used in the image tag.
# This is used to provide an accurate tag for the Docker image docs
if os.getenv("READTHEDOCS_VERSION") == "latest":
    image_tag = os.getenv("READTHEDOCS_GIT_COMMIT_HASH", version)
elif os.getenv("GITLAB_CI"):
    image_tag = os.getenv("CI_COMMIT_TAG", os.getenv("CI_COMMIT_SHA", version))
else:
    image_tag = version

# -- General configuration -----------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Content to prepend to all reStructuredText files.
# This is used to support substitutions like |release| and |version|.
rst_prolog = f"""
.. |image_name| replace:: containers.ligo.org/computing/software/igwn-robot-auth
.. |image_tag| replace:: {image_tag}
"""

# -- Options for HTML output ---------

html_theme = "furo"
html_title = f"{project} {version}"

html_static_path = ["_static"]
html_css_files = ["igwn-furo.css"]

pygments_dark_style = "monokai"

default_role = "obj"

maximum_signature_line_length = 80

# -- Extensions ----------------------

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_automodapi.automodapi",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_substitution_extensions",
    "sphinxarg.ext",
]

# -- automodapi

automodapi_inherited_members = False

# -- copybutton

copybutton_prompt_text = " |".join((  # noqa: FLY002
    ">>>",
    r"\.\.\.",
    r"\$"
    r"In \[\d*\]:",
    r" {2,5}\.\.\.:",
    " {5,8}: ",
))
copybutton_prompt_is_regexp = True
copybutton_line_continuation_character = "\\"

# -- intersphinx

intersphinx_mapping = {name: (url, None) for name, url in {
    "htcondor": "https://htcondor.readthedocs.io/en/latest/",
    "igwn-auth-utils": "https://igwn-auth-utils.readthedocs.io/en/stable/",
    "python": "https://docs.python.org/3/",
    "requests": "https://requests.readthedocs.io/en/stable/",
    "scitokens": "https://scitokens.readthedocs.io/en/latest/",
}.items()}

# -- linkcode

linkcode_url = sphinx_github_style.get_linkcode_url(
    blob=sphinx_github_style.get_linkcode_revision("head"),
    url=f"https://git.ligo.org/computing/software/{project}",
)
linkcode_resolve = sphinx_github_style.get_linkcode_resolve(linkcode_url)

# -- myst_parser

myst_enable_extensions = [
    "attrs_block",
]

# -- napoleon

napoleon_use_rtype = False
