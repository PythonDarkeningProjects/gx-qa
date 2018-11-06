"""Create htmls and generate all stuff require for visualization pages"""

import argparse
import os
import re

from gfx_qa_tools.common import log
from visualization import base_visualization as vis

# currently this source is exe as script without
logger = log.setup_logging(
	'create_visualization',
	level='debug',
	log_file='create_vis.log',
	root=True
)

# Path's where visualization pages will save
VIS_PATH_HTML = os.path.join(vis.VIS_PATH_MAIN, 'html')
VIS_PATH_HTML_FF = os.path.join(VIS_PATH_HTML, vis.IGT_TEST_SUITE_FF)
VIS_PATH_HTML_ALL = os.path.join(VIS_PATH_HTML, vis.IGT_TEST_SUITE_ALL)

# Path's/File's that scripts to creates visualization from extern repo
VIS_GEN_MAIN = os.path.join(vis.VIS_GEN_EXTERN_REPO, 'vis.py')
VIS_GEN_TEST = os.path.join(vis.VIS_GEN_EXTERN_REPO, 'vis-test-results.py')
VIS_GEN_HISTORY = os.path.join(vis.VIS_GEN_EXTERN_REPO, 'vis-history.py')

# Constant for default amount builds (columns) on pages
VIS_DEF_AMOUNT_MAIN = 5
VIS_DEF_AMOUNT_TEST = 20
VIS_DEF_AMOUNT_HIS = 20


def natural_key(string_):
	"""Function allow natural order providing a key to sorted.

	string_: string to be splitted and extract the numbers in the string
	return: tuple with values splitted containe in the string_
	"""
	return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def get_path_html(test_suite):
	"""Function provide report path according the suit

	test_suite: [igt_all | igt_fast_feedback ]
	return: str path of reports
	"""

	logger.info('argument: {}'.format(test_suite))

	report_path = os.path.join(VIS_PATH_HTML, test_suite + '/')

	logger.info('return: {}'.format(report_path))
	return report_path


def get_latest_json_reports(test_suite, amount):
	"""Provide str path list the more new json reports according the test_suite

	test_suite: string suit [ "igt_all" | "igt_fast_feedback" ]
		this parameter determine the path to search the reports

	amount: int max number the build_id in the string
	return: str the more recently path/json-reports
		Example:
		"/home/gfxserver/share/visualization/reports/igt_all/03/vis_results.json
		/home/gfxserver/share/visualization/reports/igt_all/02/vis_results.json"
	"""

	report_path = vis.get_path_reports(test_suite)
	dirs_reports = os.listdir(report_path)
	logger.info('dirs all: {}'.format(dirs_reports))

	regex = re.compile('{}*'.format(vis.VIS_LABEL_BUILDID_VIS))

	dirs_reports = filter(regex.match, dirs_reports)
	logger.info('dirs filtered: {}'.format(dirs_reports))

	dirs_reports = sorted(dirs_reports, key=natural_key, reverse=True)
	dirs_reports = dirs_reports[:amount]
	logger.info('dirs sorted:'.format(dirs_reports))

	list_json_reports = ''
	for item in dirs_reports:
		cwd = os.path.join(report_path, item)
		for root, dirs, files in os.walk(cwd):
			for current_file in files:
				if vis.VIS_NAME_RESULT_REPORT in current_file:
					list_json_reports += os.path.join(root, current_file + ' ')
					break

	logger.info('returned: {}'.format(list_json_reports))
	return list_json_reports


