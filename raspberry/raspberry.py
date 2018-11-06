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

import requests

from gfx_qa_tools.common import bash
from common.remote_client import RemoteClient
from gfx_qa_tools.common import log
from gfx_qa_tools.config import config


class ElectricalControlManager(object):
	"""ElectricalControlManager class helps to handle the power control.

	The purpose of this class is to help with the power control of the DUTs
	connected to the automated system.
	"""

	logger = log.setup_logging(
		'raspberry',
		log_file='{0}/raspberry.log'.format(config.get('raspberry', 'log_path')),
		console_log=False
	)

	def __init__(self, **kwargs):
		"""Class builder

		This class builder receives parameters in order to make it portable and
		be able to use it as a module inside of others scripts, the possible
		parameters that this class receives are:

		:param kwargs:
			- raspberry: which is the raspberry number, the possible values are:
				1-4 (int values).
				(mandatory value!)
			- switch: which is the switch number in the automated system, the
				possible values are:
				1-8 for a single switch and 9 for all switches (int values).
			- coldreset: select a single switch or all switches to apply a cold
				reset (turn off and turn on) from a raspberry system, the
				possible values are:
				1-8 for a single switch and 9 for all switches (int values).
			- down: select a single switch or all switches to turn off from a
				raspberry system the possible values are :
				1-8 for a single switch and 9 for all switches (int values).
			- up: select a single switch or all switches to turn on from a
				raspberry system the possible values are :
				1-8 for a single switch and 9 for all switches (int values).
			- console: suppress/enable console output, the possible values are:
				True: for enabling it
				False: for disabling it (useful for automated executions)
				If this option is not send, the default value is None.
			- cutter: turn on and off a usb cutter, the possible values are:
				on: For turning on the USB-Cutter
				off: This will not apply any power action in the USB-Cutter
				If this option is not send, the default value is None.
		"""

		self.raspberry = kwargs.get('raspberry', None)

		if self.raspberry is None:
			raise KeyError('raspberry value can not be empty')

		self.switch = kwargs.get('switch', None)
		self.coldreset = kwargs.get('coldreset', None)
		self.down = kwargs.get('down', None)
		self.up = kwargs.get('up', None)
		self.console = kwargs.get('console', None)
		self.cutter = kwargs.get('cutter', None)
		self.data = requests.get('http://10.219.106.111:2020/getraspberries').json()

	@staticmethod
	def check_raspberry_connection(raspberry_number, raspberry_ip, console=True):
		"""Check the raspberry connection through ping command.

		:param raspberry_number: the raspberry to check.
		:param raspberry_ip: the raspberry ip.
		:param console: print messages in the console.
		"""
		if console:
			bash.message(
				'info',
				'testing connection with (raspberry {number}) ({ip})'
				.format(number=raspberry_number, ip=raspberry_ip), '')
		bash.return_command_status(
			'ping -c 1 {ip} &> /dev/null'.format(ip=raspberry_ip),
			print_messages=console)

	@staticmethod
	def perform_ssh_cmd(raspberry_ip, cmd, **kwargs):
		"""Managing power options in a raspberry.

		:param raspberry_ip: the current raspberry ip address.
		:param cmd: the command to execute in the raspberry.
		:param kwargs: some of the possible values are:
			- gpio: the current gpio of the raspberry.
			- timeout: the timeout for ssh connection.
			- console_output: the possible values are:
				True: enable console output (default option)
				False: suppress console output
				(optional)
		"""
		raspberry_user = 'pi'
		raspberry_password = 'linux'

		timeout = kwargs['timeout'] if 'timeout' in kwargs else 10
		console_output = kwargs.get('console_output', True)

		exit_status, stdout = RemoteClient(
			raspberry_ip, user=raspberry_user, password=raspberry_password
		).run_command(
			'{sudo}{cmd} {gpio}'
			.format(
				sudo='sudo ' if 'gpio' in kwargs else '',
				cmd=cmd,
				gpio=kwargs.get('gpio', ''),
				timeout=timeout))

		if console_output:
			print('>>> (info) stdout ({stdout})'.format(stdout=stdout))

			if exit_status == 0:
				print('DONE')
			elif exit_status == 77:
				print('SKIP')
			else:
				print('FAIL')

	@staticmethod
	def read_clonezilla_file(clonezilla_file):
		"""Read continuously a file

		The aim of this function is to read continuously a clonezilla file in
		order to show the current clonezilla progress from the DUT through
		IEM/terminal.

		:param clonezilla_file: which is the file to read
		"""
		logger = ElectricalControlManager.logger
		logger.info('Reading clonezilla file: {0}'.format(clonezilla_file))

		if os.path.isfile(clonezilla_file):
			os.remove(clonezilla_file)
			logger.info('An old clonezilla file was found and was deleted')

		end_line = 'clonezilla has finished'
		minutes_allowed_to_wait = config.getint(
			'raspberry', 'clonezilla_file_timeout')

		# wait for the file to be created
		print('waiting to read: {0}'.format(clonezilla_file))
		logger.info('waiting to read: {0}'.format(clonezilla_file))

		while True:

			start_time = time.time()
			while not os.path.isfile(clonezilla_file):
				logger.debug(
					'waiting for clonezilla file to exist ({0}s)'
					.format(time.time() - start_time))
				time.sleep(1)
				if time.time() > start_time + (minutes_allowed_to_wait * 60):
					exit_msg = (
						'unable to read {cz_file} after {min} minutes'
						.format(cz_file=clonezilla_file, min=minutes_allowed_to_wait))
					logger.warning(exit_msg)
					sys.exit(exit_msg)

			logger.info('the clonezilla file was found, continuing with the reading')

			with open(clonezilla_file, 'r', buffering=0) as cf:
				file_size = 0
				while True:
					# we need a way to refresh the reference to the file in case it
					# changes (file deleted then re-created), so if at any point
					# this file becomes smaller than it was, in this case means it was
					# deleted and re-created, so we need to start reading from the
					# beginning of the file
					if not os.path.isfile(clonezilla_file):
						# if at one point we cannot read the file break out of
						# this cycle to go to the outer cycle
						break
					logger.debug('file size: {0}'.format(os.stat(clonezilla_file).st_size))
					logger.debug('previous size: {0}'.format(file_size))
					if os.stat(clonezilla_file).st_size < file_size:
						cf.seek(0)
						logger.info('the clonezilla file was re-created, reading from the top')
					where = cf.tell()
					line = cf.readline()
					logger.debug('file pointer: {0}'.format(where))
					file_size = os.stat(clonezilla_file).st_size
					if not line:
						time.sleep(1)
						cf.seek(where)
					else:
						logger.debug('printing line: {0}'.format(line))
						print line,
						# if the printed line is the one we expect as the
						# last line, exit
						if end_line in line:
							logger.info('end line was found, exiting file')
							return

	def manager(self):
		"""Perform specific actions.

		variables:
		- self.args.coldreset:
			this argument perform a cold reset in the specified switch.
			Cold reset mean turn off and then turn on the DUT.
		- self.args.down:
			this argument perform a power off in the specified switch.
		- self.args.up:
			this argument perform power on in the specified switch.
		"""

		gpios = []
		usb_cutter = []
		raspberry_ip = None
		raspberry_python_path = '/home/pi/dev'
		raspberry_cleaware_path = '/home/pi/dev/raspberry/clewarecontrol/cutter.py'

		for element in self.data:
			if self.raspberry == int(element['name'].split()[1].encode()):
				raspberry_ip = element['ip'].encode()
				for item in element['powerSwitches']:
					gpios.append(item['GPIO'].encode())
					usb_cutter.append(item['usbCutter'].encode())

		if self.coldreset:
			self.check_raspberry_connection(
				self.raspberry, raspberry_ip, self.console)
			cmd = ['sudo power -off', 'sudo power -on']

			if self.coldreset != 9:
				gpio = int(self.coldreset) - 1
				gpio = gpios[gpio]
				for argument in cmd:
					self.perform_ssh_cmd(
						raspberry_ip, argument, gpio=gpio, console_output=self.console)
					if argument == cmd[0] and self.cutter:
						# turn on the usb-cutter
						command = 'PYTHONPATH={python_path} python {cleware} ' \
							'-c {cutter_id} -a on'.format(
								python_path=raspberry_python_path,
								cleware=raspberry_cleaware_path,
								cutter_id=usb_cutter[self.coldreset - 1])
						self.perform_ssh_cmd(raspberry_ip, command, console_output=self.console)
					time.sleep(5)

				if self.console and self.cutter:
					self.read_clonezilla_file(os.path.join(
						'/home/shared/raspberry', 'raspberry-0{0}'.format(self.raspberry),
						'switch-0{0}'.format(self.coldreset), 'clonezilla'))
			else:
				for gpio in gpios:
					for argument in cmd:
						self.perform_ssh_cmd(
							raspberry_ip, argument, gpio=gpio, console_output=self.console)
						time.sleep(5)

		elif self.down:

			cmd = 'sudo power -off'

			if self.down != 9:
				gpio = int(self.down) - 1
				gpio = gpios[gpio]
				self.check_raspberry_connection(
					self.raspberry, raspberry_ip, self.console)
				self.perform_ssh_cmd(
					raspberry_ip, cmd, gpio=gpio, console_output=self.console)
			else:
				for gpio in gpios:
					self.perform_ssh_cmd(
						raspberry_ip, cmd, gpio=gpio, console_output=self.console)
					time.sleep(5)

		elif self.up:

			cmd = 'sudo power -on'

			if self.up != 9:
				gpio = int(self.up) - 1
				gpio = gpios[gpio]
				self.check_raspberry_connection(
					self.raspberry, raspberry_ip, self.console)
				self.perform_ssh_cmd(
					raspberry_ip, cmd, gpio=gpio, console_output=self.console)
			else:
				for gpio in gpios:
					self.perform_ssh_cmd(
						raspberry_ip, cmd, gpio=gpio, console_output=self.console)
					time.sleep(5)

		elif self.cutter and self.switch:
			# this part of the code turn on/off the USB-Cutters in the system.
			if self.switch != 9:
				command = 'PYTHONPATH={python_path} python {cleware} ' \
					'-c {cutter_id} -a {cutter_action}'.format(
						python_path=raspberry_python_path,
						cleware=raspberry_cleaware_path,
						cutter_id=usb_cutter[self.switch - 1],
						cutter_action=self.cutter,
						timeout=80)
				self.perform_ssh_cmd(
					raspberry_ip, command, console_output=self.console)
			else:
				for cutter in usb_cutter:
					command = 'PYTHONPATH={python_path} python {cleware} ' \
						'-c {cutter_id} -a {cutter_action}'.format(
							python_path=raspberry_python_path,
							cleware=raspberry_cleaware_path,
							cutter_id=cutter,
							cutter_action=self.cutter,
							timeout=80)
					self.perform_ssh_cmd(
						raspberry_ip, command, console_output=self.console)


