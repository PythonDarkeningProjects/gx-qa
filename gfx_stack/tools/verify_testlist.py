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

import os, sys, argparse, subprocess
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

class Actions():

	def message(self,messageType,message):
		if messageType == 'err':
			print red + '>>> (err) ' + end + message
		elif messageType == 'warn':
			print yellow + '>>> (warn) ' + end + message
		elif messageType == 'info':
			print blue + '>>> (info) ' + end + message
		elif messageType == 'ok':
			print green + '>>> (success) ' + end + message
		elif messageType == 'statistics':
			print cyan + '>>> (data) ' + end + message
		elif messageType == 'sameline_info':
			sys.stdout.write(blue + '>>> (info) ' + end + message)
		elif messageType == 'sameline_err':
			sys.stdout.write('[' + red + 'FAIL' + end  + ']\n')
		elif messageType == 'sameline_ok':
			sys.stdout.write('[' + green + 'OK' + end  + ']\n')

	def verify_testlist(self,testlist,testfolder):

		self.b = Bash()
		self.message('sameline_info','checking if (' + os.path.basename(testlist) + ') file exists ... ' )
		if not os.path.isfile(testlist):
			self.message('sameline_err','None')
			sys.exit()
		else:
			self.message('sameline_ok','None')

		self.message('sameline_info','checking if (' + os.path.basename(testfolder) + ') folder exists ... ' )
		if not os.path.exists(testfolder):
			self.message('sameline_err','None')
			sys.exit()
		else:
			self.message('sameline_ok','None')


		self.message('sameline_info','checking if all tests from (' + os.path.basename(testlist) + ') exists ... ' )

		with open(testlist) as f:
			lines = f.readlines()

		prefix = 'igt@'
		for test in lines:
			clean_test = test.rstrip().replace(prefix,'') # removing car return and prefix
			if '@' in clean_test:
				# this mean that is a subtest
				parent = clean_test.split('@')[0]
				child = clean_test.split('@')[1]
				# checking if this subtest exists
				output = self.b.get_output(os.path.join(testfolder,parent) + ' --l | grep ' + child)
				if not output:
					self.message('sameline_err','None')
					self.message('err','(' + clean_test + ') subtest does not exists')
					sys.exit()
			else:
				# this mean that is not a subtest
				if not os.path.isfile(os.path.join(testfolder,clean_test)):
					self.message('sameline_err','None')
					self.message('err','(' + clean_test + ') test does not exists')
					sys.exit()

		self.message('sameline_ok','None')
		self.message('info','all tests exists')

class Main:

	def menu(self):
		self.a = Actions()
		parser = argparse.ArgumentParser(description=cyan + 'Intel® Graphics for Linux*' + end, epilog=cyan + 'https://01.org/linuxgraphics' + end)
		parser.add_argument('--testlist', help='testlist file', required=True)
		parser.add_argument('--testfolder', help='intel-gpu-tools test folder path', required=True)
		args = parser.parse_args()

		if args.testlist and args.testfolder:
			self.a.verify_testlist(args.testlist,args.testfolder)

if __name__ == '__main__':
	Main().menu()
