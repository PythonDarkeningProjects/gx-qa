"""Unit tests for utilities.py"""

import os
import unittest

from common import network as net_utils


class TestUtilities(unittest.TestCase):

	def test_get_ip(self):
		ip = net_utils.get_ip()
		self.assertRegexpMatches(ip, '(?:\d{1,3}\.){3}\d{1,3}')

	def test_setup_sedline_connection(self):
		net_utils.set_proxy('192.168.195.78')
		self.assertEqual(os.environ.get('http_proxy'), None)

	def test_setup_internal_connection(self):
		net_utils.set_proxy('10.0.0.102')
		self.assertEqual(
			os.environ.get('http_proxy'), 'http://proxy.fm.intel.com:911')
