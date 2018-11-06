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

import argparse, sys, yaml, os, requests, urllib, datetime, json, requests
import pdb
from argparse import RawDescriptionHelpFormatter
from modules import colors as c

class Generator:

	def __init__(self):
		self.thisPath = os.path.dirname(os.path.abspath(__file__))

	def message(self,messageType,message):
		if messageType == 'err':
			print c.red + '>>> (err) ' + c.end + message
		elif messageType == 'warn':
			print c.yellow + '>>> (warn) ' + c.end + message
		elif messageType == 'info':
			print c.blue + '>>> (info) ' + c.end + message
		elif messageType == 'ok':
			print c.green + '>>> (success) ' + c.end + message
		elif messageType == 'statistics':
			print c.cyan + '>>> (data) ' + c.end + message

	def create(self,suite):

		data_dict = {}

		if suite == 'xorg':
			self.message('info','creating config.yml for (' + suite + ')')

			dut_config = {'dut_config':{'dut_user':'gfx'}}
			package_config = {'package_config':{'package_name':'xorgxserver'}}
			latest_commits = {'latest_commits':{'value':True,'libinput':True,'libva':True,'libva-utils':True,'intel-vaapi-driver':True,'cairo':True,'macros':True,'x11proto':True,'libxtrans':True,'libX11':True,'libXext':True,'dri2proto':True,'glproto':True,'libpciaccess':True,'pixman':True,'drm':True,'mesa':True,'xserver':True,'libXfont':True,'xkeyboard-config':True,'xkbcomp':True,'xf86-input-mouse':True,'xf86-input-keyboard':True,'xf86-input-evdev':True,'xf86-video-vesa':True,'xf86-video-fbdev':True,'xf86-input-libinput':True,'xf86-input-synaptics':True,'xf86-video-vmware':True,'xf86-video-qxl':True,'xf86-video-amdgpu':True,'xf86-video-ati':True,'xf86-video-chips':True,'xf86-input-wacom':True,'xproto':True,'xrdb':True,'xf86-video-intel':True,'intel-gpu-tools':True,'piglit':True}}
			specific_commit = {'specific_commit':{'value':False}}
			t2D_Driver = {'2D_Driver':{'sna':False,'glamour':True}}
			patchwork = {'patchwork':{'checkBeforeBuild':True,'libinput':{'apply':False,'path':''},'libva':{'apply':False,'path':''},'libva-utils':{'apply':False,'path':''},'intel-vaapi-driver':{'apply':False,'path':''},'cairo':{'apply':False,'path':''},'macros':{'apply':False,'path':''},'x11proto':{'apply':False,'path':''},'libxtrans':{'apply':False,'path':''},'libX11':{'apply':False,'path':''},'libXext':{'apply':False,'path':''},'dri2proto':{'apply':False,'path':''},'glproto':{'apply':False,'path':''},'libpciaccess':{'apply':False,'path':''},'pixman':{'apply':False,'path':''},'drm':{'apply':False,'path':''},'mesa':{'apply':False,'path':''},'xserver':{'apply':False,'path':''},'libXfont':{'apply':False,'path':''},'xkeyboard-config':{'apply':False,'path':''},'xkbcomp':{'apply':False,'path':''},'xf86-input-mouse':{'apply':False,'path':''},'xf86-input-keyboard':{'apply':False,'path':''},'xf86-input-evdev':{'apply':False,'path':''},'xf86-video-vesa':{'apply':False,'path':''},'xf86-video-fbdev':{'apply':False,'path':''},'':{'apply':False,'path':''},'':{'apply':False,'path':''},'':{'apply':False,'path':''},'':{'apply':False,'path':''},'':{'apply':False,'path':''},'':{'apply':False,'path':''},'xf86-input-libinput':{'apply':False,'path':''},'xf86-input-synaptics':{'apply':False,'path':''},'xf86-video-vmware':{'apply':False,'path':''},'xf86-video-qxl':{'apply':False,'path':''},'xf86-video-amdgpu':{'apply':False,'path':''},'xf86-video-ati':{'apply':False,'path':''},'xf86-video-chips':{'apply':False,'path':''},'xf86-input-wacom':{'apply':False,'path':''},'xproto':{'apply':False,'path':''},'xrdb':{'apply':False,'path':''},'xf86-video-intel':{'apply':False,'path':''},'intel-gpu-tools':{'apply':False,'path':''},'piglit':{'apply':False,'path':''}}}
			miscellaneous = {'miscellaneous':{'maximum_permitted_time':10000,'mailing_list':['humberto.i.perez.rodriguez@intel.com','humberto.i.perez.rodriguez@linux.intel.com'],'upload_package':True,'server_for_upload_package':'linuxgraphics.intel.com','server_user':'gfxserver'}}
			# falta los parches de todos estas madres


		elif suite == 'igt':
			self.message('info','creating config.yml for (' + suite + ')')

			dut_config = {'dut_config':{'dut_user':'gfx'}}
			package_config = {'package_config':{'package_name':'intelgputools'}}
			latest_commits = {'latest_commits':{'value':True,'cairo':True,'drm':True,'intel-gpu-tools':True,'piglit':True,'xf86-video-intel':False,'xserver':False,'mesa':False,'intel-vaapi-driver':False,'libva':False}}
			specific_commit = {'specific_commit':{'value':False}}
			t2D_Driver = {'2D_Driver':{'sna':False,'glamour':True}}
			patchwork = {'patchwork':{'checkBeforeBuild':True,'cairo':{'apply':False,'path':''},'drm':{'apply':False,'path':''},'intel-gpu-tools':{'apply':False,'path':''},'piglit':{'apply':False,'path':''}}}
			miscellaneous = {'miscellaneous':{'maximum_permitted_time':10000,'mailing_list':['humberto.i.perez.rodriguez@intel.com','humberto.i.perez.rodriguez@linux.intel.com'],'upload_package':True,'server_for_upload_package':'linuxgraphics.intel.com','server_user':'gfxserver'}}


		listUpdate = [dut_config,package_config,latest_commits,specific_commit,t2D_Driver,patchwork,miscellaneous]

		for element in listUpdate:
			data_dict.update(element)


		self.message('info','creating the (config.yml) into (' + os.path.join(self.thisPath,'config.yml') + ')')
		f = open(os.path.join(self.thisPath,'config.yml'),'w')
		f.write(yaml.dump(data_dict,default_flow_style=False))
		f.close()


class Arguments:

	parser = argparse.ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
		description='''
	program description:
	(%(prog)s) is a tool for generate config.yml for the following graphic stack
	- Xorg-Xserver
	- intel-gpu-tools
	project : https://01.org/linuxgraphics
	maintainer : humberto.i.perez.rodriguez@intel.com''', epilog='Intel® Graphics for Linux* | 01.org', usage='%(prog)s [options]')
	parser.add_argument('--version', action='version', version='%(prog)s 3.0')
	parser.add_argument('-x', '--xorg',  dest='xorg', required=False, choices=['True'], help='create a config.yml for Xorg-Xserver ' + c.yellow + '(required)' + c.end)
	parser.add_argument('-i', '--igt',  dest='igt', required=False, choices=['True'], help='create a config.yml for intel-gpu-tools ' + c.yellow + '(required)' + c.end)

	args = parser.parse_args()

	if args.xorg:
		Generator().create('xorg')
	elif args.igt:
		Generator().create('igt')

if __name__ == '__main__':
	Arguments()
