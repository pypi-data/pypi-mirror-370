"""
vtree - A modern, interactive terminal-based file tree viewer with file panel support
"""

__version__ = "2.4.0"
__author__ = "vtree contributors"
__description__ = "A modern, interactive terminal-based file tree viewer with file panel support" 

from .main import main, VTreeApp

__all__ = ["main", "VTreeApp", "__version__"]