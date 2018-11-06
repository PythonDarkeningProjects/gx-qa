"""Provides functions to interact with reports from IGT executions"""

from __future__ import print_function

import collections
import csv
import datetime
import json
import os
import re
import tarfile

import requests

import common.remote_client as remote_client
import common.tools.bugz as bugzilla
import gfx_qa_tools.common.bash as bash
from gfx_qa_tools.config.config import CONFIG


class ReportServer(object):
	"""Provides functions to interact with the report server"""

	def __init__(self, platform, suite):

		# initialize values
		self.platform = platform.upper()
		self.suite = suite.lower()
		valid_test_suites = ('all', 'fastfeedback')
		if self.suite not in valid_test_suites:
			raise ValueError(
				'Incorrect test suite selected. Valid test suites are: {}'
				.format(valid_test_suites)
			)

	def _compile_csv_pattern(self):
		"""Compiles a pattern to find CSV files by suite and platform

		:return: a compiled pattern to use with re.match
		"""
		suite = 'fast_feedback' if self.suite == 'fastfeedback' else self.suite
		pattern = (
			r'igt_{suite}_{platform}-._TRC_summary_WW.+\.csv'
			.format(suite=suite, platform=self.platform)
		)
		return re.compile(pattern)

	@staticmethod
	def _find_transitions(report1, report2, old_status, new_status):
		"""Finds tests that changed from old_status to new_status in two reports.

		:param report1: the report object of the first report to compare
		:param report2: the report object of the second report to compare
		:param old_status: the initial status of the test
		:param new_status: the final status of the test
		:return: a list tests that changed from old_status to new_status from
		report 1 to report 2
		"""
		results_1 = report1.get_test_results_by_list()
		results_2 = report2.get_test_results_by_list()
		if not results_1 or not results_2:
			return None

		# compare report 1, with report 2 to find those elements
		# that went from old_status to new_status
		return list(set(results_1[old_status]) & set(results_2[new_status]))

	@staticmethod
	def get_progressions(previous_report, latest_report):
		"""Finds all the progressions between two reports.

		A progression is defined as a test that was failing in one execution but
		it is passing in a subsequent execution.
		:param previous_report: the report object of previous report (N-1)
		:param latest_report: the report object of latest report (N)
		:return: a list of test progressions if both reports are found,
		None otherwise
		"""
		return ReportServer._find_transitions(
			previous_report,
			latest_report,
			'failed',
			'passed'
		)

	@staticmethod
	def get_regressions(previous_report, latest_report):
		"""Finds all the regressions between two reports.

		A regression is defined as a test that was passing in one execution
		but it is failing in a subsequent execution.
		:param previous_report: the report object of previous report (N-1)
		:param latest_report: the report object of latest report (N)
		:return: a list of test regressions if both reports are found,
		None otherwise
		"""
		return ReportServer._find_transitions(
			previous_report,
			latest_report,
			'passed',
			'failed'
		)


