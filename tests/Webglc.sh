#!/bin/bash 
#
#   Copyright (c) Intel, 2015
#
# File:         rendercheck.sh
#
# Description:
#
# Author(s):    Humberto Perez <humberto.i.perez.rodriguez@intel.com>
#
# Date:         2015/07/11
#
# https://www.khronos.org/registry/webgl/conformance-suites/1.0.3/webgl-conformance-tests.html

clear

	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>
	export CUSER=$(whoami)
	export PASSWORD=linux
	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>

	# <<-- Setting the global colors -->
	# http://misc.flogisoft.com/bash/tip_colors_and_formatting
	# The right colors that works under TTys are : https://wiki.archlinux.org/index.php/Color_Bash_Prompt_(Espa%C3%B1ol)#Indicadores_Basicos
	export nc="\e[0m"
	export underline="\e[4m"
	export bold="\e[1m"
	export green="\e[1;32m"
	export red="\e[1;31m"
	export yellow="\e[1;33m"
	export blue="\e[1;34m"
	export cyan="\e[1;36m"
	# <<-- Setting the global colors -->

	weekn=$(date +"%-V") # with this simbol '-' i can eliminite the 0 to do calculations
	export weekn=$(( weekn + 1 ))
	export getdate=$(date +"%b/%d/%Y")
	export hour=$(date +%I:%M:%S)
	export me=`basename $0`

function _spinner() {
    # $1 start/stop
    #
    # on start: $2 display message
    # on stop : $2 process exit status
    #           $3 spinner function pid (supplied from stop_spinner)

    local on_success="DONE"
    local on_fail="FAIL"
    local white="\e[1;37m"
    local green="\e[1;32m"
    local red="\e[1;31m"
    local nc="\e[0m"

    case $1 in
        start)
            # calculate the column where spinner and status msg will be displayed
            let column=$(tput cols)-${#2}-8
            # display message and position the cursor in $column column
            echo -ne ${2}
            printf "%${column}s"

            # start spinner
            i=1
            sp='\|/-'
            delay=${SPINNER_DELAY:-0.15}

            while :
            do
                printf "\b${sp:i++%${#sp}:1}"
                sleep $delay
            done
            ;;
        stop)
            if [[ -z ${3} ]]; then
                echo "spinner is not running.."
                exit 1
            fi

            kill $3 > /dev/null 2>&1

            # inform the user uppon success or failure
            echo -en "\b["
            if [[ $2 -eq 0 ]]; then
                echo -en "${green}${on_success}${nc}"
            else
                echo -en "${red}${on_fail}${nc}"
            fi
            echo -e "]"
            ;;
        *)
            echo "invalid argument, try {start/stop}"
            exit 1
            ;;
    esac
}

function start_spinner {
    # $1 : msg to display
    _spinner "start" "${1}" &
    # set global spinner pid
    _sp_pid=$!
    disown
}

function stop_spinner {
    # $1 : command exit status
    _spinner "stop" $1 $_sp_pid
    unset _sp_pid
}




	mkdir -p /home/$CUSER/Desktop/results/webglc
	dpkg-query -W -f='${Status} ${Version}\n' dos2unix &> /dev/null
	if [ $? != 0 ]; then echo $PASSWORD | sudo -S ls -l /tmp &> /dev/null && sleep 2; echo $PASSWORD | sudo -S apt-get install dos2unix -q=2 &> /dev/null; fi

function usage()
{
	echo -ne "\n\n"
    echo " Usage : $me [options]"
    echo
    echo -ne "	-a <file to analyze> \t Analyze the results from Webglc to convert to TRC format \n"
    echo -ne "	-h                   \t See this help menu \n"
    echo -ne "\n\n"
    exit 1 
}


if [ "$#" == "0" ]; then usage;fi

