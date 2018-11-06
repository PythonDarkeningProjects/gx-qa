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

from __future__ import print_function

import argparse
import gfx_qa_tools.common.bash as bash


class WatchDogCheck(object):
	"""Provide methods for managing watchdogs

	Watchdogs are being used to monitor platforms that are running tests, these
	watchdogs constantly check on platforms to make sure they don't hang. This
	class provides some methods for managing the active watchdogs.
	"""

	def get_wd_list(self):
		"""Prints the list of active watchdogs"""
		# Get the PIDs of active watchdogs
		cmd = (
			"pgrep -af 'watchdog.py' | "
			"awk '{for (I=1;I<=NF;I++) if ($I == \"watchdog.py\") "
			"{print $(I+1) \"-\" $(I+2) \"-\" $1}; }'"
		)
		active_wd = bash.get_output(cmd).split()

		watchdog_list = []
		for wd in active_wd:
			wd_info = wd.split('-')
			raspberry = wd_info[0]
			switch = wd_info[1]
			pid = wd_info[2]
			value = {
				'RaspberryNumber': str(raspberry),
				'switch': str(switch),
				'pid': str(pid)
			}
			watchdog_list.append(value)

		print(watchdog_list)

	def kill_wd(self, pid):
		"""Kills an active watchdog

		:param pid: the pid of the watchdog to be killed
		"""
		print('>>> killing pid: ' + str(pid))
		try:
			bash.get_output(
				'cat /home/shared/suites/.miau | sudo -S kill -9 ' + str(pid))
			print('>>> [' + str(pid) + '] killed successfully')
		except ValueError:
			print('>>> [' + str(pid) + '] failed to kill the pid')

	def menu(self):
		"""Parses the options provided by the user when running the script."""
		parser = argparse.ArgumentParser(
			description='Intel® Graphics for Linux*',
			epilog='https://01.org/linuxgraphics')

		# Define arguments that can be used wit the script
		group = parser.add_mutually_exclusive_group()
		group.add_argument(
			'-g', '--get',
			dest='get_active_wd',
			action='store_true',
			help='Get active watchdog'
		)
		parser.add_argument(
			'--kill',
			help='Kill watchdog'
		)
		parser.add_argument(
			'-v', '--version',
			dest='version',
			action='version',
			version='%(prog)s 1.0'
		)

		# Parse the arguments
		args = parser.parse_args()
		if args.kill:
			self.kill_wd(args.kill)
		elif args.get_active_wd:
			self.get_wd_list()


if __name__ == '__main__':
	WatchDogCheck().menu()
