#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2017
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

"""Provides different utility functions."""

import logging
import os
import socket
import time

from gfx_qa_tools.common import bash

logger = logging.getLogger(__name__)


def get_ip():
	"""Gets the IP address of the host."""
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
	except socket.error:
		ip = ''
	else:
		ip = s.getsockname()[0]
	finally:
		s.close()
	return ip


def set_proxy(ip=None):
	"""Automatically sets or unsets the proxy configuration.

	The method will set or remove the environment variables related to
	proxies depending on if the IP provided falls within the INTRANET range
	(10.X.X.X) or SEDLINE range (192.168.X.X). This is useful because the hosts
	that are connected to the sedline already have internet connection while those
	in the intranet need some proxy configuration.

	:param ip: the ip address of the host
	:return: it configures the proxy settings but does not return anything.
	"""
	if not ip:
		ip = get_ip()
		# if there was a failure getting the ip just return False
		if not ip:
			return False
	if ip.startswith('192.168.'):
		# If the IP is from the public IP range unset proxies
		proxies_list = [
			'ALL_PROXY',
			'all_proxy',
			'http_proxy',
			'https_proxy',
			'ftp_proxy',
			'socks_proxy',
			'no_proxy']

		for element in proxies_list:
			if element in os.environ:
				del os.environ[element]
	else:
		# intranet connection (setting proxies)
		proxy_list = {
			'ALL_PROXY': 'socks://proxy-socks.fm.intel.com:1080',
			'all_proxy': 'socks://proxy-socks.fm.intel.com:1080',
			'http_proxy': 'http://proxy.fm.intel.com:911',
			'https_proxy': 'https://proxy.fm.intel.com:912',
			'ftp_proxy': 'ftp://proxy.fm.intel.com:911',
			'socks_proxy': 'socks://proxy-socks.fm.intel.com:1080',
			'no_proxy': 'localhost,.intel.com,127.0.0.0/8,192.168.0.0/16,10.0.0.0/8'
		}
		for k, v in proxy_list.items():
			os.environ[k] = v

		if not bash.get_output('env | grep -i proxy'):
			os.system('clear')
			bash.center_message(
				'\n{0}err:{1} (unable to configure proxies settings)\n'
				.format(bash.RED, bash.END))
			bash.exit_message(
				bash.center_message(
					'\n{0}please configure the proxies in your local bashrc{1}\n'
					.format(bash.YELLOW, bash.END)))

	return True


def ping_system(system, timeout=10, output=True):
	"""Pings a system.

	:param system: IP address or hostname of the system to be pinged
	:param timeout: the timeout in seconds by default provided by -C param
	in ping command
	:param output: shows the command output
	:return: True if the system responds to the ping, False otherwise
	"""
	logger.debug('pinging {0} ...'.format(system))
	# Ping the system
	cmd = (
		'ping -W {timeout} -c 1 {system}'
		.format(system=system, timeout=timeout) if output else
		'ping -W {timeout} -c 1 {system} > /dev/null 2>&1'
		.format(system=system, timeout=timeout))

	response = os.system(cmd)

	# Check the response return code
	if response == 0:
		logger.debug('{0} responded to ping successfully'.format(system))
		return True
	else:
		logger.debug('no response to ping from {0}'.format(system))
		return False


def wait_for_ping(system, timeout):
	"""Pings a system until it responds.

	The function pings a system until the system pings back or until the timeout
	is reached.

	:param system: IP or hostname of the system to be pinged
	:param timeout: the time frame in seconds in which the function will keep
	trying to ping the system
	:return: True if the system responds to the ping within the timeout, False
	otherwise
	"""
	logger.debug(
		'the system {0} will be pinged for up to {1} seconds'
		.format(system, timeout))
	# Initialize the start time
	start_time = time.time()

	# Keep trying to ping until it responds or the timeout is reached
	while True:

		if ping_system(system):
			return True
		if time.time() > (start_time + timeout):
			logger.debug(
				'the system {system} did not respond to ping within the timeout'
				' of {timeout} seconds'
				.format(system=system, timeout=timeout)
			)
			return False
