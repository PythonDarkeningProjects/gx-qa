 #!/usr/bin/python

import datetime, os, glob, sys, re, csv # To execute SHELL commands
import subprocess 
import fnmatch # To get SHELL standar output
from subprocess import call, check_output


user_name = check_output('whoami').strip() # this get the current user without the 0 and the newline
now = datetime.datetime.now()
hour = str(now)[11:19]

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

def get_report():

    os.system('clear')
    os.system('mkdir -p /home/' + user_name + '/Desktop/results/rendercheck/')
    fileName = sys.argv[2] 

    f = open(fileName,'r')
    renderFile = f.read().splitlines()
    output_file= '/home/' + user_name + '/Desktop/results/rendercheck/rendercheck_TRC_' + hour + '.csv'
    f2 = open(output_file,'wb')
    #f2 = open("reportRendercheck.csv","wb")
    wr = csv.writer(f2,quoting=csv.QUOTE_NONE)
    suite = "Rendercheck"
    header = ("Component","Name","Status","Bug","Comment")
    wr.writerow(header)
    for i in range(len(renderFile)): 
        currentLine = renderFile[i]
        if(len(renderFile) >= i+2 ):
            nextLine = renderFile[i+1] 
            if(currentLine.startswith("Beginning") and nextLine.startswith("Beginning")):
                record = (suite,currentLine,"pass","","")
                wr.writerow(record)
            else:
                if(currentLine.startswith("Beginning") and nextLine.startswith("Beginning") == False):
                    record = (suite,currentLine,"fail","","")
                    wr.writerow(record)
    print "\n\n"
    print bcolors.green + " --> Completed " + bcolors.end
    print " --> The file is : " + "[" + output_file + "] \n\n" 




def help():
    "Help memu"
    os.system('clear'); print "\n\n", " === getResult.py help menu === \n\n"
    print " --help                 Shows this help menu"
    print " --report               Get the the report in format TRC \n"


# This helps to call the functions in a terminal
if __name__ == "__main__":

    if len(sys.argv) > 1:
        if  sys.argv[1] == "--report":
            if len(sys.argv) > 2:
                get_report()
            else:
                print "\n" + " --> Please specify a file \n"
        elif  sys.argv[1] == "--help":
            help()
        else:
            help()
    else:
        help()
