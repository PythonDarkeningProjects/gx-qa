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
from time import sleep

import yaml

from gfx_qa_tools.common import bash
from gfx_qa_tools.common import log

# getting the username from config.yml
data = yaml.load(open('/home/custom/config.yml'))
dut_user = data['dut_conf']['dut_user']

# initializing the logger
log_filename = 'sentinel.log'
log_path = '/home/{user}/logs'.format(user=dut_user)

if not os.path.exists(log_path):
	os.makedirs(log_path)

logger = log.setup_logging(
	'sentinel', level='debug',
	log_file='{path}/{filename}'.format(path=log_path, filename=log_filename))

path_to_files = '/var/log'

# the files to check can have rotatory files.
files_to_check = [
	'syslog',
	'kern.log'
]

# size in bytes
maximum_size_allowed = 15360

while True:
	for archive in files_to_check:
		# getting a list for the rotatory files (if any)
		rotatory_files = bash.get_output('ls {0} | grep {1}'.format(
			path_to_files, archive)).split()
		for rotatory_file in rotatory_files:
			# getting file size in bytes
			file_size_bytes = os.path.getsize('{0}/{1}'.format(
				path_to_files, rotatory_file)) / 1024
			if file_size_bytes > maximum_size_allowed:
				logger.warning('{0} : exceeds of the maximum size allowed'.format(
					rotatory_file))
				logger.info('current size : {0} MB'.format(file_size_bytes / 1024))
				logger.info('maximum size allowed : {0} MB'.format(
					maximum_size_allowed / 1024))
				logger.info('removing : {0}'.format(rotatory_file))
				output = os.system('sudo rm -rf {0}/{1}'.format(
					path_to_files, rotatory_file))
				if output:
					logger.error('{0} : could not be eliminated'.format(rotatory_file))
				else:
					logger.info('{0} : was successfully eliminated'.format(rotatory_file))
	sleep(1)
