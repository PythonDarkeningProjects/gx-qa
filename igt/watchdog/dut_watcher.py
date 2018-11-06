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
"""This module works as a reporter of the IGT execution status"""

from __future__ import division
from __future__ import print_function

import argparse
import datetime
import glob
import json
import logging
import logging.handlers
import os
import platform
import sys
import time

from flask import Flask
import yaml

from common import apiutils
from gfx_qa_tools.common import bash
from gfx_qa_tools.common import utils

# To run the DUT watcher web app run the following commands:
# $ export FLASK_APP=igt/watchdog/dut_watcher.py
# $ flask run --host=0.0.0.0 -p 4040

app = Flask(__name__)


@app.route('/statistics')
def dut_watcher():
	"""Web app for the DUT watcher.

	:return: returns all the statistics from the current test execution.
	"""
	return DutWatcher().get_statistics()


@app.route('/firmwares')
def get_firmware_version():
	"""Gets the firmware version loaded into the kernel.

	Collects the required GUC, HUC and DMC firmware versions for the
	host's
	kernel, and its load status.
	:return: a tuple with the required values for GUC, HUC and DMC
	firmwares,
	if the firmwares failed to be loaded or have a different version than
	the
	expected one, it returns None for that firmware
	"""
	# initialize values
	guc_version = None
	huc_version = None
	dmc_version = None

	# Make sure the dri data is available
	dri_path = '/sys/kernel/debug/dri/0'
	if utils.isdir(dri_path):

		# get the GUC requirements
		guc_file = os.path.join(dri_path, 'i915_guc_load_status')
		if utils.isfile(guc_file):

			# depending on the kernel version we might have a couple of
			# variations in the content of the file, so we need to consider both
			error_code, output = bash.run_command(
				"sudo cat {guc} | grep 'GuC firmware:'".format(guc=guc_file)
			)

			# if there is no error code, it means the content of the file should
			# contain something similar to this:
			# status: fetch SUCCESS, load SUCCESS\n\t
			# version: wanted 9.39, found 9.39
			# or when not loaded:
			# status: fetch NONE, load NONE\n\t
			# version: wanted 9.39, found 0.0
			if not error_code:
				error_code, output = bash.run_command(
					"sudo cat {guc} | egrep 'version:|status:'"
					.format(guc=guc_file))
				if not error_code:
					output = output.split('\n')
					status = output[0]
					version = output[1].replace(',', '').split()
					# grab the firmware version only if the version found
					# matches the wanted version
					guc_version = version[4] if version[2] == version[4] else None
					# finally verify "fetch" and "load" have both SUCCESS
					# status, if they don't then return None as firmware version
					guc_version = guc_version if status.count('SUCCESS') == 2 else None

			# if there an error code, it means the content of the file should
			# contain something similar to this:
			# fetch: SUCCESS\n\t
			# load: SUCCESS\n\t
			# version wanted: 6.1\n\t
			# version found: 6.1\n\t
			else:
				error_code, output = bash.run_command(
					"sudo cat {guc} | egrep 'fetch:|load:|version wanted:|version found:'"
					.format(guc=guc_file))
				if not error_code:
					output = output.replace('\t', '').split('\n')
					loaded = True if 'SUCCESS' in output[0] and output[1] else False
					version_wanted = output[2].replace('version wanted: ', '')
					version_found = output[3].replace('version found: ', '')
					correct_version = True if version_wanted == version_found else False
					guc_version = version_found if correct_version and loaded else None

		# get the HUC requirements
		huc_file = os.path.join(dri_path, 'i915_huc_load_status')
		if utils.isfile(huc_file):

			error_code, output = bash.run_command(
				"sudo cat {huc} | grep 'HuC firmware:'".format(huc=huc_file)
			)

			if not error_code:
				error_code, output = bash.run_command(
					"sudo cat {huc} | egrep 'version:|status:'".format(huc=huc_file))
				if not error_code:
					output = output.split('\n')
					status = output[0]
					version = output[1].replace(',', '').split()
					huc_version = version[4] if version[2] == version[4] else None
					huc_version = huc_version if status.count('SUCCESS') == 2 else None

			else:
				error_code, output = bash.run_command(
					"sudo cat {huc} | egrep 'fetch:|load:|version wanted:|version found:'"
					.format(huc=huc_file))
				if not error_code:
					output = output.replace('\t', '').split('\n')
					loaded = True if 'SUCCESS' in output[0] and output[1] else False
					version_wanted = output[2].replace('version wanted: ', '')
					version_found = output[3].replace('version found: ', '')
					correct_version = True if version_wanted == version_found else False
					huc_version = version_found if correct_version and loaded else None

		# get the DMC requirements
		dmc_file = os.path.join(dri_path, 'i915_dmc_info')
		if utils.isfile(dmc_file):

			# the content of the file should contain something similar to this:
			# fw loaded: yes\nversion: 1.4
			# or when not loaded:
			# fw loaded: no
			error_code, output = bash.run_command(
				"sudo cat {dmc} | egrep 'loaded:|version:'".format(dmc=dmc_file))
			if not error_code:
				output = output.split('\n')
				status = output[0].split()[2]
				version = output[1].split()[1] if len(output) > 1 else None
				dmc_version = version if status == 'yes' else None

	firmwares = {
		'guc': guc_version,
		'huc': huc_version,
		'dmc': dmc_version
	}

	# print and return the formatted data
	print(json.dumps(firmwares))
	return json.dumps(firmwares)


