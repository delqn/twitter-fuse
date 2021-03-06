from __future__ import with_statement

import errno
import os
import time

from .twitter import get_friends, get_tweets_for
from .logger import logger

from fuse import FUSE, FuseOSError, Operations

GID = os.getgid()
UID = os.getuid()
FETCH_AGAIN_AFTER_SECONDS = 15


def logit(fn):
    def wrapper(*args, **kwargs):
        logger.info('[mount] %s %s %s', str(fn).split(' ')[1], args, kwargs)
        return fn(*args, **kwargs)
    return wrapper


class TwitterMount(Operations):
    def __init__(self):
        self.followers, self.errors = get_friends()
        self.user_tweets = {}
        self.user_next_fetch = {}

    def _fill_tweets_for(self, screen_name):
        next_fetch = self.user_next_fetch.get(screen_name, 0)
        if screen_name not in self.user_tweets or time.time() >= next_fetch:
            self.user_next_fetch[screen_name] = int(time.time()) + FETCH_AGAIN_AFTER_SECONDS
            all_tweets_for_user = self.user_tweets.get(screen_name, {}).keys()
            since_tweet_id = max(all_tweets_for_user) if all_tweets_for_user else 1
            self.user_tweets.setdefault(screen_name, {})
            print get_tweets_for(screen_name, since_tweet_id)
            self.user_tweets[screen_name].update(get_tweets_for(screen_name, since_tweet_id))

    @logit
    def access(self, path, mode):
        if path == '/':
            return

        screen_name, tweet_id = parse_path(path)
        if screen_name not in self.followers:
            logger.error('[mount][access] Error: %s not in followers list: %s',
                         screen_name, self.followers)
            raise FuseOSError(errno.EACCES)

        self._fill_tweets_for(screen_name)

        if not tweet_id:
            return

        if tweet_id not in self.user_tweets.get(screen_name, {}):
            logger.error('[mount][access] Error: %s not in tweets fetched for user %s: %s',
                         tweet_id, screen_name, self.user_tweets.get(screen_name, {}))
            raise FuseOSError(errno.EACCES)

    @logit
    def getattr(self, path, fh=None):
        st_size = 68
        st_mtime = 1
        st_mode = 16877
        screen_name, tweet_id = parse_path(path)
        is_file = tweet_id in self.user_tweets.get(screen_name, {}) or 'error' in path
        if is_file:
            logger.info('[mount][getattr] this is a file')
            st_mode = 33188
            if 'error' in path:
                logger.info('[mount][getattr] looking at an error')
                st_size = len('\n'.join(self.errors)) if self.errors else 0
            else:
                logger.info('[mount][getattr] looking good')
                st_mtime, tweet = self.user_tweets[screen_name].get(tweet_id, (None, 0))
                st_size = len(bytearray(tweet)) + 1 if tweet else 0
        logger.info('[mount] getattr: path=%s, fh=%s', path, fh)
        return dict(
            st_uid=UID, st_gid=GID,
            st_atime=0, st_ctime=0, st_mtime=st_mtime,
            st_nlink=0, st_mode=st_mode, st_size=st_size)

    @logit
    def readdir(self, path, fh):
        logger.info('[mount] readdir: path=%s, fh=%s, len(followers)=%s, len(user_tweets)=%s',
                    path, fh, len(self.followers), len(self.user_tweets))
        file_names = ['.', '..']
        if self.errors:
            file_names.append('errors')
        if path == '/':
            file_names.extend(self.followers)
        else:
            screen_name, _ = parse_path(path)
            file_names.extend(self.user_tweets[screen_name].keys())
        for filename in file_names:
            yield str(filename)

    @logit
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

    @logit
    def open(self, path, flags):
        logger.info('[mount] open: path=%s, flags=%s', path, flags)
        return 12

    @logit
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
    tweet_id = int(pieces[2]) if len(pieces) > 2 else None
    return screen_name if screen_name else None, tweet_id


def mount(mountpoint):
    FUSE(TwitterMount(), mountpoint, nothreads=True, foreground=True)
