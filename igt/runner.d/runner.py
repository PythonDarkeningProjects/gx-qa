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
import argparse, os.path, re, os, sys, csv, subprocess, yaml, shutil, json, __main__
from tempfile import NamedTemporaryFile
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

class run:

	def __init__ (self):
		self.b = Bash()

	def checkPath(self,path): # this check for files or folders
		if not os.path.exists(path):
			os.system('clear')
			print '\n[' + yellow +  path + end + ']' + red + ' does not exist\n' + end
			sys.exit()


	def checkCSV (self,resultsFolder,checkEmptyrow,checkFails):
		row_with_empty_status, row_with_fail_status = (0,)*2

		# Checking how many failures exists in the csv and how many tests are remaining
		with open(resultsFolder + '/summary.csv') as f:
			reader = csv.reader(f)
			for row in reader:
				(component,name,status,bug,comment) = (row[0],row[1],row[2],row[3],row[4])
				if component == 'COMPONENT':
					continue
				else:
					if not status:
						row_with_empty_status += 1
					elif status == 'fail':
						row_with_fail_status += 1
			if checkEmptyrow == 'True':
				return row_with_empty_status
			elif checkFails == 'True':
				row_with_fail_status

	def run_testlist(self,*args):
		# configuration options from yaml
		values = [element for element in (args)]
		(igtpath, testList, piglitpath, username, password, resultsFolder, dmesg_script, reboot_on_error) = (values[0],values[1],values[2],values[3],values[4],values[5],values[6],values[7])
		# configuration options from yaml

		ltest = self.b.get_output('cat ' + testList + " | tr '\n' ' '")
		testtorun = ltest.split()
		if not os.path.exists(resultsFolder):
			# Creating a results folder
			os.makedirs(resultsFolder)
			# Creating a the csv summary
			c = csv.writer(open(resultsFolder + '/summary.csv', 'w'))
			c.writerow(['COMPONENT','NAME','STATUS','BUG','COMMENT',])
			for test in testtorun:
				c.writerow(['igt',test,'','','',])
		else:
			csv_empty_status = self.checkCSV(resultsFolder,'True','None') #checkEmptyrow
			csv_fail_status = self.checkCSV(resultsFolder,'None','True') #checkFails

			if csv_empty_status > 0:
				os.system('clear')
				print blue + '\n>>> ' + end + 'tests remaining : (' + blue + str(csv_empty_status) + end + ')'
				if csv_fail_status > 0:
					print blue + '\n>>> ' + end + 'tests failed : (' + red + str(csv_fail_status) + end + ')'

				with open(resultsFolder + '/summary.csv') as f:
					reader = csv.reader(f)
					for row in reader:
						(component,name,status,bug,comment) = (row[0],row[1],row[2],row[3],row[4])
						if component == 'COMPONENT':
							continue
						else:
							if not status:
								if re.search(r'igt@',name):
									singleName = name.replace('igt@','')
								else:
									singleName = name
								IGT_TEST_ROOT = igtpath + '/tests'
								print cyan + '\n\n==============================================================' + end
								print cyan + '>>>' + end + ' running [' + yellow + singleName + end + ']'
								print cyan + '==============================================================' + end
								os.system('echo ' + password + ' | sudo -S touch /tmp/tmp_file &> /dev/null; sleep .75')
								# Erasing dmesg
								self.b.get_output('echo ' + password + ' | sudo -S dmesg -C')
								testFolder = resultsFolder + '/'+ name
								tests = testFolder + '/tests'
								# Creating the current test folder
								if os.path.exists(testFolder) and os.path.exists(tests):
									# this mean that the previous test was not successful
									result = os.system('echo ' + password + ' | sudo -S IGT_TEST_ROOT=' + IGT_TEST_ROOT + ' ' + piglitpath + '/piglit resume ' + testFolder + ' --no-retry')
								elif not os.path.exists(testFolder):
									os.makedirs(testFolder)
									#result = os.system('echo ' + password + ' | sudo -S IGT_TEST_ROOT=' + IGT_TEST_ROOT + ' ' + piglitpath + '/piglit run igt -o ' + testFolder + ' -s -l verbose -t ' + singleName + '$ 2> /dev/null')
									result = os.system('echo ' + password + ' | sudo -S IGT_TEST_ROOT=' + IGT_TEST_ROOT + ' ' + piglitpath + '/piglit run igt -o ' + testFolder + ' -s -l verbose -t ' + singleName + '$ 2> /tmp/' + singleName)

								# Check on errors
								if self.b.get_output('cat /tmp/' + singleName + ' 2> /dev/null |grep -i "other drm clients running" 2> /dev/null') and reboot_on_error:
									print red +'err' + end + ' Test Environment check: other drm clients running!'
									print blue + '>>>' + end + ' rebooting the DUT ...'
									os.system('sleep 4; echo ' + password + ' | sudo -S reboot')
								elif self.b.get_output('cat /tmp/' + singleName + ' 2> /dev/null |grep -i "other drm clients running" 2> /dev/null') and not reboot_on_error:
									print red +'err' + end + ' Test Environment check: other drm clients running!'
									print '[' + yellow + 'reboot_on_error' + end + ']' + ' option is disabled in yaml'
									print 'Please reboot the DUT in order to fix this issue \n'
									sys.exit()
								# Check on errors

								# this part i am assuming that the test finished on time, and not hang or similar failures were found
								if os.path.exists(testFolder + '/results.json.bz2'):
									# changing permissions of the test folder
									os.system('echo ' + password + ' | sudo -S chown -R ' + username + '.' + username + ' ' + testFolder)
									# Getting html folder
									os.system(piglitpath + '/piglit summary html -o ' + testFolder + '/html ' + testFolder)
									# Decompressing the results.json.bz2 in order to get the test result
									os.system('bzip2 -d ' + testFolder + '/results.json.bz2')
									with open(testFolder + '/results.json') as json_file:
										data = json.load(json_file)
									jsonL = data['tests']
									jsonResult = jsonL['igt@'+singleName]['result']
									print cyan + '\n>>> ' + end + 'status : (' + jsonResult +  ')\n'
									# Getting dmesg
									dmesgFolder = testFolder + '/dmesg'
									if not os.path.exists(dmesgFolder):
										os.makedirs(dmesgFolder)
									os.system('bash ' + dmesg_script + ' ' + dmesgFolder)
									os.system('dmesg > ' + dmesgFolder + '/dmesg.log 2> /dev/null && cp /var/log/kern.log ' + dmesgFolder + ' 2> /dev/null')
									# Updating csv file with local results
									maincsv = resultsFolder + '/summary.csv'
									tempfile = NamedTemporaryFile(delete=False)
									with open(maincsv, 'rb') as csvFile, tempfile:
										reader = csv.reader(csvFile, delimiter=',', quotechar='"')
										writer = csv.writer(tempfile, delimiter=',', quotechar='"')
										for row in reader:
											(component,name,status,bug,comment) = (row[0],row[1],row[2],row[3],row[4])
											if re.search(r'igt@',name):
												onlyName = name.replace('igt@','')
											else:
												onlyName = name
											if component == "COMPONENT":
												writer.writerow(['COMPONENT','NAME','STATUS','BUG','COMMENT',])
											elif onlyName == singleName:
												#row[1] = row[1].title().upper()
												writer.writerow([component,'igt@' + singleName,jsonResult,bug,comment,])
											else:
												writer.writerow([component,'igt@' + onlyName,status,bug,comment,])
									shutil.move(tempfile.name, maincsv)
									# Erasing kern.log
									#self.b.get_output('echo ' + password + ' | sudo -S rm -rf /var/log/kern.log',)
									# If the current test was pass, this script will continue with the following tests
									whitelist = ['pass', 'incomplete']
									csv_empty_status, csv_fail_status = (None,)*2
									csv_empty_status = self.checkCSV(resultsFolder,'True','None') #checkEmptyrow
									csv_fail_status = self.checkCSV(resultsFolder,'None','True') #checkFails

									if csv_empty_status == 0:
										print '\n(' + cyan + __main__.__file__+ end + ')' + yellow + ' has finished' + end
										print 'Please see the [' + resultsFolder + '] folder to see a summary.csv and more information \n'
										sys.exit()
									else:
										if jsonResult in whitelist:
											if csv_empty_status > 0:
												print blue + '\n>>> ' + end + 'tests remaining : (' + blue + str(csv_empty_status) + end + ')'
											if csv_fail_status > 0:
												print blue + '\n>>> ' + end + 'tests failed : (' + red + str(csv_fail_status) + end + ')'
											continue
										else:
											if reboot_on_error:
												print cyan + '>>>' + end + ' rebooting the DUT in order to continue with the following test'
												os.system('sleep 4; echo ' + password + ' | sudo -S reboot')
												sys.exit()
											elif not reboot_on_error:
												print '[' + yellow + 'reboot_on_error' + end + ']' + ' option is disabled in yaml'
												sys.exit()
							elif status:
								csv_empty_status, csv_fail_status = (None,)*2
								csv_empty_status = self.checkCSV(resultsFolder,'True','None') #checkEmptyrow
								csv_fail_status = self.checkCSV(resultsFolder,'None','True') #checkFails
								if csv_empty_status > 0:
									print blue + '\n>>> ' + end + 'tests remaining : (' + blue + str(csv_empty_status) + end + ')'
								if csv_fail_status > 0:
									print blue + '\n>>> ' + end + 'tests failed : (' + red + str(csv_fail_status) + end + ')'
								continue

			elif csv_empty_status == 0:
				# Here we test all
				os.system('clear')
				print '\n(' + cyan + __main__.__file__+ end + ')' + yellow + ' has finished' + end
				print 'Please see the [' + resultsFolder + '] folder to see a summary.csv and more information \n'
				sys.exit()



