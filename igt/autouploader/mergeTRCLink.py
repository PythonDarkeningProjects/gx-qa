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


import subprocess, os, sys
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


class Actions:

	def __init__(self):
		
		self.b = Bash()
		self.sand_url = 'https://otcqarpt-stg.ostc.intel.com/gfx-sand/api/merge/'
		self.sand_key = '?auth_token=bebecc75620d546b6dd8'

		self.prod_url ='https://otcqarpt.jf.intel.com/gfx/api/merge/'
		self.prod_key ='?auth_token=b43a95c0201020406733'


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


	def merge(self,link,file):

		report_id = link.split('/')[-1]

		if not os.path.exists(file):
			self.message('err','(' + file + ') does not exists')
			sys.exit()

		if 'gfx-sand' in link:
			self.message('info','merging report to (' + yellow + 'sandbox' +  end + ') database')
			linkToUpload = self.sand_url + report_id + self.sand_key
			output = os.system('curl -k -F results_files=@' + file + ' ' + linkToUpload)
			
		else:
			self.message('info','merging report to (' + cyan + 'production' + end + ') database')
			linkToUpload = self.prod_url + report_id + self.prod_key
			output =  os.system('curl -k -F results_files=@' + file + ' ' + linkToUpload)

		if output == 0:
			self.message('info','the merge was ' + green + ' successful' + end)
			self.message('info','(' + yellow + link + end + ')')
			sys.exit()
		elif output == 403:
			self.message('err','invalid authentication token')
			sys.exit()
		elif output == 404:
			self.message('err','report not found')
			sys.exit()
		elif output == 422:
			self.message('err','invalid results files')
			self.message('info','you only can merge CSV/XML files')
			sys.exit()

class Main:

	def menu(self):

		self.a = Actions()
		if len(sys.argv) == 3:
			self.a.merge(sys.argv[1],sys.argv[2])
		else:
			print '>>> (err) some arguments are missing'
			
if __name__ == '__main__':
	Main().menu()