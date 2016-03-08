from __future__ import with_statement

import errno
import os

from . import twitter

from fuse import FUSE, FuseOSError, Operations

FILE_ATTR_KEYS = (
    'st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid')
STAT_KEYS = (
    'f_bavail', 'f_bfree', 'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files',
    'f_flag', 'f_frsize', 'f_namemax')


class TwitterClient(Operations):
    def __init__(self):
        self.followers = twitter.get_friends()
        self.user_tweets = {}

    def access(self, path, mode):
        print '--- access ---   path={}'.format(path)

        errors = twitter.get_rate_limit_status().get('errors', {})
        if errors:
            for error in errors:
                print '>'*25, error.get('message')
            return

        if path == '/':
            return

        screen_name, tweet_id = parse_path(path)

        print 'screen_name -> ', screen_name
        print 'tweet_id -> ', tweet_id
        if screen_name not in self.followers:
            raise FuseOSError(errno.EACCES)

        if not self.user_tweets.get(screen_name):
            tweets = {t[0]: t[1:] for t in twitter.get_tweets(screen_name)}
            self.user_tweets.setdefault(screen_name, {})
            self.user_tweets[screen_name].update(tweets)

        if not tweet_id:
            return

        if tweet_id not in self.user_tweets.get(screen_name, {}):
            raise FuseOSError(errno.EACCES)

    def getattr(self, path, fh=None):
        screen_name, tweet_id = parse_path(path)
        attr = dict(
            st_uid=os.getuid(), st_gid=os.getuid(),
            st_atime=0, st_ctime=0, st_mtime=1457168070,
            st_nlink=0,
            st_mode=16877,
            st_size=68)
        if tweet_id in self.user_tweets.get(screen_name, {}):
            # TODO: get the date and make it the file's
            _, tweet = self.user_tweets[screen_name].get(tweet_id, (None, 0))
            attr.update(
                dict(
                    st_mode=33188,
                    st_size=len(bytearray(tweet)) if tweet else 0))
        return attr

    def readdir(self, path, fh):
        dirs = ['.', '..']
        if path == '/':
            dirs.extend(self.followers)
        else:
            screen_name, _ = parse_path(path)
            dirs.extend(self.user_tweets[screen_name].keys())
        for r in dirs:
            yield r

    def statfs(self, path):
        return dict(
            f_bsize=1048576,
            f_bavail=3348393,
            f_favail=3348393,
            f_files=121837598,
            f_frsize=4096,
            f_blocks=121837600,
            f_ffree=3348393,
            f_bfree=3412393,
            f_namemax=255,
            f_flag=0)

    def open(self, path, flags):
        return 12

    def read(self, path, length, offset, fh):
        screen_name, tweet_id = parse_path(path)
        _, tweet = self.user_tweets.get(screen_name, {}).get(tweet_id, (0, ''))
        return ''.join([chr(x) for x in tweet[offset: offset + length]])


def parse_path(path):
    pieces = path.split('/')
    screen_name = pieces[1]
    tweet_id = pieces[2] if len(pieces) > 2 else None
    return screen_name, tweet_id


def mount(mountpoint):
    FUSE(TwitterClient(), mountpoint, nothreads=True, foreground=True)
