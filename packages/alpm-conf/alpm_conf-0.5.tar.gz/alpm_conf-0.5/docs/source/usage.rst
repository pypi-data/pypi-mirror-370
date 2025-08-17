Usage
=====

.. _`state diagram`:

State diagram
-------------

.. image:: images/state-diagram.png
   :alt: [alpm-conf state diagram]

The *alpm-conf* subcommands are:
  * ``help``
  * ``diff`` a standalone utility
  * ``create``, ``update``, ``merge``, ``state``, ``reset`` and ``clean`` for
    managing the alpm-conf repository

Running the ``update`` subcommand followed by the ``merge`` subcommand updates
the /etc directory with the changes introduced by new package archives and
updates the *master* branch with changes in the /etc directory. The ``state``
subcommand prints the current state. It is either *start*, *no-cherry-pick*,
*cherry-pick* or *cherry-pick-conflict*.

Help on a subcommand is printed by::

  $ alpm-conf help <subcommand>

The :ref:`alpm-conf` section lists the options available for each subcommand.

*alpm-conf* does not need to be run within its git repository, however conflicts
must be resolved from within the repository.

.. _terminology:

Terminology
-----------

etc-file
    A file within the /etc directory.

user-file
    An *etc-file* that has been created by the *root* user (such as a *netctl*
    profile) and that is tracked in the *master* branch.

