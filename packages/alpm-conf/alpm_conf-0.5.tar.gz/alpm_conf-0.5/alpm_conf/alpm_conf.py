"""The 'alpm-conf' command."""

import sys
import os
import hashlib
import argparse
import inspect
import shutil
import traceback
import tempfile
import io
from contextlib import redirect_stdout
from pathlib import PosixPath
from textwrap import dedent
from collections import namedtuple
from enum import Flag

from . import __version__, __doc__, ApcError, warn
from .git import GitRepo
from .packages import PacmanDataBase, get_pacman_dirs

TMP_BRANCHES = {'master-tmp', 'etc-tmp', 'packages-tmp'}

def sha256(abspath):

    try:
        if abspath.is_symlink():
            return None

        hash = hashlib.sha256()
        with abspath.open('rb') as f:
            hash.update(f.read())
        return hash.hexdigest()
    except OSError:
        pass

    return None

# The return value of AlpmConf.run_pacman_logic().
CherryPick = namedtuple('CherryPick',
                            ['cherrypick_set', 'cherrypick_commit_sha'],
                            defaults=(set(), None))

class State(Flag):
    START = 1
    NO_CHERRY_PICK = 2
    CHERRY_PICK = 4
    CHERRY_PICK_CONFLICT = 8
    TMP_BRANCHES_CREATED = 14

ALLOWED_STATES = {
    'update': ['start'],
    'merge': ['no-cherry-pick', 'cherry-pick'],
}
for cmd in ('state', 'reset', 'clean'):
    # Empty list means all states are allowed.
    ALLOWED_STATES[cmd] = []

