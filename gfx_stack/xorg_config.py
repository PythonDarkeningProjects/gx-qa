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
from shutil import rmtree
import sys

from gfx_qa_tools.common import bash
import yaml


class XorgConfig(object):

	def __init__(self):
		self.user = bash.get_output('whoami')
		if self.user == 'root':
			bash.message('info', 'please do not run this script as root')
			sys.exit(1)
		self.this_path = os.path.dirname(os.path.abspath(__file__))
		self.main_path = os.path.join(
			'/home/', self.user, 'intel-graphics', 'gfx_drivers_backup')
		self.branch_to_check = 'master'
		self.dut_user = 'gfx'
		self.package_name = 'xorgxserver'

	def check_commits(self):

		dict_of_drivers = {
			'libinput': {
				'commit': 'cc9a4debd3889a3b3a5139576ea873eebcf7dde7',
				'url': 'https://anongit.freedesktop.org/git/wayland/libinput.git'},
			'libva': {
				'commit': '',
				'url': 'https://github.com/01org/libva.git'},
			'libva-utils': {
				'commit': '',
				'url': 'https://github.com/01org/libva-utils.git'},
			'intel-vaapi-driver': {
				'commit': '',
				'url': 'https://github.com/01org/intel-vaapi-driver.git'},
			'cairo': {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/cairo'},
			'macros': {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/xorg/util/macros.git'},
			'libxtrans': {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/xorg/lib/libxtrans.git'},
			'libX11': {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/xorg/lib/libX11.git'},
			'libXext': {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/xorg/lib/libXext.git'},
			'dri2proto': {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/xorg/proto/dri2proto.git'},
			'libpciaccess': {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/xorg/lib/libpciaccess.git'},
			'pixman': {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/pixman.git'},
			"drm": {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/mesa/drm.git'},
			'mesa': {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/mesa/mesa.git'},
			'xserver': {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/xorg/xserver.git'},
			'libXfont': {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/xorg/lib/libXfont.git'},
			'xkeyboard-config': {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/xkeyboard-config.git'},
			'xkbcomp': {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/xorg/app/xkbcomp.git'},
			'xf86-input-mouse': {
				'commit': '',
				'url':
				'https://anongit.freedesktop.org/git/xorg/driver/xf86-input-mouse.git'},
			'xf86-input-keyboard': {
				'commit': '',
				'url':
				'https://anongit.freedesktop.org/git/xorg/driver/xf86-input-keyboard.git'},
			"xf86-input-evdev": {
				'commit': '',
				'url':
				'https://anongit.freedesktop.org/git/xorg/driver/xf86-input-evdev.git'},
			'xf86-video-vesa': {
				'commit': '',
				'url':
				'https://anongit.freedesktop.org/git/xorg/driver/xf86-video-vesa.git'},
			'xf86-video-fbdev': {
				'commit': '3cf99231199bd5bd9e681e85d9da1f9eb736e3e7',
				'url':
				'https://anongit.freedesktop.org/git/xorg/driver/xf86-video-fbdev.git'},
			'xf86-input-libinput': {
				'commit': '',
				'url':
				'https://anongit.freedesktop.org/git/xorg/driver/xf86-input-libinput.git'},
			'xf86-input-synaptics': {
				'commit': '',
				'url':
				'https://anongit.freedesktop.org/git/xorg/driver/'
				'xf86-input-synaptics.git'},
			'xf86-video-vmware': {
				'commit': '',
				'url':
				'https://anongit.freedesktop.org/git/xorg/driver/xf86-video-vmware.git'},
			'xf86-video-qxl': {
				'commit': '',
				'url':
				'https://anongit.freedesktop.org/git/xorg/driver/xf86-video-qxl.git'},
			'xf86-video-chips': {
				'commit': '',
				'url':
				'https://anongit.freedesktop.org/git/xorg/driver/xf86-video-chips.git'},
			'xf86-input-wacom': {
				'commit': '',
				'url': 'https://github.com/linuxwacom/xf86-input-wacom.git'},
			'xorgproto': {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/xorg/proto/xorgproto.git'},
			'xrdb': {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/xorg/app/xrdb.git'},
			'xf86-video-intel': {
				'commit': '',
				'url':
					'https://anongit.freedesktop.org/git/xorg/driver/xf86-video-intel.git'},
			'intel-gpu-tools': {
				'commit': '',
				'url': 'https://anongit.freedesktop.org/git/xorg/app/intel-gpu-tools.git'},
			'piglit': {
				'commit': '',
				'url': 'http://anongit.freedesktop.org/git/piglit.git'}}

		# validating if the folders exists
		for driver, url in dict_of_drivers.items():
			driver_path = os.path.exists(os.path.join(self.main_path, driver))
			if not driver_path:
				bash.message('info', 'cloning ({driver}) into ({path})'.format(
					driver=driver, path=self.main_path))
				output = os.system('git -C {path} clone {url}'.format(
					path=self.main_path, url=url['url']))
				if output != 0:
					bash.message(
						'err',
						'an error occurred trying to clone: {0}'.format(driver))
					if driver_path:
						bash.message('info', '{0}: will be removed'.format(driver))
						rmtree(driver_path)
					sys.exit(1)

		# checking for the latest commits and updating dictionary
		for driver, commit in dict_of_drivers.items():
			if not commit['commit']:
				driver_path = os.path.join(self.main_path, driver)
				latest_commit = bash.get_output(
					'git -C {path} ls-remote origin {branch}'.format(
						path=driver_path, branch=self.branch_to_check)).split()[0]
				bash.message('info', 'updating dictionary for: {0}'.format(driver))
				dict_of_drivers[driver]['commit'] = latest_commit

		# creating specific commit dictionary
		specific_commit = {'specific_commit': {'value': True}}
		for driver, commit in dict_of_drivers.items():
			specific_commit['specific_commit'][driver] = commit['commit']

		dut_config = {'dut_config': {'dut_user': self.dut_user}}
		package_config = {
			'package_config': {'package_name': self.package_name}}
		latest_commits = {'latest_commits': {'value': False}}
		xserver_driver = {'2D_Driver': {'sna': False, 'glamour': True}}

		patchwork = {
			'patchwork': {
				'checkBeforeBuild': True,
				'libinput': {'apply': False, 'path': ''},
				'libva': {'apply': False, 'path': ''},
				'libva-utils': {'apply': False, 'path': ''},
				'intel-vaapi-driver': {'apply': False, 'path': ''},
				'cairo': {'apply': False, 'path': ''},
				'macros': {'apply': False, 'path': ''},
				'libxtrans': {'apply': False, 'path': ''},
				'libX11': {'apply': False, 'path': ''},
				'libXext': {'apply': False, 'path': ''},
				'dri2proto': {'apply': False, 'path': ''},
				'libpciaccess': {'apply': False, 'path': ''},
				'pixman': {'apply': False, 'path': ''},
				'drm': {'apply': False, 'path': ''},
				'mesa': {'apply': False, 'path': ''},
				'xserver': {'apply': False, 'path': ''},
				'libXfont': {'apply': False, 'path': ''},
				'xkeyboard-config': {'apply': False, 'path': ''},
				'xkbcomp': {'apply': False, 'path': ''},
				'xf86-input-mouse': {'apply': False, 'path': ''},
				'xf86-input-keyboard': {'apply': False, 'path': ''},
				'xf86-input-evdev': {'apply': False, 'path': ''},
				'xf86-video-vesa': {'apply': False, 'path': ''},
				'xf86-video-fbdev': {'apply': False, 'path': ''},
				'xf86-input-libinput': {'apply': False, 'path': ''},
				'xf86-input-synaptics': {'apply': False, 'path': ''},
				'xf86-video-vmware': {'apply': False, 'path': ''},
				'xf86-video-qxl': {'apply': False, 'path': ''},
				'xf86-video-chips': {'apply': False, 'path': ''},
				'xf86-input-wacom': {'apply': False, 'path': ''},
				'xorgproto': {'apply': False, 'path': ''},
				'xrdb': {'apply': False, 'path': ''},
				'xf86-video-intel': {'apply': False, 'path': ''},
				'intel-gpu-tools': {'apply': False, 'path': ''},
				'piglit': {'apply': False, 'path': ''}}}

		miscellaneous = {
			'miscellaneous': {
				'maximum_permitted_time': 10000,
				'mailing_list': [
					'humberto.i.perez.rodriguez@intel.com',
					'humberto.i.perez.rodriguez@linux.intel.com',
					'luis.botello.ortega@intel.com',
					'maria.g.perez.ibarra@intel.com',
					'fernando.hernandez.gonzalez@intel.com',
					'hector.franciscox.velazquez.suriano@intel.com',
					'armando.antoniox.mora.reos@intel.com'
				],
				'upload_package': True,
				'server_for_upload_package': 'linuxgraphics.intel.com',
				'server_user': 'gfxserver'}}

		list_to_update = [
			dut_config,
			package_config,
			latest_commits,
			specific_commit,
			xserver_driver,
			patchwork,
			miscellaneous
		]

		data_dict = dict()

		for element in list_to_update:
			data_dict.update(element)

		bash.message(
			'info',
			'creating the (config.yml) for xserver package into: {0}'.format(
				self.this_path))

		with open(os.path.join(self.this_path, 'config.yml'), 'w') as config:
			config.write(yaml.dump(data_dict, default_flow_style=False))


if __name__ == '__main__':
	XorgConfig().check_commits()
