#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2017 Humberto Perez <humberto.i.perez.rodriguez@.intel.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  https://docs.python.org/2/library/urllib.html

import argparse
from argparse import RawDescriptionHelpFormatter
import datetime
import json
import os
import shutil
import sys
import urllib

from gfx_qa_tools.common import bash
import requests
import yaml


class Autouploader(object):

	def __init__(self):
		self.this_path = os.path.dirname(os.path.abspath(__file__))
		if os.path.exists(os.path.join(self.this_path, 'config.yml')):
			self.system_user = bash.get_output('whoami')
			self.data = \
				yaml.load(open(os.path.join(self.this_path, 'config.yml')))
			self.suite_list = self.data['testReportCenter']['suiteList']
			self.now = datetime.datetime.now()
			self.current_date = self.now.strftime('%Y-%m-%d')
			r = str(
				requests.get(
					'http://10.64.95.35/api/BugManager/GetCurrentWW').json())\
				.replace('"', '').split('-')
			self.year = r[0]
			self.work_week = 'W' + str(r[1])
		else:
			bash.message('err', '(config.yml) does not exists')
			sys.exit(1)

	def get_software_configuration(self, goal):

		if goal == 'graphic-stack':
			drivers_configuration_file_path = \
				'/home/custom/graphic_stack/packages/easy-bugs'
			kernel_commit_file_path = \
				'/home/custom/kernel/packages/commit_info'

			if os.path.isfile(drivers_configuration_file_path) and \
				os.path.isfile(kernel_commit_file_path):

				if 'xserver' in bash.get_output(
					'cat {drivers} | grep xserver'.format(
						drivers=drivers_configuration_file_path)):
					# in order to avoid that the length of the requested URL
					# exceeds the capacity limit for TestReportCenter server
					# only a few drivers will appears in easy-bugs
					selected_drivers = [
						'xserver', 'mesa', 'drm', 'macros', 'xf86-video-intel',
						'libva', 'intel-vaapi-driver', 'cairo', 'intel-gpu-tools',
						'piglit']
					# creating a new easy-bugs
					with open('/tmp/easy-bugs', 'w') as easy_bugs:
						for driver in selected_drivers:
							output = bash.get_output(
								'cat {drivers} | grep {driver} -A2'.format(
									drivers=drivers_configuration_file_path, driver=driver))
							easy_bugs.write('{0}\n\n'.format(output))
					# moving easy-bugs as easy-bugs.old
					os.rename(
						drivers_configuration_file_path,
						'/home/custom/graphic_stack/packages/easy-bugs.old')
					# copying easy-bugs from /tmp
					shutil.copy('/tmp/easy-bugs', drivers_configuration_file_path)

				drivers = bash.get_output('cat ' + drivers_configuration_file_path)
				kernel = bash.get_output('cat ' + kernel_commit_file_path)
				drivers_header = '_' * 20 + 'Software Information' + '_' * 20
				kernel_header = '_' * 20 + 'Kernel Information' + '_' * 20
				string = \
					drivers_header + '\n' + drivers + '\n\n' + \
					kernel_header + '\n' + kernel
				return string
			else:
				string = \
					bash.get_output(
						'python ../../tests/getdrivers.py -e graphic-stack')
				return string
		elif goal == 'update-tool':
				string = \
					bash.get_output(
						'python ../../tests/getdrivers.py -e update-tool')
				return string

	def uploader(
		self, url, token, platform, suite, release,
		title, file, environment, objective, goal, attachments, comment
	):

		# checking the architecture
		arch = bash.get_output('arch')
		if arch == 'x86_64':
			architecture = '64 bits'
		else:
			architecture = '32 bits'

		# fields for TestReportCenter
		prefix = '\&'
		report = 'report=@' + file
		report_str = '--form ' + report + ' '
		url_str = url + 'auth_token=' + token
		release_version = 'release_version=' + release.replace(' ', '%20')
		target = 'target=' + platform
		testtype = 'testtype=' + urllib.quote_plus(suite)
		test_environment = 'hwproduct=' + urllib.quote_plus(title)
		image = 'image=' + self.year + '-' + self.work_week
		build_id = 'build_id=' + architecture.replace(' ', '%20')
		if comment:
			title_string = \
				urllib.quote_plus(
					'[auto] ' + bash.get_output('uname -r').replace('+', '') +
					' ' + bash.get_output('echo $HOSTNAME') + ' ' + suite +
					' ' + architecture + ' ' + comment)
		else:
			title_string = \
				urllib.quote_plus(
					'[auto] ' + bash.get_output('uname -r').replace('+', '') +
					' ' + bash.get_output('echo $HOSTNAME') + ' ' + suite +
					' ' + architecture)
		title = 'title="' + title_string + '"'
		tested_at = 'tested_at=' + self.current_date
		updated_at = 'updated_at=' + self.current_date
		created_at = 'created_at=' + self.current_date
		objective_txt = 'objective_txt=' + \
			urllib.quote_plus(
				bash.get_output(
					'cat ' +
					os.path.join(
						self.this_path, 'objectives.d', objective + '.obj')))
		environment_txt = 'environment_txt=' + \
			urllib.quote_plus(self.get_software_configuration(goal))
		qa_summary_txt = 'qa_summary_txt=' + \
			urllib.quote_plus(bash.get_output(
				'cat ' + os.path.join(
					self.this_path, 'objectives.d', objective + '.obj')))

		if attachments:
			attachments_str = ''
			file_list = \
				[
					os.path.join(attachments, name) for name in
					os.listdir(attachments) if
					os.path.isfile(os.path.join(attachments, name))
				]

			if len(file_list) == 1:
				attachments_str += '--form attachment=@' + file_list[0] + ' '
			else:
				count = 1
				for item in file_list:
					attachments_str += '--form attachment.' + str(count) + \
						'=@' + item + ' '
					count += 1
			cmd = report_str + attachments_str + url_str
		else:
			cmd = report_str + url_str

		url_list = [
			release_version,
			target,
			testtype,
			test_environment,
			image,
			build_id,
			title,
			tested_at,
			updated_at,
			created_at,
			objective_txt,
			environment_txt,
			qa_summary_txt
		]

		# creating the url
		trc_url = ''
		for item in url_list:
			trc_url += prefix + item

		bash.message('info', 'autoUploader.py v3.1')
		bash.message(
			'info',
			'current environment for TRC is ({0})'.format(environment))
		# ===============================================
		# uncomment it to view the command line for curl
		# ===============================================
		# bash.message(
		# 	'cmd',
		# 	'curl -k --form ' + report + ' ' + url + 'auth_token=' + token +
		# 	trc_url)
		bash.message(
			'info',
			'uploading file (' + os.path.basename(file) +
			') to TestReportCenter')
		bash.message(
			'info',
			'_________________' + bash.CYAN + 'Transfer rate' + bash.END +
			'_________________')

		# subprocess does not capture the STDERR of curl, for that reason
		# is needed a file to capture it.
		curl_stderr_file = '/tmp/autouploader.log'
		output = bash.get_output(
			'curl -k {0}{1} 2>&1 > {2}'.format(cmd, trc_url, curl_stderr_file))

		if os.path.exists(curl_stderr_file) and \
			not os.stat(curl_stderr_file).st_size == 0:

			# the following conditions indicates that the TRC is down
			conditions_for_trc_down = [
				'An error occurred' in bash.get_output(
					'cat {0}'.format(curl_stderr_file)),
				'port 443: No route to host' in bash.get_output(
					'cat {0}'.format(curl_stderr_file)),
			]

			if True in conditions_for_trc_down:
				bash.get_output('cat {0}'.format(curl_stderr_file), True)
				bash.message('err', 'Oops! An unknown error occurred')
				bash.message(
					'info',
					'looks like that TestReportCenter for (' + environment +
					') environment is down')
				bash.message(
					'info',
					'please check if the site (' + bash.YELLOW +
					url.replace('/api/import?', '') + bash.END + ') is online')
				sys.exit(1)
			elif 'Unknown CSV delimiter' in \
				bash.get_output('cat {0}'.format(curl_stderr_file)):
				bash.message('err', 'Oops! An error occurred')
				bash.message(
					'warn',
					'the file ({0}) has unknown CSV format'.format(file))
				sys.exit(1)
			elif 'Cannot find project_to_product_id' in \
				bash.get_output('cat {0}'.format(curl_stderr_file)):
				bash.message('err', 'Oops! An error occurred')
				bash.message(
					'warn',
					'the platform ({0}) is not in ({1}) '
					.format(platform, release))
				bash.message(
					'info',
					'if this is not a human error, please verify it with the '
					'TRC admins\n'
					'- humberto.i.perez.rodriguez@intel.com\n'
					'- ricardo.vega@intel.com')
				sys.exit(1)

			elif 'The length of the requested URL exceeds the capacity limit' in \
				bash.get_output('cat {0}'.format(curl_stderr_file)):
				bash.message('err', 'Oops! An error occurred')
				bash.message(
					'warn',
					'The length of the requested URL exceeds the capacity limit this server '
					'If you think this is a server error, please contact to: '
					'qa_reports@otcqarpt-stg.ostc.intel.com')
				sys.exit(1)

		# this print the stdout from curl command
		print(output)
		dictionary_from_trc = bash.get_output('cat {0}'.format(curl_stderr_file))
		response = json.loads(dictionary_from_trc)

		if int(response['ok']) == 1:
			bash.message(
				'info',
				'_______________________________________________\n')
			bash.message(
				'info',
				'the report was uploaded' + bash.GREEN +
				' successfully' + bash.END)
			bash.message(
				'info',
				'You can view your report here : (' + bash.YELLOW +
				response['url'] + bash.END + ')')
			bash.message(
				'info', 'project    : https://01.org/linuxgraphics')
			bash.message(
				'info',
				'maintainer : humberto.i.perez.rodriguez@intel.com')
			os.system('echo ' + response['url'] + '> /tmp/trc2.log')
			os.system(
				'echo ' + response['url'] + '> ' +
				os.path.join('/home', self.system_user, 'trc2.log'))
			sys.exit(0)
		elif int(response['ok']) == 0:
			bash.message(
				'info',
				'_______________________________________________\n')
			bash.message('err', 'an error was occurred')
			bash.message('info', output)
			bash.message(
				'info',
				'please report this issue to the maintainer')
			bash.message(
				'info',
				'maintainer : humberto.i.perez.rodriguez@intel.com')
			sys.exit(1)
		else:
			bash.message(
				'info',
				'_______________________________________________\n')
			bash.message('err', 'unhandled error')
			bash.message('info', output)
			sys.exit(1)

	def arguments(
		self, platform, suite, release, title, file, environment,
		objective, goal, attachments, comment
	):

		if environment == 'production':
			url = self.data['testReportCenter']['production']['url']
			token = self.data['testReportCenter']['production']['token']
			platformList = \
				self.data['testReportCenter']['production']['platformList']
			releaseList = \
				self.data['testReportCenter']['production']['releaseList']
		elif environment == 'sandbox':
			url = self.data['testReportCenter']['sandbox']['url']
			token = self.data['testReportCenter']['sandbox']['token']
			platformList = \
				self.data['testReportCenter']['sandbox']['platformList']
			releaseList = \
				self.data['testReportCenter']['sandbox']['releaseList']

		# validating the platform
		if platform not in platformList:
			bash.message(
				'err',
				'({0}) is not recognized as platform, please use the following'
				' platforms'.format(platform))
			for element in platformList:
				print(element)
			sys.exit(1)

		# validating the suite
		m_key = False
		for key, value in self.suite_list.iteritems():
			if suite in value:
				m_key = True
			else:
				continue

		if not m_key:
			bash.message(
				'err',
				'({0}) is not recognized as suite, please use the following '
				'suites'.format(suite))
			for key, value in self.suite_list.iteritems():
				bash.message(
					'info',
					'for ({text}) use --> {lst} as suite argument'
					.format(text=key, lst=value))
			sys.exit(1)

		# validating the release
		if release not in releaseList:
			bash.message(
				'err',
				'({0}) is not recognized as release, please use the following '
				'releases for ({1}) environment'.format(release, environment))
			r_list = ''
			for r in releaseList:
				r_list += "'" + r + "' "
			print(r_list)
			sys.exit(1)

		# title does not needs to be validated

		# validating the file to upload
		valid_extensions_for_trc = ['csv', 'xml']
		if not os.path.isfile(file):
			bash.message('err', '({0}) does not exists'.format(file))
			sys.exit(1)
		if os.stat(file).st_size == 0:
			bash.message('err', '({0}) is empty'.format(file))
			sys.exit(1)

		if not os.path.splitext(file)[1][1:].strip() in \
			valid_extensions_for_trc:
			bash.message(
				'err',
				'({0}) does not has the correct extension for '
				'TestReportCenter'.format(file))
			bash.message(
				'info',
				'valid extensions for TestReportCenter are --> {lst}'
				.format(lst=valid_extensions_for_trc))
			sys.exit(1)

		# validating the attachments folder to upload
		if attachments:
			if not os.path.exists(attachments):
				bash.message(
					'err', '({0}) folder does not exists'.format(attachments))
				sys.exit(1)
			else:
				if len([
					name for name in os.listdir(attachments) if
					os.path.isfile(os.path.join(attachments, name))]) == 0:
					bash.message(
						'err',
						'there is not files on ({0}) folder'
						.format(attachments))
					sys.exit(1)

		# uploading report
		self.uploader(
			url,
			token,
			platform,
			suite,
			release,
			title,
			file,
			environment,
			objective,
			goal,
			attachments,
			comment
		)


