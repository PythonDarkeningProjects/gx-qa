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

# The config.yml has to be in the same folder as this python script
# (could be as a soft-link)

import argparse
import datetime
import os
import socket
import sys
import time

import paramiko
import requests
import yaml

import common.apiutils as apiutils
import common.network as network
import common.remote_client as remote_client
import gfx_qa_tools.common.bash as bash
import gfx_qa_tools.common.log as log
import gfx_qa_tools.common.utils as utils
import gfx_qa_tools.config.config as config


class Watchdog(object):
	"""Watchdog to verify platforms don't hang.

	Graphics tests are some times very resource intensive, and as such, they
	can some times slow down the platform a lot or even hang it. When a
	platform hangs, it needs to be rebooted so the test execution can continue
	(in the next test). The watchdog job is to continually poll the platform
	(DUT) to make sure it is still responsive and rebooted if it is not.
	"""

	def __init__(self, args):

		# Get the config file for the watchdog
		if args.config and os.path.isfile(args.config):
			# if the user specified a config file use that
			config_file = args.config
		elif not args.config and os.path.isfile('config.yml'):
			# If no config file was provided, use the default config file in the
			# current path
			config_file = 'config.yml'
		else:
			# If there is no config file available exit the script
			bash.message('err', 'Config file not found')
			sys.exit(1)

		# Gather all the configuration data from the config file
		self.data = yaml.load(open(config_file))

		# Initialize the logger
		dut_hostname = self.data['dut_conf']['dut_hostname']
		log_filename = 'watchdog_{0}.log'.format(dut_hostname)
		log_path = os.path.join(
			config.get('watchdog', 'log_path'), dut_hostname.replace('-', '_'))
		self.log = log.setup_logging(
			name='watchdog', level=config.get('watchdog', 'log_level'),
			log_file='{path}/{filename}'.format(path=log_path, filename=log_filename)
		)
		self.log.info(
			'configuring watchdog using configuration file: {0}'
			.format(config_file)
		)

		# DUT configuration
		self.autologin = self.data['dut_conf']['autologin']
		self.dut_user = self.data['dut_conf']['dut_user']
		self.dut_hostname = self.data['dut_conf']['dut_hostname']
		self.dut_password = self.data['dut_conf']['dut_password']
		self.dut_static_ip = self.data['dut_conf']['dut_static_ip']
		self.graphical_environment = self.data['dut_conf']['graphical_environment']
		self.grub_parameters = self.data['dut_conf']['grub_parameters']

		# Firmwares
		self.dmc = self.data['firmwares']['dmc']
		self.guc = self.data['firmwares']['guc']
		self.huc = self.data['firmwares']['huc']

		# Raspberry configuration
		self.raspberry_gpio = self.data['raspberry_conf']['raspberry_gpio']
		self.raspberry_ip = self.data['raspberry_conf']['raspberry_ip']
		self.raspberry_number = self.data['raspberry_conf']['raspberry_number']
		self.raspberry_power_switch = (
			self.data['raspberry_conf']['raspberry_power_switch'])
		self.raspberry_user = self.data['raspberry_conf']['raspberry_user']
		self.usb_cutter_serial = self.data['raspberry_conf']['usb_cutter_serial']

		# Suite configuration
		self.blacklist_file = self.data['suite_conf']['blacklist_file']
		self.default_mailing_list = self.data['suite_conf']['default_mailing_list']
		self.default_package = self.data['suite_conf']['default_package']
		self.gfx_stack_code = self.data['suite_conf']['gfx_stack_code']
		self.kernel_branch = self.data['suite_conf']['kernel_branch']
		self.kernel_commit = self.data['suite_conf']['kernel_commit']
		self.igt_iterations = self.data['suite_conf']['igt_iterations']

		# Autouploader information
		self.currentEnv = self.data['autouploader']['currentEnv']
		self.currentPlatform = self.data['autouploader']['currentPlatform']
		self.currentRelease = self.data['autouploader']['currentRelease']
		self.currentSuite = self.data['autouploader']['currentSuite']
		self.currentTittle = self.data['autouploader']['currentTittle']
		self.reportTRC = self.data['autouploader']['trc_report']

		# Autouploader - Clones
		self.current_tests_bunch = (
			self.data['autouploader'].get('current_tests_bunch'))
		self.total_tests_bunches = (
			self.data['autouploader'].get('total_tests_bunches'))
		self.trc_report_id = self.data['autouploader'].get('trc_report_id')
		self.state = self.data['autouploader'].get('state')

		# Reports on linuxgraphics.intel.com
		self.backupReport = self.data['database']['upload_reports']

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

		# Miscellaneous
		self.post = 'http://10.219.106.111:2020/watchdog'
		self.dut_api = 'http://{ip}:4040/statistics'.format(ip=self.dut_static_ip)
		self.email_sender = 'watchdog@noreply.com'

		# --------------------------------------------------------------------------
		# -- Control variables (DO NOT EDIT! Only the system should modify these) --
		# --------------------------------------------------------------------------
		self.nodata_real_timeout = 0
		self.nodata = False
		self.no_url_start_time = 0
		self.consecutive_reboots = 0
		self.elapsed_test_time = 0
		self.piglit_reboot_timeout = 0
		# TODO(Cas): remove this variable after observing behavior
		self.non_responsive_after_reboot = 0  # This is a temporary debug variable

		# ----------------------
		# -- Watchdog Tune Up --
		# ----------------------
		# The time the watchdog will keep trying to connect with a platform before
		# rebooting it (in minutes)
		self.dut_connection_timeout = 11
		# The timeout to wait for a response from the DUT when doing an HTTP request
		# to its API (in seconds)
		self.dut_api_timeout = 20
		# When a platform sends "nodata" for longer than this timeout, the platform
		# is rebooted (in minutes)
		self.nodata_timeout = 10
		# The time the watchdog will keep trying to ping a platform that has just
		# been rebooted (in seconds)
		self.ping_timeout = 150
		# The timeout to finish running one test, if a test takes longer than
		# this timeout, the platform is rebooted so the test is skipped (in minutes)
		self.test_timeout = 11
		# The time to wait for the DUT to provide the URLs for the TRC report or
		# the backup report if enabled (in minutes)
		self.no_url_timeout = 5
		# The number of consecutive reboots allowed for a platform
		self.consecutive_reboots_allowed = 3
		# Number of seconds to wait between every request of information from
		# the DUT
		self.wait_between_cycles = 1
		# Number of seconds to wait for Piglit to start running after a reboot,
		# if Piglit doesn't start within that time watchdog will assume something
		# is wrong and the platform will be rebooted
		self.piglit_timeout = 300

	def reboot_dut(self, raspberry, switch):
		"""Hard reboots a platform

		:param raspberry: the raspberry number
		:param switch: the switch number
		:return dut_online: the status of the platform after being rebooted,
		True if the platform responded to ping, False otherwise
		"""
		self.log.info('rebooting the platform')
		# Update the WD table about the reboot
		apiutils.update_watchdog_db(
			self.raspberry_number,
			self.raspberry_power_switch,
			Status='Rebooting platform')

		# Turn off the platform
		raspberry_path = '/home/shared/raspberry'
		dut_off = '{path}/raspberry.sh {rn} {sn} off'.format(
			path=raspberry_path, rn=str(raspberry), sn=str(switch))
		os.system(dut_off)
		# wait 5 seconds to allow for the electrical levels in the switch to go
		# down so the platform is actually turned off
		time.sleep(5)
		# Turn the platform back on
		dut_on = '{path}/raspberry.sh {rn} {sn} on'.format(
			path=raspberry_path, rn=str(raspberry), sn=str(switch))
		os.system(dut_on)

		# Update WD table with a message about the system rebooting
		apiutils.update_watchdog_db(
			self.raspberry_number,
			self.raspberry_power_switch,
			Status='Waiting for the platform to finish rebooting')

		# Ping the system for up to ping_timeout for it to come back online
		dut_online = network.wait_for_ping(self.dut_static_ip, self.ping_timeout)

		# reset the piglit timer to give it that time to start
		self.piglit_reboot_timeout = time.time() + self.piglit_timeout

		# return the online status of the DUT after a hard reboot
		return dut_online

	def create_report(self, data):
		"""Creates a report that can be sent by email using the DUT data.

		:param data: the execution data provided by the platform
		:return report: the formatted report built from the data
		"""
		self.log.info('creating report from the data')
		# Prepare the data for the email message
		display_list = []
		for k, v in data['attachedDisplays'].items():
			display_list.append(k + ':' + v)

		report = '''
intel-gpu-tools execution has finished, please see the overall statistics

================================================
DUT configuration
================================================
User: {user}
Password: {pwd}
IP: {host_ip}
Hostname: {host}
Grub parameters: {grub}
guc: {guc}
huc: {huc}
dmc: {dmc}
Raspberry IP: {raspberry_ip}
Raspberry number: {raspberry_number}
Raspberry switch: {switch_number}
USB cutter serial: {usb_cutter}
Blacklist: {blacklist}
Package: {package}
Gfx stack code: {stack_code}
Kernel branch: {kernel_branch}
Kernel commit: {kernel_commit}
Rounds: {iterations}
Default image: {image}
Distro: {distro}

================================================
Statistics
================================================
Total tests: {total_tests}
Tests in scope: {tests_in_scope}
Tests out of scope: {tests_out_of_scope}
Passed: {tests_pass}
Failed: {tests_fail}
Crashed: {tests_crash}
Skipped: {tests_skip}
Timeout: {tests_timeout}
Incomplete: {tests_incomplete}
Dmesg warn: {dmesg_warn}
Warn: {warn}
Dmesg fail: {dmesg_fail}
Pass rate: {pass_rate}
Overall time: {overall_time}
Networking-service: {net_service}
Attached displays: {displays}

TRC link: {trc_link}
Backup link: {backup_link}
			'''.format(
			user=self.dut_user,
			pwd=self.dut_password,
			host_ip=self.dut_static_ip,
			host=self.dut_hostname,
			grub=self.grub_parameters,
			guc=self.guc,
			huc=self.huc,
			dmc=self.dmc,
			raspberry_ip=self.raspberry_ip,
			raspberry_number=self.raspberry_number,
			switch_number=self.raspberry_power_switch,
			usb_cutter=self.usb_cutter_serial,
			blacklist=self.blacklist_file,
			package=self.default_package,
			stack_code=self.gfx_stack_code,
			kernel_branch=self.kernel_branch,
			kernel_commit=self.kernel_commit,
			iterations=self.igt_iterations,
			image=self.default_image,
			distro=data['detailed_information']['distro'],
			total_tests=data['overall_tests_statistics']['total_tests'],
			tests_in_scope=data['overall_tests_statistics']['test_to_run'],
			tests_out_of_scope=data['overall_tests_statistics']['test_to_not_run'],
			tests_pass=data['overall_tests_statistics']['pass_tests'],
			tests_fail=data['overall_tests_statistics']['fail_tests'],
			tests_crash=data['overall_tests_statistics']['crash_tests'],
			tests_skip=data['overall_tests_statistics']['skip_tests'],
			tests_timeout=data['overall_tests_statistics']['timeout_tests'],
			tests_incomplete=data['overall_tests_statistics']['incomplete_tests'],
			dmesg_warn=data['overall_tests_statistics']['dmesg_warn_tests'],
			warn=data['overall_tests_statistics']['warn_tests'],
			dmesg_fail=data['overall_tests_statistics']['dmesg_fail_tests'],
			pass_rate=data['overall_tests_statistics']['pass_rate_of_executed'],
			overall_time=data['overall_tests_statistics']['OverallTime'],
			net_service=data['networking-service'],
			displays=display_list,
			trc_link=(
				data['trc_link']['url'] if data['trc_link']['url'] else 'Not set'),
			backup_link=(
				data['backup_link']['url']
				if data['backup_link']['url'] else 'Not set')
		)

		return report

	def check_execution_health(self, execution_data):
		"""Assess the health of the current test execution.

		Evaluates the health of the current test execution by reviewing the results
		of the last five tests ran in the platform. If it is found that all those
		tests have failed, is is assumed something fishy is going on with the
		execution and the platform is rebooted.
		:param execution_data: a dictionary containing data from the current test
		execution. This data is obtained from the watchdog API in the platform side
		:return reboot: True if the platform is suspected to be unstable and needs
		to be rebooted, False otherwise
		"""
		self.log.info(
			'checking last test results to determine execution health: {0}'
			.format(execution_data.get('last_five_results', {}).values())
		)

		# Initialize control flag and variables
		reboot = False
		count = 0
		max_bad_tests = 5
		bad_status = ['fail', 'crash', 'timeout', 'dmesg-fail', 'dmesg-warn', 'warn']

		# Count how many of the last five tests are "bad" tests
		for value in execution_data.get('last_five_results', {}).values():
			if value in bad_status:
				count += 1

		# If all tests are considered bad, send an email notifying maintainers
		# and set the reboot flag
		if count >= max_bad_tests:
			self.log.info(
				'last five tests have a "bad" status: {0}'
				.format(execution_data.get('last_five_results', {}).values())
			)
			reboot = True

			# Send an email reporting the state
			subject = 'Test environment unstable on {hostname} ({ip})'.format(
				hostname=self.dut_hostname, ip=self.dut_static_ip
			)
			email_msg = '''
The platform is suspected to be unstable since the last five consecutive tests
are in one of these status: fail, crash, timeout, dmesg-fail.
In order to restore stability to the environment the platform will be rebooted.

Platform: {hostname}
IP Address: {ip}
			'''.format(hostname=self.dut_hostname, ip=self.dut_static_ip)

			utils.emailer(
				self.email_sender,
				self.default_mailing_list,
				subject,
				email_msg
			)

			# Update the WD table with a useful message
			apiutils.update_watchdog_db(
				self.raspberry_number,
				self.raspberry_power_switch,
				Status='Test environment unstable. Reboot required.'
			)

		return reboot

	def data_manager(self, data):
		"""Handles the data received from the DUT.

		The function parses the data received, formats it, and sends it to the
		watchdog DB which displays the data in the watchdog web page. The data
		manager also analyses the test data to determine the status of the test
		execution.

		:param data: a data dictionary containing the current test execution status
		:return reboot: True if the platform needs to be rebooted, False otherwise
		:return finished: True if the tests already finished executing and the report
		has already been updated
		"""

		self.log.info('validating the data received from the platform')

		# Initial control values: unset
		reboot = False
		finished = False
		status = 'unknown'

		# Get the current execution status from the DUT data
		if 'currentExecution' in data:
			status = data['currentExecution'].get('status', None)

		self.log.info('current execution status: {0}'.format(status))

		if str(status) == 'waiting_folder':
			# This is the first stage that DUT goes through, the test
			# execution has not yet started, but the set up for the execution
			# has. All the dynamic data must be cleaned up.

			# Reset nodata flag
			self.nodata = False

			# Submit the data to update the DB
			apiutils.update_watchdog_db(
				RaspberryNumber=self.raspberry_number,
				PowerSwitchNumber=self.raspberry_power_switch,
				DutHostname=self.dut_hostname,
				DutIP=self.dut_static_ip,
				Status='Preparing the test environment',
				NetworkingService=data.get('networking-service', 'N/A')
			)

		elif str(status) == 'ongoing':
			# This is the second stage, when the DUT has already started running
			# the tests and they are in progress

			self.log.info(
				'current test running: {test}'
				.format(test=data.get('last_json', {}).get('test_name', 'N/A'))
			)

			# Reset nodata flag
			self.nodata = False

			# Preparing the data
			execution_status = (
				'{status} [{curr_iter}/{all_iter}]'
				.format(
					status=status,
					curr_iter=data.get('overall_tests_statistics', {})
					.get('current_iteration_folder', 'N/A'),
					all_iter=data.get('suite_conf', {})
					.get('igt_iterations', 'N/A')
				)
			)
			run_rate_percentage = (
				'{run_rate}%'.format(run_rate=data.get('overall_tests_statistics', {}).get(
					'run_rate', 'N/A'))
			)
			if self.default_package == 'igt_clone_testing':

				test_number = (
					'{progress} bunch ({curr}/{total}) ({trc_id})'
					.format(
						progress=data.get('overall_tests_statistics', {})
						.get('current_progress', 'N/A'),
						curr=self.current_tests_bunch,
						total=self.total_tests_bunches,
						trc_id=self.trc_report_id
					)
				)
				suite = '{pkg} (st)'.format(
					pkg=data.get('suite_conf', {}).get('default_package', 'N/A'),
					st=self.state)
			else:

				test_number = (
					data.get('overall_tests_statistics', {}).get('current_progress', 'N/A'))
				suite = data.get('suite_conf', {}).get('default_package', 'N/A')

			# Submit the data to update the DB
			apiutils.update_watchdog_db(
				RaspberryNumber=self.raspberry_number,
				PowerSwitchNumber=self.raspberry_power_switch,
				Status=execution_status,
				CurrentTestNumber=test_number,
				Suite=suite,
				Distro=(
					data.get('detailed_information', {}).
					get('distro', 'N/A')),
				DutHostname=(
					data.get('dut_conf', {})
					.get('dut_hostname', 'N/A')),
				DutIP=(
					data.get('dut_conf', {})
					.get('dut_static_ip', 'N/A')),
				KernelBranch=(
					data.get('suite_conf', {})
					.get('kernel_branch', 'N/A')),
				KernelCommit=(
					data.get('suite_conf', {})
					.get('kernel_commit', 'N/A')),
				GfxStackCode=(
					data.get('suite_conf', {})
					.get('gfx_stack_code', 'N/A')),
				GrubParameters=(
					data.get('dut_conf', {})
					.get('grub_parameters', 'N/A')),
				dmc=(
					data.get('firmwares', {})
					.get('dmc', 'N/A')),
				guc=(
					data.get('firmwares', {})
					.get('guc', 'N/A')),
				huc=(
					data.get('firmwares', {})
					.get('huc', 'N/A')),
				Blacklist=(
					data.get('suite_conf', {})
					.get('blacklist_file', 'N/A')),
				TotalTest=(
					data.get('overall_tests_statistics', {})
					.get('total_tests', 'N/A')),
				TestsToRun=(
					data.get('overall_tests_statistics', {})
					.get('test_to_run', 'N/A')),
				TestsToNotRun=(
					data.get('overall_tests_statistics', {})
					.get('test_to_not_run', 'N/A')),
				LastTestStatus=(
					data.get('last_json', {})
					.get('status', 'N/A')),
				CurrentTestName=(
					data.get('last_json', {})
					.get('test_name', 'N/A')),
				CurrentTestTime=(
					data.get('last_json', {})
					.get('time_elapsed', 'N/A')),
				DutUptime=(
					data.get('dut_uptime', {})
					.get('uptime', 'N/A')),
				BasicPassRate=(
					data.get('basic_statistics', {})
					.get('b_pass_rate', 'N/A')),
				Pass=(
					data.get('overall_tests_statistics', {})
					.get('pass_tests', 'N/A')),
				Fail=(
					data.get('overall_tests_statistics', {})
					.get('fail_tests', 'N/A')),
				Crash=(
					data.get('overall_tests_statistics', {})
					.get('crash_tests', 'N/A')),
				Skip=(
					data.get('overall_tests_statistics', {})
					.get('skip_tests', 'N/A')),
				Timeout=(
					data.get('overall_tests_statistics', {})
					.get('timeout_tests', 'N/A')),
				Incomplete=(
					data.get('overall_tests_statistics', {})
					.get('incomplete_tests', 'N/A')),
				DmesgWarn=(
					data.get('overall_tests_statistics', {})
					.get('dmesg_warn_tests', 'N/A')),
				Warn=(
					data.get('overall_tests_statistics', {})
					.get('warn_tests', 'N/A')),
				DmesgFail=(
					data.get('overall_tests_statistics', {})
					.get('dmesg_fail_tests', 'N/A')),
				PassRate=(
					data.get('overall_tests_statistics', {})
					.get('pass_rate_of_executed', 'N/A')
				),
				RunRate=run_rate_percentage,
				attachedDisplays=(
					data.get('attachedDisplays', {})),
				ETA=(
					data.get('dut_eta', {})
					.get('time', 'N/A'))
			)

			# Check if i915 kernel module is loaded in the remote system
			# in order to continue with the test cases.
			i915_module = data.get('i915_module', None)

			if not i915_module:
				self.log.warning('i915 kernel module was not found, rebooting')
				apiutils.update_watchdog_db(
					RaspberryNumber=self.raspberry_number,
					PowerSwitchNumber=self.raspberry_power_switch,
					Status='i915 kernel module was not found'
				)
				reboot = True
			else:
				# when a platform is rebooted because a test exceeded the test_timeout,
				# when the platform comes back online, the "current test" will still be
				# the test that caused the reboot, this happens because piglit has not
				# run yet, and piglit is the responsible for skipping the previously
				# incomplete tests.
				# Piglit takes about a minute after a reboot to start running, so until
				# then, the JSON file from the last test could be confused with being
				# the "current test", so we need to wait until Piglit is running.
				# Also, even when piglit has started running it takes about 12 seconds for
				# piglit to skip the old test and start running the new one, so we need to
				# account for that time too. We will wait for 15 seconds.
				self.log.info("the DUT's time is {0}".format(data.get('dut_time', 'N/A')))
				self.log.debug('piglit up? {0}'.format(data.get('piglit_running', False)))
				self.log.debug('piglit uptime: {0}'.format(data.get('piglit_uptime', 0)))
				if (
						data.get('piglit_running', False) and
						int(data.get('piglit_uptime', 0)) > 60
				):
					self.piglit_reboot_timeout = time.time() + self.piglit_timeout
					self.log.debug(
						'piglit reboot timeout: {0}'.format(self.piglit_reboot_timeout))
					current_test = data.get('last_json', {}).get('test_name', 'N/A')
					test_time = data.get('last_json', {}).get('minutes', 0)
					self.log.info(
						'the ctime of {json} is {time}'.format(
							json=data.get('last_json', {}).get('number', 'N/A'),
							time=data.get('last_json', {}).get('json_ctime', 'N/A')
						)
					)
					self.log.info(
						'test {test} has been running for {min} minutes'
						.format(test=current_test, min=test_time)
					)
					self.elapsed_test_time = test_time
					# if a test takes longer than the test timeout defined, the platform
					# must be rebooted, that way the current is left with incomplete
					# status in the JSON file and Piglit skips it after the reboot.
					if test_time >= self.test_timeout:
						self.log.info(
							'the current test {0} has been running for {1} minutes '
							'which exceeds the timeout of {2} minutes defined.'
							.format(current_test, test_time, self.test_timeout)
						)
						reboot = True
					else:
						# Make sure the test environment still looks healthy
						reboot = self.check_execution_health(data)

				else:
					self.log.info('Piglit is not running')
					self.log.debug(
						'current watchdog time: {0}'
						.format(str(datetime.datetime.fromtimestamp(time.time())))
					)
					self.log.debug(
						'current Piglit timeout value: {0}'
						.format(str(datetime.datetime.fromtimestamp(self.piglit_reboot_timeout)))
					)
					if time.time() > self.piglit_reboot_timeout:
						self.log.error(
							'Piglit did not start running within the timeout of '
							'{0} seconds'.format(self.piglit_timeout))
						reboot = True

		elif str(status) == 'finished':
			# This is the final stage when the platform has finished running the
			# tests. Information needs to be collected and reported

			# Reset nodata flag
			self.nodata = False

			# If either the TRC report or the backup report are enabled in the
			# config file, and the report URLs have not been provided, update
			# the table with a useful message and keep waiting for the URL
			if (
				(self.reportTRC and not data['trc_link']['url']) or
				(self.backupReport and not data['backup_link']['url'])
			):

				apiutils.update_watchdog_db(
					RaspberryNumber=self.raspberry_number,
					PowerSwitchNumber=self.raspberry_power_switch,
					Status='Waiting for the report URLs',
					CurrentTestName=' ',
					CurrentTestTime=' '
				)

				# The first time it enters this condition start the timeout timer
				if self.no_url_start_time == 0:
					self.no_url_start_time = time.time()
					self.log.info('Starting timeout timer')

				self.log.info(
					'Have been waiting for the report URLs for {0} seconds'
					.format(time.time() - self.no_url_start_time))

				# If the URLs are not provided within the timeout
				timeout = self.no_url_start_time + (self.no_url_timeout * 60)
				if time.time() > timeout:

					self.log.warn('No URLs received for the TRC/Backup reports from the DUT')
					# Add a message to the watchdog
					apiutils.update_watchdog_db(
						RaspberryNumber=self.raspberry_number,
						PowerSwitchNumber=self.raspberry_power_switch,
						Status='Error: The report URLs were not provided'
					)

					# send an email informing the situation
					email_subject = (
						'intel-gpu-tools finished but no URL were provided for ({host}) ({ip})'
						.format(host=self.dut_hostname, ip=self.dut_static_ip))

					email_body = self.create_report(data)
					utils.emailer(
						self.email_sender,
						self.default_mailing_list,
						email_subject,
						email_body
					)

					# Finish execution
					finished = True

			else:

				# Preparing the data
				if self.default_package == 'igt_clone_testing':

					test_number = ('bunch ({curr}/{total}) ({trc_id})'.format(
						curr=self.current_tests_bunch,
						total=self.total_tests_bunches,
						trc_id=self.trc_report_id)
					)
					suite = ('{pkg} (st)'.format(
						pkg=data.get('suite_conf', {}).get('default_package', 'N/A'),
						st=self.state)
					)

				else:

					test_number = ' '
					suite = data.get('suite_conf', {}).get('default_package', 'N/A')

				# Submit the data to update the DB
				apiutils.update_watchdog_db(
					RaspberryNumber=self.raspberry_number,
					PowerSwitchNumber=self.raspberry_power_switch,
					Suite=suite,
					CurrentTestNumber=test_number,
					CurrentTestTime=' ',
					CurrentTestName=' ',
					LastTestStatus=' ',
					ETA=' ',
					Status=(
						'{st} on {overall_time}'.format(
							st=status,
							overall_time=(
								data.get('overall_tests_statistics', {})
								.get('OverallTime', 'N/A'))
						)
					),
					Distro=(
						data.get('detailed_information', {})
						.get('distro', 'N/A')),
					DutHostname=(
						data.get('dut_conf', {})
						.get('dut_hostname', 'N/A')),
					DutIP=(
						data.get('dut_conf', {})
						.get('dut_static_ip', 'N/A')),
					KernelBranch=(
						data.get('suite_conf', {})
						.get('kernel_branch', 'N/A')),
					KernelCommit=(
						data.get('suite_conf', {})
						.get('kernel_commit', 'N/A')),
					GfxStackCode=(
						data.get('suite_conf', {})
						.get('gfx_stack_code', 'N/A')),
					GrubParameters=(
						data.get('dut_conf', {})
						.get('grub_parameters', 'N/A')),
					dmc=(
						data.get('firmwares', {})
						.get('dmc', 'N/A')),
					guc=(
						data.get('firmwares', {})
						.get('guc', 'N/A')),
					huc=(
						data.get('firmwares', {})
						.get('huc', 'N/A')),
					Blacklist=(
						data.get('suite_conf', {})
						.get('blacklist_file', 'N/A')),
					TotalTest=(
						data.get('overall_tests_statistics', {})
						.get('total_tests', 'N/A')),
					Pass=(
						data.get('overall_tests_statistics', {})
						.get('pass_tests', 'N/A')),
					Fail=(
						data.get('overall_tests_statistics', {})
						.get('fail_tests', 'N/A')),
					Crash=(
						data.get('overall_tests_statistics', {})
						.get('crash_tests', 'N/A')),
					Skip=(
						data.get('overall_tests_statistics', {})
						.get('skip_tests', 'N/A')),
					Timeout=(
						data.get('overall_tests_statistics', {})
						.get('timeout_tests', 'N/A')),
					Incomplete=(
						data.get('overall_tests_statistics', {})
						.get('incomplete_tests', 'N/A')),
					DmesgWarn=(
						data.get('overall_tests_statistics', {})
						.get('dmesg_warn_tests', 'N/A')),
					Warn=(
						data.get('overall_tests_statistics', {})
						.get('warn_tests', 'N/A')),
					DmesgFail=(
						data.get('overall_tests_statistics', {})
						.get('dmesg_fail_tests', 'N/A')),
					PassRate=(
						data.get('overall_tests_statistics', {})
						.get('pass_rate_of_executed', 'N/A')),
					attachedDisplays=(
						data.get('attachedDisplays', {})),
					OverallTime=(
						data.get('overall_tests_statistics', {})
						.get('OverallTime', 'N/A')),
					TRCLink=(
						data.get('trc_link', {})
						.get('url', 'N/A'))
				)

				# Send the results of the execution by email
				email_subject = (
					'intel-gpu-tools execution finished on ({0}) ({1}) Overall time '
					'({2})'.format(
						self.dut_hostname,
						self.dut_static_ip,
						data.get('overall_tests_statistics', {}).get('OverallTime', 'N/A')
					)
				)
				email_body = self.create_report(data)
				utils.emailer(
					self.email_sender,
					self.default_mailing_list,
					email_subject,
					email_body
				)

				# At this point the tests have already finished running and the
				# results have been updated in the DB
				finished = True

		elif str(status) == 'wrapping_up':
			# this stage means the test execution has finished running the tests
			# but results are still being collected, and files are being cleaned
			# up

			# Reset nodata flag
			self.nodata = False

			apiutils.update_watchdog_db(
				RaspberryNumber=self.raspberry_number,
				PowerSwitchNumber=self.raspberry_power_switch,
				Status='Collecting test results'
			)

		elif str(status) == 'fail_html':
			# This status is for a special error case:
			# Sometimes Piglit incorrectly generates an error and creates an
			# HTML folder inside the iteration folder, but the tests have not
			# finished running yet which means the tests directory exists.
			# The html directory should be deleted and the platform rebooted.

			# Reset nodata flag
			self.nodata = False

			apiutils.update_watchdog_db(
				RaspberryNumber=self.raspberry_number,
				PowerSwitchNumber=self.raspberry_power_switch,
				Status='Error: html folder exists, deleting it...',
			)

			# NOTE: The actual deletion of the html directory is done by another
			# script running in the platform side. This because trying to delete
			# the directory remotely from the watchdog could lead to errors since
			# sometimes the platform can become unresponsive.
			# This dutWatcher script running in the platform deletes the directory
			# all its needed in this side is to reboot the platform
			reboot = True

		elif str(status) == 'nodata':
			# Case when the DUT responds but the response ha no data

			apiutils.update_watchdog_db(
				self.raspberry_number,
				self.raspberry_power_switch,
				Status='Error: no data was received from the DUT',
			)

			# If this is the first time the platform enters in this state, start
			# the timer
			if not self.nodata:
				self.nodata = True
				self.nodata_real_timeout = time.time() + (self.nodata_timeout * 60)
				self.log.info('the DUT returned "nodata", starting timeout timer')
			else:
				# If the platform has been returning "nodata" for more than the
				# timeout value, reboot the platform
				if time.time() > self.nodata_real_timeout:
					reboot = True
					self.log.info(
						'the DUT has been responding with "nodata" for {0} '
						'minutes, timeout exceeded'
						.format(self.nodata_timeout)
					)
					# reset the control flag in case this condition happens again
					self.nodata = False

		else:
			# Fallback option in case the API returns an empty or unknown state

			# Reset nodata flag
			self.nodata = False

			status_update = 'Error: unknown DUT state'
			self.log.warn(status_update)
			apiutils.update_watchdog_db(
				self.raspberry_number,
				self.raspberry_power_switch,
				Status=status_update
			)

		# Return the control flags
		# reboot: indicates if the platform needs to be rebooted
		# finished: indicates if the tests have finished execution either
		# correctly or incorrectly
		return reboot, finished

	def connect_with_dut(self, timeout):
		"""Attempts to establish a connection with the DUT.

		Tries to connects to a given platform in order to get data from it. If
		the platform is not responsive for a given time it returns the
		responsiveness status.

		:param timeout: the amount of minutes the connection will be attempted
		:return data: returns the execution data received from the platform, if
		the platform is not responsive it returns False
		"""

		self.log.info(
			'attempting connection with platform {hostname} ({ip})'
			.format(hostname=self.dut_hostname, ip=self.dut_static_ip)
		)

		# when defining the timeout is necessary to take in consideration how long
		# the current test has already been running (if any). This way we avoid
		# falling in the situation where a test has already been running for some
		# time, let's say for 9 minutes, and then it stops responding for another
		# 10 minutes which would sum up to 19 minutes in this example instead of
		# the intended original timeout. So its necessary to use the reminder of
		# the test time if that is less than the actual connection timeout
		connection_timeout = timeout * 60
		test_time_remaining = (self.test_timeout - self.elapsed_test_time) * 60
		real_timeout = (
			connection_timeout
			if connection_timeout < test_time_remaining
			else test_time_remaining)

		start_time = time.time()
		end_time = start_time + real_timeout
		while True:

			# sleep to lower the number of requests watchdog does to
			# the API (this reduces network traffic, api load, etc.)
			time.sleep(self.wait_between_cycles)

			# Call the DUT API and wait up to the API timeout for a response
			try:
				response = requests.get(self.dut_api, timeout=self.dut_api_timeout)
				response.raise_for_status()
				data = response.json()
				self.log.info('connection established successfully')
				return data

			except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
				# Get the current minutes and seconds since the first
				# connection attempt.
				_minute, _seconds = divmod((time.time() - start_time), 60)
				minutes = int(_minute)
				seconds = int(_seconds)

				# Send the status update
				formatted_minutes = (
					'{mins} minute{s} '.format(mins=minutes, s='s' if minutes > 1 else '')
				)
				formatted_seconds = '{0} seconds'.format(seconds)
				status = 'DUT has not responded for {mins}{secs}'.format(
					mins=formatted_minutes if minutes > 0 else '', secs=formatted_seconds)
				apiutils.update_watchdog_db(
					self.raspberry_number,
					self.raspberry_power_switch,
					Status=status
				)
				self.log.debug(status)

			except requests.exceptions.HTTPError:
				# When the dut_watcher API is responding but it has an Internal server
				# error it will generate this exception. In that case it may be a good
				# idea to try restarting the API via an SSH connection
				self.log.error(
					'the dut_watcher service is in error, status code: ({code}) {msg}'
					.format(code=response.status_code, msg=response.text)
				)
				self.log.info('trying to restart the dut_watcher service via SSH')
				try:
					dut = remote_client.RemoteClient(
						self.dut_static_ip, user=self.dut_user, password=self.dut_password
					)
					error_code, output = dut.run_command(
						'sudo systemctl restart dutwatcher.service'
					)
					if not error_code:
						self.log.info('the dut_watcher service was restarted successfully')
					else:
						self.log.error(
							'there was an error restarting the dut_watcher service: ({code}) {msg}'
							.format(code=error_code, msg=output)
						)
				except (socket.timeout, paramiko.ssh_exception.SSHException):
					self.log.error(
						'watchdog could not establish SSH communication with {host}'
						.format(host=self.dut_static_ip)
					)

			except ValueError:
				# Sometimes on network errors an HTML is returned with a message
				# from a proxy server or router, since that cannot be decoded
				# in json format, it generates a ValueError exception
				self.log.error(
					'unexpected response when attempting connection with {0} ({1}):\n{2}'
					.format(self.dut_hostname, self.dut_static_ip, response.text),
					exc_info=True)

			# If the timeout for the connection has already been reached
			# return False and exit
			if time.time() > end_time:
				self.log.info('the platform did not respond for {timeout} minutes'.format(
					timeout=timeout))
				return False

	def monitor_dut(self):
		"""Monitors the DUT for responsiveness.

		If the platform (DUT) is responsive it gets its current information and
		updates the watchdog GUI. If the platform is not responsive it reboots
		it then updates the watchdog GUI. If the tests have finished running
		the watchdog is turned off.
		"""

		self.piglit_reboot_timeout = time.time() + self.piglit_timeout
		self.log.info('started monitoring platform {hostname} ({ip})'.format(
			hostname=self.dut_hostname, ip=self.dut_static_ip))
		apiutils.cleanup_watchdog_row(
			RaspberryNumber=self.raspberry_number,
			PowerSwitchNumber=self.raspberry_power_switch,
			DutHostname=self.dut_hostname,
			DutIP=self.dut_static_ip
		)

		while True:

			self.log.info('--------------------------------------------------')
			# Reset control flags
			finished = False
			reboot = False

			# Make HTTP requests to the API running in the platform to check
			# for responsiveness. If it doesn't respond, keep trying for up to
			# X minutes
			response = self.connect_with_dut(self.dut_connection_timeout)

			if response:

				# Format the data and update the DB with current status
				reboot, finished = self.data_manager(response)

				if not reboot:
					# Since the platform responded, reset the flag for consecutive
					# reboots
					self.consecutive_reboots = 0
					self.log.info('consecutive reboots: {0}'.format(self.consecutive_reboots))

			else:
				# check if the platform has been rebooted N consecutive times
				# if so, the platform may need manual attention, notify the
				# maintainers and turn off watchdog
				if self.consecutive_reboots > self.consecutive_reboots_allowed:
					apiutils.update_watchdog_db(
						self.raspberry_number,
						self.raspberry_power_switch,
						Status='ATTENTION REQUIRED: the DUT was still unresponsive '
						'after {N} reboots'.format(N=self.consecutive_reboots - 1)
					)
					utils.emailer(
						self.email_sender,
						self.default_mailing_list,
						'IGT execution failed on ({hostname}) ({ip})'
						.format(hostname=self.dut_hostname, ip=self.dut_static_ip),
						'The platform was rebooted {N} times and still is not'
						'responding. This platform may require manual intervention.'
						.format(N=self.consecutive_reboots - 1)
					)
					finished = True
					# Sleep for 90 seconds before turning off watchdog to prevent
					# run_igt from starting watchdog again at this point.
					time.sleep(90)

				else:
					# the DUT is not responding, update WD table with a message
					# about the platform being rebooted
					apiutils.update_watchdog_db(
						self.raspberry_number,
						self.raspberry_power_switch,
						Status='The DUT has been unresponsive for {0} minutes, '
						'rebooting...'.format(self.dut_connection_timeout))

					# Send an email notification
					utils.emailer(
						self.email_sender,
						self.default_mailing_list,
						'connection refused on (' + str(self.dut_hostname) +
						') (' + str(self.dut_static_ip) + ')',
						'unable to connect to DUT after {0} minutes, '
						'rebooting...'.format(self.dut_connection_timeout))

					# Set the reboot control flag
					reboot = True

			# Check control flags
			if reboot:

				self.consecutive_reboots += 1
				self.log.info('consecutive reboots: {0}'.format(self.consecutive_reboots))
				# Hard reboot the platform
				if not self.reboot_dut(self.raspberry_number, self.raspberry_power_switch):
					# TODO(Cas): it may be necessary to act on the reboot result
					# If the reboot_dut method return False, it means the platform
					# did not responded to ping after a reboot. It may be necessary
					# to reboot it again, this could fix possible network config issues
					# remove this counter after observing the behavior
					self.non_responsive_after_reboot += 1
					self.log.warn(
						'the platform was unresponsive after a reboot. This '
						'condition has happened {0} time(s) since watchdog started'
						.format(self.non_responsive_after_reboot)
					)

			elif finished:
				# Exit the script
				# TODO(Cas): remove this log message after observing behavior
				self.log.warn(
					'the platform was unresponsive after being rebooted {0} times'
					.format(self.non_responsive_after_reboot)
				)
				self.log.info('test execution completed, exiting watchdog')
				sys.exit()


if __name__ == '__main__':
	# Parse the command line arguments (if any)
	parser = argparse.ArgumentParser(
		description='Start a watchdog process to monitor a platform responsiveness.')
	parser.add_argument(
		'-c', '--config', help=(
			'specify a config file to run watchdog with. If no config file is '
			'specified the watchdog looks for a config.yml in the current path.')
	)
	# TODO(Cas): remove these positional arguments once they are not needed
	# the optional positional parameters are not needed at all by the watchdog.py
	# script, however they are needed by the watchdog.js program that launches the
	# watchdog.py script when a user clicks on the "watchdog eye" in the watchdog
	# GUI. These parameters need to be removed when the watchdog.js file is
	# revised and refactored. These should not be here since they are not needed
	# by this script so they are misleading for the user.
	parser.add_argument('raspberry_number', nargs='?')
	parser.add_argument('switch_number', nargs='?')

	args = parser.parse_args()

	# Start the watchdog monitor
	Watchdog(args).monitor_dut()
