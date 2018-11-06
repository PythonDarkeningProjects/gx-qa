#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2018 Humberto Perez <humberto.i.perez.rodriguez@.intel.com>
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

"""Module vision

Module focus: it is aimed but it is not limited for executing in terminal with
arguments, this also can be import as module from another scripts.

Module objective : to have always up-to-date the reports in linuxgraphics.

When a report from linuxgraphics will be out-to-date?

Usually after an automated execution the folks in charge of checking bugs they
will execute the failed tests in order to decrease the fails for the automated
execution and thus be able to have the best metrics.
After this step they get an csv that differs to the one in the report of
linuxgraphics.

How to keep always up-to-date linuxgraphics?

The way to accomplish this is to run this module as script in terminal after
the manual execution will be finished.

e.g:
	python <script.py> --url <url> --csv <file.csv>

How to works this module?

Basically this will generate a new HTML folder in linxgraphics server with the
results from the csv file provided.
"""

import argparse
from argparse import RawDescriptionHelpFormatter
import csv
import json
import os
import sys

import requests

from common import remote_client
from gfx_qa_tools.common import bash
from gfx_qa_tools.common import log
from gfx_qa_tools.config import config


OUTPUT_DIR = '/tmp'
JSON_UNCOMPRESSED_NAME = 'results.json'
JSON_COMPRESSED_NAME = 'results.json.tar.gz'
LINUXGRAPHICS_REPORTS_PATH = '/var/www/html/reports/intel-gpu-tools'
LINUXGRAPHICS_BASE_URL = 'http://linuxgraphics.intel.com/igt-reports'


# getting configurations from config.ini of linuxgraphics.
LINUXGRAPHICS_USER = config.get('linuxgraphics', 'user')
LINUXGRAPHICS_IP = config.get('linuxgraphics', 'ip')
LINUXGRAPHICS_CNAME = config.get('linuxgraphics', 'cname')

# logger setup
LOG_FILENAME = 'synchronize_linuxgraphics.log'
LOG_PATH = config.get('igt', 'log_path')
LOGGER = log.setup_logging(
	'synchronize_linuxgraphics', level='debug',
	log_file='{path}/{filename}'.format(path=LOG_PATH, filename=LOG_FILENAME))


def check_an_url_from_linuxgraphics(url):
	"""Check if an url exists.

	The aim of this function is to check if an a specified url exists.

	:param url: this url must correspond to one from
	http://linuxgraphics.intel.com/igt-reports.
	"""

	try:
		requests.get(url, timeout=5)
	except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
		LOGGER.error('could not connect to linuxgraphics')
		sys.exit(1)
	else:
		LOGGER.info('the url provided was verified successfully')

	if LINUXGRAPHICS_BASE_URL not in url:
		LOGGER.error('the url provided does not correspond to : {0}'.format(
			LINUXGRAPHICS_BASE_URL))
		sys.exit(1)


def clean_workspace():
	"""Clean the workspace in order to avoid any kind of issues"""

	LOGGER.info('cleaning the workspace')

	to_delete_list = ['{0}*'.format(JSON_UNCOMPRESSED_NAME), 'html']

	for item in to_delete_list:
		item_to_delete = os.path.join(OUTPUT_DIR, item)

		code, stdout = bash.run_command('rm -rf {0}'.format(item_to_delete))

		if code:
			LOGGER.error('{0} : could not be deleted'.format(item_to_delete))
			sys.exit(1)
		else:
			LOGGER.debug('{0} : was deleted successfully'.format(item_to_delete))


