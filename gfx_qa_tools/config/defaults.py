"""Default configuration values used when generating a new config file

Variables that are between %(option)s are interpolated automatically by the
ConfigParser (with the caveat that they have to be in the same section).

Variables that are between ${section:option} will be interpolated with the
value from the appropriate section (similar to the way configparser from
Python3 works).
"""


def load_defaults(config):
	"""All config default values are defined here"""

	# General Section
	config.add_section('general')
	config.set('general', 'log_path', '/home/shared/logs')

	# Watchdog section
	config.add_section('watchdog')
	config.set('watchdog', 'log_path', '${general:log_path}/watchdog')
	config.set('watchdog', 'log_level', 'debug')
	config.set('watchdog', 'email_sender', 'watchdog@noreply.com')
	config.set('watchdog', 'dut_api', 'http://{ip}:4040/statistics')
	config.set('watchdog', 'connection_timeout', '11')
	config.set('watchdog', 'dut_api_timeout', '20')
	config.set('watchdog', 'nodata_timeout', '10')
	config.set('watchdog', 'ping_timeout', '150')
	config.set('watchdog', 'test_timeout', '11')
	config.set('watchdog', 'no_url_timeout', '5')
	config.set('watchdog', 'consecutive_reboots_allowed', '3')
	config.set('watchdog', 'wait_between_cycles', '1')

	# API section
	config.add_section('api')
	config.set('api', 'server', '10.219.106.111')
	config.set('api', 'port', '2020')
	config.set('api', 'watchdog_endpoint', '%(server)s:%(port)s/watchdog')

	# Raspberry section
	config.add_section('raspberry')
	config.set('raspberry', 'log_path', '${general:log_path}/raspberry')
	config.set('raspberry', 'clonezilla_file_timeout', '10')

	# IGT section
	config.add_section('igt')
	config.set('igt', 'report_generation_timeout', '5')
	config.set('igt', 'log_path', '/home/custom/logs')

	# linuxgraphics.intel.com section
	config.add_section('linuxgraphics')
	config.set('linuxgraphics', 'ip', '10.219.106.67')
	config.set('linuxgraphics', 'user', 'gfxserver')
	config.set('linuxgraphics', 'report_tool_user', 'guest')
	config.set('linuxgraphics', 'cname', 'linuxgraphics.intel.com')
	config.set(
		'linuxgraphics', 'vis_reports_path',
		'/home/gfxserver/share/visualization/reports')

	# <Add sections here!>

	return config
