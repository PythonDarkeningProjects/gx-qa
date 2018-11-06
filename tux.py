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
# https://docs.python.org/3/library/argparse.html

from __future__ import print_function

import argparse
import os

from gfx_qa_tools.common import bash
from common import network as net_utils

password = 'linux'


class Verify(object):

	def updates(self):
		if not net_utils.get_ip():
			bash.center_message(
				'\n({0}Network is unreachable{1})\n'.format(bash.RED, bash.END))
			bash.exit_message(
				bash.center_message(
					'\n({0}To check updates from github.com you must be connected'
					'to internet{1})\n'.format(bash.YELLOW, bash.END))
			)
		else:
			c_local_commit_sha = "git rev-parse origin/master"
			c_remote_commit_sha = (
				"timeout 2 git ls-remote origin master | awk '{print $1}'")
			local_commit_sha = bash.get_output(c_local_commit_sha)
			remote_commit_sha = bash.get_output(c_remote_commit_sha)

			if local_commit_sha == remote_commit_sha:
				os.system('clear')
				bash.center_message(
					'\nrepository [{0}up-to-date{1}]\n'.format(bash.GREEN, bash.END))
			else:
				os.system('clear')
				bash.center_message(
					'\nrepository [{0}out-to-date{1}]\n'.format(bash.RED, bash.END))
				bash.center_message(
					'({0}updating repository{1})'.format(bash.YELLOW, bash.END))
				count_current_commits = "git rev-list origin/master --count"
				current_commit_info = "git log -1 origin/master"
				c_updateBranch = "git pull origin master"
				c_resetBranch = "git reset --hard origin/master"
				c_new_commit_info = "git log -1 origin/master"

				previous_commits = bash.get_output(count_current_commits)
				print(
					'({0}current sha{1})\n{2}\n'
					.format(bash.CYAN, bash.END, bash.get_output(current_commit_info)))
				bash.get_output(c_updateBranch, c_updateBranch)
				bash.get_output(c_resetBranch, c_resetBranch)
				print(
					'\n({0}new sha{1})\n{2}\n'
					.format(bash.CYAN, bash.END, bash.get_output(c_new_commit_info)))

				c_current_commit_sha = "git rev-parse origin/master"
				current_commit_sha = bash.get_output(c_current_commit_sha)

				if local_commit_sha == current_commit_sha:
					bash.center_message(
						'({0}Something was wrong during updating master branch{1})\n'
						.format(bash.RED, bash.END))

					print('SHA before update : {0}'.format(local_commit_sha))
					print('SHA after update  : {0}'.format(str(current_commit_sha)))
					bash.center_message(
						'({0}err{2} : {1}the SHAs are the same{2})\n'
						.format(bash.RED, bash.YELLOW, bash.END))
				else:
					new_commits = bash.get_output(count_current_commits)
					diff = int(new_commits) - int(previous_commits)

					if diff > 0:
						bash.center_message(
							'({0}) commits downloaded during the update\n'
							.format(str(diff)))
					else:
						bash.center_message(
							'({0}no new commits were found{1})\n'
							.format(bash.YELLOW, bash.END))


class Main(object):

	def __init__(self):
		self.v = Verify()
		os.environ['export GIT_SSL_NO_VERIFY'] = '1'
		net_utils.set_proxy()

	def dependencies(self):
		dependencies_list = [
			'sshpass', 'dos2unix', 'ssh', 'vim', 'git', 'w3m', 'vim-gnome', 'tmux',
			'mate-terminal', 'synaptic', 'gparted']

		for dependency in dependencies_list:
			if not bash.get_output('dpkg -l | grep ' + dependency):
				bash.message('info', 'Installing (' + dependency + ') ...')
				os.system('echo ' + password + ' | sudo -S apt-get install ' + dependency)

	def menu(self):

		self.dependencies()

		parser = argparse.ArgumentParser(
			description=bash.CYAN + 'Intel® Graphics for Linux*' + bash.END,
			epilog=bash.CYAN + 'https://01.org/linuxgraphics' + bash.END)
		group = parser.add_mutually_exclusive_group()
		group.add_argument(
			'-s', '--skip', dest='skip_updates', action='store_true',
			help='skip updates from github.com')
		group.add_argument(
			'-c', '--check', dest='check_updates', action='store_true',
			help='check updates from github.com')
		# group.add_argument('-q','--quiet',dest='quiet', action='store_true')
		# parser.add_argument(
		# 'num', choices=[1,2,3], help='The fibonacci number' 'ou wish calculate',
		# type=int, required=True)
		# parser.add_argument(
		# '-s','--skip', dest='updates', help='skip updates from github.com',
		# action='store_true')
		parser.add_argument(
			'-v', '--version', dest='version', action='version', version='%(prog)s 1.0')

		args = parser.parse_args()

		if args.check_updates:
			Verify().updates()


if __name__ == '__main__':
	Main().menu()
	# Verify()
	Main()
