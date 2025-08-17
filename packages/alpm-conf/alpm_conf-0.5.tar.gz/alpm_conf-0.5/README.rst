.. image:: images/coverage.png
   :alt: [alpm-conf test coverage]

`alpm-conf`_ is an ArchLinux tool to manage /etc configuration files using
``git``. It is implemented as a Python package.

Overview
--------

Packages installed by ``pacman`` whose etc files have been changed in the last
pacman upgrade and that have been changed by the ``root`` user [#]_ in the /etc
directory are tracked in the *master* branch of the git repository created by
the *alpm-conf* ``create`` subcommand.

Using the same algorithm that is used by pacman to select files that are
installed with a *.pacnew* extension [#]_, the ``update`` subcommand
cherry-picks the changes (i.e. merges the changes) made to etc files by the
pacman upgrade into the files on a temporary *master-tmp* branch [#]_ created by
the subcommand as a descendant of the *master* branch. The ``merge`` subcommand
merges the *master-tmp* branch into the *master* branch and copies those files
to the /etc directory. This completes the transaction and the temporary branch
is deleted.

*alpm-conf* also tracks the changes in files that are created in /etc by the
root user such as *netctl* profiles for example. The files must be added first
and commited to the *master* branch by the *alpm-conf* user in order to be
tracked afterward by alpm-conf.

The ``diff`` subcommand is a standalone utility that uses a temporary alpm-conf
repository to print [4]_ the differences between the etc files of installed
pacman package archives and the corresponding files modified in the /etc
directory. The command takes less than 2 seconds to complete on a plain laptop
with 1212 installed packages.

Git commands allow to:

 * list the names of files created in /etc by the root user and tracked in the
   *master* branch
 * print [#]_ the changes made in the *master-tmp* branch before running the
   ``merge`` subcommand
 * print [4]_ the changes made by the last *alpm-conf* ``merge`` subcommand
 * print [4]_ the differences between the etc files of installed pacman package
   archives and the corresponding files modified in the /etc directory

Documentation
-------------

The documentation is hosted at `Read the Docs`_:

 - The `stable documentation`_ of the last released version.
 - The `latest documentation`_ of the current GitLab development version.

To access the documentation as a pdf document one must click on the icon at the
down-right corner of any page. It allows to switch between stable and latest
versions and to select the corresponding pdf document.

Requirements
------------

The ArchLinux packages that are required by *alpm-conf* are installed with the
command:

.. code-block:: text

  # pacman -Sy git util-linux alpm-mtree python pyalpm python-zstandard

``pyalpm`` and ``alpm-mtree`` are used to access the ArchLinux local
database, ``util-linux`` provides *setpriv* allowing to run *alpm-conf* as root
while running git commands as the creator of the git repository.

Installation
------------

Install the `python-alpm-conf`_ package from the AUR.

Or install *alpm-conf* with pip::

  $ python -m pip install alpm-conf


.. _alpm-conf: https://gitlab.com/xdegaye/alpm-conf
.. _Read the Docs: https://about.readthedocs.com/
.. _stable documentation: https://alpm-conf.readthedocs.io/en/stable/
.. _latest documentation: https://alpm-conf.readthedocs.io/en/latest/
.. _python-alpm-conf: https://aur.archlinux.org/packages/python-alpm-conf

.. rubric:: Footnotes

.. [#] Packaged files that are modified by a package scriptlet are considered as
       files modified by the root user.
.. [#] See the **HANDLING CONFIG FILES** section in the pacman man page.
.. [#] The ``update`` subcommand also creates the *etc-tmp* and *packages-tmp*
       temporary branches. These branches as well as the *etc* and *packages*
       branches are used internally by alpm-conf. The three temporary branches
       are deleted upon completion of the ``merge`` and ``reset`` subcommands.
.. [#] Or show the changes or differences using an editor such as vim or emacs
       if a git difftool has been configured.
