from __future__ import with_statement

import errno
import os
import time

from .twitter import get_friends, get_tweets_for
from .logger import logger

from fuse import FUSE, FuseOSError, Operations

GID = os.getgid()
UID = os.getuid()


class TwitterClient(Operations):
    def __init__(self):
        self.followers, self.errors = get_friends()
        self.user_tweets = {}
        self.access_seqnum = 0

    def access(self, path, mode):
        self.access_seqnum += 1
        # logger.info('[%s]: access:   path=%s, mode=%s', self.access_seqnum, path, mode)
        if path == '/':
            return

        screen_name, tweet_id = parse_path(path)
        if screen_name not in self.followers:
            raise FuseOSError(errno.EACCES)

        if screen_name not in self.user_tweets:
            self.user_tweets[screen_name] = {
                tid: (tdate, txt) for tid, tdate, txt in get_tweets_for(screen_name)}

        if not tweet_id:
            return

        if tweet_id not in self.user_tweets.get(screen_name, {}):
            raise FuseOSError(errno.EACCES)

    def getattr(self, path, fh=None):
        screen_name, tweet_id = parse_path(path)
        now = int(time.time())
        attr = dict(
            st_uid=UID, st_gid=GID,
            st_atime=0, st_ctime=0, st_mtime=now,
            st_nlink=0,
            st_mode=16877,
            st_size=68)

        is_file = tweet_id in self.user_tweets.get(screen_name, {}) or 'error' in path

        if is_file:
            if 'error' in path:
                errors_str = '\n'.join(self.errors if self.errors else [])
                attr.update(dict(st_size=len(errors_str)))
            else:
                # TODO: get the date and make it the file's
                timestamp, tweet = self.user_tweets[screen_name].get(tweet_id, (None, 0))
                attr.update(dict(st_mtime=timestamp,
                                 st_size=len(bytearray(tweet)) if tweet else 0))
            attr.update(dict(st_mode=33188))
        logger.info('[mount] getattr: path=%s, fh=%s, attr=%s', path, fh, attr)
        return attr

    def readdir(self, path, fh):
        logger.info('[mount] readdir: path=%s, fh=%s, len(followers)=%s, len(user_tweets)=%s',
                    path, fh, len(self.followers), len(self.user_tweets))
        dirs = ['.', '..']
        if self.errors:
            dirs.append('errors')
        if path == '/':
            dirs.extend(self.followers)
        else:
            screen_name, _ = parse_path(path)
            dirs.extend(self.user_tweets[screen_name].keys())
        for r in dirs:
            yield r

    def statfs(self, path):
        # logger.info('[mount] statfs: path=%s', path)
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
        logger.info('[mount] open: path=%s, flags=%s', path, flags)
        return 12

    def read(self, path, length, offset, fh):
        logger.info('[mount] read: path=%s, length=%s, offset=%s, fh=%s', path, length, offset, fh)
        if 'error' in path:
            return '\n'.join(self.errors if self.errors else [])
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
