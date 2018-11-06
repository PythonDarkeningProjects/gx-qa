"""Provide functions to interact with the Bugzilla API"""

import bugzilla

BUGZILLA_URL = 'https://bugs.freedesktop.org'


def get_bug_details(bug_id):
	"""Gets information from the requested bug from bugzilla api at FDO.

	:param bug_id: the id of the bug the user wants to retrieve info from.
		E.g. '123123'
	:return: a dictionary containing the bug info
	"""
	# establish connection with the bugzilla API, and request the bug from it
	bugzilla_api = bugzilla.Bugzilla(BUGZILLA_URL)
	bug = bugzilla_api.getbug(bug_id)

	# return the desired information from the bug
	return {
		'id': bug.id,
		'summary': bug.summary,
		'url': bug.weburl,
		'priority': bug.priority,
		'severity': bug.severity,
		'status': bug.status,
		'resolution': bug.resolution,
		'duplicate': bug.dupe_of if bug.resolution == 'DUPLICATE' else None
	}
