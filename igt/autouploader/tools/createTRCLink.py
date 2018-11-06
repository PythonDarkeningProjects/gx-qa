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

import requests
import os
import sys

from gfx_qa_tools.common import bash

main_path = '/home/shared/trcReports'
# TODO : take the hour from a internal/external server
# ============================================================================
# currently the hour is taking from the DUT but this is not the final approach
# for the following reasons :
# - in a develop platform usually a new bios is flashed every week and the
# hour from the BIOS is unconfigured and linux distros takes the hour from
# the BIOS, in a future the best approach is to take the hour from a
# internal/external server with the correct  hour
# ============================================================================
hour = bash.get_output('date +%I-%M-%S')
# ========================================================================
# for the same reason that the hour, the year and the current work week is
# being taken from an API to be more reliable.
# ========================================================================
r = str(requests.get(
	'http://10.64.95.35/api/BugManager/GetCurrentWW')
	.json()).replace('"', '').split('-')
year = r[0]
work_week = 'W' + str(r[1])


def create_trc_report(
	url, platform, environment, release, package, title, id_report):
	"""Creates a TRC link file to use with igt clones suite

	:param url: The TRC url link
	:param platform: The current system under test
	:param environment: The TRC environment value (sandbox/production)
	:param release: The TRC release value
	:param package: The current suite under test
	:param title: The title for TRC report
	:param id_report: The TRC report ID
	"""

	folder = os.path.join(
		main_path, year, work_week, environment, package,
		platform, 'release_name__' + release, 'title__' + title,
		'id__' + id_report)
	trc_link_file = os.path.join(folder, 'trc_link')

	if not os.path.exists(folder):
		bash.message(
			'info', '({0}) does not exists, creating ...'.format(folder))
		os.makedirs(folder)
	else:
		bash.message('skip', '({0}) already exists'.format(folder))

	if not os.path.isfile(trc_link_file):
		bash.message(
			'info',
			'({0}) trc_link_file does not exists, creating ...'
			.format(trc_link_file))
		os.system('echo {0} > {1}'.format(url, trc_link_file))
	else:
		bash.message('skip', '({0}) already exists'.format(trc_link_file))


if __name__ == '__main__':
	try:
		create_trc_report(
			sys.argv[1],
			sys.argv[2],
			sys.argv[3],
			sys.argv[4],
			sys.argv[5],
			sys.argv[6],
			sys.argv[7]
		)
	except IndexError:
		argument_list = [
			'url', 'platform', 'environment', 'release', 'package', 'title',
			'id_report']
		bash.message('err', 'missing arguments')
		bash.message('info', 'you must provide the following arguments')
		for element in argument_list:
			print(' - {0}'.format(element))
		sys.exit(1)
