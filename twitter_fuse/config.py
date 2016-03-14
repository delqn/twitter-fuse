import ConfigParser

from .logger import logger

CONFIG_FILE = None
SECTION = None
conf = None


def get_config(config_file=None, section=None):
    global CONFIG_FILE, SECTION, conf
    if config_file:
        CONFIG_FILE = config_file
    if section:
        SECTION = section

    if not CONFIG_FILE or not SECTION:
        raise ValueError()

    if not CONFIG_FILE:
        logger.exception('Config not initialized')
        raise ValueError()
    if not conf:
        config = ConfigParser.ConfigParser(allow_no_value=True)
        config.read(CONFIG_FILE)

        conf_keys = (
            'request_token_url', 'authorize_url', 'access_token_url',
            'consumer_key', 'consumer_secret',
            'oauth_token', 'oauth_secret')
        conf = {key: config.get(SECTION, key) for key in conf_keys}
    return conf


def store_oauth(oauth_token, oauth_secret):
    global conf
    _config = ConfigParser.RawConfigParser(allow_no_value=True)
    _config.read(CONFIG_FILE)
    _config.set(SECTION, 'oauth_token', oauth_token)
    _config.set(SECTION, 'oauth_secret', oauth_secret)
    with open(CONFIG_FILE, 'wb') as configfile:
        print 'Writing to {}'.format(configfile)
        _config.write(configfile)
    conf = get_config()
