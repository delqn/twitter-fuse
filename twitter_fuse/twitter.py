import datetime
import requests
import time

from .oauth import get_oauth
from .logger import logger


PRE = 'https://api.twitter.com/1.1'
TOTAL_FRIENDS = 500
FRIENDS_PER_REQUEST = 200
TWEETS_PER_REQUEST = 500


def timestamp(string):
    '''Convert string date to timestamp'''
    # TODO: figure out why %z does not work as expected with +0000
    string = string.replace('+0000 ', '')
    return int(time.mktime(
        datetime.datetime.strptime(string, '%a %b %d %H:%M:%S %Y').utctimetuple()))


def get_friends():
    screen_name = get_settings().get('screen_name')
    cursor = -1
    friends = set()
    static_url = '{}/friends/list.json?screen_name={}&count={}'.format(
        PRE, screen_name,
        FRIENDS_PER_REQUEST if FRIENDS_PER_REQUEST < TOTAL_FRIENDS else TOTAL_FRIENDS)
    while len(friends) < TOTAL_FRIENDS:
        url = static_url + '&cursor={}'.format(cursor)
        logger.info('[twitter] Fetching @%s\'s friends: %s', screen_name, url)
        response = requests.get(url, auth=get_oauth()).json()
        errors = None
        if 'errors' in response:
            errors = set(error['message'] for error in response['errors'])
            logger.error('[twitter][get_friends] Errors: %s', ','.join(errors))
            break
        logger.info('[twitter] get_friends -> %s', response)
        next_cursor = response.get('next_cursor')
        friends.update(set(user['screen_name'] for user in response.get('users', [])))
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
    return friends, errors


def get_settings():
    logger.info('[twitter] Getting your settings.')
    url = '{}/account/settings.json'.format(PRE)
    return requests.get(url, auth=get_oauth()).json()


def get_tweets_for(screen_name, since_tweet_id=None, max_id=None):
    url = '{}/statuses/user_timeline.json?screen_name={}&count={}&since_id={}'.format(
        PRE, screen_name, TWEETS_PER_REQUEST, since_tweet_id)
    logger.info('[twitter] Fetching new tweets for @%s via %s', screen_name, url)
    response = requests.get(url, auth=get_oauth())
    _new = []
    for t in response.json():
        try:
            _new.append((t['id_str'], t['created_at'], t['text']))
        except Exception as e:
            print t, e

    return {int(tid): (timestamp(tdate), bytearray(txt, 'utf-8')) for tid, tdate, txt in _new}


def get_rate_limit_status():
    url = '{}/application/rate_limit_status.json'.format(PRE)
    rate_limit_status = requests.get(url, auth=get_oauth()).json()
    logger.info('[twitter] Get rate limit status: %s', rate_limit_status)
    return rate_limit_status
