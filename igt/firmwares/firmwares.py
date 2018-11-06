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
import yaml

from gfx_qa_tools.common import bash

if os.path.exists('/home/custom/config.yml'):
	data = yaml.load(open('/home/custom/config.yml'))
	dut_user = data['dut_conf']['dut_user']
	guc = data['firmwares']['guc']
	dmc = data['firmwares']['dmc']
	huc = data['firmwares']['huc']
else:
	bash.message(
		'err',
		'({config}) does not exists'.format(config='/home/custom/config.yml'))
	sys.exit(1)

ctrl_file = os.path.join('/home', dut_user, '._firmware_ctrl')

if not os.path.exists(ctrl_file):
	if guc or dmc or huc:
		firmwares_path = os.path.join('/home', 'custom', 'firmwares')
		if not os.path.exists(firmwares_path):
			bash.message(
				'info',
				'(' + os.path.basename(firmwares_path) + ') does not exists')
			os.system(
				'echo "({0}) does not exists" > {1}'
				.format(firmwares_path, ctrl_file))
			sys.exit(1)
		else:
			if guc:
				bash.message('info', 'installing guc ({0}) ...'.format(guc))
				guc_path = os.path.join(firmwares_path, 'guc', guc)
				if os.path.exists(guc_path):
					fw_script = os.path.join(guc_path, 'install.sh')
					os.system('sudo bash {0}'.format(fw_script))
				else:
					bash.message(
						'err', '({0}) does not exits'.format(guc_path))
			if dmc:
				bash.message('info', 'installing dmc ({0}) ...'.format(dmc))
				dmc_path = os.path.join(firmwares_path, 'dmc', dmc)
				if os.path.exists(dmc_path):
					fw_script = os.path.join(dmc_path, 'install.sh')
					os.system('sudo bash {0}'.format(fw_script))
				else:
					bash.message(
						'err', '({0}) does not exits'.format(dmc_path))
			if huc:
				bash.message('info', 'installing huc ({0}) ...'.format(huc))
				huc_path = os.path.join(firmwares_path, 'huc', huc)
				if os.path.exists(huc_path):
					fw_script = os.path.join(huc_path, 'install.sh')
					os.system('sudo bash {0}'.format(fw_script))
				else:
					bash.message(
						'err', '({0}) does not exits'.format(huc_path))

			os.system('touch {0}'.format(ctrl_file))
			bash.message(
				'info',
				'rebooting the dut in order to apply the firmwares '
				'in the kernel')
			os.system('sudo reboot')