class DutWatcher(object):
	"""Collects test execution data from a platform.

	Graphics tests are sometimes very long running and can be very resource
	intensive which could cause a platform to become unresponsive, among other
	problems. To mitigate this problem, the infrastructure uses a watchdog that
	keeps making requests to the platform running the tests for two purposes:
	1) to make sure the platform is still responsive, 2) to ask for data about
	progress in the current test execution to the platform. This is a two tier
	activity, the "monitor" which lives in a server that controls the execution,
	and the "reporter" which lives in each platform executing tests (a.k.a DUT).
	The DutWatcher plays the role of the "reporter" in this case.
	"""

	def __init__(self):

		# Load the test execution config file
		config_file = '/home/custom/config.yml'
		self.data = yaml.load(open(config_file))
		app.logger.info(
			'configuring dut_watcher using configuration file: {0}'
			.format(config_file))

		# DUT Configuration
		self.autologin = self.data['dut_conf']['autologin']
		self.dut_user = self.data['dut_conf']['dut_user']
		self.dut_password = self.data['dut_conf']['dut_password']
		self.dut_hostname = self.data['dut_conf']['dut_hostname']
		self.dut_static_ip = self.data['dut_conf']['dut_static_ip']
		self.graphical_environment = self.data['dut_conf']['graphical_environment']
		self.grub_parameters = self.data['dut_conf']['grub_parameters']

		# Firmwares
		self.dmc = self.data['firmwares']['dmc']
		self.guc = self.data['firmwares']['guc']
		self.huc = self.data['firmwares']['huc']

		# Raspberry Configuration
		self.raspberry_gpio = self.data['raspberry_conf']['raspberry_gpio']
		self.raspberry_ip = self.data['raspberry_conf']['raspberry_ip']
		self.raspberry_number = self.data['raspberry_conf']['raspberry_number']
		self.raspberry_power_switch = (
			self.data['raspberry_conf']['raspberry_power_switch'])
		self.raspberry_user = self.data['raspberry_conf']['raspberry_user']
		self.usb_cutter_serial = self.data['raspberry_conf']['usb_cutter_serial']

		# Suite Configuration
		self.blacklist_file = self.data['suite_conf']['blacklist_file']
		self.default_mailing_list = self.data['suite_conf']['default_mailing_list']
		self.default_package = self.data['suite_conf']['default_package']
		self.gfx_stack_code = self.data['suite_conf']['gfx_stack_code']
		self.kernel_branch = self.data['suite_conf']['kernel_branch']
		self.kernel_commit = self.data['suite_conf']['kernel_commit']
		self.igt_iterations = self.data['suite_conf']['igt_iterations']

		# Autouploader Information
		self.currentEnv = self.data['autouploader']['currentEnv']
		self.currentPlatform = self.data['autouploader']['currentPlatform']
		self.currentRelease = self.data['autouploader']['currentRelease']
		self.currentSuite = self.data['autouploader']['currentSuite']
		self.currentTittle = self.data['autouploader']['currentTittle']
		self.reportTRC = self.data['autouploader']['trc_report']

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

		# This is the timeout set up in the Watchdog monitor to finish running
		# one test, if a test takes longer than this timeout, the platform is
		# rebooted so the test is skipped (in minutes)
		self.test_timeout = 11

		# We can add more testlist (suites)
		# Getting the current testlist
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
			app.logger.warn(
				'no test list found for the selected package: {0}'
				.format(self.default_package))
			bash.message('err', 'No test list found for the selected package.')
			sys.exit(1)
		app.logger.info(
			'default Package: {package}, Test list: {test_list}'
			.format(package=self.default_package, test_list=self.current_testlist)
		)

		# Useful paths
		self.scripts_path = os.path.join(
			'/home', self.dut_user, 'intel-graphics', 'intel-gpu-tools', 'scripts')
		self.tests_path = os.path.join(
			'/home', self.dut_user, 'intel-graphics', 'intel-gpu-tools', 'tests')
		self.trc_url_file = os.path.join('/home', self.dut_user, 'trc2.log')
		self.breport_url_file = os.path.join(
			'/home', self.dut_user, 'backupReport.log')
		self.iterations_list = glob.glob('{0}/*iteration*'.format(self.scripts_path))
		self.iterations_list.sort()  # iteration1, iteration2, etc.
		if len(self.iterations_list) > 0:
			self.current_iteration = self.iterations_list[-1]
			self.final_json = os.path.join(self.iterations_list[0], 'results.json')
		else:
			self.current_iteration = None
			self.final_json = None
		if self.current_iteration:
			self.iteration_tests = os.path.join(self.current_iteration, 'tests')
			self.iteration_html = os.path.join(self.current_iteration, 'html')
			self.jsons_path = os.path.join(self.current_iteration, 'tests')
			app.logger.info(
				'current iteration directory: {0}'.format(self.current_iteration))

		# Control files
		self.igt_timestamp_file = (
			os.path.join('/home', self.dut_user, '.igt_timestamp'))
		if self.current_iteration:
			self.igt_done_file = os.path.join(self.current_iteration, '.igt_done')

	def get_execution_eta(self, tests_in_scope):
		"""Get an estimate of the remaining time to complete test execution.

		Calculates an estimate of the remaining time for finishing the current test
		execution. In order to do this calculation is necessary to analyze the
		time the tests that already finished took to run. These values can be taken
		from the individual json files created for each test ran.
		:param tests_in_scope: the total number of tests in scope for this test
		execution
		:return: the amount of time estimated to finish execution
		"""

		app.logger.info('calculating the ETA')

		# if the directory where the tests should be does not exist return an
		# an empty dictionary
		if not os.path.exists(self.jsons_path):
			app.logger.warn(
				'the "test" directory that contains the json files was not '
				'found')
			return {}

		# get all the json files from executed tests
		json_files = filter(
			lambda jfile: os.path.isfile(os.path.join(self.jsons_path, jfile))
			and not jfile.endswith('.tmp'),
			os.listdir(self.jsons_path)
		)
		number_of_tests_executed = len(json_files)
		app.logger.debug(
			'number of tests executed: {0}'.format(number_of_tests_executed))

		# get the time each test took to run from its json file
		execution_time = []
		for element in json_files:
			with open(os.path.join(self.jsons_path, element)) as json_file:
				json_data = json.load(json_file)
			start_time = json_data[next(iter(json_data))]['time']['start']
			end_time = json_data[next(iter(json_data))]['time']['end']

			# there are certain conditions that may cause the estimate to go crazy
			# if they happen, so, we need to consider all those here to provide a
			# better estimate
			# 1) First we need to skip the skipped since they didn't actually run
			if json_data[next(iter(json_data))]['result'] == 'skip':
				continue
			# 2) Sometimes, when a tests fails, if the failure was caused by an
			# exception, they don't register and "end" time, which would cause a
			# negative time if considered, so we need to ignore those cases too
			elif end_time == 0:
				continue
			# 3) Finally, if the test is "incomplete" it won't have any start or
			# end time, but we can assume it took ~10 minutes then it was skipped
			# by watchdog reboot + piglit, so use that time
			elif json_data[next(iter(json_data))]['result'] == 'incomplete':
				execution_time.append(self.test_timeout * 60)
			else:
				execution_time.append(end_time - start_time)

		# get the average time spent per test (in seconds)
		if len(execution_time) > 0:
			seconds_average = sum(execution_time) / len(execution_time)
			app.logger.debug('execution average per test: {0}'.format(seconds_average))
		else:
			seconds_average = 0
			app.logger.debug(
				'there is no useful data to calculate an average execution time '
				'per test. This could mean there is no JSON files with a valid '
				'recorded time.')

		# calculate the remaining time (in seconds)
		remaining_tests = tests_in_scope - number_of_tests_executed
		app.logger.debug('remaining tests: {0}'.format(remaining_tests))
		eta = int(seconds_average * remaining_tests)
		eta_formatted = str(datetime.timedelta(seconds=eta))
		app.logger.info('execution eta: {0}'.format(eta_formatted))

		return {'eta': eta_formatted}

	def get_last_tests(self):
		"""Gets the results from the last tests (up to five).

		Sometimes when a test environment becomes corrupted, and things start to
		go wrong, the fist symptom is that all tests start to fail, so this function
		collects the result of the last tests executed (up to five) so they can be
		evaluated in the watchdog monitor.
		:return: a dictionary containing the name of the test as key and its result
		as value.
		"""

		app.logger.info('getting data from the last five tests')

		# if the directory where the tests should be does not exist return an
		# empty dictionary
		if not os.path.exists(self.jsons_path):
			app.logger.warn(
				'the "test" directory that contains the json files was not '
				'found')
			return {}

		# find the last five json files among all without counting the very last
		# one, the last one will always show as incomplete, since it is still in
		# progress. Tests that are being run at the moment show status=incomplete
		json_files = filter(
			lambda jfile: os.path.isfile(os.path.join(self.jsons_path, jfile))
			and not jfile.endswith('.tmp'), os.listdir(self.jsons_path)
		)
		json_files = sorted(json_files, key=lambda x: int(x.strip('.json')))
		json_files = json_files[-6:-1]

		# gather the result from each one in a dict with this form
		# {test_name: test_result}
		results = {}
		for element in json_files:
			with open(os.path.join(self.jsons_path, element)) as json_file:
				json_data = json.load(json_file)
			results[next(iter(json_data)).encode().replace('igt@', '')] = (
				json_data[next(iter(json_data))]['result'].encode()
			)
		app.logger.debug(
			json.dumps(results, sort_keys=True, indent=4, separators=(',', ': '))
		)

		return {'last_tests': results}

	def get_last_test(self):
		"""Gets the execution details from the last test json.

		When the test execution is in progress a json file is created for each one
		of the tests that have been run or are in progress. These files are named
		1.json, 2.json, 3.json, etc. The file with the higher numeric index
		represents either the current test being run, or the last test that was run.
		This function collects data from this file in order to provide information
		to the watchdog monitor.
		:return: a dictionary containing data from the test being run
		"""

		app.logger.info('getting data from the last test')

		# if the directory where the tests should be does not exist return an
		# an empty dictionary
		if not os.path.exists(self.jsons_path):
			app.logger.warn(
				'the "test" directory that contains the json files was not found')
			return {}

		# find the last json file among all
		json_files = filter(
			lambda jfile: os.path.isfile(os.path.join(self.jsons_path, jfile))
			and not jfile.endswith('.tmp'),
			os.listdir(self.jsons_path)
		)
		json_files = sorted(json_files, key=lambda x: int(x.strip('.json')))
		last_test_file = json_files[-1]
		last_test_file_path = os.path.join(self.jsons_path, last_test_file)
		app.logger.debug('json file: {0}'.format(last_test_file))

		# get the content of the file
		with open(last_test_file_path) as file_mgr:
			test_data = json.load(file_mgr)
			app.logger.debug(
				'content from file {jfile}: \n {jdata}'
				.format(jfile=last_test_file_path, jdata=test_data)
			)

		# from the last json, get the required execution data
		raw_data = dict()
		# number -> the name of the json file
		raw_data['number'] = last_test_file
		# test_name -> the name of the test without the igt@ prefix
		raw_data['test_name'] = next(iter(test_data)).encode().replace('igt@', '')
		# status -> the result of the test execution
		raw_data['status'] = test_data[next(iter(test_data))]['result']
		# minutes -> the amount of minutes since the test started running to
		# present time
		json_ctime = os.path.getctime(last_test_file_path)
		diff_seconds = time.time() - json_ctime
		minutes, seconds = divmod(int(diff_seconds), 60)
		hours, minutes = divmod(minutes, 60)
		raw_data['minutes'] = minutes
		# time_elapsed -> the amount of time has passed since the test started
		# running to present time with the following format:
		# XX hours XX minutes XX seconds
		h = '{0} hours '.format(hours) if hours > 0 else ''
		m = '{0} minutes '.format(minutes) if minutes > 0 else ''
		raw_data['time_elapsed'] = '{h}{m}{s} seconds'.format(h=h, m=m, s=seconds)
		# for debugging purposes it is useful to also return the ctime of the json
		# file since we are calculating the test elapsed time from it
		raw_data['json_ctime'] = str(datetime.datetime.fromtimestamp(json_ctime))

		# return data
		app.logger.debug('last_json data: \n {0}'.format(raw_data))
		return raw_data

	def get_overall_time(self):
		"""Gets the total time that the test execution has been running.

		When the run_IGT.py script starts a test execution, it creates a file called
		.igt_timestamp, this function gets the time when this file was created to
		see how long the tests have been running.
		:return: returns the time the test execution has been running in format
		HH:MM:SS. If the file is not found it returns N/A.
		"""
		if not os.path.isfile(self.igt_timestamp_file):
			return 'N/A'

		creation_date = os.path.getctime(self.igt_timestamp_file)
		time_difference = time.time() - creation_date
		minutes, seconds = divmod(int(time_difference), 60)
		hours, minutes = divmod(minutes, 60)
		return '{hour:02d}:{min:02d}:{sec:02d}'.format(
			hour=hours, min=minutes, sec=seconds
		)

	def get_execution_status(self, tests_in_scope):
		"""Determines the status of the current test execution.

		Analyzes the existence and content of some directories and control files
		to determine the status of the execution.
		:param tests_in_scope: the total number of tests in scope for this test
		execution
		:return: a dictionary with raw data which at the very least includes the
		current status
		"""

		app.logger.info('determining execution status')

		# If there is no directory for the current iteration yet, it means
		# the test execution has not started yet, other scripts may still be
		# preparing the test infrastructure.
		# Action: None, Status: waiting_folder
		if not self.current_iteration:
			app.logger.info('status: waiting_folder')
			return {'status': 'waiting_folder'}

		# Look for the control file ".igt_done" which is generated by run_IGT.py
		# when the test execution finishes.
		# Action: get_data(), Status: finished
		if os.path.isfile(self.igt_done_file):
			app.logger.info('status: finished')
			raw_data = self.get_execution_data('finished', tests_in_scope)
			raw_data['status'] = 'finished'
			return raw_data

		# If the tests directory within the current iteration doesn't exist, and
		# the ".igt_done" file does not exist either, it probably means the
		# execution finished and results are being collected.
		# Action: None, Status: wrapping_up
		if not os.path.exists(self.iteration_tests):
			app.logger.info('status: wrapping_up')
			return {'status': 'wrapping_up'}

		# If the tests directory within the current iteration exists, it may mean
		# the test execution is in progress, so if an html directory exists at this
		# point then it means something wrong is going on since that should only
		# exist once the test execution has finished.
		# Action: delete_html(), Status: "fail_html"
		if os.path.exists(self.iteration_html):
			app.logger.info('status: fail_html')
			self.delete_html()
			return {'status': 'fail_html'}

		# If the tests directory exists and has content and no html directory
		# exists, the test execution is in progress normally.
		# Action: get_data(), Status: ongoing
		if os.listdir(self.iteration_tests):
			app.logger.info('status: ongoing')
			raw_data = self.get_execution_data('ongoing', tests_in_scope)
			raw_data['status'] = 'ongoing'
			return raw_data

		# Fallback case (it covers when the iteration tests directory exists
		# but is empty, along with any other case not specifically considered).
		# Action: None, Status: waiting_folder
		app.logger.warn('falling back to default status: waiting_folder')
		return {'status': 'waiting_folder'}

	def get_execution_data(self, status, tests_in_scope):
		"""Collects status-dependent information from the current test execution.

		:param status: the current status of the test execution
		:param tests_in_scope: the total number of tests in scope for this test
		execution
		:return: an non-formatted dictionary containing all the execution data
		"""

		# initializing variables for statistics
		(
			pass_tests, fail_tests, crash_tests, skip_tests, timeout_tests, not_run,
			incomplete_tests, warn_tests, dmesg_warn_tests, dmesg_fail_tests
		) = (0,) * 10
		trc_link = ''
		breport_link = ''
		year = ' '
		ww = ' '
		execution_data = {}

		if status == 'ongoing':

			# since the test execution is ongoing there should be a json file for
			# each executed tests. Create a list with all the json files
			json_files = filter(
				lambda jfile: os.path.isfile(os.path.join(self.jsons_path, jfile))
				and not jfile.endswith('.tmp'),
				os.listdir(self.jsons_path)
			)

			# for each json file, find the result of the test execution
			app.logger.info('counting test results in all the json files')
			for json_file in json_files:
				with open(os.path.join(self.jsons_path, json_file)) as file_mgr:
					json_data = json.load(file_mgr)
					for test, test_attr in json_data.iteritems():
						result = test_attr['result']
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

			# get data from the last tests
			execution_data.update(self.get_last_test())
			execution_data.update(self.get_last_tests())
			execution_data.update(self.get_execution_eta(tests_in_scope))

		elif status == 'finished':

			# since the test execution has finished there should be a global json
			# file with all the execution summary, this file should be located in
			# the directory of the first iteration
			if not os.path.isfile(self.final_json):
				app.logger.error('the status is finished but there is no results.json')
				return {}

			with open(self.final_json) as file_mgr:
				final_json = json.loads(file_mgr.read())
				for test in final_json['tests']:
					if final_json['tests'][test]['result'] == 'pass':
						pass_tests += 1
					if final_json['tests'][test]['result'] == 'fail':
						fail_tests += 1
					if final_json['tests'][test]['result'] == 'crash':
						crash_tests += 1
					if final_json['tests'][test]['result'] == 'skip':
						skip_tests += 1
					if final_json['tests'][test]['result'] == 'timeout':
						timeout_tests += 1
					if final_json['tests'][test]['result'] == 'incomplete':
						incomplete_tests += 1
					if final_json['tests'][test]['result'] == 'warn':
						warn_tests += 1
					if final_json['tests'][test]['result'] == 'dmesg-warn':
						dmesg_warn_tests += 1
					if final_json['tests'][test]['result'] == 'dmesg-fail':
						dmesg_fail_tests += 1
					if final_json['tests'][test]['result'] == 'notrun':
						not_run += 1

			# If the reports are enabled, collect the links
			if self.reportTRC and os.path.isfile(self.trc_url_file):
				with open(self.trc_url_file) as trc_file:
					trc_link = trc_file.readline().strip()
					app.logger.debug('trc link: {0}'.format(trc_link))

			if self.backupReport and os.path.isfile(self.breport_url_file):
				with open(self.breport_url_file) as breport_file:
					breport_link = breport_file.readline().strip()
					app.logger.debug('backup report link: {0}'.format(breport_link))

			# Getting the current year and work week, if the API is down and doesn't
			# respond just use N/A
			try:
				year, week = apiutils.get_workweek()
				ww = 'W{week}'.format(week=week)
			except RuntimeError:
				year = 'N/A'
				ww = 'N/A'

		# tests_executed includes all tests considered for execution
		# regardless of if they actually ran or not
		tests_executed = (
			pass_tests + fail_tests + crash_tests + skip_tests + timeout_tests +
			incomplete_tests + dmesg_warn_tests + warn_tests + dmesg_fail_tests +
			not_run
		)
		app.logger.debug('tests already executed: {0}'.format(tests_executed))

		# tests_run should not include tests considered not run:
		# skip_tests, incomplete_tests, not_run
		tests_run = (
			pass_tests + fail_tests + crash_tests + timeout_tests +
			dmesg_warn_tests + warn_tests + dmesg_fail_tests
		)
		app.logger.debug('tests ran: {0}'.format(tests_run))
		# Pass rate
		tests_considered_passed = pass_tests
		try:
			pass_rate_of_executed = round(
				tests_considered_passed / tests_run * 100, 2)
		except ZeroDivisionError:
			pass_rate_of_executed = 'N/A'
		app.logger.debug(
			'pass rate of executed: {0}'.format(pass_rate_of_executed))
		# not_skipped_tests are all the tests that were already run
		# excepting for those that status are not in skip, crash, timeout,
		# incomplete and not_run.
		not_skipped_tests = (
				pass_tests + fail_tests + dmesg_warn_tests + dmesg_fail_tests +
				warn_tests
		)
		app.logger.debug('tests not skipped: {0}'.format(not_skipped_tests))
		# Run rate
		if tests_run:
			run_rate = round(not_skipped_tests / tests_run * 100, 2)
		else:
			run_rate = 0
		app.logger.debug('run rate: {0}'.format(run_rate))
		execution_data.update(
			{
				'pass_tests': pass_tests,
				'fail_tests': fail_tests,
				'crash_tests': crash_tests,
				'skip_tests': skip_tests,
				'timeout_tests': timeout_tests,
				'incomplete_tests': incomplete_tests,
				'dmesg_warn_tests': dmesg_warn_tests,
				'warn_tests': warn_tests,
				'dmesg_fail_tests': dmesg_fail_tests,
				'not_run': not_run,
				'tests_executed': tests_executed,
				'run_rate': run_rate,
				'tests_run': tests_run,
				'pass_rate_of_executed': pass_rate_of_executed,
				'trc_link': trc_link,
				'breport_link': breport_link,
				'year': year,
				'ww': ww,
			}
		)

		return execution_data

	def format_data(self, raw_data):
		"""Organizes the data in a standardized format.

		The data that is sent back to the watchdog monitor needs to be in a
		standard format regardless of what info is available at any given time,
		this ensure the watchdog monitor handles the data properly every time.
		:param raw_data: a dictionary with the data that is to be formatted
		:return: an formatted dictionary containing all the execution data
		"""

		app.logger.info('formatting the data')
		formatted_data = {}

		# template dictionary that should be used to send data consistently
		execution_data = {
			'detailed_information': {
				'distro': raw_data.get('distro', 'N/A')
			},
			'networking-service': raw_data.get('net_boot_time', 'N/A'),
			'attachedDisplays': {
				display: 'active' for display in raw_data.get('displays', [])
			},
			'currentExecution': {
				'status': raw_data.get('status', 'unknown')
			},
			'overall_tests_statistics': {
				'total_tests': raw_data.get('total_tests', 'N/A'),
				'test_to_run': raw_data.get('tests_in_scope', 'N/A'),
				'test_to_not_run': raw_data.get('tests_out_of_scope', 'N/A'),
				'current_progress': (
					'{executed}/{to_run} ({progress}%)'
					.format(
						executed=raw_data.get('tests_executed', 'N/A'),
						to_run=raw_data.get('tests_in_scope', 'N/A'),
						progress=raw_data.get('current_progress', 'N/A')
					)
				),
				'overall_pass_rate': raw_data.get('tests_run', 'N/A'),
				'pass_rate_of_executed': raw_data.get('pass_rate_of_executed', 'N/A'),
				'pass_tests': raw_data.get('pass_tests', 'N/A'),
				'fail_tests': raw_data.get('fail_tests', 'N/A'),
				'crash_tests': raw_data.get('crash_tests', 'N/A'),
				'skip_tests': raw_data.get('skip_tests', 'N/A'),
				'timeout_tests': raw_data.get('timeout_tests', 'N/A'),
				'incomplete_tests': raw_data.get('incomplete_tests', 'N/A'),
				'dmesg_warn_tests': raw_data.get('dmesg_warn_tests', 'N/A'),
				'warn_tests': raw_data.get('warn_tests', 'N/A'),
				'dmesg_fail_tests': raw_data.get('dmesg_fail_tests', 'N/A'),
				'not_run': raw_data.get('not_run', 'N/A'),
				'current_iteration_folder': (
					os.path.basename(self.current_iteration)
					if self.current_iteration else 'N/A'
				),
				'OverallTime': raw_data.get('overall_time', 'N/A')
			},
			'last_json': {
				'number': raw_data.get('number', 'N/A'),
				'test_name': raw_data.get('test_name', 'N/A'),
				'status': raw_data.get('status', 'N/A'),
				'time_elapsed': raw_data.get('time_elapsed', 'N/A'),
				'minutes': raw_data.get('minutes', 'N/A'),
				'json_ctime': raw_data.get('json_ctime', 'N/A')
			},
			'dut_uptime': {
				'uptime': raw_data.get('uptime_minutes', 'N/A')
			},
			'dut_eta': {
				'time': raw_data.get('eta', ' ')
			},
			'last_five_results': raw_data.get('last_tests', {}),
			'trc_link': {
				'url': raw_data.get('trc_link', 'N/A')
			},
			'backup_link': {
				'url': raw_data.get('breport_link', 'N/A')
			},
			'date': {
				'workweek': raw_data.get('ww', 'N/A'),
				'year': raw_data.get('year', 'N/A')
			},
			'i915_module': raw_data.get('i915_module', 'N/A'),
			'dut_time': raw_data.get('dut_time', 'N/A'),
			'piglit_running': raw_data.get('piglit_running', 'N/A'),
			'piglit_uptime': raw_data.get('piglit_uptime', '0')
		}

		# add to the final dictionary all the data gotten from the config file
		# plus the data from the execution
		formatted_data.update(self.data)
		formatted_data.update(execution_data)
		app.logger.debug(json.dumps(formatted_data, sort_keys=True, indent=4))

		return formatted_data

	def delete_html(self):
		"""Deletes the html directory inside the current iteration."""

		app.logger.info('deleting the html directory')
		# When the html is wrongfully created it most of the times ends up being
		# owned by root, so to delete it we need sudo privileges
		os.system('sudo rm -rf {0}'.format(self.iteration_html))
		app.logger.info('html directory deleted')

	def get_statistics(self):
		"""Collects platform and test execution data.

		This is the main function of the dut_watcher module. It's main purpose is
		to collect platform based data that is independent from the test execution
		and also gather statistics from the current execution.
		:return: An HTTP response that contains a dictionary with all the data
		from the platform and test execution. Even in the case when for some reason
		there is no data available, it still returns a dictionary with all the keys
		but empty values.
		"""

		raw_data = {}

		# Get platform data (status-independent data)
		# -------------------------------------------
		app.logger.info('collecting the platform data (status independent)')

		# Get the DUT's time, this can be useful to troubleshoot issues in the
		# watchdog side
		raw_data['dut_time'] = str(datetime.datetime.now())

		# Platform distribution
		sys_info = platform.platform()
		distro = sys_info.split('with-')[1] if 'with-' in sys_info else sys_info
		raw_data['distro'] = distro
		app.logger.debug('distro: {0}'.format(distro))

		# Platform uptime
		uptime_minutes = bash.get_output("awk '{print $0/60;}' /proc/uptime")
		raw_data['uptime_minutes'] = uptime_minutes
		app.logger.debug('platform uptime: {0}'.format(uptime_minutes))

		# Getting the networking boot time
		net_boot_time = bash.get_output(
			"systemd-analyze blame | grep networking.service").split()
		net_boot_time = net_boot_time[0] if len(net_boot_time) > 0 else 'N/A'
		raw_data['net_boot_time'] = net_boot_time
		app.logger.debug('networking boot time: {0}'.format(net_boot_time))

		# Getting the displays attached to the platform
		displays = bash.get_output(
			"sudo cat /sys/kernel/debug/dri/0/i915_display_info 2> /dev/null | "
			"grep \"^connector\" | grep -we \"connected\" | awk -F \"type \" "
			"'{{print $2}}' | awk '{{print $1}}' | sed 's/,//g'"
		).split()
		raw_data['displays'] = displays
		app.logger.debug('displays: {0}'.format(displays))

		# Getting information related i915 intel driver
		# how this works
		# =====================================================================
		# when i915 module is loaded, usually the variable "check_i915_module"
		# will contains a value > 0 and this mean that X modules is using this
		# module (which mean that the driver is loaded), otherwise if the value
		# is 0 this mean that there is not modules using i915 module
		# (which mean that the driver is unloaded).
		check_i915_module = int(bash.get_output('lsmod | grep ^i915').split()[2])
		i915_module = True if check_i915_module else False
		raw_data['i915_module'] = i915_module

		# Get test data (status-independent data)
		# ---------------------------------------
		# Getting a list of all the tests
		test_list_file = os.path.join(self.tests_path, 'test-list.txt')
		test_list = bash.get_output(
			"cat {testlist} | sed -e '/TESTLIST/d'".format(testlist=test_list_file)
		).split()

		# Get a list of tests with their sub-tests and store them as test@subtest,
		# if there are no sub-tests for the test, then just store test in the list
		overall_test_list = []
		for test in test_list:
			sub_tests = bash.get_output(
				"{tests_path}/{test} --list-subtests"
				.format(tests_path=self.tests_path, test=test)
			).split()
			if sub_tests:
				for sub_test in sub_tests:
					overall_test_list.append(test + '@' + sub_test)
			else:
				overall_test_list.append(test)

		# Get the total number of tests + sub-tests
		total_tests = len(overall_test_list)
		raw_data['total_tests'] = total_tests
		app.logger.debug('tests: {0}'.format(total_tests))

		# Total number of tests to run
		testlist = os.path.join(self.tests_path, 'intel-ci', self.current_testlist)
		with open(testlist) as file_mgr:
			tests_in_scope = sum(1 for _ in file_mgr)
		raw_data['tests_in_scope'] = tests_in_scope
		app.logger.debug('tests in scope: {0}'.format(tests_in_scope))

		# out of scope tests
		tests_out_of_scope = total_tests - tests_in_scope
		raw_data['tests_out_of_scope'] = tests_out_of_scope
		app.logger.debug('tests out of scope: {0}'.format(tests_out_of_scope))

		# Get the overall time taken so far
		overall_time = self.get_overall_time()
		raw_data['overall_time'] = overall_time
		app.logger.info('overall time: {0}'.format(overall_time))

		# Get test execution data (status-dependent data)
		# -----------------------------------------------
		app.logger.info('collecting the test execution data (status dependent)')

		# get information about Piglit
		raw_data['piglit_running'] = bash.is_process_running('piglit')
		piglit_uptime = '0'
		if raw_data['piglit_running']:
			err_code, piglit_process = bash.run_command("pgrep -of piglit")
			if not err_code:
				piglit_uptime = bash.run_command(
					'ps -o etimes= -p {0}'.format(piglit_process))[1]
		raw_data['piglit_uptime'] = piglit_uptime

		execution_data = self.get_execution_status(tests_in_scope)
		raw_data.update(execution_data)

		# If there is execution data calculate the current execution progress
		if execution_data.get('tests_executed', False):
			current_progress = (
				round(int(execution_data['tests_executed']) / tests_in_scope * 100, 2)
			)
			raw_data['current_progress'] = current_progress
			app.logger.info('execution progress: {0}%'.format(current_progress))

		# Format the data in a standardized response
		# ------------------------------------------
		formatted_data = self.format_data(raw_data)

		# print and return the formatted data
		print(json.dumps(formatted_data, sort_keys=True))
		return json.dumps(formatted_data, sort_keys=True)


