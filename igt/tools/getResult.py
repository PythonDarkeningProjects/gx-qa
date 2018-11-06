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
#
# tips : http://stackoverflow.com/questions/37224498/how-to-hide-or-delete-the-0-when-call-to-os-system-in-pyhon
# http://stackoverflow.com/questions/37229701/how-to-delete-0-form-from-os-system-in-python

from __future__ import print_function

import ast
import datetime
import json
import csv
import requests
import os
import glob
import logging
import re
import sys
import subprocess
import yaml

from subprocess import check_output
from os import listdir
from os.path import isfile, join


LOGGER = logging.getLogger(__name__)

user_name = check_output('whoami').strip() # this get the current user without the 0 and the newline
listOptionsX = []
listOptionsT = []

class bcolors:
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


purple = bcolors.purple
blue = bcolors.blue
green = bcolors.green
yellow = bcolors.yellow
red = bcolors.red
end = bcolors.end
bold = bcolors.bold
underline = bcolors.underline
cyan = bcolors.cyan
grey = bcolors.grey
default = bcolors.default
black = bcolors.black


class Bash(object):
	def get_output(self, option):
		proc = subprocess.Popen(option, stdout=subprocess.PIPE, shell=True)
		(out, err) = proc.communicate()
		out = out.strip()
		return out

	def run(self, cmd):
		subprocess.Popen(cmd, shell=True, executable='/bin/bash')


def getTotalTime(startTime, endTime):
	startTime = os.path.getctime(sys.argv[2])
	endTime = os.path.getctime(sys.argv[3])
	delta = endTime - startTime
	TotalTime = str(datetime.timedelta(seconds=float(delta)))
	TotalTime = str(TotalTime).split(".")[0] # Removing microseconds
	print(TotalTime.replace('-',''))


def getDelta(startTime, endTime):
	startTime = datetime.datetime.fromtimestamp(float(startTime))
	endTime = datetime.datetime.fromtimestamp(float(endTime))
	delta = endTime - startTime
	return delta.total_seconds()


def get_eta():
	os.system('clear')
	# Getting the last iteration folder
	list_iteration_folders = \
		glob.glob("/home/gfx/intel-graphics/"
		          "intel-gpu-tools/scripts/*iteration*")
	list_iteration_folders.sort() # sorting the list
	try:
		current_iteration_folder = list_iteration_folders[-1]
		jsonpath = current_iteration_folder + "/tests/"
	except IndexError:
		current_iteration_folder = None

	onlyfiles = [f for f in listdir(jsonpath) if isfile(join(jsonpath, f))]

	list = []
	totalSeconds = 0
	currentTests = 0

	for file in onlyfiles:
		currentTests += 1
		with open(jsonpath+file) as json_file:
			json_data = json.load(json_file)
		for key, value in json_data.iteritems():
			goTime = value['time']['start']
			finalTime = value['time']['end']
			elapsedSeconds = getDelta(goTime,finalTime)
			totalSeconds += (elapsedSeconds)
			list.append(elapsedSeconds)

	listLongitude = len(list)

	SecondsAverage = totalSeconds / listLongitude # this are seconds
	MinutesAverage = SecondsAverage / 60 %60
	HoursAverage = MinutesAverage / 60

	count = 0
	with open(
			'/home/gfx/intel-graphics/intel-gpu-tools/'
			'scripts/.statistics','r') as f2:
		for line in f2:
			line = line.rstrip('\n')
			count += 1
			if count == 2:
				totalTests = line


	remainingTests = int(totalTests) - currentTests

	ETA_seconds = SecondsAverage * remainingTests
	ETA_seconds = format(ETA_seconds,'.0f')
	remainingTime = str(datetime.timedelta(seconds=float(ETA_seconds)))

	print(remainingTime.replace('-',''))


def latest_json_result():
	"This function get the latests json file result"
	# Getting the last iteration folder
	list_iteration_folders = \
		glob.glob(
				"/home/gfx/intel-graphics/intel-gpu-tools/scripts/*iteration*")
	list_iteration_folders.sort() # sorting the list
	try:
		current_iteration_folder = list_iteration_folders[-1]
		jsonpath = current_iteration_folder + "/tests/"
	except IndexError:
		current_iteration_folder = None

	# Getting the last json file
	onlyfiles = [f for f in listdir(jsonpath) if isfile(join(jsonpath, f))]
	last_test = len(onlyfiles)
	last_test = last_test - 1

	# Setting the lastest json file
	file = jsonpath + str(last_test) + ".json"
	# file = jsonpath + str(1) + ".json" # for debug purposes
	with open(file) as json_file:
		json_data = json.load(json_file)
	for key, value in json_data.iteritems():
		result = value['result']

	print(str(result))
	return


