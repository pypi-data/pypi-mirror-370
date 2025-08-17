# Copyright 2025 Cardiff University
# SPDX-License-Identifier: MIT

"""Get credentials for an IGWN robot."""

from __future__ import annotations

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

import logging
import os
import typing
from datetime import (
    datetime,
    timezone,
)
from pathlib import Path
from unittest import mock

from igwn_auth_utils import (
    get_scitoken,
    kinit,
)
from igwn_auth_utils.scitokens import (
    default_bearer_token_file,
    load_token_file,
)

from igwn_robot_auth.htcondor import condor_vault_storer
from igwn_robot_auth.tools.core import (
    ArgumentParser,
    configure_logging,
)

if typing.TYPE_CHECKING:
    from scitokens import SciToken

log = logging.getLogger(__name__)

DEFAULT_BEARER_TOKEN_FILE = default_bearer_token_file()
DEFAULT_MINSECS = 3600
DEFAULT_REALM = "LIGO.ORG"
DEFAULT_VAULT_SERVER = "vault.ligo.org"
DEFAULT_SCITOKEN_ISSUER = "igwn"
KEYTAB_ENVIRONMENT_VARIABLE = "KRB5_KTNAME"

MANPAGE = [
    {
        "heading": "environment",
        "content": f"""
.TP
.B "BEARER_TOKEN_FILE"
The default path for the SciToken
.TP
.B "{KEYTAB_ENVIRONMENT_VARIABLE}"
The default path for the Kerberos keytab
""",
    },
]


def format_principal(
    principal: str,
    default_realm: str = DEFAULT_REALM,
) -> str:
    """Format a Kerberos principal with a default realm."""
    if "@" in principal:
        return principal
    return f"{principal}@{default_realm}"


def default_credkey(
    principal: str,
) -> str:
    """Return the default `--credkey` argument based on the principal."""
    return principal.split("@", 1)[0]


def default_role(
    principal: str,
) -> str:
    """Return the default `--role` argument based on the principal."""
    return principal.split("/", 1)[0]


def debug_token(token: SciToken) -> None:
    """Display this tokens claims as ``DEBUG``-level log messages."""
    log.debug("Token claims:")
    for claim, value in sorted(token.claims()):
        if isinstance(value, int) and claim in {"exp", "iat", "nbf"}:
            value = datetime.fromtimestamp(value, timezone.utc)  # noqa: PLW2901
        log.debug("%8s: %s", claim, value)


# -- Python entry point

def get(
    principal: str | None = None,
    keytab: str | None = None,
    outfile: str = DEFAULT_BEARER_TOKEN_FILE,
    issuer: str = DEFAULT_SCITOKEN_ISSUER,
    ccache: str | None = None,
    credkey: str | None = None,
    role: str | None = None,
    minsecs: int = DEFAULT_MINSECS,
    vaultserver: str = DEFAULT_VAULT_SERVER,
    vaulttokenfile: str | None = None,
    vaulttokenminttl: str | int = "24h",
    *,
    condor: bool = False,
) -> None:
    """Get a token for a robot Kerberos principal.

    Parameters
    ----------
    principal : `str`
        Principal name for Kerberos credential.
        If not given it will be taken from the ``keytab``.
        If ``principal`` is not specified in the form ``name@REALM``
        the default realm REALM will be applied, see ``man krb5.conf``.

    keytab : `str`, optional
        Path to keytab file.
        Default taken from ``KRB5_KTNAME`` environment variable.
        If the environment variable is not set, or is empty, this keyword is
        required.

    outfile : `str`, optional
        Path in which to write the serialised `~scitokens.SciToken`.

    issuer : `str`, optional
        Name of vault token issuer.
        Default is ``"igwn"``.

    ccache : `str`, optional
        Path to Kerberos credentials cache.
        Default is the default credential cache, see ``man krb5.conf``.

    credkey : `str`, optional
        Vault credential key for this identity.
        Default is derived from Kerberos principal.

    role : `str`, optional
        Vault name of role for this identity.
        Default is derived from Kerberos principal.

    minsecs : `int`, optional
        Minimum number of seconds left in bearer token before expiry.
        If an existing token is found with a remaining lifetime greater
        than this number, `htgettoken` will not renew it.

    vaultserver : `str`, optional
        Name or IP of vault server to use

    vaulttokenfile : `str`, optional
        Path in which to store/use vault token.

    vaulttokenminttl : `str`, optional
        Minimum remaining lifetime of vault token before attempting renewal.

    condor : `bool`, optional
        Use `condor_vault_storer` to initialise a token for HTCondor.
        Default is `False`.

    Examples
    --------
    Get a SciToken for a specific robot keytab, dynamically grabbing the
    principal name from the keytab:

    >>> get(keytab="/home/user/.secure/robot.keytab")

    See Also
    --------
    igwn_auth_utils.kinit
        For details of how Kerberos credentials are initialised.

    igwn_auth_utils.get_scitoken
        For details of how a `~scitoken.SciToken` is acquired.

    igwn_robot_auth.htcondor.condor_vault_storer
        For details of how ``condor_vault_storer`` is invoked when
        ``condor=True`` is given.
    """
    # -- step 1: get a Kerberos ticket-granting-ticket

    log.info("Getting Kerberos credential")
    creds = kinit(
        principal,
        keytab=keytab,
        ccache=ccache,
    )
    principal = str(creds.name)
    log.debug("Acquired Kerberos credential for %s", principal)

    # -- step 2: get a SciToken using Kerberos

    if credkey is None:
        credkey = default_credkey(principal)
        log.debug("Set default --credkey='%s'", credkey)
    if role is None:
        role = default_role(principal)
        log.debug("Set default --role='%s'", role)

    ccacheenv = {}
    if ccache:
        ccacheenv["KRB5CCNAME"] = ccache

    with mock.patch.dict("os.environ", ccacheenv):
        # get a token
        if condor:
            condor_vault_storer(
                issuer,
                credkey=credkey,
                role=role,
                vaultserver=vaultserver,
            )
        else:
            log.info("Getting SciToken")
            tokenfile = get_scitoken(
                credkey=credkey,
                issuer=issuer,
                outfile=outfile,
                role=role,
                minsecs=minsecs,
                vaultserver=vaultserver,
                vaulttokenfile=vaulttokenfile or False,
                vaulttokenminttl=vaulttokenminttl,
                verbose=log.isEnabledFor(logging.INFO),
                debug=log.isEnabledFor(logging.DEBUG),
            )

            # debug the token
            if log.isEnabledFor(logging.DEBUG):
                debug_token(load_token_file(tokenfile))

    return outfile