class LinuxGraphicsServer(ReportServer):
	"""Provides functions to interact with the LinuxGraphics server"""

	reports_path = CONFIG.get('linuxgraphics', 'vis_reports_path')

	def __init__(self, platform, suite, password=None, rsa_file=None):
		"""Initializes the LinuxGraphicsServer instance.

		All of the tasks that can be performed with an instance of this class
		need to have access to the LinuxGraphics server, so this initializer
		creates an SSH client to interact with that server.
		:param platform: the platform to use for listing and getting reports
		:param suite: the suite to use for listing and getting reports
		:param password: the password to use to authenticate with the server,
		if no password is provided, an RSA key will need to be used
		:param rsa_file: the path to a public RSA key to authenticate with the
		server.
		"""

		super(LinuxGraphicsServer, self).__init__(platform, suite)

		# get a client to interact with the report server via SSH
		self.report_server = remote_client.RemoteClient(
			CONFIG.get('linuxgraphics', 'ip'),
			CONFIG.get('linuxgraphics', 'report_tool_user'),
			password=password,
			rsa_file=rsa_file
		)

	def list_reports(self):
		"""Lists all the reports for a specific platform and test suite.

		:return: a dictionary with all the build_ids and their associated CSV
		reports
		"""
		suite = 'fast_feedback' if self.suite == 'fastfeedback' else self.suite

		# from all build IDs available in the report server select those that
		# start with QA_DRM (this is to remove builds from sandbox)
		suite_path = (
			'{path}/igt_{suite}'
			.format(path=LinuxGraphicsServer.reports_path, suite=suite)
		)
		all_build_ids = self.report_server.run_command(
			'ls {0}'.format(suite_path)
		)[1].split()
		build_ids = [bid for bid in all_build_ids if bid.startswith('QA_DRM_')]
		build_ids = sorted(build_ids, key=lambda x: int(x[7:]), reverse=True)

		# search in all build directories one by one for reports for the specified
		# platform
		regex = self._compile_csv_pattern()
		reports = collections.OrderedDict()
		for build_id in build_ids:
			report_path = os.path.join(suite_path, build_id, self.platform)
			error_code, report_files = self.report_server.run_command(
				'ls {0}'.format(report_path))
			# if there is no report for that platform continue with the next one
			if error_code:
				continue
			report_files = report_files.split()
			report_csv = filter(regex.match, report_files)
			# if there is no CSV that matches the criteria in the dir skip it
			if not report_csv:
				continue
			# if there are more than one CSV that matches the pattern we are
			# looking for add both with an extra index at the end
			if len(report_csv) > 1:
				bash.message(
					'warn',
					'More than one CSV files were found for build id {bid} for {platform}'
					.format(bid=build_id, platform=self.platform)
				)
				for index, csvfile in enumerate(report_csv):
					reports[
						'{build_id} ({i})'.format(build_id=build_id, i=index + 1)
					] = csvfile
			else:
				reports[build_id] = report_csv[0]

		return reports

	def get_report(self, build_id):
		"""Gets the report with specific ID, platform and suite from the server.

		:param build_id: the build_id to use to search for the report
		:return: a dictionary with the test name and test status from the CSV
		"""
		tests = dict()
		workweek = 'N/A'
		csv_path = ''
		regex = self._compile_csv_pattern()
		suite = 'fast_feedback' if self.suite == 'fastfeedback' else self.suite

		# get the path(s) to the report. Note that we can get two paths if
		# there are reports for IGT all and fast feedback for the same build_id
		build_path = self.report_server.run_command(
			'find {path} -name {bid}'
			.format(path=LinuxGraphicsServer.reports_path, bid=build_id)
		)[1].split()
		if not build_path:
			bash.message(
				'warn', 'No report with ID {id} was found'.format(id=build_id))
			return {}

		# search for a directory for the specified platform
		for path in build_path:
			if suite in path:
				report_path = os.path.join(path, self.platform)
				error_code, report_files = self.report_server.run_command(
					'ls {0}'.format(report_path))
				if error_code:
					bash.message(
						'warn',
						'There are no reports for platform {plat} for this '
						'build {build}'.format(plat=self.platform, build=build_id))
					return {}

				# search for the CSV file within the platform directory
				report_files = report_files.split()
				report_csv = filter(regex.match, report_files)

				# if there are more than one CSV that matches the pattern we are
				# looking for, ask the user interactively which one he/she wants
				if len(report_csv) > 1:
					bash.message(
						'warn',
						'More than one CSV files were found for build id {bid} '
						'for {platform}'
						.format(bid=build_id, platform=self.platform)
					)
					print('Please specify what report you want:')
					for index, csvfile in enumerate(report_csv):
						print('  {index}) {csv}'.format(index=index + 1, csv=csvfile))
					selection = input('Option: ')
					csv_path = os.path.join(report_path, report_csv[selection - 1])
				else:
					csv_path = os.path.join(report_path, report_csv[0])

		# extract the data from the CSV file
		total_cases = 0
		total_pass = 0
		total_fail = 0
		total_not_run = 0
		total_skip = 0
		total_incomplete = 0
		total_timeout = 0
		if csv_path:
			csv_file = self.report_server.open_remote_file(csv_path)
			reader = csv.reader(csv_file)
			next(reader)  # skip the header row
			for row in reader:
				tests[row[1]] = {
					'result': row[2],
					'bugs': row[3],
					'comment': row[4]
				}
				# count how many tests are for each one
				if row[2] == 'pass':
					total_pass += 1
				elif row[2] == 'fail':
					total_fail += 1
				elif row[2] == 'not run':
					total_not_run += 1
					if 'skip' in row[4]:
						total_skip += 1
					elif 'incomplete' in row[4]:
						total_incomplete += 1
					elif 'timeout' in row[4]:
						total_timeout += 1
				total_cases += 1
			csv_file.close()
			# get the work week from the CSV name
			workweek = re.search('_WW(.+)_', csv_path).group(1)

		return {
			'tests': tests,
			'profile': self.platform,
			'qa_id': build_id,
			'weeknum': workweek,
			'csv': csv_path.rsplit('/')[-1],
			'title': csv_path.rsplit('/')[-1],
			'created_at': 'N/A',
			'total_cases': total_cases,
			'total_pass': total_pass,
			'total_fail': total_fail,
			'total_skip': total_skip,
			'total_incomplete': total_incomplete,
			'total_timeout': total_timeout,
			'total_not_run': total_not_run,
		}

	def get_latest_reports(self, amount=2):
		"""Retrieves the latest reports that meet the criteria

		:param amount: the number of reports to return
		:return: a list containing the latest brief reports of a given platform
		and type
		"""
		# get the full list of reports
		reports = self.list_reports()
		latest_reports = list()

		# reduce the list to the amount requested by the user
		for build_id, csv_file in reports.items()[:amount]:
			# get the work week from the CSV name
			workweek = re.search('_WW(.+)_', csv_file).group(1)
			latest_reports.append(
				{
					'qa_id': build_id,
					'csv': csv_file,
					'profile': self.platform,
					'weeknum': workweek
				}
			)

		# return only the requested number of reports
		return latest_reports