def get_basic_tests():
	"This function get the current intel-gpu-tools basic tests"
	# Getting the last iteration folder
	list_iteration_folders = \
		glob.glob(
				"/home/gfx/intel-graphics/intel-gpu-tools/scripts/*iteration*")
	list_iteration_folders.sort() # sorting the list
	try:
		current_iteration_folder = list_iteration_folders[-1]
		jsonpath = current_iteration_folder + "/tests/"
	except IndexError:
		current_iteration_folder = None

	jsonpath= current_iteration_folder + "/tests/"
	onlyfiles = [f for f in listdir(jsonpath) if isfile(join(jsonpath, f))]

	# Declaring variables
	pass_tests, fail_tests, crash_tests, skip_tests, timeout_tests, \
	incomplete_tests, dmesg_warn_tests, warn_tests, dmesg_fail_tests = (0,)*9

	for file in onlyfiles:
		with open(jsonpath+file) as json_file:
			json_data = json.load(json_file)
		for key, value in json_data.iteritems():
			result = value['result']
			if re.search("basic", key):
				if result == "pass":
					pass_tests += 1
				elif result == "fail":
					fail_tests += 1
				elif result == "crash":
					crash_tests += 1
				elif result == "skip":
					skip_tests += 1
				elif result == "timeout":
					timeout_tests += 1
				elif result == "incomplete":
					incomplete_tests += 1
				elif result == "dmesg-warn":
					dmesg_warn_tests += 1
				elif result == "warn":
					warn_tests += 1
				elif result == "dmesg-fail":
					dmesg_fail_tests += 1

	total = pass_tests + fail_tests + crash_tests + skip_tests + \
	        timeout_tests + incomplete_tests + dmesg_warn_tests + \
	        warn_tests + dmesg_fail_tests
	total_pr = pass_tests + fail_tests + crash_tests + timeout_tests + \
	           dmesg_warn_tests + warn_tests + dmesg_fail_tests
	pass_rate = (pass_tests + dmesg_warn_tests + warn_tests) * 100 / float(
			total_pr)

	if len(sys.argv) > 2:
		if sys.argv[2] == "pass_rate":
			print(str(pass_rate) + " %")
			exit()
	else:
		print("============" + bcolors.cyan + " Basic tests " + bcolors.end
		      + "============")
		if pass_tests != 0:
			print(" -- Pass        : " + bcolors.green + str(pass_tests) +
			      bcolors.end)
		if fail_tests != 0:
			print(" -- Fail        : " + bcolors.red + str(fail_tests) +
			      bcolors.end)
		if crash_tests != 0:
			print(" -- Crash       : " + bcolors.bold + bcolors.red + str(
					crash_tests) + bcolors.end)
		if skip_tests != 0:
			print(" -- Skip        : " + bcolors.default + str(skip_tests) +
			      bcolors.end)
		if timeout_tests != 0:
			print(" -- Timeout     : " + bcolors.purple + str(timeout_tests)
			      + bcolors.end)
		if incomplete_tests != 0:
			print(" -- Incomplete  : " + bcolors.cyan + str(
					incomplete_tests) + bcolors.end)
		if dmesg_warn_tests != 0:
			print(" -- dmesg-warn  : " + bcolors.yellow + str(
					dmesg_warn_tests) + bcolors.end)
		if warn_tests != 0:
			print(" -- warn        : " + bcolors.yellow + str(warn_tests) +
			      bcolors.end)
		if dmesg_fail_tests != 0:
			print(" -- dmesg-fail  : " + bcolors.red + str(dmesg_fail_tests)
			      + bcolors.end)

		print(" ----------------------")
		print(" -- Total       : " + bcolors.bold + str(total) + bcolors.end)
		print(" -- Pass rate   : " + bcolors.blue + ("%.2f" % pass_rate) +
		      "%" + bcolors.end)

		if pass_rate == 100:
			print("\n" + bcolors.green + " Good pass rate " + bcolors.end +
			      " for basic tests")
		else:
			print("\n" + bcolors.red + " Bad pass rate " + bcolors.end + \
			     " for basic tests")
			print(" all tests must pass")


def current_json_result():
	"This function get the current json file result"
	# Getting the last iteration folder
	list_iteration_folders = \
		glob.glob("/home/gfx/intel-graphics/intel-gpu-tools/"
		          "scripts/*iteration*")
	list_iteration_folders.sort() # sorting the list
	try:
		current_iteration_folder = list_iteration_folders[-1]
		jsonpath = current_iteration_folder + "/tests/"
	except IndexError:
		current_iteration_folder = None


	# Getting the last json file
	onlyfiles = [f for f in listdir(jsonpath) if isfile(join(jsonpath, f))]
	last_test = len(onlyfiles)
	last_test = last_test - 1

	# Setting the lastest json file
	file = jsonpath + str(last_test) + ".json"
	# file = jsonpath + str(1) + ".json" # for debug purposes
	with open(file) as json_file:
		json_data = json.load(json_file)
		# print(json_data)
	for key, value in json_data.iteritems():
		result = value['result']
	result = str(result)
	result.strip()
	print(result)
	return


def get_current_statistics():
	"This function get the current statistics for the IGT execution"

	# Clear the screen
	os.system('clear')
	# Getting the last iteration folder
	list_iteration_folders = \
		glob.glob("/home/gfx/intel-graphics/intel-gpu-tools/"
		          "scripts/*iteration*")
	list_iteration_folders.sort() # sorting the list
	try:
		current_iteration_folder = list_iteration_folders[-1]
		jsonpath = current_iteration_folder + "/tests/"
	except IndexError:
		current_iteration_folder = None

	# Declaring variables
	pass_tests, fail_tests, crash_tests, skip_tests, timeout_tests, \
	incomplete_tests, dmesg_warn_tests, warn_tests, dmesg_fail_tests = (0,)*9

	onlyfiles = [f for f in listdir(jsonpath) if isfile(join(jsonpath, f))]

	for file in onlyfiles:
		with open(jsonpath + file) as json_file:
			json_data = json.load(json_file)
		for key, value in json_data.iteritems():
			result = value['result']
			if result == "pass":
				pass_tests+=1
			elif result == "fail":
				fail_tests+=1
			elif result == "crash":
				crash_tests+=1
			elif result == "skip":
				skip_tests+=1
			elif result == "timeout":
				timeout_tests+=1
			elif result == "incomplete":
				incomplete_tests+=1
			elif result == "dmesg-warn":
				dmesg_warn_tests+=1
			elif result == "warn":
				warn_tests+=1
			elif result == "dmesg-fail":
				dmesg_fail_tests+=1

	total = \
		pass_tests + \
		fail_tests + \
		crash_tests + \
		skip_tests + \
		timeout_tests + \
		incomplete_tests + \
		dmesg_warn_tests + \
		warn_tests + \
		dmesg_fail_tests
	total_pr = \
		pass_tests + \
		fail_tests + \
		crash_tests + \
		timeout_tests + \
		dmesg_warn_tests + \
		warn_tests + \
		dmesg_fail_tests
	pass_rate = \
		(pass_tests + dmesg_warn_tests + warn_tests) *100/float(total_pr)

	if len(sys.argv) > 2:
		if sys.argv[2] == "pass":
			print(pass_tests)
			exit()
		elif sys.argv[2] == "fail":
			print(fail_tests)
			exit()
		elif sys.argv[2] == "crash":
			print(crash_tests)
			exit()
		elif sys.argv[2] == "skip":
			print(skip_tests)
			exit()
		elif sys.argv[2] == "timeout":
			print(timeout_tests)
			exit()
		elif sys.argv[2] == "incomplete":
			print(incomplete_tests)
			exit()
		elif sys.argv[2] == "dmesg_warn":
			print(dmesg_warn_tests)
			exit()
		elif sys.argv[2] == "warn_test":
			print(warn_tests)
			exit()
		elif sys.argv[2] == "dmesg_fail":
			print(dmesg_fail_tests)
			exit()
		elif sys.argv[2] == "total":
			print(total)
			exit()
		elif  sys.argv[2] == "pass_rate":
			print("%.2f" % pass_rate) + "%"
			exit()
	else:
		print("============" + bcolors.cyan + " All tests " + bcolors.end +
		      "============")
		if pass_tests != 0:
			print(" -- Pass        : " + bcolors.green + str(pass_tests) +
			       bcolors.end)
		if fail_tests != 0:
			print(" -- Fail        : " + bcolors.red + str(fail_tests) +
			       bcolors.end)
		if crash_tests != 0:
			print(" -- Crash       : " + bcolors.bold + bcolors.red + str(
					crash_tests) + bcolors.end)
		if skip_tests != 0:
			print(" -- Skip        : " + bcolors.default + str(skip_tests)
			       + bcolors.end)
		if timeout_tests != 0:
			print(" -- Timeout     : " + bcolors.purple + str(timeout_tests)
			      + bcolors.end)
		if incomplete_tests != 0:
			print(" -- Incomplete  : " + bcolors.cyan + str(
					incomplete_tests) + bcolors.end)
		if dmesg_warn_tests != 0:
			print(" -- dmesg-warn  : " + bcolors.yellow + str(
					dmesg_warn_tests) + bcolors.end)
		if warn_tests != 0:
			print(" -- warn        : " + bcolors.yellow + str(warn_tests) +
			      bcolors.end)
		if dmesg_fail_tests != 0:
			print(" -- dmesg-fail  : " + bcolors.red + str(dmesg_fail_tests)
			      + bcolors.end)
		print(" ----------------------")
		print(" -- Total       : " + bcolors.bold + str(total) + bcolors.end)
		print(" -- Pass rate   : " + bcolors.blue + ("%.2f" % pass_rate) +
		      "%" + bcolors.end)


