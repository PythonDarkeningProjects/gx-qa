"""Unit tests for the config module"""

import unittest

import mock

from gfx_qa_tools.config import config


class TestConfig(unittest.TestCase):

	@mock.patch('gfx_qa_tools.config.config.os')
	@mock.patch('gfx_qa_tools.config.config.CONFIG')
	@mock.patch('gfx_qa_tools.config.config.open', create=True)
	def test_config_generator(self, mock_open, mock_config, mock_os):
		mock_os.path.isfile.return_value = True
		mock_config.sections.return_value = ['section1', 'section2']
		config.create_config()
		calls = [mock.call('section1'), mock.call('section2')]
		mock_config.remove_section.assert_has_calls(calls)
		mock_config.add_section.assert_any_call('general')
		mock_config.write.assert_called()

	@mock.patch('gfx_qa_tools.config.config.CONFIG')
	def test_get(self, mock_config):
		mock_config.get.return_value = 'test_option'
		my_val = config.get('section1', 'option1')
		mock_config.get.assert_called_with(
			'section1', 'option1', raw=False, vars=None)
		self.assertEqual('test_option', my_val)

	@mock.patch('gfx_qa_tools.config.config.CONFIG')
	def test_get_with_interpolation(self, mock_config):
		mock_config.get.side_effect = [
			'hello/${section1:option1}/world',
			'test_option',
			'hello/test_option/world']
		config.get('section2', 'option2')
		mock_config.set.assert_called_once_with(
			'section2', 'option2', 'hello/test_option/world')
		# double interpolation
		mock_config.get.side_effect = [
			'hello/${section1:option1}FOO${sec2:opt3}/world',
			'test_option',
			'other_test',
			'hello/test_optionFOOother_test/world']
		config.get('section2', 'option2')
		mock_config.set.assert_called_with(
			'section2', 'option2', 'hello/test_optionFOOother_test/world')

	@mock.patch('gfx_qa_tools.config.config.CONFIG')
	def test_getint(self, mock_config):
		mock_config.get.return_value = '1'
		self.assertEqual(1, config.getint('a', 'b'))

	@mock.patch('gfx_qa_tools.config.config.CONFIG')
	def test_getfloat(self, mock_config):
		mock_config.get.return_value = '1.23'
		self.assertEqual(1.23, config.getfloat('a', 'b'))

	@mock.patch('gfx_qa_tools.config.config.CONFIG')
	def test_config_parser_boolean(self, mock_config):
		mock_config.get.return_value = 'true'
		self.assertEqual(True, config.getboolean('a', 'b'))