def download_json_file_from_linuxgraphics(url):
	"""Download a json file from linuxgraphics.

	The aim of this function is to download a json file from linuxgraphics
	from a specific url.

	:param url: the url to linuxgraphics.
	"""

	json_output_dir = os.path.join(OUTPUT_DIR, JSON_COMPRESSED_NAME)
	url_path = url.split('igt-reports')[1]

	json_remote_file = '{base_path}{path}/{json}'.format(
		base_path=LINUXGRAPHICS_REPORTS_PATH, path=url_path,
		json=JSON_COMPRESSED_NAME)

	if not remote_client.RemoteClient(
		user=LINUXGRAPHICS_USER, host_ip=LINUXGRAPHICS_IP
	).isfile(json_remote_file):
		LOGGER.error('{json} : does not exists in {cname}'.format(
			json=os.path.join(url, JSON_COMPRESSED_NAME),
			cname=LINUXGRAPHICS_CNAME))

	LOGGER.info('downloading : {0}'.format(JSON_COMPRESSED_NAME))
	params = '--no-check-certificate --directory-prefix={dir}'.format(
		dir=OUTPUT_DIR)

	code, stdout = bash.run_command(
		'wget {params} {url}/{json}'.format(
			params=params, url=url, json=JSON_COMPRESSED_NAME)
	)

	if code:
		LOGGER.error('{url}/{json} : could not be downloaded'.format(
			url=url, json=JSON_COMPRESSED_NAME))
		LOGGER.info('{0}'.format(stdout))
		sys.exit(1)

	json_location_after_unzipping = bash.get_output('tar -tzf {json}'.format(
		json=json_output_dir))
	LOGGER.info('unzipping : {0}'.format(JSON_COMPRESSED_NAME))

	# decompressing the json file
	cmd = 'tar -C {output_dir} -xvf {json_output_dir}'.format(
		output_dir=OUTPUT_DIR, json_output_dir=json_output_dir)

	code, stdout = bash.run_command(cmd)

	if code:
		LOGGER.error('{0} : could not be decompressed'.format(json_output_dir))
		LOGGER.info(stdout)
		sys.exit(1)

	# moving the json to output_dir
	cmd = 'mv {decompressed_json} {output_dir}'.format(
		decompressed_json=os.path.join(OUTPUT_DIR, json_location_after_unzipping),
		output_dir=OUTPUT_DIR)

	code, stdout = bash.run_command(cmd)

	if code:
		LOGGER.error(
			'an error was occurred trying to moving the decompressed json file to : {0}'
			.format(OUTPUT_DIR)
		)
		sys.exit(1)

	LOGGER.info('{url}/{json} : was downloaded and decompressed into /tmp'.format(
		url=url, json=JSON_COMPRESSED_NAME))


def check_piglit():
	"""Check for piglit repository in the system.

	The aim of this function is to check if the piglit repository in the current
	system exists, otherwise this will clone it into OUTPUT_DIR.
	Piglit is used to generate the HTML folder and this does not need to be
	compiled for that.

	:return: the path to the piglit binary.
	"""

	# setting git flag to avoid issues during cloning some repository.
	os.environ['GIT_SSL_NO_VERIFY'] = '1'

	piglit_folder = None
	piglit_url = 'https://anongit.freedesktop.org/git/piglit.git'

	# in the following nested loop, is necessary to break them all because
	# piglit folder also will be present in the system cache and we want for
	# piglit repository in order to use it.
	try:
		for root, dirs, files in os.walk('/'):
			for folder in dirs:
				if folder == 'piglit':
					if 'src' not in os.path.join(root, folder):
						if os.path.isfile(os.path.join(root, folder, 'piglit')):
							piglit_folder = os.path.join(root, folder)
							raise StopIteration()
	except StopIteration:
		pass

	if not piglit_folder:
		LOGGER.info(
			'no piglit folder was detected in the system, downloading it into : {0}'
			.format(OUTPUT_DIR)
		)
		cmd = 'git -C {output_dir} clone {url}'.format(
			output_dir=OUTPUT_DIR, url=piglit_url)
		code, stdout = bash.run_command(cmd)

		if code:
			LOGGER.error('piglit repository could not be downloaded')
			LOGGER.info(stdout)
			sys.exit(1)
		piglit_folder = os.path.join(OUTPUT_DIR, 'piglit')

	piglit_binary = os.path.join(piglit_folder, 'piglit')

	return piglit_binary