def get_json_fails():

	"this function get the list for rerun the X iteration of IGT"
	os.system('clear')

	# Deleting all IGT_run files
	for fl in \
			glob.glob('/home/' + user_name +
			          '/intel-graphics/intel-gpu-tools/scripts/IGT_run*'):
		os.remove(fl)

	os.system(
		'cp /home/' + user_name +
		'/intel-graphics/intel-gpu-tools/tests/test-list.txt '
		'/tmp/test-list')
	os.system("cat /tmp/test-list | sed -e '/TESTLIST/d' > /tmp/igt-list")
	clean = open('/tmp/igt-list').read().replace(' ', '\n')
	with open('/tmp/lists','w') as f2:
		f2.write(clean)

	families_with_subtests, families_without_subtests = ('',)*2
	count_families_without_subtests, count_families_with_subtests = (0,)*2
	with open('/tmp/lists','rb') as f3: # iterating over the file with all tests
		for line in f3:
			line = line.rstrip('\n') # for remove the last empty line (family name) (type str)
			process = subprocess.Popen(["/home/" + user_name + "/intel-graphics/intel-gpu-tools/tests/" + line, "--list-subtests"], stdout=subprocess.PIPE)
			process_out, process_err = process.communicate()
			process_out = process_out.rstrip('\n') # removing empty lines (type str)
			# print process_out # this the subtests (if exists)
			if process_out:
				for subtests in process_out.splitlines():
					families_with_subtests += (line + "@" + subtests + "\n")
					count_families_with_subtests += 1
			else:
				families_without_subtests += (line + "\n")
				count_families_without_subtests += 1

	families_with_subtests = families_with_subtests.rstrip('\n') # removing empty lines
	families_without_subtests = families_without_subtests.rstrip('\n') # removing empty lines
	total_tests= count_families_without_subtests + count_families_with_subtests

	count_W, count_B, pass_tests, fail_tests, crash_tests, skip_tests, \
	timeout_tests, incomplete_tests, dmesg_warn_tests, warn_tests, \
	dmesg_fail_tests = (0,)*11
	blacklist, whitelist, whitelist_file, blacklist_file = ('',)*4

	# Getting the last iteration folder
	list_iteration_folders = \
		glob.glob(
				"/home/gfx/intel-graphics/intel-gpu-tools/scripts/*iteration*")
	list_iteration_folders.sort() # sorting the list
	try:
		current_iteration_folder = list_iteration_folders[-1]
	except IndexError:
		current_iteration_folder = None


	fileName = sys.argv[2]
	f = open(
			'/home/' + user_name +
			'/intel-graphics/intel-gpu-tools/scripts/IGT_run1','w')
	f2 = open(fileName,'r')
	resultsJ = json.loads(f2.read())
	rjTests = resultsJ["tests"] # tests are in the json

	for testName in rjTests:
		if(rjTests[testName]['result'] in listOptionsT):
			clean_test = testName.replace("igt@", '')
			whitelist += (" -t " + clean_test)
			whitelist_file += ("-t " + clean_test + "\n")

		if(rjTests[testName]['result'] == "skip"):
			skip_tests += 1
		elif(rjTests[testName]['result'] == "fail"):
			fail_tests += 1
		elif(rjTests[testName]['result'] == "crash"):
			crash_tests += 1
		elif(rjTests[testName]['result'] == "timeout"):
			timeout_tests += 1
		elif(rjTests[testName]['result'] == "incomplete"):
			incomplete_tests += 1
		elif(rjTests[testName]['result'] == "dmesg-fail"):
			dmesg_fail_tests += 1

		if(rjTests[testName]['result'] in listOptionsX):
			if(testName not in whitelist):
				clean_test = testName.replace("igt@", '')
				blacklist += (" -x " + clean_test)
				blacklist_file += ("-x " + clean_test + "\n")
				count_B +=1
		if(rjTests[testName]['result'] == "pass"):
			pass_tests+=1
		elif(rjTests[testName]['result'] == "warn"):
			warn_tests+=1
		elif(rjTests[testName]['result'] == "dmesg-warn"):
			dmesg_warn_tests+=1

	exclude = pass_tests + warn_tests + dmesg_warn_tests
	include = fail_tests + crash_tests + timeout_tests + \
	          incomplete_tests + dmesg_fail_tests

	print("\n")
	print("-- Overal IGT Statistics from " + sys.argv[2] + " -- \n")
	if pass_tests != 0:
		print(" -- Pass        : " + bcolors.green + str(pass_tests) +
		      bcolors.end)
	if fail_tests != 0:
		print(" -- Fail        : " + bcolors.red + str(fail_tests) +
		      bcolors.end)
	if crash_tests != 0:
		print(" -- Crash       : " + bcolors.bold + bcolors.red + str(
				crash_tests) + bcolors.end)
	if skip_tests != 0:
		print(" -- Skip        : " + bcolors.default + str(skip_tests) +
		      bcolors.end)
	if timeout_tests != 0:
		print(" -- Timeout     : " + bcolors.purple + str(timeout_tests) +
		      bcolors.end)
	if incomplete_tests != 0:
		print(" -- Incomplete  : " + bcolors.cyan + str(incomplete_tests) +
		      bcolors.end)
	if dmesg_warn_tests != 0:
		print(" -- dmesg-warn  : " + bcolors.yellow + str(dmesg_warn_tests)
		      + bcolors.end)
	if dmesg_fail_tests != 0:
		print(" -- dmesg-fail  : " + bcolors.yellow + str(dmesg_fail_tests)
		      + bcolors.end)
	if warn_tests != 0:
		print(" -- warn        : " + bcolors.yellow + str(warn_tests) +
		      bcolors.end)

	print("------------------------------------------")
	print("--> test to run               : " + str(include))
	print("--> test to not run           : " + str(exclude))
	print("------------------------------------------")
	print("--> families_with_subtests    : " + str(
			count_families_with_subtests))
	print("--> families_without_subtests : " + str(
			count_families_without_subtests))
	print("--> total tests               : " + str(total_tests) + "\n")
	print(" IGT_run file was created in /home/" + user_name +
	      "/intel-graphics/intel-gpu-tools/scripts/")
	print(" a new blacklist was generated for this execution, please run "
	      "again run_IGT.sh & watchdog.sh \n")
	f.write(
			"bash /home/" + user_name +
			"/intel-graphics/intel-gpu-tools/scripts/run-tests.sh -s -r "
			+ current_iteration_folder)
	f.write(whitelist)
	f.write(blacklist)
	f.flush()
	f.close()
	f2.close()

	# .not_run_tests
	nr = open('/home/' + user_name +
	          '/intel-graphics/intel-gpu-tools/scripts/.not_run_tests', 'w')
	nr.write(blacklist)
	nr.close()

	# .only_test_to_run
	otr = open(
			'/home/' + user_name +
			'/intel-graphics/intel-gpu-tools/scripts/.only_test_to_run', 'w')
	otr.write(whitelist)
	otr.close()

	# overwriting the blacklist file
	bl = open(
			'/home/' + user_name +
			'/intel-graphics/intel-gpu-tools/scripts/blacklist', 'w')
	bl.write(whitelist_file + blacklist_file)
	bl.close()


