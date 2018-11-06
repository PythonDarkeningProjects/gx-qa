#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2017 Felipe Ruiz  <felipe.de.jesus.ruiz.garcia@.intel.com>
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

"""Module is intended upload results with the new visualization's structure.

Files are uploaded to backup server through ssh access.
Results files are splitted and uploaded according results type.

You can find more documentation available at :
https://docs.google.com/document/d/1Hq9im0pT_OFcyu3dOtgVqLO9tGnjny72kieCT5Cuxmw
"""

import logging
import os

from common.remote_client import RemoteClient
import visualization.base_visualization as vis
from visualization.upload_results import extract_results
from visualization.upload_results import upload_files_sshkey_auth

logger = logging.getLogger(__name__)

# This variable is only use when the config.yml does not provide
# 'build_information' key or build_id information.
VIS_DEFAULT_DICT = {
	"hour": "0-00-00",
	"year": '0000',
	"ww": '000',
	"day": "Sunday",
	"build_id": '000',
}


def initialize_visualization(
	dict_vis,
	exe_type,
	platform,
	list_path_files,
	vis_flag=False):

	"""This function performs all actions to create visualization main

	:param dict_vis: visualization dict provide on config.yml
		dict_vis in key ['build_information'] looks like :

			{
				kernel_branch: drm-intel-qa
				kernel_commit: wednesday
				gfx_stack_code: '1214633856'
				hour: 8-58-34
				year: '2018'
				ww: '2'
				day: Wednesday
				build_id: '001'
				_id: 5a5629f9b895595e6551740c
				New: 'true'
			}

	:param exe_type: type IGT execution as igt_fast_feedback or igt_all
	:param platform: as KBL, APL, BXT, CNL
	:param list_path_files: list path files to copy ["/home/gfx/attachments"]
	:param vis_flag: Boolean flag that determine the name the directory results
		that will upload with the files indicated in list_path_files :

		if the flag is True directory will named such as VIS_LABEL_BUILDID_VIS :
			QA_DRM_180110001 > Taken in count to genenerate visualization htmls

		if the flag is False directory will named such as VIS_LABEL_BUILDID_NOVIS :
			MANUAL_ID__180110001 > No taken in count to genenerate visualization htmls

		flag define if the upload results are taken in count
		to generate visualization htmls.

	"""

	days_number = {
		'Monday': 1,
		'Tuesday': 2,
		'Wednesday': 3,
		'Thursday': 4,
		'Friday': 5,
		'Saturday': 6,
		'Sunday': 7
	}

	label = vis.VIS_LABEL_BUILDID_NOVIS

	if vis_flag:
		label = vis.VIS_LABEL_BUILDID_VIS

	build_id = generate_build_id(
		label,
		str(dict_vis['year'])[2:],
		str(dict_vis['ww']),
		days_number[str(dict_vis['day'])],
		str(dict_vis['build_id'])
	)

	report_path = vis.get_path_reports(exe_type)
	report_path = os.path.join(report_path, build_id, platform)

	client = RemoteClient(vis.VIS_HOST, vis.VIS_USER)
	client.makedirs(report_path)

	upload_files_sshkey_auth(
		vis.VIS_HOST,
		vis.VIS_USER,
		list_path_files,
		report_path
	)


def generate_build_id(label, year, week, day, build):
	"""This function generate a build_id string

		build_id string is a combination of label, year, week, and id
		reference for a unique combination of graphics components.

		example : QA_DRM_17524001

		label : initial str ('QA_DRM_' in the example)
		year : two digits represeting the year ('17' in the example)
		week : two digits representing the week ('52' in the example)
		day : a digit representing the day of week ('4' in the example)
		build : three digits representing id ('001' in the example)

		the build_id generated is returned
	"""

	build_id = (
		'{label}{year}{week}{day}{build}'
		.format(label=label, year=year, week=week, day=day, build=build)
	)

	return build_id


def generate_visualization(test_suite):
	"""Function calls through ssh the script that runs the visualization pages

	test_suites: suite generate in VIS_HOST (linuxgraphics.intel.com)

		IGT_TEST_SUITE_FF:
			http://linuxgraphics.intel.com/vis/igt_fast_feedback/

		IGT_TEST_SUITE_ALL:
			http://linuxgraphics.intel.com/vis/igt_all/

	return: output command
	"""

	logger.debug('starting generating visualization')
	logger.debug('logging {user}@{host}'.format(
		user=vis.VIS_USER, host=vis.VIS_HOST))

	logger.debug(
		'executing {script} {arg} in remote host'.format(
			script=vis.VIS_GEN_SCRIPT, arg=test_suite))

	client = RemoteClient(vis.VIS_HOST, vis.VIS_USER)

	# To generate visualization pages correctly,
	# extern visualization scripts must be execute from the dir.

	# Because, after add our project to PYTHONPATH, we going cd
	# to the dir visualization repo.

	# TODO(Felipe): Once extern support as module:
	#  and mako dependencies are not required exe on  the lever dir,
	# change `pre` variable with export external instead current WA

	pre = (
		'export PYTHONPATH={repo} ; '
		'cd {extern} ; '
	).format(repo=vis.VIS_GEN_SOURCE, extern=vis.VIS_GEN_EXTERN_REPO)

	out = client.run_command(
		'{pre} python3 {script} {suite}'.format(
			pre=pre, script=vis.VIS_GEN_SCRIPT, suite=test_suite),
		20)

	logger.debug('generation done > output {out}'.format(out=out))
	return out


def extract_report_to_vis(tar, dest):
	"""This function extract the json results with the name that vis needs

		tar : str path and tarfile as '/home/results.tar'
		dest : path to put the file extracted
	"""
	logger.debug('starting with json extraction')
	extract_results(
		tar,
		vis.VIS_NAME_DEFAULT_KEYWORD,
		os.path.join(dest, vis.VIS_NAME_RESULT_REPORT))
