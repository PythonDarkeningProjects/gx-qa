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
import argparse
from argparse import RawDescriptionHelpFormatter
import os
import re
from shutil import copyfile
from shutil import rmtree
import sys

import yaml

from common import network
from gfx_qa_tools.common import bash
from gfx_qa_tools.common import log
from gfx_qa_tools.common import utils


class KernelManaging(object):

	def __init__(self, **kwargs):
		"""Class constructor

		:param kwargs:
			- tag: build drm-tip kernel and create a QA-tag.
				The accepted value is : True
			- daily: build drm-tip kernel.
				The accepted value is : True
			- commit: build drm-tip kernel with a specific commit.
				The commit must have at least 7 digits to be recognized by git.
		"""
		self.tag = kwargs.get('tag', None)
		self.daily = kwargs.get('daily', None)
		self.specific_commit = kwargs.get('commit', None)

		list_to_validate = [self.tag, self.daily, self.specific_commit]
		if list_to_validate.count(None) != 2:
			raise RuntimeError('please set one value')

		self.this_path = os.path.dirname(os.path.abspath(__file__))
		self.data = yaml.load(open(os.path.join(self.this_path, 'kernel.yml')))

		self.kernel_keys = self.data['drm-tip']['kernel_keys']
		self.kernel_name = self.data['drm-tip']['kernel_name'].lower()
		self.debian_packages_local_path = '/home/shared/kernels_mx/drm-tip'
		self.kernel_folder_nickname = self.data['drm-tip']['kernel_folder_nickname']
		self.kernel_id = 'drm-tip'

		if self.tag:
			self.log_path = '/home/shared/logs/kernel/drm-intel-qa'
			self.kernel_keys = self.data['drm-intel-qa']['kernel_keys']
			self.kernel_name = self.data['drm-intel-qa']['kernel_name'].lower()
			self.debian_packages_local_path = '/home/shared/kernels_mx/drm-intel-qa'
			self.kernel_folder_nickname = self.data['drm-intel-qa'][
				'kernel_folder_nickname']
			self.kernel_id = 'drm-intel-qa'

		elif self.daily:
			self.log_path = '/home/shared/logs/kernel/daily'
		elif self.specific_commit:
			self.log_path = '/home/shared/logs/kernel/specific_commit'
		else:
			self.log_path = '/home/shared/logs/kernel/drm-tip'

		# initialize the logger
		self.log_filename = 'kernel.log'

		self.log = log.setup_logging(
			name=self.log_filename, level='debug',
			log_file='{path}/{filename}'.format(
				path=self.log_path, filename=self.log_filename)
		)

		self.log.info('saving the log in: {log_file}'.format(
			log_file=os.path.join(self.log_path, self.log_filename)))

		# check if self.kernel_name does not exceeds 33 characters
		if len(self.kernel_name) > 33:
			self.log.error(
				'{0} : exceeds 33 characters, please make it smaller'.format(
					self.kernel_name))
			sys.exit(1)

		# check for characters not allowed in kernel name
		# reference : https://www.debian.org/doc/debian-policy/#s-f-source
		rule = 'package names must consist only of lower case letters (a-z), ' \
			'digits (0-9), plus (+) and minus (-) signs, and periods (.)\n ' \
			'They must be at least two characters long and must start with an ' \
			'alphanumeric character'

		characters_not_allowed = ['_', '~']
		for character in characters_not_allowed:
			if character in self.kernel_name:
				self.log.error("character '{0}'not allowed in : {name}".format(
					character, name=self.kernel_name))
				self.log.info(rule)
				sys.exit(1)

		self.mailing_list = self.data['miscellaneous']['mailing_list']
		# linuxgraphics.intel.com configuration
		self.server_for_upload_package = self.data[
			'miscellaneous']['server_for_upload_package']
		self.server_user = self.data['miscellaneous']['server_user']
		self.week_number = bash.get_output('date +"%-V"')
		self.month = bash.get_output('month=`date +"%b"`; echo ${month^^}')
		self.week_day = bash.get_output('date +%A').lower()
		self.year = bash.get_output('date +%G')
		self.hour = bash.get_output('date +"%I-%M-%S %p"')
		self.enforce = self.data['miscellaneous']['enforce']
		# getting the ip
		self.ip = network.get_ip()
		# environment variables
		os.environ['GIT_SSL_NO_VERIFY'] = '1'
		# this variable will change if there is a new commit for the kernel.
		self.kernel_commit_built = None

	def write_read_config_file(self, **kwargs):
		"""Write/read data from a specific file.

		The aim of this function is to handle the kernel configuration keys to
		write in the kernel configuration file.

		:param kwargs:
			- kernel_key: the kernel key to check
			- kernel_value: the kernel value to check
			- config_file: the kernel config file
		"""
		kernel_key = kwargs['kernel_key']
		kernel_value = kwargs['kernel_value']
		key_in_config = False

		with open(kwargs['config_file'], 'r') as archive:
			data = archive.readlines()

		for key in data:
			if re.search(r'^{key}'.format(key=kernel_key), key.replace('\n', '')):
				# this mean that the key exists in the kernel config file
				key_in_config = True
				key_in_config_value = key.replace('\n', '').split('=')[1]
				key_in_config_line_number = data.index(key)
				break

		if key_in_config:
			if key_in_config_value == kernel_value:
				self.log.info('{key}={value} is already setup in : {config}'.format(
					key=kernel_key, value=kernel_value, config=kwargs['config_file']))
			else:
				self.log.info('current value for ({key}) is : ({value})'.format(
					key=kernel_key, value=key_in_config_value))
				self.log.info('setting as : {0}'.format(kernel_value))
				# changing the kernel key value
				data[key_in_config_line_number] = '{key}={value}\n'.format(
					key=kernel_key, value=kernel_value)
				# write everything back with the new kernel key value
				with open(kwargs['config_file'], 'w') as archive:
					archive.writelines(data)
		else:
			self.log.warning('{key}: was not found in : {config} as [y|m|n]'.format(
				key=kernel_key, config=kwargs['config_file']))
			self.log.info('appending: {key}={value} to {config}'.format(
				key=kernel_key, value=kernel_value, config=kwargs['config_file']))
			# appending the kernel key to the config file
			with open(kwargs['config_file'], 'a') as archive:
				archive.write('{key}={value}\n'.format(key=kernel_key, value=kernel_value))

	def create_qa_tag(self, commit):
		"""Create a QA tag

		The aim of this function is to check if a QA tag exists, if not this
		this function create it.
		:param commit, which is the commit for create the QA tag.
		:return
			does not return anything, only stops the execution in certain
			point of the function.
		"""
		# qa tag name
		date_today = bash.get_output('date +"%Y-%m-%d"')
		qa_tag_name = 'drm-intel-qa-testing-' + date_today
		# the qa folder is used for storage the qa tags
		qa_tag_path = os.path.join('/home/shared/kernels_mx/qa-tag')

		# checking if the current QA exits
		kernel_qa_path = os.path.join(qa_tag_path, 'drm-tip')
		if not os.path.exists(kernel_qa_path):
			self.log.error('{0} : not exists'.format(kernel_qa_path))
			return

		check_qa_tag = os.system(
			'git -C {path} tag -l | grep -w {tag}'.format(
				path=kernel_qa_path, tag=qa_tag_name))

		if check_qa_tag:
			# updating drm-tip in order to create the tag
			self.log.info(
				'QA tag does not exits, creating QA tag ({tag}) in ({path})'.format(
					tag=qa_tag_name, path=kernel_qa_path))
			self.log.info('updating ({0})'.format(kernel_qa_path))
			os.system(
				'git -C {path} pull origin drm-tip'.format(
					path=kernel_qa_path))
			os.system(
				'git -C {path} reset --hard origin/drm-tip'.format(
					path=kernel_qa_path))
			output = os.system(
				'git -C {path} tag -a {tag} {commit} -m {tag}'.format(
					path=kernel_qa_path, tag=qa_tag_name, commit=commit))

			if output:
				self.log.info(
					'could not be create the tag: {0}'.format(
						qa_tag_name))
				return

			self.log.info(
				'the tag ({tag}) was created successfully in ({path})'.format(
					tag=qa_tag_name, path=kernel_qa_path))
			return

		self.log.warning(
			'QA tag ({tag}) already exits on ({path})'.format(
				tag=qa_tag_name, path=kernel_qa_path))

	def send_email(self, **kwargs):
		"""Upload kernel debian packages.

		:param kwargs:
			- debian_packages_link: when set to True this function will send a
			email notification with the link to linuxgraphics.intel.com web page.
			where the user can download the packages otherwise only a email
			notification will send without the link.
			- output_dir: which is the output dir where the kernel debian packages
			are stored.
			- kernel_name: which is the kernel name.
			- kernel_version: which is the kernel version.
			- git_log: which is the log from git.
			- package_list: which are the debian packages compiled.
			- latest_commit_information: the full information for the compiled
			commit.
		"""
		output_dir = kwargs['output_dir']
		debian_packages_link = kwargs['debian_packages_link']
		kernel_name = kwargs['kernel_name']
		kernel_version = kwargs['kernel_version']
		git_log = kwargs['git_log']
		package_list = kwargs['package_list']
		latest_commit_information = kwargs['latest_commit_information']

		# sending an email notification
		if debian_packages_link:
			link = 'http://linuxgraphics.intel.com:/{kernel_id}/' \
				'WW{number}/{version}'.format(
					number=self.week_number, version=kernel_version, kernel_id=self.kernel_id)
			utils.emailer(
				'kernel.builder@noreply.com',
				self.mailing_list,
				'new commit for {kernel_name} version: {version}'.format(
					kernel_name=kernel_name, version=kernel_version),
				'a new commit for {kernel_name} was build and uploaded to {server}\n'
				'link to kernel: {link}\n\n'
				'{log}\n\n '
				'Package list: \n'
				'{package}\n'
				'Kernel version: {version}\n\n'
				'{commit}'.format(
					kernel_name=kernel_name, server=self.server_for_upload_package, link=link,
					log=git_log, package=package_list, version=kernel_version,
					commit=latest_commit_information)
			)
		else:
			utils.emailer(
				'kernel.builder@noreply.com',
				self.mailing_list,
				'new commit for {kernel_name} version: {version}'.format(
					kernel_name=kernel_name, version=kernel_version),
				'a new commit for {kernel_name} was build\n'
				'this commit was not uploaded to {server} and it is locally '
				'stored in : {output_dir}'
				'{log}\n\n '
				'Package list: \n'
				'{package}\n'
				'Kernel version: {version}\n\n'
				'{commit}'.format(
					output_dir=output_dir, kernel_name=kernel_name,
					server=self.server_for_upload_package, log=git_log,
					package=package_list, version=kernel_version,
					commit=latest_commit_information)
			)

	def upload_kernel_debian_packages(self, **kwargs):
		"""Upload kernel debian packages.

		:param kwargs:
			- output_dir: which is the output kernel debian packages directory
			where the packages will allocated in the server.
		"""
		output_dir = kwargs['output_dir']

		# uploading the debian package
		current_hostname = bash.get_output('echo ${HOSTNAME}')

		if current_hostname != 'bifrost':
			self.log.warning(
				'the system is not allowed for upload the debian package')
			self.log.info(
				'please contact to the system-admin(s) if you need to upload it from here')
			for system_admin in self.mailing_list:
				self.log.info('- {0}'.format(system_admin))
			sys.exit(1)

		if self.ip.startswith('19'):
			self.log.error(
				'the package only will be uploaded on intranet connection')
			sys.exit(1)

		# creating the folder in the external server
		path_to_upload_packages = os.path.join(
			'/var', 'www', 'html', 'linuxkernel.com', 'kernels', self.kernel_id,
			'WW{week_number}'.format(week_number=self.week_number))
		self.log.info('creating the folder in : {cname}:{path}'.format(
			cname=self.server_for_upload_package, path=path_to_upload_packages))
		cmd = 'ssh {user}@{cname} mkdir -p {path} &> /dev/null'.format(
			user=self.server_user, cname=self.server_for_upload_package,
			path=path_to_upload_packages)
		bash.check_output(
			cmd,
			'the folder was created successfully in: {0}'.format(
				self.server_for_upload_package),
			'could not created the folder in: {0}'.format(
				self.server_for_upload_package),
			print_messages=False
		)

		# uploading kernel debian packages
		self.log.info('uploading debian package')
		cmd = 'scp -o "StrictHostKeyChecking no" -r {input_path} ' \
			'{user}@{cname}:{output_path} &> /dev/null'.format(
				input_path=output_dir, user=self.server_user,
				cname=self.server_for_upload_package,
				output_path=path_to_upload_packages)
		bash.check_output(
			cmd,
			'the debian package was uploaded successfully in : {0}'.format(
				self.server_for_upload_package),
			'could not uploaded the debian package in : {0}'.format(
				self.server_for_upload_package),
			print_messages=False
		)

	def structure_debian_packages_folder(self, **kwargs):
		"""Structure the kernel debian packages output folder.

		:param kwargs:
			- output_dir: which is the kernel packages output directory.
			- kernel_target: which is kernel directory where the debian packages
			were built.
			- git_log: which is log from git.
			- package_list: which is kernel package list.
			- dsc_file: which is dsc file from the kernel.
			- changes_file: which is changes file from the kernel.
			- custom_config: which is config used during the compilation.
			- commit: which is the kernel commit.
		"""
		output_dir = kwargs['output_dir']
		kernel_target = kwargs['kernel_target']
		git_log = kwargs['git_log']
		package_list = kwargs['package_list']
		dsc_file = kwargs['dsc_file']
		changes_file = kwargs['changes_file']
		custom_config = kwargs['custom_config']
		commit = kwargs['commit']

		# structuring the folder where the kernel debian packages will stored.
		self.log.info('creating ({0}) directory'.format(output_dir))
		os.makedirs(os.path.join(output_dir, 'deb_packages'))

		self.log.info('moving debian packages to ({0})'.format(output_dir))
		os.system('mv ' + kernel_target + '/*.deb {output}'.format(
			output=os.path.join(output_dir, 'deb_packages')))

		self.log.info('generating commit_info file')

		with open(os.path.join(output_dir, 'commit_info'), 'w') as output_file:
			output_file.write(git_log + '\n')

		self.log.info('generating package_list file')

		with open(os.path.join(output_dir, 'package_list'), 'w') as output_file:
			output_file.write(package_list + '\n')

		# generating a file with the kernel key setup in kernel.yml
		# for future references
		with open(os.path.join(output_dir, 'kernel_keys'), 'w') as output_file:
			output_file.write('kernel keys setup with this kernel:\n\n')
			for kernel_key, kernel_value in self.kernel_keys.items():
				output_file.write('{key}:{value}\n'.format(
					key=kernel_key, value=kernel_value))

		# generating kernel_folder_nickname file in order that clonezilla knows
		# the kernel to install
		if self.kernel_folder_nickname:
			with open(os.path.join(output_dir, 'kernel_folder_nickname'), 'w') as \
				output_file:
				output_file.write(self.kernel_folder_nickname)

		self.log.info('copying ({0})'.format(dsc_file))
		copyfile(
			os.path.join(kernel_target, dsc_file),
			os.path.join(output_dir, dsc_file))
		self.log.info('copying ({0})'.format(changes_file))
		copyfile(
			os.path.join(kernel_target, changes_file),
			os.path.join(output_dir, changes_file))

		self.log.info('copying ({0})'.format(custom_config))
		copyfile(custom_config, os.path.join(output_dir, 'debug.conf'))

		self.log.info('deleting: ({0})'.format(kernel_target))
		rmtree(kernel_target)

		with open(os.path.join(self.this_path, 'kernelCommit'), 'w') as kernel_commit_file:
			kernel_commit_file.write(commit)

		# changing the variable value in order to use it in ff_orchestrator.py
		self.kernel_commit_built = commit

	def kernel_builder(self, **kwargs):
		"""Dedicated function to build the kernel

		The aim of this function is to build kernel from drm-tip and tagged as
		drm-intel-qa in order to preserve the commit in our server.

		:param kwargs: could has the following values
			- kernel_target: which is the kernel source code to build
			- latest_commit: which is the latest commit to build
			- latest_commit_information: which is the full information from the
			latest commit
			- kernel_name: which is the kernel name
		"""
		kernel_target = kwargs['kernel_target']
		latest_commit = kwargs['latest_commit']
		latest_commit_information = kwargs['latest_commit_information']
		kernel_name = kwargs['kernel_name']

		utils.timer('start')
		bash.check_output(
			'git -C {0} checkout drm-tip'.format(kernel_target),
			'git checkout branch drm-tip was successful',
			'git checkout branch drm-tip was failed',
			print_messages=False
		)
		bash.check_output(
			'git -C {path} checkout {commit}'.format(
				path=kernel_target, commit=latest_commit),
			'git checkout commit drm-tip was successful',
			'git checkout commit drm-tip was failed',
			print_messages=False
		)

		# this is part of the new procedure in order to avoid issues with FWs
		kernel_config = os.path.join(kernel_target, '.config')
		self.log.info('copying config to: {0}'.format(kernel_config))
		kernel_conf = os.path.join(self.this_path, 'conf.d', 'debug.conf')
		copyfile(kernel_conf, kernel_config)

		self.log.info('● setting kernel keys ●')

		# naming the kernel
		self.write_read_config_file(
			config_file=kernel_config,
			kernel_key='CONFIG_LOCALVERSION',
			kernel_value='"-{name}-ww{week_number}-commit-{commit}"'.format(
				name=kernel_name, week_number=self.week_number, commit=latest_commit)
		)

		# changing the kernel keys setup in kernel.yml
		for key, value in self.kernel_keys.items():
			self.write_read_config_file(
				config_file=kernel_config,
				kernel_key=key,
				kernel_value=value
			)

		# creating config file to build the kernel
		self.log.info('creating kernel config file')
		os.system('cd {0} && make olddefconfig'.format(kernel_target))
		self.log.info('creating a (tmp.d) folder')
		os.makedirs(os.path.join(kernel_target, 'tmp.d'))
		self.log.info('moving all kernel tree to (tmp.d)')
		dest = os.path.join(kernel_target, 'tmp.d')
		os.system('mv ' + kernel_target + '/{.,}* ' + dest + ' 2> /dev/null')

		# build options
		cores = int(bash.get_output('nproc')) + 2

		self.log.info('compiling {kernel_name} with : {cores} cores'.format(
			kernel_name=kernel_name, cores=cores))
		# there is an internal Bash variable called "$PIPESTATUS" it’s an array
		# that holds the exit status of each command in your last foreground
		# pipeline of commands.
		output = os.system(
			'cd {path} && make -j{cores}  deb-pkg | '
			'tee {log_path}/kernel_compilation.log ; '
			'bash -c "test ${{PIPESTATUS[0]}} -eq 0"'.format(
				path=dest, cores=cores, log_path=self.log_path))

		if output:
			self.log.error('unable to compile drm-tip')
			utils.emailer(
				'kernel.builder@noreply.com',
				self.mailing_list,
				'unable to compile {0} kernel'.format(kernel_name),
				'bifrost.intel.com was unable to compile {name} kernel\n\n'
				'The following commit was unable to compile: {commit}'.format(
					name=kernel_name, commit=latest_commit))
			utils.timer('stop', print_elapsed_time=False)
			sys.exit(1)

		self.log.info('{0} : was compiled successfully'.format(kernel_name))

		# getting information from the kernel tree
		custom_config = os.path.join(kernel_target, 'tmp.d', '.config')
		dsc_file = bash.get_output('ls {0} | grep .dsc$'.format(kernel_target))
		changes_file = bash.get_output('ls {0} | grep .changes$'.format(
			kernel_target))
		kernel_full_version = bash.get_output(
			'cat {path} | grep -w ^Version'.format(
				path=os.path.join(kernel_target, dsc_file))).split()[1]
		kernel_version = kernel_full_version.split('-')[0]
		my_list = kernel_full_version.split('-')
		commit_index = my_list.index('commit') + 1
		commit = my_list[commit_index].split('+')[0]

		# this condition is when a new kernel does not contains the tag rc in
		# their name
		if re.search('rc', kernel_full_version):
			release_candidate = kernel_full_version.split('-')[1]
			kernel_version = '{version}-{rc}-{commit}'.format(
				version=kernel_version, rc=release_candidate, commit=commit)
		else:
			kernel_version = '{version}-{commit}'.format(
				version=kernel_version, commit=commit)

		package_list = bash.get_output(
			'cat {path} | grep -w ^Package-List -A 4 | '
			'sed -e \'s/Package-List://g\' -e \'1d\''.format(
				path=os.path.join(kernel_target, dsc_file)))

		git_log = bash.get_output(
			'git -C {path} show {commit} --format=fuller'.format(
				path=os.path.join(kernel_target, 'tmp.d'), commit=commit))

		# creating output directory for the kernel debian packages
		pre_output_dir = os.path.join(
			self.debian_packages_local_path, 'WW{0}'.format(self.week_number))

		if self.enforce:
			enforce_folders = int(bash.get_output(
				'ls {path} | grep enforce | wc -l'.format(path=pre_output_dir))) + 1
			if self.kernel_folder_nickname:
				output_dir = os.path.join(
					pre_output_dir,
					'{kernel_version}-{week_day}-{nick_name}-enforce-{enforce}'.format(
						kernel_version=kernel_version, week_day=self.week_day,
						nick_name=self.kernel_folder_nickname, enforce=enforce_folders))
			else:
				output_dir = os.path.join(
					pre_output_dir, '{kernel_version}-{week_day}-enforce-{enforce}'.format(
						kernel_version=kernel_version, week_day=self.week_day,
						enforce=enforce_folders))
		else:
			if self.kernel_folder_nickname:
				output_dir = os.path.join(
					pre_output_dir, '{kernel_version}-{week_day}-{nick_name}'.format(
						kernel_version=kernel_version, week_day=self.week_day,
						nick_name=self.kernel_folder_nickname))
			else:
				output_dir = os.path.join(
					pre_output_dir, '{kernel_version}-{week_day}'.format(
						kernel_version=kernel_version, week_day=self.week_day))

		self.structure_debian_packages_folder(
			output_dir=output_dir,
			kernel_target=kernel_target,
			git_log=git_log,
			package_list=package_list,
			dsc_file=dsc_file,
			changes_file=changes_file,
			custom_config=custom_config,
			commit=commit
		)

		if self.tag:
			# creating the QA tag
			self.create_qa_tag(commit)

		if self.data['miscellaneous']['upload_package']:
			# uploading kernel debian packages
			self.upload_kernel_debian_packages(output_dir=output_dir)
			debian_packages_link = True
		else:
			self.log.info(
				'the kernel debian packages will not be uploaded due to '
				'(upload_package) key is set to False')
			debian_packages_link = False

		# sending a email notification
		self.send_email(
			output_dir=output_dir,
			kernel_name=kernel_name,
			debian_packages_link=debian_packages_link,
			kernel_version=kernel_version,
			git_log=git_log,
			package_list=package_list,
			latest_commit_information=latest_commit_information
		)

		utils.timer('stop', print_elapsed_time=False)

	def check_if_kernel_folder_exists(self, directory, latest_commit):
		"""Check if a folder exists

		If a folder commit exists this function will stop the script.

		:param directory: which is the main directory to iterate.
		:param latest_commit: which is the folder commit to find.
		"""
		for root, dirs, files in os.walk(directory):
			for folder in dirs:
				if latest_commit in folder:
					self.log.error(
						'the latest commit ({commit}) for {id} exists in : {folder}'.format(
							commit=latest_commit, folder=os.path.join(root, folder),
							id=os.path.basename(directory)))
					if self.enforce:
						self.log.info(
							'enforce key is set to (True), the final kernel '
							'folder will named as enforce')
						return
					else:
						self.log.info(
							'if you want to build this kernel, please set '
							'enforce key to True')
						sys.exit(1)

		self.log.info('the commit : ({commit}) does not exists in {folder}'.format(
			commit=latest_commit, folder=directory))

	def check_for_manifest(self, target_folder):
		"""Check for UTC integration manifest on kernel tree

		:param target_folder, which is the kernel target folder to build.
		"""

		kernel_target_folder = target_folder

		# checking where UTC manifest is
		self.log.info('checking for manifest commit in : {0}'.format(
			kernel_target_folder))
		manifest = bash.get_output(
			'git -C {0} log origin/drm-tip -n 1 --pretty=format:\'%s\' | '
			'grep "UTC integration manifest"'.format(kernel_target_folder))

		if manifest:
			self.log.info('{0}: has UTC integration manifest'.format(
				kernel_target_folder))
			self.log.info(
				'the kernel will be build with latest UTC integration manifest commit')
		else:
			self.log.warning('{0}: has not UTC integration manifest'.format(
				kernel_target_folder))
			self.log.info('the kernel will be build with latest commit')

	def check_pid(self):
		"""Check the PID before compile a kernel

		The aim of this function is to check if any other instance of this script
		is running in order to not run due to the following valid reason:
		- when this script is running it will use all the cores in the system,
		and if other instance is running it can crash the system due to overload.

		:return
			- self.kernel_commit_built: this value will contains a kernel commit
			id (7 digits) if this script built a new kernel from drm-tip
			otherwise the default value is None.
		"""
		script_name = os.path.basename(__file__)
		current_pid = os.getpid()

		if bash.is_process_running(script_name, current_pid):
			self.log.error('another instance of : {0} is running'.format(script_name))
			sys.exit(1)

		self.check_kernel()

		return self.kernel_commit_built

	def check_kernel_updates(self, target_folder):
		"""Check for updates in the kernel tree.

		:param target_folder, which is the kernel target folder to build.
		:return
			latest_commit_information: which is the full information from the
			latest commit on the kernel tree.
			latest_commit: which is the latest commit from the kernel tree.
		"""
		kernel_target_folder = target_folder

		# checking if drm-tip is up-to-date
		current_commit = bash.get_output(
			'git -C {0} rev-parse HEAD'.format(kernel_target_folder))[0:7]
		latest_commit = bash.get_output(
			'git -C {0} ls-remote origin drm-tip'.format(
				kernel_target_folder)).split()[0][0:7]
		latest_commit_information = bash.get_output(
			'git -C {path} show {commit} --format=fuller'.format(
				path=kernel_target_folder, commit=latest_commit))

		if current_commit != latest_commit:
			self.log.info('{0} : is out-to-date, updating'.format(kernel_target_folder))
			os.system('git -C {0} pull origin drm-tip'.format(kernel_target_folder))
			os.system('git -C {0} reset --hard origin/drm-tip'.format(
				kernel_target_folder))
		else:
			self.log.info('{0}: is up-to-date'.format(kernel_target_folder))

		return latest_commit, latest_commit_information

	def check_if_a_commit_exists(self, **kwargs):
		"""Check if a kernel commit exists

		:param kwargs:
			- kernel_build_path: the kernel path to check the commit.
			- commit: the commit to check
		"""
		kernel_build_path = kwargs['kernel_build_path']
		commit = kwargs['commit']

		output = os.system('git -C {path} show {commit} &> /dev/null'.format(
			path=os.path.join(kernel_build_path, self.kernel_id), commit=commit))

		if output:
			self.log.error('kernel commit : ({commit}) not found in {path}'.format(
				path=kernel_build_path, commit=commit))
			sys.exit(1)

	def check_kernel(self):
		"""Check the kernel to build

		The aim of this function is to check if a new kernel commit is available
		in drm-tip source code in order to build it.
		"""

		network.set_proxy()

		# defining the path to build the kernel
		if self.tag:
			kernel_build_path = '/home/shared/build/kernel/drm-intel-qa'
		elif self.daily:
			kernel_build_path = '/home/shared/build/kernel/daily'
		elif self.specific_commit:
			kernel_build_path = '/home/shared/build/kernel/specific_commit'
		else:
			kernel_build_path = '/home/shared/build/kernel/drm-tip'

		if not os.path.exists(kernel_build_path):
			self.log.info('{0} : does not exists, creating it'.format(
				kernel_build_path))
			os.makedirs(kernel_build_path)

		# checking if drm-tip exists in target folder
		kernel_target_folder = os.path.join(kernel_build_path, 'drm-tip')
		if os.path.exists(kernel_target_folder):
			self.log.warning('{0} : exists, deleting'.format(kernel_target_folder))
			rmtree(kernel_target_folder)

		# drm-tip folder is always up-to-date
		drm_tip_folder = '/home/shared/ezbench/kernel/drm-tip'
		if not os.path.exists(drm_tip_folder):
			self.log.error('{0} : does not exists'.format(drm_tip_folder))
			sys.exit(1)

		self.log.info('copying (drm-tip) to ({0})'.format(kernel_build_path))
		utils.timer('start')
		os.system('cp -r {origin} {dest}'.format(
			origin=drm_tip_folder, dest=kernel_target_folder))
		utils.timer('stop', print_elapsed_time=False)

		# checking if index.lock exists in kernel tree in order to avoid issues
		index_lock = os.path.join(kernel_target_folder, '.git', 'index.lock')
		if os.path.isfile(index_lock):
			self.log.warning('index.lock exists in ({0}), removing'.format(
				kernel_target_folder))
			os.remove(index_lock)

		latest_commit, latest_commit_information = self.check_kernel_updates(
			kernel_target_folder)

		if self.tag:
			qa_kernels = '/home/shared/kernels_mx/drm-intel-qa'
			self.check_if_kernel_folder_exists(qa_kernels, latest_commit)
			self.check_for_manifest(kernel_target_folder)
		else:
			drm_tip_kernels = '/home/shared/kernels_mx/drm-tip'
			if self.specific_commit:
				self.check_if_a_commit_exists(
					kernel_build_path=kernel_build_path, commit=self.specific_commit)
				self.check_if_kernel_folder_exists(
					drm_tip_kernels, self.specific_commit)
				latest_commit = self.specific_commit
			else:
				self.check_if_kernel_folder_exists(drm_tip_kernels, latest_commit)

		print(latest_commit_information)

		# build the kernel
		self.kernel_builder(
			kernel_target=kernel_target_folder,
			latest_commit=latest_commit,
			latest_commit_information=latest_commit_information,
			kernel_name=self.kernel_name
		)


def arguments():

	parser = argparse.ArgumentParser(
		formatter_class=RawDescriptionHelpFormatter,
		description='''
	program description:
	(%(prog)s) is a tool for managing the build of kernels.
	project : https://01.org/linuxgraphics
	repository : https://github.intel.com/linuxgraphics/gfx-qa-tools.git
	maintainer : humberto.i.perez.rodriguez@intel.com''',
		epilog='Intel® Graphics for Linux* | 01.org',
		usage='%(prog)s [options]')
	group1 = parser.add_argument_group(
		'({0}positional arguments{1})'
		.format(bash.YELLOW, bash.END))
	group1.add_argument(
		'-t', '--tag', action='store_true', dest='tag', default=None,
		help='if this option is given, the kernel to build will be tagged')
	group1.add_argument(
		'-d', '--daily', action='store_true', dest='daily', default=None,
		help='this option is dedicated for the daily kernel builds')
	group1.add_argument(
		'-c', '--commit', dest='commit', default=None,
		help='build the kernel with a specific commit')
	args = parser.parse_args()
	KernelManaging(
		tag=args.tag,
		daily=args.daily,
		commit=args.commit
	).check_pid()


if __name__ == '__main__':
	arguments()
