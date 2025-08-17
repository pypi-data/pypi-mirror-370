# Copyright (c) 2025 Cardiff University
# SPDX-License-Identifier: MIT

"""HTCondor utilities for IGWN Robot Auth."""

from __future__ import annotations

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

import logging
import shlex
import shutil
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)

CONDOR_GETTOKEN_OPTS_PARAM = "SEC_CREDENTIAL_GETTOKEN_OPTS"
CONDOR_USER_CONFIG_FILE_PARAM = "USER_CONFIG_FILE"
CONDOR_VAULT_STORER = shutil.which("condor_vault_storer") or "condor_vault_storer"


def _get_config(param: str) -> str:
    """Get a parameter from the HTCondor config."""
    import htcondor
    value = htcondor.param[param]
    log.debug("htcondor.param: %s = %s", param, value)
    return value


def condor_config_path() -> Path:
    """Return the path of the HTCondor user config."""
    user_config = _get_config(CONDOR_USER_CONFIG_FILE_PARAM)
    return Path.home() / ".condor" / user_config


def _match_config(args: list[str]) -> None:
    """Match the current HTCondor configuration against the given ``args``."""
    found = _get_config(CONDOR_GETTOKEN_OPTS_PARAM)
    foundargs = set(shlex.split(found))
    if foundargs.symmetric_difference(args):
        argstr = shlex.join(args)
        msg = (
           f"HTCondor user_config value for {CONDOR_GETTOKEN_OPTS_PARAM} "
           f"in {condor_config_path()} doesn't match current options: "
           f"{found!r} vs {argstr!r}"
        )
        raise ValueError(msg)


def check_condor_config(
    **options,
) -> None:
    """Check that the HTCondor user config matches the specified options."""
    args = [f"--{key}={value}" for key, value in options.items()]
    try:
        _match_config(args)
    except ValueError as exc:
        config = condor_config_path()
        if not config.exists():
            msg = f"""No HTCondor user_config file found at {config}.
Please consider creating one with the following contents:

{CONDOR_GETTOKEN_OPTS_PARAM} = {' '.join(args)}
"""
            raise ValueError(msg) from exc
        raise


def condor_vault_storer(
    oauth_service: str = "igwn",
    *,
    verbose: bool = True,
    **htgettoken_opts,
) -> None:
    """Call out to ``condor_vault_storer`` with the given options.

    This function just runs `subprocess.check_call`.

    Parameters
    ----------
    oauth_service : `str`, optional
        The ``oauth_service`` argument to use.
        This is typically just the name of the token issuer.
        Default is ``"igwn"``.

    verbose : `bool`, optional
        Show verbose output.

    htgettoken_opts
        Other ``key=value`` arguments are passed verbatim to the
        ``condor_vault_storer`` call.
    """
    check_condor_config(**htgettoken_opts)
    log.debug("Condor user_config matches current options")
    verbosearg = ("-v",) if verbose else ()
    log.debug("Executing condor_vault_storer")
    cmd = [
        CONDOR_VAULT_STORER,
        *verbosearg,
        oauth_service,
    ]
    cmdstr = shlex.join(cmd)
    log.debug("$ %s", cmdstr)
    try:
        subprocess.check_call(cmd, shell=False)
    except subprocess.CalledProcessError as exc:
        exc.cmd = cmdstr
        raise
