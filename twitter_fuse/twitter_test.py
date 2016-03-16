# -*- coding: utf-8 -*-

import responses
import unittest

from . import twitter


def mock_requests():
    responses.add(
        url=turl('/friends/list.json'),
        method=responses.GET, status=200, content_type='application/json',
        body=('{"previous_cursor": 0,"previous_cursor_str": "0",'
              '"next_cursor": 1333504313713126852,'
              '"users": [{"screen_name": "a"},{"screen_name": "b"}]}'))

    responses.add(
        url=turl('/account/settings.json'),
        method=responses.GET, status=200, content_type='application/json',
        body='{}')

    responses.add(
        url=turl('/application/rate_limit_status.json'),
        method=responses.GET, status=200, content_type='application/json',
        body='{}')

    responses.add(
        url=turl('/statuses/user_timeline.json'),
        method=responses.GET, status=200, content_type='application/json',
        body=open('test_data/statuses.user_timeline.json', 'r').read())


def turl(tail):
    return 'https://api.twitter.com/1.1{}'.format(tail)


class TwitterTest(unittest.TestCase):
    def setUp(self):
        mock_requests()

    @responses.activate
    def get_friends_test(self):
        friends, errors = twitter.get_friends()
        self.assertEqual(friends, set(['a', 'b']))
        self.assertEqual(errors, None)

    @responses.activate
    def get_settings_test(self):
        settings = twitter.get_settings()
        self.assertEqual(settings, {})

    @responses.activate
    def get_tweets_for_test(self):
        tweets = twitter.get_tweets_for(screen_name='some-user')
        expected = {
            240859602684612608: (
                1346289178,
                bytearray(b'Introducing the Twitter Certified Products '
                          'Program: https://t.co/MjJ8xAnT')),
            239413543487819778: (
                1345944411,
                bytearray(b'We are working to resolve issues with application management '
                          '& logging in to the dev portal: https://t.co/p5bOzH0k ^TS'))}

        self.assertEqual(tweets, expected)

    @responses.activate
    def get_rate_limit_status_test(self):
        rate_limit_status = twitter.get_rate_limit_status()
        self.assertEqual(rate_limit_status, {})
