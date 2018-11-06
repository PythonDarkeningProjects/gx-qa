from sys import argv
from subprocess import call, check_output
import os, glob, sys, re, shutil
import os.path

user_name = check_output('whoami').strip()

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


def help():
	"Help memu"
	os.system('clear'); print "\n\n", " === split.py help menu === \n\n"
	print " --help                 Shows this help menu"
	print " --csv <file.csv>       split IGT by families in csv \n"


def split_families():

	csv_file = sys.argv[2]
	header = ""
	directory = "/home/" + user_name + "/split_by_families"
	# Removing the previos folder
	if os.path.exists(directory):
		shutil.rmtree(directory)
	# Clear the screen
	os.system('clear')

	# Creating a new directory folder
	if not os.path.exists(directory):
		os.makedirs(directory)

	csv_lines = 0

	print "\n\n"
	print "Intel Graphics for Linux* 01.org \n"
	print "Spliting " + bcolors.blue + csv_file + bcolors.end + " by families \n"
	with open(csv_file) as f:
		archive = f.readlines()[1:] # this does not has the header

	for line in archive:
		csv_lines+=1
		header = ""
		family = line.split(",")[1].split("@")[1].split("_")[0]
		if(os.path.exists(directory + "/" + family + ".csv") == False):
			header = "Component,Name,Status,Bug,Comment \n"
		file = open(directory + "/" + family + ".csv", 'a')
		file.write(header)
		file.write(line)
		file.close() 

	# Opening each family file
	split_tests_count, files_count, total_split_tests = (0,)*3
	for file in os.listdir(directory):
		#print " -- Family : " + str(file)
		files_count+=1
		with open (directory + "/" + file,'rb') as f:
			for line in f:
				split_tests_count+=1
		with open (directory + "/" + file,'rb') as f2:
			lines = sum(1 for _ in f2) # Counting each line of the current file
			lines = lines - 1
			print " -- Family : " + str(file) + bcolors.cyan +  " / " + bcolors.end + str(lines) + " tests"

	total_split_tests = split_tests_count - files_count

	print "_________________________________________"
	print " -- Total families : " + str(files_count)
	print " -- Split tests    : " + str(total_split_tests)
	print " -- CSV tests      : " + str(csv_lines) + "\n"
	if csv_lines == total_split_tests:
		print " -- The splitted files" + bcolors.green + " match " + bcolors.end + "with the total number of test of : " + bcolors.blue + csv_file + bcolors.end
	else:
		print " -- The splitted files" + bcolors.red + " does not match " + bcolors.end + "with the total number of test of : " + bcolors.blue + csv_file + bcolors.end
	print " --> results has been written in " + str(directory) + "\n\n"




# This helps to call the functions in a terminal
if __name__ == "__main__":

	if len(sys.argv) > 1:
	   	if  sys.argv[1] == "--csv":
	   		if len(sys.argv) > 2:
		   		split_families()
		   	else:
				print "\n" + bcolors.red + " --> Please specify a csv file \n" + bcolors.end
	   	elif  sys.argv[1] == "--help":
	   		help()
	   	else:
	   		# os.system('clear'); print "\n\n", " --> function Not found <-- \n\n"
	   		help()
	else:
		# os.system('clear'); print "\n\n", " --> You need to specify a function as parameter <-- \n\n"
		help()
