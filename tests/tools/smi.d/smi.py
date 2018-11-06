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

import argparse, sys, os, subprocess, re, yaml
from shutil import copytree, ignore_patterns, copyfile, move, rmtree
from time import sleep
import pdb

class Bash_colors:
    purple = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    end = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'
    cyan = '\033[96m'
    grey = '\033[90m'
    default = '\033[99m'
    black = '\033[90m'


purple = Bash_colors.purple
blue = Bash_colors.blue
green = Bash_colors.green
yellow = Bash_colors.yellow
red = Bash_colors.red
end = Bash_colors.end
bold = Bash_colors.bold
underline = Bash_colors.underline
cyan = Bash_colors.cyan
grey = Bash_colors.grey
default = Bash_colors.default
black = Bash_colors.black

class Bash:
	
	def run (self,cmd,action):
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
		(out, err) = proc.communicate()
		out = out.strip()

		if action == 'True': 
			print out
		else: 
			return out

	def get_output(self,*args):
		if len(args) == 1:
			cmd = args[0]
			return self.run(cmd,'False')
		elif len(args) == 2:
			(cmd,message) = args[0],args[1]
			print blue + '>>> ' + end + message
			return self.run(cmd,'False')
		elif len(args) == 3:
			(cmd,message,action) = args[0],args[1],args[2]
			print blue + '>>> ' + end + message
			return self.run(cmd,'True')

