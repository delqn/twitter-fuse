import mock
import unittest

from fuse import FuseOSError

from . import mount
from . import config

CONF_FILE = 'fuse.conf.tests'


class MountTest(unittest.TestCase):
    def setUp(self):
        config.get_config(CONF_FILE, 'twitterapi')
        mount.get_friends = mock.MagicMock(return_value=(['a', 'b'], None))
        mount.get_tweets_for = mock.MagicMock(return_value=[('id_1', 2, 3), ('id_2', 'b', 'c')])
        self.mount = mount.TwitterMount()
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

    def test_readdir_slash(self):
        path = '/'
        dirs = list(self.mount.readdir(path, fh=12))
        expected = ['.', '..', 'a', 'b', 'some_user']
        self.assertEqual(sorted(dirs), sorted(expected))

    def test_readdir_user(self):
        path = '/some_user'
        dirs = list(self.mount.readdir(path, fh=12))
        expected = ['.', '..', '6', '7']
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

    def test_parse_path(self):
        self.assertEqual((None, None), mount.parse_path('/'))

    def test_fill_tweets_for(self):
        self.mount._fill_tweets_for('some_other_user')
        mount.get_tweets_for.assert_called_with('some_other_user', None)
        self.mount.user_next_fetch['some_other_user'] = 0
        self.mount._fill_tweets_for('some_other_user')
        mount.get_tweets_for.assert_called_with('some_other_user', 'id_2')