# -- command-line options

def create_parser() -> ArgumentParser:
    """Create an `argparse.ArgumentParser` for this tool."""
    parser = ArgumentParser(
        description=__doc__,
        manpage=MANPAGE,
    )

    # -- positionals

    parser.add_argument(
        "principal",
        action="store",
        type=format_principal,
        nargs="?",
        help="Kerberos principal name (required if -k/--keytab not given)",
    )

    # -- options

    # general
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increate verbosity (can be given multiple times).",
    )

    # kerberos
    kerberosargs = parser.add_argument_group(
        "Kerberos options",
    )
    kerberosargs.add_argument(
        "-k",
        "--keytab",
        "--kerberos-keytab",
        action="store",
        default=os.getenv(KEYTAB_ENVIRONMENT_VARIABLE),
        required=not os.getenv(KEYTAB_ENVIRONMENT_VARIABLE),
        type=Path,
        help="Path to Kerberos keytab file",
    )
    kerberosargs.add_argument(
        "-c",
        "--ccache",
        "--kerberos-ccache",
        help="Path to Kerberos ccache (default is default Kerberos ccache)",
    )

    # scitokens
    tokenargs = parser.add_argument_group(
        "SciToken options",
    )
    tokenargs.add_argument(
        "-a",
        "--vaultserver",
        default=DEFAULT_VAULT_SERVER,
        help="Name or IP of vault server to use",
    )
    tokenargs.add_argument(
        "-i",
        "--issuer",
        default=DEFAULT_SCITOKEN_ISSUER,
        help="Name of SciToken issuer",
    )
    tokenargs.add_argument(
        "--credkey",
        help=(
            "Vault credential key for this identity; "
            "default is derived from Kerberos principal"
        ),
    )
    tokenargs.add_argument(
        "-r",
        "--role",
        help=(
            "Vault name of role for this identity; "
            "default is derived from Kerberos principal"
        ),
    )
    tokenargs.add_argument(
        "-m",
        "--minsecs",
        type=int,
        default=DEFAULT_MINSECS,
        help=(
            "Minimum number of seconds left in bearer token before expiry; "
            "if an existing token is found with a remaining lifetime greater "
            "than this number, htgettoken will not renew it"
        ),
    )
    tokenargs.add_argument(
        "--vaulttokenfile",
        default=None,
        help="Path in which to store/use vault token",
    )
    tokenargs.add_argument(
        "-o",
        "--outfile",
        "--bearertokenfile",
        default=DEFAULT_BEARER_TOKEN_FILE,
        help="Path in which to store bearer token",
    )
    tokenargs.add_argument(
        "--vaulttokenminttl",
        default="24h",
        help="Minimum remaining lifetime of vault token before attempting renewal",
    )

    condorargs = parser.add_argument_group(
        "Condor options",
    )
    condorargs.add_argument(
        "--condor",
        action="store_true",
        default=False,
        help="Use `condor_vault_storer` to initialise a token for HTCondor",
    )
    return parser


# -- main entry point

def main(args: list[str] | None = None) -> None:
    """Run this tool.

    Parameters
    ----------
    args : `list` of `str`
        The list of arguments to parse.
        Passed directly to `argparse.ArgumentParser.parse_args`.

    configure_logger : `bool`, optional
        Whether to configure the root logger.
        Default is `True`.
        If calling this function from another application or library, you
        probably want to pass ``configure_logger=False`` to allow the end
        application/user to configure logging themselves.
    """
    parser = create_parser()
    opts = parser.parse_args(args=args)

    # set verbose logging
    configure_logging(verbose=opts.verbose)

    # get the creds
    get(
        principal=opts.principal,
        keytab=opts.keytab,
        outfile=opts.outfile,
        issuer=opts.issuer,
        ccache=opts.ccache,
        credkey=opts.credkey,
        role=opts.role,
        minsecs=opts.minsecs,
        vaultserver=opts.vaultserver,
        vaulttokenfile=opts.vaulttokenfile,
        vaulttokenminttl=opts.vaulttokenminttl,
        condor=opts.condor,
    )


if __name__ == "__main__":
    main()
