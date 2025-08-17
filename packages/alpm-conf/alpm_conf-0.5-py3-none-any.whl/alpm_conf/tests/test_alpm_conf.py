"""The alpm-conf tests."""

import os
import io
import re
import tempfile
import argparse
import shutil
import functools
from pathlib import PosixPath
from collections import namedtuple
from unittest import mock, skipIf
from contextlib import (contextmanager, redirect_stdout, redirect_stderr,
                        ExitStack)

import pyalpm

from .. import ApcError
from .. import __doc__ as ALPMCONF_DOC
from ..alpm_conf import alpm_conf, AlpmConf, sha256
from ..git import GitRepo, get_logname
from ..packages import package_as_dict
from . import CustomTestCase
from .pkg_utils import (PyalpmHandle, PACMAN_PKG, create_mtree, Pkg,
                        create_cache_dir, create_etc_dir, pkg_etcfiles,
                        build_archives)

# 'gitrepo_dir' is not used by the diff tests.
EmtDirectories = namedtuple('EmtDirectories',
                    ['database_dir', 'cache_dir', 'root_dir', 'gitrepo_dir'],
                    defaults=(None,))
ALPMCONF_BRANCHES = set(GitRepo._ALPMCONF_BRANCHES)

def _current_pacman_pkg():
    handle = pyalpm.Handle('/', '/var/lib/pacman/')
    localdb = handle.get_localdb()
    pacman_pkg = localdb.get_pkg('pacman')
    return PACMAN_PKG._replace(version=pacman_pkg.version)

CURRENT_PACMAN_PKG = _current_pacman_pkg()

@contextmanager
def patch_pyalpm(pkgs):
    with mock.patch.object(pyalpm, 'Handle', PyalpmHandle):
        PyalpmHandle.set_localdb(pkgs)
        yield

@functools.cache
def args_from_emtdirs(apc_dirs, fields=None):
    """Return update command line args from an EmtDirectories named tuple."""

    if fields is None:
        fields = apc_dirs._fields

    dirs = apc_dirs._asdict()
    args = []
    for key, val in dirs.items():
        if key in fields:
            args.append('--' + key.replace('_', '-'))
            args.append(str(val))
    return args

def run_create(apc_dirs, create_args=None):

    if not create_args:
        create_args = args_from_emtdirs(apc_dirs)
    with redirect_stdout(io.StringIO()) as stdout:
        return alpm_conf(['alpm-conf', 'create'] + create_args)

def run_update(apc_dirs, update_args=None):

    if not update_args:
        update_args = args_from_emtdirs(apc_dirs)
    with redirect_stdout(io.StringIO()) as stdout:
        return alpm_conf(['alpm-conf', 'update'] + update_args)

def run_merge(apc_dirs, merge_args=None):

    if not merge_args:
        merge_args = args_from_emtdirs(apc_dirs,
                                       fields=('gitrepo_dir', 'root_dir'))
    with redirect_stdout(io.StringIO()) as stdout:
        return alpm_conf(['alpm-conf', 'merge'] + merge_args)

def iter_etcfiles(dir_path):
    """Iterator of the files in the etc directory of 'dir_path'."""

    etc_dir = dir_path / 'etc'
    for root, dirs, files in etc_dir.walk():
        for file in files:
            path = root / file
            path = path.relative_to(dir_path)
            yield str(path)

def modify_line(abspath, no, new):
    """Replace line number 'no' by 'new' in 'abspath'.

    Append 'new' to 'abspath' if 'no' is -1.
    """

    with open(abspath) as f:
        lines = f.readlines()

    with open(abspath, 'w') as f:
        for idx, line in enumerate(lines):
            if idx + 1 == no:
                f.write(new)
            else:
                f.write(line)
        if no == -1:
                f.write(new)