def update_json_results(trc_csv_file):
	"""Update JSON_UNCOMPRESSED_NAME results.

	Function objective: to update specific keys/values of the downloaded json
	file with the results in the csv file provided for later generate a new HTML
	folder with visual results in order to upload it to linuxgraphics.

	What is the JSON_UNCOMPRESSED_NAME?

	- JSON_UNCOMPRESSED_NAME is the json file downloaded from linuxgraphics.
	This file is generated by piglit and it contains all the results related
	to intel-gpu-tools execution.

	:param trc_csv_file: which is the csv file downloaded from TestReportCenter.
	"""

	csv_results_dict = dict()
	passed_tests = 0
	skip_tests = 0
	fail_tests = 0
	incomplete_tests = 0
	dmesg_warn_tests = 0
	timeout_tests = 0
	dmesg_fail_tests = 0
	warn_tests = 0
	notrun_tests = 0
	crash_tests = 0

	# Rationale to check pass/fail in result and not in comment:
	# - Because pass/fail status are valid for piglit and not need to be filtered,
	# e.g : TestReportCenter only accepts "not run"/pass/fail and in "not run"
	# status the csv can include all the other possibles status in comment column
	# valid for piglit such as: skip, fail, incomplete, dmesg-warn, timeout,
	# dmesg-fail, warn, notrun and crash

	with open(trc_csv_file, 'r') as csv_file:
		spam_reader = csv.reader(csv_file)
		for row in spam_reader:
			test_case = row[1]
			result = row[2]
			comment = row[4]
			if test_case.startswith('igt@'):
				if 'pass' in result:
					passed_tests += 1
					result = 'pass'
				elif 'fail' in result and 'fail' in comment:
					# re for this
					fail_tests += 1
					result = 'fail'
				elif 'skip' in comment:
					skip_tests += 1
					result = 'skip'
				elif 'incomplete' in comment:
					incomplete_tests += 1
					result = 'incomplete'
				elif 'dmesg-warn' in comment:
					dmesg_warn_tests += 1
					result = 'dmesg-warn'
				elif 'timeout' in comment:
					timeout_tests += 1
					result = 'timeout'
				elif 'dmesg-fail' in comment:
					dmesg_fail_tests += 1
					result = 'dmesg-fail'
				elif 'warn' in comment:
					warn_tests += 1
					result = 'warn'
				elif 'notrun' in comment:
					incomplete_tests += 1
					result = 'notrun'
				elif 'crash' in comment:
					incomplete_tests += 1
					result = 'crash'

				csv_results_dict[test_case] = result

	totals_dict = {
		'pass': passed_tests,
		'skip': skip_tests,
		'fail': fail_tests,
		'incomplete': incomplete_tests,
		'dmesg-warn': dmesg_warn_tests,
		'timeout': timeout_tests,
		'dmesg-fail': dmesg_fail_tests,
		'warn': warn_tests,
		'notrun': notrun_tests,
		'crash': crash_tests
	}

	# loading data from the downloaded json file from linuxgraphics.
	with open(os.path.join(OUTPUT_DIR, JSON_UNCOMPRESSED_NAME), 'r') as json_file:
		json_data = json.loads(json_file.read())

	json_tests = json_data['tests']
	# updating the totals in the json file (JSON_UNCOMPRESSED_NAME).
	json_data['totals'][''] = totals_dict
	json_data['totals']['igt'] = totals_dict
	json_data['totals']['root'] = totals_dict

	# updating json_tests dict
	not_in_json = 0
	for csv_test_case, csv_result in csv_results_dict.items():
		try:
			if csv_result != json_tests[csv_test_case]['result'].encode('utf-8'):
				json_tests[csv_test_case]['result'] = csv_result
		except KeyError:
			# the script could be enter to this condition if the csv provided
			# does not belong to the report in linuxgraphics, eg:
			# csv from BDW DUT and url from CNL DUT
			LOGGER.error('{test} : not in results.json'.format(test=csv_test_case))
			not_in_json += 1

	if not_in_json:
		LOGGER.error('{0} : are not in results.json'.format(not_in_json))
		LOGGER.error(
			'the CSV does not seem belong to the url provided, please check it'
		)
		sys.exit(1)

	# updating tests key
	json_data['tests'] = json_tests

	# overwriting the JSON_UNCOMPRESSED_NAME
	with open(os.path.join(
		OUTPUT_DIR, JSON_UNCOMPRESSED_NAME), 'w+') as output_json:
		output_json.write(json.dumps(json_data, indent=4, sort_keys=True))

	LOGGER.info('{json} : was updated with the values from : {csv}'.format(
		json=JSON_UNCOMPRESSED_NAME, csv=trc_csv_file))