def get_statistics():
	# incomplete so far ...
	"this function get the overall statistics of intel-gpu-tools execution"

	check1 = \
		os.path.isfile(
				"/home/gfx/intel-graphics/intel-gpu-tools/scripts/"
				".families_without_subtests")
	check2 = \
		os.path.isfile(
				"/home/gfx/intel-graphics/intel-gpu-tools/scripts/"
				".families_with_subtests")

	if check1 is False or check2 is False:
		os.system('clear')
		os.system(
				'cp /home/' + user_name +
				'/intel-graphics/intel-gpu-tools/tests/test-list.txt '
				'/tmp/test-list')
		os.system(
				"cat /tmp/test-list | sed -e '/TESTLIST/d' > /tmp/igt-list")
		clean = open('/tmp/igt-list').read().replace(' ', '\n')
		with open('/tmp/lists', 'w') as f2:
			f2.write(clean)

		families_with_subtests, families_without_subtests = ('',)*2
		count_families_without_subtests, count_families_with_subtests = (0,)*2
		with open('/tmp/lists','rb') as f3: # iterating over the file with all tests
			for line in f3:
				line = line.rstrip('\n') # for remove the last empty line (family name) (type str) (this is like a workaround)
				process = subprocess.Popen(["/home/" + user_name + "/intel-graphics/intel-gpu-tools/tests/" + line, "--list-subtests"], stdout=subprocess.PIPE)
				process_out, process_err = process.communicate()
				process_out = process_out.rstrip('\n') # removing empty lines (type str)
				# print process_out # this the subtests (if exists)
				if process_out:
					for subtests in process_out.splitlines():
						families_with_subtests += \
							(line + "@" + subtests + "\n")
						count_families_with_subtests +=1
				else:
					families_without_subtests += (line + "\n")
					count_families_without_subtests +=1

		families_with_subtests = families_with_subtests.rstrip('\n') # removing empty lines
		families_without_subtests = families_without_subtests.rstrip('\n') # removing empty lines
		total_tests = count_families_without_subtests + \
		              count_families_with_subtests

		family = open(
				'/home/' + user_name +
				'/intel-graphics/intel-gpu-tools/scripts/'
				'.families_with_subtests', 'w')
		family.write(families_with_subtests)
		family.close()

		family2 = open(
				'/home/' + user_name +
				'/intel-graphics/intel-gpu-tools/scripts/'
				'.families_without_subtests', 'w')
		family2.write(families_without_subtests)
		family2.close()

	else:
		# Changing the "/" for "@" from blacklist file (this needs to be before empty lines "lines")
		clean = \
			open('/home/' + user_name +
			     '/intel-graphics/intel-gpu-tools/scripts/'
			     'blacklist').read().replace('/', '@')
		# print clean
		with open('/home/' + user_name +
				          '/intel-graphics/intel-gpu-tools/'
				          'scripts/blacklist', 'w') as f2:
			f2.write(clean)

		# Removing empy lines from blacklist file
		new_blacklist = ''
		count_total_tests = 0
		with open('/home/' + user_name +
				          '/intel-graphics/intel-gpu-tools/'
				          'scripts/blacklist') as f:
			new_blacklist += "".join(line for line in f if not line.isspace())

		new_blacklist = new_blacklist.rstrip('\n') # removing empty lines
		blacklist_f = open(
				'/home/' + user_name +
				'/intel-graphics/intel-gpu-tools/scripts/blacklist', 'w')
		blacklist_f.write(new_blacklist)
		blacklist_f.close()

		check3 = os.path.isfile(
				"/home/gfx/intel-graphics/intel-gpu-tools/"
				"scripts/.total_IGT_tests_name")
		check4 = os.path.isfile(
				"/home/gfx/intel-graphics/intel-gpu-tools/"
				"scripts/.total_IGT_tests_number")

		if check3 is False or check4 is False:
			with open('/home/' + user_name +
					          '/intel-graphics/intel-gpu-tools/'
					          'scripts/.families_without_subtests', 'r') as b1:
				data1=b1.read() # this content the data for families without subtests

			with open('/home/' + user_name +
					          '/intel-graphics/intel-gpu-tools/'
					          'scripts/.families_with_subtests', 'r') as b2:
				data2=b2.read() # this content the data for families without subtests

			all_test = data1 + data2

			with open('/home/' + user_name +
					          '/intel-graphics/intel-gpu-tools/'
					          'scripts/.total_IGT_tests_name', 'w') as f3:
				f3.write(all_test)

			with open('/home/' + user_name +
					          '/intel-graphics/intel-gpu-tools/'
					          'scripts/.total_IGT_tests_name', 'r') as f4:
				for line in f4:
					count_total_tests += 1

			with open('/home/' + user_name +
					          '/intel-graphics/intel-gpu-tools/'
					          'scripts/.total_IGT_tests_number', 'w') as f5:
				f5.write(str(count_total_tests))

	### Here this script split the tests between -x and -t in two files

	tests_exclude, tests_include = ('',)*2

	with open('/home/' + user_name +
			          '/intel-graphics/intel-gpu-tools/'
			          'scripts/blacklist', 'r') as f6:
		for line in f6:
			line = line.rstrip('\n') # removing empty lines
			exclude = line.startswith("-x")
			include = line.startswith("-t")
			new_line = ""
			if exclude is True:
				new_line = line.replace('-x ','')
				tests_exclude += (new_line + "\n")
			elif include is True:
				new_line = line.replace('-t ','')
				tests_include += (new_line + "\n")

		tests_exclude = tests_exclude.rstrip('\n') # removing empty lines
		tests_include = tests_include.rstrip('\n') # removing empty lines
		print('tests_exclude \n' + tests_exclude)


	if tests_exclude:
		# tests_exclude is not empty
		with open('/home/' + user_name +
				          '/intel-graphics/intel-gpu-tools/'
				          'scripts/.exclude_tests', 'w') as f7:
			f7.write(tests_exclude)

	if tests_include:
		with open('/home/' + user_name +
				          '/intel-graphics/intel-gpu-tools/'
				          'scripts/.include_tests', 'w') as f8:
			f8.write(tests_include)


