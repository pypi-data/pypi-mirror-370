"""Utilities to build environments for the tests."""

import contextlib
import tempfile
import gzip
from pathlib import PosixPath
from collections import namedtuple

from ..packages import tarfile_open
from ..alpm_conf import sha256

Pkg = namedtuple('Pkg', ['name', 'version', 'arch', 'files'])

PACMAN_PKG = Pkg('pacman', '1.0-1', 'x86_64',
                                (
                                    ('etc/makepkg.conf', 0, 0),
                                    ('etc/pacman.conf', 0, 0),
                                    ('etc/makepkg.conf.d/fortran.conf', 0, 0),
                                    ('etc/makepkg.conf.d/rust.conf', 0, 0),
                                    ('usr/foobar', 0, 0),
                                ))

def pkg_etcfiles(pkg):
    return [etc_file for (etc_file, _, _) in pkg.files if
                                        etc_file.startswith('etc')]

def pkg_mtree(pkg, count, type='file', mode='644'):
    """Build an mtree for 'pkg'.

    The values of 'type' and 'mode' are applied to the first etc file.
    """

    mtree = ['/set uid=0 gid=0',
             '/set type=file mode=644']

    is_first = True
    with create_etc_dir([pkg], [count], 'mtree') as etc_dir:

        for relpath in pkg_etcfiles(pkg):
            sha = sha256(etc_dir / relpath)
            if is_first:
                mtree.append(f'./{relpath} type={type} mode={mode} time=0.0'
                             f' size=0 sha256digest={sha}')
                is_first = False
            else:
                mtree.append(f'./{relpath} time=0.0 size=0 sha256digest={sha}')

    return '\n'.join(mtree) + '\n'

def create_mtree(pkg, count, db_path, type='file', mode='644'):
    """Create a mtree on 'db_path'.

    'count'     list of the number of lines for each etc file in pkg.
    """

    mtree_path = (db_path / 'local'/ f'{pkg.name}-{pkg.version}' / 'mtree')
    mtree_path.parent.mkdir(parents=True)

    # Create the mtree file.
    mtree = pkg_mtree(pkg, count, type=type, mode=mode)
    with open(mtree_path, 'wb') as f:
        f.write(gzip.compress(mtree.encode()))

@contextlib.contextmanager
def create_etc_dir(pkgs, counts, prefix):
    """Create an etc directory with the pkgs etc files.

    'pkgs'      list of namedtuple Pkg instances.
    'counts'    there is an element in 'counts' for each pkg in 'pkgs' and it
                is a list of the number of lines for each etc file in pkg.
    'prefix'    temporary directory name starts with this prefix.

    For example: create_etc_dir([PACMAN_PKG], [[5,5,5,5]], 'mtree')
    """

    assert len(pkgs) == len(counts)

    with tempfile.TemporaryDirectory(
                            prefix=f'tmp-etc-{prefix}-') as etc_dir:
        etc_dir = PosixPath(etc_dir)

        for idx, pkg in enumerate(pkgs):
            count = counts[idx]
            etc_files = pkg_etcfiles(pkg)
            assert len(count) == len(etc_files)

            for cnt_idx, etc_file in enumerate(etc_files):
                etc_file = etc_dir / etc_file
                etc_file.parent.mkdir(parents=True, exist_ok=True)
                with open(etc_file, 'w') as f:
                    for i in range(count[cnt_idx]):
                        f.write(f'line {i}\n')

        yield etc_dir

def build_archives(pkgs, counts, cache_dir):

    with create_etc_dir(pkgs, counts, 'cache') as etc_dir:
        with contextlib.chdir(etc_dir):
            for pkg in pkgs:
                # Build the archive.
                pkg_path = (cache_dir /
                    f'{pkg.name}-{pkg.version}-{pkg.arch}.pkg.tar.zst')
                with tarfile_open(pkg_path, mode='w') as tar:
                    tar.add('etc')

@contextlib.contextmanager
def create_cache_dir(pkgs, counts):
    """Create a cache directory containing the package archives.

    Same arguments as create_etc_dir() except 'prefix'.
    """

    assert len(pkgs) == len(counts)

    with tempfile.TemporaryDirectory(prefix='tmp-cache-') as cache_dir:
        cache_dir = PosixPath(cache_dir)
        build_archives(pkgs, counts, cache_dir)
        yield cache_dir

@contextlib.contextmanager
def create_packages_dir(pkgs, counts):
    """Create a packages directory.

    Same arguments as create_etc_dir() except 'prefix'.
    """

    assert len(pkgs) == len(counts)

    with tempfile.TemporaryDirectory(
                            prefix='tmp-packages-') as packages_dir:
        packages_dir = PosixPath(packages_dir)

        with create_etc_dir(pkgs, counts, 'packages') as etc_dir:
            for pkg in pkgs:
                etc_files = {}
                for file in pkg_etcfiles(pkg):
                    etc_files[PosixPath(file)] = sha256(etc_dir / file)
                with open(packages_dir / pkg.name, 'w') as f:
                    f.write(f"version = '{pkg.version}'\n")
                    f.write(f"etc_files = {etc_files}")

            yield packages_dir

class _LocalDb:
    def __init__(self, pkgs):
        self.pkgcache = pkgs

class PyalpmHandle:
    """This class mocks pyalpm.Handle.

    To use it call the set_localdb() class method with a list of instances of
    Pkg.
    """

    def __init__(self, *args):
        pass

    @classmethod
    def set_localdb(cls, pkgs):
        cls.pkgs = pkgs

    def get_localdb(self):
        return _LocalDb(self.pkgs)
