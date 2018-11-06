#!/usr/bin/env python
"""There is the need to create some periodic reports based on information from
the last two executions of IGT All in a platform. A lot of data needs to be
extracted and analyzed to create this report. This module provides tools to
accomplish this in an automated manner."""

from __future__ import print_function

import argparse
import csv
import datetime
import os
import sys

from tabulate import tabulate
import urllib3

import common.tools.bugz as bugz
import common.tools.reports as reptools

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ReportGenerator(object):
	"""Collects data from the latest test reports and prints relevant data."""

	def __init__(self, args):

		self.args = args
		self.regressions = None
		self.progressions = None

		print(
			'Searching for the {msg} reports for platform {platform}.'
			.format(
				msg='specified' if args.report_ids else 'latest',
				platform=args.platform)
		)
		print('Please wait, it can take up to a few minutes.')

		# select the appropriate library depending on user parameters
		if args.linuxgraphics:

			self.report_server = reptools.LinuxGraphicsServer(
				args.platform, args.igt_suite, args.password, args.rsa_key)
			key = lambda x: int(x[7:])
			server = 'linuxgraphics'

		else:

			self.report_server = reptools.TRCServer(args.platform, args.igt_suite)
			key = None
			server = 'trc'

		if args.report_ids:

			# Get the specified report IDs
			reports = sorted(args.report_ids, key=key, reverse=True)

			self.latest_report = reptools.Report(
				reports[0], args.platform, args.igt_suite, server,
				args.password, args.rsa_key)
			if self.latest_report.qa_id is None:
				sys.exit('Report with ID {0} could not be found'.format(reports[0]))

			self.previous_report = reptools.Report(
				reports[1], args.platform, args.igt_suite, server,
				args.password, args.rsa_key)
			if self.previous_report.qa_id is None:
				sys.exit('Report with ID {0} could not be found'.format(reports[1]))

		else:

			# if the user didn't specify reports, get the latest reports
			reports = self.report_server.get_latest_reports()

			self.latest_report = reptools.Report(
				reports[0]['qa_id'], args.platform, args.igt_suite, server,
				args.password, args.rsa_key)

			self.previous_report = reptools.Report(
				reports[1]['qa_id'], args.platform, args.igt_suite, server,
				args.password, args.rsa_key)

		# initialize attributes
		self.latest_report.failed_tests = None

		# print a title for the report regardless of what sections are chosen to
		# be shown
		print('')
		print('')
		print('===========================')
		print('= Report for platform {} ='.format(self.args.platform))
		print('===========================')
		print('Test Suite: {}'.format(self.args.igt_suite))
		print('Date: {}'.format(datetime.datetime.now().strftime('%Y-%m-%d')))
		print('')

	def _print_table(self, table_header, table_content, title=None, footer=None):
		"""Prints a table in the console and at a CSV file if enabled.

		:param table_header: a list with the header elements
		e.g. ['Name', 'Last Name', 'Age']
		:param table_content: a list of lists containing the data, each list
		represents a row of data in the table.
		e.g. [['John', 'Doe', 39], ['Jane', 'Bar', 23]]
		:param title: the title of the table
		:param footer: a footer note for the table
		:return:
		"""
		if title:
			print('')
			print('-------------------------------------------------')
			print(' {title} '.format(title=title.upper()))
			print('-------------------------------------------------')
			print('')
		print(tabulate(table_content, table_header, tablefmt=self.args.format))
		if footer:
			print(footer)
		print('')
		if self.args.output_file:
			self.export_to_csv(
				table_content, table_header, footer=footer, filename=self.args.output_file)

	def print_report_summary(self):
		""""Prints a summary of test results from reports"""

		# define some alias to work with shorter variables
		previous = self.previous_report
		latest = self.latest_report

		self._print_table(
			['General Info', 'Latest - 1', 'Latest'],
			[
				['ID', previous.qa_id, latest.qa_id],
				['Report Title', previous.title, latest.title],
				['Created At', previous.created_at, latest.created_at],
				['Work Week', previous.weeknum, latest.weeknum]
			],
			title='totals')

		self._print_table(
			['Execution Totals', 'Latest - 1', 'Latest'],
			[
				['Total test cases', previous.total_cases, latest.total_cases],
				['Total pass', previous.total_pass, latest.total_pass],
				['Total fail', previous.total_fail, latest.total_fail],
				['Total not run', previous.total_not_run, latest.total_not_run],
			])

		self.regressions = self.report_server.get_regressions(
			self.previous_report, self.latest_report
		)
		self.progressions = self.report_server.get_progressions(
			self.previous_report, self.latest_report
		)
		self._print_table(
			['Transition Type', 'Totals'],
			[
				['Regressions', len(self.regressions)],
				['Progressions', len(self.progressions)]
			])

		# get the list of failed test cases including bugs associated to them
		# from the latest report
		self.latest_report.failed_tests = self.latest_report.get_failed_tests()
		failed_tests_with_bugs = self.latest_report.failed_tests[
			'failed_tests_with_bugs']

		# count the number of bugs based on importance and status
		importance_high_critical = 0
		importance_high_major = 0
		status_new = 0
		status_reopened = 0
		for bug in failed_tests_with_bugs.itervalues():
			if bug['priority'] == 'high':
				if bug['severity'] == 'critical':
					importance_high_critical += 1
				elif bug['severity'] == 'major':
					importance_high_major += 1
			if bug['status'] == 'NEW':
				status_new += 1
			elif bug['status'] == 'REOPENED':
				status_reopened += 1

		self._print_table(
			['Bug Associated To A Failed Test', 'Totals'],
			[
				['High Critical bugs in FDO', importance_high_critical],
				['High Major bugs in FDO', importance_high_major],
				['Bugs in NEW status in FDO', status_new],
				['Bugs in REOPENED status in FDO', status_reopened]
			])

	def print_test_transitions(self):
		"""Prints the regressions and progressions of tests"""

		# regressions
		if self.regressions is None:
			self.regressions = self.report_server.get_regressions(
				self.previous_report, self.latest_report
			)
		table_content = list()
		for test in self.regressions:
			table_content.append([test])

		self._print_table(
			['Regressions'],
			table_content,
			title='test transitions',
			footer='Number of regressions: {}'.format(len(self.regressions))
		)

		# progressions
		if self.progressions is None:
			self.progressions = self.report_server.get_progressions(
				self.previous_report, self.latest_report
			)
		table_content = list()
		for test in self.progressions:
			table_content.append([test])
		self._print_table(
			['Progressions'],
			table_content,
			footer='Number of progressions: {}'.format(len(self.progressions))
		)

	def print_failures(self):
		"""Prints tests in failed status and associated bugs"""

		# get the list of failed test cases including bugs associated to them
		# from the latest report
		if self.latest_report.failed_tests is None:
			self.latest_report.failed_tests = self.latest_report.get_failed_tests()
		failed_tests_without_bugs = self.latest_report.failed_tests[
			'failed_tests_without_bugs']
		failed_tests_with_bugs = self.latest_report.failed_tests[
			'failed_tests_with_bugs']

		# check each one of those bugs, if they are duplicates of other bugs,
		# replace the bug info with the original bug info
		for test, bug in failed_tests_with_bugs.iteritems():
			if bug['duplicate']:
				failed_tests_with_bugs[test] = bugz.get_bug_details(bug['duplicate'])

		table_content = list()
		for test, bug in failed_tests_with_bugs.iteritems():
			table_content.append(
				[
					test,
					bug['id'],
					bug['status'],
					'{p} {s}'.format(p=bug['priority'], s=bug['severity'])]
			)
		for test in failed_tests_without_bugs:
			table_content.append(
				[
					test,
					'No bug associated',
					'',
					''
				]
			)
		self._print_table(
			['Failed Test', 'Bug ID', 'Bug Status', 'Bug Importance'],
			table_content,
			title='failures & bugs',
			footer='Number of failed tests: {}'.format(len(table_content))
		)

		table_content = list()
		for test in failed_tests_without_bugs:
			table_content.append([test])
		self._print_table(
			['Tests Without Bugs'],
			table_content,
			footer=(
				'Number of failed tests without bug: {}'
				.format(len(failed_tests_without_bugs)))
		)

	def print_not_run(self):
		"""Prints tests in not run status"""

		# Get the list of tests that were not run
		not_run = self.latest_report.get_not_run_tests()

		table_content = list()
		for test in not_run:
			table_content.append([test])
		self._print_table(
			['Tests Not Run'],
			table_content,
			title='tests not run',
			footer=(
				'Number of tests not run: {}'
				.format(self.latest_report.total_not_run))
		)

	def print_families_with_failures(self):
		"""Prints test families with one or more failed tests"""

		# get the family name of failed tests
		families_with_bugs = self.latest_report.get_igt_families_with_bugs()

		table_content = list()
		for family, bugs in families_with_bugs.iteritems():
			table_content.append([family, list(bugs)])

		tbl_header = [
			'Families With Failures', 'highest', 'high', 'normal', 'low', 'lowest']
		table_body = []
		for element in table_content:
			family = element[0]
			bugs = element[1]
			lowest = []
			low = []
			medium = []
			high = []
			highest = []
			for bug in bugs:
				details = bugz.get_bug_details(bug)
				priority = details['priority']
				bug_data = '{bug} ({severity})'.format(
					bug=bug, severity=details['severity'])
				if priority == 'lowest':
					lowest.append(bug_data)
				elif priority == 'low':
					low.append(bug_data)
				elif priority == 'medium':
					medium.append(bug_data)
				elif priority == 'high':
					high.append(bug_data)
				elif priority == 'highest':
					highest.append(bug_data)
			table_body.append(
				[
					family,
					', '.join(highest) if highest else '',
					', '.join(high) if high else '',
					', '.join(medium) if medium else '',
					', '.join(low) if low else '',
					', '.join(lowest) if lowest else '',
				]
			)

		self._print_table(
			tbl_header,
			table_body,
			title='families',
			footer=(
				'Number of families with failed tests: {}'
				.format(len(families_with_bugs)))
		)

	def export_to_csv(self, table, header, footer=None, filename=None):
		"""Writes the data in a CSV formatted file.

		The function receives data in a format that is compatible with tabulate
		so they both can be used seamlessly to create a table with tabulate and
		export the data to a CSV file.
		:param header: a list with the header elements
		e.g. ['Name', 'Last Name', 'Age']
		:param table: a list of lists containing the data, each list represents
		a row of data in the table.
		e.g. [['John', 'Doe', 39], ['Jane', 'Bar', 23]]
		:param footer: a footer note for the table
		:param filename: the name and path of the CSV file to be created/updated
		:return: True
		"""
		if not filename:
			filename = '{platform}_report.csv'.format(platform=self.args.platform)
		if not isinstance(header, list) or not isinstance(table, list):
			raise KeyError('header and table should be lists with one item per column')
		if not os.path.exists(os.path.dirname(filename)):
			os.makedirs(os.path.dirname(filename))
		with open(filename, 'ab') as csvfile:
			csv_writer = csv.writer(csvfile, dialect='excel')
			csv_writer.writerow(header)
			for row in table:
				csv_writer.writerow(row)
			if footer:
				csv_writer.writerow([footer])
			# add a couple of blank lines after a column
			csv_writer.writerow([])
			csv_writer.writerow([])


