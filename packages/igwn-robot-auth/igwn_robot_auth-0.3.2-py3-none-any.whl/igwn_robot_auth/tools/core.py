# Copyright (C) 2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Core utilities for IGWN Robot Auth tools."""

from __future__ import annotations

import argparse
import logging

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

# -- log formatting

DEFAULT_FORMAT = "%(asctime)s:%(name)s[%(process)d]:%(levelname)s:%(message)s"
DEFAULT_DATEFMT = "%Y-%m-%dT%H:%M:%S%z"


def configure_logging(
    verbose: int = 0,
    fmt: str = DEFAULT_FORMAT,
    datefmt: str = DEFAULT_DATEFMT,
    *,
    force: bool = False,
    **kwargs,
) -> None:
    """Configure a `logging.Logger` for a command-line application.

    Parameters
    ----------
    verbose : `int`
        Verbosity level (0-3).

    fmt : `str`
        Log message format string.

    datefmt : `str`
        Date format string.

    force : `bool`, optional
        If `True`, force reconfiguration of logging even if the root logger is
        already configured.

    kwargs
        Additional keyword arguments passed to the logging configuration.

    Notes
    -----
    If the Python root logger is already configured, this function will do
    nothing unless `force` is set to `True`.
    """
    if logging.getLogger().hasHandlers() and not force:
        return
    level = max(3 - verbose, 0) * 10
    try:
        import coloredlogs
    except ImportError:
        logging.basicConfig(
            format=fmt,
            level=level,
            datefmt=datefmt,
            **kwargs,
        )
    else:
        coloredlogs.install(
            fmt=fmt,
            level=level,
            datefmt=datefmt,
            **kwargs,
        )


# -- argument parsing

class ArgumentFormatter(
    argparse.RawDescriptionHelpFormatter,
    argparse.ArgumentDefaultsHelpFormatter,
):
    """`argparse.ArgumentFormatter` for `igwn-robot-auth` tools."""


class ArgumentParser(argparse.ArgumentParser):
    """`argparse.ArgumentParser` for `igwn-robot-auth` tools."""

    def __init__(
        self,
        version: str | None = None,
        man_short_description: str | None = None,
        manpage: list[dict[str, str]] | None = None,
        **kwargs,
    ) -> None:
        """Initialise the `ArgumentParser`."""
        # initialise ArgumentParser
        kwargs.setdefault("formatter_class", ArgumentFormatter)
        super().__init__(**kwargs)

        # update argument group titles
        self._positionals.title = "Required (positional) arguments"
        self._optionals.title = "Optional arguments"

        # handle formatting for argparse-manpage
        self._manpage = manpage
        if not man_short_description and self.description:
            # if man_short_description was not given, copy the first line of
            # the parser description, with some pedantic reformatting
            man_short_description = (
                self.description.split("\n")[0].lower().rstrip(".")
            )
        self.man_short_description = man_short_description

        # add default -V/--version
        if version is not False:
            from igwn_robot_auth import __version__
            self.add_argument(
                "-V",
                "--version",
                action="version",
                version=version or __version__,
            )
