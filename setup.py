"""Project setup script"""

import re
import ast
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('gfx_qa_tools/__init__.py', 'rb') as f:
	version = str(ast.literal_eval(_version_re.search(
		f.read().decode('utf-8')).group(1)))

setup(
	name='gfx-qa-tools',
	version=version,
	description='gfx-qa-tools project for Linux Graphics team',
	long_description=open('README.md'),
	author='Humberto Israel Perez Rodriguez',
	author_email='humberto.i.perez.rodriguez@intel.com',
	url='https://github.intel.com/linuxgraphics/gfx-qa-tools',
	download_url='https://github.intel.com/linuxgraphics/gfx-qa-tools.git',
	packages=['gfx_qa_tools'],
	license='LICENSE',
	install_requires=[
		'PyYaml',
		'requests',
		'flask',
		'tabulate',
		'paramiko',
		'python-bugzilla'
	],
	extras_require={
		'dev': [
			'tox',
			'flake8',
			'hacking',
			'flake8-import-order',
			'mock',
			'coverage'
		],
	},
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Natural Language :: English',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.5'
	],
)