def generate_local_html_folder(piglit_binary):
	"""Generate a local HTML folder.

	Function objective: to generated a local HTML folder for later
	uploaded to linuxgraphics.

	What is the HTML folder for?
	- The HTML folder is generated by piglit from a json file after an
	intel-gpu-tools execution finished, this folder contains all the results
	in a visual content in HTML web pages.

	:param piglit_binary: which is the path to piglit binary.
	"""

	cmd = 'python {piglit} summary html {output_folder} {input_folder}'.format(
		piglit=piglit_binary,
		output_folder=os.path.join(OUTPUT_DIR, 'html'),
		input_folder=os.path.join(OUTPUT_DIR, JSON_UNCOMPRESSED_NAME))

	LOGGER.info('generating HTML folder')

	code, stdout = bash.run_command(cmd)

	if code:
		LOGGER.error('could not generate HTML folder')
		LOGGER.error(stdout)
		sys.exit(1)

	LOGGER.info('HTML folder was generated successfully')


def delete_remote_content(content_to_delete):
	"""Delete remote content in linuxgraphics

	The aim of this function is to delete the remote HTML folder in
	linuxgraphics for later upload the new one generated by module.

	:param content_to_delete: the absolute path to the content to be delete.
	"""

	cmd = 'rm -rf {0}'.format(content_to_delete)

	code, stdout = remote_client.RemoteClient(
		user=LINUXGRAPHICS_USER, host_ip=LINUXGRAPHICS_IP
	).run_command(cmd)

	if code:
		LOGGER.error('could not be deleted remote content : {0}'.format(
			content_to_delete))
		sys.exit(1)

	LOGGER.info('{0} : remote content was deleted successfully'.format(
		os.path.basename(content_to_delete)))


def upload_local_content(local_content, remote_folder):
	"""Upload local content to linuxgraphics

	The aim of this function is to upload a local content to linuxgraphics
	in order to get up-to-date the information.

	:param local_content: the local content to be uploaded.
	:param remote_folder: the remote folder to upload the local content.
	"""

	LOGGER.info('uploading : {0}'.format(local_content))

	cmd = 'scp -r {local_content} {user}@{ip}:{remote_folder}'.format(
		local_content=local_content, user=LINUXGRAPHICS_USER, ip=LINUXGRAPHICS_IP,
		remote_folder=remote_folder)

	code, stdout = bash.run_command(cmd)

	if code:
		LOGGER.error(
			'an error was occurred trying to upload local content : {0}'.format(
				local_content))
		sys.exit(1)

	LOGGER.info(
		'the local content ({local_content}) was successfully uploaded to : {server}'
		.format(local_content=local_content, server=LINUXGRAPHICS_CNAME)
	)


def retrieving_remote_filename(remote_folder, regex):
	"""Retrieve a remote filename with regex.

	This function will return only one filename with the regex given, if there
	is more than 2 files retrieved from the remote system this will stops the
	module execution.

	:param remote_folder: the remote folder to check if exists the file to
	retrieve.
	:param regex: the regex to check a specific file in a remote system.
	:return: the filename matched with the regex.
	"""
	cmd = 'ls {remote_folder} | grep "{regex}"'.format(
		remote_folder=remote_folder, regex=regex)

	code, stdout = remote_client.RemoteClient(
		user=LINUXGRAPHICS_USER, host_ip=LINUXGRAPHICS_IP
	).run_command(cmd)

	if code:
		LOGGER.error('could not retrieve any file with the regex : {0}'.format(
			regex))
		sys.exit(1)

	if len(stdout.split()) > 1:
		LOGGER.error('more than one file was retrieved')
		for filename in stdout.split():
			LOGGER.error(filename)
		LOGGER.error('please check the regex : {0}'.format(regex))
		sys.exit(1)

	return stdout


