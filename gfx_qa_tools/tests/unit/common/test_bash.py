"""Unit tests for bash.py"""

import subprocess

from mock import call
from mock import patch

from gfx_qa_tools.common import bash
from gfx_qa_tools.tests import test


class TestBash(test.BaseTestCase):

	# =====================================
	# Tests for the get_output() function
	# =====================================

	def test_get_output(self):
		self.assertEqual('hello', bash.get_output('echo "hello"'))

	def test_get_output_print_output(self):
		func_out, print_out = self._perform(
			bash.get_output, 'echo "hello"', True)
		self.assertEqual('hello', func_out)
		self.assertEqual('hello', print_out)

	def test_get_output_bad_command(self):
		func_out, print_out = self._perform(
			bash.get_output, 'bad command', True)
		self.assertEqual('', func_out)
		self.assertEqual('', print_out)

	# ====================================
	# Tests for the run_command() function
	# ====================================

	def test_run_command(self):
		exit_code, output = bash.run_command('echo "hello"')
		self.assertEqual(0, exit_code)
		self.assertEqual('hello', output)

	def test_run_command_bad_command(self):
		exit_code, output = bash.run_command('bad command')
		self.assertEqual(127, exit_code)
		self.assertEqual('/bin/bash: bad: command not found', output)

	# ==============================================
	# Tests for the return_command_status() function
	# ==============================================

	def test_return_command_status(self):
		func_out, print_out = self._perform(
			bash.return_command_status, 'pwd', True)
		self.assertIsNone(func_out)
		self.assertEqual(
			'... [{color}DONE{end}]'
			.format(color=self.GREEN, end=self.END),
			print_out)

	def test_return_command_status_silent(self):
		func_out, print_out = self._perform(
			bash.return_command_status, 'pwd', False)
		self.assertIsNone(func_out)
		self.assertEqual('', print_out)

	def test_return_command_status_bad_command(self):
		self.assertRaises(SystemExit, bash.return_command_status, 'bad')

	# =====================================
	# Tests for the check_output() function
	# =====================================

	def test_check_output(self):
		func_out, print_out = self._perform(
			bash.check_output, 'pwd', 'good', 'bad', True)
		self.assertIsNone(func_out)
		self.assertEqual(
			'{color}>>> (success) {end}good'
			.format(color=self.GREEN, end=self.END),
			print_out)

	def test_check_output_silent(self):
		func_out, print_out = self._perform(
			bash.check_output, 'pwd', 'good', 'bad', False)
		self.assertIsNone(func_out)
		self.assertEqual('', print_out)

	def test_check_output_bad_command(self):
		self.assertRaises(SystemExit, bash.check_output, 'badcommand', 'good', 'bad')

	# ================================
	# Tests for the message() function
	# ================================

	def test_message(self):
		func_out, print_out = self._perform(bash.message, 'ok', 'something')
		self.assertIsNone(func_out)
		self.assertEqual(
			'{}>>> (success) {}something'.format(self.GREEN, self.END), print_out)

	def test_message_empty(self):
		func_out, print_out = self._perform(bash.message, 'err', '')
		self.assertIsNone(func_out)
		self.assertEqual(
			'{}>>> (err) {}'.format(self.RED, self.END), print_out)

	def test_message_invalid_type(self):
		self.assertRaises(ValueError, bash.message, 'invalid_type', 'some text')

	def test_message_info(self):
		func_out, print_out = self._perform(bash.message, 'info', 'hello world!')
		self.assertEqual(
			'{}>>> (info) {}hello world!'.format(self.BLUE, self.END), print_out)

	def test_message_error(self):
		func_out, print_out = self._perform(bash.message, 'err', 'wrong!')
		self.assertEqual(
			'{}>>> (err) {}wrong!'.format(self.RED, self.END), print_out)

	def test_message_with_end_string(self):
		func_out, print_out = self._perform(bash.message, 'statistics', 'foo', 'bar')
		self.assertEqual(
			'{}>>> (data) {}foobar'.format(self.CYAN, self.END), print_out)

	# =====================================
	# Tests for the exit_message() function
	# =====================================
	def test_exit_message(self):
		self.assertRaises(SystemExit, bash.exit_message, 'goodbye')

	# =======================================
	# Tests for the center_message() function
	# =======================================
	def test_center_message(self):
		func_out, print_out = self._perform(
			bash.center_message, 'hello')
		self.assertIsNone(func_out)
		self.assertEqual('hello', print_out)

	# =========================================
	# Tests for the is_process_running function
	# =========================================
	def test_is_process_running_with_pid(self):
		self.assertTrue(bash.is_process_running('1'))

	def test_is_process_running_with_command(self):
		command = 'sleep 10 &'
		subprocess.Popen(
			command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
			shell=True, executable='/bin/bash')
		self.assertTrue(bash.is_process_running('sleep 10'))

	def test_is_process_running_with_non_running_command(self):
		self.assertFalse(bash.is_process_running('random process name'))

	# ===================================
	# Tests for the disable_cups function
	# ===================================
	@patch('gfx_qa_tools.common.bash.get_output')
	@patch('gfx_qa_tools.common.bash.check_output')
	@patch('gfx_qa_tools.common.bash.sys.exit')
	def test_disable_cups(self, mock_exit, mock_check_output, mock_get_output):
		mock_get_output.return_value = 'active'
		bash.disable_cups()
		calls = [
			call(
				'sudo systemctl stop cups',
				'the command was executed successfully',
				'an error was occurred with the last command'),
			call(
				'sudo systemctl disable cups',
				'the command was executed successfully',
				'an error was occurred with the last command'),
			call(
				'sudo systemctl stop cups-browsed',
				'the command was executed successfully',
				'an error was occurred with the last command'),
			call(
				'sudo systemctl disable cups-browsed',
				'the command was executed successfully',
				'an error was occurred with the last command')
		]
		mock_check_output.assert_has_calls(calls)
		mock_exit.assert_called_once()

	@patch('gfx_qa_tools.common.bash.get_output')
	@patch('gfx_qa_tools.common.bash.check_output')
	@patch('gfx_qa_tools.common.bash.sys.exit')
	def test_disable_cups_inactive(
		self, mock_exit, mock_check_output, mock_get_output):
		mock_get_output.return_value = 'inactive'
		bash.disable_cups()
		mock_check_output.assert_not_called()
		mock_exit.assert_not_called()