class Main():

	def __init__ (self):
		self.b = Bash()
		os.environ['export GIT_SSL_NO_VERIFY'] = '1'
		self.current_kernel_file = '/home/custom/current_kernel'
		self.current_kernel = self.b.get_output('uname -r')
		self.config_file = '/home/custom/config.yml' 
		self.ext_smi_module_folder = '/home/shared/tools/BIOSConf_Release_6.1'
		self.loc_smi_module_folder = '/home/custom/BIOSConf_Release_6.1'
		self.smi_module = os.path.join(self.loc_smi_module_folder,'SMIDriver','Linux64','Release','smidrv')
		self.biosConf = os.path.join(self.loc_smi_module_folder,'Linux64','Release','BIOSConf')

		if os.path.isfile(self.config_file):
			self.data = yaml.load(open(self.config_file))
			# Dut configuration
			self.autologin = self.data['dut_conf']['autologin']
			self.dut_user = self.data['dut_conf']['dut_user']
			self.dut_hostname = self.data['dut_conf']['dut_hostname']
			self.dut_password = self.data['dut_conf']['dut_password']
			self.dut_static_ip = self.data['dut_conf']['dut_static_ip']
			self.graphical_environment = self.data['dut_conf']['graphical_environment']
			self.grub_parameters = self.data['dut_conf']['grub_parameters']
			# Firmwares
			self.dmc = self.data['firmwares']['dmc']
			self.guc = self.data['firmwares']['guc']
			self.huc = self.data['firmwares']['huc']
			# Raspberry configuration
			self.raspberry_gpio = self.data['raspberry_conf']['raspberry_gpio']
			self.raspberry_ip = self.data['raspberry_conf']['raspberry_ip']
			self.raspberry_number = self.data['raspberry_conf']['raspberry_number']
			self.raspberry_power_switch = self.data['raspberry_conf']['raspberry_power_switch']
			self.raspberry_user = self.data['raspberry_conf']['raspberry_user']
			self.usb_cutter_serial = self.data['raspberry_conf']['usb_cutter_serial']
			# Suite configuration
			self.blacklist_file = self.data['suite_conf']['blacklist_file']
			self.default_mailing_list = self.data['suite_conf']['default_mailing_list']
			self.default_package = self.data['suite_conf']['default_package']
			self.gfx_stack_code = self.data['suite_conf']['gfx_stack_code']
			self.kernel_branch = self.data['suite_conf']['kernel_branch']
			self.kernel_commit = self.data['suite_conf']['kernel_commit']
			self.igt_iterations = self.data['suite_conf']['igt_iterations']
			# Autouploader information
			self.currentEnv = self.data['autouploader']['currentEnv']
			self.currentPlatform = self.data['autouploader']['currentPlatform']
			self.currentRelease = self.data['autouploader']['currentRelease']
			self.currentSuite = self.data['autouploader']['currentSuite']
			self.currentTittle = self.data['autouploader']['currentTittle']
			self.reportTRC = self.data['autouploader']['trc_report']
			# Reports on linuxgraphics.intel.com
			self.backupReport = self.data['database']['upload_reports']
			# USB configuration
			self.custom_hostname = self.data['usb_conf']['custom_hostname']
			self.default_disk = self.data['usb_conf']['default_disk']
			self.default_image = self.data['usb_conf']['default_image']
			self.network_interface = self.data['usb_conf']['network_interface']
			self.server_user = self.data['usb_conf']['server_user']
			self.server_hostname = self.data['usb_conf']['server_hostname']
			self.server_partimag = self.data['usb_conf']['server_partimag']
			self.server_shared = self.data['usb_conf']['server_shared']
			self.usb_update_mode = self.data['usb_conf']['usb_update_mode']

		else:
			print red + '>>> (err) ' + end + 'config.yml does not exists'
			sys.exit()


	def message(self,messageType,message):
		if messageType == 'err':
			print red + '>>> (err) ' + end + message
		elif messageType == 'warn':
			print yellow + '>>> (warn) ' + end + message
		elif messageType == 'info':
			print blue + '>>> (info) ' + end + message
		elif messageType == 'ok':
			print green + '>>> (success) ' + end + message


	def boot_order(self,action):
		if not os.path.isfile(self.current_kernel_file):
			self.message('err','smi kernel driver is not compiled')
			sys.exit()
		else:
			check_status = self.b.get_output('cat ' + self.current_kernel_file + ' | tail -1')
			if check_status == 'FAIL':
				self.message('err','smi kernel driver was not compiled succcessfully')
				sys.exit()
			elif check_status == 'DONE':
				self.message('info','smi kernel driver was compiled succcessfully')
				self.message('info','checking if smi module is in the kernel (' + self.current_kernel + ')')
				check = os.system('lsmod | grep smi &> /dev/null')

				if check == 0:
					self.message('info','smi module is already in the kernel (' + self.current_kernel + ')')
				else:
					self.message('info','smi module is not in the kernel (' + self.current_kernel + ')')
					self.message('info','inserting smi kernel module ...')
					self.b.get_output('chmod +x ' + self.smi_module)
					check = os.system('sudo ' + self.smi_module + ' start')

					if check != 0:
						self.message('err','could not inserted smi kernel module')
						sys.exit()
					else:
						self.message('info','smi kernel module was inserted successfully in (' + self.current_kernel + ')')

				self.message('info','getting bios boot order')
				self.b.get_output('chmod +x ' + self.biosConf)
				pre_bios_boot_order = self.b.get_output('sudo ' + self.biosConf + ' bootorder get 2> /dev/null | grep ^[0:9] | awk \'{print $1 "-" $2}\'')
				check_usb = []
				bios_boot_order = []

				for element in pre_bios_boot_order.split():
					part_a = element.split('-')[0]
					part_b = element.split('-')[1]
					if part_b:
						bios_boot_order.append(part_a + '-' + part_b)
						check_usb.append(part_b)

				print check_usb

				self.message('info','checking if the USB is connected to the system')
				if not 'EFI USB Device' in check_usb:
					self.message('err','USB stick is not connected to the system')
					sys.exit()
				else:
					if action == 'setUSB':
						self.message('info','setting USB stick as top option in the bios')
						print 'complete it'
					elif action == 'checkUSB':
						self.message('info','checking if USB stick is the priority boot option')
						print 'complete it'


	def compile_module(self):

		if not os.path.isfile(self.current_kernel_file):
			self.message('info','(' + os.path.basename(self.current_kernel_file) + ') file does not exists, creating ...')
			self.message('info','current kernel is (' + self.current_kernel + ')')
			fich = open(self.current_kernel_file,'w')
			fich.write(self.current_kernel)
			fich.close()

			if os.path.exists(self.loc_smi_module_folder):
				self.message('info','(' + os.path.basename(self.loc_smi_module_folder) + ') exists, deleting ...')
				rmtree(self.loc_smi_module_folder)
			
			self.message('info','downloading (' + os.path.basename(self.loc_smi_module_folder) + ') from bifrost.intel.com ...')
			# scp does not allow (/) in the variables
			os.system('scp -q -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -r ' + self.server_user + '@' + self.server_hostname + ':' + self.ext_smi_module_folder + ' /home/custom')

			# we have to compile the smi module in each platform, otherwise the SMI would not be recognize the current kernel
			self.message('info','compiling smi kernel module for (' + self.current_kernel + ') ...')
			check = os.system('cd ' + self.loc_smi_module_folder + '/SMIDriver/Linux64/Release && make')

			if check == 0:
				self.message('info','smi kernel module was compiled successfully')
				with open(self.current_kernel_file,'a') as f:
					f.write('\nDONE')
				sys.exit()
			else:
				self.message('err','smi kernel module could not be compiled')
				self.message('info','removing (' + os.path.basename(self.loc_smi_module_folder) + ') ...')
				rmtree(self.loc_smi_module_folder)
				with open(self.current_kernel_file,'a') as f:
					f.write('\nFAIL')
				sys.exit()

		else:
			old_kernel_smi_compilation = self.b.get_output('cat ' + self.current_kernel_file + ' | head -1')

			if self.current_kernel != old_kernel_smi_compilation:
				self.message('warn','smi kernel module is not compiled for (' + self.current_kernel+ ')')
	
				if os.path.exists(self.loc_smi_module_folder):
					self.message('info','(' + os.path.basename(self.loc_smi_module_folder) + ') exists, deleting ...')
					rmtree(self.loc_smi_module_folder)

				self.message('info','downloading (' + os.path.basename(self.loc_smi_module_folder) + ') from bifrost.intel.com ...')
				# scp does not allow (/) in the variables
				os.system('scp -q -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -r ' + self.server_user + '@' + self.server_hostname + ':' + self.ext_smi_module_folder + ' /home/custom')

				# we have to compile the smi module in each platform, otherwise the SMI would not be recognize the current kernel
				self.message('info','compiling smi kernel module for (' + self.current_kernel + ') ...')
				check = os.system('cd ' + self.loc_smi_module_folder + '/SMIDriver/Linux64/Release && make')

				if check == 0:
					self.message('info','smi kernel module was compiled successfully')
					with open(self.current_kernel_file,'a') as f:
						f.write('\nDONE')
					sys.exit()
				else:
					self.message('err','smi kernel module could not be compiled')
					self.message('info','removing (' + os.path.basename(self.loc_smi_module_folder) + ') ...')
					rmtree(self.loc_smi_module_folder)
					with open(self.current_kernel_file,'a') as f:
						f.write('\nFAIL')
					sys.exit()
			else:
				self.message('info','smi kernel module is already compiled for (' + self.current_kernel+ ')')
				sys.exit()
			

	def menu(self):

		parser = argparse.ArgumentParser(description=cyan + 'Intel® Graphics for Linux*' + end, epilog=cyan + 'https://01.org/linuxgraphics' + end)
		parser.add_argument('-v','--version', dest='version', action='version', version='%(prog)s 2.0')
		parser.add_argument('-g','--get-bios-priority', dest='get', action='store_true', help='get first bios priority option set')
		parser.add_argument('-s','--set-usb-bios-priority', dest='set', action='store_true', help='set usb bios as top priority')
		parser.add_argument('-c','--compile', dest='compile', action='store_true', help='compile smi driver for the current kernel')
		
		args = parser.parse_args()

		if args.compile:
			self.compile_module()
		elif args.get:
			self.boot_order('checkUSB')
		elif args.set:
			self.boot_order('setUSB')

if __name__ == '__main__':
	Main().menu()
