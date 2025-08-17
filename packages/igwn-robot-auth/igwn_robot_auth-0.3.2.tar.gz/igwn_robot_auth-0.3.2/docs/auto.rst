######################
Automating credentials
######################

One key purpose of IGWN Robot Auth is to simplify automating renewal of
credentials so that an active, not-imminently-expiring SciToken is always
available for a scientific application (for example, a data analysis pipeline).

.. admonition:: Run the tool interactively first!
    :class: warning

    The first attempt to get a new token for a robot credential requires
    a human to complete an interactive OIDC workflow using their web browser.

    Before configuring any automation, run the tool interactively first
    to complete the workflow.

    For more details, see :ref:`oidc`.

====
Cron
====

The most common utility for automatically executing a process at regular
intervals is `Cron <https://en.wikipedia.org/wiki/Cron>`__.

The :doc:`igwn-robot-get` utility can be automated with Cron using
something like the following as a Crontab entry:

.. code-block:: text
    :caption: Automating `igwn-robot-get` with Cron

    0 * * * * /usr/bin/igwn-robot-get --keytab /home/user/.secure/robot.keytab --minsecs 3600

This will execute the :doc:`igwn-robot-get` utility once per hour, on the hour,
with the given options, writing the output file to the default location for non-interactive sessions:

.. code-block:: text
    :caption: Default bearer token file location for non-interactive sessions

    /tmp/bt_u$(id -u)

where ``$(id -u)`` resolves to the user ID of the POSIX user that owns the
crontab entry.

.. admonition:: Set the `BEARER_TOKEN_FILE` environment variable
    :class: tip

    The default bearer token file for interactive sessions is different to
    that for non-interactive sessions above.

    It is strongly recommended to set the ``BEARER_TOKEN_FILE`` environment
    variable point at the `/tmp/...` path, so that standard SciToken-aware
    tooling can automatically discover it regardless of the session:

    .. tab-set::

        .. tab-item:: Bourne shell (`sh`, `bash`, `zsh`)

            .. code-block:: bash

                export BEARER_TOKEN_FILE="/tmp/bt_u$(id -u)"

        .. tab-item:: C shell (`csh`, `tcsh`)

            .. code-block:: csh

                setenv BEARER_TOKEN_FILE "/tmp/bt_u$(id -u)"

        .. tab-item:: Fish

            .. code-block:: fish

                set -x BEARER_TOKEN_FILE="/tmp/bt_u$(id -u)"

.. admonition:: Always specify ``--minsecs <cadence>``
    :class: tip

    The ``--minsecs`` option to `igwn-robot-get` specifies the minimum
    acceptable remaining lifetime for an existing bearer token to be
    reused.
    If a token exists already with a remanining lifetime that exceeds
    ``--minsecs``, a new token will **not** be created.
    It is therefore important to specify ``--minsecs <cadence>`` where
    ``<cadence>`` is the time (in seconds) between iterations of the
    automation.

    The default value is ``--minsecs 3600`` to guarantee that a bearer
    token always has at least one hour remaining before expiry.

.. admonition:: Use ``--condor`` when tokens will be used with HTCondor
    :class: tip

    If the token will be used as part of an HTCondor pipeline, you should
    ensure that you include the ``--condor`` option in the ``igwn-robot-get``
    command configured with cron.
    This should ensure that any HTCondor-specific token handling is applied.

    For full details, see :ref:`igwn-robot-get-usage-htcondor`.

.. admonition:: Cron syntax
    :class: seealso

    For more details on Crontab syntax, we recommend
    `Cronguru <https://crontab.guru/#0_*_*_*_*>`__.
