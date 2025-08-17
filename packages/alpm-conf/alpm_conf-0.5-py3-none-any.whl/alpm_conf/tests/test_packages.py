"""The packages tests."""

import io
import tempfile
from pathlib import PosixPath
from contextlib import redirect_stdout, ExitStack
from unittest import TestCase, mock
from textwrap import dedent

import pyalpm

from ..packages import PacmanDataBase, Package, get_pacman_dirs
from . import CustomTestCase
from .pkg_utils import (PyalpmHandle, Pkg, PACMAN_PKG, pkg_etcfiles,
                        create_mtree, create_cache_dir, create_packages_dir)

def diff_package_files(package):
    """Diff 'original_files' and 'new_files' of a Package instance."""

    new_files = package.new_files
    original_files = package.original_files
    diff = []
    added = []
    removed = []
    for etc_file in set(new_files).union(original_files):
        new_sha = new_files.get(etc_file)
        old_sha = original_files.get(etc_file)
        if new_sha is None:
            removed.append(etc_file)
        elif old_sha is None:
            added.append(etc_file)
        elif new_sha != old_sha:
            diff.append(etc_file)
    return removed, added, diff

class PacmanDirsTests(TestCase):

    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)

    def test_all_dirs(self):
        pacconf_path = self.stack.enter_context(tempfile.NamedTemporaryFile())
        with open(pacconf_path.name, 'w') as f:
            f.write(dedent("""\
                # The RootDir line ends with white spaces.
                RootDir     = Root/Dir  
                DBPath      = DB/Some Path/
                CacheDir    = Cache/Dir
            """))
        pacman_conf = get_pacman_dirs(pacconf_path.name)
        self.assertEqual(set(('Root/Dir', 'DB/Some Path/', 'Cache/Dir')),
                                            set(pacman_conf.values()))

    def test_missing_dir(self):
        pacconf_path = self.stack.enter_context(tempfile.NamedTemporaryFile())
        with open(pacconf_path.name, 'w') as f:
            f.write(dedent("""\
                DBPath      = DB/Some Path/
                CacheDir    = Cache/Dir
            """))
        pacman_conf = get_pacman_dirs(pacconf_path.name)
        self.assertEqual(set(('/', 'DB/Some Path/', 'Cache/Dir')),
                                            set(pacman_conf.values()))

    def test_commented(self):
        pacconf_path = self.stack.enter_context(tempfile.NamedTemporaryFile())
        with open(pacconf_path.name, 'w') as f:
            f.write(dedent("""\
                #RootDir    = Root/Dir
                DBPath      = DB/Some Path/
                CacheDir    = Cache/Dir
            """))
        pacman_conf = get_pacman_dirs(pacconf_path.name)
        self.assertEqual(set(('Root/Dir', 'DB/Some Path/', 'Cache/Dir')),
                                            set(pacman_conf.values()))

    def test_comment_overriden(self):
        pacconf_path = self.stack.enter_context(tempfile.NamedTemporaryFile())
        with open(pacconf_path.name, 'w') as f:
            f.write(dedent("""\
                RootDir     = Root/Dir
                #RootDir    = Commented/Dir
                DBPath      = DB/Some Path/
                CacheDir    = Cache/Dir
            """))
        pacman_conf = get_pacman_dirs(pacconf_path.name)
        self.assertEqual(set(('Root/Dir', 'DB/Some Path/', 'Cache/Dir')),
                                            set(pacman_conf.values()))

