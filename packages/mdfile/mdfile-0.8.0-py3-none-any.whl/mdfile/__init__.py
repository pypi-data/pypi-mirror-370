# src/mdfile/__init__.py
"""
mdfile — Markdown File Manipulation Package
"""
from importlib.metadata import version

from .md_updater import update_markdown_file
__version__ = version("mdfile")
__author__ = "Chuck Bass"
__email__ = "chuck@acrocad.net"

__all__ = ["update_markdown_file", "__version__", "__author__", "__email__"]