def arguments():

	parser = argparse.ArgumentParser(
		formatter_class=RawDescriptionHelpFormatter,
		description='''
	program description:
	(%(prog)s) is a tool for managing the electrical control of the
	(DUTs/USB-cutters) connected to the automated system.
	project : https://01.org/linuxgraphics
	repository : https://github.intel.com/linuxgraphics/gfx-qa-tools.git
	maintainer : humberto.i.perez.rodriguez@intel.com''',
		epilog='Intel® Graphics for Linux* | 01.org',
		usage='%(prog)s [options]')

	# method also accepts a required argument, to indicate that at least one
	# of the mutually exclusive arguments is required
	main_group = parser.add_argument_group(
		'({0}mandatory arguments{1})'
		.format(bash.BLUE, bash.END))
	main_group.add_argument(
		'-r', '--raspberry', dest='raspberry', required=True, type=int,
		choices=[1, 2, 3, 4],
		help='select a raspberry in the automated system')
	group1 = parser.add_argument_group(
		'(cold reset) power control ({0}positional arguments{1})'
		.format(bash.YELLOW, bash.END),
		'manage the electric control of the DUTs connected to the '
		'automated system, this will generated a hard reset in the selected '
		'systems implying turn off and turn on the DUT')
	group1.add_argument(
		'-c', '--coldreset', dest='coldreset', type=int,
		choices=[1, 2, 3, 4, 5, 6, 7, 8, 9],
		help='select a single switch or all switches to apply a cold reset '
		'from a raspberry system (#9 mean all switches)')
	group2 = parser.add_argument_group(
		'(turn off) power control ({0}positional arguments{1})'
		.format(bash.YELLOW, bash.END),
		'manage the electric control of the DUTs connected to the '
		'automated system, this turn off the selected systems')
	group2.add_argument(
		'-d', '--down', dest='down', type=int, choices=[1, 2, 3, 4, 5, 6, 7, 8, 9],
		help='select a single switch or all switches to turn off '
		'from a raspberry system (#9 mean all switches)')
	group3 = parser.add_argument_group(
		'(turn on) power control ({0}positional arguments{1})'
		.format(bash.YELLOW, bash.END),
		'manage the electric control of the DUTs connected to the '
		'automated system, this turns on the selected systems')
	group3.add_argument(
		'-u', '--up', dest='up', type=int, choices=[1, 2, 3, 4, 5, 6, 7, 8, 9],
		help='select a single switch or all switches to turn on '
		'from a raspberry system (#9 mean all switches)')
	group4 = parser.add_argument_group(
		'console output ({0}positional arguments{1})'
		.format(bash.YELLOW, bash.END),
		'enable console output (default is disabled)')
	group4.add_argument(
		'--console', dest='console', action='store_true',
		help='enable console output')
	group5 = parser.add_argument_group(
		'usb-cutter ({0}positional arguments{1})'
		.format(bash.YELLOW, bash.END),
		'perform a power option in a usb-cutter')
	group5.add_argument(
		'--switch', type=int, dest='switch', choices=[1, 2, 3, 4, 5, 6, 7, 8, 9],
		help='select a single switch or all switches (#9 mean all switches)')
	group5.add_argument(
		'--cutter', dest='cutter', choices=['on', 'off'],
		help='turn on/off a USB-Cutter in the automated system')

	args = parser.parse_args()
	ElectricalControlManager(
		raspberry=args.raspberry,
		coldreset=args.coldreset,
		down=args.down,
		up=args.up,
		console=args.console,
		switch=args.switch,
		cutter=args.cutter
	).manager()


if __name__ == '__main__':
	arguments()
