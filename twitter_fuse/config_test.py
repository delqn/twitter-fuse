import unittest

from . import config


class ConfigTest(unittest.TestCase):
    def parse_test(self):
        conf_first = config.get_config('fuse.conf.tests', 'twitterapi')
        expected = {
            'oauth_secret': "''",
            'authorize_url': 'https://api.twitter.com/oauth/authorize?oauth_token=',
            'consumer_secret': 'abc',
            'oauth_token': "''",
            'request_token_url': 'https://api.twitter.com/oauth/request_token',
            'consumer_key': 'xyz',
            'access_token_url': 'https://api.twitter.com/oauth/access_token'}
        self.assertEqual(conf_first, expected)

        conf_second = config.get_config('fuse.conf.tests', 'twitterapi')
        self.assertEqual(conf_second, expected)
