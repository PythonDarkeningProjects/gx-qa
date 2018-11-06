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

from gfx_qa_tools.common import bash
from gfx_qa_tools.common import utils
from gfx_qa_tools.common import log
import yaml

data = yaml.load(open('/home/custom/config.yml'))
default_mailing_list = data['suite_conf']['default_mailing_list']
dut_hostname = data['dut_conf']['dut_hostname']
dut_static_ip = data['dut_conf']['dut_static_ip']
dut_user = data['dut_conf']['dut_user']
sender = 'ezbench@noreply.com'
control_file = os.path.join('/home', dut_user, '.xserver.ctrl')

# initialize the logger
log_file = os.path.join('/home', dut_user, 'xserver.log')

logger = log.setup_logging(
	name='launcher', level='debug', log_file='{0}'.format(log_file)
)
logger.info(
	'initialize the logger for ({0}) rendercheck'.format(log_file))


def check_xserver_xorg():
	"""Check the name of the configuration file xorg.conf in the system

	After a debian package is setup through clonezilla environment
	when Ubuntu starts for some reason the name of this file is changed to
	xorg.conf<random_number> and if the file has not the correct name TTY7 (X)
	will not be enabled.
	"""
	# validating if xserver is on graphic stack installed in the system

	path_graphic_stack = '/home/custom/graphic_stack/packages'
	xserver_in_easy_bugs = bash.get_output(
		'ls {0} | grep xserver '.format(path_graphic_stack)).decode('utf-8')

	if not xserver_in_easy_bugs:
		graphic_stack_package = bash.get_output('ls {0} | grep .deb'.format(
			path_graphic_stack)).decode('utf-8')
		logger.info('the current graphic stack does not contains xserver')
		logger.info(graphic_stack_package)
		utils.emailer(
			sender,
			default_mailing_list,
			'the current graphic stack ({stack}) does not contains xserver'
			.format(stack=graphic_stack_package),
			'The following system does not contains a graphic stack for xserver\n'
			'host: {host}\nip: {ip}\n'.format(
				host=dut_hostname, ip=dut_static_ip))
		sys.exit(1)

	if not os.path.exists(control_file):
		xserver_original_name = 'xorg.conf'
		xserver_system_name = bash.get_output(
			'ls /etc/X11 | grep xorg.conf | grep -v failsafe').decode('utf-8')

		logger.info('(xorg.conf) current name is: {0}'.format(xserver_system_name))

		if xserver_original_name != xserver_system_name:
			logger.info('changing to: {0}'.format(xserver_original_name))
			output = \
				os.system(
					'sudo mv ' +
					os.path.join('/etc', 'X11', xserver_system_name) +
					' ' + os.path.join('/etc', 'X11', xserver_original_name))
			if output != 0:
				logger.error(
					'an error has occurred trying to change the name of : {0}'
					.format(xserver_system_name))
				utils.emailer(
					sender,
					default_mailing_list,
					'an error has occurred trying to change the name of ({0}) on ({1}) ({2})'
					.format(xserver_system_name, dut_hostname, dut_static_ip),
					'The following system has poorly configured (xorg.conf), '
					'please check it manually:\n - ({0})\n - ({1})'.format(
						dut_hostname, dut_static_ip))
				sys.exit(1)
			else:
				logger.info('({0}) was changed to ({1}) successfully'.format(
					xserver_system_name, xserver_original_name))
				logger.info('creating a control file into: {0}'.format(control_file))
				os.system('touch ' + control_file)
				logger.info('rebooting the system')
				os.system('sudo reboot')
		else:
			logger.info(
				'(xserver_system_name) and (xserver_original_name) are the same')
	else:
		bash.message('info', 'control file ({0}) exists'.format(control_file))
		bash.message('info', 'nothing to do')
		sys.exit(0)


if __name__ == '__main__':
	check_xserver_xorg()
