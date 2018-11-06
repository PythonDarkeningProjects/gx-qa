#!/usr/bin/python

import os, glob, sys, re # To execute SHELL commands
from subprocess import call, check_output

user_name = check_output('whoami').strip() # this get the current user without the 0 and the newline

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



def split_blacklist():
	
	os.system('clear')
	fileName = sys.argv[2]
	splitNumber = sys.argv[3]
	IGT = "/home/gfx/intel-graphics/intel-gpu-tools"
	checkifIsCompiled = "/home/gfx/intel-graphics/intel-gpu-tools/tests/test-list.txt"


	"Check if fileName exist"
	checkFilename = os.path.isfile(fileName)
	checkIGT = os.path.isdir(IGT)
	checkCompiled = os.path.isfile(checkifIsCompiled)

	if checkFilename is False :
		print "\n\n fileName : " + fileName + bcolors.red + " does not exists \n\n" + bcolors.end
		sys.exit()
	if checkIGT is False :
		print "\n\n Folder : " + IGT + bcolors.red + " does not exists \n\n" + bcolors.end
		sys.exit()
	if checkCompiled is False :
		print "\n\n intel-gpu-tools " + bcolors.red + " is not compiled \n\n" + bcolors.end
		sys.exit()

	# print "entro"

def help():
	"Help memu"
	os.system('clear'); print "\n\n", " === splitBlacklist.py help menu === \n\n"
	print " --help                                      Shows this help menu"
	print " --split <file> <number of files to split>   Split blacklist in serveral files \n"	


# This helps to call the functions in a terminal
if __name__ == "__main__":

	if len(sys.argv) > 1:
	   	if  sys.argv[1] == "--split":
	   		if len(sys.argv) == 4:
				split_blacklist()
			elif len(sys.argv) == 2:
				print "\n" + " --> Please specify a backlist file \n"
			elif len(sys.argv) == 3:
				print "\n" + " --> Please specify a number of files to split the backlist \n"
			else:
				help()
	   	elif  sys.argv[1] == "--help":
	   		help()
	   	else:
	   		# os.system('clear'); print "\n\n", " --> function Not found <-- \n\n"
	   		help()
	else:
		# os.system('clear'); print "\n\n", " --> You need to specify a function as parameter <-- \n\n"
		help()



