.. sectionauthor:: Duncan Macleod <duncan.macleod@ligo.org>

##########################
Installing IGWN Robot Auth
##########################

.. tab-set::

    .. tab-item:: Conda

        .. code-block:: bash
            :caption: Install `igwn-robot-auth` with Conda

            conda install -c conda-forge igwn-robot-auth

    .. tab-item:: Debian Linux

        .. code-block:: bash
            :caption: Install `igwn-robot-auth` with Apt

            apt-get install python3-igwn-robot-auth

        See the IGWN Computing Guide software repositories entry for
        `Debian <https://computing.docs.ligo.org/guide/software/debian/>`__
        for instructions on how to configure the required
        IGWN Debian repositories.

    .. tab-item:: Enterprise Linux

        .. code-block:: bash
            :caption: Install `igwn-robot-auth` with DNF

            dnf install python3-igwn-robot-auth

        See the IGWN Computing Guide software repositories entries for
        `Rocky Linux 8 <https://computing.docs.ligo.org/guide/software/rl8/>`__ or
        `Rocky Linux 9 <https://computing.docs.ligo.org/guide/software/rl9/>`__
        for instructions on how to configure the required IGWN RPM repositories.

    .. tab-item:: Pip

        .. code-block:: bash
            :caption: Install `igwn-robot-auth` with Pip

            python -m pip install igwn-robot-auth

        To include support for HTCondor, include the ``[htcondor]`` extra:

        .. code-block:: bash
            :caption: Install `igwn-robot-auth[htcondor]` with Pip

            python -m pip install igwn-robot-auth[htcondor]
