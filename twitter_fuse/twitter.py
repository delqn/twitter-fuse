import requests

from .oauth import get_oauth
from .logger import logger


def get_friends():
    max_total_friends = 5
    max_friends_per_request = 5
    screen_name = get_settings().get('screen_name')
    cursor = -1
    friends = set()
    while True:
        url = 'https://api.twitter.com/1.1/friends/ids.json?screen_name={}'.format(screen_name)
        url += '&count={}'.format(max_friends_per_request)
        url += '&cursor={}'.format(cursor)
        r = requests.get(url, auth=get_oauth())
        response = r.json()
        new_cursor = response.get('next_cursor')
        friends.update(set(response.get('ids', [])))
        if new_cursor and len(friends) < max_total_friends:
            cursor = new_cursor
        else:
            break
    return friends


def get_settings():
    logger.info('Getting your settings.')
    url = 'https://api.twitter.com/1.1/account/settings.json'
    return requests.get(url, auth=get_oauth()).json()


def get_tweets(screen_name):
    last_id = None
    user_tweets = []
    max_tweets_per_request = 50
    max_total_tweets = 50
    while True:
        logger.info('Getting tweets for @%s', screen_name)
        url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
        url += '?screen_name={}'.format(screen_name)
        url += '&count={}'.format(max_tweets_per_request)
        if last_id:
            url += '&max_id={}'.format(last_id)
        logger.info('Fetching %s', url)

        response = requests.get(url, auth=get_oauth())

        if not response:
            logger.info('DONE getting tweets for @%s', screen_name)
            break
        new_tweets = [(t['id_str'], t['created_at'], bytearray(t['text'], 'utf-8'))
                      for t in response.json()]
        new_last_id = new_tweets[-1][0]
        if new_last_id == last_id or len(user_tweets.get(screen_name, [])) >= max_total_tweets:
            logger.info('DONE getting tweets for @%s', screen_name)
            break
        else:
            last_id = new_last_id
            user_tweets.extend(new_tweets)
    return user_tweets


def get_rate_limit_status():
    url = 'https://api.twitter.com/1.1/application/rate_limit_status.json'
    return requests.get(url, auth=get_oauth()).json()
