# Copyright (c) 2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Auth credential management for IGWN robots.

IGWN Robot Auth provides utilities to help manage authorisation credentials
for automated processes run by the `LIGO <https://www.ligo.org>`__
- `Virgo <https://www.virgo-gw.eu>`__
- `KAGRA <https://gwcenter.icrr.u-tokyo.ac.jp>`__ collaborations.
"""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

from .tools.get import get

try:
    from ._version import version as __version__
except ModuleNotFoundError:  # development mode
    __version__ = "dev"
