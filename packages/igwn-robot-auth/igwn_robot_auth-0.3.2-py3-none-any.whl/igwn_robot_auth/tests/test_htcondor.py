# Copyright (c) 2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Tests for `igwn_robot_auth`."""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

from pathlib import Path
from unittest import mock

import pytest

from igwn_robot_auth import htcondor as ira_condor


@mock.patch("igwn_robot_auth.htcondor.Path.home", return_value=Path("/home/user"))
def test_condor_config_path(mock_home):
    """Test `condor_config_path()`."""
    assert ira_condor.condor_config_path() == Path(
        "/home/user/.condor/user_config",
    )


@mock.patch(
    "igwn_robot_auth.htcondor._get_config",
    return_value="--one=1 --two=2 --three=3",
)
def test_check_condor_config(mock_condor_config_path):
    """Test `check_config_config()`."""
    ira_condor.check_condor_config(one=1, two=2, three=3)


@mock.patch(
    "igwn_robot_auth.htcondor._get_config",
    return_value="--one=1 --two=2 --three=3",
)
@mock.patch("igwn_robot_auth.htcondor.condor_config_path")
@pytest.mark.parametrize(("exists", "match"), [
    (False, "No HTCondor user_config file found"),
    (True, "HTCondor user_config value for SEC_CREDENTIAL_GETTOKEN_OPTS"),
])
def test_check_condor_config_error(
    mock_condor_config_path,
    mock_get_config,
    exists,
    match,
):
    """Test `check_config_config()` error handling."""
    mock_condor_config_path.return_value.exists.return_value = exists
    with pytest.raises(ValueError, match=match):
        ira_condor.check_condor_config(one=2)
