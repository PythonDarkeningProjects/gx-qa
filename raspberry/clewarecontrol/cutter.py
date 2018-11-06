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
import sys
import time

from gfx_qa_tools.common import bash


class ClewareControl(object):

	def __init__(self, args):
		"""Class constructor

		:param args: args contains the following :
			- args.cutter, which is the usb cutter serial number.
			- args.action, which is the action to perform.
		:arguments
			- self.binary, is the binary that handle the usb-cutters.
			- self.retries, is the total amount of retries if this script found
				a failure during the execution.
			- self.sleep, is the wait time between retries.
		"""
		self.args = args
		self.binary = 'clewarecontrol'
		self.retries = 20
		self.sleep = 3

		if self.args.action == 'on':
			self.turn_on()
		else:
			self.turn_off()

	def cmd(self, action):
		"""Execute a command for turn on/off a usb cutter

		:return a number with the current status of the command executed.
			0 -> for pass state.
			any other number for a failure.
		"""
		return os.system(
			'sudo {binary} -d {usb_cutter} -c 1 -as {action} 2>&1 > /dev/null'
			.format(
				binary=self.binary, usb_cutter=self.args.cutter, action=action))

	def attempts(self, action):

		if self.cmd(action) != 0:
			print('FAIL')
			flag = True

			while flag:
				for iteration in range(0, self.retries):
					counter = iteration + 1
					print(
						'attempt number {counter}/{retries}'
						.format(counter=counter, retries=self.retries))
					time.sleep(self.sleep)

					if iteration == self.retries - 1:
						print('FAIL')
						flag = False

					if self.cmd(action) == 0:
						print('DONE')
						flag = False
						break
					else:
						print('FAIL')
						continue
		else:
			print('DONE')
			sys.exit(0)

	def turn_on(self):
		"""turn on a usb cutter with the serial number"""
		print('turning on usb-cutter: {0}'.format(self.args.cutter))
		self.attempts('0 0')

	def turn_off(self):
		"""turn off a usb cutter with the serial number"""
		print('turning off usb-cutter: {0}'.format(self.args.cutter))
		self.attempts('0 1')


def arguments():
	parser = argparse.ArgumentParser(
		formatter_class=RawDescriptionHelpFormatter,
		description='''
	program description:
	(%(prog)s) is a tool to handle the usb-cutters connected to the raspberry
	system.
	project : https://01.org/linuxgraphics
	maintainer : humberto.i.perez.rodriguez@intel.com''',
		epilog='Intel® Graphics for Linux* | 01.org',
		usage='%(prog)s [options]')

	parser.add_argument(
		'--version', action='version', version='%(prog)s 1.0')
	group = parser.add_argument_group(
		'{0}mandatory arguments{1}'.format(bash.BLUE, bash.END))
	group.add_argument(
		'-c', '--cutter',
		dest='cutter',
		required=True,
		help='usb cutter serial')
	group.add_argument(
		'-a', '--action',
		dest='action',
		required=True,
		choices=['on', 'off'],
		help='set the output folder')

	args = parser.parse_args()
	ClewareControl(args)


if __name__ == '__main__':
	arguments()