def list_reports(platform, suite, password=None, rsa_key=None):
	"""Lists all the reports for a specific platform and test suite.

	:param platform: the platform to search for
	:param suite: the test suite to search for
	:param password: the password to authenticate with the report server
	:param rsa_key: the public key used to authenticate to the report server
	:return: nothing, just prints the data to the user
	"""
	report_server = reptools.LinuxGraphicsServer(
		platform, suite, password, rsa_key)
	reports = report_server.list_reports()
	print(
		'\nList of {suite} reports for platform {platform}.\n'
		.format(suite=suite, platform=platform)
	)

	for build_id, csv_file in reports.iteritems():
		print('Work Week: {0}'.format(csv_file.split('WW')[1][:2]))
		print('Build ID: {0}'.format(build_id))
		print('Report CSV: {0}'.format(csv_file))
		print('')


def parse_arguments():
	"""Parse arguments from the command line."""

	parser = argparse.ArgumentParser(
		description='Generates reports for the selected platform.')

	# required positional arguments
	parser.add_argument(
		'platform', help='The platform for which you want to generate a report')
	parser.add_argument(
		'igt_suite', choices=['all', 'fastfeedback'],
		help='The test suite you want to generate the report about, either '
		'IGT All or IGT FastFeedback')

	# optional arguments
	parser.add_argument(
		'-l', '--list-reports', action='store_true',
		help='Lists all the reports in LinuxGraphics for the specified'
		'platform and suite'
	)
	parser.add_argument(
		'--report-ids', nargs=2, metavar=('ID1', 'ID2'),
		help='By default the generator finds the latest two reports for the '
		'specified platform. Use this parameter if you want to specify '
		'different report ids for the analysis'
	)
	parser.add_argument(
		'--format', choices=['fancy_grid', 'jira', 'rst', 'html'],
		default='fancy_grid',
		help='The format for the output data. It defaults to fancy_grid')
	parser.add_argument(
		'--remove', nargs='*',
		choices=['summary', 'transitions', 'failures', 'notrun', 'families'],
		help='Removes one or many sections from the report'
	)
	parser.add_argument(
		'-o', '--output-file',
		help='If set, the report will be exported to the CSV file specified '
		'here (specify the full path)'
	)
	# this linuxgraphics option is a temporary option that will allow users to
	# generate the reports based on TRC (by default) or based on linuxgraphics.
	# this way we''ll allow users to still use the TRC functionality while it
	# is still online, but we are ready to switch to using linuxgraphics at any
	# moment.
	# TODO(Cas): As soon as TRC EOL remove this option
	parser.add_argument(
		'--linuxgraphics', action='store_true',
		help='Use this flag to get the reports from LinuxGraphics instead of '
		'TRC'
	)

	# optional mutually exclusive arguments
	exclusive_group = parser.add_mutually_exclusive_group()
	exclusive_group.add_argument(
		'--password',
		help='Password used to authenticate to the report server'
	)
	exclusive_group.add_argument(
		'--rsa-key',
		help='Public key used to authenticate with the report server (id_rsa.pub)'
	)

	args = parser.parse_args()

	if args.output_file and os.path.isfile(args.output_file):
		os.remove(args.output_file)
	args.platform = args.platform.upper()
	args.igt_suite = args.igt_suite.lower()

	# Handle mutually exclusive groups by hand to make it custom
	if args.list_reports and (args.report_ids or args.remove or args.output_file):
		sys.exit(
			'--list cannot be used with --report-ids | --format | --remove | '
			'--output-file'
		)

	return args


if __name__ == '__main__':

	# parse the command line arguments
	ARGS = parse_arguments()

	if ARGS.list_reports:

		list_reports(
			ARGS.platform, ARGS.igt_suite,
			ARGS.password, ARGS.rsa_key)

	else:

		# collect all the required information
		REPORT_GENERATOR = ReportGenerator(ARGS)

		# print the enabled data to the console
		if not ARGS.remove:
			ARGS.remove = ['default']
		if 'summary' not in ARGS.remove:
			REPORT_GENERATOR.print_report_summary()
		if 'transitions' not in ARGS.remove:
			REPORT_GENERATOR.print_test_transitions()
		if 'failures' not in ARGS.remove:
			REPORT_GENERATOR.print_failures()
		if 'notrun' not in ARGS.remove:
			REPORT_GENERATOR.print_not_run()
		if 'families' not in ARGS.remove:
			REPORT_GENERATOR.print_families_with_failures()
