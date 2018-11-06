"""GLOBAL CONSTANTS AND FUNCTIONS FOR VISUALIZATION"""

import logging
import os

logger = logging.getLogger(__name__)

IGT_TEST_SUITE_ALL = 'igt_all'
IGT_TEST_SUITE_FF = 'igt_fast_feedback'

VIS_LABEL_BUILDID_VIS = 'QA_DRM_'
VIS_LABEL_BUILDID_NOVIS = 'MANUAL_ID_'

VIS_HOST = 'linuxgraphics.intel.com'
VIS_USER = 'gfxserver'

VIS_PATH_BASE = '/home/{user}/share/'.format(user=VIS_USER)
VIS_PATH_MAIN = os.path.join(VIS_PATH_BASE, 'visualization')

# Path's of external python scripts repositorie that creates visualization
VIS_GEN_EXTERN_REPO = os.path.join(VIS_PATH_MAIN, 'source', 'vis')

VIS_PATH_REPORTS = os.path.join(VIS_PATH_MAIN, 'reports')
VIS_PATH_REPORTS_FF = os.path.join(VIS_PATH_REPORTS, IGT_TEST_SUITE_FF)
VIS_PATH_REPORTS_ALL = os.path.join(VIS_PATH_REPORTS, IGT_TEST_SUITE_ALL)

VIS_GEN_SOURCE = os.path.join(VIS_PATH_BASE, 'gfx-qa-tools')
VIS_GEN_SCRIPT = os.path.join(
	VIS_GEN_SOURCE,
	'visualization',
	'create_visualization.py '
)

VIS_NAME_DEFAULT_KEYWORD = 'results'
VIS_NAME_RESULT_REPORT = 'vis_results.json'

# TODO(CONFIGURATE ARGUMENTS ON EXTERN MAKO TEMPLATES:
# TO INDICATE FILES ON TEST AND MAKE IT AVAILABLE TO DOWNLOAD )
VIS_BUILD_FILES = [
	('..', 'gfx_stack.cfg'),
	('..', 'gfx_stack_easy_bugs.cfg'),
	('..', 'kernel_commit_information.cfg'),
]


def get_path_reports(test_suite):
	"""Function provide report path according the suit

	test_suite: [igt_all | igt_fast_feedback ]
	return: str path of reports
	"""
	logger.debug('argument: {arg}'.format(arg=test_suite))
	report_path = os.path.join(VIS_PATH_REPORTS, test_suite)

	logger.debug('return: {out}'.format(out=report_path))

	return report_path
