"""
PyMBO Main Entry Point

This module enables running PyMBO with `python -m pymbo` command.
"""

from .launcher import main

if __name__ == "__main__":
    exit(main())