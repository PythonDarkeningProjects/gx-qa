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

import os
import sys
import yaml

from gfx_qa_tools.common import bash
from gfx_qa_tools.common import utils


class Actions(object):

	def __init__(self):

		# environment variables
		os.environ['GIT_SSL_NO_VERIFY'] = '1'

		self.thisPath = os.path.dirname(os.path.abspath(__file__))
		self.data = yaml.load(open(os.path.join(self.thisPath, 'updater.yml')))
		self.mailing_list = self.data['treeroot']['mailing_list']
		self.repositories_path = self.data['treeroot']['repositories_path']
		self.sender = self.data['treeroot']['sender']

		# time variables
		self.week_number = bash.get_output('date +"%-V"')
		self.month = \
			bash.get_output('month=`date +"%b"`; echo ${month^^}').lower()
		self.week_day = bash.get_output('date +%A').lower()
		self.year = bash.get_output('date +%G')
		self.hour = bash.get_output('date +"%I-%M-%S %p"')

		if not os.path.exists(self.repositories_path):
			bash.center_message(
				bash.RED + '>>> (err)' + bash.END + ' (' +
				self.repositories_path + ') does not exists')
			sys.exit(1)

	def check_for_updates(self, path_to_repo, branch):
		"""Check for updates in each folder into updater.yml

		:param path_to_repo: the selected path to the repository.
		:param branch: the selected branch for the repository.
		"""
		local_commit = \
			bash.get_output(
				'cd ' + path_to_repo + ' && git rev-parse origin/' + branch)
		remote_commit = \
			bash.get_output(
				'cd ' + path_to_repo + ' && timeout 5 git ls-remote origin ' +
				branch + ' | awk \'{print $1}\'')

		if local_commit != remote_commit:
			bash.message(
				'warn',
				'(' + path_to_repo + ') is (' + bash.YELLOW + 'out-to-date' +
				bash.END + ')')
			bash.message('info', 'local commit  (' + local_commit + ')')
			bash.message('info', 'remote commit (' + remote_commit + ')')
			bash.message('info', 'updating repository ...')
			bash.message('info', 'counting the current commits ...')
			old_commits_number = \
				bash.get_output(
					'cd ' + path_to_repo + ' && git rev-list origin/' +
					branch + ' --count')
			old_commit_info = \
				bash.get_output(
					'cd ' + path_to_repo +
					' && git log -1 --format=fuller origin/' + branch)
			bash.message('info', 'old commit information')
			print(old_commit_info)
			bash.message('cmd', 'git pull origin ' + branch)
			os.system('cd ' + path_to_repo + ' && git pull origin ' + branch)
			bash.message('cmd', 'git reset --hard origin/' + branch)
			os.system(
				'cd ' + path_to_repo + ' && git reset --hard origin/' + branch)
			new_commit_info = \
				bash.get_output(
					'cd ' + path_to_repo +
					' && git log -1 --format=fuller origin/' + branch)
			bash.message('info', 'new commit information')
			print(old_commit_info)
			bash.message('info', 'counting the new commits ...')
			new_commits_number = bash.get_output(
				'cd ' + path_to_repo + ' && git rev-list origin/' +
				branch + ' --count')
			new_commit = \
				bash.get_output(
					'cd ' + path_to_repo +
					' && git rev-parse origin/' + branch)

			if local_commit != new_commit:
				bash.message(
					'ok',
					'(' + os.path.basename(path_to_repo) + ') is (' +
					bash.GREEN + 'up-to-date' + bash.END + ')')
				commits_diff = int(new_commits_number) - int(old_commits_number)
				bash.message(
					'info',
					'commits downloaded : (' + str(commits_diff) + ')')
				bash.message('info', 'sending a email notification')
				utils.emailer(
					self.sender,
					self.mailing_list,
					'There is a new commit for (' +
					os.path.basename(path_to_repo) + ') (' + self.month +
					') (' + self.week_day + ') (' + self.hour + ')',
					'There is a new commit for (' +
					os.path.basename(path_to_repo) +
					')\n\nCommits downloaded : (' + str(commits_diff) +
					')\n\nLatest commit is:\n\n' + new_commit_info
				)

			else:
				bash.message('info', 'local commit (' + local_commit + ')')
				bash.message('info', 'new commit   (' + new_commit + ')')
				bash.message(
					'err',
					'(' + os.path.basename(path_to_repo) + ') is (' +
					bash.YELLOW + 'out-to-date' + bash.END + ')')
				bash.message(
					'err',
					'an error occurred trying to update (' +
					os.path.basename(path_to_repo) + ')')

		else:
			bash.message(
				'info',
				'(' + os.path.basename(path_to_repo) + ') is (' + bash.GREEN +
				'up-to-date' + bash.END + ')')
			bash.message('info', 'local commit  (' + local_commit + ')')
			bash.message('info', 'remote commit (' + remote_commit + ')')
			current_commit_info = \
				bash.get_output(
					'cd ' + path_to_repo +
					' && git log -1 --format=fuller origin/' + branch)
			bash.message('info', 'current commit information\n\n')
			print(current_commit_info + '\n\n')

	def check_for_repositories(self):
		"""
		check if each folder into updater.yml exists
		"""
		ignore_keys = ['mailing_list', 'repositories_path', 'sender']
		for v in self.data.values():
			for key in v.keys():
				if key in ignore_keys:
					continue
				else:
					url = v[key]['url']
					alias = v[key]['alias']
					branch = v[key]['branch']
					bash.message(
						'info',
						'checking updates for (' + bash.CYAN + url +
						bash.END + ')')

					if alias:
						bash.message('info', 'alias (' + alias + ')')
						if os.path.exists(
							os.path.join(self.repositories_path, alias)):
							bash.message(
								'info',
								'(' +
								os.path.join(self.repositories_path, alias) +
								') exists')
							self.check_for_updates(
								os.path.join(
									self.repositories_path, alias), branch)
						else:
							bash.message(
								'info',
								'(' +
								os.path.join(self.repositories_path, alias) +
								') does not exists, cloning ...')
							bash.get_output(
								'cd ' + self.repositories_path +
								' && git clone ' + url + ' ' + alias)
					else:
						# checking if the repo comes from github.com
						if '.git' in url:
							repo_folder = \
								os.path.basename(url.replace('.git', ''))
						else:
							repo_folder = os.path.basename(url)

						if os.path.exists(
							os.path.join(self.repositories_path, repo_folder)):
							bash.message(
								'info',
								'(' +
								os.path.join(
									self.repositories_path, repo_folder) +
								') exists')
							self.check_for_updates(
								os.path.join(
									self.repositories_path, repo_folder),
								branch)
						else:
							bash.message(
								'info',
								'(' +
								os.path.join(
									self.repositories_path, repo_folder) +
								') does not exists, cloning ...')
							bash.get_output(
								'cd ' + self.repositories_path +
								' && git clone ' + url)


if __name__ == '__main__':
	Actions().check_for_repositories()
