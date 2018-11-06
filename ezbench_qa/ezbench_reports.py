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
import csv
import json
import os
import sys

from argparse import RawDescriptionHelpFormatter
from gfx_qa_tools.common import bash


def write_csv(suite, family, test_name, test_result, csv_output, round_folder):
	"""Generate a CSV with TRC format

	:param suite: the current suite tested with ezbench
	:param family: the current family tested with ezbench
	:param test_name: the current test name tested with ezbench
	:param test_result: the result of the test
	:param csv_output: the path where the csv will be written
	:param round_folder: the current iteration performed by ezbench
	"""
	if not os.path.isfile(os.path.join(round_folder, csv_output)):
		bash.message('info', 'creating ({0}) csv file'.format(csv_output))
		with open(os.path.join(round_folder, csv_output), 'w') as csv_file:
			csv_writer = csv.writer(csv_file)
			# writing the headers to a new csv file
			csv_writer.writerow(['COMPONENT', 'NAME', 'STATUS', 'BUG', 'COMMENT'])
			# writing a new line to a new csv file
			csv_writer.writerow(
				[
					'{0}'.format(suite),
					'({0}) {1}'.format(family, test_name),
					'{0}'.format(test_result),
					'',
					''
				])
	else:
		with open(os.path.join(round_folder, csv_output), 'a') as csv_file:
			csv_writer = csv.writer(csv_file)
			# appending a new line to an existing csv file.
			csv_writer.writerow(
				[
					'{0}'.format(suite),
					'({0}) {1}'.format(family, test_name),
					'{0}'.format(test_result),
					'',
					''
				])


class Rendercheck(object):

	def __init__(self):
		self.suite = 'rendercheck'
		self.easy_bugs = '/home/custom/graphic_stack/packages/easy-bugs'

		if os.path.isfile(self.easy_bugs):
			self.xserver_tag = bash.get_output(
				'cat {0} | grep xserver -A 2 | grep tag | '
				'sed \'s/    tag: //g\''
				.format(self.easy_bugs)).decode('utf-8')
			self.xserver_commit = bash.get_output(
				'cat {0} | grep xserver -A 2 | grep commit | '
				'sed \'s/    commit: //g\''
				.format(self.easy_bugs)).decode('utf-8')
			if not self.xserver_tag or not self.xserver_commit:
				bash.message(
					'err',
					'xserver not found in this system on the following '
					'file ({0})'.format(self.easy_bugs))
				sys.exit(1)
		else:
			bash.message('err', '({0}) does not exist'.format(self.easy_bugs))
			bash.message('info', 'is the DUT in the automated system ?')
			sys.exit(1)

		'''this dict indicates the relation between family and subtest
		currently of rendercheck (from martin peres repository)
		so far does not rendercheck does not shows the following families :
		(shmblend/libreoffice_xrgb/gtk_argb_xbgr)'''
		self.rendercheck_test_dict = {
			'fill': 'fill',
			'dcoords': 'dst coords',
			'scoords': 'src coords',
			'mcoords': 'mask coords',
			'tscoords': 'transform src',
			'tmcoords': 'transform mask',
			'blend': 'blend',
			'repeat': 'repeat',
			'triangles': ['Triangles', 'TriStrip', 'TriFan'],
			'bug7366': 'bug7366',
			'cacomposite': 'composite CA',
			'composite': 'composite',
			'gradients': 'gradient'
		}

	def reports(self, args):
		"""Convert reports from ezbench to TRC format

		:param args: this param contains the following variables:
		- the folder which contains ezbench reports
		- the current switch which is rendercheck
		- the output folder where the results will be stored
		"""

		ezbench_reports = bash.get_output(
			'ls {0} | grep stderr'
			.format(args.folder)).decode('utf-8').split()

		count = 0

		for report in ezbench_reports:
			round_folder = os.path.join(
				args.output, 'round_{0}'.format(count))
			if not os.path.exists(round_folder):
				os.makedirs(round_folder)
			csv_output_a = '{0}_{1}_n_{2}.csv'.format(
				self.xserver_commit, self.xserver_tag, count)

			with open(os.path.join(args.folder, report), 'r') as item_a:
				report_data = item_a.readlines()

			for line in report_data:
				test_result = line.split()[-1]
				for key, value in self.rendercheck_test_dict.items():
					csv_output_b = '{0}_{1}_{2}_n_{3}.csv'.format(
						key, self.xserver_commit, self.xserver_tag, count)
					# creating folder by family
					round_folder_by_family = os.path.join(
						round_folder, 'families')
					if not os.path.exists(round_folder_by_family):
						os.makedirs(round_folder_by_family)

					if key == 'triangles':
						for item in value:
							if line.startswith('##') and item in line:
								test_name = line \
									.replace('## ', '') \
									.replace(': {0}\n'.format(test_result), '')
								# writing the main csv
								write_csv(
									self.suite, key, test_name, test_result,
									csv_output_a, round_folder)
								# writing the csv by family
								write_csv(
									self.suite, key, test_name, test_result,
									csv_output_b, round_folder_by_family)
					else:
						if line.startswith('##') and value in line:
							test_name = line \
								.replace('## ', '') \
								.replace('{0} '.format(value), '') \
								.replace(': {0}\n'.format(test_result), '')
							if key == 'composite' and 'CA' in line:
								pass
							else:
								# writing the main csv
								write_csv(
									self.suite, key, test_name, test_result,
									csv_output_a, round_folder)
								# writing the csv by family
								write_csv(
									self.suite, key, test_name, test_result,
									csv_output_b, round_folder_by_family)
			count += 1

		bash.message(
			'info',
			'the results are available in the following path ({0})'
			.format(args.output))


