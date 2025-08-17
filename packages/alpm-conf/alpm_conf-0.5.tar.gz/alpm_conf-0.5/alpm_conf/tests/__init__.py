"""Test cases."""

from pathlib import PosixPath
from unittest import TestCase

class CustomTestCase(TestCase):

    def pacman_conf(self, root_dir='/', cache_dir='/', db_path='/'):
        return {
            'root_dir':  PosixPath(root_dir),
            'cache_dir': PosixPath(cache_dir),
            'db_path':   PosixPath(db_path),
        }
