"""The gits tests."""

import sys
import os
import io
import tempfile
from pathlib import PosixPath
from unittest import mock, skipIf
from contextlib import redirect_stdout, ExitStack

from .. import ApcError
from ..alpm_conf import AlpmConf
from ..git import GitRepo
from . import CustomTestCase

class GitTests(CustomTestCase):

    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)

        # Create a fake git repository.
        repo_dir = self.stack.enter_context(
                            tempfile.TemporaryDirectory(prefix='tmp-repo-'))
        self.repo_dir = PosixPath(repo_dir)

    @skipIf(os.geteuid() == 0, "must not be root")
    def test_setpriv(self):

        # Get the git module
        from ..git import __name__
        git_module = sys.modules[__name__]

        (self.repo_dir / '.git').mkdir()
        with (mock.patch('os.geteuid', return_value=0),
                    mock.patch.object(git_module, 'run_cmd', return_value=0)):
            gitrepo = GitRepo(self.repo_dir)

        self.assertTrue(' '.join(str(x) for x in gitrepo.git_alias).startswith(
                                                        'setpriv --reuid='))

    @skipIf(os.geteuid() == 0, "must not be root")
    def test_setpriv_no_repo(self):

        # Get the git module
        from ..git import __name__
        git_module = sys.modules[__name__]

        with (mock.patch('os.geteuid', return_value=0),
                    mock.patch.object(git_module, 'run_cmd', return_value=0)):
            gitrepo = GitRepo(self.repo_dir)

        self.assertTrue(' '.join(str(x) for x in gitrepo.git_alias).startswith(
                                    f'git -C {self.repo_dir} -c user.email='))

        # XXX
        #import time
        #time.sleep(3600)
        #print(stdout.getvalue())

    def test_create(self):
        repo_dir = self.repo_dir / 'foo'
        gitrepo = GitRepo(repo_dir)
        gitrepo.create()
        self.assertTrue((repo_dir / '.git').is_dir())

    def test_create_not_empty(self):
        with open(self.repo_dir / 'foo', 'w'):
            pass

        gitrepo = GitRepo(self.repo_dir)
        with self.assertRaises(ApcError) as cm:
              gitrepo.create()

        self.assertIn('repository is not empty', str(cm.exception))

    def test_bad_repository(self):
        path = self.repo_dir / 'foo'
        with open(path, 'w') as f:
            pass

        gitrepo = GitRepo(self.repo_dir)
        gitrepo.git_cmd('init')
        gitrepo.git_cmd(['add', path.name])
        gitrepo.commit(f'Add {path.name}')

        with self.assertRaises(ApcError) as cm:
            gitrepo.open()

        self.assertIn('not an alpm-conf repository', str(cm.exception))

    def test_root_not_repo_owner(self):
        # Create a fake git repository.
        repo_dir = self.stack.enter_context(
                            tempfile.TemporaryDirectory(prefix='tmp-repo-'))
        repo_dir = PosixPath(repo_dir)

        apc = AlpmConf(**{'gitrepo_dir': repo_dir})
        apc.repo.root_not_repo_owner = True
        with self.assertRaises(ApcError) as cm:
            try:
                apc.run_cmd('cmd_create')
            except SystemExit as e:
                raise e.__context__

        self.assertIn('cannot be executed as root', str(cm.exception))

def main():
    # Run some tests with 'python -m alpm_conf.tests.test_git'.
    test = GitTests()
    test.setUp()
    test.test_setpriv_no_repo()

if __name__ == '__main__':
    main()