class CommandLineTests(CustomTestCase):

    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)

    def test_main_help(self):
        with redirect_stdout(io.StringIO()) as stdout:
            alpm_conf(['alpm-conf', 'help'])

        self.assertIn(ALPMCONF_DOC, stdout.getvalue())

    def test_create_help(self):
        with redirect_stdout(io.StringIO()) as stdout:
            alpm_conf(['alpm-conf', 'help', 'create'])

        self.assertIn('Create the git repository', stdout.getvalue())

    def test_update_help(self):
        with redirect_stdout(io.StringIO()) as stdout:
            alpm_conf(['alpm-conf', 'help', 'update'])

        self.assertIn('Update the repository', stdout.getvalue())

    def test_isdir(self):
        file_path = self.stack.enter_context(tempfile.NamedTemporaryFile())

        with (self.assertRaisesRegex(argparse.ArgumentError,
                                     'not a directory'),
              redirect_stderr(io.StringIO())):

            try:
                alpm_conf(['alpm-conf', 'create',
                                        '--cache-dir', file_path.name])
            except SystemExit as e:
                raise e.__context__ from None

    def test_parse_boolean(self):
        cache_dir = self.stack.enter_context(
                            tempfile.TemporaryDirectory(prefix='cache-'))
        repo_dir = self.stack.enter_context(
                            tempfile.TemporaryDirectory(prefix='repo-'))

        # Use the currently installed pacman package.
        self.stack.enter_context(patch_pyalpm([CURRENT_PACMAN_PKG]))

        with redirect_stdout(io.StringIO()) as stdout:

            args = ['--cache-dir', cache_dir, '--gitrepo-dir', repo_dir]
            apc = alpm_conf(['alpm-conf', 'create', '--print-not-readable',
                             'yes'] + args)

            self.assertEqual(apc.print_not_readable, True)

    def test_bad_parse_boolean(self):
        answer = 'FOO'
        with (self.assertRaisesRegex(argparse.ArgumentError, answer),
              redirect_stderr(io.StringIO())):

            try:
                alpm_conf(['alpm-conf', 'create',
                                        '--print-not-readable', answer])
            except SystemExit as e:
                raise e.__context__ from None

    def test_no_command(self):
        with (self.assertRaises(SystemExit),
                            redirect_stderr(io.StringIO()) as stderr):
            alpm_conf(['alpm-conf'])
        self.assertIn('command is required', stderr.getvalue())

    def test_ApcError(self):
        cache_dir = self.stack.enter_context(
                            tempfile.TemporaryDirectory(prefix='cache-'))
        repo_dir = self.stack.enter_context(
                            tempfile.TemporaryDirectory(prefix='repo-'))
        self.stack.enter_context(patch_pyalpm([PACMAN_PKG]))

        args = ['--cache-dir', cache_dir, '--gitrepo-dir', repo_dir]
        with (self.assertRaises(ApcError) as cm,
                            redirect_stderr(io.StringIO())):
            try:
                alpm_conf(['alpm-conf', 'update'] + args)

            except SystemExit as e:
                raise e.__context__ from None

        self.assertIn('no git repository', str(cm.exception))

    def test_set_repo(self):
        path = PosixPath('/foobar')
        apc = AlpmConf(**{'gitrepo_dir': path})
        self.assertEqual(apc.repo.dir_path, path)

    def test_set_repo_env(self):
        path = '/foobar'
        xdg_data_home = os.environ.get('XDG_DATA_HOME')
        if xdg_data_home is not None:
            path = PosixPath(xdg_data_home)
        else:
            os.environ['XDG_DATA_HOME'] = path

        try:
            apc = AlpmConf(**{'gitrepo_dir': None})
            self.assertEqual(apc.repo.dir_path, PosixPath(path) / 'alpm-conf')
        finally:
            if xdg_data_home is None:
                del os.environ['XDG_DATA_HOME']

    @skipIf(get_logname() is None, "no controlling terminal")
    def test_set_repo_default(self):
        xdg_data_home = os.environ.get('XDG_DATA_HOME')
        if xdg_data_home is not None:
            del os.environ['XDG_DATA_HOME']

        try:
            apc = AlpmConf(**{'gitrepo_dir': None})
            self.assertTrue(apc.repo.dir_path.match(
                                                '**/.local/share/alpm-conf'))
        finally:
            if xdg_data_home is not None:
                os.environ['XDG_DATA_HOME'] = xdg_data_home

    def test_set_repo_login(self):
        xdg_data_home = os.environ.get('XDG_DATA_HOME')
        if xdg_data_home is not None:
            del os.environ['XDG_DATA_HOME']

        with (mock.patch.object(os, 'getlogin') as getlogin,
                    self.assertRaises(ApcError) as cm):
            getlogin.side_effect = OSError
            try:
                AlpmConf(**{'gitrepo_dir': None})
            finally:
                if xdg_data_home is not None:
                    os.environ['XDG_DATA_HOME'] = xdg_data_home

        self.assertIn('controlling terminal', str(cm.exception))

class AlpmConfTestCase(CustomTestCase):

    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)

    def create_alpm_conf_env(self, pkgs, pkg_counts, new_counts,
                                                        with_repo_dir=True):
        """Build the environment for the creation of a repository.

        'pkgs'       list of instances of Pkg namedtuple
        'pkg_counts' list of line number counts for each file of Pkg.files
        'new_counts' list of line number counts for each file in 'root_dir'
        """

        db_path = self.stack.enter_context(
                                tempfile.TemporaryDirectory(prefix='tmp-db-'))
        db_path = PosixPath(db_path)
        for idx, pkg in enumerate(pkgs):
            create_mtree(pkg, pkg_counts[idx], db_path)

        cache_dir = self.stack.enter_context(
                                create_cache_dir(pkgs, pkg_counts))
        root_dir = self.stack.enter_context(
                        create_etc_dir(pkgs, new_counts, prefix='root-'))
        self.stack.enter_context(patch_pyalpm(pkgs))

        if with_repo_dir:
            repo_dir = self.stack.enter_context(
                            tempfile.TemporaryDirectory(prefix='tmp-repo-'))
            repo_dir = PosixPath(repo_dir)
            return EmtDirectories(db_path, cache_dir, root_dir, repo_dir)
        else:
            return EmtDirectories(db_path, cache_dir, root_dir)

    def create_repository(self, pkgs=[PACMAN_PKG], pkg_counts=[[5,5,5,5]],
                                                    new_counts=[[5,5,5,5]]):
        self.apc_dirs = self.create_alpm_conf_env(pkgs, pkg_counts,
                                                                new_counts)
        return run_create(self.apc_dirs)

    def install_new_package(self, pkgs, counts, apc_dirs):
        for idx, pkg in enumerate(pkgs):
            create_mtree(pkg, counts[idx], apc_dirs.database_dir)

        build_archives(pkgs, counts, apc_dirs.cache_dir)
        self.stack.enter_context(patch_pyalpm(pkgs))

    def set_ready_to_merge(self, relpath):
        """Set up the context as ready to run the 'merge' command."""

        self.create_repository()
        apc_dirs = self.apc_dirs

        # Modify a file in root_dir and run the 'update' command.
        changed_line = 'first line\n'
        modify_line(apc_dirs.root_dir / relpath, 1, changed_line)
        run_update(apc_dirs)
        run_merge(apc_dirs)

        # Install a new version of the pacman package with a change in
        # 'etc/pacman.conf' and run 'update'.
        count = [5,6,5,5]
        pkg = PACMAN_PKG._replace(version='8.0')
        self.install_new_package([pkg], [count], apc_dirs)
        apc = run_update(apc_dirs)

        self.assertEqual(apc.repo.branches, ALPMCONF_BRANCHES)

        return apc

    def get_ApcError_exception(self, func, *args, **kwds):
        with self.assertRaises(ApcError) as cm:
            try:
                func(*args, **kwds)
            except SystemExit as e:
                raise e.__context__ from None
        return cm.exception

    def setup_conflict(self):
        """Build an AlpmConf instance that has a cherry-pick conflict."""

        self.create_repository()
        self.relpath = 'etc/pacman.conf'
        self.args = args_from_emtdirs(self.apc_dirs)

        # Modify a file in root_dir and run the 'update' command
        # so that the next 'update' does not include this commit
        # in master-tmp.
        changed_line = 'last line\n'
        modify_line(self.apc_dirs.root_dir / self.relpath, -1, changed_line)
        run_update(self.apc_dirs, self.args)
        run_merge(self.apc_dirs)

        # Install a new version of the pacman package with a change in
        # 'etc/pacman.conf' and run 'update'.
        count = [5,6,5,5]
        pkg = PACMAN_PKG._replace(version='8.0')
        self.install_new_package([pkg], [count], self.apc_dirs)

