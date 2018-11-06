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
import subprocess
import yaml
import time
import shutil
import timeit
import socket
import smtplib
import re

from common import network

from shutil import copytree
from shutil import copyfile
from shutil import move
from tabulate import tabulate
from os import listdir
from os.path import isfile
from os.path import join


class Builder(object):

	def __init__(self, **kwargs):
		"""Class constructor

		:param kwargs:
			- config: the configuration file to built the graphic stack, the
			input file must be a yaml, the default configuration is in the
			current path.
		"""
		config_file = kwargs.get('config_file', 'config.yml')
		# environment variables
		os.environ['GIT_SSL_NO_VERIFY'] = '1'
		# load values from config.yml
		self.data = yaml.load(open(config_file))
		self.user = self.data['dut_config']['dut_user']
		self.package_name = self.data['package_config']['package_name']
		# fixing package name
		characters_not_allowed = '[#_\s\*\-]'
		self.package_name = re.sub(characters_not_allowed, '', self.package_name)
		
		self.latest_commits_value = self.data['latest_commits']['value']
		self.specific_commits_value = self.data['specific_commit']['value']

		# getting the ip
		self.ip = network.get_ip()

		self.thisPath = os.path.dirname(os.path.abspath(__file__))
		self.mainPath = '/home/' + self.user + '/intel-graphics'
		self.gfxDriversBackupPath = self.mainPath + '/gfx_drivers_backup'
		self.gfxToolsBackupPath = self.mainPath + '/gfx_tools_backup'
		self.randonNumber = self.b.get_output("od -vAn -N4 -tu4 < /dev/urandom | awk '{print $1}'")
		self.weekNumber = self.b.get_output('date +"%-V"')
		self.month = self.b.get_output('month=`date +"%b"`; echo ${month^^}') # uppercase
		self.weekDay = self.b.get_output('date +%A')
		self.year = self.b.get_output('date +%G')
		self.hour = self.b.get_output('date +%I-%M-%S')
		self.scriptName = os.path.basename(__file__)

		# patchwork options
		self.patchValues = self.data['patchwork']

		# mailing_list
		self.data['miscellaneous']['mailing_list']

		# === Clone urls ===
		self.cloneCairo = 'https://anongit.freedesktop.org/git/cairo'
		self.cloneVaapi = 'https://github.com/01org/intel-vaapi-driver.git'
		self.cloneLibva = 'https://github.com/01org/libva.git'
		self.cloneMesa = 'https://anongit.freedesktop.org/git/mesa/mesa.git'
		self.cloneXf86 =  'https://anongit.freedesktop.org/git/xorg/driver/xf86-video-intel.git'
		self.cloneDrm = 'https://anongit.freedesktop.org/git/mesa/drm.git'
		self.cloneXorgXserver = 'https://anongit.freedesktop.org/git/xorg/xserver.git'
		self.cloneXorgXserverMacros = 'https://anongit.freedesktop.org/git/xorg/util/macros.git'
		self.cloneIgt = 'https://anongit.freedesktop.org/git/xorg/app/intel-gpu-tools.git'
		self.cloneRendercheck = 'https://anongit.freedesktop.org/git/xorg/app/rendercheck.git'
		self.clonePiglit = 'http://anongit.freedesktop.org/git/piglit.git'
		self.cloneXfont = 'https://anongit.freedesktop.org/git/xorg/lib/libXfont.git'
		self.cloneVesa = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-video-vesa.git'
		self.cloneFbdev = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-video-fbdev.git'
		self.cloneEvdev = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-input-evdev.git'
		self.cloneKeyboard = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-input-keyboard.git'
		self.cloneXkeyboard = 'https://anongit.freedesktop.org/git/xkeyboard-config.git'
		self.cloneXkbcomp = 'https://anongit.freedesktop.org/git/xorg/app/xkbcomp.git'
		self.clonexf86inputjoystick = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-input-joystick.git'
		self.clonexf86inputlibinput = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-input-libinput.git'
		self.clonexf86inputmagictouch = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-input-magictouch.git'
		self.clonexf86inputmicrotouch = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-input-microtouch.git'
		self.clonexf86inputmouse = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-input-mouse.git'
		self.clonexf86inputmutouch = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-input-mutouch.git'
		self.clonexf86inputsynaptics = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-input-synaptics.git'
		self.clonexf86inputvmmouse = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-input-vmmouse.git'
		self.cloneglamor = 'https://anongit.freedesktop.org/git/xorg/driver/glamor.git'
		self.clonevmware = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-video-vmware.git'
		self.clonexf86videoqxl = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-video-qxl.git'
		self.cloneamdgpu = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-video-amdgpu.git'
		self.clonexf86videoati = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-video-ati.git'
		self.clonexf86videoradeonhd = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-video-radeonhd'
		self.clonexf86videomodesetting = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-video-modesetting.git'
		self.clonexproto = 'https://anongit.freedesktop.org/git/xorg/proto/xproto.git'
		self.clonexf86videochips = 'https://anongit.freedesktop.org/git/xorg/driver/xf86-video-chips.git'
		self.clonex11proto = 'https://anongit.freedesktop.org/git/xorg/proto/x11proto.git'
		self.clonelibxtrans = 'https://anongit.freedesktop.org/git/xorg/lib/libxtrans.git'
		self.clonelibX11 = 'https://anongit.freedesktop.org/git/xorg/lib/libX11.git'
		self.clonelibXext = 'https://anongit.freedesktop.org/git/xorg/lib/libXext.git'
		self.clonedri2proto = 'https://anongit.freedesktop.org/git/xorg/proto/dri2proto.git'
		self.cloneglproto = 'https://anongit.freedesktop.org/git/xorg/proto/glproto.git'
		self.clonelibpciaccess = 'https://anongit.freedesktop.org/git/xorg/lib/libpciaccess.git'
		self.clonepixman = 'https://anongit.freedesktop.org/git/pixman.git'
		self.clonelibvautils = 'https://github.com/01org/libva-utils.git'
		self.clonewaylandlibinput = 'https://anongit.freedesktop.org/git/wayland/libinput.git'
		self.clonelibXfont = 'https://anongit.freedesktop.org/git/xorg/lib/libXfont.git'
		self.clonexf86inputwacom = 'https://github.com/linuxwacom/xf86-input-wacom.git'
		self.clonexrdb = 'https://anongit.freedesktop.org/git/xorg/app/xrdb.git'

		# === Build options ===
		self.cores = int(self.b.get_output('nproc'))
		self.cores = self.cores + 2
		self.debianRootPath = self.mainPath + '/tmp.drivers'
		self.masterLocation = '/opt/X11R7'

		self.outputPath = self.masterLocation

		self.wo_driver_path = self.outputPath + '/lib/dri'
		self.debianPackages = self.mainPath + '/packages'
		self.prefix = self.outputPath
		self.libdir = self.outputPath + '/lib'
		self.libdir2 = self.outputPath + '/lib/x86_64-linux-gnu'

		# Build parameters
		self.eglPlatforms = 'x11,drm'
		self.drmBuildParamters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir2
		self.mesaBuildParameters_a = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir2 + ' --with-dri-drivers=i965,swrast --with-dri-driverdir=' + self.libdir + '/dri' # for 64bit
		self.mesaBuildParameters_b = '--enable-gles1 --enable-gles2  --enable-shared-glapi --with-egl-platforms=' + self.eglPlatforms +  ' --enable-texture-float --enable-gbm --enable-glx-tls --without-gallium-drivers --enable-debug'
		self.mesaBuildParameters = self.mesaBuildParameters_a + ' '  + self.mesaBuildParameters_b
		self.xf86BuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --enable-debug --enable-kms --enable-sna'
		self.libvaBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --enable-wayland=0'
		self.vaapiBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --enable-wayland=0'
		self.cairoBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.xorgXserverMacrosBuildParameters_a = '/bin/bash git_xorg.sh'
		self.xorgXserverMacrosBuildParameters_b = 'bash ./util/modular/build.sh -m /home/' + self.user + '/intel-graphics/mesa ' + self.prefix + ' -p pre-xserver -n'

		# the parameters with latest commit automated for config.yml
		self.xorgXserverBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --enable-ipv6 --enable-dri --enable-xvfb --enable-composite --enable-xcsecurity --enable-libunwind --enable-xorg --enable-xephyr --enable-glamor -enable-kdrive --enable-config-udev --enable-systemd-logind --enable-suid-wrapper --enable-dri3 --disable-install-setuid --enable-record --disable-static --libexecdir=' + self.libdir + '/xorg-server --sysconfdir=' + self.prefix + '/etc --sysconfdir=' + self.prefix + '/etc --localstatedir='+ self.prefix + '/var --with-xkb-path=' + self.prefix + '/share/X11/xkb --with-xkb-output=' + self.libdir + '/xkb --with-fontrootdir=/usr/share/fonts --with-sha1=libgcrypt --enable-debug'

		self.xf86videovesaBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.xf86videofbdevBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.xf86inputevdevBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --with-sdkdir=' + self.outputPath + '/include/xorg'
		self.xf86inputkeyboardBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.xkeyboardBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --with-xkb-rules-symlink=xfree86,xorg'
		self.xkbcompBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.xf86inputjoystickBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --with-sdkdir=' + self.outputPath + '/include/xorg'
		self.xf86inputlibinputBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --with-sdkdir=' + self.masterLocation + '/include/xorg'
		self.xf86inputmagictouchBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.xf86inputmicrotouchBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.xf86inputmouseBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --with-sdkdir=' + self.outputPath  + '/include/xorg'
		self.xf86inputmutouchBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --with-sdkdir=' + self.outputPath  + '/include/xorg'
		self.xf86inputsynapticsBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --with-sdkdir=' + self.outputPath + '/include/xorg' + ' --with-xorg-conf-dir=' + self.outputPath + '/share/X11/xorg.conf.d --enable-debug'
		self.xf86inputvmmouseBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --with-xorg-conf-dir=' + self.outputPath + '/share/X11/xorg.conf.d'
		self.xf86videovmwareBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.xf86videoqxlBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.amdBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --with-xorg-conf-dir=' + self.outputPath + '/share/X11/xorg.conf.d'
		self.xf86videoatiBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --with-xorg-conf-dir=' + self.outputPath + '/share/X11/xorg.conf.d'
		self.xf86videoradeonhdBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.xf86videomodesettingBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.xf86videochipsBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.macrosBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.xprotoBuildParameters =  './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.glamourBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --with-xorg-conf-dir=' + self.outputPath + '/share/X11/xorg.conf.d'
		self.igtBuildParameters_a = './autogen.sh --disable-chamelium'
		self.igtBuildParameters_b = './configure --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --disable-chamelium'
		self.rendercheckBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.x11protoBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.libxtransBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.libX11BuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.libXextBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.dri2protoBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.glprotoBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.libpciaccessglprotoBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir
		self.pixmanBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --enable-gtk'
		self.libvautilsBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --enable-drm --enable-x11'
		self.waylandlibinputlBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --disable-documentation'
		self.libXfontBuildParameters_a = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir2
		self.libXfontBuildParameters_b = './configure --prefix=' + self.prefix + ' --libdir=' + self.libdir2
		self.xf86inputwacomBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir + ' --with-xorg-conf-dir=' + self.outputPath + '/share/X11/xorg.conf.d'
		self.xrdbBuildParameters = './autogen.sh --prefix=' + self.prefix + ' --libdir=' + self.libdir

		# Checking for latest_commits/specific_commit value
		if self.latest_commits_value and self.specific_commits_value:
			self.message('err','specific_commit/latest_commits keys are set to True')
			print '>>> Please set one to False'
			sys.exit()
		if not self.latest_commits_value and not self.specific_commits_value:
			self.message('err','specific_commit/latest_commits keys are empty')
			print '>>> Please set at least one to True'
			sys.exit()

		# setting a master key
		if self.latest_commits_value:
			self.masterKey = self.data['latest_commits']
		elif self.specific_commits_value:
			self.masterKey = self.data['specific_commit']

		# checking drivers pre-requisites (for default 2D_Driver) ===
		if self.masterKey['xf86-video-intel'] or self.masterKey['xserver']:
			if self.data['2D_Driver']['sna'] and self.data['2D_Driver']['glamour']:
				self.message('err','sna/glamour keys are set to True')
				print '>>> Please set one to False'
				sys.exit()
			elif not self.data['2D_Driver']['sna'] and not self.data['2D_Driver']['glamour']:
				self.message('err','sna/glamour keys are empty')
				print '>>> Please set at least one to True'
				sys.exit()

	def environmentVariables(self):
		### Driver Graphics Stack path
		os.environ['INSTALL_ROOT'] = self.outputPath
		os.environ['PATH'] = os.environ['INSTALL_ROOT'] + '/bin:' + os.environ['PATH']
		os.environ['LIBGL_DRIVERS_PATH'] = os.environ['INSTALL_ROOT'] + '/lib/dri:' + os.environ['INSTALL_ROOT'] + '/lib'
		#os.environ['LD_LIBRARY_PATH'] = os.environ['INSTALL_ROOT'] + '/lib/' + os.environ['INSTALL_ROOT'] + '/lib32:/lib:/lib64:/usr/lib:/usr/lib64'
		os.environ['LD_LIBRARY_PATH'] = os.environ['INSTALL_ROOT'] + '/lib:' + os.environ['INSTALL_ROOT'] + '/lib/x86_64-linux-gnu:' + os.environ['INSTALL_ROOT'] + '/lib32:/lib:/lib/x86_64-linux-gnu:/lib64:/usr/lib:/usr/lib64' # comes from our bashrc
		os.environ['LIBGL_DEBUG'] = 'verbose'
		#os.environ['PKG_CONFIG_PATH'] = os.environ['INSTALL_ROOT'] + '/share/pkgconfig:' + os.environ['INSTALL_ROOT'] + '/lib/pkgconfig:/usr/lib/pkgconfig'
		os.environ['PKG_CONFIG_PATH'] = os.environ['INSTALL_ROOT'] + '/share/pkgconfig:' + os.environ['INSTALL_ROOT'] + '/lib/pkgconfig:' + os.environ['INSTALL_ROOT'] + '/lib/x86_64-linux-gnu/pkgconfig:/usr/share/pkgconfig:/usr/lib/x86_64-linux-gnu/pkgconfig:/usr/lib/pkgconfig'
		os.environ['SW'] = 'env LIBGL_ALWAYS_SOFTWARE=1'
		os.environ['LDFLAGS'] = ' -L' + os.environ['INSTALL_ROOT'] + '/lib' # libtool:   error: require no space between '-L' and os.environ['INSTALL_ROOT'] + '/lib'
		os.environ['ACLOCAL'] = 'aclocal -I ' + os.environ['INSTALL_ROOT'] + '/share/aclocal'
		os.environ['CMAKE_INCLUDE_PATH'] = os.environ['INSTALL_ROOT'] + '/include/'
		os.environ['CMAKE_LIBRARY_PATH'] = os.environ['INSTALL_ROOT'] + '/lib/'
		os.environ['LIBVA_DRIVERS_PATH'] = os.environ['INSTALL_ROOT'] + '/lib/dri'

	def getTime(self,action):
		if action == 'start':
			start = timeit.default_timer()
			os.environ['START_TIME'] = str(start)
		elif action == 'stop':
			stop = timeit.default_timer()
			total_time = stop - float(os.environ['START_TIME'])

			# output running time in a nice format.
			mins, secs = divmod(total_time, 60)
			hours, mins = divmod(mins, 60)
			message = 'elapsed time (' + str(int(hours)) + 'h:' + str(int(mins)) + 'm:' + str(int(secs)) + 's)'
			self.message('info',message)

	def driver_getTime(self,action):
		if action == 'start':
			start = timeit.default_timer()
			os.environ['D_START_TIME'] = str(start)
		elif action == 'stop':
			stop = timeit.default_timer()
			total_time = stop - float(os.environ['D_START_TIME'])

			# output running time in a nice format.
			mins, secs = divmod(total_time, 60)
			hours, mins = divmod(mins, 60)
			message = '(' + str(int(hours)) + 'h:' + str(int(mins)) + 'm:' + str(int(secs)) + 's)'
			return message

	def checkPatches(self,dictionary):

		if self.patchValues['checkBeforeBuild'] == True:
			for key,value in self.patchValues.items():
				if key == 'checkBeforeBuild':
					continue
				else:
					if value['apply'] == True:
						if not value['path']:
							self.message('err','[patchwork] (' + key + ') path key is empty')
							sys.exit()
						elif not os.path.exists(value['path']):
							self.message('err','[patchwork] (' + key + ') path key does not exists')
							sys.exit()
						elif os.path.exists(value['path']):
							# check is the patch is able to apply in the driver/tool
							checkCommitToApply = self.masterKey[key] # this could be True/False or a SHA1
							if checkCommitToApply == False:
								self.message('err','[patchwork] (' + key + ') will be not build, please set to True in [latest_commits/specific_commit]')
								sys.exit()
							#elif checkCommitToApply == True:
							else:
								# checking if the patch could be apply
								for driver in dictionary:
									for k,v in driver.items():
										if key == k:
											commitToApply = v['commit']
											# copying the driver to tmp in order to apply the patch
											if os.path.exists('/tmp/' + k):
												self.message('warn','folder : (' + '/tmp/' + k + ') exits, deleting ...')
												shutil.rmtree('/tmp/' + k)
											copytree(self.gfxDriversBackupPath + '/' + k, '/tmp/' + k)

											# copying the patch/mbox to tmpFolder
											base = os.path.basename(value['path'])
											fileName = os.path.splitext(base)[0]
											extension = os.path.splitext(base)[1]
											if extension == '.patch':
												# https://git-scm.com/docs/git-apply
												# instead of applying the patch, output diffstat for the input. Turns off "apply".
												cmd = 'git apply --stat --verbose '
											elif extension == '.mbox':
												# https://git-scm.com/docs/git-am
												cmd = 'git am '

											tmpFolder = '/tmp/' + k
											self.message('info','copying [' + extension.replace('.','') + '] to ' + tmpFolder)
											copyfile(value['path'], tmpFolder + '/' + fileName + extension)
											self.message('info','git checkout (' + v['commit'] + ') ...')
											os.system('cd ' + tmpFolder + ' && git checkout ' + v['commit'] + ' 2>1 /dev/null')
											self.message('info','testing [' + fileName + extension + '] ...')
											self.message('cmd',cmd + fileName + extension)
											checkPatchStatus = os.system('cd ' + tmpFolder + ' && ' + cmd + fileName + extension)
											if checkPatchStatus == 0:
												self.message('ok','the [' + extension.replace('.','') + '] was tested successfully on (' + key + ')')
												if os.path.exists('/tmp/' + k):
													self.message('info','deleting tmp folder (' + k + ') ...')
													shutil.rmtree('/tmp/' + k)
											else:
												self.message('err','the [' + extension.replace('.','') + '] was failed')
												self.b.get_output('cd ' + tmpFolder + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
												if os.path.exists('/tmp/' + k):
													self.message('info','deleting tmp folder (' + k + ') ...')
													shutil.rmtree('/tmp/' + k)
												sys.exit()

	def build(self):

		self.getTime('start')
		os.system('clear')
		print '\n\n ========================================='
		print ' === Intel Graphics for linux | 01.org ==='
		print ' ========================================= \n\n'
		self.checkIP()
		self.checkRoot()


		# === Checking drivers pre-requisites (for driver compilation) ===
		# ((mesa needs of drm to be compiled))
		if self.masterKey['mesa'] and not self.masterKey['drm']:
			self.message('err','mesa needs of drm to be compiled, please set drm in config.yml')
			sys.exit()
		# ((vaapi (intel-driver) needs for libva to be compiled))
		if self.masterKey['intel-vaapi-driver'] and not self.masterKey['libva']:
			self.message('err','intel-vaapi-driver needs of libva to be compiled, please set libva in config.yml')
			sys.exit()
		# ((xorg-xserver-macros needs for mesa to be compiled))
		#if self.masterKey['macros'] and not self.masterKey['mesa']:
		#	self.message('err','macros needs of mesa to be compiled, please set mesa in config.yml')
		#	sys.exit()
		# ((xserver needs of xf86-video-intel in order that 2D works on the DUTs))
		'''if self.masterKey['xserver'] and not self.masterKey['xf86-video-intel']:
			self.message('err','xserver needs of xf86-video-intel to be compiled, please set xf86-video-intel in config.yml')
			sys.exit()
		elif self.masterKey['xf86-video-intel'] and not self.masterKey['xserver']:
			self.message('err','xf86-video-intel needs of xserver to be compiled, please set xserver in config.yml')
			sys.exit()'''
		# ((intel-gpu-tools needs of cairo and drm))
		'''if self.masterKey['intel-gpu-tools'] and not self.masterKey['drm'] and not self.masterKey['cairo']:
			self.message('err','intel-gpu-tools needs of drm && cairo to be compiled, please set drm && cairo in config.yml')
			sys.exit()
		elif self.masterKey['intel-gpu-tools'] and not self.masterKey['drm']:
			self.message('err','intel-gpu-tools needs of drm to be compiled, please set drm in config.yml')
			sys.exit()
		elif self.masterKey['intel-gpu-tools'] and not self.masterKey['cairo']:
			self.message('err','intel-gpu-tools needs of cairo to be compiled, please set cairo in config.yml')
			sys.exit()
		elif self.masterKey['intel-gpu-tools'] and not self.masterKey['piglit']:
			self.message('err','intel-gpu-tools needs of piglit to be compiled, please set piglit in config.yml')
			sys.exit()'''

		# === Checking gfx_drivers download time ===
		pathList = [self.gfxDriversBackupPath]

		for folder in pathList:
			if os.path.exists(folder):
				#a=os.path.getctime(folder)
				file_mod_time = os.stat(folder).st_mtime # last modification time
				should_time = time.time() - (30 * 60) # current time
				last_time = (time.time() - file_mod_time) / 60 # minutes value
				last_time = last_time / 60 # hours value with decimals
				if int(last_time) > self.data['miscellaneous']['maximum_permitted_time']:
					self.message('warn',folder + ' has been downloaded (' + str(round(last_time,2)) + ') hours ago, removing ...')
					shutil.rmtree(folder)

		########################## ADD MORE DRIVERS HERE ####################################
		# === Generating a list of the drivers/tools urls to clone (here i can add more)  ===
		# === here we have to modified something if we change the keys name in config.yml ===
		########################## ADD MORE DRIVERS HERE ####################################

		urlsDict = [{'drm':self.cloneDrm}, {'mesa':self.cloneMesa}, {'xf86-video-intel':self.cloneXf86}, {'intel-vaapi-driver':self.cloneVaapi}, {'libva':self.cloneLibva}, {'cairo':self.cloneCairo},
		{'macros':self.cloneXorgXserverMacros}, {'xserver':self.cloneXorgXserver}, {'intel-gpu-tools':self.cloneIgt},
		{'rendercheck':self.cloneRendercheck}, {'piglit':self.clonePiglit},{'xf86-video-vesa':self.cloneVesa},{'xf86-video-fbdev':self.cloneFbdev},{'xf86-input-evdev':self.cloneEvdev},
		{'xf86-input-keyboard':self.cloneKeyboard},{'xkeyboard-config':self.cloneXkeyboard},{'xkbcomp':self.cloneXkbcomp},{'xf86-input-joystick':self.clonexf86inputjoystick},{'xf86-input-libinput':self.clonexf86inputlibinput},
		{'xf86-input-magictouch':self.clonexf86inputmagictouch},{'xf86-input-microtouch':self.clonexf86inputmicrotouch},{'xf86-input-mouse':self.clonexf86inputmouse},{'xf86-input-mutouch':self.clonexf86inputmutouch},
		{'xf86-input-synaptics':self.clonexf86inputsynaptics},{'xf86-input-vmmouse':self.clonexf86inputvmmouse},{'glamor':self.cloneglamor},{'xf86-video-vmware':self.clonevmware},{'xf86-video-qxl':self.clonexf86videoqxl},
		{'xf86-video-amdgpu':self.cloneamdgpu},{'xf86-video-ati':self.clonexf86videoati},{'xf86-video-radeonhd':self.clonexf86videoradeonhd},{'xf86-video-modesetting':self.clonexf86videomodesetting},{'xproto':self.clonexproto},
		{'pixman':self.clonepixman},{'xf86-video-chips':self.clonexf86videochips},{'x11proto':self.clonex11proto},{'libxtrans':self.clonelibxtrans},{'libX11':self.clonelibX11},{'libXext':self.clonelibXext},{'dri2proto':self.clonedri2proto},
		{'glproto':self.cloneglproto},{'libpciaccess':self.clonelibpciaccess},{'libva-utils':self.clonelibvautils},{'libinput':self.clonewaylandlibinput},{'libXfont':self.clonelibXfont},{'xf86-input-wacom':self.clonexf86inputwacom},{'xrdb':self.clonexrdb}]



		# === Getting a list of the drivers to be compiled ===
		driversToCompile = []
		for driver,value in self.masterKey.items():
			if driver == 'value':
				continue
			else:
				if value:
					for url in urlsDict:
						for k,v in url.items():
							if k == driver:
								for key2,value2 in url.items():
									driverName = value2.rsplit('/', 1)[1].replace('.git','')
									driversToCompile.append({driverName:{'url':v,'commit':value}})	# here i add the driver name no matters who it is in config.yml, the driver name is based in the url

		# === Downloading the drivers/tools (only if the driver/tool folder does not exist)	===
		for driver in driversToCompile:
			for k,v in driver.items():
				folder = v['url'].rsplit('/', 1)[1].replace('.git','') # this is the real driver name
				if not os.path.exists(self.gfxDriversBackupPath + '/' + folder):
					self.message('info','Downloading (' + folder + ') ...')
					if not os.path.exists(self.gfxDriversBackupPath):
						os.makedirs(self.gfxDriversBackupPath)
					check = os.system('cd ' + self.gfxDriversBackupPath + ' && git clone ' + v['url'])
					if check != 0:
						self.message('err','Something unexpected happened')
						sys.exit()
					# Downloading xfont2 (for xserver driver)
					if folder == "xserver":
						check = os.system('cd ' + self.gfxDriversBackupPath + ' && git clone ' + self.cloneXfont)
						if check != 0:
							self.message('err','Something unexpected happened')
							sys.exit()

		# === Checking if the repos are up-to-date ===
		for driver in driversToCompile:
			for k,v in driver.items():
				folder = v['url'].rsplit('/', 1)[1].replace('.git','')
				# so far all the repositories from this scripts points to master branch by default
				branch_to_check = 'master'
				if os.path.exists(self.gfxDriversBackupPath + '/' + folder):
					self.message('info','checking if (' + k + ') is up-to-date ...')
					currentCommit = self.b.get_output('cd ' + self.gfxDriversBackupPath + '/' + folder + ' && git rev-parse HEAD')
					latestCommit = self.b.get_output('cd ' + self.gfxDriversBackupPath + '/' + folder + ' && git ls-remote origin ' + branch_to_check + ' | awk \'{print $1}\' | head -1')
					latestCommit_information = self.b.get_output('cd ' + self.gfxDriversBackupPath + '/' + folder + ' && git show ' + latestCommit + ' --format=fuller 2> /dev/null')

					out_message = yellow + 'out-to-date' + end
					in_message = green + 'up-to-date' + end
					if currentCommit != latestCommit:
						self.message('warn','(' + k + ') is ' + out_message + ', updating ...')
						self.b.get_output('cd ' + self.gfxDriversBackupPath + '/' + folder + ' && git pull origin ' + branch_to_check,'git pull origin ' + branch_to_check,True)
						self.b.get_output('cd ' + self.gfxDriversBackupPath + '/' + folder + ' && git reset --hard origin/' + branch_to_check,'git reset --hard origin/' + branch_to_check,True)
					else:
						self.message('info','(' + k + ') is ' + in_message)

					# checking the current branch in the tree
					currentBranch = self.b.get_output('cd ' + self.gfxDriversBackupPath + '/' + folder + ' && git symbolic-ref --short HEAD')

					if currentBranch != branch_to_check:
						self.message('warn','current branch for (' + k + ') is : (' + currentBranch + ')')
						self.message('info','changing to (' + branch_to_check + ') ...')
						self.b.get_output('cd ' + self.gfxDriversBackupPath + '/' + folder + ' && git checkout ' + branch_to_check,'git checkout ' + branch_to_check,True)
					else:
						self.message('info','current branch for (' + k + ') is : (' + currentBranch + ')')

		# === Checking for commits ===
		for driver in driversToCompile:
			for k,v in driver.items():
				folder = v['url'].rsplit('/', 1)[1].replace('.git','')
				if os.path.exists(self.gfxDriversBackupPath + '/' + folder):
					# Checking for latest commits
					index = driversToCompile.index({k:v})
					if v['commit'] and self.latest_commits_value == True:
						# this mean that the driver will compile with latest commit
						latest_commit = self.b.get_output('cd ' + self.gfxDriversBackupPath + '/' + folder + ' && git rev-parse HEAD')
						self.message('info','(' + k + ') will be build with latest commit from (' + v['url'] + ')')
						self.message('info','(' + k + ') will be build with : (' + latest_commit + ')')
						# Adding the latest_commit to driversToCompile list
						#index = driversToCompile.index({k:v})
						driversToCompile[index] = {k:{'url':v['url'],'commit':latest_commit}}
					elif v['commit'] and self.specific_commits_value == True:
						#self.message('info','(' + k + ') will be build with specific commit from (' + v['url'] + ')')
						self.message('info','(' + k + ') will be build with specific commit from (' + driversToCompile[index][k]['commit'] + ')')
					# Checking if the SHA1 entered is valid commit
					validateCommit = self.b.get_output('cd ' + self.gfxDriversBackupPath + '/' + folder + ' && git log -n 1 --pretty=format:%ar ' + driversToCompile[index][k]['commit'] + ' 2> /dev/null')
					if not validateCommit:
						self.message('err','(' + k + ') commit is not valid (' + yellow + driversToCompile[index][k]['commit'] + end + ')')
						sys.exit()
					else:
						self.message('info','valid commit for (' + k + ') (' + green + driversToCompile[index][k]['commit'] + end + ')')
				else:
					self.message('err','(' + folder + ') does not exists')
					sys.exit()

		# === Printing a table with the drivers to compile ===
		message_headers = [blue + '#' + end, blue + 'Driver' + end, blue + 'Commit' + end,blue + 'Tag' + end,blue + 'Author' + end,blue + 'Age' + end]
		message_launch = []
		count = 1
		for driver in driversToCompile:
			for k,v in driver.items():
				folder = v['url'].rsplit('/', 1)[1].replace('.git','')
				currentDriverPath = self.gfxDriversBackupPath + '/' + folder
				currentCommit = self.b.get_output('echo ' + v['commit'] + ' | head -c 7')
				current_commit_full = v['commit']
				
				if os.path.exists(currentDriverPath):
					# Getting git variables
					if k == 'piglit':
						tag = self.b.get_output('cd ' + currentDriverPath + ' && git describe --tags')
					else:
						tag = self.b.get_output('cd ' + currentDriverPath + ' && git describe')
					remove_tag_id = tag.split('-')[-1]
					if remove_tag_id:
						tag = tag.replace('-' + remove_tag_id,'')
					author = self.b.get_output('cd ' + currentDriverPath + ' && git show ' + current_commit_full + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d , | sed -e \'s/</(/g\' -e \'s/>/)/g\'')
					author = author.decode('unicode_escape').encode('ascii','ignore') # removing unicode characteres
					age_A = self.b.get_output('cd ' + currentDriverPath + ' && git show -s --format=%cd ' + current_commit_full + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
					remove_age_A_time = age_A.split()[-1]
					age_A = age_A.replace(remove_age_A_time,'')
					age_B = self.b.get_output('cd ' + currentDriverPath + ' && git show -s --format=%cr ' + current_commit_full + ' | tail -1') # e.g : 9 days ago
					concatenate = age_A + '(' + age_B + ')'
					updateRows = [blue + str(count) + end,str(k),str(currentCommit),str(tag),str(author),str(concatenate)]
					message_launch.append(updateRows)
					count += 1

		self.message('info','The following drivers will be compiled')
		try:
			t = tabulate(message_launch, headers=message_headers, missingval='?', stralign='left', tablefmt='fancy_grid').encode('utf-8')
		except:
			self.message('warn','the table could not be printed')
		else:
			print t

		# === checking for patches ===
		self.checkPatches(driversToCompile)

		# === Creating the package folder ===
		if not os.path.exists(self.debianPackages):
			os.makedirs(self.debianPackages)

		folderToNotRemove = ['gfx_drivers_backup','packages']
		# === Removing driver folders ===
		for root, dirs, files in os.walk(self.mainPath):
			for f in folderToNotRemove:
				dirs.remove(f) # do not remove this folders
			for d in dirs:
				shutil.rmtree(root + '/' + d)

		# === Copying driver folders ===
		for root, dirs, files in os.walk(self.gfxDriversBackupPath, topdown=False):
			dirList = dirs

		# === Getting only the keys of the drivers to compile ===
		onlyKeys = []
		for d in driversToCompile:
			onlyKeys.append(str(d.keys()).strip("[]").strip("'"))
		for s in dirList:
			if s in onlyKeys:
				copytree(self.gfxDriversBackupPath + '/' + s, self.mainPath + '/' + s)

		# === Compiling drivers (we can add more drivers for compile) ===

		# we'll to create a folder inside of (self.mainPath) to save temporally the drivers to compile

		# pre-conditions ((checking for tmp.drivers folder))
		if os.path.exists(self.outputPath):
			shutil.rmtree(self.outputPath)
		if not os.path.exists(self.outputPath):
			os.makedirs(self.outputPath + '/share/aclocal')


		########################## ADD MORE DRIVERS HERE ###################################
		# === Sorting the list of dicts (add more drivers) ===
		########################## ADD MORE DRIVERS HERE ###################################


		for element in driversToCompile: # element is a list
			for k,v in element.items():
				index = driversToCompile.index(element)
				if k == 'drm':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':1}}
				elif k == 'mesa':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':2}}
				elif k == 'macros':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':3}}
				elif k == 'xproto':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':4}}
				elif k == 'glproto':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':5}}
				elif k == 'dri2proto':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':6}}
				elif k == 'xserver':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':7}}
				elif k == 'libXfont':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':8}}
				elif k == 'xf86-input-evdev':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':9}}
				elif k == 'xf86-input-libinput':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':10}}
				elif k == 'xf86-video-fbdev':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':11}}
				elif k == 'xf86-video-vesa':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':12}}
				elif k == 'xf86-video-vmware':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':13}}
				elif k == 'xf86-video-qxl':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':14}}
				elif k == 'xf86-video-amdgpu':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':15}}
				elif k == 'xf86-video-ati':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':16}}
				elif k == 'xf86-video-chips':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':17}}
				elif k == 'x11proto':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':18}}
				elif k == 'libxtrans':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':19}}
				elif k == 'libX11':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':20}}
				elif k == 'libXext':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':21}}
				elif k == 'xrdb':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':22}}
				elif k == 'xf86-video-intel':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':23}}
				elif k == 'xkbcomp':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':24}}
				elif k == 'xf86-input-wacom':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':25}}
				elif k == 'pixman':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':26}}
				elif k == 'libpciaccess':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':27}}
				elif k == 'libinput':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':28}}
				elif k == 'xkeyboard-config':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':29}}
				elif k == 'xf86-input-mouse':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':30}}
				elif k == 'xf86-input-keyboard':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':31}}
				elif k == 'xf86-input-joystick':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':32}}
				elif k == 'xf86-input-magictouch':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':33}}
				elif k == 'xf86-input-microtouch':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':34}}
				elif k == 'xf86-input-mutouch':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':35}}
				elif k == 'xf86-input-synaptics':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':36}}
				elif k == 'xf86-input-vmmouse':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':37}}
				elif k == 'xf86-video-radeonhd':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':38}}
				elif k == 'xf86-video-modesetting':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':39}}
				elif k == 'glamor':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':40}}
				elif k == 'libva':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':41}}
				elif k == 'libva-utils':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':42}}
				elif k == 'intel-vaapi-driver':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':43}}
				elif k == 'cairo':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':44}}
				elif k == 'intel-gpu-tools':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':45}}
				elif k == 'piglit':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':46}}
				elif k == 'rendercheck':
					for v in driversToCompile[index].values():
						driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':47}}

		driversToCompile.sort(key=lambda x: list(x.values())[0]['location']) # here i am sorting the list because is hight important that certain drivers will be build before of after some others


		########################## ADD MORE DRIVERS HERE ###################################
		# Compiling the drivers (add more drivers)
		########################## ADD MORE DRIVERS HERE ###################################

		count = 1
		for driver in driversToCompile:
			totalDrivers = len(driversToCompile)
			progress = '(' + str(count) + '/' + str(totalDrivers) + ')'
			for k,v in driver.items():
				url = v['url']
				commit = v['commit']

				if k == 'drm':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					################################# debug field ##############################
					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					################################# debug field ##############################

					# build parameters
					self.message('info',self.drmBuildParamters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.drmBuildParamters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'drm':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'mesa':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					# drm version from the system
					drmSystemVersion = self.b.get_output('pkg-config --modversion libdrm_intel')
					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					self.message('info','(PKG_CONFIG_PATH) = ' + os.environ['PKG_CONFIG_PATH'])
					# drm version from the current gfx stack
					drmStackVersion = self.b.get_output('pkg-config --modversion libdrm_intel')
					self.message('info','drm system version : (' + drmSystemVersion + ')')
					self.message('info','drm stack version  : (' + drmStackVersion + ')')
					self.message('info','mesa needs at least drm version 2.4.61 to be compiled')
					# build parameters
					self.message('info','./autogen.sh ...') # this only to show a few commands because mesa build parameters are too long
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.mesaBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'mesa':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-video-intel':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					# build parameters
					self.message('info',self.xf86BuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86BuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-video-intel':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-video-vesa':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					os.environ['XORG_CFLAGS'] = '-fvisibility=hidden -I' + os.environ['INSTALL_ROOT']  + '/include/xorg -I/usr/include/xorg -I/usr/include/X11/dri -I/usr/include/pixman-1 -I/usr/include/libdrm'
					# build parameters
					self.message('info',self.xf86videovesaBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86videovesaBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-video-vesa':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-video-fbdev':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					os.environ['XORG_CFLAGS'] = '-fvisibility=hidden -I' + os.environ['INSTALL_ROOT']  + '/include/xorg -I/usr/include/xorg -I/usr/include/X11/dri -I/usr/include/pixman-1 -I/usr/include/libdrm'
					'''os.system('unset ' + os.environ['INSTALL_ROOT'])
					os.system('unset ' + os.environ['PATH'])
					os.system('unset ' + os.environ['LIBGL_DRIVERS_PATH'])
					os.system('unset ' + os.environ['LD_LIBRARY_PATH'])
					os.system('unset ' + os.environ['LIBGL_DEBUG'])
					os.system('unset ' + os.environ['PKG_CONFIG_PATH'])
					os.system('unset ' + os.environ['SW'])
					os.system('unset ' + os.environ['LDFLAGS'])
					os.system('unset ' + os.environ['ACLOCAL'])
					os.system('unset ' + os.environ['CMAKE_INCLUDE_PATH'])
					os.system('unset ' + os.environ['CMAKE_LIBRARY_PATH'])
					os.system('unset ' + os.environ['LIBVA_DRIVERS_PATH'])'''

					# build parameters
					self.message('info',self.xf86videofbdevBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86videofbdevBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-video-fbdev':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-input-evdev':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					# build parameters
					self.message('info',self.xf86inputevdevBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86inputevdevBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-input-evdev':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-input-keyboard':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.xf86inputkeyboardBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86inputkeyboardBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-input-keyboard':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xkeyboard-config':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.xkeyboardBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xkeyboardBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xkeyboard-config':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xkbcomp':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.xkbcompBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xkbcompBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xkbcomp':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-input-joystick':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					# build parameters
					self.message('info',self.xf86inputjoystickBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86inputjoystickBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-input-joystick':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-input-libinput':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					# build parameters
					self.message('info',self.xf86inputlibinputBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86inputlibinputBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-input-libinput':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-input-magictouch':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					# build parameters
					self.message('info',self.xf86inputmagictouchBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86inputmagictouchBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-input-magictouch':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-input-microtouch':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					# build parameters
					self.message('info',self.xf86inputmicrotouchBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86inputmicrotouchBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-input-microtouch':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-input-mouse':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.xf86inputmouseBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86inputmouseBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-input-mouse':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-input-mutouch':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					# build parameters
					self.message('info',self.xf86inputmutouchBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86inputmutouchBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-input-mutouch':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-input-synaptics':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.xf86inputsynapticsBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86inputsynapticsBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-input-synaptics':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-input-wacom':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# Bug 901333 - aclocal fails with "couldn't open directory 'm4': No such file or directory"
					# reference : https://bugzilla.redhat.com/show_bug.cgi?id=901333
					self.message('info','creating (m4) directory into (' + os.path.join(self.mainPath,k) + ')')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + ' && aclocal --install')
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.xf86inputwacomBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86inputwacomBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-input-wacom':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-input-vmmouse':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					# build parameters
					self.message('info',self.xf86inputvmmouseBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86inputvmmouseBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-input-vmmouse':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-video-vmware':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.xf86videovmwareBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86videovmwareBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-video-vmware':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-video-qxl':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.xf86videoqxlBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86videoqxlBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-video-qxl':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-video-amdgpu':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)


					# Bug 901333 - aclocal fails with "couldn't open directory 'm4': No such file or directory"
					# reference : https://bugzilla.redhat.com/show_bug.cgi?id=901333
					self.message('info','creating (m4) directory into (' + os.path.join(self.mainPath,k) + ')')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + ' && aclocal --install')
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.amdBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.amdBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-video-amdgpu':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-video-ati':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.xf86videoatiBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86videoatiBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-video-ati':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-video-radeonhd':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					# build parameters
					self.message('info',self.xf86videoradeonhdBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86videoradeonhdBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-video-radeonhd':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-video-modesetting':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					# build parameters
					self.message('info',self.xf86videomodesettingBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86videomodesettingBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					#output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make')
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-video-modesetting':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xf86-video-chips':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.xf86videochipsBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xf86videochipsBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					#output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make')
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xf86-video-chips':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'pixman':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.pixmanBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.pixmanBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					#output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make')
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'pixman':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xproto':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					# build parameters
					self.message('info',self.xprotoBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xprotoBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					#output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make')
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xproto':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'glamor':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					#os.environ['XORG_CFLAGS'] = '-fvisibility=hidden -I' + self.outputPath + '/include/X11/dri -I' + self.outputPath + '/include/pixman-1 -I' + self.outputPath + '/include/libdrm -I' + self.outputPath + '/include/xorg'
					#os.environ['XORG_CFLAGS'] = self.outputPath + '/include/xorg'

					# build parameters
					self.message('info',self.glamourBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.glamourBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'glamor':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'libva':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.libvaBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.libvaBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'libva':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'libva-utils':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.libvautilsBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.libvautilsBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'libva-utils':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'intel-vaapi-driver':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					libvaSystemVersion = self.b.get_output('pkg-config --modversion libva')
					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					self.message('info','(PKG_CONFIG_PATH) = ' + os.environ['PKG_CONFIG_PATH'])
					libvaStackVersion = self.b.get_output('pkg-config --modversion libva')
					self.message('info','libva system version : (' + libvaSystemVersion + ')')
					self.message('info','libva stack version  : (' + libvaStackVersion + ')')
					self.message('info','intel-vaapi-driver needs at least libva version 0.39.2 to be compiled')

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.vaapiBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.vaapiBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'intel-vaapi-driver':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'libinput':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					# build parameters
					self.message('info',self.waylandlibinputlBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.waylandlibinputlBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'libinput':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'cairo':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					# build parameters
					self.message('info',self.cairoBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.cairoBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'cairo':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'macros':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.macrosBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.macrosBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'macros':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'x11proto':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.x11protoBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.x11protoBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'x11proto':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'libxtrans':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.libxtransBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.libxtransBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'libxtrans':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'libX11':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.libX11BuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.libX11BuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'libX11':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'libXext':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.libXextBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.libXextBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'libXext':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xrdb':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.xrdbBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xrdbBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xrdb':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'dri2proto':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.dri2protoBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.dri2protoBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'dri2proto':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'glproto':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.glprotoBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.glprotoBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'glproto':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'libpciaccess':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# build parameters
					self.message('info',self.libpciaccessglprotoBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.libpciaccessglprotoBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'libpciaccess':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'macros2':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')

					if not os.path.exists(self.mainPath + '/xorg-xserver-macros'):
						os.makedirs(self.mainPath + '/xorg-xserver-macros')
					# copying build.sh, git_xorg.sh to xorg-xserver-macros
					os.system('cp ' + self.thisPath + '/tools/build.sh ' + self.thisPath + '/tools/git_xorg.sh ' + self.mainPath + '/xorg-xserver-macros')

					# compiling git_xorg.sh
					self.message('info',self.xorgXserverMacrosBuildParameters_a)
					output = os.system('cd ' + self.mainPath + '/xorg-xserver-macros && timeout 240 ' + self.xorgXserverMacrosBuildParameters_a) # the timeout here is due to network issues
					self.checkOutput(output,k,False)

					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/xorg-xserver-macros/util/macros && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/xorg-xserver-macros/util/macros/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/xorg-xserver-macros/util/macros && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/xorg-xserver-macros/util/macros && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()


					# compiling build.sh
					self.message('info',self.xorgXserverMacrosBuildParameters_b)
					output = os.system('cd ' + self.mainPath + '/xorg-xserver-macros && cp build.sh ./util/modular')
					self.checkOutput(output,k,False)
					output = os.system('cd ' + self.mainPath + '/xorg-xserver-macros && ' + self.xorgXserverMacrosBuildParameters_b)
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'macros':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'libXfont':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					##############################################################################################################
					# WA for the err : (‘required file `./ltmain.sh' not found’)
					# url : http://www.gnu.org/software/automake/manual/html_node/Error-required-file-ltmain_002esh-not-found.html
					##############################################################################################################
					if os.path.isfile('/usr/share/libtool/build-aux/ltmain.sh'):
						self.message('info','linking (ltmain.sh) from (/usr/share/libtool/build-aux) into (' + os.path.join(self.mainPath,k)+ ')')
						output = os.system('ln -s /usr/share/libtool/build-aux/ltmain.sh ' + os.path.join(self.mainPath,k))
						#output = os.system('cd ' + os.path.join(self.mainPath,k) + ' && libtoolize')
						self.checkOutput(output,k,False)
					else:
						self.message('err','(/usr/share/libtool/build-aux/ltmain.sh) does not exists')
						sys.exit(1)

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)


					# build parameters
					self.message('info',self.libXfontBuildParameters_a)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.libXfontBuildParameters_a)
					self.checkOutput(output,k,False)
					self.message('info',self.libXfontBuildParameters_b)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.libXfontBuildParameters_b)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'libXfont':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'xserver':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					# bug#19964: automake fails if files named “install.sh” and “install-sh” a
					# reference : https://lists.gnu.org/archive/html/bug-automake/2015-02/msg00005.html
					self.message('info','adding (AC_CONFIG_AUX_DIR) to configure.ac')
					output = os.system('cd ' + os.path.join(self.mainPath,k) + " && sed -i 's/.*AM_INIT_AUTOMAKE.*/AC_CONFIG_AUX_DIR\(\[.\]\) \\n&/' configure.ac")
					self.checkOutput(output,k,False)

					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					self.message('info','(PKG_CONFIG_PATH) = ' + os.environ['PKG_CONFIG_PATH'])
					# build parameters
					self.message('info',self.xorgXserverBuildParameters)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.xorgXserverBuildParameters)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)

					#########################################################################################################
					# this part is not needed anymore because libXfont will be compiled as a individual driver before xserver
					#########################################################################################################
					# Compiling libxfont2
					# self.message('info','compiling (xfont2) ' + progress + ' ...')
					# output = os.system('cd ' + self.gfxDriversBackupPath + ' && cp -r libXfont ' + self.mainPath)
					# self.checkOutput(output,'libXfont',False)
					# # build parameters
					# self.message('info',self.xfont2BuildParameters_a)
					# output = os.system('cd ' + self.mainPath + '/libXfont' + ' && ' + self.xfont2BuildParameters_a)
					# self.checkOutput(output,'libXfont',False)
					# self.message('info',self.xfont2BuildParameters_b)
					# output = os.system('cd ' + self.mainPath + '/libXfont' + ' && ' + self.xfont2BuildParameters_b)
					# self.checkOutput(output,'libXfont',False)
					# # make
					# self.message('info','make -j' + str(self.cores))
					# output = os.system('cd ' + self.mainPath + '/libXfont' + ' && make -j' + str(self.cores))
					# self.checkOutput(output,'libXfont',False)
					# # install
					# self.message('info','make install')
					# output = os.system('cd ' + self.mainPath + '/libXfont' + ' && make install')
					# self.checkOutput(output,'libXfont',True)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'xserver':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'intel-gpu-tools':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					# drm version from the system
					drmSystemVersion = self.b.get_output('pkg-config --modversion libdrm_intel')
					# sourcing environment graphic stack variables (the ones compiled so far)
					self.environmentVariables()
					self.message('info','(PKG_CONFIG_PATH) = ' + os.environ['PKG_CONFIG_PATH'])
					# drm version from the current gfx stack
					drmStackVersion = self.b.get_output('pkg-config --modversion libdrm_intel')
					self.message('info','drm system version : (' + drmSystemVersion + ')')
					self.message('info','drm stack version  : (' + drmStackVersion + ')')
					self.message('info','intel-gpu-tools needs at least drm version 2.4.67 to be compiled')
					# build parameters
					#self.message('info','CPPFLAGS=-I/usr/include/linux ' + self.igtBuildParameters_a)
					#output = os.system('cd ' + self.mainPath + '/' + k + ' && CPPFLAGS="-I/usr/include" ' + self.igtBuildParameters_a)
					#self.checkOutput(output,k,False)

					self.message('info',self.igtBuildParameters_a)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.igtBuildParameters_a)
					self.checkOutput(output,k,False)

					self.message('info',self.igtBuildParameters_b)
					output = os.system('cd ' + self.mainPath + '/' + k + ' && ' + self.igtBuildParameters_b)
					self.checkOutput(output,k,False)
					# make
					self.message('info','make -j' + str(self.cores))
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make -j' + str(self.cores))
					self.checkOutput(output,k,False)
					# install
					self.message('info','make install')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && make install')
					self.checkOutput(output,k,True)


					# generating a whole intel-gpu-tools testlist
					self.message('info','generating a whole intel-gpu-tools testlist')
					testList = self.b.get_output('cat ' + self.mainPath + '/' + k + "/tests/test-list.txt | sed -e '/TESTLIST/d'").split()
					fullTests = []
					tests_wo_subtests, tests_w_subtests = (0,)*2

					fich = open(self.mainPath + '/' + k + '/tests/intel-gpu-tools.testlist','w')
					prefix = 'igt@'

					for test in testList:
						# drm_mm & drv_selftest needs at least the kenrel 4.X in
						# order to list them.
						# chamelium needs a external hardware connected in the DUTs,
						# so far we dont have HW for this kind of test cases.
						# - gvt_basic causes that i915 module is unloaded and thus all the following tests
						#   will be marked as skip by piglit, a bug was raised for this, and when the bug is fixed
						#   this test (that contains so far one sub-test) will be returned to the igt test list.
						#   reference :
						#   http://linuxgraphics.intel.com/igt-reports/2018/igt_all/KBL/WW03/tuesday/08-47-42/html/iteration1/igt@gvt_basic@invalid-placeholder-test.html
						if test.startswith('amdgpu/') or test in (
							'drm_mm', 'chamelium', 'drv_selftest', 'gvt_basic'):
							self.message('info', 'omitting (' + test + ') ...')
							continue
						subtest = self.b.get_output(self.mainPath + '/' + k + '/tests/' + test + ' --list-subtest 2> /dev/null').split()
						if 'WARNING:' in subtest:
							continue
						else:
							if not subtest:
								fich.write(prefix+test+'\n')
								fich.flush()
								fullTests.append(test)
								tests_wo_subtests += 1
							else:
								for singleTest in subtest:
									fich.write(prefix+test+'@'+singleTest+'\n')
									fich.flush()
									fullTests.append(singleTest)
									tests_w_subtests += 1

					fich.close()

					# copying intel-gpu-tools.testlist to intel-ci folder
					# self.message('info','copying intel-gpu-tools.testlist to (intel-ci) folder')
					# copyfile(os.path.join(self.mainPath,k,'tests','intel-gpu-tools.testlist'),os.path.join(self.mainPath,k,'tests','intel-ci','intel-gpu-tools.testlist'))

					# Eliminating comments from testlist
					basePath = os.path.join(self.mainPath,k,'tests','intel-ci')
					files_to_analize = []
					files_list = []
					for (dirpath, dirnames, filenames) in os.walk(basePath):
						 files_list.extend(filenames)
						 for file in files_list:
						 	if os.path.splitext(file)[1][1:].strip() == 'testlist': # getting file extension
								with open(os.path.join(basePath,file),'r') as f:
									for line in f:
										if not line.startswith('igt@'):
											files_to_analize.append(file)
											break
					files_list = []
					for file in files_to_analize:
						self.message('info','parsing (' + file + ') into (' + os.path.basename(basePath) + ')')
						with open(os.path.join(basePath,file)) as oldfile, open(os.path.join(basePath,'tmp.testlist'), 'w') as newfile:
							for line in oldfile:
								if line.startswith('igt@'):
									newfile.write(line)
							os.system('rm ' + os.path.join(basePath,file))
							os.system('mv ' + os.path.join(basePath,'tmp.testlist') + ' ' + os.path.join(basePath,file))


					self.message('info','generating testlist by families into (intel-ci)')
					os.system('python ' + self.thisPath + '/tools/split_by_families.py --testlist ' + os.path.join(self.mainPath,k,'tests','intel-gpu-tools.testlist') + ' --output ' + os.path.join(self.mainPath,k,'tests','intel-ci') + ' --visualize true')

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'intel-gpu-tools':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'piglit':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying a revert as WA for latest incomplete test ===
					# self.message('info','applying a revert as WA for latest incomplete test')
					# self.message('info','git revert 4f5f852eb225eb78b3231ad4e8cd73fc191adca0')
					# output = os.system('cd ' + self.mainPath + '/' + k + ' && git revert 4f5f852eb225eb78b3231ad4e8cd73fc191adca0')

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					self.message('info','copying piglit to intel-gpu-tools ...')
					output = os.system('cd ' + self.mainPath + ' && cp -R ./piglit ./intel-gpu-tools')
					self.checkOutput(output,k,False)

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'piglit':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git tag') # this command is special for piglit since it does not has tags
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_time}}

				elif k == 'rendercheck':
					self.driver_getTime('start')
					self.message('info','compiling (' + k + ') ' + progress + ' ...')
					# checkout
					self.message('info','git checkout (' + commit + ')')
					output = os.system('cd ' + self.mainPath + '/' + k + ' && git checkout ' + str(commit) + ' > /dev/null 2>&1')
					self.checkOutput(output,k,False)

					# === applying the patch (if any) ===
					if self.patchValues[k]['apply'] == True:
						base = os.path.basename(self.patchValues[k]['path'])
						fileName = os.path.splitext(base)[0]
						extension = os.path.splitext(base)[1]
						if extension == '.patch':
							cmd = 'git apply --stat --verbose '
						elif extension == '.mbox':
							cmd = 'git am '

						if os.path.exists(self.patchValues[k]['path']):
							self.message('info','copying (' + extension.replace('.','') + ') to (' + k + ') ...')
							copyfile(self.patchValues[k]['path'],self.mainPath + '/' + k + '/' + fileName + extension)
							self.message('info','applying the (' + extension.replace('.','') + ') to (' + k + ') ...')
							checkPatchStatus = os.system('cd ' + self.mainPath + '/' + k + ' && ' + cmd + fileName + extension)
							if checkPatchStatus == 0:
								self.message('ok','the [' + extension.replace('.','') + '] was applied successfully on (' + k + ')')
							else:
								self.message('err','the [' + extension.replace('.','') + '] was failed')
								self.b.get_output('cd ' + self.mainPath + '/' + k + ' && git log -1','in the following commit the [' + extension.replace('.','') + '] can not be applied',True)
								sys.exit()
						else:
							self.message('err','(' + fileName + extension + ') does not exists')
							sys.exit()

					# adding git variables to the dictionary 'driversToCompile'
					for element in driversToCompile: # element is a list
						for key,value in element.items():
							index = driversToCompile.index(element)
							if key == 'rendercheck':
								for v in driversToCompile[index].values():
									# Getting git variables
									tag = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git describe')
									author = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show ' + driversToCompile[index][k]['commit'] + ' | grep -w "^Author" | awk -F": " \'{print $2}\' | tr -d ,')
									age_A = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cd ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : (2017-03-25 13:48:08 +0000)
									age_B = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%cr ' + driversToCompile[index][k]['commit'] + ' | tail -1') # e.g : 9 days ago
									comment = self.b.get_output('cd ' + self.mainPath + '/' + key + ' && git show -s --format=%B ' + driversToCompile[index][k]['commit'])
									# Getting driver compilation time
									compilation_time = self.driver_getTime('stop')
									driversToCompile[index] = {k:{'url':v['url'],'commit':v['commit'],'location':v['location'],'tag':tag,'author':author,'age':age_A + ' ' + age_B,'comment':comment,'compilation_time':compilation_times}}

			count+=1

		# === Structuring debian package ===
		dCount = 1
		#dirsToCreate = ['DEBIAN',self.mainPath,'etc/apt/apt.conf.d','root',self.wo_driver_path]
		dirsToCreate = ['DEBIAN',self.mainPath,'etc/apt/apt.conf.d','root']
		totald = len(dirsToCreate)

		# DEBIAN = this directory is needed in order to create a debian package
		# self.mainPath = for graphic stack drivers/tools
		# self.user = for bashrc
		# /etc/apt/apt.conf.d = for 99proxy
		# /root = for vimrc

		# === Creating the package folder ===
		for d in dirsToCreate:
			self.message('info','creating (' + d + ') directory [' + str(dCount) + '/' + str(totald) + '] ...')
			os.makedirs(self.debianRootPath + '/' + d)
			dCount+=1

		# === Copying the drivers/tools ===
		#=============================================================
		# === we can add much as we want to add to debian package ===
		#=============================================================
		whitelist = ['intel-gpu-tools','rendercheck']

		for i in whitelist:
			if i in onlyKeys:
				if os.path.exists(self.mainPath + '/' + i):
					self.message('info','copying ' + i + ' ...')
					copytree(self.mainPath + '/' + i, self.debianRootPath + self.mainPath + '/' + i)

		# === Creating the output folder ===
		#outputFolder = self.debianPackages + '/' +  self.month + '__WW' + self.weekNumber + '__' + self.weekDay + '__' + self.hour
		outputFolder = self.debianPackages + '/WW' + self.weekNumber + '/' + self.weekDay + '__' + self.month + '__' + self.hour
		self.message('info','creating output folder (' + outputFolder + ') ...')
		os.makedirs(outputFolder)

		# generating testlist by families into outputPath (if intel-gpu-tools is being builded)
		for i in onlyKeys:
			if i == 'intel-gpu-tools':
				if os.path.exists(os.path.join(self.mainPath,'intel-gpu-tools')):
					self.message('info','generating testlist by family into (' + os.path.basename(outputFolder) + ')')
					if not os.path.exists(os.path.join(outputFolder,'testlist.d')):
						self.message('info','creating (testlist.d) folder')
						os.makedirs(os.path.join(outputFolder,'testlist.d'))
					os.system('python ' + self.thisPath + '/tools/split_by_families.py --testlist ' + os.path.join(self.mainPath,'intel-gpu-tools','tests','intel-gpu-tools.testlist') + ' --output ' + os.path.join(outputFolder,'testlist.d') + ' --visualize false')

		# === Moving X11R7 from opt to tmp.drivers
		self.message('info','moving (' + self.masterLocation + ') to (' + self.debianRootPath + self.masterLocation + ') ...')
		move(self.masterLocation,self.debianRootPath + self.masterLocation)
		# === Moving tmp.drivers folder to outputFolder ===
		move(self.debianRootPath,outputFolder)
		finalFolder = outputFolder + '/tmp.drivers'

		# === Copying bashrc and vimrc and some useful files to the deb package's folder ===
		copyfile(self.thisPath + '/tools/bashrc', finalFolder + '/home/' + self.user + '/.bashrc')
		copyfile(self.thisPath + '/tools/bashrc', outputFolder + '/bashrc')
		copyfile(self.thisPath + '/tools/vimrc', finalFolder + '/home/' + self.user + '/.vimrc')
		copyfile(self.thisPath + '/tools/vimrc', finalFolder + '/root/.vimrc')
		copyfile(self.thisPath + '/tools/tmux.conf', finalFolder + '/home/' + self.user + '/.tmux.conf')
		copyfile(self.thisPath + '/tools/tmux.split', finalFolder + '/home/' + self.user + '/.tmux.split')
		copyfile(self.thisPath + '/tools/99proxy', finalFolder + '/etc/apt/apt.conf.d/99proxy')

		# === Creating the control file (file needed for create a debian package) ===
		folderSize = self.b.get_output('size=`du -s ' + finalFolder + '`; echo ${size} | awk \'{print $1}\'' )

		fichCTRL = open(finalFolder + '/DEBIAN/control','w')
		# the characters that aren't lowercase alphanums or '-+.'
		if not self.package_name:
			packageName = 'GraphicStack-' + self.month.lower() + '-ww' + self.weekNumber + '-' + self.weekDay.lower() + '-' + self.hour + '-code-' + self.randonNumber
			fichCTRL.write('Package: ' + packageName + '\n')
		else:
			packageName = self.package_name + '-' + self.month.lower() + '-ww' + self.weekNumber + '-' + self.weekDay.lower() + '-' + self.hour + '-code-' + self.randonNumber
			fichCTRL.write('Package: ' + packageName + '\n')

		fichCTRL.write('Version: 2.0 \n')
		fichCTRL.write('Code: ' + self.randonNumber + '\n')
		fichCTRL.write('Architecture: all \n')
		fichCTRL.write('Installed-Size: ' +  folderSize + '\n')
		fichCTRL.write('Homepage: http://linuxgraphics.intel.com \n')
		fichCTRL.write('Maintainer: Humberto Israel Perez Rodriguez <humberto.i.perez.rodriguez@intel.com> \n')
		fichCTRL.write('Description: Intel® Graphics for Linux* | 01.org \n')
		fichCTRL.write(' .\n') # this works as an space
		fichCTRL.write(' Project: Intel® Graphics for Linux \n')
		fichCTRL.write(' .\n')
		fichCTRL.write(' https://01.org/linuxgraphics \n')
		fichCTRL.write(' .\n')
		fichCTRL.write(' Maintainer: Humberto Israel Perez Rodriguez (humberto.i.perez.rodriguez@intel.com) \n')
		fichCTRL.write(' .\n')
		fichCTRL.write(' Date: ' + self.month + '__WW' + self.weekNumber + '__' + self.weekDay + '__' + self.hour + '\n')
		fichCTRL.write(' .\n')
		fichCTRL.write(' This debian package contains the following drivers : \n')
		fichCTRL.write(' .\n')
		fichCTRL.flush()


		# === Creating the config.cfg ===
		fichConfig = open(outputFolder + '/config.cfg','w')
		fichEasy = open(outputFolder + '/easy-bugs','w')
		# iterating over driversToCompile
		for element in driversToCompile: # element is a list
			for key,value in element.items():

				# the config.log for each driver contains the whole configuration for the driver related during the compilation
				config_log = os.path.join(self.mainPath, key, 'config.log')
				if os.path.isfile(config_log):
					self.message('info','(' + key + ') has (config.log), copying to (' + outputFolder + ') ...')
					config_folder = os.path.join(outputFolder,'config.d')
					if not os.path.exists(config_folder):
						os.makedirs(config_folder)
					copyfile(config_log,config_folder + '/' + key + '__config.log')

				# Getting the PCI-IDs for each driver, this will be useful in
				# to detect if a new platform in enabled in the driver or not
				folder_to_find = os.path.join(self.mainPath, key)
				pci_id_folder = \
					self.b.get_output('find ' + folder_to_find + " -maxdepth 100 -type d -name '*pci_id*' -print -quit")

				if pci_id_folder:
					onlyfiles = [f for f in listdir(pci_id_folder) if isfile(join(pci_id_folder, f))]
					pci_id_output_folder = \
						os.path.join(outputFolder, 'pci_ids', key)
					self.message(
						'info',
						'(' + key + ') has (pci_id) folder, copying to (' +
						pci_id_output_folder + ') ...')
					if not os.path.exists(pci_id_output_folder):
						os.makedirs(pci_id_output_folder)
					for f1 in onlyfiles:
						pci_full_path = os.path.join(pci_id_folder, f1)
						copyfile(pci_full_path, os.path.join(pci_id_output_folder, f1))


				if key == 'xf86-video-intel':
					# The below step does not apply anymore, because sna driver has to be in /opt/X11R7 folder, otherwise the system will not load it
					# besides that, xorg-xserver is the driver in charge to load it in Xorg.0.log
					'''# Copying xf86 to the system into /usr (this apply for ubuntu 16.10)
					if not os.path.exists(finalFolder + '/usr/lib/xorg/modules/drivers'):
						self.message('info','creating (/usr/lib/xorg/modules/drivers) directory ...')
						os.makedirs(finalFolder + '/usr/lib/xorg/modules/drivers')
					self.message('info','copying sna to (/usr/lib/xorg/modules/drivers) ...')
					copyfile(finalFolder + self.masterLocation + '/lib/xorg/modules/drivers/intel_drv.so',finalFolder + '/usr/lib/xorg/modules/drivers/intel_drv.so')
					self.message('info','given permissions to sna driver ...')
					os.system('chmod 664 ' + finalFolder + '/usr/lib/xorg/modules/drivers/intel_drv.so')'''

					# Copying xf86_HOWTO
					self.message('info','copying (xf86_HOWTO) to (/home/' + self.user + '/) ...')
					copytree(self.thisPath + '/tools/xf86_HOWTO', finalFolder +'/home/' + self.user + '/xf86_HOWTO')
					copytree(self.thisPath + '/tools/xf86_HOWTO', outputFolder + '/xf86_HOWTO')

				elif key == 'xserver':
					# The below step does not apply anymore, because sna driver has to be in /opt/X11R7 folder, otherwise the system will not load it
					# besides that, xorg-xserver is the driver in charge to load it in Xorg.0.log

					'''# Copying modesetting into the system (this apply for Ubuntu 16.10)
					self.message('info','enabling glamor driver ...')
					if not os.path.exists(finalFolder + '/usr/lib/xorg/modules/drivers'):
						self.message('info','creating (/usr/lib/xorg/modules/drivers) directory ...')
						os.makedirs(finalFolder + '/usr/lib/xorg/modules/drivers')
					self.message('info','copying glamor into (/usr/lib/xorg/modules/drivers)')
					copyfile(finalFolder + self.masterLocation + '/lib/xorg/modules/drivers/modesetting_drv.so',finalFolder + '/usr/lib/xorg/modules/drivers/modesetting_drv.so')
					self.message('info','giving the permissions to glamor')
					os.system('chmod 664 ' + finalFolder + '/usr/lib/xorg/modules/drivers/modesetting_drv.so')'''

					# Enabling modesetting driver by default
					# the default is sna (xf86-video-intel)
					drivers_path = os.path.join(
						finalFolder, 'opt', 'X11R7', 'lib', 'xorg', 'modules', 'drivers')
					sna_libraries = ['intel_drv.la', 'intel_drv.so']
					if self.data['2D_Driver']['glamour'] and os.path.exists(drivers_path):
						self.message(
							'info',
							'enabling modesetting driver as default in graphic stack')
						output_folder = os.path.join(finalFolder, 'home', self.user)
						for library in sna_libraries:
							move(
								os.path.join(drivers_path, library),
								os.path.join(output_folder, library))

					# Copying drirc configuration file
					if os.path.isfile(finalFolder + self.masterLocation + '/etc/drirc'):
						self.message('info','copying drirc configuration file ...')
						copyfile(finalFolder + self.masterLocation + '/etc/drirc',finalFolder + '/home/' + self.user + '/.drirc')

					# Setting libinput 1.6.3 for ubuntu 16 and minor
					#if self.current_os == '16':
					###################################################################
					# Ubuntu 17.04 already has libinput 1.5 for this does not affect it
					###################################################################
					self.message('info','setting libinput 1.6.3')
					libinput_path = os.path.join(self.thisPath,'tools','libinput10_1.6.3_amd_64','usr')
					copytree(libinput_path,os.path.join(finalFolder,'usr'))

					self.message('info','setting (Xorg) file')
					if not os.path.exists(os.path.join(finalFolder,'usr','bin')):
						self.message('info','creating (' + os.path.join(finalFolder,'usr','bin') + ')')
						os.makedirs(os.path.join(finalFolder,'usr','bin'))
					copyfile(os.path.join(self.thisPath,'tools','xserver.d','Xorg'),os.path.join(finalFolder,'usr','bin','Xorg'))
					copyfile(
						os.path.join(
							self.thisPath, 'tools', 'xserver.d', 'Xorg'),
						os.path.join(outputFolder, 'Xorg'))

					self.message('info','setting (xorg.conf) file')
					if not os.path.exists(os.path.join(finalFolder,'etc','X11')):
						self.message('info','creating (' + os.path.join(finalFolder,'etc','X11') + ')')
						os.makedirs(os.path.join(finalFolder,'etc','X11'))
					copyfile(os.path.join(self.thisPath,'tools','xserver.d','xorg.conf'),os.path.join(finalFolder,'etc','X11','xorg.conf'))
					copyfile(
						os.path.join(
							self.thisPath, 'tools', 'xserver.d', 'xorg.conf'),
						os.path.join(outputFolder, 'xorg.conf'))


				elif key == 'intel-gpu-tools':
					#testlists = ['extended.testlist','fast-feedback.testlist','generic.testlist','README','intel-gpu-tools.testlist']
					testlistsPath = os.path.join(self.mainPath, key,'tests','intel-ci')
					testlists = self.b.get_output('ls ' + testlistsPath + '| grep .testlist').split()

					if not os.path.exists(os.path.join(outputFolder,'testlist.d')):
						self.message('info','creating (' + os.path.basename(os.path.join(outputFolder,'testlist.d')) + ')')
						os.makedirs(os.path.join(outputFolder,'testlist.d'))
					self.message('info','copying remaining testlists to (' + os.path.basename(os.path.join(outputFolder,'testlist.d')) + ')')
					for tlist in testlists:
						if not os.path.exists(os.path.join(outputFolder,'testlist.d',tlist)):
							self.message('info','copying (' + tlist + ') ...')
							copyfile(os.path.join(testlistsPath,tlist), os.path.join(outputFolder,'testlist.d',tlist))

					# Eliminating comments from testlist
					basePath = os.path.join(outputFolder,'testlist.d')
					files_to_analize = []
					files_list = []
					for (dirpath, dirnames, filenames) in os.walk(basePath):
						 files_list.extend(filenames)
						 for file in files_list:
						 	if os.path.splitext(file)[1][1:].strip() == 'testlist': # getting file extension
								with open(os.path.join(basePath,file),'r') as f:
									for line in f:
										if not line.startswith('igt@'):
											files_to_analize.append(file)
											break
					files_list = []
					for file in files_to_analize:
						self.message('info','parsing (' + file + ') into (' + os.path.basename(basePath) + ')')
						with open(os.path.join(basePath,file)) as oldfile, open(os.path.join(basePath,'tmp.testlist'), 'w') as newfile:
							for line in oldfile:
								if line.startswith('igt@'):
									newfile.write(line)
							os.system('rm ' + os.path.join(basePath,file))
							os.system('mv ' + os.path.join(basePath,'tmp.testlist') + ' ' + os.path.join(basePath,file))

					self.message('info','copying intel-gpu-tools.testlist to (' + os.path.basename(outputFolder) + ') folder')
					copyfile(os.path.join(self.mainPath,key,'tests','intel-gpu-tools.testlist'),os.path.join(outputFolder,'intel-gpu-tools.testlist'))


				fichConfig.write('Component: ' + key + '\n')
				fichConfig.write('    url: ' + value['url'] + '\n')
				fichConfig.write('    tag: ' + value['tag'] + '\n')
				fichConfig.write('    commit: ' + value['commit'] + '\n')
				fichConfig.write('    author: ' + value['author'] + '\n')
				fichConfig.write('    age: ' + value['age'] + '\n')
				fichConfig.write('    comment: ' + value['comment'] + '\n\n')
				fichConfig.flush()
				fichEasy.write('Component: ' + key + '\n')
				fichEasy.write('    tag: ' + value['tag'] + '\n')
				fichEasy.write('    commit: ' + value['commit'] + '\n\n')
				fichEasy.flush()
				if self.data['2D_Driver']['sna'] and key == 'xf86-video-intel':
					fichCTRL.write(' |====[' + key + ']====| (sna enabled by default on this package)\n')
				elif self.data['2D_Driver']['glamour'] and key == 'xserver':
					fichCTRL.write(' |====[' + key + ']====| (glamour enabled by default on this package)\n')
				else:
					fichCTRL.write(' |====[' + key + ']====|\n')
				fichCTRL.write(' .\n')
				fichCTRL.write(' - url (' + value['url'] + ')\n')
				fichCTRL.write(' .\n')
				fichCTRL.write(' - tag (' + value['tag'] + ')\n')
				fichCTRL.write(' .\n')
				fichCTRL.write(' - commit (' + value['commit'] + ')\n')
				fichCTRL.write(' .\n')
				fichCTRL.write(' - author (' + value['author'] + ')\n')
				fichCTRL.write(' .\n')
				fichCTRL.write(' - age (' + value['age'] + ')\n')
				fichCTRL.write(' .\n')
				fichCTRL.flush()


		# === Building the debian package ===
		self.message('info','building the debian package ...')
		output = os.system('dpkg-deb --build ' + finalFolder)

		if output != 0:
			self.message('err','unable to create the debian package')
			sys.exit()
		elif output == 0:
			self.message('ok','the debian package was created successfully')

		# === Changing the permissions to the debian package ===
		self.message('info','changing permissions to debian package ...')
		tmpDebianName = finalFolder + '.deb'
		os.system('chmod 755 ' + tmpDebianName)

		# === Renaming the debian package ===
		self.message('info','renaming the debian package ...')
		os.rename(finalFolder + '.deb',outputFolder + '/' + packageName + '.deb')

		# === Getting statistics ===
		debianSize = self.b.get_output('echo `du -s ' + outputFolder + '/' + packageName + '.deb | awk \'{print $1}\' `') # this are kb
		debianSize = self.b.get_output('echo "scale =2;' + debianSize + '/1024" | bc') # this are MB
		tmpDriversSize = self.b.get_output('echo `du -s ' + finalFolder + '| awk \'{print $1}\' `') # this are kb
		tmpDriversSize = self.b.get_output('echo "scale =2;' + tmpDriversSize + '/1024" | bc') # this are MB
		compressionSize = self.b.get_output('echo "scale =2;' + debianSize + '*100/' + tmpDriversSize + '" | bc')
		compressionSize = self.b.get_output('echo "scale =2; 100- ' + compressionSize + '" | bc')

		# === Erasing tmp.drivers folder ===
		self.message('info','erasing (tmp.drivers) folder ...')
		shutil.rmtree(finalFolder)

		# === Renaming the final folder if it has intel-gpu-tools ===
		if 'intel-gpu-tools' in onlyKeys:
			os.rename(outputFolder,outputFolder + '__intel-gpu-tools')
			outputFolder = outputFolder + '__intel-gpu-tools'

		# === Showing statistics ===
		self.message('info','=== Statistics ====')
		self.message('info','(tmp.drivers) folder size : (' + tmpDriversSize + ') mb')
		self.message('info','(debian package)     size : (' + debianSize + ') mb')
		self.message('info','compression rate          : (' + compressionSize + '%)')
		self.message('info','graphic stack code        : (' + self.randonNumber + ')')
		self.message('info','debian package local path : (' + outputFolder + ')')

		# === Printing driver compilation statistics in a table ===
		statistics_headers = [blue + '#' + end, blue + 'Driver' + end, blue + 'Compilation time' + end]
		statistics_launch = []
		count = 1
		for driver in driversToCompile:
			for k,v in driver.items():
				compilation_time = v['compilation_time']
				updateRows = [blue + str(count) + end,k,compilation_time]
				statistics_launch.append(updateRows)
				count += 1

		t = tabulate(statistics_launch, headers=statistics_headers, missingval='?', stralign='left', tablefmt='fancy_grid').encode('utf-8')
		print t

		self.getTime('stop')
		# === Uploading the debian package ===
		serversAllowed = ['bifrost','midgard']
		currentHostname = self.b.get_output('echo ${HOSTNAME}')
		maintainers = ['humberto.i.perez.rodriguez@intel.com']

		if self.data['miscellaneous']['upload_package']:
			if self.ip.startswith('19'):
				self.message('err','the package only will be uploaded on intranet connection')
				if not currentHostname in serversAllowed:
					self.message('warn','this dut is not allowed for upload the debian package')
					self.message('info','please contact the maintainer if you need to upload it from here')
					for m in maintainers:
						self.message('info','- ' + m)
			else:
				if not currentHostname in serversAllowed:
					self.message('warn','this dut is not allowed for upload the debian package')
					self.message('info','please contact the maintainer if you need to upload it from here')
					for m in maintainers:
						self.message('info','- ' + m)
				elif currentHostname in serversAllowed:
					# === Creating the folder in the server ===
					serverUser = self.data['miscellaneous']['server_user']
					serverCname = self.data['miscellaneous']['server_for_upload_package']
					serverOutputFolder = '/home/' + serverUser + '/automation/gfx_stack_deb_packages/WW' + self.weekNumber + '/'

					self.message('info','creating the folder on (' + serverCname + ') ...')
					output = os.system('ssh ' + serverUser + '@' +  serverCname + ' mkdir -p ' + serverOutputFolder + ' &> /dev/null')
					self.checkOutputB(output,'the folder was created sucessfully on (' + serverCname + ')','could not created the folder on (' + serverCname + ')')

					# === Uploading debian package ===
					self.message('info','uploading debian package ...')
					output = os.system('scp -o "StrictHostKeyChecking no" -r ' + outputFolder + ' ' + serverUser + '@' + serverCname + ':' + serverOutputFolder + '/ &> /dev/null')
					self.checkOutputB(output,'the debian package was uploaded sucessfully on (' + serverCname + ')','could not uploaded the debian package on (' + serverCname + ')')

					# === Sending an email notification ===

					# Sending a email notification
					sender = 'gfx.stack@noreply.com'
					receivers = self.data['miscellaneous']['mailing_list']

					#receivers = ','.join(receivers) # converting from a list to string in order to visualize the lync names in the email notification

					gfxStackCode = self.randonNumber
					pkgName = packageName + '.deb'
					link = 'http://linuxgraphics.intel.com/deb/WW' + self.weekNumber + '/' + os.path.basename(outputFolder)

					emailMessage = """From: {senderB}
									To: {mailto}
									Subject: New graphic stack available on ({server})

									Hi team :

									A new graphic stack was built and is now available on ({server}).
									Please find the details below.

									- graphic stack code	: ({gfxCode})
									- debian package name	: ({debian})
									- link to download it	: ({linkD})


									Intel Graphics for linux*| 01.org
									Maintainer : humberto.i.perez.rodriguez@intel.com
									This is an automated message, please do not reply this message""".format(senderB=sender, mailto=receivers, gfxCode=gfxStackCode, debian=pkgName, linkD=link, server=serverCname)

					emailMessage = emailMessage.replace('\t','' ) # this is as a workaround, to eliminate car return from emailMessage

					try:
						smtpObj = smtplib.SMTP('smtp.intel.com')
						smtpObj.sendmail(sender, receivers, emailMessage)
						self.message('info','the email was sent successfully')
					except:
						self.message('err','unable to send the email')

		with open(os.path.join(self.thisPath, 'gfx_stack_code'), 'w') as gfx_stack_code_file:
			gfx_stack_code_file.write(self.randonNumber)

		# return the graphic_stack_code in order to use from ff_orchestrator
		return self.randonNumber


if __name__ == '__main__':
	Builder().build()
