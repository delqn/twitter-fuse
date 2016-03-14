import ctypes
import mock
import unittest

from fuse import FuseOSError

from . import mount
from . import config

CONF_FILE = 'fuse.conf.tests'


class MountTest(unittest.TestCase):
    def setUp(self):
        config.get_config(CONF_FILE, 'twitterapi')
        mount.twitter = mock.MagicMock()
        mount.twitter.get_friends.return_value = (['a', 'b'], None)
        self.mount = mount.TwitterClient()
        self.mount.followers = ['a', 'b', 'some_user']
        self.mount.user_tweets = {'a': {'3': (123, bytearray(b'three')),
                                        '4': (124, bytearray(b'four'))},
                                  'b': {'5': (256, bytearray(b'five'))},
                                  'some_user': {
                                      '6': (221, bytearray(b'six')),
                                      '7': (456, bytearray(b'@seven3d needs custom '
                                                           'kernel molds'))}}

    def test_access(self):
        mode = 1
        path = '/'
        self.mount.access(path, mode)

    def test_access_error(self):
        mount.twitter.get_rate_limit_status.return_value = {}
        with self.assertRaises(FuseOSError):
            self.mount.access(path='/blah', mode=1)

    def test_getattr(self):
        path = '/'
        attr = self.mount.getattr(path, fh=None)
        expected = {
            'st_ctime': mock.ANY, 'st_mtime': mock.ANY, 'st_nlink': 0, 'st_gid': mock.ANY,
            'st_size': 68,
            'st_mode': 16877, 'st_uid': mock.ANY, 'st_atime': mock.ANY
        }
        self.assertEqual(attr, expected)

    def test_getattr_error_file(self):
        path = '/error'
        attr = self.mount.getattr(path, fh=None)
        expected = {'st_ctime': mock.ANY, 'st_mtime': mock.ANY, 'st_nlink': 0, 'st_gid': mock.ANY,
                    'st_size': mock.ANY, 'st_mode': 33188, 'st_uid': mock.ANY,
                    'st_atime': mock.ANY}
        self.assertEqual(attr, expected)

    def test_getattr_mathematica_notebook(self):
        path = '/some_user.nb'
        attr = self.mount.getattr(path, fh=None)
        expected = {'st_ctime': mock.ANY, 'st_mtime': mock.ANY, 'st_nlink': 0, 'st_gid': mock.ANY,
                    'st_size': 1487, 'st_mode': 33188, 'st_uid': mock.ANY,
                    'st_atime': mock.ANY}
        self.assertEqual(attr, expected)

    def test_readdir_slash(self):
        path = '/'
        dirs = list(self.mount.readdir(path, fh=12))
        expected = ['.', '..', 'a', 'a.nb', 'b', 'b.nb', 'some_user', 'some_user.nb', 'errors']
        self.assertEqual(sorted(dirs), sorted(expected))

    def test_readdir_user(self):
        path = '/some_user'
        dirs = list(self.mount.readdir(path, fh=12))
        expected = ['.', '..', '6', '7', 'errors']
        self.assertEqual(sorted(dirs), sorted(expected))

    def test_statfs(self):
        path = '/'
        self.mount.statfs(path)

    def test_open(self):
        path = '/'
        flags = 1
        self.mount.open(path, flags)

    def test_read(self):
        path = '/'
        length = 23
        offset = 1
        fh = 12
        self.mount.read(path, length, offset, fh)

    def test_read_mathematica_notebook(self):
        path = '/some_user.nb'
        notebook_content = self.mount.read(path, length=999999, offset=0, fh=12)
        self.assertIn('six', notebook_content)
        self.assertIn('seven', notebook_content)
        ctypes.create_string_buffer(notebook_content)

    def test_parse_path(self):
        self.assertEqual((None, None), mount.parse_path('/'))