def analyze_testlist():
	basePath = '/home/' + user_name + \
	           '/intel-graphics/intel-gpu-tools/tests/intel-ci'

	print('>>> (info) changing owner for (' + os.path.basename(basePath) +
	      ') to (' + user_name + ')')
	os.system('sudo chown -R ' + user_name + '.' + user_name + ' ' + basePath)

	# Eliminating comments from testlist
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
		print(blue + '>>> (info)' + end + ' parsing (' + file + ') into (' +
		      os.path.basename(basePath) + ')')
		with open(os.path.join(basePath,file)) as oldfile, \
				open(os.path.join(basePath,'tmp.testlist'), 'w') as newfile:
			for line in oldfile:
				if line.startswith('igt@'):
					newfile.write(line)
			os.system('rm ' + os.path.join(basePath,file))
			os.system(
				'mv ' + os.path.join(basePath,'tmp.testlist') + ' ' +
				os.path.join(basePath,file))


def get_results_fails(file,iteration_number):

	blacklist = ['fail','crash,','incomplete','timeout','dmesg-fail']
	fich = open(file)
	fulljsonresults = json.loads(fich.read())
	testsjsonresults = fulljsonresults['tests']

	# Generation a new blacklist file with the test in the blacklist
	blacklist_file = '/home/' + user_name + \
	                 '/intel-graphics/intel-gpu-tools/scripts/blacklist'
	new_blacklist = open(blacklist_file,'w')
	count = 0

	for test in testsjsonresults:
		result = testsjsonresults[test]['result']
		format_test = test.replace('igt@','-t ')
		if result in blacklist:
			new_blacklist.write(format_test + '\n')
			new_blacklist.flush()
			count += 1

	new_blacklist.close()
	fich.close()

	if count > 0:
		# Generating a new IGT_runX file
		fich_2 = open(blacklist_file)
		tests = fich_2.read()
		tests = tests.replace('\n',' ')
		fich_2.close()
		new_IGT_run = open(
				'/home/' + user_name +
				'/intel-graphics/intel-gpu-tools/scripts/IGT_run1','w')
		results_folder = '/home/' + user_name + \
		                 '/intel-graphics/intel-gpu-tools/scripts/' \
		                 'iteration' + iteration_number + ' '
		script_to_run = 'bash /home/' + user_name + \
		                '/intel-graphics/intel-gpu-tools/' \
		                'scripts/run-tests.sh -s -r '
		cmd = script_to_run + results_folder + tests
		new_IGT_run.write(cmd)
		new_IGT_run.close()
		print('True')
	else:
		print('False')


def generate_new_testlist(jsonResults,testlist_name):

	blacklist = [
		'fail',
		'crash,',
		'incomplete',
		'timeout',
		'dmesg-fail'
		]
	fich = open(jsonResults)
	fulljsonresults = json.loads(fich.read())
	testsjsonresults = fulljsonresults['tests']

	testlist_file = \
		'/home/' + user_name + \
		'/intel-graphics/intel-gpu-tools/tests/intel-ci/' + testlist_name
	new_blacklist = open(testlist_file,'w')
	count = 0

	for test in testsjsonresults:
		result = testsjsonresults[test]['result']
		if result in blacklist:
			new_blacklist.write(test + '\n')
			new_blacklist.flush()
			count += 1

	new_blacklist.close()
	fich.close()

	if count > 0:
		print(blue + '>>> (info) ' + end + '(' + yellow + str(count) + end
		       + ') tests has been added to (' + cyan + testlist_name + end
		      + ')')


