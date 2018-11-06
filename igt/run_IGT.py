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

import datetime
import glob
import json
import os
import platform
import sys
import time
from os import listdir
from os.path import isfile
from os.path import join
from shutil import move
from time import sleep

import requests
import yaml

import igt.watchdog.dut_watcher as dutwatcher
from common import apiutils
from common import network
from common import remote_client
from gfx_qa_tools.common import bash
from gfx_qa_tools.common import log
from gfx_qa_tools.common import utils
from gfx_qa_tools.config import config
from igt.tools import getResult
from visualization import upload_visualization as upload_vis


class Data(object):
	def __init__(self):
		self.python_version = platform.python_version()
		self.distro = (
			platform.platform().split('with-')[1] if 'with-' in
			platform.platform() else platform.platform()
		)
		self.kernel = platform.release()
		# here we can add more suites for testing
		self.allowed_list = [
			'igt_fast_feedback', 'igt_all', 'igt_extended_list', 'igt_all_clone_mode',
			'igt_clone_testing'
		]
		self.this_path = os.path.dirname(os.path.abspath(__file__))
		self.hour = bash.get_output('date +%I-%M-%S')
		self.day = bash.get_output('date +%A').lower()
		self.data = yaml.load(open('/home/custom/config.yml'))
		self.email_sender = 'intel-gpu-tools@noreply.com'

		# logger setup
		dut_hostname = self.data['dut_conf']['dut_hostname']
		log_filename = 'run_igt.log'.format(dut_hostname)
		log_path = '{0}/logs'.format(os.path.dirname(os.path.abspath(__file__)))
		self.logger = log.setup_logging(
			'run_igt', level='info',
			log_file='{path}/{filename}'.format(path=log_path, filename=log_filename))

		# DUT configuration
		self.autologin = self.data['dut_conf']['autologin']
		self.dut_user = self.data['dut_conf']['dut_user']
		self.dut_password = self.data['dut_conf']['dut_password']
		self.dut_hostname = self.data['dut_conf']['dut_hostname']
		self.dut_static_ip = self.data['dut_conf']['dut_static_ip']
		self.graphical_environment = self.data['dut_conf']['graphical_environment']
		self.grub_parameters = self.data['dut_conf']['grub_parameters']
		# firmwares
		self.dmc = self.data['firmwares']['dmc']
		self.guc = self.data['firmwares']['guc']
		self.huc = self.data['firmwares']['huc']
		# raspberry configuration
		self.raspberry_gpio = self.data['raspberry_conf']['raspberry_gpio']
		self.raspberry_ip = self.data['raspberry_conf']['raspberry_ip']
		self.raspberry_number = self.data['raspberry_conf']['raspberry_number']
		self.raspberry_power_switch = self.data['raspberry_conf'][
			'raspberry_power_switch']
		self.raspberry_user = self.data['raspberry_conf']['raspberry_user']
		self.usb_cutter_serial = self.data['raspberry_conf']['usb_cutter_serial']
		# suite configuration
		self.blacklist_file = self.data['suite_conf']['blacklist_file']
		self.default_mailing_list = self.data['suite_conf']['default_mailing_list']
		self.default_package = self.data['suite_conf']['default_package']
		self.gfx_stack_code = self.data['suite_conf']['gfx_stack_code']
		self.kernel_branch = self.data['suite_conf']['kernel_branch']
		self.kernel_commit = self.data['suite_conf']['kernel_commit']
		self.igt_iterations = self.data['suite_conf']['igt_iterations']
		# autouploader information
		self.current_env = self.data['autouploader']['currentEnv']
		self.current_platform = self.data['autouploader']['currentPlatform']
		self.current_release = self.data['autouploader']['currentRelease']
		self.current_suite = self.data['autouploader']['currentSuite']
		self.current_tittle = self.data['autouploader']['currentTittle']
		self.report_trc = self.data['autouploader']['trc_report']
		# reports on linuxgraphics.intel.com
		self.backup_report = self.data['database']['upload_reports']
		# USB configuration
		self.custom_hostname = self.data['usb_conf']['custom_hostname']
		self.default_disk = self.data['usb_conf']['default_disk']
		self.default_image = self.data['usb_conf']['default_image']
		self.network_interface = self.data['usb_conf']['network_interface']
		self.server_user = self.data['usb_conf']['server_user']
		self.server_hostname = self.data['usb_conf']['server_hostname']
		self.server_partimag = self.data['usb_conf']['server_partimag']
		self.server_shared = self.data['usb_conf']['server_shared']
		self.usb_update_mode = self.data['usb_conf']['usb_update_mode']

		# miscellaneous
		self.igt_folder = '/home/{0}/intel-graphics/intel-gpu-tools'.format(
			self.dut_user)
		self.igt_test_root = '{0}/tests'.format(self.igt_folder)
		self.main_path = '{0}/scripts'.format(self.igt_folder)
		self.piglit_path = '{0}/piglit'.format(self.igt_folder)
		self.piglit = os.path.join(self.piglit_path, 'piglit')
		self.uptime_data = bash.get_output("awk '{print $0/60;}' /proc/uptime")
		# this are minutes
		self.igt_timestamp_file = os.path.join(
			'/home', self.dut_user, '.igt_timestamp')

		self.linuxgraphics_user = 'gfxserver'
		self.linuxgraphics_alias = 'linuxgraphics.intel.com'

		# checking internet connection
		network.set_proxy()

		# getting the networking boot time
		self.networking_boot_time = bash.get_output(
				"systemd-analyze blame | grep networking.service | "
				"awk '{print $1}'"
		)

		# getting the displays attached to the DUT
		self.displays_attached = None
		self.i915_display_info = '/sys/kernel/debug/dri/0/i915_display_info'
		if utils.isfile(self.i915_display_info):
			self.logger.info('(i915_display_info) is accessible')
			self.displays_attached = bash.get_output(
				"sudo cat /sys/kernel/debug/dri/0/i915_display_info | grep "
				"\"^connector\" | grep -we \"connected\" | awk -F\"type \" "
				"'{print $2}' | awk '{print $1}' | sed 's/,//g'").split()
			self.displaysDict = dict()
			self.displaysDict['attachedDisplays'] = {}
			for display in self.displays_attached:
				self.displaysDict['attachedDisplays'][display] = 'active'

		# getting the current testlist
		allowed_packages = [
			'igt_fast_feedback', 'igt_extended_list', 'igt_all', 'igt_clone_testing',
			'igt_generic_testing'
			]
		if self.default_package in allowed_packages:
			if self.default_package == 'igt_fast_feedback':
				self.current_testlist = 'fast-feedback.testlist'
			elif self.default_package == 'igt_extended_list':
				self.current_testlist = 'extended.testlist'
			elif self.default_package == 'igt_all':
				self.current_testlist = 'all.testlist'
			elif self.default_package == 'igt_clone_testing':
				self.current_testlist = 'clone.testlist'
			elif self.default_package == 'igt_generic_testing':
				self.current_testlist = 'generic.testlist'
		else:
			self.logger.error('{0} : is not recognized'.format(self.default_package))
			self.logger.info('the allowed packages are : ')
			for package in allowed_packages:
				self.logger.info(' - ({0})'.format(package))
			sys.exit(1)

		if self.current_testlist:
			self.current_testlist_path = os.path.join(
					self.igt_test_root, 'intel-ci', self.current_testlist)

		if os.path.exists(os.path.join(
			self.igt_test_root, 'intel-gpu-tools.testlist')):
			self.total_intel_gpu_tools_tests = os.path.join(
				self.igt_test_root, 'intel-gpu-tools.testlist')

		os.system('bash {path} start'.format(
			path=os.path.join(self.this_path, 'tools', 'banners.sh')))

		# generating a attachments folder
		self.attachments_folder = '/home/{0}/attachments'.format(self.dut_user)
		if not os.path.exists(self.attachments_folder):
			self.logger.info('creating attachment folder')
			os.makedirs(self.attachments_folder)

		# getting the current work week and year
		self.year, ww = apiutils.get_workweek(timeout=10)
		self.work_week = 'W{0}'.format(ww)

		# installing firmwares (if any)
		# TODO(Beto) so far the script of firmwares.py can not be called as
		# module since there is not a main() function, a refactoring is needed.
		os.system('python {0}'.format(
			os.path.join(self.this_path, 'firmwares', 'firmwares.py')))

		# make sure the loaded firmwares are the correct ones
		firmwares = json.loads(dutwatcher.get_firmware_version())
		guc = firmwares.get('guc', None)
		huc = firmwares.get('huc', None)
		dmc = firmwares.get('dmc', None)
		invalid_firmware = []
		if self.data['firmwares'].get('enforced', True):
			if self.guc and not guc:
				invalid_firmware.append('guc')
			if self.huc and not huc:
				invalid_firmware.append('huc')
			if self.dmc and not dmc:
				invalid_firmware.append('dmc')
		if invalid_firmware:
			# update the watchdog UI with a message about the failed validation
			apiutils.update_watchdog_db(
				self.raspberry_number,
				self.raspberry_power_switch,
				Status=(
					'Error: firmware validation is enforced and {firmware} failed '
					'to be loaded in the DUT'.format(firmware=invalid_firmware)
				)
			)
			# notify users by email
			utils.emailer(
				self.email_sender,
				self.default_mailing_list,
				'IGT execution could not be started on platform ({host}) ({ip}).'
				' Firmware validation failed.'
				.format(host=self.dut_hostname, ip=self.dut_static_ip),
				'Firmware validation failed in the platform. The following '
				'firmware was not found loaded in the platform {firmware} and '
				'firmware enforcement was enabled.\n'
				'Please make sure the firmware you selected is the correct one '
				'for the kernel.'
				.format(firmware=invalid_firmware)
			)
			# exit execution
			sys.exit(
				'No {firmware} firmware is loaded or is the wrong version'
				.format(firmware=invalid_firmware)
			)

		# disabling CUPS
		bash.disable_cups()

		# creating a file in order to get the overall IGT time
		if not os.path.isfile(self.igt_timestamp_file):
			self.logger.info('creating timestamp file for intel-gpu-tools execution')
			with open(self.igt_timestamp_file, 'w') as timestamp:
				timestamp.write('timestamp file for intel-gpu-tools execution')

		# getting the current environment for autoUploader.py
		if self.current_env == 'sand':
			self.trc_environment = 'sandbox'
		else:
			self.trc_environment = 'production'

		# control flag used to indicate whether a report was uploaded to
		# linuxgraphics or not
		self.report_uploaded = False

	def get_latest_iteration_folder(self):
		"""
		This function helps to get the latest iteration folder.
		"""

		# =================================
		# Getting the last iteration folder
		# =================================
		list_iteration_folders = \
			glob.glob(
				'/home/' + self.dut_user +
				'/intel-graphics/intel-gpu-tools/scripts/*iteration*')
		list_iteration_folders.sort()

		try:
			self.current_iteration_folder = list_iteration_folders[-1]
			self.json_path = \
				os.path.join(self.current_iteration_folder, 'tests')
			self.current_iteration_number = \
				self.current_iteration_folder.split('iteration')[1]
		except:
			self.current_iteration_folder = ''
			self.json_path = ''
			self.current_iteration_number = ''

	def merge_trc_report(self):
		"""
		This part is exclusive for clone testing (for now)
		This function helps to merge a csv from a existing TRC report
		"""

		try:
			state = self.data['autouploader']['state']
			merge = self.data['autouploader']['merge']
			trc_report_id = self.data['autouploader']['trc_report_id']
		except:
			bash.message(
				'warn',
				'(state/merge/trc_report_id) keys are not set in (config.yml)')
			return

		if self.default_package == 'igt_clone_testing':

			if os.path.exists(
				os.path.join('/home', self.dut_user, 'trc2.log')) \
					and state == 'master':

				url_link = \
					bash.get_output(
						'cat ' + os.path.join(
								'/home', self.dut_user, 'trc2.log'))
				bash.message(
					'info',
					'state for (' + self.current_platform + ') is (master)')
				bash.message('info', 'uploading TRC link to bifrost.intel.com')

				autouploader_create_link = \
					'http://10.219.106.111:2021' \
					'/autouploaderCreateLink?var_1=' + url_link + \
					'&var_2=' + self.current_platform + '&var_3=' + \
					self.current_env + '&var_4=' + self.current_release + \
					'&var_5=' + self.default_package + '&var_6=' + \
					self.current_tittle + '&var_7=' + trc_report_id
				bash.message('info', 'cmd (' + autouploader_create_link + ')')
				a = requests.get(autouploader_create_link)
				output = a.status_code

				if output == 200:
					bash.message(
						'info',
						'TRC link successfully created at bifrost.intel.com')
				else:
					bash.message(
						'err',
						'TRC link could not be created on bifrost.intel.com')
					bash.message('info', 'err code (' + str(output) + ')')

			elif not os.path.exists(
					os.path.join('/home', self.dut_user, 'trc2.log')) and \
				state == 'slave' and merge is True:

				# ======================
				# == Showing a banner ==
				# ======================
				os.system('bash ' + os.path.join(
					self.this_path, 'tools', 'banners.sh') + ' merge')

				bash.message(
					'info',
					'state for (' + self.current_platform + ') is (slave)')
				bash.message(
					'info',
					'getting TRC link from master system on bifrost.intel.com')
				autouploader_get_link = \
					'http://10.219.106.111:2021/' \
					'autouploaderGetLink?var_1=' + trc_report_id
				bash.message('info', 'cmd (' + autouploader_get_link + ')')
				a = requests.get(autouploader_get_link)
				output = a.status_code
				status = a.text.encode().split(',')[0]
				link = a.text.encode().split(',')[1].rstrip()

				if output == 200:
					bash.message(
						'info',
						'connection successfully with bifrost.intel.com API')
					bash.message(
							'info',
							'checking if the TRC report from master system '
							'is created on bifrost.intel.com')

					if status == 'waiting':
						bash.message(
							'info', 'TRC report state is (waiting)')
						bash.message(
							'info', 'checking again in 30 seconds ...')
						sleep(30)

						while True:
							a = requests.get(autouploader_get_link)
							status = a.text.encode().split(',')[0]
							link = a.text.encode().split(',')[1]

							if status == 'waiting':
								bash.message(
									'info', 'TRC report state is (waiting)')
								bash.message(
									'info', 'checking again in 30 seconds ...')
								sleep(30)

							elif status == 'done':
								bash.message(
									'info',
									'TRC report found in bifrost.intel.com')
								bash.message(
									'info',
									'merging this current csv file (' +
									output_trc_name + ') with the report (' +
									link.rstrip() + ')')
								bash.message(
									'info',
									'cmd (' + 'python  ' +
									os.path.join(
										'/home', self.dut_user, 'gfx-qa-tools', 'igt',
										'autouploader', 'mergeTRCLink.py') +
									' ' + link.rstrip() + ' ' +
									os.path.join(
										output_dir, output_trc_name) + ')')

								output = \
									os.system(
										'python ' +
										os.path.join(
											'/home', self.dut_user, 'gfx-qa-tools',
											'igt', 'autouploader',
											'mergeTRCLink.py') + ' ' +
										link.rstrip() + ' ' +
										os.path.join(
											output_dir, output_trc_name))

								bash.message(
									'info',
									'mergeTRCLink.py output (' +
									str(output) + ')')
								break

					elif status == 'done':
						bash.message(
							'info',
							'merging this current csv (' +
							output_trc_name + ') file with (' +
							link.rstrip() + ')')
						bash.message(
							'info',
							'cmd (' + 'python  ' +
							os.path.join(
								'/home', self.dut_user, 'gfx-qa-tools', 'igt',
								'autouploader', 'mergeTRCLink.py') +
							' ' + link.rstrip() + ' ' +
							os.path.join(
								output_dir, output_trc_name) + ')')

						output = \
							os.system(
								'python ' +
								os.path.join(
									'/home', self.dut_user, 'gfx-qa-tools', 'igt',
									'autouploader', 'mergeTRCLink.py') +
								' ' + link.rstrip() + ' ' +
								os.path.join(output_dir, output_trc_name))

						bash.message(
							'info',
							'mergeTRCLink.py output (' + str(output) + ')')
				else:
					bash.message('info', 'err code (' + str(output) + ')')

			elif not os.path.exists(
				os.path.join('/home', self.dut_user, 'trc2.log')):
				bash.message(
					'err',
					'(' + os.path.join('/home', self.dut_user, 'trc2.log') +
					') does not exists')

	def create_attachments(self):
		"""
		This function creates attachments for TRC and linuxgraphics server.
		"""

		bash.message('info', 'creating attachments for TRC ...')

		# =======================================
		# === getting latest_iteration_folder ===
		# =======================================
		self.get_latest_iteration_folder()
		# m_date_today = bash.get_output('date +"%Y-%m-%d"')
		hour = bash.get_output('date +%I-%M-%S')

		if self.default_package == 'igt_clone_testing':
			trc_report_id = self.data['autouploader']['trc_report_id']
			ci_backup_message_link = \
				'Please find this report as well in (' + bash.CYAN + \
				os.path.join(
					'http://linuxgraphics.intel.com/igt-reports',
					self.year, self.default_package, self.current_platform,
					'id__' + trc_report_id, self.work_week, self.day,
					hour + bash.END + ')')
			ci_backup_message_link_clean = \
				'Please find this report as well in (' + \
				os.path.join(
					'http://linuxgraphics.intel.com/igt-reports', self.year,
					self.default_package, self.current_platform,
					'id__' + trc_report_id, self.work_week, self.day,
					hour + ')')
			ci_link = os.path.join(
				'http://linuxgraphics.intel.com/igt-reports', self.year,
				self.default_package, self.current_platform,
				'id__' + trc_report_id, self.work_week, self.day, hour)
		else:
			ci_backup_message_link = \
				'Please find this report as well in (' + bash.CYAN + \
				os.path.join(
					'http://linuxgraphics.intel.com/igt-reports', self.year,
					self.default_package, self.current_platform,
					self.work_week, self.day, hour + bash.END + ')')
			ci_backup_message_link_clean = \
				'Please find this report as well in (' + \
				os.path.join(
					'http://linuxgraphics.intel.com/igt-reports', self.year,
					self.default_package, self.current_platform,
					self.work_week, self.day, hour + ')')
			ci_link = os.path.join(
				'http://linuxgraphics.intel.com/igt-reports', self.year,
				self.default_package, self.current_platform, self.work_week,
				self.day, hour)

		# ===============================
		# === getting trc attachments ===
		# ===============================

		files = [
			os.path.join(output_dir, 'runtime.log'),
			os.path.join(
				output_dir, output_backtrace_name),
			os.path.join(output_dir, output_runtime_name)
			]

		for element in files:
			bash.message(
				'info',
				'copying (' + os.path.basename(element) + ') to (' +
				self.attachments_folder + ')')
			os.system('cp ' + element + ' ' + self.attachments_folder)

		# ========================================
		# Iterating over ../iteration1/html folder
		# ========================================
		files_list = []

		for (dirpath, dirnames, filenames) in os.walk(os.path.join(
				self.main_path, 'iteration1', 'html')):
			files_list.extend(filenames)

		for element in files_list:
			if element.startswith('igt@'):
				continue
			else:
				bash.message(
					'info',
					'copying (' + element + ') to (' +
					self.attachments_folder + ')')
				os.system(
					'cp ' +
					os.path.join(
						self.main_path, 'iteration1', 'html', element) +
					' ' + self.attachments_folder)

		# ===========================
		# iterating over /home/custom
		# ===========================

		for element in os.listdir(os.path.join('/home', 'custom')):
			if os.path.isfile(os.path.join('/home', 'custom', element)):
				bash.message(
					'info',
					'copying (' + element + ') to (' +
					self.attachments_folder + ')')
				os.system(
					'cp ' +
					os.path.join('/home', 'custom', element) + ' ' +
					self.attachments_folder)

		# ==================================================
		# Iterating over /home/custom/graphic_stack/packages
			# ==================================================

		for element in os.listdir('/home/custom/graphic_stack/packages'):
			if os.path.isfile(
				os.path.join('/home/custom/graphic_stack/packages', element)):
				if os.path.splitext(element)[1][1:].strip() == 'deb':
					continue
				else:
					bash.message(
						'info',
						'copying (' + element + ') to (' +
						self.attachments_folder + ')')
					if element == 'config.cfg':
						os.system(
							'cp ' +
							os.path.join(
								'/home/custom/graphic_stack/packages',
								element) +
							' ' + os.path.join(
									self.attachments_folder, 'gfx_stack.cfg'))

					elif element == 'easy-bugs':
						os.system(
							'cp ' +
							os.path.join(
								'/home/custom/graphic_stack/packages',
								element) + ' ' +
							os.path.join(
								self.attachments_folder,
								'gfx_stack_easy_bugs.cfg'))

		# ===========================================
		# Iterating over /home/custom/kernel/packages
		# ===========================================

		for element in os.listdir('/home/custom/kernel/packages'):
			if os.path.isfile(
				os.path.join('/home/custom/kernel/packages', element)):
				if os.path.splitext(element)[1][1:].strip() == 'deb':
					continue
				else:
					bash.message(
						'info',
						'copying (' + element + ') to (' +
						self.attachments_folder + ')')
					os.system(
						'cp ' +
						os.path.join(
							'/home', 'custom', 'kernel', 'packages', element) +
						' ' + os.path.join(
								self.attachments_folder,
								'kernel_commit_information.cfg'))

		# =============================
		# Getting the original testlist
		# =============================
		if int(self.current_iteration_number) == 1:
			testlist = self.current_testlist_path
		else:
			testlist = \
				bash.get_output(
					'ls ' +
					os.path.join(
						self.igt_test_root, 'intel-ci', 'tmp.d') +
					'| sort -n | head -1')

			testlist = os.path.join(
				self.igt_test_root, 'intel-ci', 'tmp.d', testlist)

		bash.message(
			'info',
			'copying (' + self.current_testlist + ') to (' +
			self.attachments_folder + ')')
		os.system(
			'cp ' + testlist + ' ' +
			os.path.join(self.attachments_folder, self.current_testlist))

		bash.message(
			'info',
			'copying (results.json) to (' + self.attachments_folder + ')')
		os.system(
			'cp ' +
			os.path.join(self.main_path, 'iteration1', 'results.json') + ' ' +
			self.attachments_folder)
		bash.message('info', 'compressing results.json')
		os.system(
			'cd ' + self.attachments_folder +
			'; tar cvzf results.json.tar.gz ' +
			os.path.join(self.attachments_folder, 'results.json') +
			' 2> /dev/null; rm results.json 2> /dev/null')

		bash.message(
			'info',
			'checking if (' +
			os.path.basename(self.attachments_folder) +
			') files does not exceed for 10MB')

		for element in os.listdir(self.attachments_folder):
			if os.path.isfile(os.path.join(self.attachments_folder, element)):
				file_size = \
					int(bash.get_output(
							'du -s ' +
							os.path.join(
								self.attachments_folder, element) +
							'| awk \'{print $1}\''))
				file_size_limit = 10000

				if file_size > file_size_limit:
					bash.message(
						'warn',
						'(' + element + ') exceed the file size for TRC, '
						'deleting ...')
					os.system(
						'rm -rf ' +
						os.path.join(self.attachments_folder, element))
				elif file_size < file_size_limit:
					bash.message(
						'info',
						'(' + element + ') (' + str(file_size) +
						'KB) has the correct file size for TRC')

		bash.message('info', 'getting displays information')
		output = os.system(
				'sudo ls /sys/kernel/debug/dri/0/i915_display_info &> '
				'/dev/null')

		if output == 0:
			bash.message(
				'info',
				'(i915_display_info) is accessible')
			os.system(
				'sudo cat /sys/kernel/debug/dri/0/i915_display_info > ' +
				os.path.join(self.attachments_folder, 'attachedDisplays.cfg'))
		else:
			bash.message(
				'warn',
				'(i915_display_info) file does not exists into'
				'(/sys/kernel/debug/dri/0/i915_display_info)')
			with open(
					os.path.join(
						self.attachments_folder, 'attachedDisplays.cfg'),
					'w') as i915_f:
				i915_f.write(
						'warning : (i915_display_info) file does not '
						'exists into /sys/kernel/debug/dri/0/ \n')

		# ============================================
		# showing a banner for igt_clone_testing suite
		# ============================================

		if self.default_package == 'igt_clone_testing' and \
					self.data['autouploader']['state'] == 'master':
			os.system(
				'bash ' + os.path.join(
						self.this_path, 'tools', 'banners.sh master'))
		elif self.default_package == 'igt_clone_testing' and \
			self.data['autouploader']['state'] == 'slave':
			os.system(
				'bash ' +
				os.path.join(self.this_path, 'tools', 'banners.sh slave'))

		if self.report_trc is True:
			bash.message(
				'info',
				'uploading a new report to TRC (' + self.trc_environment +
				') database')

			# ===============================================
			# creating backupReport.log in attachments folder
			# ===============================================

			if self.backup_report:
				if self.default_package == 'igt_clone_testing':
					state = self.data['autouploader']['state']
					current_tests_bunch = \
						self.data['autouploader']['current_tests_bunch']
					backup_report_file = \
						os.path.join(
							self.attachments_folder,
							'backupReport__' + self.dut_hostname + '_' +
							state + '_bunch_' + current_tests_bunch + '__.log')

					if not os.path.exists(backup_report_file):
						bash.message(
							'info',
							'creating (' +
							os.path.basename(backup_report_file) +
							') in (' + self.attachments_folder + ')')
						os.system(
							'echo "' + ci_backup_message_link_clean +
							'" > ' + backup_report_file)
				else:
					backup_report_file = \
						os.path.join(
							self.attachments_folder, 'backupReport.log')
					if not os.path.exists(backup_report_file):
						bash.message(
							'info',
							'creating (' +
							os.path.basename(backup_report_file) + ') in (' +
							self.attachments_folder + ')')
						os.system(
							'echo "' + ci_backup_message_link_clean + '" > ' +
							backup_report_file)

			# ========================================
			# Generating a command for autoUploader.py
			# ========================================
			bash.message('info', 'Generating a command for autoUploader.py')
			os.system(
				'echo "python ' +
				os.path.join(
					'/home', self.dut_user, 'gfx-qa-tools', 'igt', 'autouploader',
					'autoUploader.py') + ' -s \'' +
				self.current_suite + '\' -r ' + self.current_release + ' -t ' +
				self.current_tittle + ' -p ' + self.current_platform + ' -f ' +
				os.path.join(output_dir, output_trc_name) + ' -a ' +
				self.attachments_folder + ' -e ' + self.trc_environment  +
				' -o intel-gpu-tools -g graphic-stack " > ' +
				os.path.join(
					'/home', self.dut_user, 'python__trc__command.log'))
			output = \
				os.system(
					'python ' +
					os.path.join(
						'/home', self.dut_user, 'gfx-qa-tools', 'igt', 'autouploader',
						'autoUploader.py') + ' -s \'' + self.current_suite +
					'\' -r ' + self.current_release + ' -t ' +
					self.current_tittle + ' -p ' + self.current_platform +
					' -f ' + os.path.join(output_dir, output_trc_name) +
					' -a ' + self.attachments_folder + ' -e ' +
					self.trc_environment  + ' -o intel-gpu-tools -g graphic-stack')

			if output == 0:
				bash.message(
					'info',
					'(autoUploader.py) was executed successfully with' 
					'code (' + str(output) + ')')

				# ========================================
				# Creating TRC report on bifrost.intel.com
				# ========================================
				if os.path.exists(
					os.path.join('/home', self.dut_user, 'trc2.log')):
					global trc_link
					trc_link = \
						bash.get_output(
							'cat ' + os.path.join(
									'/home', self.dut_user, 'trc2.log'))
				else:
					bash.message(
						'err',
						'file (' +
						os.path.join(
							'/home', self.dut_user, 'trc2.log') +
						') does not exists')
			else:
				bash.message(
					'err',
					'(autoUploader.py) command was executed with error (' +
					str(output) + ')')
		else:
			bash.message(
				'warn',  '(trc_report) value is set to False in (config.yml)')

		if self.backup_report is True:

			# ========================================
			# Creating TRC report on bifrost.intel.com
			# ========================================

			# ================================================
			# Creating backupReport.log in attachments folders
			# ================================================

			if self.default_package == 'igt_clone_testing':
				state = self.data['autouploader']['state']
				current_tests_bunch = \
					self.data['autouploader']['current_tests_bunch']

				backup_report_file = \
					os.path.join(
						self.attachments_folder,
						'backupReport__' + self.dut_hostname + '_' + state +
						'_bunch_' + current_tests_bunch + '__.log')

				if not os.path.exists(backup_report_file):
					bash.message(
						'info',
						'creating (' +
						os.path.basename(backup_report_file) + ') in (' +
						self.attachments_folder + ')')
					os.system(
						'echo "' + ci_backup_message_link_clean + '" > ' +
						backup_report_file)
			else:
				backup_report_file = \
					os.path.join(self.attachments_folder, 'backupReport.log')

				if not os.path.exists(backup_report_file):
					bash.message(
						'info',
						'creating (' + os.path.basename(backup_report_file) +
						') in (' + self.attachments_folder + ')')
					os.system(
						'echo "' + ci_backup_message_link_clean + '" > ' +
						backup_report_file)

			bash.message(
				'info',
				'adding more files to (' + self.attachments_folder +
				') for upload them to (linuxgraphics.intel.com)')
			bash.message(
				'info',
				'creating i915 folder into (' + self.attachments_folder + ')')
			i915_folder = os.path.join(self.attachments_folder, 'i915')
			os.system('mkdir -p ' + i915_folder)
			bash.message(
				'info',
				'creating scan folder into (' + self.attachments_folder + ')')
			scan_folder = os.path.join(self.attachments_folder, 'scan')
			os.system('mkdir -p ' + scan_folder)
			os.system('sudo blkid > ' + os.path.join(scan_folder, 'blkid'))
			os.system(
				'cat /proc/cpuinfo  > ' + os.path.join(scan_folder, 'cpuinfo'))
			os.system(
				'sudo dmidecode > ' + os.path.join(scan_folder, 'dmidecode'))
			os.system('sudo fdisk -l > ' + os.path.join(scan_folder, 'fdisk'))
			os.system(
				'lsb_release -a 2> /dev/null > ' +
				os.path.join(scan_folder, 'lsb_release'))
			os.system('lsblk > ' + os.path.join(scan_folder, 'lsblk'))
			os.system('sudo lshw > ' + os.path.join(scan_folder, 'lshw'))
			os.system('lspci > ' + os.path.join(scan_folder, 'lspci'))
			os.system('vmstat -s > ' + os.path.join(scan_folder, 'vmstat'))
			os.system(
				'cat /proc/meminfo  > ' + os.path.join(scan_folder, 'meminfo'))
			os.system('uname -a  > ' + os.path.join(scan_folder, 'uname'))
			os.system(
				'sudo parted -l -s 2> /dev/null > ' +
				os.path.join(scan_folder, 'parted'))
			os.system('cat /etc/fstab > ' + os.path.join(scan_folder, 'fstab'))
			os.system(
				'cat /etc/default/grub > ' +
				os.path.join(scan_folder, 'grub'))

			# =============================================
			# Copying trc csv results to attachments folder
			# =============================================
			os.system(
				'cp ' + os.path.join(output_dir,output_trc_name) + ' ' +
				self.attachments_folder)

			# ==========================================
			# Erasing some files into attachments folder
			# ==========================================
			ext = [
				'html',
				'css'
				]

			for element in os.listdir(self.attachments_folder):
				if os.path.isfile(
					os.path.join(self.attachments_folder, element)):
					if os.path.splitext(element)[1][1:].strip() in ext:
						bash.message('info', 'deleting (' + element + ')')
						os.system(
							'rm -rf ' +
							os.path.join(self.attachments_folder,element))

			# ===================================
			# Copying html folder from iteration1
			# ===================================
			os.system(
				'cp -R ' +
				os.path.join(self.main_path, 'iteration1', 'html') + ' ' +
				self.attachments_folder)

			# =================================================
			# Creating visualization file in attachments folder
			# =================================================
			try:
				if self.data['autouploader']['visualization'] == 'true':
					bash.message(
						'info',
						'creating a visualization file into (' +
						self.attachments_folder + ')')
					os.system(
						'touch ' +
						os.path.join(self.attachments_folder, 'visualization'))

					# extract and rename the file only if visualization is YES
					report_name = 'results.json.tar.gz'
					tar_file = os.path.join(self.attachments_folder, report_name)
					upload_vis.extract_report_to_vis(tar_file, self.attachments_folder)

			except:
				bash.message('warn', '(visualization) key is not set')

			i915_files = \
				bash.get_output(
					'sudo ls /sys/kernel/debug/dri/0 | grep i915').split()

			for element in i915_files:
				if element == 'i915_gpu_info':
					# ==========================================
					# when BXT is trying to copy/view this file,
					# it causes a gpu hang
					# ==========================================
					continue
				bash.message(
					'info',
					'copying (' + element + ') to (' + i915_folder + ')')
				os.system(
					'sudo cp ' +
					os.path.join('/sys/kernel/debug/dri/0', element) + ' ' +
					i915_folder + ' 2> /dev/null')

			if self.default_package == 'igt_clone_testing':
				trc_report_id = self.data['autouploader']['trc_report_id']
				path_upload_reports = \
					os.path.join(
						'/var/www/html/reports/intel-gpu-tools', self.year,
						self.default_package, self.current_platform,
						'id__' + trc_report_id, self.work_week, self.day, hour)
			else:
				path_upload_reports = \
					os.path.join(
						'/var/www/html/reports/intel-gpu-tools', self.year,
						self.default_package, self.current_platform,
						self.work_week, self.day,hour)

			# to aviod duplicating reports, make sure the report doesn't already
			# exist in the server
			output = \
				os.system(
					'timeout 2 ssh -C -o "StrictHostKeyChecking no" -o '
					'ConnectTimeout=1 -q ' + self.linuxgraphics_user + '@' +
					self.linuxgraphics_alias + ' [ -d ' +
					path_upload_reports + ' 2> /dev/null ]')

			if output == 0:
				bash.message(
					'warn',
					'this report exists on (' + self.linuxgraphics_alias +
					'), omitting it ...')
			else:
				bash.message(
					'info',
					'uploading report to (' + self.linuxgraphics_alias + ')')
				bash.message(
					'info',
					'creating a folder in (' + self.linuxgraphics_alias + ')')

				# create the directory for the report in the server
				check_bkp_dir_limit = time.time() + 60
				while check_bkp_dir_limit > time.time():
					os.system(
						'ssh ' + self.linuxgraphics_user + '@' +
						self.linuxgraphics_alias + ' "mkdir -p "' +
						path_upload_reports + ' &> /dev/null')
					check_dir = os.system(
						'ssh -C -o "StrictHostKeyChecking'
						' no" -o ConnectTimeout=1 -q ' +
						self.linuxgraphics_user + '@' +
						self.linuxgraphics_alias + ' [ -d ' +
						path_upload_reports + ' ]')
					if not check_dir:
						break
				bash.message(
					'info',
					'changing owner (' + self.attachments_folder + ') to (' +
					self.dut_user + ')')
				os.system(
					'sudo chown -R ' + self.dut_user + '.' + self.dut_user +
					' ' + self.attachments_folder)

				bash.message(
					'info',
					'uploading (' + os.path.basename(self.attachments_folder) +
					') folder')

				bash.message(
					'cmd',
					'scp -o "StrictHostKeyChecking no" -r ' +
					self.attachments_folder + '/* ' +
					self.linuxgraphics_user + '@' +
					self.linuxgraphics_alias + ':' +
					path_upload_reports + ' &> /dev/null')

				# path's lists to copy into build_id
				paths_to_copy = [self.attachments_folder + '/*']

				visualization_flag = False

				# this boolean value comes from config.yml
				if self.data['autouploader']['visualization'] == 'true':

					visualization_flag = True

				visualization_data = self.data.get('build_information', False)

				# this code only will runs if 'build_information' key
				# on config.yml does not provide a dict.
				if not isinstance(visualization_data, type({})):

					# Try to retrieve the build_information for generate build_id
					visualization_data = apiutils.get_build_id_dict(
						graphic_stack_code=self.gfx_stack_code,
						kernel_commit=self.kernel_commit,
						kernel_branch=self.kernel_branch,
						suite=self.default_package
					)
					self.logger.info('visualization was uploaded')

					# If API does not return a dict that contains build_id data
					# we have to use default values from VIS_DEFAULT_DICT
					if not isinstance(visualization_data, type({})):
						visualization_data = upload_vis.VIS_DEFAULT_DICT
						visualization_flag = False

				# upload and generate new visualization
				upload_vis.initialize_visualization(
					visualization_data,
					self.default_package,
					self.current_platform,
					paths_to_copy,
					visualization_flag
				)

				# ============================================
				# Uploading results to linuxgraphics.intel.com
				# ============================================
				self.logger.info('uploading report to linuxgraphics.intel.com')

				# sometimes Piglit takes some time to generate the results
				# files so it is necessary to wait until the files exist
				trc_csv = os.path.join(self.attachments_folder, output_trc_name)
				results_tar = os.path.join(self.attachments_folder, 'results.json.tar.gz')
				results_timeout = config.getint('igt', 'report_generation_timeout') * 60
				results_generation_timeout = time.time() + results_timeout
				results_exist = True
				self.logger.info('waiting for Piglit to finish creating the result files')
				while not (os.path.isfile(trc_csv) and os.path.isfile(results_tar)):
					if time.time() > results_generation_timeout:
						results_exist = False
						failure_message = (
							'the result files were not generated within the '
							'timeout of 60 seconds')
						self.logger.warning(failure_message)

				if results_exist:
					# copy the files to linuxgraphics
					self.logger.info('copying files to linuxgraphics.intel.com')
					upload_command = (
						'scp -o "StrictHostKeyChecking no" -r {attachments_path}/* '
						'{user}@{host}:{path} &> /dev/null'
						.format(
							attachments_path=self.attachments_folder,
							user=self.linuxgraphics_user,
							host=self.linuxgraphics_alias,
							path=path_upload_reports
						)
					)
					error_code, output = bash.run_command(upload_command)
					if not error_code:
						# make sure all files got copied to linuxgraphics
						self.logger.info('verifying all files were copied')
						lgclient = remote_client.RemoteClient(
							self.linuxgraphics_alias, user=self.linuxgraphics_user)
						local_content = (
							bash.run_command(
								"find {0} -type f -printf '%f\n'"
								.format(self.attachments_folder))[1].split()
						)
						remote_content = (
							lgclient.run_command(
								"find {0} -type f -printf '%f\n'"
								.format(path_upload_reports))[1].split()
						)
						missing_files = [
							item for item in local_content if item not in remote_content]
						if not missing_files:
							self.report_uploaded = True
						else:
							failure_message = (
								'the following files failed to be uploaded: {0}'.format(missing_files))
							self.logger.warning(failure_message)
					else:
						failure_message = (
							'there was an error while copying files to the server ({code}): {msg}'
							.format(code=error_code, msg=output))
						self.logger.warning(failure_message)

				# if the report could not be uploaded for some reason notify it
				if not self.report_uploaded:
					# send message to watchdog
					apiutils.update_watchdog_db(
						self.raspberry_number,
						self.raspberry_power_switch,
						Status='Report failed to be uploaded to linuxgraphics'
					)
					# email maintainers
					utils.emailer(
						self.email_sender,
						self.default_mailing_list,
						'Report failed to be uploaded to linuxgraphics on {host} ({ip})'
						.format(host=self.dut_hostname, ip=self.dut_static_ip),
						failure_message
					)

				# ============================================
				# Generating a new visualization webpage into
				# linuxgraphics.intel.com
				# ============================================
				try:
					self.logger.info('trying to generate a new visualization')

					if self.data['autouploader']['visualization'] == 'true':
						allowed_visualization_packages = \
							[
								'igt_fast_feedback',
								'igt_all'
							]

						if self.default_package not in \
							allowed_visualization_packages:
							bash.message(
								'warn',
								'this package (' + self.default_package +
								') is not allowed to generated '
								'visualization webpage on '
								'(linuxgraphics.intel.com)')
						else:

							self.logger.info(
									'visualization: suite: {0}'.format(
										self.default_package
									)
							)

							output_vis = upload_vis.generate_visualization(self.default_package)

							self.logger.info(
								'new visualization generate successfully, output: {0}'.format(
									output_vis
								)
							)

							bash.message(
								'info',
								'Generating a new visualization webpage '
								'into linuxgraphics.intel.com for (' +
								self.default_package + ')')
							cmd = \
								'timeout 120 ssh -C -o ' \
								'"StrictHostKeyChecking no" -o ' \
								'ConnectTimeout=1 -q ' + \
								self.linuxgraphics_user + '@' + \
								self.linuxgraphics_alias + ' python ' + \
								os.path.join(
									'/home', self.linuxgraphics_user,
									'visualization', 'vis.py') + \
								' -o ' + \
								os.path.join(
									'/var', 'www', 'html', 'reports',
									'intel-gpu-tools', self.year,
									self.default_package, 'visualization',
									'index.html') + \
								' -t ' + self.default_package + \
								' &> /dev/null'
							bash.message('info', cmd)

							output = \
								os.system(
									'timeout 120 ssh -C -o '
									'"StrictHostKeyChecking no" -o '
									'ConnectTimeout=1 -q ' +
									self.linuxgraphics_user + '@' +
									self.linuxgraphics_alias + ' python ' +
									os.path.join(
										'/home', self.linuxgraphics_user,
										'visualization', 'vis.py') +
									' -o ' + os.path.join(
											'/var', 'www', 'html',
											'reports', 'intel-gpu-tools',
											self.year, self.default_package,
											'visualization', 'index.html') +
									' -t ' + self.default_package +
									' &> /dev/null')

							if output == 0:
								bash.message(
									'info',
									'visualization webpage has been generated'
									' successfully for this (' +
									self.dut_hostname + ')')
							else:
								bash.message(
									'err',
									'could not be generating visualization'
									' webpage for this (' +
									self.dut_hostname + ')')

				except:
					bash.message(
						'warn', '(visualization) key is not set')

				try:
					bash.message(
						'info',
						'TRC report (' + bash.CYAN + trc_link + bash.END + ')')
				except:
					bash.message(
						'warn',
						'(trc_report) value is set to False in (config.yml)')

				bash.message('info', ci_backup_message_link)
				os.system(
					'echo "' + ci_link + '" > ' +
					os.path.join('/home', self.dut_user, 'backupReport.log'))
		else:
			bash.message(
				'warn',
				'(upload_reports) value is set to False in (config.yml)')

		# ============================
		# intel-gpu-tools has finished
		# ============================
		json_final_file = os.path.join(self.main_path, 'iteration1', 'results.json')
		self.logger.info('intel-gpu-tools has finished')
		getResult.getStatisticsfromJson(json_final_file, 'all', None)

		# ===================
		# merging TRC report
		# ===================
		self.merge_trc_report()

	def get_eta(self, total_tests):
		"""
		:param total_tests: the total number of json executed by piglit
		:return: estimated time of arrival for intel-gpu-tools test cases
		"""
		only_files = \
			[
				f for f in listdir(self.json_path)
				if isfile(join(self.json_path, f))]

		seconds_list = []
		total_seconds, current_tests, count = (0,)*3

		for element in only_files:
			current_tests += 1
			with open(os.path.join(self.json_path, element)) as json_file:
				json_data = json.load(json_file)
			for key, value in json_data.iteritems():
				go_time = value['time']['start']
				final_time = value['time']['end']
				elapsed_seconds = int(final_time) - int(go_time)
				total_seconds += (elapsed_seconds)
				seconds_list.append(elapsed_seconds)

		list_length = len(seconds_list)
		seconds_average = total_seconds / list_length
		# =======================================
		# this is the average of seconds per test
		# =======================================
		# minutes_average = seconds_average / 60 % 60
		# HoursAverage = minutes_average / 60
		remaining_tests = int(total_tests) - int(current_tests)

		eta_seconds = seconds_average * remaining_tests
		eta_seconds = format(eta_seconds, '.0f')
		remaining_time = str(datetime.timedelta(seconds=float(eta_seconds)))

		eta = {'dut_eta': {'time': str(remaining_time.replace('-', ''))}}
		return eta

	def statistics(self):
		"""
		This function obtain the current intel-gpu-tools statistics from json
		files in the current iteration folder.
		"""
		print('===========================================')
		bash.message('info', 'intel-gpu-tools statistics')

		with open(self.current_testlist_path) as f:
			testlist_test_cases = sum(1 for line in f)

		with open(self.total_intel_gpu_tools_tests) as f:
			overall_test_cases = sum(1 for line in f)

		percentage_to_run = \
			round(testlist_test_cases * 100 / float(overall_test_cases), 2)

		bash.message(
			'statistics',
			'Overall test cases (' + str(overall_test_cases) + ')')
		bash.message(
			'statistics',
			'Test to run (' + str(testlist_test_cases) + ')')
		bash.message(
			'statistics',
			'Percentage to run (' + str(percentage_to_run) + '%)')

		if self.current_iteration_folder:
			if os.path.exists(
				os.path.join(self.current_iteration_folder, 'tests')):
				path, dirs, files = \
					os.walk(os.path.join(
							self.current_iteration_folder, 'tests')).next()
				current_json_files = len(files)
				current_progress_percentage = \
					round(current_json_files * 100 / float(
							testlist_test_cases), 2)
				bash.message(
					'statistics',
					'Current progress (' +
					str(current_json_files) + '/' +
					str(testlist_test_cases) + ') (' +
					str(current_progress_percentage) + '%)')

				# ==========================================
				# Declaring variables for overall statistics
				# ==========================================
				pass_tests, fail_tests, crash_tests, skip_tests,\
					timeout_tests, incomplete_tests, dmesg_warn_tests, \
					warn_tests, dmesg_fail_tests, not_run = (0,)*10

				only_files = \
					[
						f for f in listdir(self.json_path)
						if isfile(join(self.json_path, f))]

				for element in only_files:
					with open(os.path.join(
							self.json_path, element)) as json_file:
						json_data = json.load(json_file)
						for key, value in json_data.iteritems():
							result = value['result'].encode()
							if result == "pass":
								pass_tests += 1
							elif result == "fail":
								fail_tests += 1
							elif result == "crash":
								crash_tests += 1
							elif result == "skip":
								skip_tests += 1
							elif result == "timeout":
								timeout_tests += 1
							elif result == "incomplete":
								incomplete_tests += 1
							elif result == "dmesg-warn":
								dmesg_warn_tests += 1
							elif result == "warn":
								warn_tests += 1
							elif result == "dmesg-fail":
								dmesg_fail_tests += 1
							elif result == "not_run":
								not_run += 1

				if pass_tests:
					bash.message(
						'statistics', 'pass (' + str(pass_tests) + ')')
				if fail_tests:
					bash.message(
						'statistics', 'fail (' + str(fail_tests) + ')')
				if crash_tests:
					bash.message(
						'statistics', 'crash (' + str(crash_tests) + ')')
				if skip_tests:
					bash.message(
						'statistics', 'skip (' + str(skip_tests) + ')')
				if timeout_tests:
					bash.message(
						'statistics', 'timeout (' + str(timeout_tests) + ')')
				if incomplete_tests:
					bash.message(
						'statistics',
						'incomplete (' + str(incomplete_tests) + ')')
				if dmesg_warn_tests:
					bash.message(
						'statistics',
						'dmesg-warn (' + str(dmesg_warn_tests) + ')')
				if warn_tests:
					bash.message(
						'statistics', 'warn (' + str(warn_tests) + ')')
				if dmesg_fail_tests:
					bash.message(
						'statistics',
						'dmesg-fail (' + str(dmesg_fail_tests) + ')')
				if not_run:
					bash.message(
						'statistics', 'not-run (' + str(not_run) + ')')
				try:
					total_pass_rate = \
						pass_tests + fail_tests + crash_tests + \
						timeout_tests + dmesg_warn_tests + warn_tests + \
						dmesg_fail_tests
					pass_rate_of_executed = \
						str(round((pass_tests + dmesg_warn_tests + warn_tests)
										* 100 / float(total_pass_rate), 2)) + \
						'%'
					bash.message(
						'statistics',
						'pass rate (' + str(pass_rate_of_executed) + ')')
				except:
					bash.message('warn', 'pass rate could not print')

		print ('===========================================')

	def preconditions(self):
		"""
		This function check all the preconditions needed for run
		intel-gpu-tools, if any of this preconditions are not met this
		function will exit of the program.
		"""

		# ===========================================================
		# Checking if the self.default_package is in the allowed list
		# ===========================================================

		if self.default_package not in self.allowed_list:
			bash.message(
				'err',
				'this default package (' + self.default_package +
				') in config.yml is now allowed yet')
			bash.message(
				'info',
				'Please contact to system administrator '
				'(humberto.i.perez.rodriguez@intel.com)')
			bash.message('info', 'sending a email notification')
			utils.emailer(
				self.email_sender,
				self.default_mailing_list,
				'default package not allowed on (' + self.dut_hostname +
				')',
				'an error was occured trying to run intel-gpu-tools '
				'on (' + self.dut_hostname + ')\nthe following package is not'
				'allowed (' + self.default_package + ')')
			sys.exit(1)
		else:
			bash.message(
				'info',
				'default package (' + self.default_package +
				') in config.yml is allowed to run')

		# ==============================
		# Checking for i915 intel driver
		# ==============================
		bash.message('info', 'checking for i915 intel driver ...')
		i915 = \
			bash.get_output(
				'lspci -v -s $(lspci |grep "VGA compatible controller" | '
				'cut -d" " -f 1) | grep "Kernel driver in use"  '
				'| awk -F": " \'{print $2}\'')
		if not i915:
			bash.message(
				'err',
				'i915 intel driver is not in use, please enable i915')
			bash.message(
				'info',
				'the following grub parameters is used in order to enable '
				'i915 driver in (6th gen) GPUs and newer')
			bash.message('info', '- i915.preliminary_hw_support=1')
			bash.message('info', '- i915.alpha_support=1')
			bash.message('info', 'sending a email notification')
			utils.emailer(
				self.email_sender,
				self.default_mailing_list,
				'i915 driver is not enabled on (' + self.dut_hostname +
				')',
				'an error was occured trying to run intel-gpu-tools on (' +
				self.dut_hostname + ')\ni915 driver is not enabled on (' +
				self.default_package + '), please check the grub command '
				'line : (' + self.grub_parameters + ')')
			sys.exit(1)
		else:
			bash.message(
				'info',
				'i915 driver is enabled on (' + self.dut_hostname + ')')

		# ========================
		# Checking if X is enabled
		# ========================
		check_x = bash.get_output('ps -e | grep X')

		if check_x:
			bash.message(
				'err',
				'X is enabled on tty7, '
				'please disable in order to run intel-gpu-tools')
			bash.message('info', 'sending a email notification')
			utils.emailer(
				self.email_sender,
				self.default_mailing_list,
				'X is enabled on (' + self.dut_hostname + ')',
				'an error was occured trying to run intel-gpu-tools '
				'on (' + self.dut_hostname + ')\nX is enabled in tty7 ,'
				' please disabled it in order to run intel-gpu-tools')
			sys.exit(1)
		else:
			bash.message(
				'info',
				'X is disabled on (' + self.dut_hostname + ')')

		# =========================================
		# Checking if intel-gpu-tools folder exists
		# =========================================
		if not os.path.exists(self.main_path):
			bash.message('err', 'intel-gpu-tools folder does not exists')
			bash.message(
				'info', 'please install a debian package with intel-gpu-tools')
			bash.message('info', 'sending a email notification')
			utils.emailer(
				self.email_sender,
				self.default_mailing_list,
				'intel-gpu-tools folder does not exists on (' +
				self.dut_hostname + ')',
				'an error was occured trying to run intel-gpu-tools on (' +
				self.dut_hostname + ')\nintel-gpu-tools folder does not '
				'exists on (' + self.default_package + '), please check the '
				'graphic stack : (' + self.gfx_stack_code + ')')
			sys.exit(1)
		else:
			bash.message('info', 'intel-gpu-tools folder exists')

		# ===============================
		# Checking if piglit folder exist
		# ===============================
		if not os.path.exists(self.piglit_path):
			bash.message('err', 'piglit folder does not exists')
			bash.message(
				'info', 'please install a debian package with intel-gpu-tools')
			bash.message('info', 'sending a email notification')
			utils.emailer(
				self.email_sender,
				self.default_mailing_list,
				'piglit folder does not exists on (' + self.dut_hostname + ')',
				'an error was occured trying to run intel-gpu-tools on (' +
				self.dut_hostname + ')\npiglit folder does not exists on (' +
				self.default_package + '), please check the graphic stack'
				' : (' + self.gfx_stack_code + ')')
			sys.exit(1)
		else:
			bash.message('info', 'piglit folder exists')

		# ========================================
		# Checking if intel-gpu-tools was compiled
		# ========================================
		if not os.path.exists(
			os.path.join(self.igt_test_root, 'test-list.txt')):
			bash.message('err', 'test-list.txt file does not exists')
			bash.message(
				'info', 'intel-gpu-tools was not compiled successfully')
			bash.message(
				'info', 'please install a debian package with intel-gpu-tools')
			bash.message('info', 'sending a email notification')
			utils.emailer(
				self.email_sender,
				self.default_mailing_list,
				'test-list.txt file does not exists on (' +
				self.dut_hostname + ')',
				'an error was occured trying to run intel-gpu-tools '
				'on (' + self.dut_hostname + ')\nintel-gpu-tools was not '
				'compiled successfully on (' + self.default_package + '), '
				'please check the graphic stack : (' + self.gfx_stack_code +
				')')
			sys.exit(1)
		else:
			bash.message('info', 'intel-gpu-tools was compiled successfully')

		# =======================================
		# Checking if the current testlist exists
		# =======================================
		if not os.path.isfile(
			os.path.join(
				self.igt_test_root, 'intel-ci', self.current_testlist)):
			bash.message('err', self.current_testlist + ' does not exists')
			bash.message('info', 'sending a email notification')
			utils.emailer(
				self.email_sender,
				self.default_mailing_list,
				self.current_testlist + ' does not exists on (' +
				self.dut_hostname + ')',
				'an error was occured trying to run '
				'intel-gpu-tools on (' + self.dut_hostname + ')\n' +
				self.current_testlist + ' does not exists on (' +
				self.default_package + '), please check the graphic '
				'stack : (' + self.gfx_stack_code + ')')
			sys.exit(1)
		else:
			bash.message('info', '(' + self.current_testlist + ') exists')

	def check_campaigns(self):
		"""
		If the user setup more than campaign, this function check in
		the last iteration folder the file results.json file for some
		failed tests in order to setup the environment for a next iteration
		"""
		# ===================================
		# Getting the latest iteration folder
		# ===================================
		self.get_latest_iteration_folder()

		if not os.path.isfile(
			os.path.join(self.current_iteration_folder, '.control')):

			# =========================================
			# Generating html files for each iterationX
			# =========================================
			if not os.path.exists(os.path.join(
					self.current_iteration_folder, 'html')):
				bash.message(
					'info',
					'generating html folder with piglit ...')
				os.system(
					'python ' + self.piglit + ' summary html ' +
					os.path.join(self.current_iteration_folder, 'html') +
					' ' + self.current_iteration_folder + ' 2> /dev/null')

			if str(self.current_iteration_number) == str(self.igt_iterations) \
				and os.path.isfile(
						os.path.join(
							self.current_iteration_folder, '.control')):
				bash.message('info', 'all the campaigns have ended')

			elif str(self.current_iteration_number) != str(self.igt_iterations) \
				and not os.path.isfile(
							os.path.join(
								self.current_iteration_folder , '.control')):

				# ======================================================
				# validating if there is some failure to run in the next
				# campaign
				# ======================================================
				self.logger.info(
					'validating if there are some tests to run for the next campaign')
				json_target = os.path.join(
					self.current_iteration_folder, 'results.json')
				self.logger.info(
					'searching for any of the following test results '
					'(fail/crash/timeout/incomplete/dmesg_fail)'
				)

				# =============================================================
				# evaluating if there is some of the test to run with the
				# following status : fail, crash, timeout, incomplete, dmesg_fail
				# =============================================================

				if getResult.getStatisticsfromJson(json_target, 'check_failures', None):
					next_campaign = int(self.current_iteration_number) + 1
					bash.message('info', 'setting up the next campaign')
					bash.message(
						'info',
						'campaign (' + str(next_campaign) + '/' +
						str(self.igt_iterations) + ')')

					if not os.path.exists(
						os.path.join(self.igt_test_root, 'intel-ci', 'tmp.d')):
						bash.message(
							'info',
							'creating a (tmp.d) folder into (intel-ci)')
						os.makedirs(
							os.path.join(
								self.igt_test_root, 'intel-ci', 'tmp.d'))
					bash.message(
						'info',
						'moving (' + self.current_testlist + ') to (tmp.d) '
						'folder')

					number = \
						bash.get_output(
							'ls ' +
							os.path.join(
								self.igt_test_root, 'intel-ci', 'tmp.d') +
							'| wc -l')
					testlist_backup_bame = \
						self.current_testlist + '__' + number
					bash.message(
						'info',
						'making a backup for (' + self.current_testlist +
						') --> (' + testlist_backup_bame + ')')
					move(os.path.join(
							self.igt_test_root, 'intel-ci',
							self.current_testlist),
							os.path.join(
								self.igt_test_root, 'intel-ci', 'tmp.d',
								testlist_backup_bame))
					bash.message(
						'info',
						'generating a new (' + self.current_testlist + ')')
					getResult.generate_new_testlist(json_target, self.current_testlist)
					bash.message(
						'info',
						'creating control file to run next iteration: ' +
						self.main_path + '/.run_next_iteration')
					os.system(
						'touch {control_file}'
							.format(
								control_file=self.main_path +
								'/.run_next_iteration'))
					bash.message(
							'info',
							'rebooting the system (' + self.dut_hostname + ')')
					os.system('sudo reboot')

				else:
					bash.message(
						'info',
						'the (' + os.path.basename(json_target) +
						') has not more test to run again')
					bash.message(
						'info',
						'creating a control file in (' +
						os.path.basename(self.current_iteration_folder) + ')')
					os.system(
						'touch ' +
						os.path.join(
							self.current_iteration_folder, '.control'))

			elif str(self.current_iteration_number) == \
				str(self.igt_iterations) and not os.path.isfile(
					os.path.join(
						self.current_iteration_folder, '.control')) and \
				os.path.isfile(
					os.path.join(
						self.current_iteration_folder, 'results.json')):

				# ==========================================
				# validating if there is some failure to run
				# ==========================================
				json_target = os.path.join(
					self.current_iteration_folder, 'results.json')

				# ==========================================================
				# evaluating if there is some test to run with the following
				# status : fail, crash, timeout, incomplete, dmesg_fail
				# ==========================================================
				if getResult.getStatisticsfromJson(json_target, 'check_failures', None):
					self.logger.info(
						'{0} : has some failures to run but this script has '
						'reached the maximum campaigns'.format(json_target))
				else:
					self.logger.info('{0} : has not more test to run again'.format(
						json_target))

				bash.message(
					'info',
					'creating a control file in (' +
					os.path.basename(self.current_iteration_folder) + ')')
				os.system(
					'touch ' +
					os.path.join(self.current_iteration_folder, '.control'))

		elif os.path.isfile(
			os.path.join(self.current_iteration_folder, '.control')):

			if not os.path.exists(
				os.path.join(self.current_iteration_folder, 'html')):
				bash.message('info', 'generating html folder with piglit ...')
				os.system(
					'python ' + self.piglit + ' summary html ' +
					os.path.join(self.current_iteration_folder, 'html') +
					' ' + self.current_iteration_folder + ' 2> /dev/null')

			bash.message('info', 'all the campaigns have ended')

	def check_folder_structure(self, current_iteration_folder):
		"""Check the folder structure of the current iteration folder

		This functions checks for the following conditions :
			- tests folder exists on current iteration folder
			- results.json.bz2 exists on current iteration folder
		if the mentioned conditions are True, the tests folder must be deleted
		in order to continue with the execution.

		:param current_iteration_folder: the current iteration folder.
		:return
			- True if all the conditions are met
			- False if any if the conditions are not met
		"""

		items = filter(
			lambda item: item != 'tests', os.listdir(current_iteration_folder))
		json_files = os.listdir(os.path.join(current_iteration_folder, 'tests'))
		current_testlist_lines = sum(1 for line in open(self.current_testlist_path))

		conditions = [
			len(items) == 1,
			items[0] == 'results.json.bz2',
			len(json_files) == current_testlist_lines
		]

		if all(conditions):
			current_tests_folder = os.path.join(current_iteration_folder, 'tests')
			bash.message('info', 'an unusual condition was detected with piglit')
			bash.message('info', 'removing {0}'.format(current_tests_folder))
			os.system('sudo rm -rf {0}'.format(current_tests_folder))
			return True
		return False

	def check_last_iteration(self):
		"""
		This function checks if the last iteration folder was finished,
		and calls to check_campains function to see if there is some test
		to run in a new iteration only if the user setup more than 1 campaign
		"""
		# ===================================
		# Getting the latest iteration folder
		# ===================================
		self.get_latest_iteration_folder()

		# ===============================================
		# Changing root owner folder for the current user
		# ===============================================
		if os.path.exists(self.current_iteration_folder):
			current_owner = \
				os.popen(
					'stat -c %U ' +
					self.current_iteration_folder).read().split()[0]

			if current_owner == 'root':
				bash.message(
					'info',
					'current owner for (' +
					os.path.basename(self.current_iteration_folder) +
					') is root, changing to (' + self.dut_user + ')')
				os.system(
					'sudo chown -R ' + self.dut_user + '.' + self.dut_user +
					' ' + self.current_iteration_folder)

		if os.path.exists(self.current_iteration_folder + '/tests'):
			# =====================================================
			# this mean that intel-gpu-tools execution is ongoing
			# =====================================================
			bash.message('warn', 'intel-gpu-tools has not finished')

			# ===================
			# Getting latest json
			# ===================
			latest_json = \
				bash.get_output(
					'ls ' + self.json_path + ' | sort -n | tail -1')
			latest_json_path = os.path.join(self.json_path, latest_json)

			with open(latest_json_path) as j:
				json_data = json.load(j)
				for key, value in json_data.iteritems():
					json_result = value['result']

			bash.message(
				'info',
				'latest json (' + latest_json + '), result (' +
				str(json_result) + ')')

		elif not os.path.exists(
					self.current_iteration_folder + '/tests') and \
			os.path.isfile(
				self.current_iteration_folder + '/results.json.bz2') \
			and not os.path.isfile(
				os.path.join(self.current_iteration_folder, '.igt_done')):

			# =====================================================
			# this mean that intel-gpu-tools execution is finished
			# =====================================================
			bash.message('info', 'decompressing (results.json.bz2)')
			target = \
				os.path.join(self.current_iteration_folder, 'results.json.bz2')
			os.system('bzip2 -d ' + target)
			bash.message(
				'info',
				bash.GREEN + 'intel-gpu-tools has finished' + bash.END)
			bash.message(
				'info',
				'iteration (' + str(self.current_iteration_number) +
				'/' + str(self.igt_iterations) + ')')
			self.check_campaigns()

			# =================================================
			# Generating the dmesg for the full igt execution #
			# =================================================
			bash.message(
				'info',
				'generating full dmesg for the whole igt execution ...')
			dmesg_name = \
				'dmesg_and_kern_logs_hostname_' + self.dut_hostname + \
				'_gfxStackCode_' + str(self.gfx_stack_code) +  \
				'_kernelBranch_' + self.kernel_branch + '_kernelCommit_' + \
				str(self.kernel_commit)

			if not os.path.exists(
				os.path.join(self.attachments_folder,dmesg_name)):
				bash.message(
					'info',
					'creaing (' + dmesg_name + ') folder in (' +
					self.attachments_folder + ')')
				os.makedirs(os.path.join(self.attachments_folder, dmesg_name))
			bash.message('info', 'running checkDmesg.sh script ...')
			os.system(
				'bash ' + self.this_path + '/tools/checkDmesg.sh ' +
				os.path.join(self.attachments_folder, dmesg_name))
			bash.message(
				'info',
				'getting the dmesg from (' + self.dut_hostname + ')')
			os.system(
				'dmesg > ' +
				os.path.join(
					self.attachments_folder, dmesg_name) + '/dmesg.log')
			# ======================================================
			# this functionality was commented because in some cases
			# kern.log file could be very heavy
			# ======================================================
			# bash.message(
			# 	'info', 'getting the kern.log from (' +
			# 	self.dut_hostname + ')')
			# os.system(
			# 	'cp /var/log/kern.log ' +
			# 	os.path.join(self.attachments_folder, dmesg_name))
			bash.message(
				'info',
				'compress at maximum the dmesg in order to upload it to TRC')
			os.system(
				'export GZIP=-9; cd ' + self.attachments_folder +
				' && tar czf dmesg_and_kern_logs.tar.gz ./' + dmesg_name +
				' && rm -rf ' + dmesg_name)

			# ========================
			# Setting global variables
			# ========================
			global output_dir, output_trc_name, output_backtrace_name,\
				output_runtime_name

			output_dir = \
				os.path.join(
					'/home', self.dut_user, 'Desktop', 'results',
					'intel-gpu-tools')

			if self.default_package == 'igt_clone_testing':
				current_tests_bunch = \
					self.data['autouploader']['current_tests_bunch']
				output_trc_name = \
					self.default_package + '_bunch_' + current_tests_bunch + \
					'_' + self.dut_hostname + '_TRC_summary_' + \
					self.work_week + '_' + self.day + '_' + self.hour + '.csv'
				output_backtrace_name = \
					self.default_package + '_' + self.dut_hostname + \
					'_backtrace_' + self.work_week + '_' + self.day + '_' + \
					self.hour + '_bunch_' + current_tests_bunch + '.xls'
				output_runtime_name = \
					self.default_package + '_' + self.dut_hostname + \
					'_runtime_' + self.work_week + '_' + self.day + '_' + \
					self.hour + '_bunch_' + current_tests_bunch + '.csv'
			else:
				output_trc_name = \
					self.default_package + '_' + self.dut_hostname + \
					'_TRC_summary_' + self.work_week + '_' + self.hour + '.csv'
				output_backtrace_name = \
					self.default_package + '_' + self.dut_hostname + \
					'_backtrace_' + self.work_week + '_' + self.hour + '.xls'
				output_runtime_name = \
					self.default_package + '_' + self.dut_hostname + \
					'_runtime_' + self.work_week + '_' + self.hour + '.csv'

			if not os.path.exists(output_dir):
				os.makedirs(output_dir)

			main_json_file_path = os.path.join(
				self.main_path, 'iteration1', 'results.json')

			self.logger.info('merging all json files')
			getResult.get_json_files(self.main_path)

			self.logger.info('generating html folder with piglit')
			os.system(
				'python {piglit} summary html {html_folder} {input_folder} '
				'2> /dev/null'.format(
					piglit=self.piglit,
					html_folder=os.path.join(
						self.main_path, 'iteration1', 'html'),
					input_folder=os.path.join(
						self.main_path, 'iteration1'))
			)

			self.logger.info('generating generic csv file for TestReportCenter')
			getResult.createCSV(
				main_json_file_path, os.path.join(output_dir, output_trc_name))

			self.logger.info('generating xls backtrace file')
			getResult.createCSV_backtrace(
				main_json_file_path, os.path.join(output_dir, output_backtrace_name)
			)

			self.logger.info('generating runtime files')
			getResult.createCSV_runtime(
				main_json_file_path, os.path.join(output_dir, output_runtime_name)
			)

			self.logger.info('adding bugs to CSV file from the API')
			getResult.updateCSVfromAPI(
				os.path.join(output_dir, output_trc_name), self.current_platform,
				output_dir
			)

			if os.path.isfile(os.path.join(output_dir, 'tmp.csv')):
				self.logger.info('renaming the final CSV file (with bugs)')
				os.system(
					'rm -rf ' + os.path.join(output_dir, output_trc_name))
				os.system(
					'mv ' + os.path.join(output_dir, 'tmp.csv') + ' ' +
					os.path.join(output_dir, output_trc_name))

			# =========================================================
			# creating a control file in order to NOT run the next time
			# because is supposed that IGT has finished
			# =========================================================
			os.system(
				'touch ' +
				os.path.join(self.current_iteration_folder, '.igt_done'))

			# =================================
			# getting statistics from json file
			# =================================
			self.logger.info('showing the final statistics')
			json_final_file = os.path.join(self.main_path, 'iteration1', 'results.json')
			getResult.getStatisticsfromJson(json_final_file, 'all', None)

			# ====================
			# Creating attachments
			# ====================
			self.create_attachments()
			bash.message(
				'info', 'waiting for 1 minute to let the system report to TRC')
			sleep(60)

			# =====================================
			# releasing the DUT in watchdog webpage
			# =====================================
			# only release the platform if the report was uploaded successfully
			# to linuxgraphics or if reports were not enabled
			if self.report_uploaded or not self.backup_report:
				self.logger.info('releasing the DUT in watchdog')
				getResult.release_dut('free')
				sys.exit(0)

		elif os.path.exists(
			os.path.join(self.current_iteration_folder, '.igt_done')):

			# ============================
			# intel-gpu-tools has finished
			# ============================
			json_final_file = os.path.join(
				self.main_path, 'iteration1', 'results.json')
			self.logger.info('intel-gpu-tools has finished')
			getResult.getStatisticsfromJson(json_final_file, 'all', None)
			sys.exit(0)
		elif (os.path.isfile(
				os.path.join(self.main_path, '.run_next_iteration'))):
			bash.message(
				'info',
				'found ' + os.path.join(self.main_path,'.run_next_iteration'))
		else:
			self.check_campaigns()

	def run(self):
		"""
		This function helps to run intel-gpu-tools with piglit framework
		"""
		# ===============================
		# Showing some useful information
		# ===============================
		if self.displays_attached:
			for display in self.displays_attached:
				bash.message(
					'info',
					'display attached to (' + self.dut_hostname + ') <--> (' +
					display + ')')
		bash.message('info', 'python version (' + self.python_version + ')')
		bash.message('info', 'ip address (' + self.dut_static_ip + ')')
		bash.message(
			'info',
			'graphic stack code (' + self.gfx_stack_code + ')')
		bash.message('info', 'current kernel (' + self.kernel + ')')
		bash.message('info', 'kernel branch (' + self.kernel_branch + ')')
		bash.message('info', 'kernel commit (' + self.kernel_commit + ')')
		bash.message('info', 'grub parameters (' + self.grub_parameters + ')')
		bash.message('info', 'linux image (' + self.default_image + ')')
		bash.message('info', 'distro (' + self.distro + ')')
		bash.message(
			'info',
			'networking boot time (' + self.networking_boot_time + ')')
		bash.message(
			'info',
			'(' + self.dut_hostname + ') uptime (' + self.uptime_data + ')')

		# ===================================
		# Getting the latest iteration folder
		# ===================================
		self.get_latest_iteration_folder()

		# =======================================================
		# Checking all precondition before to run intel-gpu-tools
		# =======================================================
		self.preconditions()

		# ===========================================
		# Checking the last intel-gpu-tools iteration
		# ===========================================
		self.check_last_iteration()

		# ==================
		# Showing statistics
		# ==================
		self.statistics()
		intel_gpu_tools_output = 0

		# ===================================
		# running intel-gpu-tools with piglit
		# ===================================
		bash.message('info', 'setting (IGT_TEST_ROOT) flag')
		os.environ['IGT_TEST_ROOT'] = self.igt_test_root

		# =================================================================
		# the following information comes from Petri :
		# (--dmesg) : the IGT profile for piglit already fetches dmesg into
		# the tests results and filters the kernel logs to avoid spurious
		# dmesg-warn results, and using the --dmesg option will bypass the
		# filter and cause any kernel log activity to change the results to
		# dmesg-warm / dmesg-fail
		# =================================================================
		if not self.current_iteration_folder:
			os.system(
				'bash ' +
				os.path.join(self.this_path, 'tools', 'banners.sh') + ' ' +
				self.default_package)
			bash.message('info', 'running intel-gpu-tools ...')
			bash.message(
				'info', 'iteration (1/' + str(self.igt_iterations) + ')')
			bash.message(
				'info',
				'cmd (' + self.piglit + ' run igt --ignore-missing -o ' +
				os.path.join(self.main_path, 'iteration1') +
				'  --test-list ' + self.current_testlist_path +
				' -l verbose --sync' + ')')
			intel_gpu_tools_output = \
				os.system(
					'sudo -E ' + self.piglit +
					' run igt --ignore-missing -o ' +
					os.path.join(self.main_path, 'iteration1') +
					'  --test-list ' + self.current_testlist_path +
					' -l verbose --sync')

		elif self.current_iteration_folder and \
			os.path.exists(
				os.path.join(self.current_iteration_folder, 'tests')):

			if self.check_folder_structure(self.current_iteration_folder):
				self.run()

			os.system(
				'bash ' +
				os.path.join(self.this_path, 'tools', 'banners.sh') + ' ' +
				self.default_package)
			bash.message(
				'info',
				bash.YELLOW + 'resuming intel-gpu-tools ...' + bash.END)
			bash.message(
				'info',
				'iteration (' + str(self.current_iteration_number) + '/' +
				str(self.igt_iterations) + ')')
			bash.message(
				'info',
				'cmd (' + self.piglit + ' resume ' +
				self.current_iteration_folder + ' --no-retry' +')')
			intel_gpu_tools_output = \
				os.system(
					'sudo -E ' + self.piglit + ' resume ' +
					self.current_iteration_folder + ' --no-retry')

		# =================
		# running campaigns
		# =================
		elif self.current_iteration_folder and \
			os.path.exists(
				os.path.join(self.main_path, '.run_next_iteration')):

			bash.message(
				'info',
				'removing control file: ' + self.main_path +
				'/.run_next_iteration')
			os.system('rm ' + self.main_path + '/.run_next_iteration')
			bash.message('info', 'running a subsequent campaign')

			os.system(
				'bash ' +
				os.path.join(self.this_path, 'tools', 'banners.sh') +
				' ' + self.default_package)
			bash.message('info', 'running intel-gpu-tools ...')
			current_iteration = int(self.current_iteration_number) + 1
			bash.message(
				'info',
				'iteration (' + str(current_iteration) + '/' +
				str(self.igt_iterations) + ')')
			bash.message(
				'info',
				'cmd (' + self.piglit + ' run igt --ignore-missing -o ' +
				os.path.join(
					self.main_path,'iteration' + str(current_iteration)) +
				'  --test-list ' + self.current_testlist_path +
				' -l verbose --sync' + ')')
			intel_gpu_tools_output = \
				os.system(
					'sudo -E ' + self.piglit +
					' run igt --ignore-missing -o ' +
					os.path.join(
						self.main_path,'iteration' + str(current_iteration)) +
					'  --test-list ' + self.current_testlist_path +
					' -l verbose --sync')

		if intel_gpu_tools_output == 0:
			bash.message(
				'info',
				'intel-gpu-tools has finished with output (' +
				str(intel_gpu_tools_output) + ')')
			self.check_last_iteration()

		elif intel_gpu_tools_output == 256:
			os.system(
				'bash ' +
				os.path.join(self.this_path,'tools','banners.sh') + ' error')
			bash.message(
				'info',
				'intel-gpu-tools has finished with output (' +
				str(intel_gpu_tools_output) + ')')
			bash.message(
				'err',
				'an error was occurred executing intel-gpu-tools')
			bash.message(
				'err',
				'piglit does not recognize some tests on (' +
				self.current_testlist + ')')
			sys.exit(1)

		else:
			os.system(
				'bash ' +
				os.path.join(self.this_path, 'tools', 'banners.sh') + ' error')
			bash.message(
				'info',
				'intel-gpu-tools has finished with output (' +
				str(intel_gpu_tools_output) + ')')
			bash.message(
				'err',
				'an error was occurred executing intel-gpu-tools')
			bash.message(
				'err',
				'rebooting the system (' + self.dut_hostname + ')')
			os.system('sudo reboot')

	def _make_http_request(
			self, url, request_type='get', max_retries=10, interval=10, timeout=10):
		"""Attempts an HTTP request for a predefined number of times.

		:param url: the endpoint for the request
		:param request_type: the HTTP verb for the request: get or post
		:param max_retries: number of times the request will be attempted if not
		successful
		:param interval: the interval in seconds between retries
		:param timeout: the timeout for an http request to respond back
		:return: the response of the HTTP request if the request was performed
		successfully, it raises a RuntimeError if the API does not respond
		"""
		# prepare the payload for the HTTP request
		target_system = {
			'RaspberryNumber': self.raspberry_number,
			'PowerSwitchNumber': self.raspberry_power_switch
		}

		# get the http function (verb) to be used (either get or post)
		http_func = getattr(requests, request_type, None)
		if not http_func:
			self.logger.error(
				'bad http function: {type}. Please use get or post'
				.format(type=request_type)
			)
			raise RuntimeError(
				'bad http function: {type}'.format(type=request_type)
			)

		# attempt to make the HTTP request up to the number of retries defined
		current_attempt = 0
		while current_attempt < max_retries:
			try:
				response = http_func(url, data=target_system, timeout=timeout)
			except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
				self.logger.warn('an exception was generated calling the API')
				current_attempt += 1
			else:
				if response.status_code == 200:
					self.logger.debug('HTTP request submitted successfully')
					return response
				current_attempt += 1
				self.logger.debug(
					'the API responded with a status code of {code} '
					'(Attempt number {attempt})'
					.format(code=response.status_code, attempt=current_attempt)
				)
				time.sleep(interval)

		self.logger.warn(
			'the HTTP request could not be submitted successfully within {0} attempts'
			.format(max_retries)
		)
		raise RuntimeError(
			'The API did not respond within {0} attempts'.format(max_retries)
		)

	def get_watchdog_status(self):
		"""Checks if a watchdog is already running for the current host.

		:return: True if the watchdog is already running, False otherwise
		"""
		self.logger.info(
			'checking if a watchdog is already running for this platform'
		)
		wd_status_url = 'http://10.219.106.111:2020/watchdogStatusDb'
		response = self._make_http_request(request_type='get', url=wd_status_url)
		watchdogs_info = response.json()
		wd_info = (
			item for item in watchdogs_info
			if item['RaspberryNumber'] == int(self.raspberry_number) and
			item['PowerSwitchNumber'] == int(self.raspberry_power_switch)
		).next()
		watchdog_status = wd_info['watchdogStatus']
		self.logger.debug(
			'watchdog is running' if watchdog_status else
			'watchdog not running')
		return True if watchdog_status else False

	def start_watchdog(self):
		"""Starts the watchdog in the monitor system.

		Watchdog is a two-tier system that runs one module in a remote server as a
		monitor, and another module locally as the data collector. This function
		starts the watchdog monitor in the remote system. There is an API that can be
		used to start the watchdgo monitor remotely. The API receives the raspberry
		number and switch number the platform is connected to.
		"""
		# start watchdog
		self.logger.info('starting watchdog')
		start_wd_url = 'http://10.219.106.111:2020/startWatchdog'
		self._make_http_request(request_type='post', url=start_wd_url)
		self.logger.info(
			'request to start watchdog submitted to the API successfully'
		)
		# wait for watchdog to start
		start_time = time.time()
		timeout = 60
		while not self.get_watchdog_status():
			time.sleep(1)
			if time.time() > (start_time + timeout):
				raise RuntimeError('watchdog failed to be started')


if __name__ == '__main__':
	igt = Data()
	try:
		# check if a watchdog is already running for the platform
		watchdog_running = igt.get_watchdog_status()
		# if watchdog is not running try to start it
		if not watchdog_running:
			igt.start_watchdog()
	except RuntimeError:
		igt.logger.error(
			'Watchdog failed to be started, or its status could not be verified '
			'the automation API might be unavailable. IGT will be started without'
			'watchdog monitoring.')
	igt.run()