class AlpmConfTests(AlpmConfTestCase):

    def test_create(self):
        apc = self.create_repository()

        with redirect_stdout(io.StringIO()) as stdout:
            apc.cmd_state()
        self.assertIn("'start'", stdout.getvalue())

        # Check master branch.
        apc.repo.checkout('master')
        repo_dir = self.apc_dirs.gitrepo_dir
        etc_dir = repo_dir / 'etc'
        self.assertFalse(etc_dir.exists())

        # Check etc branch.
        apc.repo.checkout('etc')
        self.assertEqual(set(iter_etcfiles(repo_dir)),
                                        set(pkg_etcfiles(PACMAN_PKG)))

    def test_not_a_package(self):
        pkg_count = [5,5,5,5]
        apc_dirs = self.create_alpm_conf_env([PACMAN_PKG], [pkg_count],
                                                                [pkg_count])
        args = args_from_emtdirs(apc_dirs)

        # Create the repository.
        apc = run_create(apc_dirs, args)

        # Add a file that is not a package in the packages branch.
        dummy_pkg = 'this-is-not-a-package'
        apc.repo.checkout('packages')
        with open(apc_dirs.gitrepo_dir / dummy_pkg, 'a') as f:
            f.write('some line\n')
        apc.repo.git_cmd(f'add {dummy_pkg}')
        apc.repo.git_cmd('commit -m some_commit_msg')

        # Run the 'update' command.
        # The 'dummy_pkg' file is removed because there is no package with
        # such a name in pacman database.
        with redirect_stdout(io.StringIO()) as stdout:
            apc = alpm_conf(['alpm-conf', 'update'] + args)

        output = stdout.getvalue()
        self.assertIn('Remove 1 package from the packages-tmp branch', output)
        self.assertIn(dummy_pkg, output)

    def test_not_etc_file(self):
        pkg_count = [5,5,5,5]
        apc_dirs = self.create_alpm_conf_env([PACMAN_PKG], [pkg_count],
                                                                [pkg_count])
        args = args_from_emtdirs(apc_dirs)

        # Create the repository.
        apc = run_create(apc_dirs, args)

        # Add a file that is not an etc file in the etc and master branches.
        dummy_file = 'this-is-not-an-etc-file'
        for branch in ('etc', 'master'):
            apc.repo.checkout(branch)
            with open(apc_dirs.gitrepo_dir / dummy_file, 'a') as f:
                f.write('some line\n')
            apc.repo.git_cmd(f'add {dummy_file}')
            apc.repo.git_cmd('commit -m some_commit_msg')

        # Run the 'update' command.
        # The 'dummy_file' file is removed from the etc branch because there
        # is no file with such a name in the installed etc files. It is
        # removed from the master branch because it is removed from the etc
        # branch.
        with redirect_stdout(io.StringIO()) as stdout:
            apc = alpm_conf(['alpm-conf', 'update'] + args)

        output = stdout.getvalue()
        self.assertIn('Remove 1 file from the etc-tmp branch', output)
        self.assertIn('Remove 1 file from the master-tmp branch', output)
        self.assertIn(dummy_file, output)

    def test_file_untracked(self):
        apc = self.create_repository()

        # Make a change not staged for commit.
        repo_dir = self.apc_dirs.gitrepo_dir
        path = repo_dir / 'foo'
        with open(path, 'w') as f:
            pass

        # Run the update command.
        exception = self.get_ApcError_exception(run_update, self.apc_dirs)
        self.assertIn("Run 'alpm-conf clean'", str(exception))

        # Clean the repository.
        with redirect_stdout(io.StringIO()) as stdout:
            alpm_conf(['alpm-conf', 'clean', '--gitrepo-dir', str(repo_dir)])
        self.assertFalse(path.is_file())

    def test_file_staged(self):
        apc = self.create_repository()

        # Make a change to be commited.
        relpath = 'foo'
        repo_dir = self.apc_dirs.gitrepo_dir
        path = repo_dir / relpath
        with open(path, 'w') as f:
            pass
        apc.repo.git_cmd(['add', relpath])

        # Run the update command.
        exception = self.get_ApcError_exception(run_update, self.apc_dirs)
        self.assertIn("Run 'alpm-conf reset'", str(exception))

        # Clean the repository.
        with redirect_stdout(io.StringIO()) as stdout:
            apc = alpm_conf(['alpm-conf', 'reset', '--gitrepo-dir',
                                                        str(repo_dir)])
        self.assertFalse(path.is_file())
        self.assertEqual(apc.state, 'start')

    def test_create_many(self):
        count = 20
        files = []
        for i in range(count):
            files.append((f'etc/foo-{i}.conf', 0, 0))
        pkg = PACMAN_PKG._replace(files=tuple(files))

        pkg_count = [5 for i in range(count)]
        apc_dirs = self.create_alpm_conf_env([pkg], [pkg_count],
                                                                [pkg_count])
        args = args_from_emtdirs(apc_dirs)
        with redirect_stdout(io.StringIO()) as stdout:
            apc = alpm_conf(['alpm-conf', 'create'] + args)

        # Check master branch.
        apc.repo.checkout('master')
        repo_dir = apc_dirs.gitrepo_dir
        etc_dir = repo_dir / 'etc'
        self.assertFalse(etc_dir.exists())

        # Check etc branch.
        apc.repo.checkout('etc')
        self.assertEqual(set(iter_etcfiles(repo_dir)), set(pkg_etcfiles(pkg)))

        # Check that the git command to print the files exists.
        self.assertIn('git diff-tree --no-commit-id --name-only -r',
                                                            stdout.getvalue())

    def test_create_remove_pkgs(self):
        # Set the environment with two packages.
        foobar_pkg = Pkg('foobar', '1.0', 'x86_64',
                         (('etc/foo.conf', 0, 0), ('etc/bar.conf', 0, 0),))
        pkg_counts = new_counts = [[5,5,5,5], [5,5]]
        apc_dirs = self.create_alpm_conf_env([PACMAN_PKG, foobar_pkg],
                                                    pkg_counts, new_counts)
        args = args_from_emtdirs(apc_dirs)

        # Modify a file from the 'foobar' package in root_dir.
        # This will cause the 'create' command to add the file to the master
        # branch and we can verify that the file is removed from master
        # by the next update command after the package has been removed.
        foo_conf = 'etc/foo.conf'
        with open(apc_dirs.root_dir / foo_conf, 'a') as f:
            f.write('line 5\n')

        # Create the repository.
        apc = run_create(apc_dirs, args)

        # Check etc branch.
        apc.repo.checkout('etc')
        repo_dir = apc_dirs.gitrepo_dir
        self.assertEqual(set(iter_etcfiles(repo_dir)),
                set(pkg_etcfiles(PACMAN_PKG)).union(pkg_etcfiles(foobar_pkg)))

        # Check packages branch
        apc.repo.checkout('packages')
        self.assertTrue((repo_dir / PACMAN_PKG.name).is_file())
        self.assertTrue((repo_dir / foobar_pkg.name).is_file())

        # Remove 'foobar_pkg' from the list of installed packages and check
        # that its etc files are removed and the Pkg has been removed from the
        # packages branch.
        self.stack.enter_context(patch_pyalpm([PACMAN_PKG]))
        with redirect_stdout(io.StringIO()) as stdout:
            apc = alpm_conf(['alpm-conf', 'update'] + args)

        # Check etc branch.
        apc.repo.checkout('etc-tmp')
        repo_dir = apc_dirs.gitrepo_dir
        self.assertEqual(set(iter_etcfiles(repo_dir)),
                                        set(pkg_etcfiles(PACMAN_PKG)))

        # Check packages branch
        apc.repo.checkout('packages-tmp')
        self.assertTrue((repo_dir / PACMAN_PKG.name).is_file())
        self.assertFalse((repo_dir / foobar_pkg.name).is_file())

        # Check that 'etc/foo.conf' has been removed from master.
        output = stdout.getvalue()
        self.assertIn('Remove 1 file from the master-tmp branch', output)
        relpaths = apc.repo.list_changed_files('master')
        self.assertEqual(relpaths, [foo_conf])

    def test_create_diff(self):
        LINE_COUNT = 10
        new_count = [5, LINE_COUNT, 5, 5]
        apc = self.create_repository(new_counts=[new_count])

        # Check master branch.
        apc.repo.checkout('master')
        repo_dir = self.apc_dirs.gitrepo_dir
        with open(repo_dir / 'etc/pacman.conf') as f:
            lines = f.readlines()
        self.assertEqual(len(lines), LINE_COUNT)
        self.assertEqual(set(iter_etcfiles(repo_dir)), {'etc/pacman.conf'})

    def test_update_pacman_file(self):
        self.create_repository()
        apc_dirs = self.apc_dirs

        # Modify a file in root_dir and run the 'update' command.
        relpath = 'etc/pacman.conf'
        with open(apc_dirs.root_dir / relpath, 'a') as f:
            f.write('line 5\n')
        apc = run_update(apc_dirs)
        run_merge(apc_dirs)

        # Check master branch.
        apc.repo.checkout('master')
        repo_dir = apc_dirs.gitrepo_dir
        self.assertEqual(set(iter_etcfiles(repo_dir)), {relpath})
        self.assertEqual(sha256(repo_dir / relpath),
                                sha256(apc_dirs.root_dir / relpath))

    def test_update_remove_file(self):
        pkg_count = [5,5,5,5]
        apc_dirs = self.create_alpm_conf_env([PACMAN_PKG], [pkg_count],
                                                                [pkg_count])
        args = args_from_emtdirs(apc_dirs)

        # Modify a file in root_dir.
        # This will cause the 'create' command to add the file to the master
        # branch and we can verify that the file is removed from master
        # by the next update command.
        relpath = 'etc/pacman.conf'
        with open(apc_dirs.root_dir / relpath, 'a') as f:
            f.write('line 5\n')

        # Create the repository.
        run_create(apc_dirs, args)

        # Remove 3 files from the package.
        pkg = PACMAN_PKG._replace(files=(('etc/makepkg.conf', 0, 0),))
        self.stack.enter_context(patch_pyalpm([pkg]))

        # Run the 'update' command.
        with redirect_stdout(io.StringIO()) as stdout:
            apc = alpm_conf(['alpm-conf', 'update'] + args)

        # Check that the file is removed from master.
        output = stdout.getvalue()
        self.assertIn('Remove 3 files from the etc-tmp branch', output)
        self.assertIn('Remove 1 file from the master-tmp branch', output)
        relpaths = apc.repo.list_changed_files('master')
        self.assertEqual(relpaths, [relpath])

        # XXX sleep to allow examining the temporary directories.
        #import time; time.sleep(3600)
        #print(stdout.getvalue())

    def test_update_local_file(self):
        apc = self.create_repository()
        apc_dirs = self.apc_dirs

        # Add a new etc file to root_dir and the master branch, then modify
        # this file on root_dir and run the 'update' command.
        relpath = 'etc/foo'
        root_relpath = apc_dirs.root_dir / relpath
        repo_relpath = apc_dirs.gitrepo_dir / relpath
        with open(root_relpath, 'w') as f:
            f.write('line 1\n')

        apc.repo.checkout('master')
        (repo_relpath).parent.mkdir()
        shutil.copyfile(root_relpath, repo_relpath)
        apc.repo.git_cmd(['add', relpath])
        apc.repo.commit(f'Add user-file {relpath}')
        with open(root_relpath, 'a') as f:
            f.write('line 2\n')

        run_update(apc_dirs)
        run_merge(apc_dirs)

        # Check master branch.
        self.assertEqual(set(iter_etcfiles(apc_dirs.gitrepo_dir)), {relpath})
        self.assertEqual(sha256(repo_relpath), sha256(root_relpath))

    def test_update_nocherrypick(self):
        self.create_repository()
        apc_dirs = self.apc_dirs

        # Modify a file in root_dir and run the 'update' command.
        relpath = 'etc/pacman.conf'
        changed_line = 'first line\n'
        modify_line(apc_dirs.root_dir / relpath, 1, changed_line)
        apc = run_update(apc_dirs)
        self.assertEqual(apc.state, 'no-cherry-pick')

        run_merge(apc_dirs)

        # Install a new version of the pacman package including a change in
        # 'etc/pacman.conf' and run 'update'.
        count = [5,6,5,5]
        pkg = PACMAN_PKG._replace(version='8.0')
        self.install_new_package([pkg], [count], apc_dirs)
        apc = run_update(apc_dirs)

        # Check the 'master-tmp' branch.
        self.assertEqual(apc.repo.branches, ALPMCONF_BRANCHES)
        apc.repo.checkout('master-tmp')
        result_path = self.stack.enter_context(tempfile.NamedTemporaryFile())
        result_path = PosixPath(result_path.name)
        with open(result_path, 'w') as f:
            f.write(changed_line)
            for i in range(1, 6):
                f.write(f'line {i}\n')
        self.assertEqual(sha256(apc_dirs.gitrepo_dir / relpath),
                                                    sha256(result_path))

    def test_update_nocherrypick_2(self):
        # This test is the same as 'test_update_nocherrypick' except that
        # there is a second change in '/etc/pacman.conf' when a new version
        # of the pacman package is installed.
        self.create_repository()
        apc_dirs = self.apc_dirs

        # Modify a file in root_dir and run the 'update' command.
        relpath = 'etc/pacman.conf'
        changed_line = 'first line\n'
        modify_line(apc_dirs.root_dir / relpath, 1, changed_line)
        apc = run_update(apc_dirs)
        self.assertEqual(apc.state, 'no-cherry-pick')

        run_merge(apc_dirs)

        # Install a new version of the pacman package including a change in
        # 'etc/pacman.conf' and with a second change in this file in root_dir,
        # and run 'update'.
        count = [5,6,5,5]
        changed_line_2 = 'second line\n'
        pkg = PACMAN_PKG._replace(version='8.0')
        self.install_new_package([pkg], [count], apc_dirs)
        modify_line(apc_dirs.root_dir / relpath, 2, changed_line_2)
        apc = run_update(apc_dirs)

        # Check the 'master-tmp' branch.
        self.assertEqual(apc.repo.branches, ALPMCONF_BRANCHES)
        apc.repo.checkout('master-tmp')
        result_path = self.stack.enter_context(tempfile.NamedTemporaryFile())
        result_path = PosixPath(result_path.name)
        with open(result_path, 'w') as f:
            f.write(changed_line)
            f.write(changed_line_2)
            for i in range(2, 6):
                f.write(f'line {i}\n')
        self.assertEqual(sha256(apc_dirs.gitrepo_dir / relpath),
                                                    sha256(result_path))

    def test_update_symlink(self):
        self.create_repository()
        apc_dirs = self.apc_dirs

        # Modify 'relpath' in root_dir and run the 'update' command.
        relpath = 'etc/pacman.conf'
        changed_line = 'first line\n'
        modify_line(apc_dirs.root_dir / relpath, 1, changed_line)
        run_update(apc_dirs)
        apc =run_merge(apc_dirs)

        etc_path = apc_dirs.gitrepo_dir / relpath
        apc.repo.checkout('etc')
        sha = sha256(etc_path)

        # Change 'relpath' in root_dir to a symlink.
        abspath = apc_dirs.root_dir / relpath
        abspath.unlink()
        os.symlink(apc_dirs.root_dir, abspath)

        # Install a new version of the pacman package with a change in
        # 'etc/pacman.conf' and run 'update'.
        count = [5,6,5,5]
        pkg = PACMAN_PKG._replace(version='8.0')
        self.install_new_package([pkg], [count], apc_dirs)
        apc = run_update(apc_dirs)

        # Check that no cherry-picking has been done and that relpath remains
        # unchanged in the etc branch.
        self.assertEqual(apc.repo.branches, ALPMCONF_BRANCHES)
        apc.repo.checkout('etc')
        new_sha = sha256(etc_path)
        self.assertEqual(sha, new_sha)

    def test_update_empty_commit(self):
        relpath = 'etc/pacman.conf'

        for i in range(2):
            with self.subTest(i=i):
                apc = self.create_repository()
                apc_dirs = self.apc_dirs

                # Install a new version of the pacman package including a
                # change in 'etc/pacman.conf'. But without changing the file
                # in the 'etc' branch.
                # This is not possible in real life unless the packages or etc
                # branch has been tampered with.
                apc.repo.checkout('packages')
                pacman_path = apc_dirs.gitrepo_dir / 'pacman'
                package_dict = package_as_dict('pacman', pacman_path)
                package_dict['version'] = '8.0'
                package_dict['etc_files'][PosixPath('etc/pacman.conf')] = (
                                                            'dummy sha256')

                # Write the modified pacman file, commit the changes and run
                # update.
                with open(pacman_path, 'w') as f:
                    f.write(f"version = '{package_dict['version']}'\n")
                    f.write(f"etc_files = {package_dict['etc_files']}")
                apc.repo.git_cmd(f'add pacman')
                apc.repo.git_cmd('commit -m some_commit_msg')

                # Modify the pacman.conf file in root_dir to attempt a
                # cherry-pick instead.
                if i == 1:
                    modify_line(apc_dirs.root_dir / 'etc' / 'pacman.conf', 1,
                                                                'dummy line')

                # Run the update command.
                exception = self.get_ApcError_exception(run_update, apc_dirs)
                self.assertIn("Empty commit on the 'etc-tmp' branch",
                              str(exception))
                if i == 1:
                    self.assertIn('commit to be cherry-picked in master-tmp',
                                                            str(exception))
                else:
                    self.assertIn(
                        'Add or update 1 file in the etc-tmp branch',
                        str(exception))

    def test_pkg_as_dict_failure(self):
        apc = self.create_repository()

        # Install a bugged version of the pacman package.
        apc.repo.checkout('packages')
        pacman_path = self.apc_dirs.gitrepo_dir / 'pacman'
        with open(pacman_path, 'w') as f:
            f.write(f'1/0\n')
        apc.repo.git_cmd(f'add pacman')
        apc.repo.git_cmd('commit -m some_commit_msg')

        # Run the update command.
        exception = self.get_ApcError_exception(run_update, self.apc_dirs)
        self.assertIn('division by zero', str(exception))

    def test_invalid_state(self):
        pkg_count = [5,5,5,5]
        apc_dirs = self.create_alpm_conf_env([PACMAN_PKG], [pkg_count],
                                                                [pkg_count])
        args = args_from_emtdirs(apc_dirs)

        with redirect_stdout(io.StringIO()) as stdout:
            apc = alpm_conf(['alpm-conf', 'create'] + args)
        self.assertEqual(apc.state, 'start')

        exception = self.get_ApcError_exception(run_merge, apc_dirs)
        self.assertEqual(r"Cannot run 'merge' command in 'start' state",
                                                            str(exception))

    def test_update_failure(self):
        self.create_repository()

        # Modify a file in root_dir and run the 'update' command.
        relpath = 'etc/pacman.conf'
        with open(self.apc_dirs.root_dir / relpath, 'a') as f:
            f.write('line 5\n')

        kwds = self.apc_dirs._asdict()
        kwds['print_not_readable'] = False
        apc = AlpmConf(**kwds)
        apc.repo.open()

        with (mock.patch.object(apc, 'run_pacman_logic') as run_pacman_logic,
                    redirect_stdout(io.StringIO()) as stdout,
                    self.assertRaises(OSError)):
            run_pacman_logic.side_effect = OSError
            apc.cmd_update()

        # Check that the temporary branches have been removed.
        self.assertEqual(apc.state, 'start')

