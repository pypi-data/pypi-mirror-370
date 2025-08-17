# Copyright (c) 2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Tests for `igwn_robot_auth.tools.get`."""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

import pytest

from igwn_robot_auth.tools import get as tools_get


def test_help():
    """Test the ``--help`` option."""
    with pytest.raises(SystemExit) as excinfo:
        tools_get.main(["--help"])
    assert excinfo.value.code == 0
