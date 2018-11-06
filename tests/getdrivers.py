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

import platform
import subprocess
import os
import sys
import getopt
import re
import pdb

class Bash:
	def get_output(self, option):
		#proc = subprocess.Popen(option, stdout=subprocess.PIPE, shell=True)
		proc = subprocess.Popen(option, stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
		(out, err) = proc.communicate()
		out = out.strip()
		return out

	def run (self,cmd):
		subprocess.Popen(cmd, shell=True, executable='/bin/bash')

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

b = Bash()
program_name = os.path.basename(sys.argv[0])
program_version = "v1.0"
password='linux'
user = b.get_output('whoami')

class Validator:
	def __init__ (self, value, sentence):
		if value:
			if sentence.find('modesetting') == 0:
				print 'modesetting                 : ' + green + 'enabled' + end
				print 'modesetting compiled for    : ' + value + ' X.Org Video Driver'
			else:
				print sentence + value
			#print sentence + value

class Hardware:
	def __init__ (self):
		print '\n======================================'
		print '\t     Hardware'
		print '======================================'

		dut_model = {
			'BRASWELL':'Braswell',
			'LenovoG50-80':'Broadwell',
			'NUC5i7RYB':'Broadwell',
			'NUC5i5MYBE':'Broadwell',
			'NUC5i5RYB':'Broadwell',
			'06D7TR':'Sandy Bridge',
			'18F8':'Ivy Bridge',
			'0XR1GT':'Ivy Bridge',
			'02HK88':'Skylake',
			'NOTEBOOK':'Broxton-P',
			'SkylakeYLPDDR3RVP3':'Skylake-Y to Kabylake (RVP3)',
			'SkylakeUDDR3LRVP7':'Kabylake (RVP7)',
			'PortablePC':'Bay Trail-M (Toshiba)',
			'1589':'HP Z420 Workstation',
			'D54250WYK':'Haswell-Nuc',
			'NUC6i5SYB':'Skylake-Nuc',
			'NUC6i7KYB':'Skylake Canyon',
			'MS-B1421':'Kabylake-Nuc',
			'06CC14':'Kabylake-Laptop',
			'GLKRVP1DDR4(05)':'Geminilake',
		}

		self.motherboard_model = 'echo ' + password + " | sudo -S dmidecode -t 1 2> /dev/null | grep 'Product Name' | awk -F': ' '{print $2}' | sed 's/ //g'"
		self.motherboard_id = 'echo ' + password + " | sudo -S dmidecode -t 2 2> /dev/null | grep 'Product Name' | awk -F': ' '{print $2}' | sed 's/ //g'"
		self.form_factor = 'echo ' + password + " | sudo -S dmidecode -t 3 2> /dev/null | grep 'Type' | head -n 1 |awk -F': ' '{print $2}'"
		self.manufacturer = 'echo ' + password + " | sudo -S dmidecode -t 1 2> /dev/null | grep 'Manufacturer' | awk -F': ' '{print $2}' | sed 's/ //g'"
		self.cpu_family = 'echo ' + password + " | sudo -S dmidecode -t 4 2> /dev/null | grep 'Family:' | awk -F': ' '{print $2}'"
		self.cpu_family_id = "lscpu | grep -i 'cpu family' | awk -F':' '{print $2}' | tr -d ' '"
		self.cpu_info = "cat /proc/cpuinfo | grep 'model name' | head -n 1 | awk -F': ' '{print $2}'"
		self.gpu_card = 'echo ' + password + " | sudo -S lspci -v -s $(lspci |grep 'VGA compatible controller' |cut -d' ' -f 1) | grep 'VGA compatible controller' | awk -F': ' '{print $2}'"
		self.memory_ram = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')  # e.g. 4015976448
		self.memory_ram = str(round(self.memory_ram/(1024.**3),2)) + ' GB'  # e.g. 3.74
		self.memory_ram = 'echo ' + self.memory_ram
		self.max_ram = 'echo ' + password + " | sudo -S dmidecode -t 16 2> /dev/null | grep 'Maximum Capacity' | awk -F': ' '{print $2}'"
		self.display_res = "xdpyinfo 2> /dev/null | grep dimensions | awk '{print $2}'"
		self.cpu_thread = "lscpu | grep -w 'CPU(s):' | awk '{print $2}' | head -n 1"
		self.cpu_core = 'echo ' + password + " | sudo -S dmidecode 2> /dev/null | grep -B 15 'Thread Count:' | grep 'Core Count:' | sed 's/\t*Core Count: //g'"
		self.cpu_model = "lscpu | grep -i 'model:' | awk -F':' '{print $2}' | tr -d ' '"
		self.cpu_stepping = "lscpu | grep -i 'stepping:' | awk -F':' '{print $2}' | tr -d ' '"
		self.socket = 'echo ' + password + " | sudo -S dmidecode 2> /dev/null | grep -B 15 'Thread Count:' | grep 'Upgrade:' | sed 's/\t*Upgrade: //g'"
		self.signature = 'echo ' + password + " | sudo -S dmidecode | grep -A 6 'Processor Information' | grep 'Signature:' | sed 's/\t*Signature: //g'"
		self.hdd = 'echo ' + password + " | sudo -S lshw 2> /dev/null | grep -A 20 '*-scsi' | grep -A 10 '*-disk' | grep 'size:' | sed 's/ *size: //g'"
		self.currentCdClockFrequency = 'echo ' + password + ' | sudo -S cat /sys/kernel/debug/dri/0/i915_frequency_info 2> /dev/null | grep "Current CD clock frequency" | awk \'{print $5, $6}\''
		self.MaximumCdClockFrequency = 'echo ' + password + ' | sudo -S cat /sys/kernel/debug/dri/0/i915_frequency_info 2> /dev/null | grep "Max CD clock frequency" | awk \'{print $5, $6}\''
		self.displaysConnected = 'echo ' + password + ' | sudo -S cat /sys/kernel/debug/dri/0/i915_display_info 2> /dev/null | grep ^connector | grep -w connected | awk \'{print $4}\' | sed \'s/,//g\' | tr \'\n\' \' \''

		for c, v in dut_model.items():
			if c == b.get_output(self.motherboard_id):
				print str('platform                   : ') + v

		variables = [ self.motherboard_model, self.motherboard_id, self.form_factor, self.manufacturer, self.cpu_family, self.cpu_family_id, self.cpu_info, self.gpu_card,
		self.memory_ram, self.max_ram, self.display_res,self.cpu_thread,self.cpu_core,self.cpu_model,self.cpu_stepping,self.socket,self.signature,self.hdd,self.currentCdClockFrequency,
		self.MaximumCdClockFrequency,self.displaysConnected]
		sentences = ['motherboard model          : ', 'motherboard id             : ', 'form factor                : ', 'manufacturer               : ', 'cpu family                 : ',
		'cpu family id              : ', 'cpu information            : ', 'gpu card                   : ', 'memory ram                 : ', 'max memory ram             : ', 'display resolution         : ', 'cpu thread                 : ',
		'cpu core                   : ', 'cpu model                  : ', 'cpu stepping               : ', 'socket                     : ', 'signature                  : ', 'hard drive                 : ', 'current cd clock frequency : ',
		'maximum cd clock frequency : ', 'displays connected         : ']

		for (v,s) in zip(variables,sentences):
			Validator(b.get_output(v),s)


class Software:
	def __init__ (self):
		self.b = Bash()
		print '\n======================================'
		print '\t     Software'
		print '======================================'
		self.kernel = 'uname -r'
		self.hostname = 'echo $HOSTNAME'
		self.processor_architecture = "lscpu | grep -i architecture | awk -F':' '{print $2}' | sed s'/ //'g"
		self.os_version = "lsb_release -a 2> /dev/null | grep -i description | awk -F':' '{print $2}' | sed -e 's/^[ \t]*//'"
		self.os_codename = "lsb_release -a 2> /dev/null | grep -i codename | awk -F':' '{print $2}' | sed -e 's/^[ \t]*//'"
		self.kernel_driver = 'echo ' + password + " | sudo -S lspci -v -s $(lspci |grep 'VGA compatible controller' 2> /dev/null |cut -d' ' -f 1) | grep 'Kernel driver in use'  | awk -F': ' '{print $2}'"
		self.bios = 'echo ' + password + " | sudo -S dmidecode 2> /dev/null 2> /dev/null | grep 'BIOS Revision:' | awk '{print $3}'"
		self.bios_release_date = 'echo ' + password + " | sudo -S dmidecode 2> /dev/null | grep -A 6 'BIOS Information' | grep 'Release Date:' | sed 's/\t*Release Date: //g'"
		self.ksc = 'echo ' + password + " | sudo -S  dmidecode -t 0 2> /dev/null | grep 'Firmware Revision:' | awk '{print $3}' | sed 's/ //g'"
		# Hardware accelation
		self.checkX = self.b.get_output('ps -e | grep X')
		self.currentTTY = self.b.get_output('tty')
		textTTYs = ['/dev/tty1','/dev/tty2','/dev/tty3','/dev/tty4','/dev/tty5','/dev/tty6']

		if self.currentTTY in textTTYs:
			self.HardwareAcceleration = yellow + 'only available on X' + end
		else:
			self.Unity3Dsupported = '/usr/lib/nux/unity_support_test -p 2> /dev/null | sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g" | grep "Unity 3D" | grep yes | awk -F":" \'{print $2}\' | sed \'s/ //g\''
			self.Notsoftwarerendered = '/usr/lib/nux/unity_support_test -p 2> /dev/null | sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g" | grep "Not software" | grep yes | awk -F":" \'{print $2}\' | sed \'s/ //g\''
			checkA = self.b.get_output(self.Unity3Dsupported)
			checkB= self.b.get_output(self.Notsoftwarerendered)

			if checkA == 'yes' and checkB == 'yes':
				self.HardwareAcceleration = green + 'enabled' + end
			else:
				self.HardwareAcceleration = red + 'disabled' + end

		# Check for swap partition
		self.checkSwap = self.b.get_output('cat /proc/swaps | grep dev | awk \'{print $1}\'')

		if self.checkSwap:
			self.swap = green + 'enabled' + end + ' on (' + self.checkSwap + ')'
		else:
			self.swap = red + 'disabled' + end

		variables = [self.kernel,self.hostname,self.processor_architecture,self.os_version,self.os_codename,self.kernel_driver,self.bios,self.bios_release_date,self.ksc]
		sentences = ['kernel version              : ', 'hostname                    : ', 'architecture                : ', 'os version                  : ', 'os codename                 : ',
		'kernel driver               : ', 'bios revision               : ', 'bios release date           : ', 'ksc                         : ']
		for (v,s) in zip(variables,sentences):
			Validator(b.get_output(v),s)

		print 'hardware acceleration       : ' + self.HardwareAcceleration
		print 'swap partition              : ' + self.swap

	def firmware (self):
		print '\n======================================'
		print '\t     Firmware'
		print '======================================'
		dmc_fw_loaded = 'echo ' + password + " | sudo -S cat /sys/kernel/debug/dri/0/i915_dmc_info 2> /dev/null | grep 'fw loaded' | awk '{print $3}'"
		dmc_version = 'echo ' + password + " | sudo -S cat /sys/kernel/debug/dri/0/i915_dmc_info 2> /dev/null | grep 'version' | awk '{print $2}'"
		guc_fw_loaded = 'echo ' + password + " | sudo -S cat /sys/kernel/debug/dri/0/i915_guc_load_status 2> /dev/null | grep 'load' | awk -F': ' '{print $2}'"
		guc_version_wanted = 'echo ' + password + " | sudo -S cat /sys/kernel/debug/dri/0/i915_guc_load_status 2> /dev/null | grep 'wanted' | awk -F': ' '{print $2}'"
		guc_version_found = 'echo ' + password + " | sudo -S cat /sys/kernel/debug/dri/0/i915_guc_load_status 2> /dev/null | grep 'found' | awk -F': ' '{print $2}'"
		huc_fw_loaded = "[[ $(dmesg | grep -i huc | grep -i 'fetch SUCCESS, load SUCCESS') ]] && echo yes"
		variables = [dmc_fw_loaded,dmc_version,guc_fw_loaded,guc_version_wanted,guc_version_found,huc_fw_loaded]
		sentences = ['dmc fw loaded             : ', 'dmc version               : ', 'guc fw loaded             : ', 'guc version wanted        : ', 'guc version found         : ', 'huc fw loaded             : ']
		for (v,s) in zip(variables,sentences):
			Validator(b.get_output(v),s)

	def kernel_parameters (self):
		print '\n======================================'
		print '\t     kernel parameters'
		print '======================================'
		grub_parameters = "sed -n 11p /etc/default/grub | awk -F'GRUB_CMDLINE_LINUX_DEFAULT=' '{print $2}'"
		grub_parameters = b.get_output(grub_parameters).replace('"','')
		print grub_parameters + '\n'


class Drivers:
	def __init__ (self):
		print '\n======================================'
		print '\tGraphic drivers'
		print '======================================'
		self.mesa = "glxinfo 2>&1 | grep 'OpenGL version string:' | awk -F'Mesa ' '{print $2}' | tr -d ')'"
		#self.modesetting = "cat /opt/X11R7/var/log/Xorg.0.log  2> /dev/null | grep -i modesetting_drv.so | awk -F '/' '{print $NF}' 2> /dev/null"
		self.modesetting_compiled_for = "grep -A2 modesetting /opt/X11R7/var/log/Xorg.0.log | grep compiled | awk -F \"compiled for \" '{print $2}' | awk '{print $1}' | sed 's/,//g'"
		self.gfx_stack_code = "dpkg -l | awk '{print $2}' | grep '\-code-[0-9][0-9][0-9]' | awk -F'code-' '{print $2}'"

	def update_tool (self):
		self.xf86 = "grep 'LoadModule: \'intel\'' /opt/X11R7/var/log/Xorg.0.log -A5 2> /dev/null | grep compiled | awk -F'= ' '{print $2}'"
		self.xorgxserver = "cat /opt/X11R7/var/log/Xorg.0.log 2> /dev/null | grep 'X.Org X Server' | awk -F'Server ' '{print $2}' 2> /dev/null"
		self.libdrm = "dpkg -l | grep libdrm-dev | awk '{print $3}' | awk -F'-1' '{print $1}'"
		self.libva = "dpkg -l | grep libva1 | awk '{print $3}' | awk -F'-1' '{print $1}'"
		self.vaapiinteldriver = "dpkg -l | grep VAAPI | awk '{print $3}' | awk -F'-1' '{print $1}'"
		self.cairo = "dpkg -l | grep libcairo2-dev | awk '{print $3}' | awk -F'-2ubuntu2' '{print $1}'"
		self.intelgputools = "dpkg -l | grep intel-gpu-tools | awk '{print $3}'"
		variables = [self.mesa,self.xf86,self.modesetting_compiled_for,self.xorgxserver,self.libdrm,self.libva,self.vaapiinteldriver,self.cairo,self.intelgputools,self.gfx_stack_code]
		sentences = ['mesa                        : ', 'xf86-video-intel          : ', 'modesetting               : ', 'xorg-xserver                : ', 'libdrm                    : ',
		'libva                       : ','vaapi (intel-driver)        : ', 'cairo                       : ', 'intel-gpu-tools             : ']
		for (v,s) in zip(variables,sentences):
			Validator(b.get_output(v),s)

	def graphic_stack (self):
		self.xf86 = "grep -A2 intel_drv /opt/X11R7/var/log/Xorg.0.log 2> /dev/null | tail -n 1 | awk -F'module version = ' '{print $2}'"
		self.xf86_commit = "cat /opt/X11R7/var/log/Xorg.0.log 2> /dev/null | grep -i sna | awk -F'compiled from ' '{print $2}'"
		self.xorgxserver = "cat /opt/X11R7/var/log/Xorg.0.log 2> /dev/null | head -n 2 | grep X | awk -F'Server ' '{print $2}'"
		self.libdrm = "pkg-config --modversion libdrm_intel 2> /dev/null"
		self.vaapiinteldriver = "vainfo 2> /dev/null | grep -i 'Driver version' | awk -F'Driver version: ' '{print $2}'"
		self.cairo = 'pkg-config --modversion cairo 2> /dev/null'
		#b.run('Xorg -version &> /tmp/Xserver')
		#self.xserver = "cat /tmp/Xserver | grep -i 'x.org x server'"
		self.igt_tag = 'cd /home/' + user + '/intel-graphics/intel-gpu-tools/ 2> /dev/null && git describe'
		self.igt_commit = 'cd /home/' + user + '/intel-graphics/intel-gpu-tools/ 2> /dev/null && git log -n 1 --pretty=format:"%h"'
		variables = [ self.mesa, self.xf86, self.xf86_commit, self.modesetting_compiled_for, self.xorgxserver, self.libdrm, self.vaapiinteldriver, self.cairo, self.igt_tag,
		self.igt_commit]
		sentences = ['mesa                        : ', 'xf86-video-intel (tag)      : ', 'xf86-video-intel (commit)   : ', 'modesetting                 : ', 'xorg-xserver                : ',
		'libdrm                      : ', 'vaapi (intel-driver)        : ', 'cairo                       : ', 'intel-gpu-tools (tag)       : ', 'intel-gpu-tools (commit)    : ']
		for (v,s) in zip(variables,sentences):
			Validator(b.get_output(v),s)


class Generator:

	def __init__(self):
		# setting LIBGL_DEBUG to none
		os.environ['LIBGL_DEBUG'] = ''

	def update_tool (self):
		print blue + '\n======================================' + end
		print blue + '\tUpdate tool' + end
		print blue + '======================================' + end
		Soft = Software()
		Soft
		drivers = Drivers()
		drivers.update_tool()
		Hardware()
		Soft.firmware()
		Soft.kernel_parameters()

	def graphic_stack (self):
		print blue + '\n======================================' + end
		print blue + '\tGraphic stack' + end
		print blue + '======================================' + end
		Soft = Software()
		Soft
		drivers = Drivers()
		drivers.graphic_stack()
		Hardware()
		Soft.firmware()
		Soft.kernel_parameters()

def usage ():
	os.system('clear')
	print 'Usage for : ' + blue + program_name + end + '[options]\n'
	print '--help             show this help message and exit\n'
	print '--update-tool      show user environment for update tool\n'
	print '--graphic-stack    show user environment for graphic stack\n'


def main (argv):

	try:
		opts, args = getopt.getopt(argv, 'hug', ['help', 'update-tool', 'graphic-stack',])
	except getopt.GetoptError as err:
        # print help information and exit:
		print yellow + str(err) + end # will print something like "option -a not recognized"
		sys.exit(2)

	if not opts:
		os.system('clear')
		print blue + program_name + end + yellow +' requires an argument\n' + end
		print 'try with --help option\n'
		sys.exit()
	else:
		for option, argument in opts:

			if re.search(r'^'+option+'$', '-h') or re.search(r'^'+option+'$', '--help'):
				usage()
				sys.exit()
			elif re.search(r''+option+'', '-u') or re.search(r''+option+'', '--update-tool'):
				os.system('clear')
				action = Generator()
				action.update_tool()
				sys.exit()
			elif re.search(r'^'+option+'$', '-g') or re.search(r'^'+option+'$', '--graphic-stack'):
				action = Generator()
				action.graphic_stack()
				sys.exit()
			else:
				assert False, 'unhandled option'


if __name__ == "__main__":
	main(sys.argv[1:])