class MergeTests(AlpmConfTestCase):

    def test_merge(self):
        relpath = 'etc/pacman.conf'
        apc = self.set_ready_to_merge(relpath)
        apc_dirs = self.apc_dirs
        self.assertEqual(apc.state, 'cherry-pick')

        # Run the 'merge' command.
        # Use an AlpmConf instance here and don't run repo.open()
        # with os.geteuid() mock set to zero which would fail otherwise.
        # See also test_merge_not_root below.
        apc = AlpmConf(**apc_dirs._asdict())
        apc.repo.open()

        with (mock.patch('os.geteuid', return_value=0),
                redirect_stdout(io.StringIO()) as stdout):
            apc.cmd_merge()

        # Check the master branch and root_dir.
        self.assertEqual(apc.state, 'start')
        self.assertNotIn('master-tmp', apc.repo.branches)
        self.assertEqual(sha256(apc_dirs.gitrepo_dir / relpath),
                                    sha256(apc_dirs.root_dir / relpath))

    def test_merge_not_root(self):
        relpath = 'etc/pacman.conf'
        apc = self.set_ready_to_merge(relpath)
        apc_dirs = self.apc_dirs
        self.assertEqual(apc.state, 'cherry-pick')

        # Run the 'merge' command.
        exception = self.get_ApcError_exception(run_merge, apc_dirs)

        # Check the master branch.
        self.assertEqual(apc.state, 'cherry-pick')
        self.assertEqual('Must be root to copy 1 files to /etc',
                                                        str(exception))

    def test_merge_bad_ff(self):
        relpath = 'etc/pacman.conf'
        apc = self.set_ready_to_merge(relpath)
        apc_dirs = self.apc_dirs

        path = apc_dirs.gitrepo_dir / 'foo'
        with open(path, 'w') as f:
            pass
        gitrepo = apc.repo
        gitrepo.checkout('master')
        gitrepo.git_cmd(['add', path.name])
        gitrepo.commit(f'Add {path.name}')

        # The 'merge' command fails as the merge cannot be a fast-forward.
        exception = self.get_ApcError_exception(run_merge, apc_dirs)
        self.assertTrue(bool(re.search(
            r'commits .* added .* since .* last update', str(exception))))

    def test_merge_partial_tmp(self):
        apc = self.create_repository()
        self.assertEqual(apc.state, 'start')
        apc.repo.create_branch(f'etc-tmp')
        apc.repo.create_branch(f'packages-tmp')

        exception = self.get_ApcError_exception(run_merge, self.apc_dirs)
        self.assertTrue(bool(re.search(
            r"temporary branches are missing: {'master-tmp'}",
                                                        str(exception))))

    def test_merge_symlink(self):
        relpath = 'etc/pacman.conf'
        self.set_ready_to_merge(relpath)
        apc_dirs = self.apc_dirs

        # Change 'relpath' in root_dir as a symlink.
        abspath = apc_dirs.root_dir / relpath
        abspath.unlink()
        os.symlink(apc_dirs.root_dir, abspath)

        # Run the 'merge' command.
        merge_args = args_from_emtdirs(apc_dirs,
                                       fields=('gitrepo_dir', 'root_dir'))
        with redirect_stdout(io.StringIO()) as stdout:
            apc = alpm_conf(['alpm-conf', 'merge'] + merge_args)

        # Check the master branch and root_dir.
        self.assertNotIn('master-tmp', apc.repo.branches)
        output = stdout.getvalue()
        self.assertTrue(bool(re.search(
                        r'Copied 0 file from master-tmp branch', output)))
        self.assertTrue(bool(re.search(
                        r'warning: .* not synced, does not exist', output)))

