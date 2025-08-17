Release history
===============

Version 0.5
  - A lot of major changes in this release modifying the user interface:

      * The *start*, *no-cherry-pick*, *cherry-pick* and *cherry-pick-conflict*
        states are defined and a simple state machine is implemented. See the
        state diagram in the *Usage* section of the documentation.
      * The *sync* command is renamed *merge* and this command must be run in
        all cases to complete the transaction, whether there is a cherry-pick or
        not. As a consequence, the ``--dry-run`` option of the *update* command
        has been removed as not needed anymore.
      * The following commands have been added: *state*, *clean*, *reset* and
        *diff*.
  - Add the *diff* subcommand.
  - Do not add anymore to the *packages* branch, packages whose metadata in the
    pacman database contains only etc 'file names' that are directory names or
    symlink names.

Version 0.4
  - Improve the documentation on the usage of the *update* command's
    ``--dry-run`` option.

Version 0.3
  - The *python-alpm-conf* package is released as an AUR package.

Version 0.2
  - Parse ``/etc/pacman.conf`` to get the pacman directories default values.
  - Add the *emacs git tools* section.
  - Remove also from the *master* branch the files that have been removed by the
    previous pacman upgrade.
  - Add the *--print-not-readable* option that defaults to ``False``.
  - Print the git command to be used to list the files changed by a commit on
    the *etc-tmp* branch when there are more than ten files on this list.

Version 0.1
  - Project creation.
