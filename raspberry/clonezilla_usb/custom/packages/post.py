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

import os
import sys
import requests
import yaml

from time import sleep
from gfx_qa_tools.common import bash


class Displays(object):

	def __init__(self):
		self.config_file = '/home/custom/config.yml'
		self.url = 'http://bifrost.intel.com:2020/watchdog'
		self.distro = \
			bash.get_output(
				'lsb_release -d | awk \'{print $2 " " $3}\'').decode('utf-8')
		self.codename = \
			bash.get_output(
				'lsb_release -c | awk \'{print $2}\'').decode('utf-8')
		self.full_distro = self.distro + ' (' + self.codename + ')'
		self.networking_service = \
			bash.get_output(
				'systemd-analyze blame | grep networking.service | '
				'awk \'{print $1}\'').decode('utf-8')

	def post_to_watchdog(self, displays_dictionary):
		"""Sent posts to watchdog database

		Args:
			displays_dictionary(dict) : the list of the displays attached to
			the DUT.

		This function allows to post a dictionary to watchdog database
		that contains the displays attached to the DUT in a real time
		"""

		retries = 0
		while retries < 11:
			try:
				requests.post(self.url, json=displays_dictionary)
				bash.message('ok', 'post was sent to database')
				break
			except requests.exceptions.ConnectionError:
				retries += 1
				bash.message(
					'warn', 'connection refused with database')
				bash.message(
					'info', 'attempt (' + str(retries) + ')')

				if retries == 10:
					bash.message(
						'err', 'could not connect to database')
					sys.exit(1)
				sleep(10)

	def get_data(self):
		"""Grab data from the DUT

		Creates a dictionary with the following information :
		- with the info from config.yml located into /home/custom
		- with the displays attached the the DUT reading i915_display_info
		in order to send a post to watchdog database.
		"""

		if os.path.exists(self.config_file):
			bash.message(
				'info', '(' + os.path.basename(self.config_file) + ') exists')
			data = yaml.load(open(self.config_file))
			default_package = data['suite_conf']['default_package']
			raspberry_number = data['raspberry_conf']['raspberry_number']
			raspberry_power_switch = \
				data['raspberry_conf']['raspberry_power_switch']
			kernel_branch = data['suite_conf']['kernel_branch']
			kernel_commit = data['suite_conf']['kernel_commit']
			gfx_stack_code = data['suite_conf']['gfx_stack_code']
			dut_hostname = data['dut_conf']['dut_hostname']
			dut_static_ip = data['dut_conf']['dut_static_ip']
			grub_parameters = data['dut_conf']['grub_parameters']
			guc = data['firmwares']['guc']
			huc = data['firmwares']['huc']
			dmc = data['firmwares']['dmc']

			# Getting the displays attached to the DUT
			displays_attached = \
				bash.get_output(
					"sudo cat /sys/kernel/debug/dri/0/i915_display_info "
					"| grep \"^connector\" | grep "
					"-we \"connected\" | awk -F\"type \" '{print $2}' | "
					"awk '{print $1}' | sed 's/,//g'").decode('utf-8').split()

			displays_dict = dict()
			displays_dict['attachedDisplays'] = {}

			for display in displays_attached:
				displays_dict['attachedDisplays'][display] = 'active'

			bash.message('info', 'default_package (' + default_package + ')')

			data_out = {
				'RaspberryNumber': raspberry_number,
				'PowerSwitchNumber': raspberry_power_switch,
				'Suite': default_package,
				'Status': 'online',
				'DutHostname': dut_hostname,
				'Distro': self.full_distro,
				'DutIP': dut_static_ip,
				'KernelBranch': kernel_branch,
				'KernelCommit': kernel_commit,
				'GfxStackCode': gfx_stack_code,
				'GrubParameters': grub_parameters,
				'guc': guc,
				'huc': huc,
				'dmc': dmc,
				'networking-service': self.networking_service}

			# Adding the current displays
			data_out.update(displays_dict)
			bash.message('info', 'printing dictionary ...')
			print(data_out)

			bash.message('info', 'sending post to database')
			self.post_to_watchdog(data_out)

		else:
			bash.message(
				'err',
				'(' + os.path.basename(self.config_file) + ') does not exists')
			sys.exit(1)


if __name__ == '__main__':
	Displays().get_data()
