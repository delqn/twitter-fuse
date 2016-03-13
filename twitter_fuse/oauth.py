import requests
import urlparse

from requests_oauthlib import OAuth1

from .config import get_config


def _request_token():
    conf = get_config()
    oauth = OAuth1(conf['consumer_key'], client_secret=conf['consumer_secret'])
    response = requests.post(url=conf['request_token_url'], auth=oauth)
    credentials = urlparse.parse_qs(response.content)
    return credentials.get('oauth_token')[0], credentials.get('oauth_secret')[0]


def _authorize():
    conf = get_config()
    resource_owner_key, resource_owner_secret = _request_token()
    authorize_url = conf['authorize_url'] + resource_owner_key
    print 'Visit this link and authorize: ' + authorize_url
    verifier = raw_input('Paste verifier: ')
    return OAuth1(
        conf['consumer_key'],
        client_secret=conf['consumer_secret'],
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier)


def oauth_token_and_secret():
    conf = get_config()
    oauth = _authorize()
    response = requests.post(url=conf['access_token_url'], auth=oauth)
    credentials = urlparse.parse_qs(response.content)
    token = credentials.get('oauth_token')[0]
    secret = credentials.get('oauth_secret')[0]
    return token, secret


def get_oauth():
    conf = get_config()
    oauth = OAuth1(
        conf['consumer_key'],
        client_secret=conf['consumer_secret'],
        resource_owner_key=conf['oauth_token'],
        resource_owner_secret=conf['oauth_secret'])
    return oauth