class AlpmConf():
    """Provide methods to implement the alpm-conf commands."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.repo = GitRepo(self.gitrepo_dir)
        self.closed = False

    def parse_status(self, status, closing=False):
        dir_path = self.repo.dir_path
        tracked = untracked = False
        for line in status:
            if line[:2] == '??':
                untracked = True
            else:
                tracked = True
        msg = f'The {dir_path} repository is not clean:\n'
        msg += '\n'.join(f'  {line}' for line in status)

        if closing and (dir_path / '.git' / 'CHERRY_PICK_HEAD').exists():
            return msg

        msg += '\n'
        if tracked:
            msg += ("Run 'alpm-conf reset' to discard any change in the"
            " working tree and in the index.")
        if untracked:
            msg += ("Run 'alpm-conf clean' to clean the working tree by"
                    " recursively removing files not under version control.")
        return msg

    def open(self, cmd):
        assert cmd != 'create'
        self.repo.open()

        allowed = ALLOWED_STATES[cmd]
        state = self.state
        if allowed and state not in allowed:
            raise ApcError(f"Cannot run '{cmd}' command in '{state}' state")

        status = self.repo.get_status()
        dir_path = self.repo.dir_path
        if (status and
                cmd in ('update', 'merge') and
                not (dir_path / '.git' / 'CHERRY_PICK_HEAD').exists()):
            msg = self.parse_status(status)
            raise ApcError(msg)

    def close(self):
        self.closed = True

        # Do not close the repo (that is, do not check out the initial
        # branch) when the repo is not clean.
        if self.repo.initialized:
            status = self.repo.get_status()
            if status:
                print('Closing the repository:')
                print(self.parse_status(status, closing=True))
            else:
                self.repo.close()

    def run_cmd(self, command):
        """Run the alpm-conf command."""

        # Cannot run two commands with the same AlpmConf instance.
        assert self.closed == False

        assert command.startswith('cmd_')

        # The merge subcommand is the only command that can be run as root
        # except when the repository has been created by root.
        if self.repo.root_not_repo_owner and command != 'cmd_merge':
            raise ApcError('cannot be executed as root')

        method = getattr(self, command)
        try:
            if command != 'cmd_create':
                self.open(command[4:])
            method()
        finally:
            self.close()

    def cmd_create(self):
        """Create the git repository and populate the etc and master branches.

        The git repository is located at the directory specified by the
        command line option '--gitrepo-dir' when this option is set, otherwise
        at $XDG_DATA_HOME/alpm-conf if the XDG_DATA_HOME environment variable
        is set, otherwise at $HOME/.local/share/alpm-conf.
        """

        self.repo.create()
        self.update_repository('create')
        print(f'Git repository created at {self.repo.dir_path}.')

    def cmd_update(self):
        """Update the repository with packages and user changes.

        The changes are made in the 'packages-tmp', 'etc-tmp' and
        'master-tmp' temporary branches.
        """

        self.update_repository('update')

    def cmd_merge(self):
        """Incorporate changes made by the previous 'update' command into /etc.

        Copy to the /etc directory the files of the 'master-tmp' branch that
        are listed in the cherry-pick commit and for each one of the
        'packages', 'etc' and 'master' branches:
          - Create a tag named '<branch>-prev' at '<branch>' before the merge.
          - Incorporate changes from '<branch>-tmp' into '<branch>' with a
            fast-forward merge.
          - Remove '<branch>-tmp'.
        """

        # Check there are no user commits since last 'update' command.
        for tmp_branch in TMP_BRANCHES:
            self.repo.check_fast_forward(tmp_branch[:-4], tmp_branch)

        if self.has_cherry_pick():
            # Get the list of files updated by a cherry-pick.
            relpaths = self.files_to_sync()

            # Copy the files to /etc.
            if relpaths:
                assert self.repo.current_branch == 'master-tmp'

                if os.geteuid() != 0:
                    raise ApcError(
                        f'Must be root to copy {len(relpaths)} files to /etc')

                for relpath in list(relpaths):
                    current = self.root_dir / relpath
                    master = self.repo.dir_path / relpath
                    try:
                        shutil.copyfile(master, current, follow_symlinks=False)
                    except OSError as e:
                        relpaths.remove(relpath)
                        warn(f'{current} not synced, cannot copy to /etc: {e}')
                        continue

            length = len(relpaths)
            plural = 's' if length > 1 else ''
            print(f"Copied {length} file{plural} from master-tmp branch to"
                  f" '{self.root_dir}'.")
            for relpath in relpaths:
                print(f'  {relpath}')

        self.print_commits(suffix='-tmp')
        self.merge_fastforward()
        self.remove_tmp_branches()
        print(
            f"'merge' command terminated - the new state is '{self.state}'.")

    def cmd_diff(self):
        """Print changes made in pacman installed etc files.

        An alpm-conf  repository is created in a temporary directory removed
        upon completion of the command. A 'git diff' command prints the
        differences between the etc files of the package archives currently
        installed by pacman and the corresponding files modified in the /etc
        directory.

        Using the '-–difftool' option allows using an editor for browsing the
        changes instead of printing the diffs.
        """

        assert False, "'cmd_diff()' method is only used for its documentation"

    def cmd_state(self):
        """Print the current state."""

        print(f"Current state: '{self.state}'\n")

    def cmd_clean(self):
        """Clean the working tree.

        Remove recursively files not under version control.
        """

        output = self.repo.git_cmd('clean -d -f')
        if output:
            print(output)

    def cmd_reset(self):
        """Clean the working tree, the index and change the state to start.

        . remove recursively files not under version control
        . reset the index and working tree by running the 'git reset --hard'
          command
        . remove the temporary branches
        """

        self.cmd_clean()
        self.repo.git_cmd('reset --hard')
        self.remove_tmp_branches()
        print(
            f"'reset' command terminated - the new state is '{self.state}'.")

    def has_cherry_pick(self):
        tags = self.repo.git_cmd('tag')
        if 'cherry-pick' in tags.splitlines():
            cherry_pick_sha = self.repo.git_cmd('rev-parse  cherry-pick')

            # Check that the 'cherry-pick' tag is within the 'etc-tmp' branch.
            rev_list = self.repo.git_cmd('rev-list etc..etc-tmp')
            if cherry_pick_sha in rev_list.splitlines():
                return True
        return False

    def files_to_sync(self):
        """Build the list of files to be synced to /etc."""

        relpaths = self.repo.git_cmd(
                        'diff-tree -r --name-only --no-commit-id cherry-pick')
        relpaths = relpaths.splitlines()

        if relpaths:
            self.repo.checkout('master-tmp')

            for relpath in list(relpaths):
                current = self.root_dir / relpath
                if not current.is_file() or current.is_symlink():
                    relpaths.remove(relpath)
                    warn(f'{current} not synced, does not exist or a symlink')
                    continue

                master = self.repo.dir_path / relpath
                # Skip it when the /etc file had been copied to the
                # 'master-tmp' branch by a previous commit.
                cur_sha = sha256(current)
                master_sha = sha256(master)
                assert master_sha is not None
                if cur_sha == master_sha:
                    relpaths.remove(relpath)
                    continue

        return relpaths

    def create_tmp_branches(self):

        print('Creating the temporary branches.')

        for tmp_branch in TMP_BRANCHES:
            branch = tmp_branch[:-4]
            self.repo.create_branch(tmp_branch, branch)

    def remove_tmp_branches(self):

        branches = self.repo.branches
        if TMP_BRANCHES.intersection(branches):
            print('Removing the temporary branches.')
            for tmp_branch in TMP_BRANCHES:
                branch = tmp_branch[:-4]
                if tmp_branch in branches:
                    if self.repo.current_branch == tmp_branch:
                        self.repo.checkout(branch)
                    self.repo.git_cmd(f'branch --delete --force {tmp_branch}')

    def merge_fastforward(self):

        for tmp_branch in TMP_BRANCHES:
            branch = tmp_branch[:-4]
            if not self.repo.commit_list(branch, tmp_branch):
                continue

            # Tag the branch as '<branch>-prev' before the merge.
            self.repo.git_cmd(f'tag -f {branch}-prev {branch}')

            # Use 'git fetch' to do a fast-forward merge without having to
            # checkout 'branch'.
            if self.repo.current_branch == branch:
                self.repo.checkout(tmp_branch)
            print(f"Merging changes from the {tmp_branch} branch"
                  f" into {branch}.")
            # The format of the fetch command is:
            #     git fetch <remote> <remoteBranch>:<localBranch>
            # See the "<refspec>" section of the fetch command man page.
            # Here '.' means the local repository as the <remote>.
            self.repo.git_cmd(f'fetch . {tmp_branch}:{branch}')

    @property
    def state(self):
        """alpm-conf state."""

        common = TMP_BRANCHES.intersection(self.repo.branches)
        if common == TMP_BRANCHES:
            # State.TMP_BRANCHES_CREATED.
            if self.has_cherry_pick():
                if (self.repo.dir_path / '.git' / 'CHERRY_PICK_HEAD').exists():
                    state = State.CHERRY_PICK_CONFLICT
                else:
                    state = State.CHERRY_PICK
            else:
                state = State.NO_CHERRY_PICK
        else:
            missing = TMP_BRANCHES.difference(common)
            if missing != TMP_BRANCHES:
                raise ApcError(
                    f'Some temporary branches are missing: {missing}\n'
                    f"Run 'alpm-conf reset' to remove all temporary branches")
            else:
                state = State.START

        return state.name.lower().replace('_', '-')

    def init_pacman_db(self):
        # Initialize access to the pacman database.
        pacman_conf = {
            'root_dir':     self.root_dir,
            'db_path':      self.database_dir,
            'cache_dir':    self.cache_dir,
        }
        self.pacman_db = PacmanDataBase(pacman_conf, self.repo)
        self.pacman_db.init()

    def print_commits(self, suffix=''):

        indent = ' ' * 4

        for branch in ('packages', 'etc', 'master'):
            tmp_branch = branch + '-tmp'
            commit_list = self.repo.commit_list(branch, tmp_branch)
            if not commit_list:
                continue

            # Print the commits in chronological order.
            print(f'Commits in the {branch}{suffix} branch.')
            for sha, subject in commit_list:
                print(f'  {subject}')

                relpaths = self.repo.list_changed_files(sha)
                if branch == 'etc' and len(relpaths) > 10:
                    list_relpath = (f'diff-tree --no-commit-id --name-only -r'
                                f' {sha}')
                    print(f"{indent}git command to list the files:")
                    print(f"{indent}  'git {list_relpath}'")
                else:
                    lines = (sorted(relpaths) if relpaths else
                                                            ['empty commit'])
                    print('\n'.join((indent + l) for l in lines))

                print()

    def copy_to_repo(self, abspath, relpath):
        """Copy a file to the repository.

        'relpath' type is PosixPath or str.
        """

        repo_path = self.repo.dir_path / relpath
        dirname = repo_path.parent
        if dirname and not dirname.is_dir():
            dirname.mkdir(parents=True)

        shutil.copy(abspath, repo_path, follow_symlinks=False)

    def commit_etc_files(self, relpaths, files_type):
        """Commit a list of files from /etc that have been modified."""

        if not relpaths:
            return

        self.repo.checkout('master-tmp')

        relpath_list = []
        for relpath in relpaths:
            sha = sha256(self.repo.dir_path / relpath)
            current = self.root_dir / relpath
            cur_sha = sha256(current)
            if cur_sha is not None and sha != cur_sha:
                self.copy_to_repo(current, relpath)
                relpath_list.append(relpath)

        if relpath_list:
            length = len(relpath_list)
            plural = 's' if length > 1 else ''
            self.repo.git_cmd(['add'] + relpath_list)
            self.repo.commit(f'Add or update {length} {files_type}{plural}'
                             f' from /etc to the master-tmp branch')

    def update_packages_branch(self):
        """Update the 'packages-tmp' branch

        with the changes in the pacman database since the last 'merge' command.
        """

        # To be consistent with the naming in packages.py, in the following
        # code 'pkg' is an instance of pyalpm.Package and 'package' is an
        # instance of packages.Package.

        self.repo.checkout('packages-tmp')

        # Remove from the packages branch the packages that are not installed
        # any more.
        packages_tracked = self.repo.tracked_files('packages-tmp')
        installed_packages = [pkg.name for pkg in
                                    self.pacman_db.installed_packages]
        removed = packages_tracked.difference(installed_packages)
        if removed:
            length = len(removed)
            plural = 's' if length > 1 else ''
            self.repo.git_cmd(['rm'] + list(removed))
            self.repo.commit(f'Remove {length} package{plural}'
                             f' from the packages-tmp branch')

        # Add to the packages branch the new packages that have etc files.
        new_packages = self.pacman_db.list_new_packages(self.repo.dir_path,
                                    print_not_readable=self.print_not_readable)
        if new_packages:
            files = {}
            for package in new_packages:
                files[package.name] = str(package)
            length = len(new_packages)
            plural = 's' if length > 1 else ''
            self.repo.commit_files_with_content(files,
                                f'Add or update {length}'
                                f' package{plural} to the packages branch')

    def remove_etc_files(self):

        # Remove from the etc branch the etc files that are not in the
        # installed packages.
        etc_tracked = self.repo.tracked_files('etc-tmp')
        etc_files = self.pacman_db.installed_files
        removed = etc_tracked.difference(etc_files)
        if removed:
            self.repo.checkout('etc-tmp')

            length = len(removed)
            plural = 's' if length > 1 else ''
            self.repo.git_cmd(['rm'] + list(removed))
            self.repo.commit(f'Remove {length} file{plural}'
                             f' from the etc-tmp branch')

        return removed

    def remove_master_files(self, removed_files):

        if not removed_files:
            return

        # Remove from the master branch the files that have been removed
        # from the etc branch.
        master_tracked = self.repo.tracked_files('master-tmp')
        removed = master_tracked.intersection(removed_files)
        if removed:
            self.repo.checkout('master-tmp')

            length = len(removed)
            plural = 's' if length > 1 else ''
            self.repo.git_cmd(['rm'] + list(removed))
            self.repo.commit(f'Remove {length} file{plural}'
                             f' from the master-tmp branch')

    def run_pacman_logic(self):
        """Implement pacman 'HANDLING CONFIG FILES' (see pacman man page).

        The pacman terminology:
            original        file in the etc-tmp branch
            current         file in /etc
            new             file in the pacman archive

        State before pacman upgrade              State after logic applied

        case 1:  original=X  current=X  new=X    no change
        case 2:  original=X  current=X  new=Y    current=Y
        case 3:  original=X  current=Y  new=X    no change
        case 4:  original=X  current=Y  new=Y    no change
        case 5:  original=X  current=Y  new=Z    need merging
        case 6:  original=0  current=Y  new=Z      idem

        State upon entering this method after pacman upgrade:

        case 1:  original=X  current=X  new=X
        case 2:  original=X  current=Y  new=Y    becomes same as case 4
        case 3:  original=X  current=Y  new=X
        case 4:  original=X  current=Y  new=Y
        case 5:  original=X  current=Y  new=Z    need merging
        case 6:  original=0  current=Y  new=Z      idem

        Pseudo code handling the changes:

            if new != original:
                # Cases 5, 6.
                if current != new and current != original:
                  git add 'new' to 'cherrypick_set'

                # Cases 2, 4.
                else:
                    git add 'new' to 'etc_list'

        """

        self.repo.checkout('etc-tmp')

        # Copy to the etc branch the installed etc files (that are new or
        # different from the original etc files).
        self.pacman_db.extract_files(self.repo.dir_path)

        if not len(self.pacman_db.new_files):
            return CherryPick()

        # By construction, 'new_files' and 'original_files' have the same keys
        # and their corresponding sha256 are different.
        etc_list = []
        cherrypick_set = set()
        etc_tracked = self.repo.tracked_files('etc-tmp')
        has_warnings = False
        for path, new_sha in self.pacman_db.new_files.items():

            relpath = str(path)
            original_sha = self.pacman_db.original_files[path]

            current = self.root_dir / path
            cur_sha = sha256(current)

            # Ignore a file on the etc branch that, in /etc, does not exist or
            # is not readable or is a symlink.
            if (not current.is_file() or current.is_symlink() or not
                        os.access(current, os.R_OK)):
                warn(f"Ignore '{relpath}' (missing or symlink or"
                     f" not readable in /etc)")
                has_warnings = True
                if relpath in etc_tracked:
                    self.repo.git_cmd(['checkout', relpath])
                else:
                    (self.repo.dir_path / relpath).unlink()
                continue

            # Cases 5, 6.
            # - 'new_sha' is never None.
            # - 'original_sha' may be None if the file did not exist.
            if cur_sha not in (new_sha, original_sha):
                # No previous install, add the /etc file to the master branch.
                if original_sha is None:
                    etc_list.append(relpath)
                else:
                    cherrypick_set.add(relpath)

            # Cases 2, 4.
            else:
                etc_list.append(relpath)

        cherrypick_commit_sha = None
        if cherrypick_set:
            length = len(cherrypick_set)
            plural = 's' if length > 1 else ''
            result = self.repo.add_and_commit(list(cherrypick_set),
                                f'Update {length} file{plural} - commit'
                                f' to be cherry-picked in master-tmp')
            if result is not True:
                raise ApcError(result)

            # Get the commit sha of the previous commit.
            cherrypick_commit_sha = self.repo.git_cmd('rev-list -1 HEAD')

            # Tag the cherry-pick commit (to be used by cmd_merge()).
            self.repo.git_cmd('tag -f cherry-pick HEAD')

        if etc_list:
            length = len(etc_list)
            plural = 's' if length > 1 else ''
            result = self.repo.add_and_commit(etc_list,
                                f'Add or update {length} file{plural} in the'
                                f' etc-tmp branch')
            if result is not True:
                raise ApcError(result)

        if has_warnings:
            print()
        return CherryPick(cherrypick_set, cherrypick_commit_sha)

    def update_user_changes(self):
        """Update the 'master-tmp' branch with changes to user-files."""

        # Update the repository with changes made to files in /etc that are
        # not installed by pacman (i. e. they are tracked by the 'master-tmp'
        # branch but not by the 'etc-tmp' branch).

        master_tracked = self.repo.tracked_files('master-tmp')
        etc_tracked = self.repo.tracked_files('etc-tmp')
        relpaths = master_tracked.difference(etc_tracked)

        self.commit_etc_files(relpaths, 'user-file')

    def update_etc_changes(self):
        """Update the 'master-tmp' branch with changes to packaged-files."""

        self.repo.checkout('etc-tmp')

        # Get the list of files in the 'etc-tmp' branch that are different
        # from files in /etc.
        etc_tracked = self.repo.tracked_files('etc-tmp')
        etc_files = set()
        for relpath in etc_tracked:
            sha = sha256(self.repo.dir_path / relpath)
            current = self.root_dir / relpath
            cur_sha = sha256(current)
            if cur_sha is not None and sha != cur_sha:
                etc_files.add((relpath, current, cur_sha))

        # Get the list of files that need to be copied to the 'master-tmp'
        # branch.
        relpaths = []
        if etc_files:
            self.repo.checkout('master-tmp')

            for relpath, current, cur_sha in etc_files:
                sha = sha256(self.repo.dir_path / relpath)
                if sha != cur_sha:
                    self.copy_to_repo(current, relpath)
                    relpaths.append(relpath)

        if relpaths:
            length = len(relpaths)
            plural = 's' if length > 1 else ''
            self.repo.git_cmd(['add'] + relpaths)
            self.repo.commit(f"Update {length} packaged file{plural}"
                f" changed by the root user or by a package's scriptlet")

    def print_conflicts(self):

        self.print_commits(suffix='-tmp')

        # See 'git help status'.
        conflicts = [line for line in self.repo.get_status()
                     if 'U' in line[:2] or line[:2] in ('AA', 'DD')]
        plural = 's' if len(conflicts) > 1 else ''
        print(f'The cherry-picking has conflict{plural}.')

        output = self.repo.git_cmd('status')
        print("This is the output of the 'git status' command:")
        print('\n'.join(f'>  {line}' for line in output.splitlines()))
        print('List of files with a conflict to resolve:')
        print('\n'.join(f'  {c}' for c in sorted(conflicts)))
        print()

        print(f'Please resolve the conflict{plural}.')

        # In order to resolve the conflict the current working
        # directory must be within the repository.
        curdir = PosixPath.cwd()
        repo_dir = self.repo.dir_path
        if curdir != repo_dir:
            for parent in curdir.parents:
                if parent == repo_dir:
                    break
            else:
                print(
                    f"To run the git command you must change the current"
                    f" working directory to the repository at '{repo_dir}'"
                    f" where the master-tmp banch is checked out.\n")

        print("Running the 'git cherry-pick --abort' command"
              " causes the alpmconf state to change from"
              " 'cherry-pick-conflict' to 'cherry-pick' with an empty"
              " cherry-pick (i.e. ignore latest changes made by pacman"
              " upgrade)."
              " To cancel the 'update' command run the 'alpmconf reset'"
              " command instead.\n")

    def cherry_pick(self, cherrypick):

        self.repo.checkout('master-tmp')

        try:
            # Merge the changes to the master-tmp branch using the
            # cherrypick commit sha.
            self.repo.cherry_pick(cherrypick.cherrypick_commit_sha)
        except ApcError as e:
            if (self.repo.dir_path / '.git' / 'CHERRY_PICK_HEAD').exists():
                self.print_conflicts()
                return False
            else:
                raise ApcError(stdout) from e
        return True

    def _update_repository(self, cmd):
        """Update the repository from packages updates and user updates."""

        self.init_pacman_db()
        self.create_tmp_branches()

        #   --- In the packages-tmp branch ---
        # Update the repository with the pacman database changes.
        self.update_packages_branch()


        #   --- In the etc-tmp branch ---
        removed_files = self.remove_etc_files()

        # 'cherrypick' is an instance of the CherryPick namedtuple.
        cherrypick = self.run_pacman_logic()


        #   --- In the master-tmp branch ---
        # Remove files removed from the etc branch.
        self.remove_master_files(removed_files)

        # Update the master branch with /etc files changes.
        self.update_etc_changes()

        # Update the master branch with user-files changes.
        self.update_user_changes()

        newline = ''
        if cmd == 'create':
            self.print_commits()
            self.merge_fastforward()
            self.remove_tmp_branches()

        elif not cherrypick.cherrypick_set or self.cherry_pick(cherrypick):
            self.print_commits(suffix='-tmp')

            if not any(self.repo.commit_list(branch, branch + '-tmp')
                                for branch in ('packages', 'etc', 'master')):
                print('No commit in any of the temporary branches,'
                      ' there is nothing to do.')
                self.remove_tmp_branches()
            else:
                print("Use the 'merge' command to merge the changes from the"
                      " '-tmp' branches to the master, etc and packages branches"
                      " and copy the changes to /etc if any.")
        else:
            newline = '\n'

        print(f"'{cmd}' command terminated -"
              f" the new state is '{self.state}'.{newline}")

    def update_repository(self, cmd):
        try:
            return self._update_repository(cmd)
        except Exception:
            self.remove_tmp_branches()
            raise

def cmd_diff(options):
    """Run the git diff command in a temporary directory."""

    with tempfile.TemporaryDirectory(prefix='tmp-alpm-repo') as repo_dir:
        options['gitrepo_dir'] = PosixPath(repo_dir)
        options['print_not_readable'] = False

        # Create the repository.
        apc = AlpmConf(**options)
        with redirect_stdout(io.StringIO()) as stdout:
            apc.run_cmd('cmd_create')

        difftool = options['difftool']
        cmd = f'{difftool} --diff-filter=M etc master --'
        print('git', cmd)
        output = apc.repo.git_cmd(cmd)
        print(output)

def dispatch_help(options):
    """Get help on a command."""

    command = options['subcommand']
    if command is None:
        command = 'help'
    options['parsers'][command].print_help()

    cmd_func = getattr(AlpmConf, f'cmd_{command}', None)
    if cmd_func:
        lines = cmd_func.__doc__.splitlines()
        print(f'\n{lines[0]}')

        other_lines = lines[2:]
        if other_lines:
            print()
            print(dedent('\n'.join(other_lines)))

def parse_args(argv):
    def isdir(path):
        if path is not None:
            path = PosixPath(path)
            if not path.is_dir():
                raise argparse.ArgumentTypeError(f'{path} is not a directory')
        return path

    def parse_boolean(val):
        if val in true:
            return True
        elif val in false:
            return False
        else:
            raise argparse.ArgumentTypeError(val)

    true = ('1', 'yes', 'true')
    false = ('0', 'no', 'false')
    pacman_dirs = get_pacman_dirs('/etc/pacman.conf')

    # Instantiate the main parser.
    main_parser = argparse.ArgumentParser(description=__doc__, add_help=False,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    main_parser.add_argument('--version', '-v', action='version',
                                        version='%(prog)s ' + __version__)
    subparsers = main_parser.add_subparsers(title='alpm-conf subcommands')

    # The 'parsers' dict collects all the subparsers.
    # It is used by dispatch_help() to print the help of a subparser.
    parsers = {}
    parsers['help'] = main_parser

    # The help subparser handles the help for each command.
    help_parser = subparsers.add_parser('help', add_help=False,
                                   help=dispatch_help.__doc__.splitlines()[0])
    help_parser.add_argument('subcommand', choices=parsers, nargs='?',
                                                                default=None)
    help_parser.set_defaults(command='dispatch_help', parsers=parsers)

    # Add the command subparsers.
    d = dict(inspect.getmembers(AlpmConf, inspect.isfunction))
    for command in sorted(d):
        if not command.startswith('cmd_'):
            continue

        cmd = command[4:]
        func = d[command]
        parser = subparsers.add_parser(cmd, help=func.__doc__.splitlines()[0],
                                                            add_help=False)
        parser.set_defaults(command=command)
        if cmd == 'diff':
            parser.add_argument('--difftool', default='diff',
                help='use a git difftool instead of diff'
                ' (default: "%(default)s")')
        else:
            parser.add_argument('--gitrepo-dir', type=isdir,
                help='git repository directory (default: "%(default)s")')

        if cmd in ('create', 'update', 'diff'):
            parser.add_argument('--database-dir',
                default=pacman_dirs['database-dir'], type=isdir,
                help='pacman database directory (default: "%(default)s")')
            parser.add_argument('--cache-dir',
                default=pacman_dirs['cache-dir'], type=isdir,
                help='pacman cache directory (default: "%(default)s")')
        if cmd in ('create', 'update', 'merge', 'diff'):
            parser.add_argument('--root-dir', default=pacman_dirs['root-dir'],
                help=('root directory, used for testing'
                      ' (default: "%(default)s")'),
                type=isdir)
        if cmd in ('create', 'update'):
            parser.add_argument('--print-not-readable', default='false',
                type=parse_boolean, metavar=f'{true}|{false}',
                help='print ignored etc-files that do not have'
                ' others-read-permission (default: "%(default)s")')
        parsers[cmd] = parser

    options = vars(main_parser.parse_args(argv[1:]))
    if 'command' not in options:
        main_parser.error('a command is required')
    return options

def alpm_conf(argv):
    options = parse_args(argv)

    # Run the command.
    if options['command'] == 'dispatch_help':
        dispatch_help(options)
        return

    try:
        if options['command'] == 'cmd_diff':
            # Call the function, not the AlpmConf method.
            cmd_diff(options)
            return

        apc = AlpmConf(**options)
        apc.run_cmd(apc.command)

    except ApcError as e:
        error = f'*** error: {str(e).strip()}\n'

        # Get the last frame of the traceback that is in alpm_conf.py.
        frame_summaries = traceback.extract_tb(e.__traceback__)
        for fs in reversed(frame_summaries):
            path = PosixPath(fs.filename)
            if path.name == 'alpm_conf.py':
                error += (f'Error triggered by the call to {fs.name}() at'
                          f' {path.name}:{fs.lineno}:\n')
                error += f'  {fs.line}'
                break
        sys.exit(error)

    return apc

def main():
    alpm_conf(sys.argv)

if __name__ == '__main__':
    main()
