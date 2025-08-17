"""The pacman database."""

import os
import io
import re
import stat
import gzip
import shutil
import tempfile
import json
import contextlib
import itertools
import tarfile
import zstandard
from pathlib import PosixPath

import pyalpm

from . import ApcError, run_cmd

def _pacman_dirs(pacconf_path, pacconf_map, commented=False):
    pacman_conf = {}
    comment = r'\#' if commented else ''

    # Compile the regular expressions.
    pacconf_re = {}
    for dir in pacconf_map:
        dirpath = pacconf_map[dir]

        # Possibly a white space separated pathname.
        pacconf_re[dir] = re.compile(
          rf'^[ ]*{comment}[ ]*{dirpath}[ ]*=[ ]*(?P<{dirpath}>.*(\w|/))[ ]*$')

    with open(pacconf_path) as f:
        for lineno, line in enumerate(f):
            for dir in pacconf_re:
                matchobj = pacconf_re[dir].match(line)
                if matchobj:
                    cache_dir = matchobj.group(pacconf_map[dir])
                    pacman_conf[dir] = cache_dir
                    break

    return pacman_conf

def get_pacman_dirs(pacconf_path):
    """Get the pacman directories."""

    pacman_conf = {
        'root-dir':     '/',
        'database-dir': '/var/lib/pacman/',
        'cache-dir':    '/var/cache/pacman/pkg/',
    }

    pacconf_map = {
        'root-dir':     'RootDir',
        'database-dir': 'DBPath',
        'cache-dir':    'CacheDir',
    }

    # Update first with the commented out default dirs values.
    pacman_conf.update(_pacman_dirs(pacconf_path, pacconf_map, commented=True))

    # Update with the configured dirs values.
    pacman_conf.update(_pacman_dirs(pacconf_path, pacconf_map))

    return pacman_conf

def package_as_dict(name, path):
    """Return a Package content as a dict."""

    package_dict = {}
    try:
        with open(path) as f:
            package_as_str = f.read()
    except FileNotFoundError:
        pass
    else:
        try:
            exec(package_as_str, globals(), package_dict)
        except Exception as e:
            raise ApcError(f"in the '{name}' package file: {e}") from e
    return package_dict

@contextlib.contextmanager
def tarfile_open(name, mode='r'):

    assert mode in ('r', 'w')
    if mode == 'r':
        compressor = zstandard.ZstdDecompressor().stream_reader
    elif mode == 'w':
        compressor = zstandard.ZstdCompressor().stream_writer

    # Currently z-standard only supports stream-like file objects.
    # See https://github.com/indygreg/python-zstandard/issues/23.
    with open(name, f'{mode}b') as f:
        with compressor(f) as fobj:
            with tarfile.open(mode=f"{mode}|", fileobj=fobj) as tar:
                yield tar

