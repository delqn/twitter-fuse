import datetime
import requests
import time

from .oauth import get_oauth
from .logger import logger


PRE = 'https://api.twitter.com/1.1'
TOTAL_FRIENDS = 500
FRIENDS_PER_REQUEST = 200
TWEETS_PER_FRIEND = 3500
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


def _process_get_tweets_response(url):
    response = requests.get(url, auth=get_oauth())
    if not response:
        raise ValueError()
    _new = ((t['id_str'], t['created_at'], t['text']) for t in response.json())
    return [(tid, timestamp(tdate), bytearray(txt, 'utf-8')) for tid, tdate, txt in _new]


def _fill_back(screen_name):
    max_id = None
    static_url = '{}/statuses/user_timeline.json?screen_name={}&count={}'.format(
        PRE, screen_name, TWEETS_PER_REQUEST)
    user_tweets = []
    while len(user_tweets) < TWEETS_PER_FRIEND:
        url = static_url + ('&max_id={}'.format(max_id) if max_id else '')
        logger.info('[twitter] Getting tweets for @%s via %s', screen_name, url)
        try:
            new_tweets = _process_get_tweets_response(url)
        except ValueError:
            break
        new_max_id = min(x[0] for x in new_tweets)
        if new_max_id == max_id:
            break
        max_id = new_max_id
        user_tweets.extend(new_tweets)
    return user_tweets


def _fill_up(screen_name, since_tweet_id):
    since_id = since_tweet_id
    static_url = '{}/statuses/user_timeline.json?screen_name={}&count={}'.format(
        PRE, screen_name, TWEETS_PER_REQUEST)
    user_tweets = []
    while True:
        url = static_url + '&since_id={}'.format(since_id)
        logger.info('[twitter] Fetching new tweets for @%s via %s', screen_name, url)
        try:
            new_tweets = _process_get_tweets_response(url)
            if not new_tweets:
                break
        except ValueError:
            break
        since_id = max(x[0] for x in new_tweets)
        user_tweets.extend(new_tweets)
    return user_tweets


def get_tweets_for(screen_name, since_tweet_id=None):
    if since_tweet_id:
        return _fill_up(screen_name, since_tweet_id)
    else:
        return _fill_back(screen_name)


def get_rate_limit_status():
    url = '{}/application/rate_limit_status.json'.format(PRE)
    rate_limit_status = requests.get(url, auth=get_oauth()).json()
    logger.info('[twitter] Get rate limit status: %s', rate_limit_status)
    return rate_limit_status
