###########
Basic usage
###########

.. admonition:: Requesting a Robot Kerberos keytab
    :class: hint

    This guide presumes that you already have a robot Kerberos keytab
    to support your application.

    If you don't have one, and would like to request one, please
    see http://robots.ligo.org/.
    On page 1 under *Kind of keytab* select option *4. SciToken keytab*,
    and then proceed to complete the form.
    The request will be recorded as a ticket on the
    `IGWN Computing Help Desk <https://git.ligo.org/computing/helpdesk/-/issues/?label_name%5B%5D=iam%3A%3Arobots>`__.

========================
Getting a Robot SciToken
========================

The most common use case for IGWN Robot Auth is to get a
`SciToken <https://scitokens.org>`__ for a robot identity, to allow
access to secure resources from automated processes.

The :doc:`igwn-robot-get` utility handles the end-to-end authentication
procedure as follows:

1. Initialise a Kerberos credential ('Ticket-granting ticket') for the
   robot principal

2. Use the Kerberos credential to acquire a new SciToken.

To run this, pass the path to the robot Kerberos keytab, to the tool:

.. code-block:: shell
    :caption: Use `igwn-robot-get`

    /usr/bin/igwn-robot-get --keytab /home/user/.secure/robot.keytab

.. admonition:: The first time needs a human
    :class: warning

    The first time that this utility is run must be attended by a human.
    See :ref:`oidc` below for details.

.. admonition:: Kerberos keytabs need strict file permissions
    :class: caution

    Kerberos keytabs are effectively passwords stored in files, so must be
    secured to prevent access by unauthorised users.

    The `igwn-robot-get` utility will assert that the keytab file is
    only readable (or writable) by the user that owns the file, and not
    by anyone else.

    To ensure this, you can use the
    `chmod <https://www.gnu.org/software/coreutils/manual/html_node/chmod-invocation.html>`__
    utility:

    .. code-block:: shell
        :caption: Securing a keytab file

        chmod 400 /home/user/.secure/robot.keytab

.. _igwn-robot-get-usage-htcondor:

----------------------
SciTokens for HTCondor
----------------------

Managing tokens with `HTCondor` can require some special handling.
If you plan to use the SciToken with an HTCondor workflow, pass the
``--condor`` option to `igwn-robot-get`.
This will invoke the ``condor_vault_storer`` executable to generate the
token, which should ensure that any HTCondor special handling is applied.

==================
Checking the token
==================

To validate that `igwn-robot-get` did what you want it to, you can
use the `htdecodetoken` utility provided by the
`htgettoken <https://github.com/fermitools/htgettoken>`__ project.

.. code-block:: json
    :caption: Example output from ``htdecodetoken``

    {
      "aud": "ANY",
      "sub": "igwnconda-scitoken@ligo.org",
      "uid": "igwnconda-scitoken",
      "ver": "scitoken:2.0",
      "nbf": 1234567890,
      "scope": "read:/frames gwdatafind.read gracedb.read dqsegdb.read",
      "iss": "https://cilogon.org/igwn",
      "exp": 1234567899,
      "iat": 1234567890,
      "jti": "https://cilogon.org/oauth2/1234567890abcdefghijklmnopqrstuv?type=accessToken&ts=1234567890123&version=v2.0&lifetime=10800000"
    }

.. admonition:: Use the ``-H`` flag to get human-readable times
    :class: tip

    Dy default `htdecodetoken` emits time claims (e.g. ``exp`` - expiry time)
    as Unix times (seconds since the start of the Unix epoch).

    To display these as human-readable date strings, pass the ``-H`` option to
    ``htdecodetoken``.

------------------------
Checking HTCondor tokens
------------------------

When generating tokens using ``igwn-robot-get --condor``, the best way to
validate the result is to use the
:external+htcondor:ref:`htcondor_command` command line interface:

.. code-block:: console
    :caption: Example usage of ``htcondor credential list``

    $ htcondor credential list
    >> no Windows password found
    >> no Kerberos credential found
    >> Found OAuth2 credentials for 'duncan.macleod@hawk.supercomputingwales.ac.uk':
       Service             Handle                   Last Refreshed  File              Jobs
       igwn                                    2025-05-02 12:09:39  igwn.use

.. _oidc:

===================
OIDC Authentication
===================

When a SciToken is requested for a robot principal for the very first
time [#]_ a human must complete an
`OIDC <https://openid.net/developers/how-connect-works/>`__ workflow
using their web browser.

In these instances, `igwn-robot-get` will print to instructions to the
console, including a URL, that looks something like:

.. code-block:: console

    $ igwn-robot-get ...
    ...
    Attempting OIDC authentication with https://vault.ligo.org:8200

    Complete the authentication at:
        https://cilogon.org/device/?user_code=ABC-DEF-GHI

The user should browser to the listed URL and authenticate with their
LIGO.ORG or IGWN.ORG credentials.

Once the OIDC authentication is complete, `igwn-robot-get` will continue to
request a new SciToken.

.. [#] An OIDC workflow must be completed by a human any time that the
       IGWN Vault server has no active 'refresh token' for the relevant
       principal. This will include the very first authentication, but
       may also include times after restarts of the Vault service itself.