class TRCServer(ReportServer):
	"""Provides functions to interact with the TRC server"""

	trc_url = 'https://otcqarpt.jf.intel.com/gfx/api/reports'

	@staticmethod
	def get_report(report_id, brief=False):
		"""Retrieves the specified report from TRC.

		:param report_id: the qa_id of the report to be retrieved
		:param brief: if True only the brief report is returned (without individual
		test results), otherwise the full report is returned
		:return: a dictionary containing the whole report data if a report is found
		otherwise None is returned
		"""
		report_id = str(report_id)
		payload = {
			'limit_amount': '500',
			'brief': 'true'
		}

		# search for reports starting today minus 30 days and go back 30 day
		# by 30 day until we find the report requested
		brief_report = dict()
		today = datetime.datetime.now().strftime('%Y-%m-%d')
		payload['begin_time'] = today
		day_counter = 365
		day_period = 30

		while not brief_report and day_counter > 0:

			begin_time = datetime.datetime.strptime(payload['begin_time'], '%Y-%m-%d')
			begin_time = begin_time - datetime.timedelta(days=day_period)
			payload['begin_time'] = begin_time.strftime('%Y-%m-%d')

			# get a list of reports for the selected day
			response = requests.get(
				'https://otcqarpt.jf.intel.com/gfx/api/reports',
				params=payload, verify=False, timeout=30)
			response.raise_for_status()
			reports = response.json()

			# search for the desired id within the retrieved reports,
			# if found copy it and exit the search
			for report in reports.itervalues():
				if report['qa_id'] == report_id:
					brief_report = report
					break

			# decrease the day counter, this is to make sure the while does not get
			# stuck forever if no report is found with the given id. The function
			# would go back up to this amount of days to search for the report.
			day_counter -= day_period

		# if no report was found return None
		if not brief_report:
			return None

		# return the brief report (without individual test results) if that is what
		# the user selected
		if brief:
			return brief_report

		# if the user wanted the full report search for it by using the created_at
		# field
		payload = {
			'limit_amount': '1',
			'begin_time': brief_report['created_at'],
			'brief': 'false'
		}
		response = requests.get(
			TRCServer.trc_url, params=payload, verify=False, timeout=10)

		# if the status code of the response is not 200 raise an exception
		response.raise_for_status()
		full_report = response.json()['0']

		# create a section in the report called tests that include test names and
		# result so it is consistent with the JSON reports
		tests = dict()
		total_incomplete = 0
		total_skip = 0
		total_timeout = 0
		total_not_run = 0
		for test in full_report['features']['0']['cases'].itervalues():
			tests[test['name']] = {
				'result': test['result'],
				'comment': test['comment'],
				'bugs': test['bugs'],
			}
			if test['result'] == 'not_run':
				total_not_run += 1
				if 'skip' in test['comment']:
					total_skip += 1
				elif 'incomplete' in test['comment']:
					total_incomplete += 1
				elif 'timeout' in test['comment']:
					total_timeout += 1

		# add the test summary to the report
		full_report['total_incomplete'] = total_incomplete
		full_report['total_skip'] = total_skip
		full_report['total_timeout'] = total_timeout
		full_report['total_not_run'] = total_not_run
		full_report['tests'] = tests

		return full_report if full_report['qa_id'] == report_id else None

	def get_latest_reports(self, amount=2):
		"""Retrieves the latest reports that meet the criteria from TRC.

		:param amount: the number of reports to return
		:return: a list containing the latest brief reports of a given
		platform and type
		"""
		# convert arguments
		test_suite = 'IGT' if self.suite == 'all' else 'IGT fastfeedback'

		# variable initialization
		counter = 0
		payload = {
			'brief': 'true',
			'limit_amount': '200'
		}

		# search for reports starting today and go back one day by one day
		# until we find the amount of reports requested
		today = datetime.datetime.now().strftime('%Y-%m-%d')
		payload['begin_time'] = today
		while counter < amount:
			counter = 0
			latest_reports = list()

			reports_brief = requests.get(
				TRCServer.trc_url, params=payload, verify=False, timeout=10)
			reports_brief.raise_for_status()

			for report in reports_brief.json().itervalues():
				if report['profile'] == self.platform and report['testtype'] == test_suite:
					counter += 1
					latest_reports.append(report)
			begin_time = datetime.datetime.strptime(payload['begin_time'], '%Y-%m-%d')
			begin_time = begin_time - datetime.timedelta(days=1)
			payload['begin_time'] = begin_time.strftime('%Y-%m-%d')

		# order the filtered reports from most recent to oldest
		latest_reports = sorted(
			latest_reports, key=lambda rep: rep['created_at'], reverse=True)

		# return only the requested number of reports
		return latest_reports[:amount]


