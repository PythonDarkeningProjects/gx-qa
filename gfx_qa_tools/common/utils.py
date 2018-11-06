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

"""Provides a library of useful utilities.

This module provides a list of general purpose utilities. Those functions that
are part of a larger domain, for example functions related to networking,
should be provided by a different module.

This module should only include functions that are not related with a
specific application, in other words these methods should be application
agnostic.
"""

from __future__ import print_function

import logging
import os
import re
import smtplib
import time
import timeit

from tabulate import tabulate

from gfx_qa_tools.common import bash

LOGGER = logging.getLogger(__name__)


def create_formatted_table(headers, content, index=False, silent=True):
	"""Create a formatted table with tabulate module.

	:param headers: a list with the headers of the table
	:param content: a list of lists with the content of the table
	:param index: set to True if you want to show an index in the table
	:param silent: if set to False it will print the table before returning it
	:return: a table

	How to use it:
		headers = ['component', 'family', 'id']

	- an example of the param content is:
	for one row:
		content = [['igt', 'kms', '1']]
	for two rows:
		content = [['igt', 'kms', '1'], ['igt', 'gem', '2']]
	"""
	if not isinstance(headers, list):
		headers = [headers]
	if not isinstance(content, list):
		content = [[content]]

	if index:
		headers.insert(0, 'index')

	table = tabulate(
		content, headers, 'fancy_grid',
		missingval='?', stralign='center', numalign='center',
		showindex=True if index else False)

	if not silent:
		print(table)

	return table


def emailer(sender, mailing_list, subject, message, silent=False):
	"""Emailer function is dedicated to send emails

	:param sender: the person/entity who is sending the message
	:param mailing_list: the PDL of the email to be sent
	:param subject: the subject of the email to be sent
	:param message: the message of the email to be sent
	:param silent: suppress the bash.messages from the output when set to True
	"""

	mailing_list = mailing_list if mailing_list is not None else list()

	receivers = mailing_list
	email_message = (
		"""From: {sender}
		To: {mail_to}
		Subject: {subject}

		Hi sys-admin:

		{email_body}


		Intel Graphics for linux*| 01.org
		This is an automated message, please do not reply this message"""
		.format(
			sender=sender,
			mail_to=receivers,
			subject=subject,
			email_body=message)
	)

	email_message = email_message.replace('\t', '')
	# this is as a workaround, to eliminate car return from email_message

	try:
		LOGGER.debug(
			'sending email about "{subject}" to {receivers}'
			.format(subject=subject, receivers=receivers)
		)
		smtp_obj = smtplib.SMTP('smtp.intel.com')
		smtp_obj.sendmail(sender, receivers, email_message)
		if not silent:
			bash.message('info', 'email sent successfully')
		LOGGER.debug('email sent successfully')

	except smtplib.SMTPRecipientsRefused:
		error_message = 'All recipients were refused. Nobody got the mail.'
		LOGGER.error(error_message, exc_info=True)
		if not silent:
			bash.message('err', error_message)
		return False

	except (
		smtplib.SMTPHeloError, smtplib.SMTPSenderRefused,
		smtplib.SMTPDataError) as error:
		error_message = 'Unable to send the email: {0}'.format(error.message)
		LOGGER.error(error_message, exc_info=True)
		if not silent:
			bash.message('err', error_message)
		return False

	return True


def isdir(path, sudo=True):
	"""Validates if a directory exist in a host.

	:param path: the path of the directory to be validated
	:param sudo: this needs to be set to True for directories that require
	root permission
	:return: True if the directory exists, False otherwise
	"""
	LOGGER.debug('validating if directory {dir} exists'.format(dir=path))
	status, _ = bash.run_command(
		'{prefix}test -d {path}'.format(path=path, prefix='sudo ' if sudo else ''))
	exist = True if not status else False
	LOGGER.debug('directory exists: {exist}'.format(exist=exist))
	return exist


def isfile(path, sudo=True):
	"""Validates if a file exist in a host.

	:param path: the absolute path of the file to be validated
	:param sudo: this needs to be set to True for files that require
	root permission
	:return: True if the file exists, False otherwise
	"""
	LOGGER.debug('validating if file {file} exists'.format(file=path))
	status, _ = bash.run_command(
		'{prefix}test -f {path}'.format(path=path, prefix='sudo ' if sudo else ''))
	exist = True if not status else False
	LOGGER.debug('file exists: {exist}'.format(exist=exist))
	return exist


def wait_for_file_existence(dirname, regex, timeout=10):
	r"""This function waits for the existence of one file.

	This function waits for the existence of one file named with a specific
	string or char using regular expressions.

	:param dirname: select the folder path to check the file named with a
	specific regex.
	:param regex: regular expression to look for.
	:param timeout: specify how much time do you want to wait for the file
	named with specific regex (waits in seconds).
	:return: True when the regular expression is found in the named file,
	False when there is no file that matches with the regex you are looking
	for and the waiting time is over.

	How to use it:
		ls /home/user/mypath:
		file1.txt file2.txt

	call the function:
		wait_for_file_existence(dirname='/home/user/mypath', regex='\#', timeout=20)

	create "File#1.txt"
		touch /home/user/mypath/File#1.txt

	Function returns data=True since 'File#1.txt' contains the regex '\#'
	"""
	timeout = time.time() + timeout
	data = False
	while True:

		if data or time.time() > timeout:
			break

		for _, _, files in os.walk(dirname):
			if files:
				for file_named in files:
					reg_search = re.search(regex, file_named)
					if reg_search:
						data = True
		time.sleep(1)

	if not data:
		LOGGER.debug(
			'The waiting time was over, the files that matches the '
			'regex was not found in {0} = '.format(dirname))

	return data


def timer(action, print_elapsed_time=True):
	"""Function that works as a timer, with a start/stop button.

	:param action: the action to perform, the valid options are:
		- start: start a counter for an operation
		- stop: stop the current time
	:param print_elapsed_time: if set to False the message is not printed to
	console, only returned
	:return: the elapsed_time string variable
	"""
	elapsed_time = 0
	if action.lower() == 'start':
		start = timeit.default_timer()
		os.environ['START_TIME'] = str(start)
	elif action.lower() == 'stop':
		if 'START_TIME' not in os.environ:
			bash.message('err', 'you need to start the timer first')
			return None
		stop = timeit.default_timer()
		total_time = stop - float(os.environ['START_TIME'])
		del os.environ['START_TIME']

		# output running time in a nice format.
		minutes, seconds = divmod(total_time, 60)
		hours, minutes = divmod(minutes, 60)
		elapsed_time = 'elapsed time ({h}h:{m}m:{s}s)'.format(
			h=0 if round(hours, 2) == 0.0 else round(hours, 2),
			m=0 if round(minutes, 2) == 0.0 else round(minutes, 2),
			s=round(seconds, 2))
		if print_elapsed_time:
			bash.message('info', elapsed_time)
		else:
			LOGGER.debug(elapsed_time)
	else:
		bash.message('err', '{0}: not allowed'.format(action))

	return elapsed_time