def igt_reports(args):
	"""Convert reports from ezbench to TRC format

	:param args: this param contains the following variables:
	- the folder which contains ezbench reports
	- the current switch which is rendercheck
	- the output folder where the results will be stored
	"""

	# smartezbench.state, is the json file that contains the commits,
	# tests, rounds that ezbench ran

	smartezbench_file = os.path.join(args.folder, 'smartezbench.state')

	if not os.path.isfile(smartezbench_file):
		bash.message(
			'err', 'file ({0}) does not exist into ({1})'
			.format(os.path.basename(smartezbench_file), args.folder))
		sys.exit(1)

	with open(smartezbench_file, 'r') as item_a:
		data = item_a.read()

	smartezbench_dict = json.loads(data)
	# iterating over each commit/value that could has the file
	# smartezbench.state
	for commit_id, tests in \
		smartezbench_dict['tasks']['user']['commits'].items():
		ezbench_commit = commit_id
		# iterating over each value of the current commit has
		for ezbench_tests in tests.values():
			ezbench_test_name = [*ezbench_tests.keys()][0]
			for rounds in ezbench_tests.values():
				ezbench_rounds = [*rounds.values()][0]

		ezbench_log_name = '{0}_unit_{1}'.format(
			ezbench_commit, ezbench_test_name)

		for ez_round in range(ezbench_rounds):
			current_log_name = '{0}#{1}'.format(ezbench_log_name, ez_round)
			current_log_path = os.path.join(args.folder, current_log_name)
			output_name = '{0}_round_{1}.csv'.format(
				ezbench_commit, ez_round)

			if not os.path.exists(os.path.join(
				args.output, ezbench_commit)):
				os.makedirs(os.path.join(args.output, ezbench_commit))

			if os.path.isfile(
				os.path.join(args.output, ezbench_commit, output_name)):
				bash.message(
					'skip', '({0}) already exist'.format(output_name))
				continue
			else:
				ezbench_commit_folder = os.path.join(
					args.output, ezbench_commit)
				if not os.path.exists(ezbench_commit_folder):
					bash.message(
						'info',
						'creating ({0}) ezbench commit folder'
						.format(ezbench_commit_folder), '')
					bash.return_command_status(
						'mkdir -p {0}'.format(ezbench_commit_folder))

				bash.message(
					'info', 'creating ({0}) csv file'.format(output_name))

				with open(current_log_path, 'r') as item_b:
					data = item_b.readlines()

				with open(os.path.join(
					args.output, ezbench_commit, output_name), 'w') as csv_file:
					csv_writer = csv.writer(csv_file)
					# writing the headers to a new csv file
					csv_writer.writerow(
						['COMPONENT', 'NAME', 'STATUS', 'BUG', 'COMMENT'])

					whitelist = ['pass', 'incomplete']
					fail_list = ['dmesg-fail', 'fail', 'crash', 'dmesg-warn', 'warn']
					not_run_list = ['skip', 'timeout', 'incomplete', 'notrun']

					for line in data:
						if line.startswith('igt'):
							igt_test_case = line.split(': ')[0]
							igt_test_case_result = \
								line.split(': ')[1].strip()

							if igt_test_case_result in whitelist:
								status = 'pass'
							elif igt_test_case_result in fail_list:
								status = 'fail'
							elif igt_test_case_result in not_run_list:
								status = 'not run'

							# using a ternary operator
							csv_writer.writerow(
								[
									'igt',
									'igt@{0}'.format(igt_test_case),
									'{0}'.format(status),
									'',
									('' if igt_test_case_result == 'pass'
										else 'this test was {0}'
										.format(igt_test_case_result))
								]
							)
	bash.message(
		'info',
		'the results are available in the following path ({0})'
		.format(args.output))


