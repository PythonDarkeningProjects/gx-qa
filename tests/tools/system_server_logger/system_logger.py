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

from gfx_qa_tools.common import bash
from gfx_qa_tools.common import utils


def send_email(remote_username, machine_logged, remote_user_ip):
	"""Send a email notification

	:param remote_username: the remote user name
	:param machine_logged: the machine what is logged
	:param remote_user_ip: the remote ip what is logged
	"""

	user_info = bash.get_output('id {0}'.format(remote_username)).replace(
		' ', '\n')
	sender = 'bifrost.intel.com@noreply'
	mailing_list = 'humberto.i.perez.rodriguez@intel.com'
	subject = 'new ssh connection detected of: {0}'.format(remote_username)
	message = '''

	A new ssh connection was detected on bifrost, please see the details below:

	{detail_info}

	machine logged : {machine}
	ip logged      : {ip}
	'''.format(
		detail_info=user_info,
		machine=machine_logged,
		ip=remote_user_ip
	)

	utils.emailer(
		sender,
		mailing_list,
		subject,
		message,
		silent=True
	)


def banner_sys_admin():
	"""Returns a banner"""

	banner = '''
+-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+
|w|e|l|c|o|m|e| |s|y|s|-|a|d|m|i|n|
+-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+
	'''
	return banner


def check_new_ssh_connection():
	"""Checks for a new ssh connection in the system

	every new ssh session detected in the system, this funcion will sent a email
	notification.
	"""
	server = 'bifrost.intel.com'
	remote_user_ip = os.environ['SSH_CLIENT'].split()[0]
	remote_username = bash.get_output('whoami')
	machine_logged = bash.get_output('nslookup -timeout=10 {0}'.format(
		remote_user_ip)).split()[-1]

	banner = '''
=======================================================
- session started from : {ip}
- logging as           : {username}
- machine logged       : {machine_logged}
=======================================================
	'''.format(
		server=server,
		ip=remote_user_ip,
		username=remote_username,
		machine_logged=machine_logged
	)

	current_user_group = bash.get_output('groups {0} | grep sys-admin'.format(
		remote_username))

	if 'sys-admin' in current_user_group:
		print(banner_sys_admin())

	print(banner)

	send_email(remote_username, machine_logged, remote_user_ip)


if __name__ == '__main__':
	check_new_ssh_connection()