class ConflictTests(AlpmConfTestCase):

    def test_update_conflict(self):
        self.setup_conflict()
        apc = run_update(self.apc_dirs, self.args)

        # Check the 'master-tmp' branch.
        self.assertEqual(apc.state, 'cherry-pick-conflict')
        self.assertEqual(apc.repo.branches, ALPMCONF_BRANCHES)
        self.assertTrue(apc.repo.current_branch, 'master-tmp')
        self.assertEqual(['UU etc/pacman.conf'], apc.repo.get_status())
        result = ('<<<<<<< HEAD\n'
                  'last line\n'
                  '=======\n'
                  'line 5\n'
                  '>>>>>>>')
        with open(self.apc_dirs.gitrepo_dir / self.relpath) as f:
            content = f.read()
        self.assertIn(result, content)

        # Try to run the 'update' command while there is a conflict.
        exception = self.get_ApcError_exception(run_update, self.apc_dirs,
                                                                    self.args)
        self.assertIn("Cannot run 'update' command in 'cherry-pick-conflict'",
                                                            str(exception))
        self.assertEqual(apc.state, 'cherry-pick-conflict')

        # Abort the cherry-pick and check the master and master-tmp branches.
        apc.repo.git_cmd('cherry-pick --abort')
        output = apc.repo.git_cmd('diff master...master-tmp')
        self.assertEqual(len(output), 0)
        self.assertEqual(apc.state, 'cherry-pick')

    def test_outside_repodir(self):
        self.setup_conflict()

        with redirect_stdout(io.StringIO()) as stdout:
            apc = alpm_conf(['alpm-conf', 'update'] + self.args)
        self.assertTrue(bool(re.search(
                    rf"change .* to the repository at '{apc.repo.dir_path}'",
                    stdout.getvalue())))

    def test_inside_repodir(self):
        def get_curdir():
            return curdir

        for i in range(2):
            with self.subTest(i=i):
                self.setup_conflict()
                curdir = (self.apc_dirs.gitrepo_dir if i else
                                self.apc_dirs.gitrepo_dir / 'some_subdir')

                with (redirect_stdout(io.StringIO()) as stdout,
                        mock.patch.object(PosixPath, 'cwd', get_curdir)):
                    apc = alpm_conf(['alpm-conf', 'update'] + self.args)
                self.assertFalse(bool(re.search(
                    rf"change .* to the repository at '{apc.repo.dir_path}'",
                    stdout.getvalue())))

    def test_abort_cherry_pick(self):
        self.setup_conflict()
        apc = run_update(self.apc_dirs, self.args)
        apc.repo.git_cmd('cherry-pick --abort')

        # Check that the merge command does not require to be run as root.
        merge_args = args_from_emtdirs(self.apc_dirs,
                                       fields=('gitrepo_dir', 'root_dir'))
        with redirect_stdout(io.StringIO()) as stdout:
            apc = alpm_conf(['alpm-conf', 'merge'] + merge_args)
        output = stdout.getvalue()
        self.assertNotIn('Must be root to copy', output)
        self.assertIn('Copied 0 file', output)

    def test_empty_cherry_pick(self):
        self.setup_conflict()
        apc = run_update(self.apc_dirs, self.args)

        # Revert to the version in the master branch.
        current = apc.root_dir / self.relpath
        master = apc.repo.dir_path / self.relpath
        shutil.copyfile(current, master)
        apc.repo.git_cmd(f'add {self.relpath}')
        apc.repo.git_cmd('commit --allow-empty -m some_commit_msg')

        # Check that the merge command does not require to be run as root.
        merge_args = args_from_emtdirs(self.apc_dirs,
                                       fields=('gitrepo_dir', 'root_dir'))
        with redirect_stdout(io.StringIO()) as stdout:
            apc = alpm_conf(['alpm-conf', 'merge'] + merge_args)
        output = stdout.getvalue()
        self.assertNotIn('Must be root to copy', output)
        self.assertIn('Copied 0 file', output)

    def test_cherry_pick_resolved(self):
        self.setup_conflict()
        apc = run_update(self.apc_dirs, self.args)

        # Don't bother fixing relpath.
        apc.repo.git_cmd(f'add {self.relpath}')
        apc.repo.git_cmd('commit -m some_commit_msg')

        # Check that the merge command must be run as root.
        exception = self.get_ApcError_exception(run_merge, self.apc_dirs)
        self.assertIn('Must be root to copy', str(exception))

