"""
WSA+ (WSA surrogate) — Generate solar wind speed maps at 0.1 AU from synoptic magnetograms.

Public API:
- generate_wsaplus_map(...): core function returning the predicted speed map and grids.
- load_magnetogram(...): utility to load synoptic magnetograms.

Command line:
- `wsaplus` entry point (see `wsaplus.cli:main`).
"""

from .api import generate_wsaplus_map, load_magnetogram

__all__ = ["generate_wsaplus_map", "load_magnetogram"]

__version__ = "0.1.0"