class PackageTests(CustomTestCase):

    def test_installed_packages(self):
        with mock.patch.object(pyalpm, 'Handle', PyalpmHandle):
            pacman_conf = self.pacman_conf()

            PyalpmHandle.set_localdb([PACMAN_PKG])
            db = PacmanDataBase(pacman_conf)
            db.init()
            pkgs = db.installed_packages
            self.assertTrue(all(isinstance(pkg, Pkg)for pkg in pkgs))
            for pkg, etc_files in pkgs.items():
                self.assertEqual(pkg.name, 'pacman')
                self.assertEqual(set(etc_files), set(pkg_etcfiles(pkg)))

    def test_installed_files(self):
        with mock.patch.object(pyalpm, 'Handle', PyalpmHandle):
            pacman_conf = self.pacman_conf()

            # The dummy passwd package must have a file that exists in the
            # local /etc directory.
            passwd_pkg = Pkg('passwd', '1.0', 'x86_64',
                                                (('etc/passwd', 0, 0),))
            PyalpmHandle.set_localdb([PACMAN_PKG, passwd_pkg])

            db = PacmanDataBase(pacman_conf)
            db.init()
            etc_files = pkg_etcfiles(PACMAN_PKG)
            etc_files.extend(pkg_etcfiles(passwd_pkg))
            self.assertEqual(db.installed_files, set(etc_files))

    def test_new_files(self):
        with tempfile.TemporaryDirectory() as db_path:

            pkg = PACMAN_PKG
            count = [5,5,5,5]
            pacman_conf = self.pacman_conf(db_path=db_path)
            create_mtree(pkg, count, pacman_conf['db_path'])

            # Instantiate the pyalpm Package.
            package = Package(pkg, pacman_conf)
            self.assertEqual(set(pkg_etcfiles(pkg)),
                        set(str(path) for path in package.new_files.keys()))

            # Execute the str representation of 'package' as Python code.
            d = {}
            exec(str(package), globals(), d)
            etc_files = d['etc_files']
            version = d['version']
            self.assertEqual(str(package),
                        f"version = '{version}'\n" f"etc_files = {etc_files}")

    def test_new_files_dir(self):
        with tempfile.TemporaryDirectory() as db_path:

            pkg = PACMAN_PKG
            count = [5,5,5,5]
            pacman_conf = self.pacman_conf(db_path=db_path)
            create_mtree(pkg, count, pacman_conf['db_path'], type='dir')

            # Instantiate the pyalpm Package.
            package = Package(pkg, pacman_conf)

            # The first relpath type is dir.
            self.assertTrue('etc/makepkg.conf',
                        set(str(path) for path in package.new_files.keys()))

    def test_new_files_aread(self):
        with tempfile.TemporaryDirectory() as db_path:

            pkg = PACMAN_PKG
            count = [5,5,5,5]
            pacman_conf = self.pacman_conf(db_path=db_path)
            create_mtree(pkg, count, pacman_conf['db_path'], mode='600')

            with redirect_stdout(io.StringIO()) as stdout:
                # Instantiate the pyalpm Package.
                package = Package(pkg, pacman_conf, stdout=stdout)

                # The first relpath is not readable.
                self.assertTrue('etc/makepkg.conf',
                        set(str(path) for path in package.new_files.keys()))

            self.assertIn('etc/makepkg.conf', stdout.getvalue())

