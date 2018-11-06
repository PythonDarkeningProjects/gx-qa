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
import calendar
from datetime import date
import os

import requests
import yaml

from gfx_qa_tools.common import bash


def check_current_platform(current_platform, firmware):
	"""Check the current platform.

	The aim of this function is to evaluate the current platform in order to
	return a specific params for variables grub_parameters, dmc, guc, huc.
	:param current_platform: which is the current platform.
	:param firmware: the possible values are:
		- True: if the execution will run with FWs.
		- False: if the execution will not run with FWs.
	:return:
		- grub_parameters: which are the grub parameters.
		- dmc: which is the dmc firmware to be loaded in the system.
		- guc: which is the guc firmware to be loaded in the system.
		- huc: which is the huc firmware to be loaded in the system.
	"""
	general_grub_params = 'drm.debug=0x1e auto panic=1 nmi_watchdog=panic ' \
		'intel_iommu=igfx_off fsck.repair=yes'
	fw_grub_params = 'i915.enable_guc=-1'
	driver_grub_param = 'i915.alpha_support=1'
	grub_parameters = ''
	dmc = ''
	guc = ''
	huc = ''

	if current_platform == 'GLK':
		if firmware:
			guc = ''
			dmc = 'glk_dmc_ver1_04'
			huc = ''
			grub_parameters = '{general} {fw}'.format(
				general=general_grub_params, fw=fw_grub_params)
		else:
			grub_parameters = '{general} {i915}'.format(
				general=general_grub_params, i915=driver_grub_param)

	elif current_platform == 'BXT':
		if firmware:
			guc = 'bxt_guc_ver9_29'
			dmc = 'bxt_dmc_ver1_07'
			huc = 'bxt_huc_ver01_07_1398'
			grub_parameters = '{general} {fw}'.format(
				general=general_grub_params, fw=fw_grub_params)
		else:
			grub_parameters = '{general}'.format(general=general_grub_params)

	elif current_platform == 'SKL':
		if firmware:
			guc = 'skl_guc_ver9_33'
			dmc = 'skl_dmc_ver1_27'
			huc = 'skl_huc_ver01_07_1398'
			grub_parameters = '{general} {fw}'.format(
				general=general_grub_params, fw=fw_grub_params)
		else:
			grub_parameters = '{general}'.format(general=general_grub_params)

	elif current_platform == 'KBL':
		if firmware:
			guc = 'kbl_guc_ver9_39'
			dmc = 'kbl_dmc_ver1_04'
			huc = 'kbl_huc_ver02_00_1810'
			grub_parameters = '{general} {fw}'.format(
				general=general_grub_params, fw=fw_grub_params)
		else:
			grub_parameters = '{general}'.format(general=general_grub_params)

	elif current_platform == 'CFL':
		if firmware:
			guc = 'kbl_guc_ver9_39'
			dmc = 'kbl_dmc_ver1_04'
			huc = 'kbl_huc_ver02_00_1810'
			grub_parameters = '{general} {fw} {i915}'.format(
				general=general_grub_params, fw=fw_grub_params, i915=driver_grub_param)
		else:
			grub_parameters = '{general} {i915}'.format(
				general=general_grub_params, i915=driver_grub_param)

	elif current_platform == 'CNL':
		if firmware:
			guc = ''
			dmc = 'cnl_dmc_ver1_07'
			huc = ''
			grub_parameters = '{general}'.format(
				general=general_grub_params)
	else:
		grub_parameters = '{general}'.format(general=general_grub_params)

	return grub_parameters, dmc, guc, huc


