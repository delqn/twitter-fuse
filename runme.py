#!/usr/bin/env python2.7
# pylint: disable=unexpected-keyword-arg, no-value-for-parameter

import click
from twitter_fuse import config, mount, oauth_token_and_secret


CONFIG_FILE = 'fuse.conf'
SECTION = 'twitterapi'


@click.command()
@click.option('--mountpoint', default='./mnt')
def mount_twitter(mountpoint):
    mount.mount(mountpoint)


if __name__ == "__main__":
    conf = config.get_config(CONFIG_FILE, SECTION)
    # TODO: or expired??
    if not conf.get('oauth_token'):
        config.store_oauth(oauth_token_and_secret())
    mount_twitter()
