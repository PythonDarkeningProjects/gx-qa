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
import fnmatch
import os
from shutil import rmtree
import sys

from common import apiutils
from gfx_stack import gfxStack
from igt.suites.fastfeedback import create_config_files as yaml_creator
from kernel import kernel_build
from raspberry import raspberry
import requests
import yaml

from gfx_qa_tools.common import bash
from gfx_qa_tools.common import log
from gfx_qa_tools.common import utils


class IGTLauncher(object):

	def __init__(self, **kwargs):
		"""Class constructor

		:param kwargs:
			- stack: build a new graphic stack (boolean value).
			- kernel: build a new kernel (boolean value).
			- firmware: set the configurations files with firmware (if any)
				(boolean value).
			- dryrun: simulate the run of this script, do not setup any DUT
				(boolean value).
			- grabsystemsbusy: grab the systems in (platforms_not_launched.yml)
				and launch them with latest configuration.
			- visualization: enabling reporting in visualization.
			- report: enabling reporting to Test Report Center.
		"""
		# initialize the logger
		log_name = 'orchestrator'
		log_path = '/home/shared/logs/orchestrator/fastfeedback'

		self.log = log.setup_logging(
			name=log_name, level='info',
			log_file='{path}/{filename}.log'.format(path=log_path, filename=log_name)
		)

		self.stack = kwargs.get('stack', None)
		self.kernel = kwargs.get('kernel', None)
		self.firmware = kwargs.get('firmware', None)
		self.dryrun = kwargs.get('dryrun', None)
		self.grab_systems_busy = kwargs.get('grabsystemsbusy', None)
		self.visualization = kwargs.get('visualization', None)
		self.report = kwargs.get('report', 'sand')

		# environment variables
		os.environ['GIT_SSL_NO_VERIFY'] = '1'

		self.this_path = os.path.dirname(os.path.abspath(__file__))
		self.main_path = '/home/shared/build'
		self.gfx_qa_repo = 'https://github.intel.com/linuxgraphics/gfx-qa-tools.git'
		self.suite = 'intel-gpu-tools'

		# graphic stack variables
		self.gfx_stack_path = os.path.join(self.main_path, 'gfx_stack', self.suite)
		self.gfx_stack_config = os.path.join(
			self.gfx_stack_path, 'gfx-qa-tools', 'gfx_stack', 'config.yml')
		self.debian_packages_path = '/home/shared/gfx_stack/packages'
		self.kernel_packages_path = '/home/shared/kernels_mx/drm-intel-qa'

		self.week_number = bash.get_output('date +"%-V"')
		self.week_day = bash.get_output('date +%A')
		self.year = bash.get_output('date +%G')
		self.hour = bash.get_output('date +"%I-%M-%S"')
		self.sender = 'fastfeedback@noreply.com'
		self.mailing_list = [
			'humberto.i.perez.rodriguez@intel.com',
			'hector.edmundox.ramirez.gomez@intel.com'
		]

		get_raspberries = 'http://10.219.106.111:2020/getraspberries'
		self.raspberries_json_data = requests.get(get_raspberries, timeout=20).json()
		self.table_content_launch, self.table_content_not_launch = ([],) * 2
		self.systems_to_launch = {}
		self.systems_to_not_launch = {}

	def create_configuration_files(self, **kwargs):
		"""Create configuration files

		The aim of this function is for create the configuration files required
		which are the config.cfg/yml for the automated system.
		The configuration files only will be created if a system is available
		in watchdog.

		:param kwargs:
			- graphic_stack_code: which is the graphic stack code.
			- kernel_commit: which is the kernel commit.
			- build_id: which is the build id for visualization.
			- build_status: the build status, the possible values are:
				- true: when the build id is new in the API.
				- false: when the build id already exists in the API.

		"""
		raspberry_main_path = '/home/shared/raspberry'
		graphic_stack_code = kwargs['graphic_stack_code']
		kernel_commit = kwargs['kernel_commit']
		build_id = kwargs['build_id']
		build_status = kwargs['build_status']

		# getting the host names setup for intel-gpu-tools execution
		whitelist_data = self.whitelist()

		# raspberry: value=string
		# host: value=dictionary
		for raspberry, hosts in iter(whitelist_data.items()):

			# single_host: value=string
			for single_host in hosts.keys():

				for rasp in self.raspberries_json_data:
					raspberry_name = rasp['name'].split()[0].lower().encode()
					raspberry_id = rasp['name'].lower().split()[1].encode()
					current_raspberry = '{name}-0{id}'.format(
						name=raspberry_name, id=raspberry_id)

					for power_switch in rasp['powerSwitches']:
						if power_switch['Dut_Hostname'].encode() == hosts[
							single_host]:
							# loading the values for each system
							current_status = power_switch['Status'].encode()
							current_platform = power_switch[
								'Platform'].encode()
							current_hostname = power_switch[
								'Dut_Hostname'].encode()
							current_switch = power_switch['value'].encode()
							current_cname = power_switch['CNAME'].encode()
							current_gpio = power_switch['GPIO'].encode()
							current_ip = power_switch['DUT_IP'].encode()
							current_usb_cutter = power_switch[
								'usbCutter'].encode()

							# checking if the DUT is available
							if current_status == 'available':
								self.log.info(
									'the following platform is available ({0}) - hostname ({1})'
									.format(current_platform, current_hostname))
								to_update = {
									current_hostname: {
										'currentStatus': current_status,
										'currentPlatform': current_platform,
										'currentHostname': current_hostname,
										'currentSwitch': current_switch,
										'currentCname': current_cname,
										'currentGPIO': current_gpio,
										'currentIP': current_ip,
										'currentUSB_Cutter': current_usb_cutter}}

								self.systems_to_launch.update(to_update)

								update_rows = [
									current_platform, current_status, current_hostname,
									current_switch, current_ip, current_usb_cutter
								]

								self.table_content_launch.append(update_rows)

								config_path = os.path.join(
									raspberry_main_path, current_raspberry,
									'switch-0{0}'.format(current_switch), 'custom'
								)
								self.log.info('path to write the configs: ({0})'.format(
									config_path))

								# writing the configuration files
								config_extensions = ['cfg', 'yml']

								for extension in config_extensions:
									self.log.info(
										'creating config.{ext} for ({current_platform}) '
										'hostname ({current_hostname})'.format(
											current_platform=current_platform,
											current_hostname=current_hostname,
											ext=extension))

									yaml_creator.create_configuration_files(
										raspberry_number=int(raspberry_id),
										switch_number=int(current_switch),
										gfx_stack_code=graphic_stack_code,
										kernel_commit=kernel_commit,
										firmware=self.firmware,
										hour=self.hour,
										year=self.year,
										workweek=self.week_number,
										day=self.week_day,
										build_id=build_id,
										build_status=build_status,
										extension=extension,
										visualization='true' if self.visualization else 'false',
										report=self.report
									)

								# setup the current system
								self.setup_system(
									current_hostname=current_hostname, current_platform=current_platform,
									raspberry_id=raspberry_id, current_switch=current_switch,
									current_ip=current_ip, kernel_commit=kernel_commit,
									graphic_stack_code=graphic_stack_code
								)

							else:
								self.log.warning(
									'the following platform is not available : ({current_platform}) '
									'hostname ({current_hostname}) skipping it'.format(
										current_platform=current_platform,
										current_hostname=current_hostname))
								to_update = {
									current_hostname: {
										'currentStatus': current_status,
										'currentPlatform': current_platform,
										'currentHostname': current_hostname,
										'currentSwitch': current_switch,
										'currentCname': current_cname,
										'currentGPIO': current_gpio,
										'currentIP': current_ip,
										'currentUSB_Cutter': current_usb_cutter,
										'raspberry': current_raspberry}}

								self.systems_to_not_launch.update(to_update)

								update_rows = [
									current_platform, current_status, current_hostname,
									current_switch, current_ip, current_usb_cutter
								]

								self.table_content_not_launch.append(update_rows)

	def whitelist(self):
		"""Make a dictionary with the hosts names to run intel-gpu-tools

		:return: data, which is the dictionary with the host names that will run
		intel-gpu-tools fast-feedback
		"""

		if self.grab_systems_busy:
			if not os.path.isfile('platforms_not_launched.yml'):
				self.log.error('(platforms_not_launched.yml) does not exist')
				self.log.info('please set --grabsystemsbusy to False')
				sys.exit(1)
			else:
				self.log.info(
					'taking the configuration file (platforms_not_launched.yml)')
				data = yaml.load(
					open(os.path.join(self.this_path, 'platforms_not_launched.yml')))
				return data
		else:
			self.log.info(
				'taking the default configuration from '
				'(http://bifrost.intel.com:2020/modifydb)')

			systems_up = 0
			data = {}

			for raspberry in self.raspberries_json_data:
				raspberry_number = raspberry['name'].encode().split()[1]
				for switch in raspberry['powerSwitches']:
					switch_number = switch['name'].encode().split()[1]
					system = switch['Dut_Hostname'].encode()

					# evaluating the boolean condition
					condition_to_evaluate = switch['fbb_member'].encode()[0].upper() == 'T'

					if condition_to_evaluate:
						systems_up += 1
						# updating whitelist_data dict
						try:
							data[
								'raspberry_0{0}'.format(raspberry_number)][
								'host_0{0}'.format(switch_number)] = system
						except KeyError:
							data.update({
								'raspberry_0{0}'.format(raspberry_number): {
									'host_0{0}'.format(switch_number): system}})
			if not systems_up:
				self.log.error(
					'please setup some system in (http://bifrost.intel.com:2020/modifydb)')
				sys.exit(1)

			return data

	def send_custom_message_to_watchdog(self, **kwargs):
		"""Send a custom message to watchdog.

		:param kwargs:
			- raspberry_id: which is the raspberry number.
			- current_switch: which is the current switch number.
			- current_hostname: which is the current system hostname.
			- current_ip: which is the current system ip.
			- kernel_commit: which is the kernel commit.
			- graphic_stack_code: which is the graphic stack code.
			- current_platform: which is the current platform.
		"""
		raspberry_id = kwargs['raspberry_id']
		current_switch = kwargs['current_switch']
		current_hostname = kwargs['current_hostname']
		current_ip = kwargs['current_ip']
		kernel_commit = kwargs['kernel_commit']
		graphic_stack_code = kwargs['graphic_stack_code']
		current_platform = kwargs['current_platform']

		# custom message for the watchdog
		message_for_api = '(auto-setup for {0} fastfeedback)'.format(self.suite)

		self.log.info(
			'sending a post for ({current_platform}) '
			'hostname ({current_hostname}) in watchdog'.format(
				current_platform=current_platform,
				current_hostname=current_hostname))

		# submit and clean the data to update the DB
		apiutils.cleanup_watchdog_row(
			raspberry_id,
			current_switch,
			DutHostname=current_hostname,
			DutIP=current_ip,
			Status=message_for_api,
			Suite='igt_fast_feedback',
			KernelBranch='drm-intel-qa',
			KernelCommit=kernel_commit,
			GfxStackCode=graphic_stack_code
		)

	def setup_system(self, **kwargs):
		"""Setup a system.

		The aim of this function is to setup a system for the automated execution.

		:param kwargs:
			- current_hostname: which is the current hostname to setup.
			- current_platform: which is the current platform to setup.
			- raspberry_id: which is the raspberry number.
			- current_switch: which is the switch number.
			- kernel_commit: which is the kernel commit to setup.
			- graphic_stack_code: which is the graphic stack to setup.
			- current_ip: which is the current ip of the DUT.
		"""
		current_hostname = kwargs['current_hostname']
		current_platform = kwargs['current_platform']
		raspberry_id = int(kwargs['raspberry_id'])
		current_switch = int(kwargs['current_switch'])
		kernel_commit = kwargs['kernel_commit']
		graphic_stack_code = kwargs['graphic_stack_code']
		current_ip = kwargs['current_ip']
		raspberry_script = '/home/shared/gitlist/gfx-qa-tools/raspberry/raspberry.py'

		if self.dryrun:
			self.log.info('dryrun parameter was set')
			self.log.info(
				'({script}) will not be executed for hostname ({current_hostname})'
				.format(script=raspberry_script, current_hostname=current_hostname))
		else:
			self.log.info(
				'setting ({current_platform}) hostname ({current_hostname}) '
				'with (raspberry.py)'.format(
					current_platform=current_platform, current_hostname=current_hostname))

			# setting the DUT with (raspberry.py)
			raspberry.ElectricalControlManager(
				raspberry=raspberry_id, coldreset=current_switch, cutter='on'
			).manager()

			# blocking the platform in database
			self.log.info(
				'blocking ({current_platform}) hostname ({current_hostname}) in database'
				.format(
					current_platform=current_platform, current_hostname=current_hostname))

			apiutils.unlock_lock_system_in_watchdog_db(
				raspberry_id, current_switch, 'busy')

			# custom message for the watchdog
			self.send_custom_message_to_watchdog(
				raspberry_id=raspberry_id,
				current_switch=current_switch,
				current_hostname=current_hostname,
				current_ip=current_ip,
				kernel_commit=kernel_commit,
				graphic_stack_code=graphic_stack_code,
				current_platform=current_platform
			)

	def check_for_systems_not_launched(self):
		"""Check for systems not launched.

		if there is some system busy, this part will create the file
		platforms_not_launched.yml
		"""
		output_file = os.path.join(self.this_path, 'platforms_not_launched.yml')

		if self.systems_to_not_launch.keys():
			self.log.info('creating a file with the systems not launched')

			systems_not_launched_dict = {}
			host_count = 1

			# iterating over systems_to_not_launch.keys() in order to get the platforms
			# not launched
			for hostname in self.systems_to_not_launch.keys():
				raspberry = self.systems_to_not_launch[hostname]['raspberry'].replace(
					'-', '_')
				if raspberry not in systems_not_launched_dict:
					tmp_dict = {
						raspberry: {'host_0{0}'.format(host_count): hostname}}
					systems_not_launched_dict.update(tmp_dict)
					host_count += 1
				else:
					tmp_dict = {'host_0{0}'.format(host_count): hostname}
					systems_not_launched_dict[raspberry].update(tmp_dict)
					host_count += 1

			with open(output_file, 'w') as platforms_file:
				platforms_file.write(yaml.dump(
					systems_not_launched_dict, default_flow_style=False))

			if not os.path.isfile('platforms_not_launched.yml'):
				self.log.error(
					'the file (platforms_not_launched.yml) could not be created')
				sys.exit(1)

			self.log.info(
				'the file (platforms_not_launched.yml) was created '
				'successfully into ({0})'.format(self.this_path))

		elif not self.systems_to_not_launch.keys() and os.path.isfile(output_file):
			self.log.info('removing : {0}'.format(output_file))
			os.remove(output_file)

	def build_qa_kernel(self):
		"""Build a QA kernel.

		This function is dedicated to build a QA kernel in order to intel-gpu-tools
		by the automated system.
		The kernels from QA have the same source code that drm-tip.
		:return:
			- kernel_commit : which is the kernel commit built from kernel_build.py
			script and it will be use during fastfeedback execution.
		"""
		kernel_builder_path = os.path.join(
			self.main_path, 'kernel', 'drm-intel-qa')

		workspace = os.path.join(kernel_builder_path, 'gfx-qa-tools')
		if os.path.exists(workspace):
			self.log.info('deleting workspace')
			rmtree(workspace)

		self.log.info(
			'cloning gfx-qa-tools in : {0}'.format(kernel_builder_path))
		cmd = 'git -C {path} clone {repo}'.format(
			path=kernel_builder_path, repo=self.gfx_qa_repo)
		bash.check_output(
			cmd,
			'gfx-qa-tools repository was successfully cloned',
			'an error occurred cloning gfx-qa-tools repository'
		)

		self.log.info('building QA kernel')
		kernel_commit = kernel_build.KernelManaging(tag=True).check_pid()

		if not kernel_commit:
			utils.emailer(
				self.sender,
				self.mailing_list,
				'fastfeedback could not be launched on ({year}) '
				'(WW{week_number}) ({week_day}) ({hour})'.format(
					year=self.year, week_number=self.week_number, week_day=self.week_day,
					hour=self.hour),
				'fastfeedback could not be launched due to '
				'({kernel_commit}) is empty'.format(
					kernel_commit=os.path.basename(kernel_commit)),
				silent=True)
			sys.exit(1)

		self.log.info('using the latest kernel code built : {0}'.format(
			kernel_commit))

		return kernel_commit

	@staticmethod
	def check_components_in_bifrost(**kwargs):
		"""Check a component in bifrost.

		The aim of this function is to check if a component like graphic stack/
		kernel exist in bifrost.
		If the component does not exist in bifrost clonezilla will fail trying
		to install it, in order to avoid this scenario this function return
		a False when the component does not exist.
		:param kwargs:
			- component: the component to find, e.g:
				* kernel_commit
				* graphic_stack_code
			- path_to_component: the absolute path to the component to find.
		:return:
			- False: when the component to find does not exist in bifrost.
			- True: when the component to find exist in bifrost.
		"""
		component = kwargs['component']
		path_to_component = kwargs['path_to_component']
		pattern = '*{0}*'.format(component)

		for dirpath, dirnames, filenames in os.walk(path_to_component):
			if filenames:
				for archive in filenames:
					if fnmatch.fnmatch(archive, pattern):
						return True
		return False

	def get_kernel_commit(self):
		"""Get a kernel commit.

		The aim of this function is to get a kernel commit in order to run
		intel-gpu-tools fastfeedback testlist in the systems.
		If the user chose 'kernel' argument as true, this function will build a new
		QA kernel, otherwise this will get the latest kernel commit from the API.

		:return:
			- kernel_commit : which is the kernel commit built from kernel_build.py
			script and it will be use during fastfeedback execution.
		"""

		if self.kernel:
			# getting a kernel commit
			kernel_commit = self.build_qa_kernel()
		else:
			# getting the kernel_commit from latest execution registered in
			# the API
			kernel_commit = apiutils.get_latest_data_from_api('kernel_commit', stop=True)
			# checking if the kernel_commit returned from the API exits in bifrost
			if not self.check_components_in_bifrost(
				component=kernel_commit,
				path_to_component=self.kernel_packages_path
			):
				self.log.error(
					'the following kernel commit code does not exist in '
					'bifrost : {0}'.format(kernel_commit))
				sys.exit(1)
			self.log.info('taking the latest kernel commit from the API : {0}'.format(
				kernel_commit))

		return kernel_commit

	def build_graphic_stack(self):
		"""Build a new graphic stack.

		The aim of this function is to build a new graphic stack for intel-gpu-tools.
		This action will be performed by gfxStack.py script, and the final file will
		be a debian package that will contains all the drivers required in order to
		run intel-gpu-tools.

		:return:
			-graphic_stack_code: the graphic_stack_code is a file that is created
			by gfxStack.py if everything went well.
		"""
		self.log.info('building a new graphic stack for : {0}'.format(self.suite))
		graphic_stack_code = gfxStack.Builder(
			config_file=self.gfx_stack_config
		).build()

		if not graphic_stack_code:
			self.log.error('graphic_stack_code is empty')
			utils.emailer(
				self.sender,
				self.mailing_list,
				'fastfeedback could not be launched on ({year}) '
				'(WW{week_number}) ({week_day}) ({hour})'.format(
					year=self.year, week_number=self.week_number, week_day=self.week_day,
					hour=self.hour),
				'fastfeedback could not be launched due to gfx_stack_code is empty',
				silent=True)
			sys.exit(1)

		self.log.info('using the latest graphic stack code built : ({0})'.format(
			graphic_stack_code))

		return graphic_stack_code

	def create_graphic_stack_config(self):
		"""Create a graphic stack configuration file.

		This function is dedicated to build config.yml with all the configurations
		required to build the graphic stack for intel-gpu-tools
		"""

		workspace = os.path.join(self.gfx_stack_path, 'gfx-qa-tools')
		if os.path.exists(workspace):
			self.log.info('deleting workspace for graphic stack : {0}'.format(
				self.suite))
			rmtree(workspace)

		self.log.info('cloning gfx-qa-tools repository in : {0}'.format(
			self.gfx_stack_path))
		cmd = 'git -C {path} clone {repo}'.format(
			path=self.gfx_stack_path, repo=self.gfx_qa_repo)
		bash.check_output(
			cmd,
			'gfx-qa-tools repository was successfully cloned',
			'an error occurred cloning gfx-qa-tools repository'
		)

		self.log.info(
			'creating a new ({graphic_stack_config}) for {suite}'.format(
				graphic_stack_config=self.gfx_stack_config, suite=self.suite))
		config_yml = {}
		dut_config = {'dut_config': {'dut_user': 'gfx'}}
		package_config = {'package_config': {'package_name': 'fastfeedback'}}
		latest_commits = {
			'latest_commits': {
				'value': True,
				'drm': True,
				'cairo': False,
				'intel-gpu-tools': True,
				'piglit': True,
				'mesa': False,
				'xf86-video-intel': False,
				'libva': False,
				'intel-vaapi-driver': False,
				'macros': False,
				'xserver': False}}
		specific_commit = {
			'specific_commit':
				{'value': False,
					'drm': False,
					'mesa': False,
					'xf86-video-intel': False,
					'libva': False,
					'intel-vaapi-driver': False,
					'cairo': False,
					'macros': False,
					'xserver': False,
					'intel-gpu-tools': False,
					'piglit': False}}
		xserver_driver = {'2D_Driver': {'sna': False, 'glamour': True}}
		patchwork = {
			'patchwork':
				{'checkBeforeBuild': True,
					'drm': {'apply': False, 'path': ''},
					'mesa': {'apply': False, 'path': ''},
					'xf86-video-intel': {'apply': False, 'path': ''},
					'libva': {'apply': False, 'path': ''},
					'intel-vaapi-driver': {'apply': False, 'path': ''},
					'cairo': {'apply': False, 'path': ''},
					'macros': {'apply': False, 'path': ''},
					'xserver': {'apply': False, 'path': ''},
					'intel-gpu-tools': {'apply': False, 'path': ''},
					'rendercheck': {'apply': False, 'path': ''},
					'piglit': {'apply': False, 'path': ''}}}
		miscellaneous = {
			'miscellaneous':
				{'maximum_permitted_time': '2',
					'mailing_list': self.mailing_list,
					'upload_package': True,
					'server_for_upload_package': 'linuxgraphics.intel.com',
					'server_user': 'gfxserver'}}

		dictionaries_to_update = [
			dut_config, package_config, latest_commits, specific_commit,
			xserver_driver, patchwork, miscellaneous
		]

		for dictionary in dictionaries_to_update:
			config_yml.update(dictionary)

		with open(self.gfx_stack_config, 'w') as config:
			config.write(yaml.dump(config_yml, default_flow_style=False))

	def get_graphic_stack_code(self):
		"""Get a graphic stack code.

		The aim of this function is to get a graphic stack code in order to run
		intel-gpu-tools fastfeedback testlist in the systems.
		If the user chose 'stack' argument as true, this function will build a new
		graphic stack, otherwise this will get the latest graphic stack code from
		the API.

		:return
			- graphic_stack_code: the graphic stack code is an ID that identifies
			a debian package which contains all the components required in order
			to run intel-gpu-tools suite.
		"""

		if self.stack:
			# building a graphic stack dedicated for intel-gpu-tools
			self.create_graphic_stack_config()
			# getting the graphic_stack_code
			graphic_stack_code = self.build_graphic_stack()
		else:
			# getting the graphic_stack_code from latest execution registered
			# in the API
			graphic_stack_code = apiutils.get_latest_data_from_api(
				'gfx_stack_code', stop=True)
			if not graphic_stack_code:
				self.log.error('not graphic stack code was returned from the API')
			# checking if the graphic_stack_code returned from the API exists
			# in bifrost
			if not self.check_components_in_bifrost(
				component=graphic_stack_code,
				path_to_component=self.debian_packages_path
			):
				self.log.error(
					'the following graphic stack code does not exist in '
					'bifrost : {0}'.format(graphic_stack_code))
				sys.exit(1)
			self.log.info(
				'taking the latest graphic_stack_code from the API : {0}'.format(
					graphic_stack_code))

		return graphic_stack_code

	def check_previous_execution(self):
		"""Check for the previous execution

		The aim of this function is to check if intel-gpu-tools/kernel commits
		exist in the latest data returned by the API, in this case this will
		stop the script execution since does not make sense to run again with
		the same components reported in the latest execution.
		"""

		igt_path = '/home/shared/repositories/intel-gpu-tools'
		drm_tip_path = '/home/shared/repositories/drm-tip'

		# checking if the folders exist
		for path in igt_path, drm_tip_path:
			if not os.path.exists(path):
				self.log.error('{0} : does not exist'.format(path))
				sys.exit(1)

		# getting the latest commit of intel-gpu-tools
		latest_igt_commit = bash.get_output(
			'git -C {0} ls-remote origin master'.format(igt_path)).split()[0][:7]

		# getting the latest commit of drm-tip
		latest_drm_tip_commit = bash.get_output(
			'git -C {0} ls-remote origin drm-tip'.format(drm_tip_path)).split()[0][:7]

		# getting the intel-gpu-tools commit from a gfx_stack_code
		latest_igt_commit_bifrost = None
		graphic_stack_code = apiutils.get_latest_data_from_api(
			'gfx_stack_code', stop=True)
		if not graphic_stack_code:
			self.log.error('no graphic stack code was returned from the API')
			sys.exit(1)
		pattern = '*{0}*'.format(graphic_stack_code)

		for dirpath, dirnames, filenames in os.walk(self.debian_packages_path):
			if filenames:
				for archive in filenames:
					if fnmatch.fnmatch(archive, pattern):
						latest_igt_commit_bifrost = bash.get_output(
							'cat {0}/easy-bugs | grep intel-gpu-tools -A1'.format(
								dirpath)).split()[5][:7]

		# TODO(Beto): if this condition is met, we have to delete this build id
		# automatically from the API in order to avoid issues with clonezilla
		# (known errata)
		if not latest_igt_commit_bifrost:
			self.log.error(
				'({0}) : graphic stack code does not exits in bifrost however '
				'exist in the API, you have to delete it from the API in order '
				'to avoid conflicts with clonezilla'.format(graphic_stack_code))
			sys.exit(1)

		# checking if igt/kernel commit is in the latest data from the API
		conditions = [
			latest_igt_commit == latest_igt_commit_bifrost,
			latest_drm_tip_commit == apiutils.get_latest_data_from_api('kernel_commit')
		]

		if all(conditions):
			self.log.info(
				'the following intel-gpu-tools commit is already in latest data '
				'from the API : {0}'.format(latest_igt_commit))
			self.log.info(
				'the following drm-tip commit is already in latest data '
				'from the API : {0}'.format(latest_drm_tip_commit))

			utils.emailer(
				self.sender,
				self.mailing_list,
				'fastfeedback was not launched on ({year}) '
				'(WW{week_number}) ({week_day}) ({hour})'.format(
					year=self.year, week_number=self.week_number, week_day=self.week_day,
					hour=self.hour),
				'fastfeedback was not launched due to drm-tip/intel-gpu-tools '
				'commits exist on latest data from the API)\n\n'
				'drm-tip commit         : {kernel_commit}\n'
				'intel-gpu-tools commit : {igt_commit}'.format(
					kernel_commit=latest_drm_tip_commit,
					igt_commit=latest_igt_commit),
				silent=True)
			sys.exit(1)

	def orchestrator(self):
		"""Managing of the automated intel-gpu-tools execution.

		The aim of this function is to manage the automated execution of
		intel-gpu-tools fastfeedback of the DUTs connected to the system.
		"""
		# check the previous execution
		self.check_previous_execution()

		# getting a graphic stack code for the execution
		graphic_stack_code = self.get_graphic_stack_code()

		# getting a kernel commit for the execution
		kernel_commit = self.get_kernel_commit()

		# if the graphic stack or the kernel are new components, the build_id
		# function will create a new entry in API and this will return a new
		# build_id, otherwise this will return an existing build_id.
		get_dict_from_api = apiutils.get_build_id_dict(
			stop=True, graphic_stack_code=graphic_stack_code,
			kernel_commit=kernel_commit, hour=self.hour, year=self.year,
			week_number=self.week_number, kernel_branch='drm-intel-qa',
			suite='igt_fast_feedback', latest='true'
		)

		# creating the configuration files
		self.create_configuration_files(
			graphic_stack_code=graphic_stack_code, kernel_commit=kernel_commit,
			build_id=get_dict_from_api['build_id'],
			build_status=get_dict_from_api['New']
		)

		table_headers = [
			'Platform', 'Status', 'Hostname', 'Switch', 'IP address', 'USB Cutter'
		]

		if self.systems_to_launch:
			# creating the table
			table = utils.create_formatted_table(
				table_headers, self.table_content_launch, index=True, silent=True)

			# if there is some system busy, this part will create the file
			# platforms_not_launched.yml
			self.check_for_systems_not_launched()

			if self.grab_systems_busy:
				utils.emailer(
					self.sender,
					self.mailing_list,
					'fastfeedback was launched on ({year}) (WW{week_number}) '
					'({week_day}) ({hour}) (grabsystemsbusy)'
					.format(
						year=self.year, week_number=self.week_number, week_day=self.week_day,
						hour=self.hour),
					'fastfeedback was launched on the following platforms\n\n' +
					table.encode('utf-8'), silent=True)
			elif self.dryrun:
				utils.emailer(
					self.sender,
					self.mailing_list,
					'fastfeedback was launched on ({year}) (WW{week_number}) '
					'({week_day}) ({hour}) (dryrun)'.format(
						year=self.year, week_number=self.week_number, week_day=self.week_day,
						hour=self.hour),
					'fastfeedback was launched on the following platforms\n\n' +
					table.encode('utf-8'), silent=True)
			else:
				utils.emailer(
					self.sender,
					self.mailing_list,
					'fastfeedback was launched on ({year}) (WW{week_number}) '
					'({week_day}) ({hour})'.format(
						year=self.year, week_number=self.week_number, week_day=self.week_day,
						hour=self.hour),
					'fastfeedback was launched on the following platforms\n\n' +
					table.encode('utf-8'), silent=True)

			print(table.encode('utf-8'))
			sys.exit(0)

		else:
			# creating the table
			table = utils.create_formatted_table(
				table_headers, self.table_content_not_launch, index=True, silent=True)

			# if there is some system busy, this part will create the file
			# platforms_not_launched.yml
			self.check_for_systems_not_launched()

			self.log.warning(
				'there is not platforms to launch intel-gpu-tools (fastfeedback)')
			utils.emailer(
				self.sender,
				self.mailing_list,
				'fastfeedback could not be launched on ({year}) '
				'(WW{week_number}) ({week_day}) ({hour})'.format(
					year=self.year, week_number=self.week_number, week_day=self.week_day,
					hour=self.hour),
				'fastfeedback could not be launched due to not platforms '
				'are available\n\n' + table.encode('utf-8'), silent=True)

			print(table.encode('utf-8'))
			sys.exit(0)


