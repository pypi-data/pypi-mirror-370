########################################
Running igwn-robot-auth from a container
########################################

IGWN Robot Auth is available as a (Docker) container image, which provides
a convenient way to run the tool in containerised environments without
needing to install Python dependencies locally.

.. admonition:: Run the tool interactively first!
    :class: warning

    The first attempt to get a new token for a robot credential requires
    a human to complete an interactive OIDC workflow using their web browser.

    Before configuring any automation, run the tool interactively first
    to complete the workflow.

    For interactive usage with docker, see :ref:`igwn-robot-auth-docker-interactive-usage`

    For more details, see :ref:`oidc`.

.. admonition:: No containerised HTCondor support
    :class: warning

    The container image does not include HTCondor support, so it cannot be used
    to generate tokens for HTCondor jobs.
    If you need to use the tool with HTCondor, please install the Python package
    directly on your system.

===============================
Running the container manually
===============================

The Docker container is designed to run the :doc:`igwn-robot-get` utility
as its main entrypoint. Any arguments passed to ``docker run`` (or ``podman run``)
will be forwarded to the ``igwn-robot-get`` command.

Basic usage
-----------

.. code-block:: bash
    :substitutions:
    :caption: Basic Docker usage

    docker run --rm \
        --user $(id -u):$(id -g) \
        -v /path/to/tokens:/tokens \
        -v /path/to/robot.keytab:/keytab:ro \
        -e BEARER_TOKEN_FILE=/tokens/scitoken.use \
        -e KRB5_KTNAME=/keytab \
        |image_name|:|image_tag|

This example demonstrates the three key requirements for running the container:

1. **User ID mapping** (``--user $(id -u):$(id -g)``): Run the container with
   the same user and group IDs as the host user to ensure generated tokens
   have the correct ownership.

2. **Token volume** (``-v /path/to/tokens:/tokens``): Mount a directory from the
   host to ``/tokens`` in the container where the generated tokens will be stored.

3. **Bearer token file** (``-e BEARER_TOKEN_FILE=/tokens/scitoken.use``): Set the
   environment variable to control the name of the generated bearer token file.

4. **Keytab mounting** (``-v /path/to/robot.keytab:/keytab:ro`` and ``-e KRB5_KTNAME=/keytab``):
   Mount the robot Kerberos keytab into the container and set the environment
   variable to point to it.

.. _igwn-robot-auth-docker-interactive-usage:

Interactive usage
-----------------

.. admonition:: Interactive usage
    :class: note

    If this is the first time you have ever run `igwn-robot-get` for this
    robot identity, you will need to complete an interactive OIDC workflow.

    To support this, you must include the `-it` flag to run the container
    interactively.

    .. code-block:: bash
        :substitutions:
        :caption: Interactive Docker usage

        docker run --rm -it \
            --user $(id -u):$(id -g) \
            -v /path/to/tokens:/tokens \
            -v /path/to/robot.keytab:/keytab:ro \
            -e KRB5_KTNAME=/keytab \
            |image_name|:|image_tag|

    For more details on OIDC, see :ref:`oidc`.

Advanced options
----------------

You can pass any of the standard :doc:`igwn-robot-get` options to the container:

.. code-block:: bash
    :caption: Using additional options
    :substitutions:

    docker run --rm \
        --user $(id -u):$(id -g) \
        -v /home/user/tokens:/tokens \
        -v /home/user/.secure/robot.keytab:/keytab:ro \
        -e KRB5_KTNAME=/keytab \
        |image_name|:|image_tag| \
            --minsecs 3600 \
            --audience https://my-service.example.org \
            --scopes read:/data

Interactive shell access
------------------------

For debugging or manual intervention, you can override the entrypoint to get
a shell inside the container:

.. code-block:: bash
    :caption: Getting a shell in the container
    :substitutions:

    docker run --rm -it \
        --user $(id -u):$(id -g) \
        -v /path/to/tokens:/tokens \
        -v /path/to/robot.keytab:/keytab:ro \
        -e KRB5_KTNAME=/keytab \
        --entrypoint /bin/bash \
        |image_name|:|image_tag|

============================
Container orchestration
============================

Docker Compose
--------------

For recurring token generation, you can use Docker Compose with a scheduled
service. Here's an example ``docker-compose.yml`` configuration:

.. code-block:: yaml
    :caption: docker-compose.yml for automated token generation
    :substitutions:

    version: '3.8'

    services:
      token-generator:
        image: |image_name|:|image_tag|
        user: "1000:1000"  # Replace with your user ID
        environment:
          - KRB5_KTNAME=/keytab
        volumes:
          - ./tokens:/tokens
          - ./robot.keytab:/keytab:ro
        command: >
          --minsecs 3600
        restart: "no"
        profiles:
          - token-gen

      # Your application that uses the tokens
      my-app:
        image: my-application:latest
        volumes:
          - ./tokens:/app/tokens:ro
        depends_on:
          - token-generator
        # ... other configuration

To run the token generator service:

.. code-block:: bash
    :caption: Running token generation with Docker Compose

    # Generate tokens once
    docker compose --profile token-gen run --rm token-generator

    # Start your main application
    docker compose up my-app

For scheduled execution, you can combine this with a cron job on the host:

.. code-block:: text
    :caption: Crontab entry for Docker Compose token generation

    0 * * * * cd /path/to/compose/directory && docker compose --profile token-gen run --rm token-generator

Kubernetes
----------

For Kubernetes deployments, you can use a
`CronJob <https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/>`__
to periodically generate tokens and store them in a shared volume:

.. code-block:: yaml
    :caption: Kubernetes CronJob for token generation
    :substitutions:

    apiVersion: v1
    kind: Secret
    metadata:
      name: robot-keytab
    type: Opaque
    data:
      robot.keytab: |
        # Base64 encoded keytab content
        # Use: cat robot.keytab | base64 -w 0

    ---
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: robot-tokens
    spec:
      accessModes:
        - ReadWriteMany
      resources:
        requests:
          storage: 1Gi

    ---
    apiVersion: batch/v1
    kind: CronJob
    metadata:
      name: robot-token-generator
    spec:
      schedule: "0 * * * *"  # Every hour
      jobTemplate:
        spec:
          template:
            spec:
              restartPolicy: OnFailure
              securityContext:
                runAsUser: 1000  # Replace with your user ID
                runAsGroup: 1000
                fsGroup: 1000
              containers:
              - name: token-generator
                image: |image_name|:|image_tag|
                args:
                  - "--minsecs"
                  - "3600"
                env:
                - name: KRB5_KTNAME
                  value: "/keytab"
                - name: BEARER_TOKEN_FILE
                  value: "/tokens/scitoken.use"
                volumeMounts:
                - name: robot-tokens
                  mountPath: /tokens
                - name: keytab
                  mountPath: /keytab
                  readOnly: true
              volumes:
              - name: robot-tokens
                persistentVolumeClaim:
                  claimName: robot-tokens
              - name: keytab
                secret:
                  secretName: robot-keytab
                  items:
                  - key: robot.keytab
                    path: keytab
                    mode: 0400

Your application pods can then mount the same ``robot-tokens`` volume to
access the generated tokens:

.. code-block:: yaml
    :caption: Application deployment using shared tokens

    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: my-application
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: my-application
      template:
        metadata:
          labels:
            app: my-application
        spec:
          containers:
          - name: app
            image: my-application:latest
            volumeMounts:
            - name: robot-tokens
              mountPath: /app/tokens
              readOnly: true
            env:
            - name: BEARER_TOKEN_FILE
              value: "/app/tokens/scitoken.use"
          volumes:
          - name: robot-tokens
            persistentVolumeClaim:
              claimName: robot-tokens

.. admonition:: Security considerations
    :class: warning

    When using containers in production:

    - Keytabs are stored securely using Kubernetes Secrets, which provide
      better access controls and are designed for sensitive data
    - Use proper RBAC to limit access to token volumes and secrets
    - Consider using service accounts with appropriate permissions
    - Ensure token files are not readable by unauthorized containers
    - Enable encryption at rest for secrets in your Kubernetes cluster

================
Troubleshooting
================

Common issues and solutions:

**Permission denied errors**
    Ensure you're using ``--user $(id -u):$(id -g)`` to run the container with
    the correct user and group IDs, and that the mounted directories have
    appropriate permissions.

**Keytab not found**
    Verify that the keytab file exists on the host and is mounted correctly.
    Check that the ``KRB5_KTNAME`` environment variable points to the
    correct path inside the container.

**Token not created**
    Check the container logs for error messages. Ensure the first OIDC
    workflow was completed interactively before attempting automated runs.

**Network connectivity issues**
    The container needs network access to reach LIGO authentication services.
    Ensure your container runtime and orchestration platform allow outbound
    HTTPS connections.