class PacmanDataBaseTests(CustomTestCase):

    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)

    def list_new_packages(self, pkg, old_count, new_count,
                          pacman_conf=None, print_not_readable=False,
                          version=None, files=None, type='file', mode='644'):
        """Run the PacmanDataBase.list_new_packages method."""

        # Populate db_path and cache_dir.
        if pacman_conf is None:
            cache_dir = self.stack.enter_context(
                                    create_cache_dir([pkg], [new_count]))
            db_path = self.stack.enter_context(
                            tempfile.TemporaryDirectory(prefix='tmp-db-'))
            pacman_conf = self.pacman_conf(cache_dir=cache_dir,
                                           db_path=db_path)

        create_mtree(pkg, new_count, pacman_conf['db_path'],
                                                        type=type, mode=mode)

        # Create the directory for the checked out packages branch.
        if old_count:
            old_pkg = pkg._replace(version=version) if version else pkg
            old_pkg = old_pkg._replace(files=files) if files else old_pkg
            repo_dir = self.stack.enter_context(
                                create_packages_dir([old_pkg], [old_count]))
        else:
            repo_dir = self.stack.enter_context(create_packages_dir([], []))

        # Instantiate PacmanDataBase and run list_new_packages()
        pacman_db = PacmanDataBase(pacman_conf)
        pacman_db.installed_packages = [pkg]
        pacman_db.list_new_packages(repo_dir,
                                    print_not_readable=print_not_readable)
        return pacman_db

    def test_new_packages(self):

        with redirect_stdout(io.StringIO()):
            old_count = [5,5,5,5]
            new_count = [5,5,5,5]
            pacman_db = self.list_new_packages(PACMAN_PKG,
                                old_count, new_count, version='old version')
            pkgs = pacman_db.new_packages

        self.assertEqual(len(pkgs), 0)

    def test_new_pkgs_version(self):

        # Same version.
        with redirect_stdout(io.StringIO()):
            old_count = [5,5,5,5]
            new_count = [6,6,6,6]
            pacman_db = self.list_new_packages(PACMAN_PKG,
                                               old_count, new_count)
            pkgs = pacman_db.new_packages

        self.assertEqual(len(pkgs), 0)

    def test_new_pkgs_diff(self):

        with redirect_stdout(io.StringIO()):
            old_count = [5,5,5,5]
            new_count = [6,5,5,5]
            pacman_db = self.list_new_packages(PACMAN_PKG,
                                               old_count, new_count,
                                               version='old version')
            pkgs = pacman_db.new_packages

        self.assertEqual(len(pkgs), 1)
        removed, added, diff = diff_package_files(pkgs[0])
        self.assertEqual(diff, [PosixPath('etc/makepkg.conf')])

    def test_new_pkgs_rm(self):

        with redirect_stdout(io.StringIO()):
            old_count = [5,5,5,5,5]
            new_count = [5,5,5,5]
            files = (
                ('etc/foobar.conf', 0, 0),
                ('etc/makepkg.conf', 0, 0),
                ('etc/pacman.conf', 0, 0),
                ('etc/makepkg.conf.d/fortran.conf', 0, 0),
                ('etc/makepkg.conf.d/rust.conf', 0, 0),
                ('usr/foobar', 0, 0),
            )
            pacman_db = self.list_new_packages(PACMAN_PKG,
                                            old_count, new_count,
                                            version='old version', files=files)
            pkgs = pacman_db.new_packages

        self.assertEqual(len(pkgs), 1)
        removed, added, diff = diff_package_files(pkgs[0])
        self.assertEqual(removed, [PosixPath('etc/foobar.conf')])

    def test_new_pkgs_add(self):

        with redirect_stdout(io.StringIO()):
            old_count = [5,5,5]
            new_count = [5,5,5,5]
            files = [
                ('etc/makepkg.conf', 0, 0),
                ('etc/pacman.conf', 0, 0),
                ('etc/makepkg.conf.d/fortran.conf', 0, 0),
                ('etc/makepkg.conf.d/rust.conf', 0, 0),
                ('usr/foobar', 0, 0),
            ]
            pacman_db = self.list_new_packages(PACMAN_PKG,
                                old_count, new_count,
                                version='old version', files=tuple(files[1:]))
            pkgs = pacman_db.new_packages

        self.assertEqual(len(pkgs), 1)
        removed, added, diff = diff_package_files(pkgs[0])
        self.assertEqual(added, [PosixPath('etc/makepkg.conf')])

    def test_new_pkgs_dir(self):

        # The first two files are modified, and the first one is a 'dir'.
        with redirect_stdout(io.StringIO()):
            old_count = [6,6,5,5]
            new_count = [5,5,5,5]
            pacman_db = self.list_new_packages(PACMAN_PKG,
                                          old_count, new_count,
                                          version='old version', type='dir')
            pkgs = pacman_db.new_packages

        self.assertEqual(len(pkgs), 1)
        removed, added, diff = diff_package_files(pkgs[0])
        self.assertEqual(diff, [PosixPath('etc/pacman.conf')])

    def test_new_pkgs_mode(self):

        # The first two files are modified, and the first one mode is '600'.
        with redirect_stdout(io.StringIO()) as stdout:
            old_count = [6,6,5,5]
            new_count = [5,5,5,5]
            pacman_db = self.list_new_packages(PACMAN_PKG,
                                          old_count, new_count,
                                          print_not_readable=True,
                                          version='old version', mode='600')
            pkgs = pacman_db.new_packages

        self.assertEqual(len(pkgs), 1)
        removed, added, diff = diff_package_files(pkgs[0])
        self.assertEqual(diff, [PosixPath('etc/pacman.conf')])

        stdout = stdout.getvalue()
        self.assertIn('Ignored etc-files', stdout)
        self.assertIn('etc/makepkg.conf', stdout)

    def test_new_pkgs_archive(self):

        with redirect_stdout(io.StringIO()) as stdout:
            old_count = [6,5,5,5]
            new_count = [5,5,5,5]
            pkg = PACMAN_PKG

            cache_dir = self.stack.enter_context(
                                    create_cache_dir([pkg], [new_count]))
            db_path = self.stack.enter_context(
                            tempfile.TemporaryDirectory(prefix='tmp-db-'))
            pacman_conf = self.pacman_conf(cache_dir=cache_dir,
                                           db_path=db_path)

            # Make the archive readonly.
            path = PosixPath(pacman_conf['cache_dir'],
                        f'{pkg.name}-{pkg.version}-{pkg.arch}.pkg.tar.zst')
            path.chmod(0o222)

            pacman_db = self.list_new_packages(pkg, old_count, new_count,
                            pacman_conf=pacman_conf, version='old version')
            pkgs = pacman_db.new_packages

        self.assertEqual(len(pkgs), 0)
        self.assertIn(f'Ignore {path.name} (not readable)', stdout.getvalue())

    def test_new_pkgs_missing(self):

        # The package file in the packages branch is missing, 'original_files'
        # is empty (the package has been installed, not upgraded).
        with redirect_stdout(io.StringIO()):
            old_count = []
            new_count = [5,5,5,5]
            pacman_db = self.list_new_packages(PACMAN_PKG,
                                               old_count, new_count,
                                               version='old version')
            pkgs = pacman_db.new_packages

        self.assertEqual(len(pkgs), 1)
        removed, added, diff = diff_package_files(pkgs[0])
        self.assertEqual(set(added), set(PosixPath(path) for path in
                                                pkg_etcfiles(PACMAN_PKG)))

    def test_extract(self):

        with redirect_stdout(io.StringIO()):
            pkg = PACMAN_PKG
            old_count = [5,5,5,5]
            new_count = [6,5,5,5]
            pacman_db = self.list_new_packages(pkg, old_count, new_count,
                                                        version='old version')

            repo_dir = self.stack.enter_context(
                                create_packages_dir([pkg], [old_count]))
            pacman_db.extract_files(repo_dir)

        self.assertEqual(len(pacman_db.new_packages), 1)
        path = PosixPath('etc/makepkg.conf')
        self.assertEqual(list(pacman_db.new_files.keys()), [path])
        self.assertEqual(list(pacman_db.original_files.keys()), [path])
        self.assertTrue(pacman_db.new_files[path] !=
                                            pacman_db.original_files[path])

    def test_extract_missing(self):

        # The package file in the packages branch is missing, 'original_files'
        # is empty (the package has been installed, not upgraded).
        with redirect_stdout(io.StringIO()):
            pkg = PACMAN_PKG
            old_count = []
            new_count = [6,5,5,5]
            pacman_db = self.list_new_packages(pkg, old_count, new_count,
                                                        version='old version')

            repo_dir = self.stack.enter_context(
                                create_packages_dir([], old_count))
            pacman_db.extract_files(repo_dir)

        self.assertEqual(len(pacman_db.new_packages), 1)
        paths = [PosixPath(path) for path in pkg_etcfiles(pkg)]
        self.assertEqual(set(pacman_db.new_files.keys()), set(paths))
        self.assertEqual(set(pacman_db.original_files.keys()), set(paths))
        self.assertEqual(None,
                    pacman_db.original_files[PosixPath('etc/makepkg.conf')])

def main():
    # Run some tests with 'python -m alpm_conf.tests.test_packages'.
    PackageTests().test_new_files()

    test = PacmanDirsTests()
    test.setUp()
    test.test_comment_overriden()

if __name__ == '__main__':
    main()
