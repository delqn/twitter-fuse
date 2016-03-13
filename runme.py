#!/usr/bin/env python2.7
# pylint: disable=unexpected-keyword-arg, no-value-for-parameter

import click
import ConfigParser
from twitter_fuse import config, mount, oauth_token_and_secret


CONFIG_FILE = 'fuse.conf'
SECTION = 'twitterapi'


@click.command()
@click.option('--mountpoint', default='./mnt')
def mount_twitter(mountpoint):
    mount.mount(mountpoint)


if __name__ == "__main__":
    config.init(CONFIG_FILE, SECTION)
    conf = config.get_config()
    if not conf.get('oauth_token'):  # TODO: or expired??
        oauth_token, oauth_secret = oauth_token_and_secret()
        _config = ConfigParser.RawConfigParser()
        _config.read(CONFIG_FILE)
        _config.set(SECTION, 'oauth_token', oauth_token)
        _config.set(SECTION, 'oauth_secret', oauth_secret)
        with open(CONFIG_FILE, 'wb') as configfile:
            print 'Writing to {}'.format(configfile)
            _config.write(configfile)

    mount_twitter()