def create_remote_control_file(url):
	"""Create a remote control file.

	The aim of this function is to create a remote control file in
	linuxgraphics server in order to know exactly if the HTML folder of an
	intel-gpu-tools execution was updated with the values from TestReportCenter.

	:param url: this url must correspond to one from
	http://linuxgraphics.intel.com/igt-reports.
	"""

	url_path = url.split('igt-reports')[1]

	remote_folder = '{base_path}{path}'.format(
		base_path=LINUXGRAPHICS_REPORTS_PATH, path=url_path)

	cmd = 'touch {0}/html_folder_was_synchronized'.format(remote_folder)

	code, stdout = remote_client.RemoteClient(
		user=LINUXGRAPHICS_USER, host_ip=LINUXGRAPHICS_IP
	).run_command(cmd)

	if code:
		LOGGER.error('remote control file could not be created')
		sys.exit(1)

	LOGGER.info('remote control file was created successfully')


def orchestrator(args):
	"""Managing the flow of this module.

	The aim of this function is to operate the correct flow of this module
	calling functions in order to synchronize the results between TestReportCenter
	and our internal server linuxgraphics.

	This script is directed to use in the DUTs connected to the automated system
	since we can not declared the password for our server in a script.

	:param args: The possible values are:
		- args.url: which is the url comes from linuxgraphics.
		- args.csv: which is the csv comes from TestReportCenter (the new one
		updated with the manual third iteration performed by the folks in charge
		to report bugs in https://bugs.freedesktop.org)
	"""
	# calling the functions step by step.

	# checking if the csv file provided exists in the system.
	if not os.path.isfile(args.csv):
		LOGGER.error('{csv} : does not exists'.format(csv=args.csv))
		sys.exit(1)

	# deleting the latest character (if any) in the url if this ends with
	# backslash.
	if args.url.endswith('/'):
		args.url = args.url.rstrip('/')

	url_path = args.url.split('igt-reports')[1]

	local_html_folder = os.path.join(OUTPUT_DIR, 'html')
	remote_folder = '{base_path}{path}'.format(
		base_path=LINUXGRAPHICS_REPORTS_PATH, path=url_path)
	html_remote_folder = '{base_path}{path}/html'.format(
		base_path=LINUXGRAPHICS_REPORTS_PATH, path=url_path)
	# getting the remove csv filename in linuxgrahics.
	remote_csv_filename = retrieving_remote_filename(remote_folder, 'TRC_summary')

	check_an_url_from_linuxgraphics(args.url)
	clean_workspace()
	download_json_file_from_linuxgraphics(args.url)
	piglit_binary = check_piglit()
	update_json_results(args.csv)
	generate_local_html_folder(piglit_binary)
	# deleting remote HTML folder.
	delete_remote_content(html_remote_folder)
	# uploading local HTML folder.
	upload_local_content(local_html_folder, remote_folder)
	# deleting remote csv file (this file is out-to-date).
	delete_remote_content(os.path.join(remote_folder, remote_csv_filename))
	# renaming the local csv before to upload it to linuxgraphics.
	new_csv_filename = os.path.join(
		os.path.dirname(args.csv), remote_csv_filename)
	os.rename(args.csv, new_csv_filename)
	# uploading local csv file (this file is up-to-date).
	upload_local_content(new_csv_filename, remote_folder)
	create_remote_control_file(args.url)


def arguments():
	parser = argparse.ArgumentParser(
		formatter_class=RawDescriptionHelpFormatter,
		description='''
	program description:
	(%(prog)s) is a tool for synchronize TRC results with the ones in
	linuxgraphics.intel.com
	project : https://01.org/linuxgraphics
	maintainer : humberto.i.perez.rodriguez@intel.com''',
		epilog='Intel® Graphics for Linux* | 01.org',
		usage='%(prog)s [options]')

	group = parser.add_argument_group(
		'{0}mandatory arguments{1}'.format(bash.BLUE, bash.END))
	group.add_argument(
		'-u', '--url',
		dest='url', required=True,
		help='The url for the report to be updated from '
		'http://linuxgraphics.intel.com'
	)
	group.add_argument(
		'-c', '--csv',
		dest='csv', required=True,
		help='The CSV file for update the HTML folder in '
		'http://linuxgraphics.intel.com'
	)

	args = parser.parse_args()

	orchestrator(args)


if __name__ == '__main__':
	arguments()
