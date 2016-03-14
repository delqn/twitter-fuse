import unittest

from . import mathematica

TWEETS = ['Hello', 'Hi', 'How are you']


class ConfigTest(unittest.TestCase):
    def make_notebook_test(self):
        with open('test_data/mathematica.nb', 'r') as f:
            notebook_rows = mathematica.make_notebook(TWEETS).split('\n')
            expected_rows = f.read().split('\n')
            self.maxDiff = None
            self.assertEqual(notebook_rows, expected_rows)