def create_build_dirs(test_suite):
	"""Creates build_id dirs require by visualization history and test

	test_suite: string suit [ "igt_all" | "igt_fast_feedback" ]
	this parameter determine the path to take build_id dirs
	"""

	report_path = vis.get_path_reports(test_suite)
	dirs_reports = os.listdir(report_path)
	regex = re.compile(vis.VIS_LABEL_BUILDID_VIS + '*')
	dirs_reports = filter(regex.match, dirs_reports)
	dirs_reports = sorted(dirs_reports, key=natural_key, reverse=True)
	logger.info('dirs_reports sorted: {}'.format(dirs_reports))

	if not dirs_reports:
		logger.info('no dirs to create: {}'.format(dirs_reports))
		return

	html_path = get_path_html(test_suite)

	for item in dirs_reports:
		cwd = os.path.join(html_path, item)
		if not os.path.exists(cwd):

			os.makedirs(cwd)
			logger.info('creating dir: {0}'.format(cwd))
			build_dir = os.path.join(report_path, item)
			platforms = os.listdir(build_dir)

			for elem in vis.VIS_BUILD_FILES:

				to_link = os.path.join(build_dir, platforms[0], elem[1])
				at_link = os.path.join(build_dir, elem[1])
				os.symlink(to_link, at_link)

				to_link = os.path.join(build_dir, elem[1])
				at_link = os.path.join(cwd, elem[1])
				os.symlink(to_link, at_link)

			continue

		logger.info('dir already exists: {}'.format(cwd))


def run_visualization(
	test_suite,
	amount_main=VIS_DEF_AMOUNT_MAIN,
	amount_test=VIS_DEF_AMOUNT_TEST,
	amount_his=VIS_DEF_AMOUNT_HIS):
	"""Function runs the scripts that generate visualization pages

	test_suite: suite to generate the html pages
	amount_main: amount reports to show sin the main page
	amount_test: amount reports to show in test page
	amount_his: amount reports to show in the build page
	"""

	logger.info('starting to generate visualization {}'.format(test_suite))

	if not os.path.isfile(VIS_GEN_MAIN):
		logger.warning('error doesnt exist {}'.format(VIS_GEN_MAIN))
		return -1

	if not os.path.isfile(VIS_GEN_TEST):
		logger.warning('error doesnt exist {}'.format(VIS_GEN_TEST))
		return -1

	if not os.path.isfile(VIS_GEN_HISTORY):
		logger.warning('error doesnt exist {}'.format(VIS_GEN_HISTORY))
		return -1

	create_build_dirs(test_suite)
	reports_main = get_latest_json_reports(test_suite, amount_main)
	reports_test = get_latest_json_reports(test_suite, amount_test)
	reports_his = get_latest_json_reports(test_suite, amount_his)

	to_exe = ' python3 {} -o {} {}'

	base = get_path_html(test_suite)
	base_index = os.path.join(base + 'index.html')

	exe_ind = to_exe.format(VIS_GEN_MAIN, base_index, reports_main)
	exe_test = to_exe.format(VIS_GEN_TEST, base, reports_test)
	exe_his = to_exe.format(VIS_GEN_HISTORY, base, reports_his)

	os.system(exe_ind)
	logger.info('vis.py: {}'.format(exe_ind))

	os.system(exe_test)
	logger.info('vis-test: {}'.format(exe_test))

	os.system(exe_his)
	logger.info('vis-his: '.format(exe_his))


# generate visualization
if __name__ == '__main__':
	# This blocked is use as script to create visualization pages.

	# This script is intended to be execute on VIS_HOST (linuxgraphics)

	# This script will be called by a DUT through ssh:
	# from generate_visualization()

	# This script needs of other sources outside gfx-qa-tools repository

	# For now, these external sources are designed
	# to run as script with parameters.

	# Them are unsoportable to import and use it as module

	# Thinking in the current structure and the coming refactor for these script:
	# This call these scripts with parameters in the host.
	# Once these are able to import as module, the current process allows use them

	# test_suites is received as parameter parse by argparse
	# It is use to generate only the suite needed

	# configure logger from this level
	# Logger is generate in this lever because this block runs directly as script
	# without parents to use an existing logger.

	# TODO(Felipe): if suit is not receive as argument generate all suites
	# (VIS_SUITE)

	ap = argparse.ArgumentParser(description='Generate visualization')
	ap.add_argument('suites', type=str, help='Suites to generate')

	args = ap.parse_args()

	test_suite = args.suites
	logger.debug('create_visualization.py {}'.format(test_suite))

	run_visualization(test_suite)
