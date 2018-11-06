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
import json

# =====================
# creating dictionaries
# =====================
gfxStack = dict()
drm_intel_qa = dict()
drm_tip = dict()
mainline = dict()
gfxStacks = dict()


def create_debian_packages_dictionary():
	"""
	:return: this function return a dictionary with all the debian packages
	avaialbles in bifrost.intel.com
	"""
	source = os.path.join('/home', 'gfx', 'intel-graphics', 'packages')
	for dirname, dirnames, filenames in os.walk(source):
		for element in filenames:
			ext = element[-3:]
			if ext == 'deb':
				work_week = dirname.split('/')[5]
				if work_week not in gfxStacks:
					gfxStacks[work_week] = []
					gfxStacks[work_week].append(element)
				else:
					gfxStacks[work_week].append(element)


def create_drm_intel_qa_dictionary():
	"""
	:return: this function return a dictionary with all the kernels
	avaialbles from drm-intel-qa branch per week
	"""
	for root, dirs, files in os.walk(
		os.path.join('/home', 'shared', 'kernels_mx', 'drm-intel-qa')):
		for name in dirs:
			full_path = os.path.join(root, name)
			if len(full_path.split("/")) == 7:
				ww = full_path.split("/")[5]
				try:
					drm_intel_qa[ww]
					drm_intel_qa[ww].append(name)
				except KeyError:
					drm_intel_qa[ww] = []
					drm_intel_qa[ww].append(name)


def create_drm_tip_dictionary():
	"""
	:return: this function return a dictionary with all the kernels
	avaialbles from drm-intel-tip branch per week
	"""
	for root, dirs, files in os.walk(
		os.path.join('/home', 'shared', 'kernels_mx', 'drm-tip')):
		for name in dirs:
			full_path = os.path.join(root, name)
			if len(full_path.split("/")) == 7:
				ww = full_path.split("/")[5]
				try:
					drm_tip[ww]
					drm_tip[ww].append(name)
				except KeyError:
					drm_tip[ww] = []
					drm_tip[ww].append(name)


def create_mainline_dictionary():
	"""
	:return: this function return a dictionary with all the kernels
	avaialbles from mainline branch per week
	"""
	for root, dirs, files in os.walk(
		os.path.join('/home', 'shared', 'kernels_mx', 'mainline')):
		for name in dirs:
			full_path = os.path.join(root,name)
			if len(full_path.split("/")) == 7:
				ww = full_path.split("/")[5]
				try:
					mainline[ww]
					mainline[ww].append(name)
				except KeyError:
					mainline[ww] =[]
					mainline[ww].append(name)


# ====================================================
# Calling the functions in order to get the components
# ====================================================
create_debian_packages_dictionary()
create_drm_intel_qa_dictionary()
create_drm_tip_dictionary()
create_mainline_dictionary()

# =======================
# Creating the dictionary
# =======================
components = {
	'gfxStack': gfxStacks,
	'drm-intel-qa': drm_intel_qa,
	'drm-tip': drm_tip,
	'mainline': mainline}

components = json.dumps(components)

print(components)