while test $# != 0
do
	case $1 in
		-h) usage; 
			exit 1 ;;
		-a) 
			file=$2
			if [ -f "$file" ]; then 

				# Converting the file to unix format
				dos2unix -f $2 &> /dev/null
				# Cleaning the report in order to get only the tests
				cat $2 | grep -w "conformance" | grep -v "tests failed" > /tmp/webglc.tmp

				echo "Component,Name,Status,Bug,Comment" > /home/$CUSER/Desktop/results/webglc/Webglc-results_WW$weekn-$hour.csv
				echo -ne "\n\n"
				echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
				start_spinner '--> Generating the report by families ...'

				count_criterion=''
				count_pass=''
				count_fail=''
				count_timeout=''
				count_skip=''

				_total_tests=`cat /tmp/webglc.tmp | grep -w ^conformance | wc -l`

					while read line
					do
						criteria=$(echo $line | awk -F"/" '{print $1}') # This mean conformance

						if [[ "$criteria" == "conformance" ]]; then 

							data=$(echo $line | awk -F": " '{print $2}') # here we got all data to analyze (example : 273 / 273 / 0 / 0 / 0)
							totaltests=$(echo $data | awk -F" / " '{print $1}')
							pass=$(echo $data | awk -F" / " '{print $2}')
							fail=$(echo $data | awk -F" / " '{print $3}')
							timeout=$(echo $data | awk -F" / " '{print $4}')
							skipped=$(echo $data | awk -F" / " '{print $5}')
							testname=$(echo $line | awk -F":" '{print $1}')
							
							if [[ "$pass" -gt "$fail" && "$pass" -gt "$timeout" && "$pass" -gt "$skipped" ]]; then ((count_pass++)); echo "Webglc,$testname,pass,,$pass passed tests of $totaltests," >> /home/$CUSER/Desktop/results/webglc/Webglc-results_WW$weekn-$hour.csv;fi
							if [[ "$fail" -gt "$pass" && "$fail" -gt "$timeout" && "$fail" -gt "$skipped" ]]; then ((count_fail++)); echo "Webglc,$testname,fail,,$fail failed tests of $totaltests," >> /home/$CUSER/Desktop/results/webglc/Webglc-results_WW$weekn-$hour.csv;fi
							if [[ "$timeout" -gt "$pass" && "$timeout" -gt "$fail" && "$timeout" -gt "$skipped" ]]; then ((count_timeout++)); echo "Webglc,$testname,timeout,,$timeout timeout tests of $totaltests," >> /home/$CUSER/Desktop/results/webglc/Webglc-results_WW$weekn-$hour.csv;fi
							if [[ "$skipped" -gt "$pass" && "$skipped" -gt "$fail" && "$skipped" -gt "$timeout" ]]; then ((count_skip++)); echo "Webglc,$testname,not run,,$skipped skipped tests of $totaltests," >> /home/$CUSER/Desktop/results/webglc/Webglc-results_WW$weekn-$hour.csv;fi
							if [[ "$pass" -eq "$fail" ]]; then ((count_criterion++)); echo "Webglc,$testname,verify,,Total tests : [$totaltests] - pass [$pass] / fail [$fail] you must apply a criterion," >> /home/$CUSER/Desktop/results/webglc/Webglc-results_WW$weekn-$hour.csv;fi
						fi


					done < /tmp/webglc.tmp

				stop_spinner $?
				echo -ne "\n\n"

				# Statistics
				vt=$(cat /home/$CUSER/Desktop/results/webglc/Webglc-results_WW$weekn-$hour.csv | grep -w "verify" | wc -l)
				passrate=$( echo "scale =2; $count_pass*100/$_total_tests" | bc)

				echo -ne " --- Summary --- \n" 								            | tee /home/$CUSER/Desktop/results/webglc/Summary-Webglc-results_WW$weekn.csv
				echo -ne " --> Total tests         : [$_total_tests] \n"		        | tee -a /home/$CUSER/Desktop/results/webglc/Summary-Webglc-results_WW$weekn.csv
				if [ ! -z "${count_pass}" ]; then
					echo -ne " --> Passed tests        : [${green}$count_pass${nc}] \n"		| tee -a /home/$CUSER/Desktop/results/webglc/Summary-Webglc-results_WW$weekn.csv
				fi
				if [ ! -z "${count_fail}" ]; then
					echo -ne " --> Failed tests        : [${red}$count_fail${nc}] \n"		| tee -a /home/$CUSER/Desktop/results/webglc/Summary-Webglc-results_WW$weekn.csv
				fi
				if [ ! -z "${count_timeout}" ]; then
					echo -ne " --> Timeout tests       : [${blue}$count_timeout${nc}] \n"	| tee -a /home/$CUSER/Desktop/results/webglc/Summary-Webglc-results_WW$weekn.csv
				fi
				if [ ! -z "${count_skip}" ]; then
					echo -ne " --> Skipped tests       : [${yellow}$count_skip${nc}] \n"	| tee -a /home/$CUSER/Desktop/results/webglc/Summary-Webglc-results_WW$weekn.csv
				fi
				echo -ne " --> Pass rate           : [$passrate%] \n"		            | tee -a /home/$CUSER/Desktop/results/webglc/Summary-Webglc-results_WW$weekn.csv
				echo; echo -ne " a report was generate in  --> [Desktop/results/webglc/Webglc-results_WW$weekn-$hour.csv] \n"
				echo -ne " a summary was generate in --> [Desktop/results/webglc/Summary-Webglc-results_WW$weekn-$hour.csv] \n\n\n"

					if [ "$vt" -gt 0 ]; then 
						echo -ne " --> ${yellow}NOTICE${nc} : You have [$vt] in verify status`tput sgr0` \n"
						echo -ne "   tests that are in [verify status] is because the pass and fail tests are the same"
						echo -ne "   and you must apply a criterion if the test pass or fail in the csv file \n\n" 
						exit 1
					elif [ "$vt" -eq 0 ]; then
						exit 1
					fi
	

			else
				echo -ne "\n\n"
				echo -ne " `tput bold``tput setf 6`The file`tput sgr0` `tput bold`[$file]`tput sgr0` `tput bold``tput setf 6`does not exists, please type a valid file`tput sgr0` \n"
				echo -ne "\n\n"
				exit 1
			fi

		;;

	esac
    	usage
done