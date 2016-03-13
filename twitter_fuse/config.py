import ConfigParser

from .logger import logger

CONFIG_FILE = None
SECTION = None
conf = None


def get_config(config_file=None, section=None):
    global conf
    global CONFIG_FILE, SECTION
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
        config = ConfigParser.ConfigParser()
        config.read(CONFIG_FILE)

        conf_keys = (
            'request_token_url', 'authorize_url', 'access_token_url',
            'consumer_key', 'consumer_secret',
            'oauth_token', 'oauth_secret')
        conf = {key: config.get(SECTION, key) for key in conf_keys}
    return conf
