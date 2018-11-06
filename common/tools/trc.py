"""Provides functions to interact with TRC"""

from __future__ import print_function

import datetime

import requests

import common.tools.bugz as bugz

TRC_URL = 'https://otcqarpt.jf.intel.com/gfx/api/reports'


def _extract_bug_number(bug_reference):
	"""Extracts the bug number from a bug reference in a TRC report.

	:param bug_reference: the string returned by TRC for a bug reference in a test
	:return: the bug ID referenced by TRC if any, None otherwise
	"""
	# validate the input, if the string does not contain a bug reference return
	# None
	if 'https://bugs.freedesktop.org/show_bug.cgi?id' not in bug_reference:
		return None
	# extract the bug number from the reference
	bug_url = bug_reference.split()[0].replace('[', '')
	bug_id = bug_url.split('=')[1]

	return str(bug_id)


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

	# search for reports starting today minus 30 days and go back 30 day by 30 day
	# until we find the report requested
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
			'https://otcqarpt.jf.intel.com/gfx/api/reports', params=payload,
			verify=False, timeout=30)
		response.raise_for_status()
		reports = response.json()

		# search for the desired id within the retrieved reports, if found copy
		# it and exit the search
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
		TRC_URL, params=payload, verify=False, timeout=10)
	# if the status code of the response is not 200 raise an exception
	response.raise_for_status()
	full_report = response.json()['0']
	# create a section in the report called tests that include test names and
	# result so it is consistent with the JSON reports
	tests = {
		test['name']: {'result': test['result']}
		for test in full_report['features']['0']['cases'].itervalues()
	}
	full_report['tests'] = tests

	return full_report if full_report['qa_id'] == report_id else None


def get_latest_reports(platform, test_suite, amount=2):
	"""Retrieves the latest reports that meet the criteria from TRC.

	:param platform: the platform to look for in the reports
	:param test_suite: the test suite to look for in the reports.
		Valid values: (igt, fastfeedback)
	:param amount: the number of reports to return
	:return: a list containing the latest brief reports of a given platform and
	type
	"""
	# validate arguments
	platform = platform.upper()
	test_suite = test_suite.lower()
	valid_test_suites = ('all', 'fastfeedback')
	if test_suite not in valid_test_suites:
		raise ValueError(
			'Incorrect test suite selected. Valid test suites are: {}'
			.format(valid_test_suites))
	test_suite = 'IGT' if test_suite == 'all' else 'IGT fastfeedback'

	# variable initialization
	counter = 0
	payload = {
		'brief': 'true',
		'limit_amount': '200'
	}

	# search for reports starting today and go back one day by one day until we
	# find the amount of reports requested
	today = datetime.datetime.now().strftime('%Y-%m-%d')
	payload['begin_time'] = today
	while counter < amount:
		counter = 0
		latest_reports = list()

		reports_brief = requests.get(
			TRC_URL, params=payload, verify=False, timeout=10)
		reports_brief.raise_for_status()

		for report in reports_brief.json().itervalues():
			if report['profile'] == platform and report['testtype'] == test_suite:
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


def get_failed_tests(report_id, bug_details=True):
	"""Finds all the failed tests and their related bugs in a report.

	:param report_id: the qa_id of the report to be retrieved
	:param bug_details: wether or not return details from a bug, if set to True
	the bug number and current info will be retrieved from bugzilla, if set to
	False only the bug number will be provided
	:return: a dictionary containing the following fields:
		failed_tests_with_bugs: contains a dictionary with failed tests and their
		associated bug ID and bug details if enabled
		failed_tests_without_bugs: a list of failed tests with no associated bug
	"""
	# get the full report
	full_report = get_report(report_id)
	if not full_report:
		return None

	failed_tests = dict()
	failed_tests_without_bug = list()
	for test in full_report['features']['0']['cases'].itervalues():
		if test['result'] == 'fail':
			if test['bugs'] == 'this test has not bug related in database':
				failed_tests_without_bug.append(str(test['name']))
			else:
				bug_id = _extract_bug_number(test['bugs'])
				failed_tests[str(test['name'])] = bug_id

	# if enabled, get the bug details from bugzilla
	if bug_details:
		failed_tests = {
			test: bugz.get_bug_details(bug)
			for test, bug in failed_tests.iteritems()
		}

	return {
		'failed_tests_with_bugs': failed_tests,
		'failed_tests_without_bugs': failed_tests_without_bug
	}


def get_not_run_tests(report_id):
	"""Finds all the tests that did not run in a report.

	:param report_id: the qa_id of the report to be retrieved
	:return: a list of tests that were not run
	"""
	# get the full report
	full_report = get_report(report_id)
	if not full_report:
		return None

	not_run_tests = list()
	for test, values in full_report['tests'].iteritems():
		if values['result'] == 'not_run':
			not_run_tests.append(str(test))

	return not_run_tests


def get_igt_families_with_bugs(report_id):
	"""Retrieves all IGT families with failures and their related bugs.

	:param report_id: the qa_id of the report from which the families and bugs
	will be collected.
	:return: a dictionary containing the IGT families that have one or more
	failed tests and a list of the related bugs for each family.
	"""
	tests_with_bugs = get_failed_tests(report_id, False)['failed_tests_with_bugs']
	families = dict()
	for test, bug in tests_with_bugs.iteritems():
		family = test.replace('igt@', '').split('@')[0]
		families.setdefault(family, set()).add(bug)

	return families
