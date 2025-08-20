"""Franklin Container - Jupyter magic commands for Franklin exercise containers.

This package provides IPython magic commands for managing packages within
Franklin exercise containers using the Pixi package manager.
"""

from franklin_container.magic import load_ipython_extension

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "load_ipython_extension",
]