class Package():

    def __init__(self, pkg, pacman_conf, stdout=None):
        self.root_dir = pacman_conf['root_dir']
        self.name = pkg.name
        self.version = pkg.version
        self.path = PosixPath(pacman_conf['cache_dir'],
                        f'{pkg.name}-{pkg.version}-{pkg.arch}.pkg.tar.zst')

        db_path = pacman_conf['db_path']
        if stdout is not None:
            assert isinstance(stdout, io.StringIO)
        self.new_files = self._get_new_files(db_path, stdout)
        self.original_files = None

    def _get_new_files(self, db_path, stdout):
        """Get the package new files.

        Exclude files that are symlinks.
        Exclude files that do not have others-read-permission.
        """

        # Parse the package mtree file to get sha256digest of the etc files.
        mtree_path = (db_path / 'local'/ f'{self.name}-{self.version}'
                      / 'mtree')

        with tempfile.NamedTemporaryFile() as f_tmp:
            # Extract mtree content.
            with gzip.open(mtree_path, 'rb') as f_in:
                with open(f_tmp.name, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Convert mtree content to json format and then to Python object.
            proc = run_cmd(['alpm-mtree', 'format', '-o', 'json', f_tmp.name])
            mtree_obj = json.loads(proc.stdout)

        # Return the dict {etc relpath: sha256digest}
        # excluding directories, symlinks and files not readable by 'others'.
        d = {}
        root_dir = self.root_dir
        root_dir_length = len(root_dir.parts)
        for item in mtree_obj:
            path = root_dir / item['path']
            if path.parts[root_dir_length] == 'etc':
                relpath = PosixPath(*path.parts[root_dir_length:])
                if item['type'] in ('dir', 'link'):
                    continue

                # Exclude files with no others-read-permission when not
                # root user.
                if (os.geteuid() != 0 and
                            not int(item['mode'], base=8) & stat.S_IROTH):
                    if stdout is not None:
                        if not stdout.getvalue():
                            print('Ignored etc-files that do not have'
                                  ' others-read-permission:', file=stdout)
                        print(f'  {relpath}', file=stdout)
                    continue

                sha256digest = item.get('sha256_digest')
                assert sha256digest is not None, ('alpm-mtree parser'
                    'is supposed to fail when a file misses its sha256digest')
                d[relpath] = sha256digest

        return d

    def get_original_files(self, path):
        """Get the original files from path."""

        self.original_files = {}
        package_dict = package_as_dict(self.name, path)
        if not package_dict:
            return None

        self.original_files = package_dict['etc_files']
        return package_dict['version']

    def _extract_from_package(self, fnames, repo_dir):

        with tarfile_open(self.path) as tar:
            for tinfo in tar:
                if tinfo.name in list(fnames):
                    tar.extract(tinfo, repo_dir, filter='fully_trusted')
                    fnames.remove(tinfo.name)
                    if not fnames:
                        break

    def extract_new_files(self, repo_dir):

        assert self.original_files is not None

        new_files = {}
        original_files = {}
        for fname, sha256digest in self.new_files.items():

            prev_sha256digest = None
            if len(self.original_files):
                prev_sha256digest = self.original_files.get(fname)
                if prev_sha256digest == sha256digest:
                    continue

            # 'prev_sha256digest' is None when the corresponding etc file is a
            # new file.
            new_files[fname] = sha256digest
            original_files[fname] = prev_sha256digest

        # Extract 'new_files' from the archive.
        if new_files:
            self._extract_from_package(set(str(f) for f in new_files),
                                                                repo_dir)
        return new_files, original_files

    def __str__(self):
        return (f"version = '{self.version}'\n"
                f"etc_files = {self.new_files}")

class PacmanDataBase():

    def __init__(self, pacman_conf, repo=None):
        self.pacman_conf = pacman_conf
        self.root_dir = self.pacman_conf['root_dir']
        self.repo = repo
        self.new_packages = None
        self.new_files = {}         # {PosixPath(relpath): sha256digest}
        self.original_files = {}    # {PosixPath(relpath): sha256digest}

    def init(self):
        db_path = self.pacman_conf['db_path']
        handle = pyalpm.Handle(str(self.root_dir), str(db_path))
        self.localdb = handle.get_localdb()

        self.installed_packages = self._installed_packages()
        self.installed_files = self._installed_files()

    def _installed_packages(self):
        """Installed packages that have etc files.

        Return the dict {pyalpm pkg instance: etc file names}.
        """

        d = {}
        for pkg in self.localdb.pkgcache:
            etc_files = []
            for (relpath, _, _) in pkg.files:
                if not relpath.startswith('etc/'):
                    continue

                # Check that relpath is a plain file in the /etc directory.
                path = self.root_dir / relpath
                try:
                    if path.is_file() and not path.is_symlink():
                        etc_files.append(relpath)
                except OSError:
                    pass

            if len(etc_files):
                d[pkg] = etc_files

        return d

    def _installed_files(self):
        return set(itertools.chain(*(etc_files for (pkg, etc_files) in
                                        self.installed_packages.items())))

    def list_new_packages(self, repo_dir, print_not_readable=False):
        """List of Package instances whose etc files have changed.

        'repo_dir' is the path to the repository where the 'packages-tmp'
        branch has been checked out.

        Side effect:
          - Fill up the 'package.original_files' dict with the corresponding
            file content in the 'packages' banch, for all the packages in this
            list.
        """

        if self.repo is not None:
            assert self.repo.current_branch == 'packages-tmp'

        repo_dir = PosixPath(repo_dir)
        packages = []
        with io.StringIO() as not_readable:
            for pkg in self.installed_packages:
                package = Package(pkg, self.pacman_conf, stdout=not_readable)

                # Ignore package when the archive is not readable:
                # the etc branch cannot be updated.
                path = package.path
                if not path.is_file() or not os.access(path, os.R_OK):
                    print(f'Ignore {package.path.name} (not readable)')
                    continue

                prev_version = package.get_original_files(
                                                    repo_dir / package.name)

                # Ignore package with package version unchanged.
                if prev_version == package.version:
                    continue

                # Ignore package with all etc_files unchanged.
                # 'package.original_files' is the empty dictionary when the
                # package does not exist in the 'packages-tmp' branch.
                if (len(package.original_files) and
                        package.new_files == package.original_files):
                    continue

                packages.append(package)

            length = len(packages)
            plural = 's' if length > 1 else ''
            result = (f'{length} package archive{plural} with changed or new'
                      f' etc-files')
            if length:
                print(f'{result}:')
                for package in packages:
                    print(f'  {package.path.name}')
            else:
                print(f'{result}.')
            print()

            if print_not_readable:
                output = not_readable.getvalue()
                if output:
                    print(output, sep='')

        self.new_packages = packages
        return packages

    def extract_files(self, repo_dir):
        """Extract all new etc files from package archives in pacman cache.

        'repo_dir' is the path to the repository where the 'etc-tmp' branch
        has been checked out.

        Side effects:
          - Discard files whose sha256digest is the same for the new and the
            original version.
          - The files are extracted to the 'etc-tmp' branch.
        """

        if self.repo is not None:
            assert self.repo.current_branch == 'etc-tmp'
        assert self.new_packages is not None

        repo_dir = PosixPath(repo_dir)
        for package in self.new_packages:
            new_files, original_files = package.extract_new_files(repo_dir)

            self.new_files.update(new_files)
            self.original_files.update(original_files)
