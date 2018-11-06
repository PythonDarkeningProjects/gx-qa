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
import os
import platform
import sys
import yaml

from argparse import RawDescriptionHelpFormatter

from common import apiutils
from gfx_qa_tools.common import bash
from gfx_qa_tools.common import utils
import ezbench_qa.suites.rendercheck as rendercheck
from time import sleep


class Setup(object):
	"""
	Provide methods for setup the following test suites for ezbench :
	- intel-gpu-tools
	- rendercheck
	- benchmarks

	ezbench is able to run the mentioned test suites with kernel bisection
	but is not smart enough yet.
	A command series is required in order to simulate a kernel bisection
	for more information about this commands please read the following
	document in google drive:

	https://docs.google.com/document/d/
	1t8dNPgGNvLxu8iwNiwHJH14XZCZG_VuuEkp54agChAk/edit#

	"""

	def __init__(self):
		self.thisPath = os.path.dirname(os.path.abspath(__file__))
		self.python_version = \
			platform.python_version_tuple()[0]  # this will return "2/3"

		# Checking if the DUT was setup with the automated system
		config_file = os.path.join('/home', 'custom', 'config.yml')
		self.sender = 'ezbench@noreply.com'

		if not os.path.isfile(config_file):
			self.dut_user = 'gfx'
			self.automated_system = False
			self.server_hostname = 'bifrost.intel.com'
			self.server_user = 'root'
			self.ip = bash.get_output(
				"/sbin/ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | "
				"grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'").decode(
				"utf-8")
		else:
			self.data = yaml.load(open(config_file))
			self.ip = self.data['dut_conf']['dut_static_ip']
			self.suite = self.data['suite_conf']['default_package']
			self.dut_hostname = self.data['dut_conf']['dut_hostname']
			self.grub_parameters = self.data['dut_conf']['grub_parameters']
			self.graphical_environment = \
				self.data['dut_conf']['graphical_environment']
			self.guc = self.data['firmwares']['guc']
			self.huc = self.data['firmwares']['huc']
			self.dmc = self.data['firmwares']['dmc']
			self.default_mailing_list = \
				self.data['suite_conf']['default_mailing_list']
			self.dut_user = self.data['dut_conf']['dut_user']
			self.raspberry_n = self.data['raspberry_conf']['raspberry_number']
			self.switch_n = \
				self.data['raspberry_conf']['raspberry_power_switch']
			self.server_hostname = self.data['usb_conf']['server_hostname']
			self.server_user = self.data['usb_conf']['server_user']
			self.automated_system = True

		self.ezbench_grub_entry = \
			os.path.join(self.thisPath, 'tools', 'grub_entry.sh')

		# repositories
		self.ezbench_repo = 'https://anongit.freedesktop.org/git/ezbench.git'
		self.debian_packages_url = 'http://linuxgraphics.intel.com/deb'

		self.file_to_write = \
			os.path.join(
				'/home', self.dut_user, '.ezbench_setup_completed')

		self.repo_folders = ['/opt/source', '/opt/benchmarks']

		for element in self.repo_folders:
			if not os.path.exists(element):
				os.makedirs(element)

		self.kernel_folder = os.path.join('/opt', 'source', 'linux')
		# ===================================================================
		# for the moment, this script only will run through SSH due to issues
		# with w3m under terminal
		# self.ssh_connection_a = bash.get_output('echo $SSH_CLIENT').decode(
		# 	"utf-8")
		# self.ssh_connection_b = bash.get_output('echo $SSH_TTY').decode(
		# 	"utf-8")
		# if not self.ssh_connection_a or not self.ssh_connection_b:
		# 	bash.message('err', 'please run this script under SSH connection')
		# 	sys.exit(1)
		# ===================================================================

	def check_environment(self, custom_message):
		"""
		:param custom_message:
		:return: check if a DUT is in the automated system in order to sent
		messages to watchdog webpage : http://bifrost.intel.com:2020/watchdog
		"""

		if self.automated_system:
			bash.message('info', 'sending a message to watchdog webpage')
			apiutils.update_watchdog_db(
				self.raspberry_n,
				self.switch_n,
				Suite=self.suite,
				Status=custom_message)
			sleep(3)

	def gfx_stack(self):
		"""
		:return: here are two possibles scenarios for this function :
		1 - (DUT in the automated system) : check if a graphic stack package
		was installed during clonezilla installation, if not this script will
		not continue.
		2 - (DUT outside of the automated system) : check if a graphic stack
		is installed in the system, otherwise this function will help you to
		install a graphic stack from http://linuxgraphics.intel.com/deb.
		"""

		# Checking for graphic stack from linuxgraphics.intel.com
		has_gfx_stack = bash.get_output("dpkg -l | grep 01.org").decode(
			"utf-8")
		has_gfx_stack_name = bash.get_output(
			"dpkg -l | grep 01.org | awk '{print $2}'").decode("utf-8")

		if not has_gfx_stack:
			while True:
				bash.message(
					'warn', 'no graphic stack was detected in the system, '
					'please install one graphic stack')
				self.check_environment(
					'(err) no graphic stack was detected in the system,'
					' please install a graphic stack')
				if self.automated_system:
					sys.exit(1)
				workweek_list = \
					bash.get_output(
						"w3m -dump " + self.debian_packages_url +
						" | awk '{print $2}' | grep WW | "
						"sed 's|/||g'").decode("utf-8").split()
				for ww in workweek_list:
					print('-> ' + ww)
				workweek_input = input(
					bash.BLUE + '>>> (info)' + bash.END +
					' enter a workweek (case sensitive) : ')
				if workweek_input not in workweek_list:
					bash.message(
						'err', 'invalid workweek, '
						'please select a valid one')
					bash.message('info', 'press any key to continue ...')
					input()
					os.system('clear')
				else:
					workweek_selection = workweek_input
					break
			while True:
				os.system('clear')
				bash.message(
					'info', 'please select a graphic stack to install')
				folder_list = \
					bash.get_output(
						'w3m -dump ' +
						os.path.join(
							self.debian_packages_url, workweek_selection) +
						" | grep -w \"\["
						"DIR\]\" | awk '{print $2}' | sed "
						"'s|/||g'").decode("utf-8").split()
				folder_dict = {}
				count = 1
				for folder in folder_list:
					to_update = {str(count): folder}
					folder_dict.update(to_update)
					count += 1
				count = 1
				for folder in folder_list:
					print('(' + str(count) + ') ' + folder)
					count += 1
				folder_input = input(
					bash.BLUE + '>>> (info)' + bash.END + ' enter a number : ')

				if folder_input in folder_dict:
					folder_to_download = folder_dict[folder_input]
					full_link_to_download = os.path.join(
						self.debian_packages_url, workweek_selection,
						folder_to_download)
					stack_folder = os.path.join(
						'/home', self.dut_user, 'graphic_stack_packages')
					if not os.path.exists(stack_folder):
						bash.message(
							'info', 'creating folder '
							'(graphic_stack_packages) into (' +
							stack_folder + ')', '')
						bash.return_command_status('mkdir -p ' + stack_folder)
					bash.message(
						'info', 'downloading graphic stack debian '
						'package (' + folder_to_download + ')', '')
					bash.return_command_status(
						'cd ' + stack_folder + " && wget -q -A '.deb' -np"
						" -nd -m -E -k -K -e robots=off -l 1 " +
						full_link_to_download)
					bash.message('info', 'installing the graphic stack', '')
					bash.return_command_status(
						'cd ' + stack_folder + ' && sudo dpkg -i '
						'--force-overwrite *.deb')
					break
				else:
					bash.message(
						'err', 'invalid selection, please select a valid one')
					bash.message(
						'info', 'press any key to continue ...')
					input()
					os.system('clear')
		elif has_gfx_stack:
			bash.message(
				'info', 'the following graphic stack was detected in '
				'the system')
			self.check_environment(
				'the following graphic stack was detected in the system (' +
				has_gfx_stack_name + ')')
			bash.message(
				'info', '(' + bash.CYAN + has_gfx_stack_name + bash.END + ')')

	def check_gfx_stack_for_xorg_xserver(self):
		"""
		check if all the following condition are met for xorg-xserver
		debian package
		"""
		custom_path = os.path.join('/opt', 'X11R7')
		xorg_binary = os.path.join(custom_path, 'bin', 'Xorg')
		modesetting_library = \
			os.path.join(
				custom_path, 'lib', 'xorg', 'modules', 'drivers',
				'modesetting_drv.so')
		xorg_conf = os.path.join('/etc', 'X11', 'xorg.conf')
		which_xorg = bash.get_output('which Xorg').decode("utf-8")

		checklist = [
			xorg_binary,
			modesetting_library,
			xorg_conf
		]

		if os.path.exists(custom_path):
			for element in checklist:
				bash.message(
					'info',
					'checking if (' + element + ') exists in the system')
				if not os.path.exists(element):
					self.check_environment(
						'(err) (' + os.path.basename(element) +
						') does not exists')
					bash.message(
						'err',
						'(' + os.path.basename(element) +
						') does not exists, please check the graphic stack')
					sys.exit(1)
				else:
					self.check_environment(
						'(info) (' + os.path.basename(element) + ') exists')
					bash.message(
						'info', '(' + os.path.basename(element) + ') exists')

			if which_xorg != '/opt/X11R7/bin/Xorg':
				self.check_environment(
					'(err) xorg binary is in (' + which_xorg +
					') instead of (/opt/X11R7/bin/Xorg) rebooting the system '
					'to check again')
				bash.message(
					'err',
					'xorg binary is in (' + which_xorg +
					') instead of (/opt/X11R7/bin/Xorg) rebooting the system '
					'to check again')
				bash.message('info', 'sending an email')
				utils.emailer(
					self.sender,
					self.default_mailing_list,
					'xorg binary is in (' + which_xorg +
					') instead of (/opt/X11R7/bin/Xorg) (' +
					self.dut_hostname + ') (' + self.ip + ')',
					'Xorg is misconfigured in the following platform :\n'
					' - (' + self.dut_hostname + ')\n'
					' - (' + self.ip + ')\n\n'
					'the automated system will reboot the DUT in order to '
					'check again in the next reboot'
				)
				os.system('sudo reboot')
			else:
				self.check_environment(
					'(info) xorg binary is in the correct location '
					'(/opt/X11R7/bin/Xorg)')
				bash.message(
					'info',
					'xorg binary is in the correct location '
					'(/opt/X11R7/bin/Xorg)')
		else:
			self.check_environment(
				'(err) (' + custom_path + ') does not exists')
			bash.message('err', '(' + custom_path + ') does not exists')
			sys.exit(1)

	def ezbench_repository(self):
		"""
		:return: check if ezbench folder exists on /home/<user> otherwise
		this function will download it from the official repo handled by
		martin peres from FI.
		"""

		# Checking for ezbench repository
		global ezbench_folder
		ezbench_folder = os.path.join('/home', self.dut_user, 'ezbench')
		if not os.path.exists(ezbench_folder):
			bash.message(
				'info', 'cloning ezbench into (' +
				os.path.join('/home', self.dut_user) + ')', '')
			bash.return_command_status(
				'git clone ' + self.ezbench_repo + ' ' + ezbench_folder)
			self.check_environment(
				'cloning ezbench into (' +
				os.path.join('/home', self.dut_user) + ')')
		elif os.path.exists(ezbench_folder):
			bash.message(
				'skip', '(ezbench) already exists on (' + ezbench_folder + ')')
			self.check_environment(
				'(ezbench) already exists on (' + ezbench_folder + ')')

	def check_kernel_on_server(self):
		"""
		:return: this function is for download the kernel source code of
		drm-tip from bifrost.intel.com into the DUT and speed up the setup
		of any of the availables test suites in the script.
		"""

		# checking if the kernel folder exists on bifrost.intel.com
		# to optimize times
		kernel_external_path = '/home/shared/ezbench/kernel/drm-tip'
		output = \
			bash.get_output(
				'ssh ' + self.server_user + '@' + self.server_hostname +
				" '[ -d  " + kernel_external_path + " ] "
				"&& echo true || echo false'").decode("utf-8")

		if output == 'true':
			bash.message(
				'info',
				'(drm-tip) folder exists on (' + self.server_hostname + ')')
			self.check_environment(
				'downloading drm-tip from (' + self.server_hostname + ')')
			bash.message(
				'info',
				'downloading drm-tip from (' + self.server_hostname + ')')
			output = os.system(
				'scp -r ' + self.server_user + '@' + self.server_hostname +
				':' + kernel_external_path + ' ' + self.kernel_folder)
			if output != 0:
				self.check_environment(
					'(warn) an error was occurred trying to download '
					'(drm-tip) (' + self.server_hostname + ')')
				bash.message(
					'warn',
					'an error was occurred trying to download (drm-tip) '
					'from (' + self.server_hostname + ')')
				return False
			else:
				self.check_environment(
					'(info) (drm-tip) was downloaded successfully from (' +
					self.server_hostname + ')')
				bash.message(
					'info',
					'(drm-tip) was downloaded successfully from (' +
					self.server_hostname + ')')

				# updating kernel as a double check
				kernel_local_folder = \
					os.path.join(self.kernel_folder, 'drm-tip')
				if os.path.exists(kernel_local_folder):
					bash.message('info', 'updating (drm-tip)')
					bash.message('cmd', 'git pull origin drm-tip')
					os.system(
						'cd ' + kernel_local_folder +
						' && git pull origin drm-tip')
					bash.message('cmd', 'git reset --hard origin/drm-tip')
					output = os.system(
						'cd ' + kernel_local_folder +
						' && git reset --hard origin/drm-tip')
					if output != 0:
						return False
					else:
						return True
		else:
			self.check_environment(
				'(warn) (drm-tip) folder does not exists on (' +
				self.server_hostname + ')')
			bash.message(
				'warn',
				'(drm-tip) folder does not exists on (' +
				self.server_hostname + ')')
			return False

	def kernel(self):
		"""
		:return: this function check if the kernel source code from drm-tip
		exists in the system, otherwise it will try to download in this order:
		1 - if the kernel source code is available on bifrost.intel.com will
		download from here (this process is faster than the second step).
		2 - if the kernel source code does not exists on bifrost.intel.com
		this function will download it from the official repo of drm-tip
		(this process is slow than the first step)
		Note : the kernel source code from bifrost.intel.com is under a cronjob
		that keeps up-to-date every 5 minutes.
		"""

		# Checking for kernel directory
		if not os.path.exists(self.kernel_folder):
			bash.message(
				'info', 'creating kernel folder into (' +
				self.kernel_folder + ')', '')
			bash.return_command_status('mkdir -p ' + self.kernel_folder)
		elif os.path.exists(self.kernel_folder):
			bash.message('skip', '(' + self.kernel_folder + ') already exists')

		# Checking for drm-tip into kernel_directory
		drm_tip_folder = os.path.join(self.kernel_folder, 'drm-tip')
		drm_tip_local_config_file = \
			os.path.join(self.thisPath, 'conf.d', 'debug.conf')
		drm_tip_config_file = os.path.join(drm_tip_folder, '.config')

		if not os.path.exists(drm_tip_folder):

			check_kernel = self.check_kernel_on_server()

			if not check_kernel:
				if os.path.exists(drm_tip_folder):
					self.check_environment(
						'(info) removing (drm-tip) from (' +
						self.kernel_folder + ')')
					bash.message(
						'info',
						'removing (drm-tip) from (' + self.kernel_folder + ')')
					os.system('rm -rf ' + drm_tip_folder)
				bash.message(
					'info', 'the following process will take a while, '
					'go for a cup of coffee °o°')
				bash.message(
					'info', 'cloning drm-tip')
				self.check_environment(
					'cloning drm-tip, this step could take a while')
				bash.return_command_status(
					'git clone https://anongit.freedesktop.org/git/'
					'drm-tip.git ' + drm_tip_folder)

		elif os.path.exists(drm_tip_folder):
			bash.message('skip', '(drm-tip) already exists')
			self.check_environment('(drm-tip) already exists')

		if os.path.exists(drm_tip_folder) and not \
			os.path.isfile(drm_tip_config_file):
			bash.message(
				'info', 'copying kernel config file to (' +
				drm_tip_folder + ')')
			self.check_environment(
				'copying kernel config file to (' + drm_tip_folder + ')')
			bash.return_command_status(
				'cp ' + drm_tip_local_config_file + ' ' + drm_tip_config_file)
		elif os.path.exists(drm_tip_folder) and \
			os.path.isfile(drm_tip_config_file):
			bash.message('skip', 'kernel config file already exists')
			self.check_environment('kernel config file already exists')

	def ssh_keys(self):
		"""
		:return: this function is dedicated to introduce several ssh keys to
		the DUTs in order to get connection from they without any password from
		the following servers :
		- bifrost.intel.com
		- asgard.intel.com
		- midgard.intel.com
		- and some others systems
		"""

		# Setting ssh keys in order to download anything from our servers
		if not os.path.isfile(
			os.path.join('/home', self.dut_user, '.ssh_keys')):
			if not os.path.exists(
				os.path.join('/home', self.dut_user, '.ssh')):
				bash.message('info', 'creating ssh directory')
				os.makedirs(os.path.join('/home', self.dut_user, '.ssh'))
			bash.message('info', 'setting ssh keys')
			self.check_environment('setting ssh keys')
			ssh_path = os.path.join(self.thisPath, 'tools', 'ssh')
			ssh_files = \
				bash.get_output('ls ' + ssh_path).decode("utf-8").split()
			for element in ssh_files:
				bash.message('info', 'copying (' + element + ')', '')
				bash.return_command_status(
					'cp ' + os.path.join(ssh_path, element) + ' ' +
					os.path.join('/home', self.dut_user, '.ssh'))
			os.system(
				'chmod 600 ' + os.path.join(
					'/home', self.dut_user, '.ssh', 'id_rsa'))
			bash.message('info', 'restarting ssh service')
			self.check_environment('restarting ssh service')
			bash.return_command_status('sudo systemctl restart ssh')
			os.system(
				'touch ' + os.path.join('/home', self.dut_user, '.ssh_keys'))
		else:
			bash.message('skip', 'ssh keys are already setup')
			self.check_environment('ssh keys are already setup')

	def benchmarks(self):
		"""
		:return: this function is dedicated to setup benchmarks environment
		for ezbench
		"""

		# Checking for benchmarks directory
		benchmarks_folder = os.path.join('/opt', 'benchmarks')
		if not os.path.exists(benchmarks_folder):
			bash.message(
				'info', 'creating benchmarks folder into (' +
				benchmarks_folder + ')', '')
			bash.return_command_status('mkdir -p ' + benchmarks_folder)
		elif os.path.exists(benchmarks_folder):
			bash.message('skip', '(' + benchmarks_folder + ') already exists')

		if len(os.listdir(benchmarks_folder)) == 0:
			os.path.getsize(benchmarks_folder)
			benchmarks_size = \
				bash.get_output(
					'ssh gfxserver@linuxgraphics.intel.com '
					'"du -sh /home/benchmarks"').decode("utf-8").split()[0]
			bash.message(
				'info', 'downloading (' + str(benchmarks_size) + ')', '')
			self.check_environment('downloading (' + str(benchmarks_size) + ')')
			bash.return_command_status(
				'scp gfxserver@linuxgraphics.intel.com:'
				'/home/benchmarks/* ' + benchmarks_folder)
		elif len(os.listdir(benchmarks_folder)) > 0:
			bash.message('skip', 'the benchmarks are already downloaded')
			self.check_environment('the benchmarks are already downloaded')

		if not os.path.isfile(
			os.path.join('/home', self.dut_user, '.benchmarks_done')):
			bash.message('info', 'decompressing the benchmarks', '')
			self.check_environment('decompressing the benchmarks')
			bash.return_command_status(
				'bash ' + os.path.join(self.thisPath, 'tools', 'unpack.sh'))
			os.system(
				'touch ' + os.path.join(
					'/home', self.dut_user, '.benchmarks_done'))
		elif os.path.isfile(
			os.path.join(
				'/home', self.dut_user, '.benchmarks_done')):
			bash.message('skip', 'the benchmarks were already decompressed')
			self.check_environment('the benchmarks were already decompressed')

	def user_parameters(self):
		"""
		:return: this function is dedicated to modified the file that comes
		from ezbench called (user_parameters.sh) in order to setup the correct
		environment variables that ezbench uses for run different test suites.
		"""

		# Setting user_parameters.sh
		user_parameters_sample = \
			os.path.join(
				'/home', self.dut_user,
				'ezbench', 'user_parameters.sh.sample')
		user_parameters_file = \
			os.path.join(
				'/home', self.dut_user, 'ezbench', 'user_parameters.sh')

		if os.path.isfile(user_parameters_sample) and not os.path.isfile(
			user_parameters_file):
			bash.message(
				'info', 'copying (user_parameters.sample) to '
				'(user_parameters.sh)')
			self.check_environment(
				'copying (user_parameters.sample) to (user_parameters.sh)')
			bash.return_command_status(
				'cp ' + user_parameters_sample + ' ' +
				user_parameters_file)
		elif not os.path.isfile(user_parameters_sample):
			bash.message(
				'err', '(user_parameters.sh.sample) does not '
				'exists into (' + ezbench_folder + ')')
			self.check_environment(
				'(err) (user_parameters.sh.sample) does not exists into (' +
				ezbench_folder + ')')
			sys.exit(1)

		if os.path.isfile(user_parameters_file):
			keys_to_replace = [
				'REPO_LINUX=/opt/source/linux/drm-tip',
				'REPO_LINUX_CONFIG=$\{REPO_LINUX\}/.config',
				'REPO_PIGLIT=' +
				os.path.join(
					'/home', self.dut_user, 'intel-graphics',
					'intel-gpu-tools', 'piglit'),
				'IGT_ROOT=' +
				os.path.join(
					'/home', self.dut_user, 'intel-graphics',
					'intel-gpu-tools'),
				'REPO_MESA=/opt/source/mesa',
				'REPO_XF86_VIDEO_INTEL=/opt/source/xf86-video-intel',
				'RENDERCHECK_FOLDER=/opt/benchmarks/rendercheck',
				'XF86_VIDEO_INTEL=/opt/benchmarks/xf86-video-intel']
			for key in keys_to_replace:
				only_variable = key.split('=')[0]
				line_number = \
					int(bash.get_output(
						"cat -n " + user_parameters_file + "| grep -w " +
						only_variable +
						"= | awk '{print $1}'").decode("utf-8"))
				line_value = \
					bash.get_output(
						"cat -n " + user_parameters_file +
						"| grep " + only_variable +
						"= | awk '{print $2}'").decode("utf-8")
				if key != line_value:
					bash.message(
						'info', 'replacing (' + only_variable +
						') in (' + os.path.basename(user_parameters_file) +
						')', '')
					bash.return_command_status(
						"sed -i '" + str(line_number) + "s|^.*$|" + key +
						"|g' " + user_parameters_file)
		else:
			bash.message(
				'err', '(user_parameters.sh) does not exists into (' +
				ezbench_folder + ')')
			self.check_environment(
				'(user_parameters.sh) does not exists into (' +
				ezbench_folder + ')')
			sys.exit(1)

	def grub_entry(self):
		"""
		:return: this function is dedicated to setup a grub entry for
		ezbench daemon.
		If ezbench daemon is not setup in the DUT, ezbench will not works.
		"""

		# Creating the grub entry for ezbench
		ezbench_grub_file = \
			os.path.join('/etc', 'grub.d', '40_ezbench-kernel')
		if not os.path.isfile(ezbench_grub_file):
			bash.message('info', 'creating the grub entry for ezbench')
			self.check_environment('creating the grub entry for ezbench')
			bash.return_command_status('sudo bash ' + self.ezbench_grub_entry)
		elif os.path.isfile(ezbench_grub_file):
			bash.message(
				'skip', '(' + os.path.basename(self.ezbench_grub_entry) +
				') already exists')
			self.check_environment('grub entry for ezbench already exists')

	def ezbench_daemon(self):
		"""
		:return: This function is dedicated to setup the ezbench daemon
		in the DUT.
		Without the ezbench daemon the suites will not works.
		"""

		# Setting ezbench daemon
		ezbench_daemon_file = \
			os.path.join(
				'/etc', 'systemd', 'system', 'ezbenchd.service')
		ezbench_daemon_local_file = \
			os.path.join(self.thisPath, 'tools', 'ezbenchd.service')
		if not os.path.isfile(ezbench_daemon_file):
			bash.message(
				'info', 'setting (' +
				os.path.basename(ezbench_daemon_file) + ') daemon')
			self.check_environment(
				'setting (' + os.path.basename(ezbench_daemon_file) +
				') daemon')
			bash.message(
				'info', 'copying (' +
				os.path.basename(ezbench_daemon_file) + ') local daemon '
				'into (' + os.path.dirname(ezbench_daemon_file) + ')', '')
			bash.return_command_status(
				'sudo cp ' + ezbench_daemon_local_file + ' ' +
				os.path.dirname(ezbench_daemon_file))
			self.check_environment('setting (ezbench) http server')
			bash.message(
				'info', 'setting (ezbench) http server on (' + self.ip +
				':8080)', '')
			line_number = \
				int(bash.get_output(
					"cat -n " + ezbench_daemon_local_file +
					"| grep ExecStart= | awk '{print $1}'").decode("utf-8"))
			bash.return_command_status(
				"sudo sed -i '" + str(line_number) + "s|^.*$|ExecStart=" +
				os.path.join(ezbench_folder, 'ezbenchd.py') +
				"  --http_server " + self.ip + ":8080|g' " +
				ezbench_daemon_file)
			bash.message(
				'info', 'setting the user (' + self.dut_user + ')', '')
			line_number = \
				int(bash.get_output(
					"cat -n " + ezbench_daemon_local_file +
					"| grep User= | awk '{print $1}'").decode("utf-8"))
			bash.return_command_status(
				"sudo sed -i '" + str(line_number) + "s|^.*$|User=" +
				self.dut_user + "|g' " + ezbench_daemon_file)
			bash.message(
				'info', 'setting the group (' + self.dut_user + ')', '')
			line_number = \
				int(bash.get_output(
					"cat -n " + ezbench_daemon_local_file + "| grep Group= | "
					"awk '{print $1}'").decode("utf-8"))
			bash.return_command_status(
				"sudo sed -i '" + str(line_number) +
				"s|^.*$|Group=" + self.dut_user + "|g' " + ezbench_daemon_file)
			bash.message(
				'info', 'changing owner for (' +
				os.path.basename(ezbench_daemon_local_file) + ') to root', '')
			bash.return_command_status('sudo chown root.root ' + ezbench_daemon_file)

			# enabling ezbench.d service
			self.check_environment('enabling ezbench daemon')
			bash.message(
				'info', 'enabling (' +
				os.path.basename(ezbench_daemon_local_file) + ') daemon', '')
			bash.return_command_status('sudo systemctl enable ezbenchd.service')
			bash.message(
				'info', 'checking is ezbench daemon was enabled correctly', '')
			ezbench_was_enabled = \
				bash.get_output(
					'systemctl is-enabled '
					'ezbenchd.service').decode("utf-8")
			if ezbench_was_enabled == 'enabled':
				print(' ... [' + bash.GREEN + 'DONE' + bash.END + ']')
				self.check_environment('ezbench daemon was enabled correctly')
			else:
				print(' ... [' + bash.RED + 'FAIL' + bash.END + ']')
				bash.message(
					'err', 'a issue was occurred enabling ezbench daemon')
				self.check_environment(
					'a issue was occurred enabling ezbench daemon')
				sys.exit(1)

			self.check_environment('starting ezbench daemon')
			bash.message(
				'info', 'starting (' +
				os.path.basename(ezbench_daemon_local_file) + ') daemon', '')
			bash.return_command_status('sudo systemctl start ezbenchd.service')
			bash.message(
				'info', 'checking is ezbench daemon was started correctly', '')
			ezbench_was_enabled = \
				bash.get_output(
					'systemctl is-active ezbenchd.service').decode("utf-8")
			if ezbench_was_enabled == 'active':
				print(' ... [' + bash.GREEN + 'DONE' + bash.END + ']')
				self.check_environment('ezbench daemon was correctly started')
			else:
				print(' ... [' + bash.RED + 'FAIL' + bash.END + ']')
				bash.message(
					'err', 'a issue was occurred activating '
					'ezbench daemon')
				self.check_environment(
					'a issue was occurred activating ezbench daemon')
				sys.exit(1)
			# =========================================================
			# 1) to check more information about the service (daemon) :
			# systemctl status ezbenchd.service
			# 2) https://www.digitalocean.com/community/tutorials/
			# how-to-use-systemctl-to-manage-systemd-services-and-units
			# =========================================================

		elif os.path.isfile(ezbench_daemon_file):
			bash.message(
				'skip', '(' + os.path.basename(ezbench_daemon_file) +
				') daemon already exists on (' +
				os.path.dirname(ezbench_daemon_file) + ')')
			bash.message(
				'info', 'checking if (' +
				os.path.basename(ezbench_daemon_file) +
				') is enabled', '')
			is_enabled = bash.get_output(
				'systemctl is-enabled ezbenchd.service').decode("utf-8")
			is_active = bash.get_output(
				'systemctl is-active ezbenchd.service').decode("utf-8")
			if is_enabled == 'enabled':
				print(' ... (' + bash.GREEN + 'DONE' + bash.END + ')')
				bash.message(
					'info', 'ezbench.d is enabled in the following url '
					'(http://' + self.ip + ':8080)')
				self.check_environment(
					'ezbench.d is enabled in the following url '
					'(http://' + self.ip + ':8080)')
			else:
				print(' ... (' + bash.RED + 'FAIL' + bash.END + ')')
				sys.exit(1)

			bash.message(
				'info', 'checking if (' +
				os.path.basename(ezbench_daemon_file) + ') is active', '')
			if is_active == 'active':
				print(' ... (' + bash.GREEN + 'DONE' + bash.END + ')')
				bash.message('info', 'ezbench.d is active in the system')
				self.check_environment('ezbench.d is active in the system')
			else:
				print(' ... (' + bash.RED + 'FAIL' + bash.END + ')')
				self.check_environment(
					'(err) ezbench.d is not active in the system')
				sys.exit(1)

		# setting a crontab for ezbench daemon
		cron_control_file = \
			os.path.join('/home', self.dut_user, '.cron_ctrl_root')
		crontab_root_file = \
			os.path.join(self.thisPath, 'tools', 'crontab_ezbench')
		if not os.path.isfile(cron_control_file):
			bash.message(
				'info', 'setting crontab for root in order to enable '
				'ezbench daemon at startup')
			self.check_environment(
				'setting crontab for root in order to enable ezbench daemon '
				'at startup')
			bash.return_command_status('sudo crontab -u root ' + crontab_root_file)
			bash.message('info', 'setting a cron control file', '')
			bash.return_command_status('touch ' + cron_control_file)
		elif os.path.isfile(cron_control_file):
			bash.message('skip', 'crontab for root is already setup')
			self.check_environment('crontab for root is already setup')

	def watchdog(self):
		"""
		:return: This function is dedicated to compile the watchdog that
		ezbench has.
		This watchdog is develop by Petri from FI team.
		when this watchdog does not detect any movement from any test from
		intel-gpu-tools it will reboot the DUT automatically.
		"""

		# Compiling internal watchdog
		ezbench_watchdog_folder = \
			os.path.join(ezbench_folder, 'utils', 'owatch')
		ezbench_watchdog_folder_binary = \
			os.path.join(ezbench_folder, 'utils', 'owatch', 'owatch')
		if os.path.exists(ezbench_watchdog_folder) and not \
			os.path.isfile(ezbench_watchdog_folder_binary):
			self.check_environment('compiling ezbench watchdog')
			bash.message('info', 'compiling ezbench watchdog', '')
			bash.return_command_status('cd ' + ezbench_watchdog_folder + ' && make')
		elif os.path.exists(ezbench_watchdog_folder) and \
			os.path.isfile(ezbench_watchdog_folder_binary):
			self.check_environment('ezbench watchdog is already compiled')
			bash.message('skip', 'ezbench watchdog is already compiled')
		elif not os.path.exists(ezbench_watchdog_folder):
			bash.message(
				'warn', '(owatch) folder does not exists, skipping '
				'internal watchdog compilation')
			self.check_environment(
				'(warn) (owatch) folder does not exists, '
				'skipping internal watchdog compilation')

	def disable_x(self):
		"""
		:return: This function is dedicated to disable X.
		The suite that does not needs X is:
		- intel-gpu-tools
		"""

		# Disabling X
		check_x = bash.get_output('ps -e | grep X').decode("utf-8")
		current_tty = bash.get_output('tty').decode("utf-8")

		if check_x:
			bash.message('info', 'X is enabled, disabling')
			self.check_environment('X is enabled, disabling')
			bash.message(
				'info', 'systemctl enable multi-user.target --force', '')
			bash.return_command_status(
				'sudo systemctl enable multi-user.target '
				'--force 2> /dev/null')
			bash.message(
				'info', 'systemctl set-default multi-user.target', '')
			bash.return_command_status(
				'sudo systemctl set-default multi-user.target 2> /dev/null')
		else:
			bash.message(
				'info', 'X is not enabled, current TTY is (' + bash.CYAN +
				current_tty + bash.END + ')')
			self.check_environment('X is not enabled')

	def control_file(self, send_email=True):
		"""
		:return: This function is dedicated to create a control file for this
		scripts, in order to know when the functions are not needed anymore
		because this script executed successfully the function called for each
		suite in this script.
		"""

		if not os.path.isfile(self.file_to_write):
			with open(self.file_to_write, 'w') as ez_file:
				ez_file.write('(info) ezbench setup is completed\n')
			self.check_environment(
				'ezbench setup completed daemon on (' + self.ip + ':8080)')

			if self.automated_system and self.default_mailing_list and send_email:
				utils.emailer(
					self.sender,
					self.default_mailing_list,
					'ezbench is ready to run in [' +
					self.dut_hostname + '] [' + self.ip + ']',
					'(' + self.dut_hostname + ') is ready for run ezbench\n\n'
					'Technical data\n'
					' - ezbench daemon on (' + self.ip + ':8080)\n'
					' - ezbench folder   : (' +
					os.path.join('/home', self.dut_user, 'ezbench') + ')\n'
					' - kernel tree path : (/opt/source/linux/drm-tip)\n'
					' - Kernel command line : (' + self.grub_parameters + ')\n'
					' - Graphical environment : (' +
					str(self.graphical_environment) + ')\n\n'
					'Firmwares\n'
					' - guc : (' + str(self.guc) + ')\n'
					' - huc : (' + str(self.huc) + ')\n'
					' - dmc : (' + str(self.dmc) + ')\n'
				)
			bash.return_command_status('sudo reboot')
		else:
			self.check_environment(
				'ezbench setup completed daemon on (' + self.ip + ':8080)')
			# running rendercheck
			if self.suite == 'ezbench_rendercheck':
				rendercheck.ExecutionManager().run_rendercheck()

	def enable_x(self):
		"""
		:return: This function is dedicated to enable X.
		The following suites needs X enabled in order to run :
		- rendercheck
		- benchmarks
		"""

		# Enabling X
		check_x = bash.get_output('ps -e | grep X').decode("utf-8")

		if check_x:
			bash.message('skip', 'X is enabled')
			self.check_environment('X is enabled')
		else:
			bash.message('info', 'X is not enabled, enabling')
			self.check_environment('X is not enabled, enabling')
			bash.message('info', 'systemctl set-default graphical.target', '')
			bash.return_command_status(
				'sudo systemctl set-default graphical.target &> /dev/null')
			bash.message('info', 'systemctl start lightdm', '')
			bash.return_command_status('sudo systemctl start lightdm &> /dev/null')

	def repositories(self):
		"""
		:return: This function is dedicated to clone the repositories that
		ezbench needed in order to test different suites.
		"""

		mesa_url = 'https://anongit.freedesktop.org/git/mesa/mesa.git'
		xf86_video_intel_url = \
			'https://anongit.freedesktop.org/git/xorg/driver/' \
			'xf86-video-intel.git'
		repo_list = [
			'/opt/source/mesa', '/opt/source/xf86-video-intel',
			'/opt/benchmarks/xf86-video-intel']

		for repo in repo_list:
			only_repo = os.path.basename(repo)
			if not os.path.exists(repo):
				bash.message(
					'info', 'cloning (' + only_repo + ') into (' +
					os.path.dirname(repo) + ')', '')
				self.check_environment(
					'cloning (' + only_repo + ') into (' +
					os.path.dirname(repo) + ')')
				if only_repo == 'mesa':
					bash.return_command_status('cd ' + os.path.dirname(
						repo) + ' && git clone ' + mesa_url)
				elif only_repo == 'xf86-video-intel':
					bash.return_command_status('cd ' + os.path.dirname(
						repo) + ' && git clone ' + xf86_video_intel_url)
			else:
				bash.message('skip', '(' + repo + ') already exists')
				self.check_environment('(' + repo + ') already exists')

	def bashrc(self):
		"""
		:return: This function is dedicated to check python version.
		ezbench only works with python3 version, other lower python version
		does not works with ezbech.
		"""
		if int(self.python_version) == 2:
			bash.message(
				'info',
				'please set python 3 as default interpreter for (' +
				self.dut_user + ')')
			bash.message('info', 'type the following commands')
			bash.message('cmd', 'sudo rm /usr/bin/python')
			bash.message(
				'cmd', 'sudo ln -s /usr/bin/python3.5 /usr/bin/python')
			sys.exit(1)
		elif int(self.python_version) == 3:
			bash.message('skip', 'python 3 is the default interpreter')
			self.check_environment('python 3 is the default interpreter')

	def rendercheck_setup(self):
		"""
		:return: This function is dedicated to setup all things needed for
		rendercheck since we are cloning from a different repository than the
		oficcial one, this is because that the repository of martin peres has
		some modification on rendercheck binary that allows to list the
		subtests by family and get the reports by subtests as well.
		"""

		# dependencies
		dependencies_list = ['meson:0.40.1', 'tsocks', 'ninja:1.7.1']

		self.check_environment('(info) checking dependencies for rendercheck')
		for element in dependencies_list:
			dependency = element.split(':')[0]
			if ':' in element:
				required_version = element.split(':')[1]
			else:
				required_version = False

			output = \
				bash.get_output('dpkg -l | grep ' + dependency).decode("utf-8")
			if not output:
				self.check_environment(
					'(err) (' + dependency +
					') dependency not found in the system')
				bash.message(
					'err',
					'(' + dependency + ') dependency not found in the system')
				sys.exit(1)
			else:
				if required_version:
					dependency_version = \
						bash.get_output(dependency + ' --v').decode("utf-8")
					if required_version != dependency_version:
						self.check_environment(
							'(err) (' + dependency +
							') version is not satisfactory')
						bash.message(
							'err',
							'(' + dependency + ') version is not satisfactory')
						bash.message(
							'info',
							'minimum version required is (' +
							required_version + ')')
						bash.message(
							'info',
							'current (' + dependency + ') version is (' +
							dependency_version + ')')
						sys.exit(1)
					else:
						bash.message(
							'info',
							'(' + dependency + ') version is : (' +
							dependency_version + ') ☆')

		# proxies configuration file
		if not os.path.isfile('/etc/tsocks.conf'):
			self.check_environment('copying (tsocks.conf) to /etc')
			bash.message('info', 'copying (tsocks.conf) to /etc')
			os.system(
				'sudo cp ' + os.path.join(
					self.thisPath, 'tools', 'tsocks.conf') + ' /etc')

		# rendercheck repository
		# due to rendercheck only shows results per family, we have to clone
		# from martin peres repository located at :
		# https://cgit.freedesktop.org/~mperes/rendercheck
		# because martin did a patch in order to rendercheck shows the subtest
		# during the test per family with --r option

		rendercheck_url = 'git://people.freedesktop.org/~mperes/rendercheck'

		if not os.path.exists('/opt/benchmarks/rendercheck'):
			self.check_environment(
				'cloning (rendercheck) into (/opt/benchmarks)')
			bash.message(
				'info', 'cloning (rendercheck) into (/opt/benchmarks)')
			bash.return_command_status(
				'cd /opt/benchmarks && tsocks git clone ' + rendercheck_url)

		# compiling rendercheck
		rendercheck_folder = '/opt/benchmarks/rendercheck'

		if os.path.exists(rendercheck_folder) and not \
			os.path.exists(os.path.join(rendercheck_folder, 'build')):
			self.check_environment('compiling rendercheck')
			bash.message('info', 'compiling rendercheck')
			if not os.path.exists(os.path.join(rendercheck_folder, 'build')):
				os.makedirs(os.path.join(rendercheck_folder, 'build'))
			self.check_environment('(cmd) meson . build')
			bash.message('cmd', 'meson . build')
			bash.return_command_status(
				'cd ' + rendercheck_folder + ' && meson . build')
			self.check_environment('(cmd) cd build && ninja')
			bash.message('cmd', 'cd build && ninja')
			bash.return_command_status(
				'cd ' + os.path.join(rendercheck_folder, 'build') +
				' && ninja')
			self.check_environment(
				'(info) creating a soft link for rendercheck')
			bash.message('info', 'creating a soft link for rendercheck')
			bash.return_command_status(
				'ln -s ' + rendercheck_folder + '/build/rendercheck ' +
				rendercheck_folder)

		elif os.path.exists(rendercheck_folder) and \
			os.path.isfile(
				os.path.join(rendercheck_folder, 'build', 'rendercheck')):
			self.check_environment('(info) (rendercheck) is already compiled')
			bash.message('info', '(rendercheck) is already compiled')

		elif not os.path.exists(rendercheck_folder):
			self.check_environment(
				'(err) (' + rendercheck_folder + ') does not exists')
			bash.message(
				'err', '(' + rendercheck_folder + ') does not exists')
			sys.exit(1)

		rendercheck_current_commit = \
			bash.get_output(
				'cd ' + rendercheck_folder +
				' && git log -1 --pretty=fuller').decode("utf-8")
		bash.message(
			'info', '(rendercheck) commit :\n\n' + rendercheck_current_commit)

	def setup(self, suite):
		"""
		:param suite: the suite to be setup in the DUT.
		:return: calls to specific functions in order to setup the available
		test suites.
		"""

		if not os.path.isfile(self.file_to_write):
			if suite == 'igt':
				self.gfx_stack()
				self.bashrc()
				self.ezbench_repository()
				self.kernel()
				self.user_parameters()
				self.ssh_keys()
				self.grub_entry()
				self.ezbench_daemon()
				self.watchdog()
				self.disable_x()
				self.control_file()

			elif suite == 'benchmarks':
				self.gfx_stack()
				self.check_gfx_stack_for_xorg_xserver()
				self.bashrc()
				self.ezbench_repository()
				self.kernel()
				self.user_parameters()
				self.ssh_keys()
				self.benchmarks()
				self.grub_entry()
				self.ezbench_daemon()
				self.repositories()
				self.enable_x()
				self.control_file()

			elif suite == 'rendercheck':
				self.rendercheck_setup()
				self.gfx_stack()
				self.check_gfx_stack_for_xorg_xserver()
				self.bashrc()
				self.ezbench_repository()
				self.ssh_keys()
				self.user_parameters()
				self.grub_entry()
				self.ezbench_daemon()
				self.repositories()
				self.enable_x()
				self.control_file(send_email=False)

			elif suite == 'piglit':
				bash.message('info', 'suite not implemented yet')
				sys.exit(0)
		else:
			# running rendercheck
			if suite == 'rendercheck':
				rendercheck.ExecutionManager().run_rendercheck()
			else:
				bash.message('info', 'ezbench setup is completed')
				bash.message('info', 'nothing to do')
				sys.exit(0)


class Arguments(object):

	parser = argparse.ArgumentParser(
		formatter_class=RawDescriptionHelpFormatter,
		description='''
	program description:
	(%(prog)s) is a tool for setup ezbench for different suites
	project : https://01.org/linuxgraphics
	maintainer : humberto.i.perez.rodriguez@intel.com''',
		epilog='Intel® Graphics for Linux* | 01.org',
		usage='%(prog)s [options]')

	parser.add_argument(
		'--version', action='version', version='%(prog)s 3.0')
	group = parser.add_argument_group(
		'{0}mandatory arguments{1}'.format(bash.BLUE, bash.END))
	group.add_argument(
		'-s', '--suite',
		dest='suite',
		required=True,
		choices=['igt', 'benchmarks', 'piglit', 'rendercheck'],
		help='select a suite for setup with ezbench'
	)

	args = parser.parse_args()

	# Setting a suite
	Setup().setup(args.suite)


if __name__ == '__main__':
	Arguments()
