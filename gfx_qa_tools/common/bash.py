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

"""Manages execution of bash commands.

Executes bash commands in the underlying system and formats the output
in a consistent manner.

The functions that belong to this package are the ones that meet this criteria:
- All those that rely on running a command in the shell (bash) to work.
- All those related to printing/formatting messages for the console.
- This module should only include functions that are not related with a
specific application.

Note: Since a lot of functions in this package need to run a in a shell, this
package should most of the times only be used in Linux.
"""

from __future__ import print_function

import logging
import re
import subprocess
import sys

LOGGER = logging.getLogger(__name__)

# Defines a color schema for messages.
PURPLE = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
GREY = '\033[90m'
BLACK = '\033[90m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
DEFAULT = '\033[99m'
END = '\033[0m'


# -------------------------------------------
# Functions for running commands in the shell
# -------------------------------------------

# TODO(Cas): rename this function to something that makes more sense,
# for example run_in_shell()
def get_output(cmd, print_output=None):
	"""Runs a shell command in the host without validating execution.

	This function executes the shell command provided, prints (if enabled) and
	returns its output. This function does not validate successful command
	execution in any way. If the command fails to run the output will just be
	empty.
	:param cmd: the command to be executed in the shell
	:param print_output: if True, the function will print the command output
	(if any), if False, then the function is executed silently
	:return: the output of the executed command
	"""
	proc = subprocess.Popen(
		cmd, stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
	out, _ = proc.communicate()
	out = out.strip()
	if print_output:
		print(out)
	return out


def run_command(command):
	"""Runs a shell command in the host.

	:param command: the command to be executed
	:return: a tuple that contains the exit code of the command executed,
	and the output message of the command.
	"""
	proc = subprocess.Popen(
		command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
		executable='/bin/bash')
	output, error = proc.communicate()
	output = output.strip() if output else output
	error = error.strip() if error else error
	return proc.returncode, error or output


# TODO(Cas): rename this function to something that makes more sense
def check_output(cmd, message_done, message_fail, print_messages=True):
	"""Runs a command and validates its correct execution.

	The function runs a command in the shell and generates a SystemExit exception
	if the command fails to execute. The function also prints user defined
	messages depending on the success/failure of the command execution.
	:param cmd: the command to run
	:param message_done: the message to show if the command is successful
	:param message_fail: the message to show if the command fails
	:param print_messages: if set to False, the messages are silenced
	:return: raises a SystemExit exception on command failure
	"""
	exit_code, _ = run_command(cmd)

	if not exit_code:
		if print_messages:
			message('ok', message_done)
		else:
			LOGGER.debug(message_done)
	else:
		if print_messages:
			message('err', message_fail)
		else:
			LOGGER.error(message_fail)
		raise SystemExit(1)


# TODO(Cas): rename this function to something that makes more sense
def return_command_status(cmd, print_messages=True):
	"""Runs a command and validates its correct execution.

	The function runs a command in the shell and generates a SystemExit
	exception
	if the command fails to execute. The function also prints either DONE or
	FAIL
	to the console depending on the success/failure of the command execution.
	:param cmd: the command to be executed
	:param print_messages: if set to False, the messages are silenced
	:return: raises a SystemExit exception on command failure
	"""
	exit_code, _ = run_command(cmd)

	if not exit_code:
		if print_messages:
			print(' ... [' + GREEN + 'DONE' + END + ']')
	else:
		if print_messages:
			print(' ... [' + RED + 'FAIL' + END + ']')
		raise SystemExit(1)


# --------------------------------------------------------
# Functions for printing formatted messages in the console
# --------------------------------------------------------

def message(message_type, msg, end_string=None):
	"""Wrapper that provides format to messages based on message type.

	The function prints messages of the following type:
	'>>> (success) hello world'
	'>>> (err) bye bye world'

	:param message_type: specifies the type of message
	:param msg: the message to be formatted
	:param end_string: specifies a different character to end the
	message, if None is specified it uses a newline
	"""
	if message_type == 'err':
		print(RED + '>>> (err) ' + END + msg, end=end_string)
	elif message_type == 'warn':
		print(YELLOW + '>>> (warn) ' + END + msg, end=end_string)
	elif message_type == 'info':
		print(BLUE + '>>> (info) ' + END + msg, end=end_string)
	elif message_type == 'ok':
		print(GREEN + '>>> (success) ' + END + msg, end=end_string)
	elif message_type == 'statistics':
		print(CYAN + '>>> (data) ' + END + msg, end=end_string)
	elif message_type == 'cmd':
		print(CYAN + '>>> (cmd) ' + END + msg, end=end_string)
	elif message_type == 'skip':
		print(
			BLUE + '>>> (info) ' + END + msg + ' ... [' + YELLOW + 'SKIP' + END + ']',
			end=end_string)
	else:
		raise ValueError('Invalid argument.')


def center_message(msg):
	"""Wrapper that prints a message centered in the terminal.

	The function prints messages of the following type:
	'                 hello world                  '

	:param msg: the message to be printed
	"""
	return_code, output = run_command('stty size')
	terminal_width = int(output.split()[1]) if return_code == 0 else 0
	print(msg.center(terminal_width))


# TODO(Cas): this function may not be needed since it is only a one liner
# also currently it is only being called 3 times
def exit_message(msg=''):
	"""Prints a message in the terminal and exits the program.

	:param msg: the message to be printed when exiting
	"""
	raise SystemExit(msg)


# ---------------------------------------------
# Functions that rely on running shell commands
# ---------------------------------------------

def is_process_running(process, pid_to_exclude=''):
	"""Checks if a process is running.

	:param process: the process to check. This can either be a PID or the
	command used to start the process
	:param pid_to_exclude: int values are accepted only. If this param is set,
	this function will exclude the pid on this variable.
	:return:
		True: if the process is still running.
		False: if the process has finished (was not found)
	"""
	ps_aux = subprocess.Popen(['ps', 'axw'], stdout=subprocess.PIPE)
	for element in ps_aux.stdout:
		if re.search(process, element.decode('utf-8')):
			pid = int(element.split()[0])
			if pid_to_exclude and pid == pid_to_exclude:
				continue
			else:
				return True
	return False


def disable_cups():
	"""Disable CUPS (Common UNIX Printing System) in the host.

	CUPS is a modular printing system for Unix-like computer operating systems
	which allows a computer to act as a print server. A computer running CUPS
	is a host that can accept print jobs from client computers, process them,
	and send them to the appropriate printer. This function disable CUPS in
	the host if it is enabled.
	"""

	cups_status = get_output('systemctl is-active cups')
	need_reboot = False

	if cups_status == 'active':
		LOGGER.debug('(cups) is active, disabling it')
		LOGGER.debug('systemctl stop cups')
		check_output(
			'sudo systemctl stop cups',
			'the command was executed successfully',
			'an error was occurred with the last command')

		LOGGER.debug('systemctl disable cups')
		check_output(
			'sudo systemctl disable cups',
			'the command was executed successfully',
			'an error was occurred with the last command')

		LOGGER.debug('systemctl stop cups-browsed')
		check_output(
			'sudo systemctl stop cups-browsed',
			'the command was executed successfully',
			'an error was occurred with the last command')

		LOGGER.debug('systemctl disable cups-browsed')
		check_output(
			'sudo systemctl disable cups-browsed',
			'the command was executed successfully',
			'an error was occurred with the last command')
		need_reboot = True

	else:
		LOGGER.debug('(cups) is inactive')

	if need_reboot:
		LOGGER.debug('rebooting the system')
		# TODO(Beto) sometimes the system can takes a long time in rebooting, the
		# best approach for this is to do a cold reboot with raspberry.py
		get_output('sudo reboot')
		sys.exit('rebooting the system in order to disable CUPS')
