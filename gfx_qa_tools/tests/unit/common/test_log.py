"""Unit tests for the log module"""

import os
import unittest

from mock import patch

from gfx_qa_tools.common import log


class TestLog(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.logger_name = 'test_logger'
		cls.common_library = 'common'
		cls.stable_package = 'gfx_qa_tools'
		cls.log_file = 'test.log'
		cls.error_file = 'test.error.log'

	@patch('gfx_qa_tools.common.log.logging')
	def test_setup_logging_using_config(self, mock_logging):
		unittests_path = os.path.dirname(__file__)
		root_path = os.path.abspath(
			os.path.join(unittests_path, os.pardir, os.pardir, os.pardir, os.pardir))
		config_file = os.path.join(root_path, 'conf', 'logging.yaml')
		log.setup_logging_using_config(self.logger_name, config_file)
		mock_logging.getLogger.assert_called_with(self.logger_name)
		mock_logging.config.dictConfig.assert_called()
		call_arguments = mock_logging.config.dictConfig.call_args[0][0]
		self.assertIn('loggers', call_arguments)
		self.assertIn('formatters', call_arguments)
		self.assertIn('handlers', call_arguments)
		self.assertIn('root', call_arguments)
		self.assertIn('disable_existing_loggers', call_arguments)

	@patch('gfx_qa_tools.common.log.logging')
	def test_setup_logging_with_default_values(self, mock_logging):
		# call the function under test
		logger = log.setup_logging(self.logger_name)

		# verify two handlers are getting added for logging to files
		# and one is getting added for logging to the console
		logger.addHandler.assert_any_call(mock_logging.StreamHandler())
		logger.addHandler.assert_any_call(
			mock_logging.handlers.RotatingFileHandler())
		logger.addHandler.assert_any_call(
			mock_logging.handlers.RotatingFileHandler())
		mock_logging.handlers.RotatingFileHandler.assert_any_call(
			'gfx.log', maxBytes=10485760, backupCount=10)
		mock_logging.handlers.RotatingFileHandler.assert_any_call(
			'gfx.error.log', maxBytes=10485760, backupCount=10)
		# verify loggers are getting created (no root logger)
		mock_logging.getLogger.assert_any_call(self.logger_name)
		mock_logging.getLogger.assert_any_call(self.common_library)
		mock_logging.getLogger.assert_any_call(self.stable_package)
		# verify log level defaults to INFO
		logger.setLevel.assert_called_with(mock_logging.INFO)

	@patch('gfx_qa_tools.common.log.logging')
	def test_setup_logging_with_log_file(self, mock_logging):
		log.setup_logging(self.logger_name, log_file=self.log_file)

		mock_logging.handlers.RotatingFileHandler.assert_any_call(
			self.log_file, maxBytes=10485760, backupCount=10)
		mock_logging.handlers.RotatingFileHandler.assert_any_call(
			self.error_file, maxBytes=10485760, backupCount=10)

	@patch('gfx_qa_tools.common.log.logging')
	def test_setup_logging_formatter(self, mock_logging):
		log.setup_logging(self.logger_name)

		mock_logging.Formatter.assert_called_once_with(
			'%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	@patch('gfx_qa_tools.common.log.logging')
	def test_setup_logging_with_no_console(self, mock_logging):
		logger = log.setup_logging(self.logger_name, console_log=False)

		self.assertRaises(
			AssertionError, logger.addHandler.assert_any_call,
			mock_logging.StreamHandler())

	@patch('gfx_qa_tools.common.log.logging')
	def test_setup_logging_with_root_logger(self, mock_logging):
		log.setup_logging(self.logger_name, root=True)

		self.assertRaises(
			AssertionError, mock_logging.getLogger.assert_called_with,
			self.logger_name)
		self.assertRaises(
			AssertionError, mock_logging.getLogger.assert_called_with,
			self.common_library)
		mock_logging.getLogger.assert_called_with()

	@patch('gfx_qa_tools.common.log.logging')
	def test_setup_logging_with_different_levels(self, mock_logging):
		logger = log.setup_logging(self.logger_name, level='debug')
		logger.setLevel.assert_called_with(mock_logging.DEBUG)
		logger = log.setup_logging(self.logger_name, level='info')
		logger.setLevel.assert_called_with(mock_logging.INFO)
		logger = log.setup_logging(self.logger_name, level='warn')
		logger.setLevel.assert_called_with(mock_logging.WARN)
		logger = log.setup_logging(self.logger_name, level='error')
		logger.setLevel.assert_called_with(mock_logging.ERROR)
		logger = log.setup_logging(self.logger_name, level='critical')
		logger.setLevel.assert_called_with(mock_logging.CRITICAL)
		logger = log.setup_logging(self.logger_name, level='notset')
		logger.setLevel.assert_called_with(mock_logging.NOTSET)
		logger = log.setup_logging(self.logger_name, level='')
		logger.setLevel.assert_called_with(mock_logging.INFO)


if __name__ == '__main__':
	unittest.main()
