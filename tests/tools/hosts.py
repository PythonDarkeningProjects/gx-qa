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

import requests
import os
import subprocess
import sys
import time

# ===================================
# Defines a color schema for messages
# ===================================
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


class Bash(object):
	
	def run(self, cmd, action):
		proc = \
			subprocess.Popen(
				cmd,
				stdout=subprocess.PIPE,
				shell=True,
				executable='/bin/bash')
		(out, err) = proc.communicate()
		out = out.strip()

		if action == 'True': 
			print(out)
		else: 
			return out

	def get_output(self, *args):
		if len(args) == 1:
			cmd = args[0]
			return self.run(cmd, 'False')
		elif len(args) == 2:
			(cmd, message) = args[0], args[1]
			print(blue + '>>> ' + end + message)
			return self.run(cmd, 'False')
		elif len(args) == 3:
			(cmd, message, action) = args[0], args[1], args[2]
			print(blue + '>>> ' + end + message)
			return self.run(cmd, 'True')


class Hosts(object):

	def __init__(self):
		self.url = 'http://bifrost.intel.com:2020/getRaspberries'
		self.b = Bash()
		self.dut_user = 'gfx'

	def show_hostnames(self, data, raspberry):
		rasp = int(raspberry) - 1
		switches_list = [0, 1, 2, 3, 4, 5, 6, 7]

		os.system('clear')
		print('\n' + cyan + '=================================' + end)
		print(
			cyan + '|' + end + '     Hostnames Availables      ' + cyan +
			'|' + end)
		print(cyan + '=================================' + end + '\n')

		values = []
		count = 1

		for switch in switches_list:
			hostname = data[rasp]['powerSwitches'][switch]['Dut_Hostname']
			ip = data[rasp]['powerSwitches'][switch]['DUT_IP']
			values.append(str(count) + '@' + str(hostname) + '@' + str(ip))
			print('\t' + str(count) + ') ' + yellow + '◉' + end + ' ' + str(
					hostname))
			count += 1

		option = raw_input(
				'\n ' + blue + '>>> (info)' + end + ' Select an option : ')

		if not option:
			raw_input(
				'\n ' + red + '(err)' + end + ' : Please select an option')
			self.show_hostnames(data, raspberry)
		else:
			count = 1
			for x in values:
				number = x.split('@')[0]
				hostname = x.split('@')[1]
				ip = x.split('@')[2]
				if option == number:
					print(
						'\n ' + blue + '>>> (info)' + end + ' : reaching (' +
						str(hostname) + ') (' + str(ip) + ') ...')
					response = \
						os.system(
							'timeout 3 ping -c 1 ' + str(ip) + ' 2> /dev/null')
					if response == 0:
						user = self.b.get_output('whoami')
						know_hosts_file = os.path.join(
							'/home', user, '.ssh', 'know_hosts')
						if os.path.exists(know_hosts_file):
							print(
								blue + '>>> (info)' + end + ' removing (' +
								str(ip) + ') from (' +
								os.path.basename(know_hosts_file) + ') ...')
							os.system(
								'ssh-keygen -f ' + know_hosts_file + ' -R '
								+ ip + ' &> /dev/null')
						print(
							'\n ' + blue + '>>> (info)' + end +
							' : connecting to (' + str(hostname) +
							') (' + str(ip) + ') ...')
						time.sleep(1)
						print(
							'\n ' + blue + '>>> (info)' + end + ' enabling \n'
							' ◉ compression\n'
							' ◉ X11 forwarding\n\n')
						os.system('ssh -X -C ' + self.dut_user + '@' + ip)
					else:
						print(
							'\n ' + red +
							'==============================' + end)
						print(
							'\n ' + red + '>>> (err)' + end + ' : the hostname'
							' (' + str(hostname) + ') (' + str(ip) +
							') is down\n')
						print(
							'\n ' + red +
							'==============================' + end + '\n')
						sys.exit(1)
				else:
					if count == len(values):
						raw_input(
							'\n ' + red + '(err)' + end + ' : out of range')
						self.show_hostnames(data, raspberry)
					count += 1

	def menu(self):
		r = requests.get(self.url)
		dictionary = r.json()
		raspberrys = len(dictionary)

		# ===============================================================
		# Generating a list with the current raspberries in the automated
		# system
		# ===============================================================
		raspberrys_list = []
		for raspberry_number in range(raspberrys):
			raspberrys_list.append(str(dictionary[raspberry_number]['name']))
		
		os.system('clear')
		print('\n' + blue + '=================================' + end)
		print(
			blue + '|' + end + '     Raspberrys Availables     ' + blue +
			'|' + end)
		print(blue + '=================================' + end + '\n')

		count_list = []
		count = 0

		for element in raspberrys_list:
			count += 1
			print(
				'\t' + str(count) + ') ' + yellow + '◉' + end + ' {rasp}'
				.format(rasp=element))
			count_list.append(count)

		option = raw_input(
				'\n ' + blue + '>>> (info)' + end + ' Select an option : ')

		if not option:
			raw_input(
				'\n ' + red + '>>> (err)' + end + ' : Please select an option')
			self.menu()

		elif int(option) in count_list:
			self.show_hostnames(dictionary, option)

		elif not int(option) in count_list:
			raw_input('\n ' + red + '>>> (err)' + end + ' : out of range')
			self.menu()


if __name__ == "__main__":
	Hosts().menu()
