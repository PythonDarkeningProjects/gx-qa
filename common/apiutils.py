"""Provides a library of useful utilities specific to gfx-qa-tools.

This module provides a list of general purpose utilities that are domain
specific for the gfx-qa-tools project and are not portable or add no value
outside the scope of this project.
"""

import json
import logging
import sys

import requests

LOGGER = logging.getLogger(__name__)


def unlock_lock_system_in_watchdog_db(
	raspberry_number, power_switch_number, action, user='automated-system'):
	"""lock/unlock a system in watchdog database

	the aim of this function is to lock/unlock systems in watchdog database

	:param raspberry_number: the current raspberry number
	:param power_switch_number: the current switch number
	:param action: the valid actions are: free/busy
	:param user: the user who will lock/unlock the system
	"""

	post = 'http://10.219.106.111:2020/power/'

	LOGGER.debug(
		'the switch ({power_switch_number}) will be set to ({action}) for raspberry '
		'({raspberry_number}) by ({user})'
		.format(
			raspberry_number=raspberry_number,
			power_switch_number=power_switch_number, action=action, user=user)
	)

	data = '{post}{action}-{raspberry_number}-{power_switch_number}'\
		.format(
			post=post, action=action, raspberry_number=raspberry_number,
			power_switch_number=power_switch_number)

	payload = {'user': user}

	try:
		requests.get(data, params=payload, timeout=5)
		LOGGER.debug('the system was successfully {0}'.format(action))
	except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
		LOGGER.error('could not connect to watchdog database', exc_info=True)


def update_watchdog_db(RaspberryNumber, PowerSwitchNumber, **kwargs):
	"""Sends data to be update in the watchdog DataBase.

	The function sends a json with data to be updated in the watchdog DB. If
	a value is not included in the dictionary then it is not updated.

	:param RaspberryNumber: the raspberry number. Mandatory value.
	:param PowerSwitchNumber: the switch number. Mandatory value.
	:param kwargs: the optional values to update on the watchdog DB, some of
	the possible values are:
		- DutHostname: the hostname of the platform
		- DutIP: the IP value of the platform
		- availabilityStatus: value that controls system access to DUT
		- dutOnlineStatus: shows the DUT power status
		- attachedDisplays: the displays connected to the platform
		- Suite: the test suite running in the platform
		- Status: the status of the platform
		- CurrentTestName: the name of the test that is currently running
		- CurrentTestTime: the elapsed time
		- CurrentTestNumber: the progress of the test suite
		- PassRate: the success / fail rate of the test suite running
		- ETA: estimated time for finishing execution
	"""
	POST = 'http://10.219.106.111:2020/watchdog'
	# Build the payload based on the values received
	data_out = {
		'RaspberryNumber': str(RaspberryNumber),
		'PowerSwitchNumber': str(PowerSwitchNumber)
	}
	data_out.update(kwargs)

	# the networking-service is a special case that needs to be handled
	# separately since you cannot pass as argument a variable that includes a
	# dash in the name.
	if 'NetworkingService' in kwargs:
		data_out['networking-service'] = kwargs['NetworkingService']

	LOGGER.debug(
		'the watchdog table will be updated with the following data:\n{0}'
		.format(data_out)
	)

	# Send a POST HTTP request with the payload to the watchdog endpoint that
	# writes the DB. Print a message either if successful or not.
	try:
		requests.post(POST, json=data_out)
		LOGGER.debug('watchdog table updated successfully')

	except requests.exceptions.ConnectionError:
		LOGGER.error('could not connect to watchdog database', exc_info=True)


def cleanup_watchdog_row(RaspberryNumber, PowerSwitchNumber, **kwargs):
	"""Cleans up the data in the DB for a raspberry-switch record.

	This function is basically a wrapper that uses the update_watchdog_db
	function to clean up the data for a raspberry-switch number. Any value not
	specifically included in the kwargs will be cleaned up from the DB.
	:param RaspberryNumber: the raspberry number. Mandatory value.
	:param PowerSwitchNumber: the switch number. Mandatory value
	:param kwargs: the key and values that you want the DB to be updated with,
	all values not included here will be updated to ' ' (blank). Some of
	the possible values are:
		- DutHostname: the hostname of the platform
		- DutIP: the IP value of the platform
		- availabilityStatus: value that controls system access to DUT
		- dutOnlineStatus: shows the DUT power status
		- attachedDisplays: the displays connected to the platform
		- Suite: the test suite running in the platform
		- Status: the status of the platform
		- CurrentTestName: the name of the test that is currently running
		- CurrentTestTime: the elapsed time
		- CurrentTestNumber: the progress of the test suite
		- PassRate: the success / fail rate of the test suite running
		- ETA: estimated time for finishing execution
	"""
	# cleanup dictionary
	watchdog_update_values = {
		'BasicPassRate': ' ',
		'Blacklist': ' ',
		'Crash': ' ',
		'CurrentTestName': ' ',
		'CurrentTestNumber': ' ',
		'CurrentTestTime': ' ',
		'Distro': ' ',
		'DmesgFail': ' ',
		'DmesgWarn': ' ',
		'DutHostname': ' ',
		'DutIP': ' ',
		'DutUptime': ' ',
		'ETA': ' ',
		'Fail': ' ',
		'GfxStackCode': ' ',
		'GrubParameters': ' ',
		'Incomplete': ' ',
		'KernelBranch': ' ',
		'KernelCommit': ' ',
		'LastTestStatus': ' ',
		'OverallTime': ' ',
		'Pass': ' ',
		'PassRate': ' ',
		'Skip': ' ',
		'Status': ' ',
		'Suite': ' ',
		'TRCLink': ' ',
		'TestsToNotRun': ' ',
		'TestsToRun': ' ',
		'Timeout': ' ',
		'TotalTest': ' ',
		'Warn': ' ',
		'attachedDisplays': {},
		'dmc': ' ',
		'guc': ' ',
		'huc': ' ',
		'networking-service': ' '
	}

	# update the clean up dictionary with the data that you want to update
	watchdog_update_values.update(kwargs)

	# the networking-service is a special case that needs to be handled
	# separately since you cannot pass as argument a variable that includes a
	# dash in the name.
	watchdog_update_values['networking-service'] = (
		kwargs.get('NetworkingService', ' '))

	update_watchdog_db(
		RaspberryNumber,
		PowerSwitchNumber,
		**watchdog_update_values
	)


