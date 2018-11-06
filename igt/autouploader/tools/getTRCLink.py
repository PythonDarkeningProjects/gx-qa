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

import argparse, requests, subprocess, os, sys
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

	def getTRCLink(self,trc_report_id):

		self.b = Bash()
		self.basePath = '/home/shared/trcReports'
		self.path = self.b.get_output('find ' + self.basePath + ' -maxdepth 100 -type d -name "*' + trc_report_id + '*"')
		self.link = self.b.get_output('cat ' + os.path.join(self.path,'trc_link') + ' 2> /dev/null')

		if self.path:
			print 'done,' + self.link
		else:
			print 'waiting,empty'

if __name__ == '__main__':
	Actions().getTRCLink(sys.argv[1])