cherry-pick
    The changes in the ``new`` [#]_ *etc-files* extracted from new versions of
    package archives that are different from the ``original`` files in the
    previous version and that have been modified by the *root* user in the
    ``current`` instanciation of the file in the /etc directory are commited in
    the *etc_tmp* branch as a **single commit**. The *update* subcommand merges
    these changes into the *master-tmp* branch by running the ``git
    cherry-pick`` command on the *master-tmp* branch using the sha of **this
    commit** from the *etc-tmp* branch.

    The files in the list of files of the *cherry-pick* commit are copied to
    the /etc directory by the *merge* subcommand.

Git repository
--------------

The *master-tmp*, *etc-tmp* and *packages-tmp* temporary branches are created by
the *update* subcommand at respectively the *master*, *etc* and *packages*
branches. All the changes made by the *update* subcommand are made in the
temporary branches. These branches are merged into their ancestor as a
fast-forward merge by the *merge* subcommand. The temporary branches are deleted
after the merge.

*master* branch
    * *etc-files* installed by pacman archives and modified by the *root* user
    * *user-files*

*etc* branch
    * *etc-files* of the package archives currently installed

*packages* branch
    * files whose names are the names of the packages currently installed owning
      *etc-files* that are not symlinks; each file contains the package version
      and the sha256 of their *etc-files*

The *master-prev*, *etc-prev* and *packages-prev* tags are created at
their respective branch just before the fast-forward merge.

Commands
--------

create
""""""

Create the git repository and populate the *master* branch with files
installed by pacman in the /etc directory that have been modified by the *root*
user. The subcommand may be issued by the *root* user or by a plain user, the next
*alpm-conf* subcommands should be issued by the owner of the repository except for
the :ref:`merge cmd` subcommand.

The git repository is located at the directory specified by the command line
option ``--gitrepo-dir`` when this option is set, otherwise at
$XDG_DATA_HOME/alpm-conf if the XDG_DATA_HOME environment variable is set,
otherwise at $HOME/.local/share/alpm-conf.

.. note::
   An *etc-file* added to the *master* branch by this subcommand may have been
   modified in the /etc directory a long time ago and never updated since
   then. The file may be very different from the one in the latest package
   version. In that case, when a new version of this file is installed by
   pacman, the following *update* subcommand may end in the
   *cherry-pick-conflict* state because the file in the *master* branch
   originates from a too old version.

update
""""""

Update the *master-tmp* branch after:

 * a pacman upgrade
 * modifications in the /etc directory of pacman installed *etc-files*
 * modifications in the /etc directory of *user-files* (i.e. files tracked by
   the *master* branch)

After the command has completed, the alpm-conf state is either *no-cherry-pick*,
*cherry-pick* or *cherry-pick-conflict*.

The *update* subcommand calls ``git cherry-pick`` when there are changes in the
*etc-files* extracted from new versions of package archives and the
corresponding files in the /etc directory have been changed. There is a
cherry-pick conflict when git cannot merge all the changes into the *master-tmp*
branch and alpm-conf enters the *cherry-pick-conflict* state. One must resolve
the conflicts to enter the *cherry-pick* state and to be able to run the *merge*
subcommand. A git cherry-pick is just like a git merge, so one may use an editor
to resolve the conflicts such as vim or emacs when a git *mergetool* has been
configured.

Running ``git cherry-pick --abort`` also sets the alpm-conf state to
*cherry-pick*. However this discards all the changes made by the new package
versions and the cherry-pick becomes empty. Use instead the alpm-conf *reset*
subcommand to abort the cherry-pick even in the middle of a partial attempt to
resolve the conflicts. After the *reset* the alpm-conf state becomes *start*.

.. _`merge cmd`:

merge
"""""

The *merge* subcommand:

  * copies the changes made to the *master-tmp* branch by the *cherry-pick* to
    the /etc directory when the current state is *cherry-pick*
  * runs a git fast-forward merge of the temporary branches
  * deletes the temporary branches

When the current state is *cherry-pick*, the subcommand must be run with *root*
privileges [#]_. When the *alpm-conf* repository is owned by a plain user it may
be useful to run the ``sudo`` or ``su`` subcommand to preserve the user's
environment (to access the location of the repository for example). This is done
with the following subcommand line arguments:

 * sudo
     *-E* or *--preserve-env*

 * su
     *-m* or *-p* or *--preserve-environment*

state
"""""

The *state* subcommand prints the current alpm-conf state. See :ref:`state
diagram`.

clean
"""""

The *clean* subcommand removes recursively files not under version control. For
example backup files created by the editor while merging a conflict.

The alpm-conf subcommands *update* and *merge* require a clean working area
because git will fail to switch between branches when a tracked file has been
modified.

reset
"""""

The *reset* subcommand resets the alpm-conf state to *start*:

  - remove recursively files not under version control
  - reset the index and working tree by running the ``git reset --hard`` command
  - delete the temporary branches

diff
""""

The *diff* subcommand prints the differences between the etc files of installed
pacman package archives and the corresponding files modified in the /etc
directory:

  - run the *create* subcommand to create the alpm-conf repository in a
    temporary directory
  - run the ``git diff --diff-filter=M etc master --`` within the repository
  - remove the temporary directory upon completion of the command

Using the *--difftool* option allows using an editor for browsing the changes
instead of printing the diffs.

Checking changes with git
-------------------------

The following git commands are run within the git repository (obviously).

List the *user-file* names (see :ref:`terminology`)::

    $ git diff --name-only --diff-filter=A etc master --

.. note::
  It is easier to use an editor when browsing differences between files in the
  following git commands. In order to use an editor with git one can use a git
  diff tool instead of the *git diff* command. For example *diff* can be
  replaced with *ediff* in the following commands when git is configured to use
  emacs or replaced with *difftool* when git is configured to use gvim as shown
  in the next :ref:`emacs tools` section.

Print the changes before a *merge* subcommand::

    $ git diff --diff-filter=M master...master-tmp

Print the changes after a *merge* subcommand, that is after the temporary
branches have been merged and deleted [#]_::

    $ git diff --diff-filter=M master-prev...master

Print the differences between the *etc-files* of the package archives currently
installed by pacman and the corresponding files modified in the /etc directory
[#]_::

    $ git diff --diff-filter=M etc master --

Print the differences between one *etc-file* of the package archive currently
installed by pacman and the corresponding file modified in the /etc directory::

    $ git diff etc master -- etc/pacman.conf

.. _`emacs tools`:

Git tools
---------

Git tools may be configured in ``$HOME/.gitconfig`` to use an editor for
browsing differences in git revisions or for merging conflicts. The following
links point to the corresponding documentation:

  - `git-difftool - Show changes using common diff tools`_
  - `git-mergetool - Run merge conflict resolution tools to resolve merge conflicts`_

emacs git tools
"""""""""""""""

With the following configuration and the emacs *ediff* major mode loaded, one
may run ``git ediff`` in place of the *git diff* command and ``git mergetool``
in place of the *git merge* command in order to use emacs as a git tool::

  [diff]
      tool = ediff-difftool

  [difftool "ediff-difftool"]
      prompt = false
      cmd = emacs --no-desktop --eval \"(ediff-directories\
              \\\"$LOCAL\\\" \\\"$REMOTE\\\" nil)\" \
              2>/dev/null

  [merge]
      tool = ediff-mergetool

  [mergetool "ediff-mergetool"]
      keepBackup = false
      trustExitCode = true
      cmd = emacs --no-desktop --eval \"(ediff-merge-files-with-ancestor\
              \\\"$LOCAL\\\" \\\"$REMOTE\\\" \\\"$BASE\\\" nil \\\"$MERGED\\\")\" \
              2>/dev/null

  [alias]
      ediff = difftool -d

vim git tools
"""""""""""""

With the following configuration, one may run ``git difftool`` in place of the
*git diff* command and ``git mergetool`` in place of the *git merge* command in
order to use gvim as a git tool::

  [merge]
      tool = gvimdiff

See also `Git documentation on vimdiff`_.

.. _`git-difftool - Show changes using common diff tools`:
   https://git-scm.com/docs/git-difftool
.. _`git-mergetool - Run merge conflict resolution tools to resolve merge conflicts`:
   https://git-scm.com/docs/git-mergetool
.. _`Git documentation on vimdiff`: https://git-scm.com/docs/vimdiff

.. rubric:: Footnotes

.. [#] Using the terminology of the **HANDLING CONFIG FILES** section in the
       pacman man page.
.. [#] alpm-conf uses *setpriv* to run the git commands as the creator of the
       git repository when running with root privileges.
.. [#] The name of a branch followed by the *-prev* suffix is a git tag that
       references the head of this branch upon running the last *update* command
       that was completed successfully by a *merge* command.
.. [#] This may also be done using the ``alpm-conf diff`` command.