class StateTransitionTests(AlpmConfTestCase):

    def test_transition_1(self):
        # State transition 1.
        self.create_repository()
        update_args = args_from_emtdirs(self.apc_dirs)

        with redirect_stdout(io.StringIO()) as stdout:
            apc = alpm_conf(['alpm-conf', 'update'] + update_args)
        self.assertIn('there is nothing to do', stdout.getvalue())
        self.assertEqual(apc.state, 'start')

    def test_transition_2_pkg(self):
        # State transition 2.
        # pacman.conf changed by the new package, but not changed by the
        # user.
        self.create_repository()

        # Install a new version of the pacman package including a change in
        # 'etc/pacman.conf' and run 'update'.
        count = [5,6,5,5]
        pkg = PACMAN_PKG._replace(version='8.0')
        self.install_new_package([pkg], [count], self.apc_dirs)
        apc = run_update(self.apc_dirs)
        self.assertEqual(apc.state, 'no-cherry-pick')

    def test_transition_2_user(self):
        # State transition 2.
        # New pacman package with unchanged etc files. pacman.conf changed by
        # user in the /etc directory.
        self.create_repository()

        # Install a new version of the pacman package.
        count = [5,5,5,5]
        pkg = PACMAN_PKG._replace(version='8.0')
        self.install_new_package([pkg], [count], self.apc_dirs)

        # Modify a file in root_dir.
        relpath = 'etc/pacman.conf'
        changed_line = 'first line\n'
        modify_line(self.apc_dirs.root_dir / relpath, 1, changed_line)

        apc = run_update(self.apc_dirs)
        self.assertEqual(apc.state, 'no-cherry-pick')

    def test_transition_2_added(self):
        # State transition 2.
        # A new file is added to /etc, added to the master branch and modified
        # in /etc.
        apc = self.create_repository()
        apc_dirs = self.apc_dirs

        # Create a new file in /etc and add it to the master branch.
        relpath = 'etc/foo.conf'
        root_relpath = apc_dirs.root_dir / relpath
        repo_relpath = apc_dirs.gitrepo_dir / relpath
        with open(root_relpath, 'w') as f:
            f.write('line 1\n')
        apc.repo.checkout('master')
        (repo_relpath).parent.mkdir()
        shutil.copyfile(root_relpath, repo_relpath)
        apc.repo.git_cmd(['add', relpath])
        apc.repo.commit(f'Add user-file {relpath}')

        # Modify the file.
        with open(root_relpath, 'a') as f:
            f.write('line 2\n')

        run_update(apc_dirs)
        self.assertEqual(apc.state, 'no-cherry-pick')

    def test_transition_3(self):
        relpath = 'etc/pacman.conf'
        apc = self.set_ready_to_merge(relpath)
        self.assertEqual(apc.state, 'cherry-pick')

    def test_transition_4(self):
        self.setup_conflict()
        apc = run_update(self.apc_dirs, self.args)
        self.assertEqual(apc.state, 'cherry-pick-conflict')

    def test_transition_5(self):
        self.setup_conflict()
        apc = run_update(self.apc_dirs, self.args)

        # Resolve the conflict. Don't bother fixing relpath.
        apc.repo.git_cmd(f'add {self.relpath}')
        apc.repo.git_cmd('commit -m some_commit_msg')

        self.assertEqual(apc.state, 'cherry-pick')

    def test_transition_6(self):
        self.setup_conflict()
        apc = run_update(self.apc_dirs, self.args)

        # Abort the cherry-pick and check the master and master-tmp branches.
        apc.repo.git_cmd('cherry-pick --abort')
        output = apc.repo.git_cmd('diff master...master-tmp')
        self.assertEqual(len(output), 0)
        self.assertEqual(apc.state, 'cherry-pick')

    def test_transition_7(self):
        self.setup_conflict()
        apc = run_update(self.apc_dirs, self.args)

        with redirect_stdout(io.StringIO()) as stdout:
            apc = alpm_conf(['alpm-conf', 'reset', '--gitrepo-dir',
                                            str(self.apc_dirs.gitrepo_dir)])
        self.assertEqual(apc.state, 'start')

    def test_transition_8(self):
        self.create_repository()

        # Install a new version of the pacman package including a change in
        # 'etc/pacman.conf' and run 'update'.
        count = [5,6,5,5]
        pkg = PACMAN_PKG._replace(version='8.0')
        self.install_new_package([pkg], [count], self.apc_dirs)
        apc = run_update(self.apc_dirs)
        self.assertEqual(apc.state, 'no-cherry-pick')

        run_merge(self.apc_dirs)
        self.assertEqual(apc.state, 'start')

    def test_transition_9(self):
        relpath = 'etc/pacman.conf'
        apc = self.set_ready_to_merge(relpath)
        self.assertEqual(apc.state, 'cherry-pick')

        with redirect_stdout(io.StringIO()) as stdout:
            apc = alpm_conf(['alpm-conf', 'reset', '--gitrepo-dir',
                                            str(self.apc_dirs.gitrepo_dir)])
        self.assertEqual(apc.state, 'start')

