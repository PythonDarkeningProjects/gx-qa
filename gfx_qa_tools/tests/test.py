"""Base Class for the GFX QA unit and integration tests"""

from contextlib import contextmanager
from io import BytesIO as StringIO
import sys
import unittest


class BaseTestCase(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.BLUE = '\033[94m'
		cls.END = '\033[0m'
		cls.RED = '\033[91m'
		cls.GREEN = '\033[92m'
		cls.CYAN = '\033[96m'

	@contextmanager
	def _captured_output(self):
		new_out, new_err = StringIO(), StringIO()
		old_out, old_err = sys.stdout, sys.stderr
		try:
			sys.stdout, sys.stderr = new_out, new_err
			yield sys.stdout, sys.stderr
		finally:
			sys.stdout, sys.stderr = old_out, old_err

	def _perform(self, bash_function, *args):
		with self._captured_output() as (out, err):
			function_output = bash_function(*args)
		print_output = out.getvalue().strip()
		return function_output, print_output
