import unittest

from . import config

CONF_FILE = 'fuse.conf.tests'


class ConfigTest(unittest.TestCase):
    def setUp(self):
        with open(CONF_FILE, 'w') as f:
            f.write('[twitterapi]\n'
                    'access_token_url = https://api.twitter.com/oauth/access_token\n'
                    'authorize_url = https://api.twitter.com/oauth/authorize?oauth_token=\n'
                    'consumer_key = xyz\n'
                    'consumer_secret = abc\n'
                    'request_token_url = https://api.twitter.com/oauth/request_token\n'
                    'oauth_token\n'
                    'oauth_secret\n')

    def parse_test(self):
        conf_first = config.get_config('fuse.conf.tests', 'twitterapi')
        expected = {
            'access_token_url': 'https://api.twitter.com/oauth/access_token',
            'authorize_url': 'https://api.twitter.com/oauth/authorize?oauth_token=',
            'consumer_secret': 'abc',
            'consumer_key': 'xyz',
            'request_token_url': 'https://api.twitter.com/oauth/request_token',
            'oauth_token': None,
            'oauth_secret': None,
        }
        self.assertEqual(conf_first, expected)

        conf_second = config.get_config('fuse.conf.tests', 'twitterapi')
        self.assertEqual(conf_second, expected)

    def store_oauth_test(self):
        conf = config.get_config()
        self.assertFalse(conf['oauth_token'])
        self.assertFalse(conf['oauth_secret'])
        config.store_oauth(oauth_token='token-here', oauth_secret='secret-here')
        self.assertFalse(conf['oauth_token'], 'token-here')
        self.assertFalse(conf['oauth_secret'], 'secret-here')