def createCSV_runtime(resultsJson,csvFile):

	# Getting a runtime.csv
	fich = open(resultsJson)
	fulljsonresults = json.loads(fich.read())
	testsjsonresults = fulljsonresults['tests']

	c = csv.writer(open(csvFile,'w'))
	c.writerow(
			['COMPONENT',
			 'NAME',
			 'STATUS',
			 'RUN TIME (seconds)',]
			)

	total_seconds = 0

	for test in testsjsonresults:
		result = str(testsjsonresults[test]['result'])
		sTime = testsjsonresults[test]['time']['start']
		eTime = testsjsonresults[test]['time']['end']
		single_test_seconds = getDelta(sTime,eTime)
		total_seconds += single_test_seconds
		c.writerow(
				['igt',
				 test,
				 result,
				 single_test_seconds,]
				)

	fich.close()

	total_minutes = total_seconds / 60 %60
	total_hours = total_minutes / 60

	# Getting a runtime.log
	dir_path = os.path.dirname(os.path.realpath(csvFile))
	fich2 = open(dir_path + '/runtime.log','w')
	fich2.write('hours   : (' + str(total_hours) +')\n')
	fich2.write('minutes : (' + str(total_minutes) +')\n')
	fich2.write('seconds : (' + str(total_seconds) +')\n')
	fich2.close()


def createCSV_backtrace(resultsJson, csvFile):

	fich = open(resultsJson)
	fulljsonresults = json.loads(fich.read())
	testsjsonresults = fulljsonresults['tests']

	not_run_list = [
		'skip',
		'incomplete',
		'timeout',
		'notrun'
		]
	fail_list = [
		'fail',
		'crash',
		'dmesg=fail',
		'dmesg-warn',
		'warn'
		]
	pass_list = ['pass']

	c = csv.writer(open(csvFile, 'w'))
	c.writerow(
			[
				'COMPONENT',
				'NAME',
				'STATUS',
				'BUG',
				'COMMENT',
			]
			)

	for test in testsjsonresults:
		test = test.encode('utf-8')
		result = testsjsonresults[test]['result'].encode('utf-8')
		dmesg = testsjsonresults[test]['dmesg'].encode('utf-8')
		# could be empty
		stdout = testsjsonresults[test]['out'].encode('utf-8')
		# could be empty
		error = testsjsonresults[test]['err'].encode('utf-8')
		# could be empty
		dmesg.replace(',', '')
		stdout.replace(',', '')
		error.replace(',', '')
		if result in not_run_list:
			if error:
				c.writerow(
						[
							'igt',
							test,
							'not run',
							'',
							'[[ this test was : ' + result + ' ]]' + '\n' +
							'[[ error ]] ' + error,
						]
						)
			elif not error:
				c.writerow(
						[
							'igt',
							test,
							'not run',
							'',
							'[[ this test was : {0} ]]'.format(result),
						]
						)
		elif result in fail_list:
				if error:
					c.writerow(
							[
								'igt',
								test,
								'fail',
								'',
								'[[ this test was : ' + result + ' ]]' + '\n' +
								'[[ error ]] ' + error,
							]
							)
				elif not error:
					c.writerow(
							[
								'igt',
								test,
								'fail',
								'',
								'[[ this test was : {0} ]]'.format(result),
							]
							)
		elif result in pass_list:
			if dmesg:
				c.writerow(
						[
							'igt',
							test,
							'pass',
							'',
							'[[ this test was : ' + result + ' ]]' + '\n' +
							'[[ dmesg ]]' + '\n' + dmesg,
						]
						)
			elif not dmesg:
				c.writerow(
						[
							'igt',
							test,
							'pass',
							'',
							'[[ this test was : {0}]]'.format(result),
						]
						)
	fich.close()


def createCSV(resultsJson, csvFile):
	fich = open(resultsJson)
	fulljsonresults = json.loads(fich.read())
	testsjsonresults = fulljsonresults['tests']

	not_run_list = [
		'skip',
		'incomplete',
		'timeout',
		'notrun'
		]
	fail_list = [
		'fail',
		'crash',
		'dmesg-fail',
		'dmesg-warn',
		'warn'
		]
	pass_list = ['pass']

	c = csv.writer(open(csvFile, 'w'))
	c.writerow(
			[
				'COMPONENT',
				'NAME',
				'STATUS',
				'BUG',
				'COMMENT',
			]
			)

	for test in testsjsonresults:
		result = testsjsonresults[test]['result']
		dmesg = testsjsonresults[test]['dmesg']  # could be empty
		stdout = testsjsonresults[test]['out']  # could be empty
		error = testsjsonresults[test]['err']  # could be empty
		dmesg.replace(',', '')
		stdout.replace(',', '')
		error.replace(',', '')
		if result in not_run_list:
			c.writerow(
					[
						'igt',
						test,
						'not run',
						'',
						'this test was {0}'.format(result),
					]
					)
		elif result in fail_list:
			c.writerow(
					[
						'igt',
						test,
						'fail',
						'',
						'this test was {0}'.format(result),
					]
					)
		elif result in pass_list:
			c.writerow(
					[
						'igt',
						test,
						'pass',
						'',
						'this test was {0}'.format(result),
					]
					)
		else:
			print(result)

		fich.flush()
	fich.close()