def parse_arguments():
	"""Parses arguments from command line."""

	parser = argparse.ArgumentParser(
		description=bash.CYAN + 'Intel® Graphics for Linux*' + bash.END,
		epilog=bash.CYAN + 'https://01.org/linuxgraphics' + bash.END)
	group = parser.add_mutually_exclusive_group()
	group.add_argument(
		'-s',
		'--statistics',
		dest='get_statistics',
		action='store_true',
		help='shows dut statistics from current igt execution')
	group.add_argument(
		'-f',
		'--firmwares',
		dest='get_firmwares',
		action='store_true',
		help='shows firmwares loaded in the kernel')
	group.add_argument(
		'-w',
		'--webserver',
		dest='web_server',
		action='store_true',
		help='starts the DUT watcher web server')
	group.add_argument(
		'-v',
		'--version',
		dest='version',
		action='version',
		version='%(prog)s 1.0')
	args = parser.parse_args()

	if args.web_server:
		app.run(host='0.0.0.0', port=4040)

	if args.get_statistics:
		DutWatcher().get_statistics()

	if args.get_firmwares:
		get_firmware_version()


if __name__ == '__main__':

	# Initialize the logger

	# create the console handler
	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.INFO)

	# Create the file handlers
	log_path = '{0}/logs'.format(os.path.dirname(os.path.abspath(__file__)))
	if not os.path.exists(log_path):
		os.makedirs(log_path)
	log_file = '{path}/dut_watcher.log'.format(path=log_path)
	file_handler = logging.handlers.RotatingFileHandler(
		log_file,
		maxBytes=10485760,  # Max file size 10 MB (10 x 1024 x 1024)
		backupCount=10  # Number of rotating files
	)
	file_handler.setLevel(logging.DEBUG)
	error_log_file = '{path}/dut_watcher.error.log'.format(path=log_path)
	error_file_handler = logging.handlers.RotatingFileHandler(
		error_log_file,
		maxBytes=10485760,  # Max file size 10 MB (10 x 1024 x 1024)
		backupCount=10  # Number of rotating files
	)
	error_file_handler.setLevel(logging.ERROR)

	# create a formatter
	formatter = logging.Formatter(
		'%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	# add the formatter to handlers
	console_handler.setFormatter(formatter)
	file_handler.setFormatter(formatter)
	error_file_handler.setFormatter(formatter)

	app.logger.setLevel(logging.DEBUG)
	app.logger.addHandler(console_handler)
	app.logger.addHandler(file_handler)
	app.logger.addHandler(error_file_handler)

	parse_arguments()