class DiffTests(AlpmConfTestCase):

    def set_ready_to_diff(self):
        pkg_count = [5,5,5,5]
        apc_dirs = self.create_alpm_conf_env([PACMAN_PKG], [pkg_count],
                                             [pkg_count], with_repo_dir=False)
        self.diff_args = args_from_emtdirs(apc_dirs,
                            fields=('database_dir', 'cache_dir', 'root_dir'))

        # Modify a file in root_dir.
        relpath = 'etc/pacman.conf'
        self.changed_line = 'first line\n'
        modify_line(apc_dirs.root_dir / relpath, 1, self.changed_line)

    def test_diff(self):
        self.set_ready_to_diff()
        with redirect_stdout(io.StringIO()) as stdout:
            alpm_conf(['alpm-conf', 'diff'] + self.diff_args)
        self.assertIn(f'-line 0\n+{self.changed_line}', stdout.getvalue())

    def test_diff_bad_tool(self):
        self.set_ready_to_diff()
        args = ['alpm-conf', 'diff', '--difftool=foo']
        args.extend(self.diff_args)
        with redirect_stdout(io.StringIO()) as stdout:
            exception = self.get_ApcError_exception(alpm_conf, args)
        self.assertIn('foo', str(exception))

    def test_diff_method(self):
        apc = AlpmConf(gitrepo_dir=True)
        with self.assertRaises(AssertionError) as cm:
            self.get_ApcError_exception(apc.cmd_diff)
        self.assertIn("'cmd_diff()' method is only used for its documentation",
                                                            str(cm.exception))

def main():
    # Run some tests with 'python -m alpm_conf.tests.test_alpm_conf'.
    test = AlpmConfTests()
    test.setUp()
    test.test_update_remove_file()

if __name__ == '__main__':
    main()