def updateCSVfromAPI(csvFile, platform, outputDir):

	try :
		r = requests.get(
				'http://10.64.95.35/api/BugManager/'
				'GetLastIgt?platformName=' + platform)
		obj = r.json()
		dictionary = ast.literal_eval(obj)
		bugs = dictionary['Bugs']
		c = csv.writer(open(outputDir + '/tmp.csv','w'))
		c.writerow(
			[
				'COMPONENT',
				'NAME',
				'STATUS',
				'BUG',
				'COMMENT',]
				)

		with open(csvFile) as f:
			reader = csv.reader(f)
			for row in reader:
				count = 0
				# component,test,status,bug,comment
				test = row[1]
				status = row[2]
				comment = row[4]
				if test == 'NAME':
					continue
				for value in bugs:
					if test == value['Name'] and status == 'fail':
						bug = value['Bug']
						count += 1
						if bug:
							regex = re.search(r'VIZ',bug)
							if regex:
								c.writerow(
										[
											'igt',
											test,
											status,
											'[[' + bug + ']]',
											comment,]
										)
							elif not regex:
								c.writerow(
										[
											'igt',
											test,
											status,
											'[[https://bugs.freedesktop.org/'
											'show_bug.cgi?id=' + bug + ' ' +
											bug + ']]',
											comment,]
										)
						elif not bug:
							c.writerow(
									[
										'igt',
										test,
										status,
										'this test has not bug related in '
										'database',
										comment,]
									)
				if status == 'fail' and count == 0:
					c.writerow(
							[
								'igt',
								test,
								status,
								'this test has not bug related in database',
								comment,]
							)
				elif status != 'fail':
					c.writerow(
							[
								'igt',
								test,
								status,
								'',
								comment,]
							)

	except ValueError:
		print(red + 'err '+ end + ': malformed string')
		print(yellow + 'No report found in database for : ' + end + str(
				platform))

		c = csv.writer(open(outputDir + '/tmp.csv', 'w'))
		c.writerow(
				[
					'COMPONENT',
					'NAME',
					'STATUS',
					'BUG',
					'COMMENT',]
				)

		with open(csvFile) as f:
			reader = csv.reader(f)
			for row in reader:
				# component,test,status,bug,comment
				test = row[1]
				status = row[2]
				comment = row[4]
				if test == 'NAME':
					continue
				elif status == 'fail':
					c.writerow(
							[
								'igt',
								test,
								status,
								'no bug found in database',
								comment,]
							)
				else:
					c.writerow(
							[
								'igt',
								test,
								status,
								'',
								comment,]
							)


def merge_json(main_json_file, secondary_json_file):
	"""Merge json files.

	The aim of this function is to merge two json files preserving the best
	result (the one in white_list)

	:param main_json_file: the main json file to be merged.
	:param secondary_json_file: the secondary json file to compare the results.
	"""
	with open(main_json_file, 'r') as archive:
		main_json_full_data = json.loads(archive.read())

	with open(secondary_json_file, 'r') as archive:
		secondary_json_full_data = json.loads(archive.read())

	main_json_tests_data = main_json_full_data['tests']
	secondary_json_tests_data = secondary_json_full_data['tests']
	white_list = ['pass']

	for test_case in secondary_json_tests_data:
		if (
				secondary_json_tests_data[test_case]['result'] !=
				main_json_tests_data[test_case]['result'] and
				secondary_json_tests_data[test_case]['result'] in white_list
		):
			main_json_tests_data[test_case] = secondary_json_tests_data[test_case]
	main_json_full_data['tests'] = main_json_tests_data

	with open(main_json_file, 'w+') as output_json:
		output_json.write(json.dumps(
			main_json_full_data, indent=4, sort_keys=True))


def get_json_files(path_to_files):
	"""Get all the json files from a specific path.

	The aim of this function if to get all the json files from a specific path
	for later merge them with merge_json function.

	:return: exit from this function when the path_to_files does not exists.
	"""
	if not os.path.exists(path_to_files):
		LOGGER.error('{0} : does not exist'.format(path_to_files))
		return

	main_json_file = []
	json_files = []

	for root, dirs, files in os.walk(path_to_files):
		for archive in files:
			if archive.endswith('.json'):
				json_path = os.path.join(root, archive)
				main_json_file.append(json_path) if 'iteration1' in json_path else \
					json_files.append(json_path)

	# in main_json_file only can be 1 iteration1 folder in order to merge the
	# others, otherwise the function merge_json will not works.
	if len(main_json_file) > 1:
		LOGGER.error('{0} has more than one (iteration1) folder'.format(
			path_to_files))
		LOGGER.info(main_json_file)
		return

	# main_json_file only will have 1 element and this needs to be passed as a
	# string to merge_json function.
	if json_files:
		for json_file in json_files:
			merge_json(main_json_file[0], json_file)
	elif not json_files:
		LOGGER.info('there is not json files to be merged')


def getStatisticsfromJson(jsonFile, action, status):

	"""
	:type jsonFile: is a json file from iteration folder
	:type action:
	:type status:
	"""
	if not os.path.isfile(jsonFile):
		print('>>> (warn) (' + str(jsonFile) + ') does not exists')
	else:
		pass_t, fail, crash, skip, timeout, incomplete, dmesg_warn, warn, \
		dmesg_fail, not_run = (0,)*10

		with open(jsonFile) as f:
			mainJson = json.loads(f.read())
			for test in mainJson['tests']:
				if mainJson['tests'][test]['result'] == 'fail':
					fail += 1
				if mainJson['tests'][test]['result'] == 'crash':
					crash += 1
				if mainJson['tests'][test]['result'] == 'skip':
					skip += 1
				if mainJson['tests'][test]['result'] == 'incomplete':
					incomplete += 1
				if mainJson['tests'][test]['result'] == 'timeout':
					timeout += 1
				if mainJson['tests'][test]['result'] == 'notrun':
					not_run += 1
				if mainJson['tests'][test]['result'] == 'dmesg-fail':
					dmesg_fail += 1
				if mainJson['tests'][test]['result'] == 'dmesg-warn':
					dmesg_warn += 1
				if mainJson['tests'][test]['result'] == 'warn':
					warn += 1
				if mainJson['tests'][test]['result'] == 'pass':
					pass_t += 1

		total_test = pass_t + fail + crash + skip + timeout + incomplete + \
		             dmesg_warn + warn + dmesg_fail + not_run
		try:
			calculate_pr = warn + dmesg_warn + pass_t
			calculate_pr_b = \
				pass_t + fail + crash + timeout + dmesg_warn + warn + dmesg_fail
			pass_rate_of_executed = calculate_pr * 100 / calculate_pr_b
		except:
			pass_rate_of_executed = 'N/A'
		tests_dictionary = {
			'pass_t': pass_t,
			'fail': fail,
			'crash': crash,
			'skip': skip,
			'timeout': timeout,
			'incomplete': incomplete,
			'dmesg_warn': dmesg_warn,
			'warn': warn,
			'dmesg_fail': dmesg_fail,
			'not_run': not_run,
			'total_test': total_test,
			'pass_rate': pass_rate_of_executed}

		if action == 'all':
			print('\n========================================')
			print(' overall intel-gpu-tools statistics ')
			print('========================================\n')
			print('- Total                   : (' + str(total_test) + ')')
			print('- pass                    : (' + green +
			      str(pass_t) + end  +')')
			print('- warn                    : (' + yellow + str(warn) +
			      end + ')')
			print('- fail                    : (' + red + str(fail) + end + ')')
			print('- crash                   : (' + red + str(crash) + end +
			      ')')
			print('- skip                    : (' + str(skip) + end + ')')
			print('- not run                 : (' + str(not_run) + end + ')')
			print('- timeout                 : (' + str(timeout) + end + ')')
			print('- incomplete              : (' + str(incomplete) + end +
			      ')')
			print('- dmesg-warn              : (' + yellow + str(dmesg_warn) +
			      end + ')')
			print('- dmesg-fail              : (' + red + str(dmesg_fail) +
			      end + ')')
			print('- pass rate of executed   : (' + blue + str(
					pass_rate_of_executed) + '%' + end + ')\n')
		elif action == 'single':
			for key,value in tests_dictionary.items():
				if status == key:
					if value:
						print(value)
					elif not value:
						print('0')
		elif action == 'check_failures':
			count = 0
			list_failures = {
				'fail': fail,
				'crash': crash,
				'timeout': timeout,
				'incomplete': incomplete,
				'dmesg_fail': dmesg_fail
				}

			for failure,value in list_failures.items():
				if value > 0:
					count += 1
			if count > 0:
				return True
			else:
				return False


