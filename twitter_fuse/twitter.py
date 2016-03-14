import datetime
import requests
import time

from .oauth import get_oauth
from .logger import logger


PRE = 'https://api.twitter.com/1.1'
MAX_TOTAL_FRIENDS = 5
MAX_FRIENDS_PER_REQUEST = 20


def timestamp(string):
    '''Convert string date to timestamp'''
    return int(time.mktime(
        datetime.datetime.strptime(
            string.replace('+0000 ', ''),
            '%a %b %d %H:%M:%S %Y'
        ).utctimetuple()))


def get_friends():
    screen_name = get_settings().get('screen_name')
    cursor = -1
    friends = set()
    sequence = 0
    while True:
        sequence += 1
        url = '{}/friends/list.json?screen_name={}'.format(PRE, screen_name)
        url += '&count={}'.format(MAX_FRIENDS_PER_REQUEST)
        url += '&cursor={}'.format(cursor)
        logger.info('[%s] Fetching @%s\'s friends: %s', sequence, screen_name, url)
        response = requests.get(url, auth=get_oauth()).json()
        errors = set()
        if 'errors' in response:
            for error in response['errors']:
                errors.add(error['message'])
                logger.error('[twitter][get_friends] Error: %s', error['message'])
            break
        logger.info('[twitter] get_friends -> %s', response)
        new_cursor = response.get('next_cursor')
        friends.update(set(user['screen_name'] for user in response.get('users', [])))
        if not new_cursor or len(friends) >= MAX_TOTAL_FRIENDS or new_cursor == cursor:
            break
        cursor = new_cursor
    logger.info('[twitter] Friends: %s', friends)
    return friends, errors


def get_settings():
    logger.info('[twitter] Getting your settings.')
    url = '{}/account/settings.json'.format(PRE)
    return requests.get(url, auth=get_oauth()).json()


def get_tweets(screen_name):
    last_id = None
    user_tweets = {}
    max_tweets_per_request = 50
    max_total_tweets = 50
    sequence = 0
    while True:
        sequence += 1
        logger.info('[twitter][%s] Getting tweets for @%s', sequence, screen_name)
        url = '{}/statuses/user_timeline.json'.format(PRE)
        url += '?screen_name={}'.format(screen_name)
        url += '&count={}'.format(max_tweets_per_request)
        if last_id:
            url += '&max_id={}'.format(last_id)
        logger.info('[twitter] Fetching %s', url)

        response = requests.get(url, auth=get_oauth())

        if not response:
            logger.info('[twitter] DONE: getting tweets for @%s', screen_name)
            break
        new_tweets = [(t['id_str'], timestamp(t['created_at']), bytearray(t['text'], 'utf-8'))
                      for t in response.json()]
        if not new_tweets:
            logger.info('[twitter] DONE: now new tweets for @%s', screen_name)
            break
        new_last_id = new_tweets[-1][0]
        if new_last_id == last_id or len(user_tweets.get(screen_name, [])) >= max_total_tweets:
            logger.info('[twitter] DONE: getting tweets for @%s', screen_name)
            break
        else:
            last_id = new_last_id
            user_tweets.setdefault(screen_name, [])
            user_tweets[screen_name].extend(new_tweets)
    return user_tweets[screen_name]


def get_rate_limit_status():
    url = '{}/application/rate_limit_status.json'.format(PRE)
    rate_limit_status = requests.get(url, auth=get_oauth()).json()
    logger.info('[twitter] Get rate limit status: %s', rate_limit_status)
    return rate_limit_status