def arguments():

	parser = argparse.ArgumentParser(
		formatter_class=RawDescriptionHelpFormatter,
		description='''
	program description:
	(%(prog)s) is a tool for launch intel-gpu-tools fastfeedback executions
	project : https://01.org/linuxgraphics
	maintainer : humberto.i.perez.rodriguez@intel.com''',
		epilog='Intel® Graphics for Linux* | 01.org',
		usage='%(prog)s [options]')
	group1 = parser.add_argument_group(
		'({yellow}positional arguments{end})'.format(
			yellow=bash.YELLOW, end=bash.END))
	group1.add_argument(
		'-s', '--stack', dest='stack', action='store_true', default=None,
		help='set a graphic stack for the execution')
	group1.add_argument(
		'-k', '--kernel', dest='kernel', action='store_true', default=None,
		help='set a kernel for the execution')
	group1.add_argument(
		'-f', '--firmware', dest='firmware', action='store_true', default=None,
		help='set a platform with firmwares for the execution')
	group1.add_argument(
		'-v', '--visualization', dest='visualization', action='store_true',
		default=None, help='enabling reporting in visualization')
	group1.add_argument(
		'-r', '--report', dest='report', choices=['sand', 'prod'],
		default='sand',
		help='reporting to Test Report Center (default is reporting to sandbox)')
	group1.add_argument(
		'-g', '--grabsystemsbusy',
		action='store_true', dest='grabsystemsbusy', default=None,
		help='grab the systems in (platforms_not_launched.yml) and launch them '
		'with latest configuration')
	group1.add_argument(
		'-d', '--dryrun', dest='dryrun', action='store_true', default=None,
		help='do not setup any platform ({0}for debug purposes only{1})'
		.format(bash.BLUE, bash.END))
	args = parser.parse_args()

	IGTLauncher(
		stack=args.stack, kernel=args.kernel, firmware=args.firmware,
		visualization=args.visualization, report=args.report,
		grabsystemsbusy=args.grabsystemsbusy, dryrun=args.dryrun
	).orchestrator()


if __name__ == '__main__':
	arguments()