def validate_arguments(args):
	"""validate the arguments from the function arguments

	:param args: this param contains the following variables:
	- the folder which contains ezbench reports
	- the current switch which is rendercheck
	- the output folder where the results will be stored

	This function is dedicated for the following purposes:
	- to validate if the input folder exist (args.folder)
	- to validate if the output folder exist (args.output)
	"""
	# validating if input folder exist
	if not os.path.exists(args.folder):
		bash.message(
			'err', 'input folder ({0}) does not exist'.format(args.folder))
		sys.exit(1)

	# validating if output folder exist
	if not os.path.exists(args.output):
		bash.message(
			'info',
			'output folder ({0}) does not exist, creating'
			.format(args.output), '')
		bash.return_command_status('mkdir -p {0}'.format(args.output))

	if args.suite == 'igt':
		igt_reports(args)
	else:
		Rendercheck().reports(args)


def arguments():
	"""Provides a set of arguments

	Defined arguments must be specified in this function in order to interact
	with the others class and functions in this script
	"""
	this_path = os.path.dirname(os.path.abspath(__file__))
	default_folder = os.path.join(this_path, 'results')

	parser = argparse.ArgumentParser(
		formatter_class=RawDescriptionHelpFormatter,
		description='''
	program description:
	(%(prog)s) This is a tool for converting ezbench reports to csv.
	Python minimum required version : >= 3.5
	project : https://01.org/linuxgraphics
	maintainer : humberto.i.perez.rodriguez@intel.com''',
		epilog='Intel® Graphics for Linux* | 01.org',
		usage='%(prog)s [options]')
	parser.add_argument(
		'--version', action='version', version='%(prog)s 1.0')
	parser.add_argument(
		'-o', '--output',
		dest='output',
		default=default_folder,
		help='the output folder for the reports, default folder is ({0})'
		.format(default_folder))
	group_csv = parser.add_argument_group(
		'Get reports ({0}mandatory arguments{1})'
		.format(bash.BLUE, bash.END),
		'this function is dedicated to converting files comes '
		'from ezbench to csv')
	group_csv.add_argument(
		'-f', '--folder',
		dest='folder',
		required=True,
		help='the folder which contains ezbench reports')
	group_csv.add_argument(
		'-s', '--suite',
		dest='suite',
		choices=['rendercheck', 'igt'],
		required=True,
		help='the current ezbench suite')

	args = parser.parse_args()
	validate_arguments(args)


if __name__ == '__main__':
	arguments()