class Report(object):
	"""Manages data from a specific report"""

	def __init__(
		self, build_id, platform, suite, server='trc',
		password=None, rsa_file=None):
		"""Initializes the Report object with a report from a platform & suite.

		:param build_id: the build_id to use to search for the report
		:param platform: the platform for the report
		:param suite: the test suite for the report
		:param password: the password to authenticate to the report server
		:param rsa_file: the public rsa key to authenticate to the report server
		"""
		# get the report
		if server == 'linuxgraphics':
			report_server = LinuxGraphicsServer(platform, suite, password, rsa_file)
		else:
			report_server = TRCServer(platform, suite)

		report = report_server.get_report(build_id)
		self.tests = report.get('tests', None)
		self.profile = report.get('profile', None)
		self.qa_id = report.get('qa_id', None)
		self.weeknum = report.get('weeknum', None)
		self.csv_file = report.get('csv', None)
		self.title = report.get('title', None)
		self.created_at = report.get('created_at', None)
		self.total_cases = report.get('total_cases', None)
		self.total_pass = report.get('total_pass', None)
		self.total_fail = report.get('total_fail', None)
		self.total_skip = report.get('total_skip', None)
		self.total_incomplete = report.get('total_incomplete', None)
		self.total_timeout = report.get('total_timeout', None)
		self.total_not_run = report.get('total_not_run', None)

	@staticmethod
	def _extract_bug_number(bug_reference):
		"""Extracts the bug number from a bug reference in a report.

		:param bug_reference: the string returned for a bug reference in a
		test
		:return: the bug ID referenced if any, None otherwise
		"""
		# validate the input, if the string does not contain a bug reference
		# return None
		if 'https://bugs.freedesktop.org/show_bug.cgi?id' not in bug_reference:
			return None
		# extract the bug number from the reference
		bug_url = bug_reference.split()[0].replace('[', '')
		bug_id = bug_url.split('=')[1]

		return str(bug_id)

	def get_test_results_by_list(self):
		"""Separates tests from a report into lists based on its result.

		:return: a dictionary containing 6 lists:
			- passed
			- failed
			- not_run
			- skip
			- incomplete
			- timeout
			- None if the report is not found
		"""
		passed_tests = list()
		failed_tests = list()
		not_run_tests = list()
		skip_tests = list()
		incomplete_tests = list()
		timeout_tests = list()

		# separate the tests in lists according to result & comment
		for test, test_data in self.tests.iteritems():
			if test_data['result'] == 'pass':
				passed_tests.append(test)
			elif test_data['result'] == 'fail':
				failed_tests.append(test)
			elif test_data['result'] == 'not_run' or test_data['result'] == 'not run':
				not_run_tests.append(test)
				if 'skip' in test_data['comment']:
					skip_tests.append(test)
				elif 'incomplete' in test_data['comment']:
					incomplete_tests.append(test)
				elif 'timeout' in test_data['comment']:
					timeout_tests.append(test)

		results = {
			'passed': passed_tests,
			'failed': failed_tests,
			'not_run': not_run_tests,
			'skipped': skip_tests,
			'incomplete': incomplete_tests,
			'timeout': timeout_tests
		}

		return results

	def get_failed_tests(self, bug_details=True):
		"""Finds all the failed tests and their related bugs in a report.

		:param bug_details: whether or not return details from a bug, if set to
		True the bug number and current info will be retrieved from bugzilla,
		if set to False only the bug number will be provided
		:return: a dictionary containing the following fields:
			failed_tests_with_bugs: contains a dictionary with failed tests and
			their associated bug ID and bug details if enabled
			failed_tests_without_bugs: a list of failed tests with no
			associated bug
		"""
		failed_tests = dict()
		failed_tests_without_bug = list()

		# build the lists with all failed tests from the report
		for test, test_values in self.tests.iteritems():
			if test_values['result'] == 'fail':
				if test_values['bugs'] == 'this test has not bug related in database':
					failed_tests_without_bug.append(str(test))
				else:
					bug_id = Report._extract_bug_number(test_values['bugs'])
					failed_tests[str(test)] = bug_id

		# if enabled, get the bug details from bugzilla
		if bug_details:
			failed_tests = {
				test: bugzilla.get_bug_details(bug)
				for test, bug in failed_tests.iteritems()
			}

		return {
			'failed_tests_with_bugs': failed_tests,
			'failed_tests_without_bugs': failed_tests_without_bug
		}

	def get_not_run_tests(self):
		"""Finds all the tests that did not run in a report.

		:return: a list of tests that were not run
		"""
		not_run_tests = list()

		# build the list of tests not run
		for test, values in self.tests.iteritems():
			if values['result'] == 'not run' or values['result'] == 'not_run':
				not_run_tests.append(str(test))

		return not_run_tests

	def get_igt_families_with_failures(self):
		"""Gets all the test families that have failed tests in a report.

		:return: a list containing all the families that contain one or more
		failed tests
		"""
		# get all families with failed tests
		failed_tests = self.get_test_results_by_list()['failed']
		families = [test.replace('igt@', '').split('@')[0] for test in failed_tests]

		# remove duplicate families and convert them to string
		return [str(family) for family in set(families)]

	def get_igt_families_with_bugs(self):
		"""Retrieves all IGT families with failures and their related bugs.

		:return: a dictionary containing the IGT families that have one or
		more failed tests and a list of the related bugs for each family.
		"""
		# get all the failed tests with bugs
		failed_tests = self.get_failed_tests(bug_details=False)
		tests_with_bugs = failed_tests['failed_tests_with_bugs']

		# get the families from the failures and add the related bugs
		families = dict()
		for test, bug in tests_with_bugs.iteritems():
			family = test.replace('igt@', '').split('@')[0]
			families.setdefault(family, set()).add(bug)

		return families


def get_report_from_json(results_file):
	"""Retrieves the specified report from a json file.

	:param results_file: the full path to the file that contains the results from
	the IGT execution. The file can be a json file or a compressed json tar.
	Example: '/my/path/resulst.json', '/my/path/results.json.tar' or
	'/my/path/results.json.tar.gz'
	:return: a dictionary containing the whole report data if a report is found
	otherwise an empty dictionary is returned
	"""
	# validate the provided path to the file
	report = dict()
	if not os.path.isfile(results_file):
		return report

	# get the report from the file depending on if the file is compressed or not
	if '.tar' in results_file:
		with tarfile.open(name=results_file, mode='r') as tar:
			for member in tar.getmembers():
				if '/results.json' in member.name:
					results_file = tar.extractfile(member)
					report = json.loads(results_file.read())
	else:
		with open(results_file, 'r') as json_file:
			report = json.load(json_file)

	# return the report
	return report
