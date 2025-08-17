.. _alpm-conf:

alpm-conf man page
==================

Synopsis
--------

  - :program:`alpm-conf` --version
  - :program:`alpm-conf` help {create,update,merge,state,clean,reset,diff}
  - :program:`alpm-conf`
    {help,create,update,merge,state,clean,reset,diff} [*options*]

*alpm-conf* is an ArchLinux tool to manage /etc configuration files using
git. See the documentation at https://alpm-conf.readthedocs.io/en/stable/.

All the subcommands except *help* and *diff* support the *--gitrepo-dir* option:

.. option:: --gitrepo-dir GITREPO_DIR

The git repository is located at GITREPO_DIR when this option is set, otherwise
at $XDG_DATA_HOME/alpm-conf if the XDG_DATA_HOME environment variable is set,
otherwise at $HOME/.local/share/alpm-conf.

create
------

::

  usage: alpm-conf create [--database-dir DATABASE_DIR] [--cache-dir CACHE_DIR]
                          [--print-not-readable ('1', 'yes', 'true')|('0', 'no', 'false')]
                          [--gitrepo-dir GITREPO_DIR] [--root-dir ROOT_DIR]

Create the git repository and populate the etc and master branches.

.. option:: --database-dir DATABASE_DIR

The pacman database directory (default: /var/lib/pacman/).

.. option:: --cache-dir CACHE_DIR

The pacman cache directory (default: /var/cache/pacman/pkg/).

.. option:: --print-not-readable ('1', 'yes', 'true')|('0', 'no', 'false')

Print ignored etc-files that do not have others-read-permission (default: false).

.. option::  --root-dir ROOT_DIR

The root directory, used for testing (default: /).

update
------

::

  usage: alpm-conf update [--database-dir DATABASE_DIR] [--cache-dir CACHE_DIR]
                          [--print-not-readable ('1', 'yes', 'true')|('0', 'no', 'false')]
                          [--gitrepo-dir GITREPO_DIR] [--root-dir ROOT_DIR]

Update the repository with packages and user changes. The changes are made in
the *packages-tmp*, *etc-tmp* and *master-tmp* temporary branches.

The options are the same as the *create* subcommand options.

merge
-----

::

  usage: alpm-conf merge [--gitrepo-dir GITREPO_DIR] [--root-dir ROOT_DIR]

Incorporate the changes made by the previous ``update`` subcommand into the /etc
directory. Copy to the /etc directory the files of the *master-tmp* branch that
are listed in the cherry-pick commit and for each one of the *packages*, *etc*
and *master* branches:

  * A tag named *<branch>-prev* is created at *<branch>* before the
    merge.
  * Changes from *<branch>-tmp* are incorporated into *<branch>* with a
    fast-forward merge.
  * The *<branch>-tmp* is removed.

.. option:: --root-dir ROOT_DIR

The root directory, used for testing (default: /).

state
-----

::

  usage: alpm-conf state [--gitrepo-dir GITREPO_DIR]

Print the current alpm-conf state.

clean
-----

::

  usage: alpm-conf clean [--gitrepo-dir GITREPO_DIR]

Clean the working tree. Remove recursively files not under version control.

reset
-----

::

  usage: alpm-conf reset [--gitrepo-dir GITREPO_DIR]

Clean the working tree, the index and change the alpm-conf state to *start*:

  - remove recursively files not under version control
  - reset the index and working tree by running the ``git reset --hard`` command
  - remove the temporary branches

diff
----

::

  usage: alpm-conf diff [--difftool DIFFTOOL] [--database-dir DATABASE_DIR]
                        [--cache-dir CACHE_DIR] [--root-dir ROOT_DIR]

Print changes made in pacman installed etc files.

An alpm-conf  repository is created in a temporary directory removed upon
completion of the command. A 'git diff' command prints the differences between
the etc files of the package archives currently installed by pacman and the
corresponding files modified in the /etc directory.

Using the '-–difftool' option allows using an editor for browsing the changes
instead of printing the diffs.

.. option:: --difftool DIFFTOOL

Use git DIFFTOOL instead of diff (default: "diff").

.. option:: --database-dir DATABASE_DIR

The pacman database directory (default: /var/lib/pacman/).

.. option:: --cache-dir CACHE_DIR

The pacman cache directory (default: /var/cache/pacman/pkg/).

.. option::  --root-dir ROOT_DIR

The root directory, used for testing (default: /).