def release_dut(action):
	data = yaml.load(open('/home/custom/config.yml'))
	# Raspberry configuration
	raspberry_number = data['raspberry_conf']['raspberry_number']
	raspberry_power_switch = data['raspberry_conf']['raspberry_power_switch']
	dut_hostname = data['dut_conf']['dut_hostname']

	url = 'http://bifrost.intel.com:2020/getRaspberries'
	r = requests.get(url)
	dictionary = r.json()
	raspberrys = len(dictionary)  # total raspberries number
	# range1 = lambda start, end: range(start, end + 1) # start with 1
	# instead 0

	if action == 'free':
		for rasp in range(raspberrys): # start with 1 instead 0
			for switch in dictionary[rasp]['powerSwitches']:
				if str(switch['Dut_Hostname']) == dut_hostname:
					if str(switch['Status']) == 'available':
						print(blue + '>>> (info) ' + end + 'this system '
							'is already available in watchdog database')
					else:
						try :
							r = requests.get(
									'http://bifrost.intel.com:2020/'
									'power/free-' + raspberry_number +
									'-' + raspberry_power_switch)
						except:
							print(red + '>>> (err) ' + end +
							      'could not connect to database')
						else:
							print('>>> (info) the switch : (' + cyan +
							      raspberry_power_switch + end +
							      ') ' + 'was release ' + '(' + green +
							      'successfully' + end + ')')
	elif action == 'busy':
		for rasp in range(raspberrys):
			for switch in dictionary[rasp]['powerSwitches']:
				if str(switch['Dut_Hostname']) == dut_hostname:
					if str(switch['Status']) == 'busy':
						print(blue + '>>> (info) ' + end + 'this system '
							'is already busy in watchdog database')
					else:
						try:
							r = \
								requests.get(
										'http://bifrost.intel.com:2020/'
										'power/busy-' + raspberry_number +
										'-' + raspberry_power_switch)
						except:
							print(red + '>>> (err) ' + end +
							      'could not connect to database')
						else:
							print('>>> (info) the switch : (' + cyan +
							      str(raspberry_power_switch) +  end + \
							      ') ' + 'was blocked ' + '(' + green +
							      'successfully' + end + ')')


def help():
	"Help memu"
	os.system('clear')
	print("\n\n", " === getResult.py help menu === \n\n")
	print(" --help                 Shows this help menu")
	print(" --split --<number>     Split blacklist in serveral files")
	print(" --json                 Get the latest json result")
	print(" --basic                Get basic tests")
	print(" --getfail              Get IGT_run1 file to run the second "
	      "iteration (caution : this option will erase all IGT_run files)")
	print(" --statistics           Shows the current IGT statistics")
	print(" --overall-statistics   Shows the overall IGT statistics ("
	      "incomplete) \n")


if __name__ == "__main__":

	if len(sys.argv) > 1:
		if sys.argv[1] == "--json":
			latest_json_result()
		elif sys.argv[1] == "--current":
			current_json_result()
		elif sys.argv[1] == "--statistics":
			get_current_statistics()
		elif sys.argv[1] == "--overall-statistics":
			get_statistics()
		elif sys.argv[1] == "--basic":
			get_basic_tests()
		elif sys.argv[1] == "--getfail":
			if len(sys.argv) > 2:
				listOptionsT = [
					'fail',
					'crash',
					'timeout',
					'incomplete',
					'dmesg-fail']
				listOptionsX = [
				    'pass',
				    'dmesg-warn',
				    'warn']
				get_json_fails()
			else:
				print("\n" + " --> Please specify a results.json file \n")
		elif sys.argv[1] == "--eta":
			get_eta()
		elif sys.argv[1] == "--getTime":
			getTotalTime(sys.argv[2],sys.argv[3])
		elif sys.argv[1] == "--totalfails":
			get_results_fails(sys.argv[2],sys.argv[3])
		elif sys.argv[1] == "--backtraceReport":
			createCSV_backtrace(sys.argv[2],sys.argv[3])
		elif sys.argv[1] == "--runtime":
			createCSV_runtime(sys.argv[2],sys.argv[3])
		elif sys.argv[1] == "--csvreport":
			createCSV(sys.argv[2],sys.argv[3])
		elif sys.argv[1] == "--updatecsv":
			updateCSVfromAPI(sys.argv[2],sys.argv[3],sys.argv[4])
		elif sys.argv[1] == "--getjsonfiles":
			get_json_files()
		elif sys.argv[1] == "--getjsonstatistics":
			getStatisticsfromJson(sys.argv[2],sys.argv[3],sys.argv[4])
		elif sys.argv[1] == "--release":
			release_dut(sys.argv[2])
		elif sys.argv[1] == "--mergejson":
			merge_json(sys.argv[2],sys.argv[3])
		elif sys.argv[1] == "--generate":
			generate_new_testlist(sys.argv[2],sys.argv[3])
		elif sys.argv[1] == "--analyze":
			analyze_testlist()

		elif sys.argv[1] == "--help":
			help()
		else:
			help()
	else:
		help()
