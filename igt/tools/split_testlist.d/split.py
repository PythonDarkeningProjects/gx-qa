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
#  https://docs.python.org/2/library/urllib.html

import argparse, sys, yaml, os
import pdb
from modules import main as c
from argparse import RawDescriptionHelpFormatter
from shutil import rmtree, copyfile

class Main:

	def __init__(self):
		self.var = 1

	def split_testlist(self,bunches,testlist,output,families):

		if families == 'True':

			tmp_folder = os.path.join(output,'families.d')
			if not os.path.exists(tmp_folder):
				c.message('info','creating (' + os.path.basename(tmp_folder) + ') in (' + os.path.basename(output) + ')')
				os.makedirs(tmp_folder)
			else:
				c.message('warn','(' + os.path.basename(tmp_folder) + ') exists, deleting it ...')
				rmtree(tmp_folder)
				c.message('info','creating (' + os.path.basename(tmp_folder) + ') in (' + os.path.basename(output) + ')')
				os.makedirs(tmp_folder)

			# creating the testlist by families
			families_count = 0

			for test in lines:
				fam = test.split('@')[1].rstrip()
				stest = test.rstrip()
				if '/' in fam:
					fam = fam.replace('/','_')
				if not os.path.isfile(os.path.join(tmp_folder,fam + '.testlist')):
					file = open(os.path.join(tmp_folder,fam + '.testlist'), 'w')
					file.write(stest + '\n')
					file.flush()
					file.close()
					families_count += 1
				elif os.path.isfile(os.path.join(tmp_folder,fam + '.testlist')):
					file = open(os.path.join(tmp_folder,fam + '.testlist'), 'a')
					file.write(stest + '\n')
					file.flush()
					file.close()

		# spliting into bunches
		# bounches_to_split = int(len(lines)) / bunches
		# tmp_file = os.path.join(output,'tmp.testlist')
		# if not os.path.isfile(tmp_file):
		# 	c.message('info','creating (' + os.path.basename(tmp_file) + ')')
		# 	copyfile(testlist.name,tmp_file)
		# else:
		# 	c.message('warn','(' + os.path.basename(tmp_file) + ') exists, deleting ...')
		# 	os.remove(tmp_file)
		# 	c.message('info','creating (' + os.path.basename(tmp_file) + ')')
		# 	copyfile(testlist.name,tmp_file)

		count = 1
		files_created = 0
		while True:
			if len(lines) >= bunches:
				tmp_list = lines[:bunches]
				for test in tmp_list:
					# removing the current test from full testlist
					lines.remove(test)
					test_bunch = os.path.join(output,str(count))
					if not os.path.exists(test_bunch):
						file = open(test_bunch, 'w')
						file.write(test)
						file.flush()
						file.close()
						files_created += 1
					else:
						file = open(test_bunch, 'a')
						file.write(test)
						file.flush()
						file.close()

				count += 1

			elif len(lines) < bunches and not len(lines) == 0:
				# this is the final test_bunch to write in the output folder
				tmp_list = lines[:len(lines)]
				for test in tmp_list:
					# removing the current test from full testlist
					lines.remove(test)
					test_bunch = os.path.join(output,str(count))
					if not os.path.exists(test_bunch):
						file = open(test_bunch, 'w')
						file.write(test)
						file.flush()
						file.close()
						files_created += 1
					else:
						file = open(test_bunch, 'a')
						file.write(test)
						file.flush()
						file.close()

			elif len(lines) == 0:
				break


		c.message('info','bunches created : (' + str(files_created) + ')')
		if families == 'True':
			c.message('info','families found  : (' + str(families_count) +')')
		sys.exit(0)


	def arguments(self,bunches,testlist,output,families,clean):

		# validating if the bunches given is =< to testlist
		global lines
		lines = testlist.readlines()

		if bunches > len(lines):
			c.message('err','bunches could not be greater than the lines in the (' + os.path.basename(testlist.name) + ') file')
			c.message('info','(' + os.path.basename(testlist.name) + ') lines : ' + str(len(lines)))
			sys.exit(1)

		# validating if output folder exists
		if not os.path.exists(output):
			c.message('err','(' + os.path.basename(output) + ') does not exists')
			sys.exit(1)


		# validating if clean option is enabled
		if clean == 'True':
			c.message('info','cleaning all (files/folders) in (' + os.path.basename(output) + ')')
			os.system('rm -rf ' + os.path.join(output,'*'))
		elif not clean:
			c.message('warn','clean option is disabled')

		# creating files for families
		self.split_testlist(bunches,testlist,output,families)

class Arguments:

	parser = argparse.ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
		description='''
	Program description:
	(%(prog)s) is a tool for split intel-gpu-tools testlist in a smart way
	passing parameters to get several bunches of testlist that they will help
	to run in tests in different platforms.
	(The goal of this is run all intel-gpu-tools tests in the shortest possible time)
	project : https://01.org/linuxgraphics
	maintainer : humberto.i.perez.rodriguez@intel.com''', epilog='Intel® Graphics for Linux* | 01.org', usage='%(prog)s [options]')
	parser.add_argument('--version', action='version', version='%(prog)s 3.0')
	parser.add_argument('-b', '--bunches',  dest='bunches', required=True, type=int, help='set the bunches to split the testlist ' + c.yellow + '(required)' + c.end)
	parser.add_argument('-t', '--testlist',  dest='testlist', required=True, type=argparse.FileType('r'), help='input testlist file ' + c.yellow + '(required)' + c.end)
	parser.add_argument('-o', '--output',  dest='output', required=True, help='set the output folder ' + c.yellow + '(required)' + c.end)
	parser.add_argument('-f', '--families',  dest='families', required=False, choices=['True'], help='create a families folder ' + c.cyan + '(optional)' + c.end)
	parser.add_argument('-c', '--clean',  dest='clean', required=False, choices=['True'], help='clean all (files/folders) in output directory ' + c.cyan + '(optional)' + c.end)
	#parser.add_argument('-m', '--master',  dest='master', required=False, default="50%", choices=[True], help='set the first bunch at %(default)s less than the other testlist ' + c.cyan + '(optional)' + c.end)

	args = parser.parse_args()
	# Validating arguments
	Main().arguments(args.bunches,args.testlist,args.output,args.families,args.clean)

if __name__ == '__main__':
	Arguments()