def get_latest_data_from_api(data_to_verify, stop=False):
	"""Check for the latest data returned from the API.

	The aim of this function is to check if the value given (usually a key
	because the API return a dictionary) exist in the latest data returned
	from the API.

	:param
		- data_to_verify: this variable is the value to check in the dictionary
		returned by the API.
		- stop: if true this will exit with 1.
	:return:
		- The value consulted (if any).
		- False: when the key to find does not exists.
	"""
	payload = {'suite': 'igt_fast_feedback'}
	url = 'http://10.219.106.111:2020/getLatestBuild'
	api_data = requests.get(url, params=payload)
	api_dict = json.loads(api_data.text)
	# converting all the elements in api_dict to ascii
	api_dict = {str(key): str(value) for key, value in api_dict.items()}

	try:
		return api_dict[data_to_verify]
	except KeyError:
		LOGGER.error('{0} : key does not exist'.format(data_to_verify))
		if stop:
			sys.exit(1)
		return False


def get_build_id_dict(stop=False, **kwargs):
	"""Update the components in the API.

	The aim of this function is to update the components in the API such as:
	- kernel commit
	- graphic stack commit.

	if some of the mentioned components already exists in the API, it will return
	a exiting build id, otherwise will return a new build id.

	:param
		- stop: if true this will exit with 1.
		- kwargs:
			- graphic_stack_code: which is the graphic stack code.
			- kernel_commit: which is the kernel commit.
			- hour: the current hour.
			- year: the current year.
			- week_number: the current work week.
			- kernel_branch: the current kernel branch.
			- suite: the current suite.
	:return:
		- A dictionary that contains the build id, this is useful for visualization.
		- False: when the API does not return a value.
	"""
	graphic_stack_code = kwargs['graphic_stack_code']
	kernel_commit = kwargs['kernel_commit']
	hour = kwargs.get('hour', '00-00-00')
	year = kwargs.get('year', '0000')
	week_number = kwargs.get('week_number', '00')
	kernel_branch = kwargs['kernel_branch']
	suite = kwargs['suite']

	payload = {
		'kernel_branch': kernel_branch,
		'kernel_commit': kernel_commit,
		'gfx_stack_code': graphic_stack_code,
		'hour': hour,
		'year': year,
		'ww': week_number,
		'suite': suite
	}

	LOGGER.debug('getting build id from API')
	url = 'http://10.219.106.111:2020/getNextBuildID'
	api_data = requests.post(url, data=payload)
	api_dict = json.loads(api_data.text)
	# converting all the elements in api_dict to ascii
	api_dict = {str(key): str(value) for key, value in api_dict.items()}

	if not api_dict:
		LOGGER.error('not dictionary was returned from the API')
		if stop:
			sys.exit(1)
		return False
	else:
		build_id_condition = 'existing' if api_dict['New'] == 'False' else 'New'
		LOGGER.debug('build id status : {0}'.format(build_id_condition))
		return api_dict


def get_workweek(timeout=1):
	"""Gets the current year and work week from a common server.

	In some cases there could be variances in the date in different systems,
	to avoid this inconsistency, a program could request the year and work week
	from a server so it gets the correct values.

	:param
		- timeout: sets time in seconds to wait for API response

	:return: a tuple with the current year and work week.
	"""
	ww_endpoint = 'http://10.64.95.35/api/BugManager/GetCurrentWW'
	try:
		resp = requests.get(ww_endpoint, timeout=timeout)
		if resp.status_code == 200:
			year_ww = resp.json().replace('"', '').split('-')
			LOGGER.debug(
				'current year: {0}, current work week: {1}'
				.format(year_ww[0], year_ww[1])
			)
			return year_ww[0].encode(), year_ww[1].encode()
		else:
			LOGGER.debug(
				'the current year and work week could not be retrieved from the '
				'endpoint {0}, it responded with status code {1}'
				.format(ww_endpoint, resp.status_code)
			)
			return None, None
	except requests.exceptions.Timeout:
		LOGGER.error(
			'the request to get the current year and work week for endpoint '
			'{0} timed out'.format(ww_endpoint)
		)
		raise RuntimeError
