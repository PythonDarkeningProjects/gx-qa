"""Unit tests for utils.py"""

import os
from smtplib import SMTPDataError
from smtplib import SMTPRecipientsRefused
import string
import time

from mock import patch

from gfx_qa_tools.common import bash
from gfx_qa_tools.common import utils
from gfx_qa_tools.tests import test


class TestUtils(test.BaseTestCase):

	def _remove_non_ascii(self, unicode_string):
		printable = set(string.printable)
		return filter(lambda x: x in printable, unicode_string)

	# ===============================================
	# Tests for the create_formatted_table() function
	# ===============================================
	def test_create_formatted_table(self):
		headers = ['col1', 'col2']
		content = [['val1', 'val2'], ['val3', 'val4']]
		table = utils.create_formatted_table(headers, content)
		ascii_table = self._remove_non_ascii(table)
		expected_values = ['col1', 'col2', 'val1', 'val2', 'val3', 'val4']
		self.assertEqual(expected_values, ascii_table.split())

	def test_create_formatted_table_with_index(self):
		headers = ['col1', 'col2']
		content = [['val1', 'val2'], ['val3', 'val4']]
		table = utils.create_formatted_table(headers, content, index=True)
		ascii_table = self._remove_non_ascii(table)
		expected_values = [
			'index', 'col1', 'col2', '0', 'val1', 'val2', '1', 'val3', 'val4']
		self.assertEqual(expected_values, ascii_table.split())

	def test_create_formatted_table_bad_input(self):
		headers = 'col1'
		content = 'val1'
		table = utils.create_formatted_table(headers, content)
		ascii_table = self._remove_non_ascii(table)
		expected_values = ['col1', 'val1']
		self.assertEqual(expected_values, ascii_table.split())

	# ===================================
	# Tests for the emailer function
	# ===================================
	@patch.object(utils.smtplib.SMTP, 'sendmail')
	def test_emailer(self, mock_sendmail):
		utils.emailer('tester', ['email1@test.com'], 'my subject', 'test message')
		mock_sendmail.assert_called_once()

	@patch.object(utils.smtplib.SMTP, 'sendmail')
	def test_emailer_recipient_refused(self, mock_sendmail):
		mock_sendmail.side_effect = SMTPRecipientsRefused('')
		_, print_out = self._perform(
			utils.emailer, 'tester', ['email1@test.com'], 'my subject', 'test message')
		mock_sendmail.assert_called_once()
		self.assertEqual(
			'{red}>>> (err) {end}All recipients were refused. Nobody got the mail.'
			.format(red=bash.RED, end=bash.END),
			print_out)

	@patch.object(utils.smtplib.SMTP, 'sendmail')
	def test_emailer_data_error(self, mock_sendmail):
		mock_sendmail.side_effect = SMTPDataError(1, 'No bueno')
		_, print_out = self._perform(
			utils.emailer, 'tester', ['email1@test.com'], 'my subject', 'test message')
		mock_sendmail.assert_called_once()
		self.assertEqual(
			'{red}>>> (err) {end}Unable to send the email:'
			.format(red=bash.RED, end=bash.END),
			print_out)

	# ==============================
	# Tests for the isdir() function
	# ==============================
	@patch('gfx_qa_tools.common.utils.bash.run_command')
	def test_isdir(self, mock_runcommand):
		mock_runcommand.return_value = (0, '')
		existence = utils.isdir('/home/test')
		self.assertTrue(existence)
		mock_runcommand.assert_called_once_with('sudo test -d /home/test')

	@patch('gfx_qa_tools.common.utils.bash.run_command')
	def test_isdir_non_sudo(self, mock_runcommand):
		mock_runcommand.return_value = (0, '')
		existence = utils.isdir('/home/test', sudo=False)
		self.assertTrue(existence)
		mock_runcommand.assert_called_once_with('test -d /home/test')

	@patch('gfx_qa_tools.common.utils.bash.run_command')
	def test_isdir_not_found(self, mock_runcommand):
		mock_runcommand.return_value = (1, '')
		existence = utils.isdir('/home/test')
		self.assertFalse(existence)
		mock_runcommand.assert_called_once_with('sudo test -d /home/test')

	# ==============================
	# Tests for the isfile() function
	# ==============================
	@patch('gfx_qa_tools.common.utils.bash.run_command')
	def test_isfile(self, mock_runcommand):
		mock_runcommand.return_value = (0, '')
		existence = utils.isfile('/home/test')
		self.assertTrue(existence)
		mock_runcommand.assert_called_once_with('sudo test -f /home/test')

	@patch('gfx_qa_tools.common.utils.bash.run_command')
	def test_isfile_non_sudo(self, mock_runcommand):
		mock_runcommand.return_value = (0, '')
		existence = utils.isfile('/home/test', sudo=False)
		self.assertTrue(existence)
		mock_runcommand.assert_called_once_with('test -f /home/test')

	@patch('gfx_qa_tools.common.utils.bash.run_command')
	def test_isfile_not_found(self, mock_runcommand):
		mock_runcommand.return_value = (1, '')
		existence = utils.isfile('/home/test')
		self.assertFalse(existence)
		mock_runcommand.assert_called_once_with('sudo test -f /home/test')

	# ================================================
	# Tests for the wait_for_file_existence() function
	# ================================================
	@patch('gfx_qa_tools.common.utils.os.walk')
	def test_wait_for_file_existence(self, mock_walk):
		mock_walk.return_value = [
			('/foo', ('bar',), ('baz',)),
			('/foo/bar', (), ('spam', 'eggs')),
		]
		file_found = utils.wait_for_file_existence('home/test', 'egg')
		self.assertTrue(file_found)

	@patch('gfx_qa_tools.common.utils.os.walk')
	def test_wait_for_file_existence_not_found(self, mock_walk):
		mock_walk.return_value = [
			('/foo', ('bar',), ('baz',)),
			('/foo/bar', (), ('spam', 'eggs')),
		]
		file_found = utils.wait_for_file_existence('home/test', 'dog', timeout=0.1)
		self.assertFalse(file_found)

	# ==============================
	# Tests for the timer() function
	# ==============================
	def test_timer(self):
		func_out, print_out = self._perform(utils.timer, 'start')
		self.assertEqual(0, func_out)
		self.assertEqual('', print_out)
		time.sleep(0.1)
		func_out, print_out = self._perform(utils.timer, 'stop')
		self.assertIn('elapsed time (0h:0m:0.1', func_out)
		text = (
			'{color}>>> (info) {end}elapsed time (0h:0m:0.1'
			.format(color=self.BLUE, end=self.END))
		self.assertIn(text, print_out)
		pattern = 'elapsed time \(0h:0m:0\.1.?s\)'
		self.assertRegexpMatches(func_out, pattern)

	def test_timer_silent(self):
		func_out, print_out = self._perform(utils.timer, 'start', False)
		self.assertEqual(0, func_out)
		self.assertEqual('', print_out)
		time.sleep(0.1)
		func_out, print_out = self._perform(utils.timer, 'stop')
		self.assertIn('elapsed time (0h:0m:0.1', func_out)
		self.assertIn('', print_out)

	def test_timer_bad_order(self):
		if 'START_TIME' in os.environ:
			del os.environ['START_TIME']
		func_out, print_out = self._perform(utils.timer, 'stop')
		self.assertIsNone(func_out)
		self.assertIn('you need to start the timer first', print_out)