class Main:

	def __init__ (self):
		self.r = run()

	def menu(self):
		parser = argparse.ArgumentParser(description=cyan + 'Intel® Graphics for Linux*' + end, epilog=cyan + 'https://01.org/linuxgraphics' + end)
		#group = parser.add_mutually_exclusive_group()
		#group.add_argument('-v','--verbose', dest='verbose', action='store_true', help='shows verbose during the test')
		parser.add_argument('-v','--version', dest='version', action='version', version='%(prog)s 1.0')
		#parser.add_argument('-l','--list', dest='list', action='version', help='list of test to run', required=True)
		#parser.add_argument('--list', help='list of test to run', required=True)
		parser.add_argument('--file', help='path to configuration file', required=True)
		args = parser.parse_args()

		if args.file:
			# Cheking if configuration file exits
			self.r.checkPath(args.file)
			data = yaml.load(open(args.file))
			diccionary = data['configuration']
			diccionary_whitelist = ['reboot_on_error']
			empty_fields = []
			for k,v in diccionary.items():
				if not v and k not in diccionary_whitelist:
					empty_fields.append(k)
			if empty_fields:
				os.system('clear')
				print '\n>>> Please fill out all the options in [' + args.file + ']'
				print '>>> the following options are empty\n'
				for field in empty_fields:
					print '- ' + field
				print '\n'
			else:
				# checking if the files and paths exists
				checkList = [diccionary['path_to_igt'],diccionary['testlist'],diccionary['path_to_piglit']]
				for item in checkList:
					self.r.checkPath(item)
				self.r.run_testlist(checkList[0],checkList[1],checkList[2],diccionary['user'],diccionary['password'],diccionary['path_to_results'],diccionary['dmesg_script'],diccionary['reboot_on_error'])

if __name__ == '__main__':
	Main().menu()