# Releasing IGWN Robot Auth

The instructions below detail how to finalise a new release
for version `{X.Y.Z}`.

In all commands below that placeholder should be replaced
with an actual release version.

## 1. Update the packaging files

-   Pick the new release version number:

    ```shell
    IGWN_ROBOT_AUTH_VERSION="{X.Y.Z}"  # CHANGEME
    ```

-   Create a new branch on which to finalise the release:

    ```shell
    git checkout -b finalise-${IGWN_ROBOT_AUTH_VERSION}
    ```

-   Bump versions and add changelog entries in OS packaging files:

    - `debian/changelog`
    - `rpm/python-igwn-robot-auth.spec`

    NOTE: only document changes to the packaging files in the
    distribution-specific changelog.

-   Add release notes to the `CHANGELOG.md` file.

    The release notes should be formatted as an itemised list of changes from
    the merge requests associated with the
    [milestone on GitLab](https://git.ligo.org/computing/software/igwn-robot-auth/-/milestones):

    ```markdown
    (vX.Y.Z)=
    ## <X.Y.Z> - <DATE>

    -   <change-1>
        ([!<MR>](https://git.ligo.org/computing/software/igwn-robot-auth/-/merge_requests/<MR>))
    -   <change-2>
        ([!<MR>](https://git.ligo.org/computing/software/igwn-robot-auth/-/merge_requests/<MR>))

    [Full details](https://git.ligo.org/computing/software/igwn-robot-auth/-/releases/<X.Y.Z>)
    ```

    This syntax includes `myst-parser` block anchors to provide custom `#vX-Y-Z`
    anchor links for each release.
    Please follow the syntax and formatting as above, or by example of the
    previous releases as much as you can.

-   Commit all of these changes to your branch:

    ```shell
    git commit \
        -m "Finalise release: ${IGWN_ROBOT_AUTH_VERSION}" \
        debian/changelog \
        rpm/python-igwn-robot-auth.spec \
        CHANGELOG.md
    ```

-   Push this branch to your fork:

    ```shell
    git push -u origin finalise-{X.Y.Z}
    ```

-   Follow the link printed in the `remote` response to open a
    merge request on GitLab to finalise the packaging update.

## 2. Tag the release

-   Create an annotated, signed tag in `git` using the release notes
    as the tag message:

    ```shell
    git tag --sign {X.Y.Z}
    ```

-   Push the tag to the project on GitLab:

    ```shell
    git push -u upstream {X.Y.Z}
    ```

    NOTE: the tag pipeline includes jobs to build the source and binary (wheel)
    distributions, and to upload them to <https://pypi.org/project/igwn-robot-auth>.

## 3. Create a Release on GitLab

-   Create a
    [Release on GitLab](https://git.ligo.org/computing/software/igwn-robot-auth/-/releases/new),
    copying the same release notes from the tag message.

    Make sure and correctly associated the correct Tag and Milestone to
    the Release.

## 4. Open an SCCB request

-   Go to <https://git.ligo.org/computing/sccb/-/issues/new> to request
    that this new version be built and distributed for each of the supported platforms.
