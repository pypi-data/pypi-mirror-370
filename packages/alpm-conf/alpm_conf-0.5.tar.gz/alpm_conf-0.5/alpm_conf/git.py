"The git repository."

import os
import re
import stat
import shutil
import functools
import itertools
from pathlib import PosixPath

from . import ApcError, run_cmd

def get_logname():
    try:
        return os.getlogin()
    except OSError:
        return None

def repository_dir():
    xdg_data_home = os.environ.get('XDG_DATA_HOME')
    if xdg_data_home is not None:
        return PosixPath(xdg_data_home, 'alpm-conf')

    logname = get_logname()
    if logname is None:
        # Cannot fall back to getpass.getuser() or use the pwd database as
        # they do not provide the correct value when alpm-conf is run with
        # sudo.
        raise ApcError('alpm-conf requires a controlling terminal')
    return PosixPath(f'~{logname}/.local/share/alpm-conf').expanduser()

def git_version():
    proc = run_cmd(['git', '--version'])
    version = re.search(r'[\d\.]+', proc.stdout).group(0)
    return [int(part) for part in version.split('.')]

class GitRepo():
    """A git repository."""

    _ALPMCONF_BRANCHES = ['etc', 'etc-tmp', 'master', 'master-tmp',
                          'packages', 'packages-tmp']
    _FIRST_COMMIT_MSG = '__First alpm-conf commit__'

    GIT_VERSION = git_version()

    def __init__(self, gitrepo_dir):
        self.dir_path = gitrepo_dir if gitrepo_dir else repository_dir()
        self.current_branch = None
        self.initial_branch = None
        self.initialized = False

        self.root_not_repo_owner = False
        self.git_alias = self.setpriv()
        self.git_alias.extend(['git', '-C', self.dir_path,
                                    '-c', 'user.email="alpm-conf email"',
                                    '-c', 'user.name=alpm-conf',
                                    '-c', 'color.ui=false'])

    def setpriv(self):
        """Run git commands as the owner of the repository,

        when running as root and the git repository is not owned by root.

        setpriv is a simple, non-set-user-ID wrapper around execve(2),
        it allows commands to be run with a substitute user and group ID.
        """

        if os.geteuid() == 0:
            gitdir = self.dir_path / '.git'
            try:
                statinfo = gitdir.stat()
            except FileNotFoundError as e:
                # The repository has not been created yet.
                return []

            if statinfo.st_uid != 0:
                self.root_not_repo_owner = True

                if shutil.which('setpriv') is None:
                    raise ApcError("The 'util-linux' ArchLinux package"
                                   " is missing")
                cmd = ['setpriv', f'--reuid={statinfo.st_uid}',
                       '--clear-groups', f'--regid={statinfo.st_gid}']
                return cmd

        return []

    def create(self):
        """Create the git repository."""

        if self.dir_path.is_dir():
            if list(self.dir_path.iterdir()):
                raise ApcError(f"'{self.dir_path}' repository is not empty")
        else:
            self.dir_path.mkdir(parents=True)
        self.git_cmd('init')

        # First empty commit used to identify the alpm-conf repository.
        self.git_cmd(['commit', '--allow-empty', '-m', self._FIRST_COMMIT_MSG])

        # Create the etc and packages branches.
        self.create_branch('etc')
        self.create_branch('packages')

        self.checkout('master')
        self.initial_branch = self.current_branch = 'master'
        self.initialized = True

    def open(self):
        # Check the first commit message.
        output = self.git_cmd('rev-list --max-parents=0 --format=%s master',
                              msg=f'no git repository at {self.dir_path}')
        commit, first_commit_msg = output.splitlines()
        commit_msg = self._FIRST_COMMIT_MSG
        if first_commit_msg != commit_msg:
            err_msg = (f"this is not an alpm-conf repository\n"
                    f"First commit message found: '{first_commit_msg}'\n"
                    f"instead of the expected commit message: '{commit_msg}'")
            raise ApcError(err_msg)

        # Get the initial branch.
        output = self.git_cmd(['symbolic-ref', '--short', 'HEAD'])
        self.initial_branch = output
        self.current_branch = self.initial_branch
        self.initialized = True

    def close(self):
        if self.initialized:
            branch = 'master'
            if self.initial_branch in self.branches:
                branch = self.initial_branch
            self.checkout(branch)

    def git_cmd(self, cmd, msg=None):
        if type(cmd) == str:
            cmd = cmd.split()
        proc = run_cmd(self.git_alias + cmd, msg)
        output = proc.stdout.rstrip()
        return output

    def get_status(self):
        output = self.git_cmd('status --porcelain')
        return output.splitlines()

    def checkout(self, branch):
        if branch == self.current_branch:
            return
        self.git_cmd(f'checkout {branch}')
        self.current_branch = branch

    def create_branch(self, branch_name, start_point=''):
        self.git_cmd(f'branch {branch_name} {start_point}')

    def commit(self, commit_msg):
        self.git_cmd(['commit', '-m', commit_msg])

    def add_and_commit(self, relpaths, commit_msg):
        """Add files and commit, ignoring an empty commit.

        As git reports an error  when attempting to commit with no files
        staged in this index.
        """

        if relpaths:
            self.git_cmd(['add'] + relpaths)
            staged_list = self.git_cmd('diff --name-only --staged')
            if staged_list:
                self.git_cmd(['commit', '-m', commit_msg])
            else:
                return (
                    f"Empty commit on the '{self.current_branch}' branch.\n"
                    f'   Commit message:\n'
                    f'      "{commit_msg}"\n'
                    f'   Files list:\n'
                    f'       {relpaths}\n')
        return True

    def commit_files_with_content(self, files, commit_msg):
        """Add and commit a list of files.

        'files' is a dictionary mapping filename to the file content that must
        be written before the commit.
        """

        relpaths = []
        for relpath in files:
            path = self.dir_path / relpath
            relpaths.append(relpath)
            with open(path, 'w') as f:
                f.write(files[relpath])

        self.add_and_commit(relpaths, commit_msg)

    def cherry_pick(self, sha):
        # If a commit being cherry picked duplicates a commit already in the
        # current history, it  will become empty. By default these redundant
        # commits cause cherry-pick to stop so the user can examine the
        # commit. This option overrides that behavior and creates an empty
        # commit object.
        if self.GIT_VERSION >= [2, 45 ,0]:
            empty_option = '--empty=keep'
        else:
            empty_option = '--keep-redundant-commits'
        self.git_cmd(['cherry-pick', '-x', empty_option, sha])

    def tracked_files(self, branch):
        """The tracked files in this branch."""

        relpaths = set()
        ls_tree = self.git_cmd(f'ls-tree -r --name-only --full-tree {branch}')
        for relpath in ls_tree.splitlines():
            relpaths.add(relpath)
        return relpaths

    def check_fast_forward(self, parent, descendant):
        """A fast-forward merge is allowed."""

        # This is  equivalent to 'git rev-list parent ^descendant'.
        output = self.git_cmd(f'rev-list {descendant}..{parent}')
        if output.strip():
            raise ApcError(f'commits have been added to the {parent} branch'
                           f' since the last update command, please run again'
                           f' the update command')

    def list_changed_files(self, revision):
        """List changed files at a git revision."""

        list_relpath = (f'diff-tree --no-commit-id --name-only -r {revision}')
        diff_tree = self.git_cmd(list_relpath)
        return diff_tree.splitlines()

    @functools.cache
    def commit_list(self, parent, descendant):
        """List the commits in 'descendant' and not in 'parent'.

        Return the list of tuples made of (sha, commit message) in
        chronological order.
        """

        rev_list = self.git_cmd(f'rev-list --no-commit-header'
                                f' --format=%H%n%s {parent}..{descendant}')
        return list(reversed(
                    list(itertools.batched(rev_list.splitlines(), n=2))))

    @property
    def branches(self):
        branches = self.git_cmd("for-each-ref --format=%(refname:short)")
        return set(b for b in branches.splitlines() if b in
                                                    self._ALPMCONF_BRANCHES)