def create_configuration_files(**kwargs):
	"""Create configuration files.

	The aim of this function is to create configurations files in order to the
	automated system perform several actions with them like install a linux
	image, run a specific suite, etc.

	:param kwargs:
		- raspberry_number: which is the raspberry number where the config will
		be storage, e.g : raspberry-01
		- switch_number: which is the switch number where the config will be
		storage, e.g : switch-01
		- gfx_stack_code: which is the gfx stack code.
		- kernel_commit: which is the kernel commit.
		- firmware: the two possibles values are :
			True (if the user wants the config with FWs (if any))
			False (if the user does not wants the config with FWs (if any))
		- extension: the extension of the output file, the two possibles values
			are :
			cfg (for bash) and yml (for python).
		- hour: the hour to be write in the configuration file.
		- year: the year to be write in the configuration file.
		- workweek: the workweek to be write in the configuration file.
		- day: the day to be write in the configuration file.
		- build_id: the build id to be write in the configuration file.
		- build_status: the build id status, the possible values are:
			- true: when a build id is new in the API.
			- false: when a build id already exists in the API.
		- visualization: enabling reporting in visualization.
	"""

	raspberry_number = kwargs['raspberry_number']
	switch_number = kwargs['switch_number']
	gfx_stack_code = kwargs['gfx_stack_code']
	kernel_commit = kwargs['kernel_commit']
	firmware = kwargs['firmware']
	extension = kwargs['extension']
	hour = kwargs['hour']
	year = kwargs['year']
	workweek = kwargs['workweek']
	day = kwargs['day']
	build_id = kwargs['build_id']
	build_status = kwargs['build_status']
	visualization = kwargs['visualization']
	report = kwargs['report']

	http_address = 'http://10.219.106.111:2020/getraspberries'

	try:
		raspberries_dict = requests.get(http_address, timeout=10)
		data = raspberries_dict.json()
	except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
		bash.message('err', 'could not connect to database')
	else:
		new_switch_number = switch_number - 1
		for raspberry in data:
			if '{0}'.format(raspberry['name']) == 'Raspberry {0}'.format(
				raspberry_number):
				raspberry_ip = raspberry['ip'].encode()
				dut_hostname = raspberry['powerSwitches'][new_switch_number][
					'Dut_Hostname'].encode()
				current_platform = raspberry['powerSwitches'][new_switch_number][
					'Platform'].encode()
				raspberry_gpio = raspberry['powerSwitches'][new_switch_number][
					'GPIO'].encode()
				dut_static_ip = raspberry['powerSwitches'][new_switch_number][
					'DUT_IP'].encode()
				usb_cutter_serial = raspberry['powerSwitches'][new_switch_number][
					'usbCutter'].encode()
			else:
				continue

		grub_parameters, dmc, guc, huc = check_current_platform(
			current_platform, firmware)

		weekday = calendar.day_name[date.today().weekday()]
		current_tittle = 'drm-intel-qa' if weekday == 'Monday' else 'drm-tip'

		default_mailing_list = [
			'humberto.i.perez.rodriguez@intel.com'
		]

		data_dict = {}

		usb_conf = {
			'usb_conf': {
				'network_interface': '',
				'custom_hostname': 'clonez',
				'server_hostname': '10.219.106.111',
				'server_user': 'root',
				'server_partimag': '/home/clonezilla',
				'server_shared': '/home/shared',
				'default_image': 'Ubuntu_17.10_64bits_20GB_intel-gpu-tools',
				'default_disk': '',
				'usb_update_mode': 'on',
				'clonezilla_debug': 'False'
			}
		}

		raspberry_conf = {
			'raspberry_conf': {
				'raspberry_number': '{0}'.format(raspberry_number),
				'raspberry_ip': '{0}'.format(raspberry_ip),
				'raspberry_user': 'pi',
				'usb_cutter_serial': '{0}'.format(usb_cutter_serial),
				'raspberry_power_switch': '{0}'.format(switch_number),
				'raspberry_gpio': '{0}'.format(raspberry_gpio)
			}
		}

		suite_conf = {
			'suite_conf': {
				'kernel_branch': 'drm-intel-qa',
				'kernel_commit': '{0}'.format(kernel_commit),
				'gfx_stack_code': '{0}'.format(gfx_stack_code),
				'default_package': 'igt_fast_feedback',
				'default_mailing_list': default_mailing_list,
				'blacklist_file': 'yes',
				'igt_iterations': '2'
			}
		}

		dut_conf = {
			'dut_conf': {
				'dut_hostname': '{0}'.format(dut_hostname),
				'dut_static_ip': '{0}'.format(dut_static_ip),
				'grub_parameters': '{0}'.format(grub_parameters),
				'dut_user': 'gfx',
				'dut_password': 'linux',
				'graphical_environment': 'off',
				'autologin': 'off'
			}
		}

		firmwares = {'firmwares': {'guc': guc, 'dmc': dmc, 'huc': huc}}
		database = {'database': {'upload_reports': True}}
		autouploader = {
			'autouploader': {
				'trc_report': True,
				'currentEnv': report,
				'currentPlatform': '{0}'.format(current_platform),
				'currentRelease': 'Platforms',
				'currentSuite': 'IGT fastfeedback',
				'currentTittle': current_tittle,
				'visualization': visualization
			}
		}

		build_information = {
			'build_information': {
				'kernel_branch': 'drm-intel-qa',
				'kernel_commit': kernel_commit,
				'gfx_stack_code': gfx_stack_code,
				'suite': 'igt_fast_feedback',
				'hour': hour,
				'year': year,
				'ww': workweek,
				'day': day,
				'build_id': build_id,
				'New': build_status
			}
		}

		list_update = [
			usb_conf, raspberry_conf, suite_conf, dut_conf, firmwares, database,
			autouploader, build_information
		]

		for element in list_update:
			data_dict.update(element)

		output_config_file = os.path.join(
			'/home/shared/raspberry/raspberry-0{0}'.format(raspberry_number),
			'switch-0{0}'.format(switch_number), 'custom',
			'config.yml' if extension == 'yml' else 'config.cfg'
		)

		with open(output_config_file, 'w') as archive:
			if extension == 'yml':
				archive.write(yaml.dump(data_dict, default_flow_style=False))
			else:
				for element in data_dict.values():
					for key, value in iter(element.items()):
						archive.write('{0}="{1}"\n'.format(key, value))
