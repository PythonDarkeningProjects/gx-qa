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
import argparse
from argparse import RawDescriptionHelpFormatter
import os

from gfx_qa_tools.common import bash
from gfx_qa_tools.common import log


class APIManager(object):

	def __init__(self, args):
		# initialize the logger
		self.log_filename = 'api.log'
		self.log_path = '/home/shared/logs/api'

		self.log = log.setup_logging(
			name=self.log_filename, level='debug',
			log_file='{path}/{filename}'.format(
				path=self.log_path, filename=self.log_filename)
		)
		self.attempts = args.attempts
		self.server = 'bifrost.intel.com'
		self.tmux_session_name = 'api-automation'
		self.api_script = 'automation.js'
		self.path_to_api = '/home/gfx/apiAutomation'

	def check_tmux_session(self):
		"""Checks if a tmux session is active

		:return
			- True when the command return a exit status of 0.
			- False when the command return a exit status different of 0.
		"""
		api_tmux_session = os.system('tmux has-session -t {0}'.format(
			self.tmux_session_name))

		if api_tmux_session:
			# this mean that there is not a tmux session for the API
			self.log.warning('no tmux session was found for : {0}'.format(
				self.api_script))
			return False

		self.log.info('a tmux session was found for : {0}'.format(self.api_script))
		return True

	def check_api_process(self):
		"""Checks for the API process

		:return
			- True when the command return a exit status of 0.
			- False when the command return a exit status different of 0.
		"""
		api_process = os.system('pgrep -fan {0}'.format(self.api_script))

		if api_process:
			# this mean that there is not process for the API
			self.log.warning('no process was found for : {0}'.format(self.api_script))
			return False

		self.log.info('a process was found for : {0}'.format(self.api_script))
		return True

	def create_tmux_session(self):
		"""Create a tmux session with a specific name

		:return
			- True when the command return a exit status of 0.
			- False when the command return a exit status different of 0.
		"""
		tmux_session = os.system(
			'tmux new-session -d -s {name}'.format(name=self.tmux_session_name))

		if tmux_session:
			# this mean that the tmux session could not be created
			self.log.warning('the tmux session : ({0}) could not be created'.format(
				self.tmux_session_name))
			return False

		self.log.warning('the tmux session : ({0}) was created successfully'.format(
			self.tmux_session_name))
		return True

	def send_command_to_tmux_session(self, tmux_session, cmd):
		"""Send a command through of a specific tmux session

		:return
			- True when the command return a exit status of 0.
			- False when the command return a exit status different of 0.
		"""
		tmux_command = os.system('tmux send -t {session} "{command}" ENTER'.format(
			session=tmux_session, command=cmd))

		if tmux_command:
			# this mean that the tmux command failed
			self.log.warning('tmux command was failed')
			return False

		self.log.info('tmux command was successfully')
		return True

	def kill_api_process(self):
		"""Kill the current api process id

		:return
			- True when the command return a exit status of 0.
			- False when the command return a exit status different of 0.
		"""
		api_process = bash.get_output('pgrep -fan {0}'.format(self.api_script))

		if not api_process:
			self.log.warning('not process found for : {0}'.format(self.api_script))
			return True

		api_pid = api_process.split()[0]
		output = os.system('kill -9 {0}'.format(api_pid))

		if output:
			self.log.warning('could not kill : {0}'.format(self.api_script))
			return False

		return True

	def check_api(self):
		"""Check if the API is running

		The aim of this function is to check if the api is currently running
		in the server, otherwise this will try to start it in a tmux session.
		"""
		count = 0
		while count < self.attempts:

			if self.check_api_process():
				# this mean that there is process for the API
				if self.check_tmux_session():
					# this mean that there is a tmux session for the API
					self.log.info('the api is running on : {0}'.format(self.server))
					break
				else:
					# this mean that there is not a tmux session for the API
					if self.create_tmux_session():
						# killing current API process
						if self.kill_api_process():
							# initializing the API in the new tmux session created
							if self.send_command_to_tmux_session(
								self.tmux_session_name,
								'cd {path} && nodejs {script}'.format(
									path=self.path_to_api, script=self.api_script)):
								self.log.info('the api is running on : {0}'.format(
									self.server))
								break
							else:
								# the API could not be initialized in the tmux session
								self.log.info('attempt : {0}'.format(count))
								count += 1
								continue
						else:
							# the API process could not be eliminated
							count += 1
							continue
					else:
						# the tmux session could not be created
						self.log.info('attempt : {0}'.format(count))
						count += 1
						continue
			else:
				# this mean that there is not process for the API
				if self.check_tmux_session():
					# initializing the API through a tmux session
					if self.send_command_to_tmux_session(
						self.tmux_session_name,
						'cd {path} && nodejs {script}'.format(
							path=self.path_to_api, script=self.api_script)):
						self.log.info('the api is running on : {0}'.format(
							self.server))
						break
					else:
						# the API could not be initialized in the tmux session
						count += 1
						continue
				else:
					# this mean that there is not a tmux session for the API
					if self.create_tmux_session():
						# initializing the API in the new tmux session created
						if self.send_command_to_tmux_session(
							self.tmux_session_name,
							'cd {path} && nodejs {script}'.format(
								path=self.path_to_api, script=self.api_script)):
							self.log.info('the api is running on : {0}'.format(
								self.server))
							break
						else:
							# the API could not be initialized in the tmux session
							self.log.info('attempt : {0}'.format(count))
							count += 1
							continue
					else:
						# increasing the counter
						self.log.info('attempt : {0}'.format(count))
						count += 1
						continue


def arguments():

	parser = argparse.ArgumentParser(
		formatter_class=RawDescriptionHelpFormatter,
		description='''
	program description:
	(%(prog)s) is a tool for check if the API is running.
	project : https://01.org/linuxgraphics
	repository : https://github.intel.com/linuxgraphics/gfx-qa-tools.git
	maintainer : humberto.i.perez.rodriguez@intel.com''',
		epilog='Intel® Graphics for Linux* | 01.org',
		usage='%(prog)s [options]')
	group1 = parser.add_argument_group(
		'({0}required arguments{1})'
		.format(bash.YELLOW, bash.END))
	group1.add_argument(
		'-a', '--attempts',
		dest='attempts',
		type=int,
		required=True,
		help='attempts to initialize the API')

	args = parser.parse_args()
	APIManager(args).check_api()


if __name__ == '__main__':
	arguments()
