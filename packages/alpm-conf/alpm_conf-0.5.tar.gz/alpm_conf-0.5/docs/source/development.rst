Development
===========

Implementation
--------------

The *PacmanDataBase.extract_files()* method of the *packages* module extracts in
the current directory, from each package archive of newly updated packages, the
content of the ``new`` *etc-files* whose sha256 are different from the
``original`` ones. This method also builds the *new_files* and *original_files*
dictionaries of the *PacmanDataBase* instance. The sets of the keys of both
dictionaries are equal and the values (their sha256) of identical keys are
different.

The *AlpmConf.run_pacman_logic()* method of the *alpm_conf* module implements
the pacman logic used to decide when to not overwrite a configuration file. See
the *run_pacman_logic()* method documentation and the *HANDLING CONFIG FILES*
section in the pacman man page.

Development process [#]_
------------------------

Requirements
""""""""""""

Development:
    * `coverage`_ is used to get the test suite coverage.
    * `python-packaging`_ is used to set the development version name as conform
      to PEP 440.
    * `flit`_ is used to publish *alpm-conf* to PyPi and may be used to install
      *alpm-conf* locally.

      At the root of the *alpm-conf* git repository, use the following command
      to install *alpm-conf* locally::

        $ flit install --symlink [--python path/to/python]

      This symlinks *alpm-conf* into *site-packages* rather than copying it, so
      that you can test changes by running the *alpm-conf* command provided that
      the *PATH* environment variable holds ``$HOME/.local/bin``.

      Otherwise without using `flit`_, one can run those commands from the root
      of the repository as::

        $ python -m alpm_conf.alpm_conf

Documentation:
    * `Sphinx`_
    * `Read the Docs theme`_
    * `curl`_
    * `D2 diagram scripting language`_
    * `Imagemagick`_ to convert svg images to png
    * The latex *TeX Live* package group to build the pdf documentation

Documentation
"""""""""""""

To build locally the documentation follow these steps:

  - Fetch the GitLab test coverage badge::

      $ curl -o images/coverage.svg "https://gitlab.com/xdegaye/alpm-conf/badges/master/coverage.svg?min_medium=85&min_acceptable=90&min_good=90"
      $ magick images/coverage.svg images/coverage.png

  - Build the state diagram image::

      $ d2 --center --scale 0.4 state-diagram.d2 images/state-diagram.svg
      $ magick images/state-diagram.svg images/state-diagram.png

  - Build the html documentation and the man pages::

      $ make -C docs clean html man latexpdf

Updating development version
""""""""""""""""""""""""""""

Run the following commands to update the version name at `latest documentation`_
after a bug fix or a change in the features::

    $ python -m tools.set_devpt_version_name
    $ make -C docs clean html man latexpdf
    $ git commit -m "Update development version name"
    $ git push

Releasing
"""""""""

* Run the test suite from the root of the project [#]_::

    $ python -m unittest --verbose --catch --failfast

* Get the test suite coverage::

    $ coverage run -m unittest
    $ coverage report -m

* Update ``__version__`` in alpm_conf/__init__.py.
* Update docs/source/history.rst if needed.
* Build locally the documentation, see one of the previous sections.
* Commit the changes::

    $ git commit -m 'Version 0.n'
    $ git push

* Tag the release and push::

    $ git tag -a 0.n -m 'Version 0.n'
    $ git push --tags

* Publish the new version on the *AUR*:

  * Run make in the local *AUR* repository to update *pkgver*, *pkgrel* and the
    *sha256* in PKGBUILD and .SRCINFO::

      $ pkgver=<version> pkgrel=<release> make

  * Build the archive and check its content::

      $ make archive
      $ pacman -Qip python-alpm-conf-v-r-any.pkg.tar.zst      # Get package info.
      $ pacman -Qlp python-alpm-conf-v-r-any.pkg.tar.zst      # List package files.

  * Commit the changes and push the changes to the *AUR* repository.

* Publish the new version to PyPi::

    $ flit publish

.. _Read the Docs theme:
    https://docs.readthedocs.io/en/stable/faq.html#i-want-to-use-the-read-the-docs-theme-locally
.. _Sphinx: https://archlinux.org/packages/extra/any/python-sphinx/
.. _curl: https://archlinux.org/packages/core/x86_64/curl/
.. _`D2 diagram scripting language`: https://d2lang.com/
.. _`coverage`: https://archlinux.org/packages/extra/x86_64/python-coverage/
.. _flit: https://archlinux.org/packages/extra/any/python-flit/
.. _unittest command line options:
    https://docs.python.org/3/library/unittest.html#command-line-options
.. _latest documentation: https://alpm-conf.readthedocs.io/en/latest/
.. _python-packaging: https://archlinux.org/packages/extra/any/python-packaging/
.. _Imagemagick: https://archlinux.org/packages/extra/x86_64/imagemagick/

.. rubric:: Footnotes

.. [#] The shell commands in this section are all run from the root of the
       repository.
.. [#] See `unittest command line options`_.
