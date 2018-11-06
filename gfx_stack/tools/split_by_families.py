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
from shutil import rmtree
from os import listdir
from os.path import isfile, join
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

	def split_by_families(self,testlist,output,visualize):

		self.b = Bash()
		self.message('sameline_info','checking if (' + os.path.basename(testlist) + ') file exists ... ' )
		if not os.path.isfile(testlist):
			self.message('sameline_err','None')
			sys.exit()
		else:
			self.message('sameline_ok','None')

		if not os.path.exists(output):
			self.message('sameline_info','creating (' + os.path.basename(output) + ') folder ... ')
			try:
				os.makedirs(output)
				self.message('sameline_ok','None')
			except:
				self.message('sameline_err','None')
				sys.exit()
		'''else:
			self.message('sameline_info','deleting (' + os.path.basename(output) + ') ... ')
			try:
				rmtree(output)
				self.message('sameline_ok','None')
			except:
				self.message('sameline_err','None')
				sys.exit()

			self.message('sameline_info','creating (' + os.path.basename(output) + ') folder ... ')
			try:
				os.makedirs(output)
				self.message('sameline_ok','None')
			except:
				self.message('sameline_err','None')
				sys.exit()'''


		with open(testlist) as f:
			lines = f.readlines()

		families = {}

		for test in lines:
			fam = test.split('@')[1].rstrip()
			stest = test.rstrip()
			if '/' in fam:
				fam = fam.replace('/','_')
			if not os.path.isfile(os.path.join(output,fam + '.testlist')):
				mfile = open(os.path.join(output,fam + '.testlist'),'w')
				mfile.close()
				file = open(os.path.join(output,fam + '.testlist'), 'a')
				file.write(stest + '\n')
				file.close()
			elif os.path.isfile(os.path.join(output,fam + '.testlist')):
				file = open(os.path.join(output,fam + '.testlist'), 'a')
				file.write(stest + '\n')
				file.close()

			#if not fam in families:
				#families.append(fam)

		# Getting families from the generated files
		onlyfiles = [f for f in listdir(output) if isfile(join(output, f))]
		only_testlist = []

		for file in onlyfiles:
			if os.path.splitext(file)[1][1:].strip() == 'testlist': # getting file extension
				only_testlist.append(file)
				with open(os.path.join(output,file)) as f:
					lines = sum(1 for _ in f)

				only_family = file.replace('.testlist','')
				families.update({only_family:lines})

		# Printing families numbers
		number_of_tests, number_of_families = (0,)*2
		for key,value in families.iteritems():
			number_of_families += 1
			number_of_tests += value
			if visualize == 'true':
				if key == 'gem_concurrent_blit':
					self.message('info','family (' + yellow + key + end + ') tests (' + yellow + str(value) + end + ')')
				else:
					self.message('info','family (' + key + ') tests (' + str(value) + ')')

		if visualize == 'true':
			self.message('info',cyan + '============= summary =============' + end)
			self.message('info','total tests    : (' + str(number_of_tests) + ')')
			self.message('info','total families : (' + str(number_of_families) + ')')
			self.message('info',cyan + '===================================' + end)

		# Generating a general testlist with all tests except gem_concurrent_blit

		all_testlist = self.b.get_output('cat ' + testlist + '| grep -v gem_concurrent_blit').split()

		for test in all_testlist:
			if not os.path.exists(os.path.join(output,'all.testlist')):
				mfile = open(os.path.join(output,'all.testlist'),'w')
				mfile.close()
			stest = test.rstrip()
			if stest.startswith('igt@'):
				file = open(os.path.join(output,'all.testlist'), 'a')
				file.write(stest + '\n')
				file.close()


		'''for file in only_testlist:
			if file != 'gem_concurrent_blit.testlist':
				with open(os.path.join(output,file)) as f:
					#lines = sum(1 for _ in f)
					f_lines = f.readlines()
				if not os.path.exists(os.path.join(output,'all.testlist')):
					mfile = open(os.path.join(output,'all.testlist'),'w')
					mfile.close()
				for line in f_lines:
					stest = line.rstrip()
					if stest.startswith('igt@'):
						file = open(os.path.join(output,'all.testlist'), 'a')
						file.write(stest + '\n')
						file.close()'''


class Main:

	def menu(self):
		self.a = Actions()
		parser = argparse.ArgumentParser(description=cyan + 'Intel® Graphics for Linux*' + end, epilog=cyan + 'https://01.org/linuxgraphics' + end)
		parser.add_argument('--testlist', help='testlist file with format igt@parent@child', required=True)
		parser.add_argument('--output', help='output folder', required=True)
		parser.add_argument('--visualize', help='visualize output', choices=['true','false'], required=True)
		args = parser.parse_args()

		if args.testlist and args.output and args.visualize:
			self.a.split_by_families(args.testlist,args.output,args.visualize)

if __name__ == '__main__':
	Main().menu()
