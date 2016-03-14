import unittest

from .logger import logger


class LoggerTest(unittest.TestCase):
    def log_test(self):
        logger.info('This should work')
        logger.warn('This should work too')
        logger.debug('This should work as well')
        logger.error('This should work, yup!')
