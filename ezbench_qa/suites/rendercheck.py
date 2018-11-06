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
import platform
import sys

from common import apiutils
from gfx_qa_tools.common import bash
from gfx_qa_tools.common import log
from gfx_qa_tools.common import utils

import yaml


class ExecutionManager(object):

	def __init__(self):
		self.config_file = '/home/custom/config.yml'

		if not os.path.isfile(self.config_file):
			bash.message('err', '{0}: does not exists'.format(self.config_file))
			sys.exit(1)

		self.data = yaml.load(open('/home/custom/config.yml'))
		self.dut_user = self.data['dut_conf']['dut_user']
		self.dut_hostname = self.data['dut_conf']['dut_hostname']
		self.dut_static_ip = self.data['dut_conf']['dut_static_ip']
		self.raspberry_number = self.data['raspberry_conf']['raspberry_number']
		self.raspberry_power_switch = self.data['raspberry_conf'][
			'raspberry_power_switch']
		self.log_folder_path = os.path.join(
			'/home', self.dut_user, 'rendercheck_logs')

		self.control_file = os.path.join(self.log_folder_path, 'control')

		if os.path.isfile(self.control_file):
			bash.message('info', 'rendercheck has finished')
			bash.message('info', 'nothing to do')
			sys.exit(0)

		# initialize the logger
		os.system('mkdir -p {0}'.format(self.log_folder_path))

		self.log_file = os.path.join(self.log_folder_path, 'rendercheck.log')

		if os.path.isfile(self.log_file):
			os.remove(self.log_file)

		self.log = log.setup_logging(
			name='launcher', level='debug',
			log_file='{0}'.format(self.log_file)
		)

		self.log.info(
			'initialize the logger for ({0}) rendercheck'.format(
				self.log_file))

	def unlock_system(self):
		"""Unlock the system when rendercheck execution is finished"""

		self.log.info('unlocking the system')
		apiutils.unlock_lock_system_in_watchdog_db(
			self.raspberry_number,
			self.raspberry_power_switch,
			'free'
		)

	def send_email(
		self, trc_link, pass_test, fail_test, total_test, pass_rate_of_executed,
		elapsed_time):
		"""Send a email to notify that the execution is finished

		:param trc_link: which is the trc link report.
		:param pass_test: which is passed tests.
		:param fail_test: which is the failed tests.
		:param total_test: which is the total test run.
		:param pass_rate_of_executed: which is the pass rate of the executed.
		:param elapsed_time: which is the elapsed time of the execution.
		"""

		self.log.info('sending the email')
		# platform distribution
		sys_info = platform.platform()
		distro = sys_info.split('with-')[1] if 'with-' in sys_info else sys_info
		# Getting the displays attached to the DUT
		displays_attached = \
			bash.get_output(
				"sudo cat /sys/kernel/debug/dri/0/i915_display_info "
				"| grep \"^connector\" | grep "
				"-we \"connected\" | awk -F\"type \" '{print $2}' | "
				"awk '{print $1}' | sed 's/,//g'").decode('utf-8').split()
		displays_attached = ' & '.join(displays_attached)

		body = '''
rendercheck execution has finished, please see the overall statistics

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
Passed: {tests_pass}
Failed: {tests_fail}
Pass rate: {pass_rate}%
{overall_time}
Attached displays: {displays}

TRC link: {trc_link}
			'''.format(
			user=self.dut_user,
			pwd=self.data['dut_conf']['dut_password'],
			host_ip=self.data['dut_conf']['dut_static_ip'],
			host=self.dut_hostname,
			grub=self.data['dut_conf']['grub_parameters'],
			guc=self.data['firmwares']['guc'],
			huc=self.data['firmwares']['huc'],
			dmc=self.data['firmwares']['dmc'],
			raspberry_ip=self.data['raspberry_conf']['raspberry_ip'],
			raspberry_number=self.raspberry_number,
			switch_number=self.raspberry_power_switch,
			usb_cutter=self.data['raspberry_conf']['usb_cutter_serial'],
			package=self.data['suite_conf']['default_package'],
			stack_code=self.data['suite_conf']['gfx_stack_code'],
			kernel_branch=self.data['suite_conf']['kernel_branch'],
			kernel_commit=self.data['suite_conf']['kernel_commit'],
			iterations=self.data['suite_conf']['igt_iterations'],
			image=self.data['usb_conf']['default_image'],
			distro=distro,
			total_tests=total_test,
			tests_pass=pass_test,
			tests_fail=fail_test,
			pass_rate=pass_rate_of_executed,
			overall_time=elapsed_time,
			displays=displays_attached,
			trc_link=trc_link,
		)

		utils.emailer(
			'ezbench-rendercheck@noreply.com',
			self.data['suite_conf']['default_mailing_list'],
			'rendercheck execution finished on ({hostname})'.format(
				hostname=self.dut_hostname),
			body
		)

	def update_watchdog(self, ezbench_csv_file_path, elapsed_time):
		"""Update watchdog web page

		:param ezbench_csv_file_path, is the ezbench csv results path
		:param elapsed_time, is the elapsed time.

		:return
		- trc_link: which is the trc link report.
		- pass_test: which is passed tests.
		- fail_test: which is the failed tests.
		- total_test: which is the total test run.
		- pass_rate_of_executed: which is the pass rate of the executed.
		"""

		trc_link = bash.get_output('cat {report}'.format(
			report=os.path.join('/home', self.dut_user, 'trc2.log'))).decode('utf-8')
		pass_test = int(bash.get_output('cat {0} | grep pass | wc -l'.format(
			ezbench_csv_file_path)).decode('utf-8'))
		fail_test = int(bash.get_output('cat {0} | grep fail | wc -l'.format(
			ezbench_csv_file_path)).decode('utf-8'))
		total_test = int(bash.get_output('cat {0} | wc -l'.format(
			ezbench_csv_file_path)).decode('utf-8'))
		# calculating the pass rate
		try:
			pass_rate_of_executed = round(
				pass_test / total_test * 100, 2)
		except ZeroDivisionError:
			pass_rate_of_executed = 'N/A'

		apiutils.update_watchdog_db(
			RaspberryNumber=self.raspberry_number,
			PowerSwitchNumber=self.raspberry_power_switch,
			Status='finished - {0} '.format(elapsed_time),
			Pass=pass_test,
			Fail=fail_test,
			PassRate='{0}%'.format(pass_rate_of_executed),
			OverallTime=elapsed_time,
			TRCLink=trc_link
		)

		return trc_link, pass_test, fail_test, total_test, pass_rate_of_executed

	def report_to_trc(self, ezbench_path, ezbench_folder_results):
		"""Report to Test Report Center

		This function generate a report from ezbench results and then report the
		csv generated to TRC.

		:param ezbench_path, is the ezbench path
		:param ezbench_folder_results, is te ezbench folder results

		:return
			- ezbench_csv_file_path, which is the absolute path for the ezbench
			csv results.
		"""

		# generating the report with the results from ezbench
		this_path = os.path.dirname(os.path.abspath(__file__))
		ezbench_input_folder = os.path.join(
			ezbench_path, 'logs', ezbench_folder_results)
		ezbench_output_folder = os.path.join(self.log_folder_path, 'results')
		self.log.info('generating the report with the results from ezbench')
		output = os.system(
			'python {script} -s rendercheck -f {input_folder} '
			'-o {output_folder} 2>> {log}'.format(
				script=os.path.join(os.path.dirname(this_path), 'ezbench_reports.py'),
				input_folder=ezbench_input_folder,
				output_folder=ezbench_output_folder,
				log=self.log_file))

		if output:
			self.log.error('an error occurred generating the report')
			self.log.info('closing the log')
			sys.exit(1)

		# uploading the results to TestReportCenter
		self.log.info('uploading the results to TestReportCenter')
		autouploader_script = os.path.join(
			os.path.dirname(os.path.dirname(this_path)), 'igt', 'autouploader',
			'autoUploader.py')
		ezbench_csv_file = bash.get_output(
			'ls {0} | egrep "*.csv"'.format(
				os.path.join(ezbench_output_folder, 'round_0'))).decode('utf-8')
		ezbench_csv_file_path = os.path.join(
			ezbench_output_folder, 'round_0', ezbench_csv_file)
		environment = 'sandbox' if self.data['autouploader'][
			'currentEnv'] == 'sand' else 'production'

		is_sna_enabled = bash.get_output(
			'cat /opt/X11R7/var/log/Xorg.0.log | grep -i sna').decode('utf-8')
		current_driver = 'sna' if is_sna_enabled else 'modesetting'
		self.log.info('current driver is: {0}'.format(current_driver))

		autouploader_cmd = 'python2 {script} -p {platform} -s {suite} ' \
			'-r {release} -t {title} -f {file} -e {environment} -o {objective} ' \
			'-g {goal} -a {attachments} -c {comment}'.format(
				script=autouploader_script,
				platform=self.data['autouploader']['currentPlatform'],
				suite=self.data['autouploader']['currentSuite'],
				release=self.data['autouploader']['currentRelease'],
				title=self.data['autouploader']['currentTittle'],
				file=ezbench_csv_file_path,
				environment=environment,
				objective='installer',
				goal='graphic-stack',
				attachments=os.path.join(ezbench_output_folder, 'round_0', 'families'),
				comment=current_driver)

		self.log.info('autoUploader cmd')
		self.log.info(autouploader_cmd)

		output = os.system('{cmd} 2>> {log}'.format(
			cmd=autouploader_cmd, log=self.log_file))

		if output:
			self.log.error('an error occurred uploading the report')
			self.log.info('closing the log')
			sys.exit(1)

		return ezbench_csv_file_path

	def run_rendercheck(self):
		"""Run rendercheck test suite in the current system.

		The aim of this function is to run automatically rendercheck with
		ezbench tool.
		"""
		ezbench_path = os.path.join('/home', self.dut_user, 'ezbench')
		ezbench_script = os.path.join(ezbench_path, 'ezbench')
		ezbench_campaigns = self.data['suite_conf']['igt_iterations']
		ezbench_folder_results = 'sbench_rendercheck'
		ezbench_folder_results_full_path = os.path.join(
			ezbench_path, 'logs', ezbench_folder_results)
		ezbench_wait_for_results = 20
		ezbench_cmd_setup_environment = '{script} -c HEAD -r {campaigns} ' \
			'-b x11:rendercheck -p x11-gl {results}'.format(
				script=ezbench_script, campaigns=ezbench_campaigns,
				results=ezbench_folder_results)
		ezbench_cmd_run_tests = '{script} sbench_rendercheck start'.format(
			script=ezbench_script)

		self.log.info('setting the environment for rendercheck')
		output = os.system('{cmd} 2>> {log}'.format(
			cmd=ezbench_cmd_setup_environment, log=self.log_file))

		if output:
			self.log.error('the environment could not be set')
			self.log.info('closing the log')
			sys.exit(1)

		# wait for runner.sh finished in order to apply the second command
		# for run rendercheck, since the second command check if runner.sh is
		# running
		self.log.info('waiting for (runner.sh) to finish')

		while bash.is_process_running('runner.sh'):
			continue

		self.log.info('runner.sh: is not running')

		self.log.info('the environment has been set successfully')
		utils.timer('start')
		self.log.info('running rendercheck')
		output = os.system('{cmd} 2>> {log}'.format(
			cmd=ezbench_cmd_run_tests, log=self.log_file))

		if output:
			self.log.error('an error occurred while running rendercheck')
			self.log.info('closing the log')
			sys.exit(1)

		# check if ezbench generated the folder for results files
		if utils.isdir(ezbench_folder_results_full_path):
			# check if ezbench generate the results files
			if utils.wait_for_file_existence(
				ezbench_folder_results_full_path, '\#', ezbench_wait_for_results):
				self.log.info('rendercheck ran successfully')
				elapsed_time = utils.timer('stop', print_elapsed_time=False)
				self.log.info(elapsed_time)

				# reporting to TestReportCenter
				ezbench_csv_file_path = self.report_to_trc(
					ezbench_path, ezbench_folder_results)
				# updating the watchdog
				trc_link, pass_test, fail_test, total_test, \
				pass_rate_of_executed = self.update_watchdog(
					ezbench_csv_file_path, elapsed_time)
				# sending a email notification
				self.send_email(
					trc_link, pass_test, fail_test, total_test, pass_rate_of_executed,
					elapsed_time)
				# unlock the system
				self.unlock_system()

				# creating a control file in order to not run again this script
				self.log.info('creating a control file')
				with open(self.control_file, 'w') as ctl_file:
					ctl_file.write('rendercheck has finished')

			else:
				self.log.error('ezbench did not generate the results files in {0} seconds'.format(
					ezbench_wait_for_results))
				sys.exit(1)
		else:
			self.log.error('ezbench did not generate the folder for results files'.format(
				ezbench_folder_results_full_path))
			sys.exit(1)


if __name__ == '__main__':
	ExecutionManager().run_rendercheck()