class Arguments(object):

	parser = \
		argparse.ArgumentParser(
			formatter_class=RawDescriptionHelpFormatter,
			description='''
	program description:
	(%(prog)s) is a tool for upload reports to TestReportCenter
	project : https://01.org/linuxgraphics
	maintainer : humberto.i.perez.rodriguez@intel.com''',
			epilog='Intel® Graphics for Linux* | 01.org',
			usage='%(prog)s [options]')
	parser.add_argument('--version', action='version', version='%(prog)s 3.0')
	parser.add_argument(
		'-p',
		'--platform',
		dest='platform',
		required=True,
		help='set a platform for TestReportCenter ' + bash.YELLOW +
		'(required)' + bash.END)
	parser.add_argument(
		'-s',
		'--suite',
		dest='suite',
		required=True,
		help='set a suite for TestReportCenter ' + bash.YELLOW +
		'(required)' + bash.END)
	parser.add_argument(
		'-r',
		'--release',
		dest='release',
		required=True,
		help='set a release for TestReportCenter ' + bash.YELLOW +
		'(required)' + bash.END)
	parser.add_argument(
		'-t',
		'--title',
		dest='title',
		required=True,
		help='set a title for TestReportCenter ' + bash.YELLOW +
		'(required)' + bash.END)
	parser.add_argument(
		'-f',
		'--file',
		dest='file',
		required=True,
		help='file for upload to TestReportCenter ' + bash.YELLOW +
		'(required)' + bash.END)
	parser.add_argument(
		'-e',
		'--environment',
		dest='environment',
		required=True,
		choices=['production', 'sandbox'],
		help='set a environment for TestReportCenter ' + bash.YELLOW +
		'(required)' + bash.END)
	parser.add_argument(
		'-o',
		'--objective',
		dest='objective',
		required=True,
		choices=['installer', 'intel-gpu-tools', 'quarterly-release'],
		help='set a test objective  for TestReportCenter ' + bash.YELLOW +
		'(required)' + bash.END)
	parser.add_argument(
		'-g',
		'--goal',
		dest='goal',
		required=True,
		choices=['graphic-stack', 'update-tool'],
		help='set the current graphic environment in order to get the '
		'drivers for TestReportCenter ' + bash.YELLOW + '(required)' + bash.END)
	parser.add_argument(
		'-a',
		'--attachments',
		dest='attachments',
		required=False,
		help='attachments folder for TestReportCenter ' + bash.BLUE +
		'(optional)' + bash.END)
	parser.add_argument(
		'-c',
		'--comment',
		dest='comment',
		required=False,
		help='add a comment for the report title in TestReportCenter ' +
		bash.BLUE + '(optional)' + bash.END)

	args = parser.parse_args()

	# validating arguments
	Autouploader().arguments(
		args.platform,
		args.suite,
		args.release,
		args.title,
		args.file,
		args.environment,
		args.objective,
		args.goal,
		args.attachments,
		args.comment
	)


if __name__ == '__main__':
	Arguments()
