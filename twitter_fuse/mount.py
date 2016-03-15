from __future__ import with_statement

import errno
import os
import time

from .twitter import get_friends, get_tweets_for
from .logger import logger

from fuse import FUSE, FuseOSError, Operations

GID = os.getgid()
UID = os.getuid()
FETCH_AGAIN_AFTER_SECONDS = 60 * 3  # 3 minutes


class TwitterMount(Operations):
    def __init__(self):
        self.followers, self.errors = get_friends()
        self.user_tweets = {}
        self.access_seqnum = 0
        self.next_fetch = int(time.time()) + FETCH_AGAIN_AFTER_SECONDS

    def _fill_tweets_for(self, screen_name):
        if screen_name not in self.user_tweets or time.time() >= self.next_fetch:
            self.next_fetch = int(time.time()) + FETCH_AGAIN_AFTER_SECONDS
            all_tweets_for_user = self.user_tweets.get(screen_name, {}).keys()
            start_from_tweet = max(all_tweets_for_user) if all_tweets_for_user else None
            self.user_tweets.setdefault(screen_name, {})
            self.user_tweets[screen_name].update({
                tid: (tdate, txt)
                for tid, tdate, txt in get_tweets_for(screen_name, start_from_tweet)})

    def access(self, path, mode):
        self.access_seqnum += 1
        # logger.info('[%s]: access:   path=%s, mode=%s', self.access_seqnum, path, mode)
        if path == '/':
            return

        screen_name, tweet_id = parse_path(path)
        if screen_name not in self.followers:
            raise FuseOSError(errno.EACCES)

        self._fill_tweets_for(screen_name)

        if not tweet_id:
            return

        if tweet_id not in self.user_tweets.get(screen_name, {}):
            raise FuseOSError(errno.EACCES)

    def getattr(self, path, fh=None):
        st_size = 68
        st_mtime = 1
        st_mode = 16877
        screen_name, tweet_id = parse_path(path)
        is_file = tweet_id in self.user_tweets.get(screen_name, {}) or 'error' in path
        if is_file:
            st_mode = 33188
            if 'error' in path:
                st_size = len('\n'.join(self.errors)) if self.errors else 0
            else:
                st_mtime, tweet = self.user_tweets[screen_name].get(tweet_id, (None, 0))
                st_size = len(bytearray(tweet)) if tweet else 0
        logger.info('[mount] getattr: path=%s, fh=%s', path, fh)
        return dict(
            st_uid=UID, st_gid=GID,
            st_atime=0, st_ctime=0, st_mtime=st_mtime,
            st_nlink=0, st_mode=st_mode, st_size=st_size)

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
        return ''.join([chr(x) for x in tweet[offset: offset + length]]) + '\n'


def parse_path(path):
    pieces = path.split('/')
    screen_name = pieces[1]
    tweet_id = pieces[2] if len(pieces) > 2 else None
    return screen_name if screen_name else None, tweet_id


def mount(mountpoint):
    FUSE(TwitterMount(), mountpoint, nothreads=True, foreground=True)
