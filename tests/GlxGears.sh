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
# Date:         2015/14/11
#
	clear

	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>
	export CUSER=$(whoami)
	export PASSWORD=linux
	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>

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

	# Cheking that this script does not run via ssh, otherwise some tests could be skipped
	checkTTY=$(tty | awk -F"/dev/" '{print $2}')
	if [ ! -z "$SSH_CLIENT" ] || [ ! -z "$SSH_TTY" ] || [[ "$checkTTY" = "tty1"  || "$checkTTY" = "tty2" || "$checkTTY" = "tty3" || "$checkTTY" = "tty4" || "$checkTTY" = "tty5" || "$checkTTY" = "tty6" ]]; then echo -ne "\n\n";	echo -ne "`tput bold``tput setf 4` ******************************************`tput sgr0` \n"; echo -ne " `tput bold``tput setf 6`GLXGEARS needs to run under [X Window System]`tput sgr0` \n"; echo -ne " `tput bold``tput setf 6`otherwise some tests could be skipped`tput sgr0` \n"; echo -ne " `tput bold``tput setf 6`DO NOT RUN CAIRO UNDER SSH`tput sgr0` \n"; echo -ne "`tput bold``tput setf 4` ******************************************`tput sgr0` \n"; echo -ne "\n\n" ;exit 1; fi

	check_mesa_utils=$(dpkg --get-selections | grep mesa-utils 2> /dev/null)
	if [ -z "$check_mesa_utils" ]; then start_spinner "++ Installing mesa-utils ..."; echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 5; echo $PASSWORD | sudo -S apt-get install mesa-utils -q=2 &> /dev/null; stop_spinner $? ;fi
	

		echo -ne "\n\n"
		echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
		read -p " --> How many iterations for GLXGEARS? : " iteration
		echo; clear; echo -ne "\n\n"; echo -ne " ++ You select [$iteration] iterations for glxgears \n\n\n" ; sleep 3

		rm /tmp/log* &> /dev/null ; rm /tmp/pidglx &> /dev/null ; rm /tmp/report* &> /dev/null
		export portconnected=$(xrandr | grep -v "disconnected" | grep -w "connected primary" | awk '{print $1}')  
		export statusport=$(xrandr | grep -v "disconnected" | grep -w "connected primary" | awk '{print $2}')  
		export currentmode=$(xrandr | grep -w "+" | awk '{print $1}')
		#export currentrefreshrate=$(xrandr | grep -w "+" | awk '{print $2}' | awk -F"*" '{print $1}' )
		#export criteriona=$(echo "scale=2; $currentrefreshrate+5" | bc)
		#export criterionb=$(echo "scale=2; $currentrefreshrate-5" | bc)

		#creating a report in format csv
		dat=$(date +'%m-%d-%Y-%T'); mkdir -p /home/$CUSER/Desktop/results/glxgears/
		echo "Component,Name,Status,Bug,Comment," > /home/$CUSER/Desktop/results/glxgears/glxgears_$dat.csv
		count=1

		for (( i=1; i <= $iteration; i++ ))
		do
	
			echo -ne " Launching glxgears in [$portconnected] ... \n\n"
			glxgears &> /tmp/log$count 2>&1 &     # this command send a log for stdout and error to a log and then send the app to background
			#sleep 10    # here needs some time in order to generate the Frame rate value in the log
			#GLXGEARSRR=$(cat /tmp/log$count | tail -n 1 | awk -F"= " '{print $2}' | awk -F" FPS" '{print $1}')
			pid=$(pidof glxgears | awk '{print $1}')  # the pid drops always to right cuz always needs to be one in awk command
			cpuusage=$(top -p $pid -n 1 | tail -3 | grep -w "$pid" | awk '{print $10}')
			memorysage=$(top -p $pid -n 1 | tail -3 | grep -w "$pid" | awk '{print $11}')
			TotalMemory=$(free -h | grep "Mem" | awk '{print $2}')
			MemoryUsed=$(free -h | grep "Mem" | awk '{print $3}')
			MemoryFree=$(free -h | grep "Mem" | awk '{print $4}')

			echo " Iteration number             : [$count]"
			echo " System total memory          : [$TotalMemory]"
			echo " System memory used           : [$MemoryUsed]"
			echo " System Memory free           : [$MemoryFree]"
			echo " glxgears CPU usage           : [$cpuusage%]"
			echo " glxgears memory usage        : [$memorysage%]"
			
			#echo " glxgears refresh rate       : [$GLXGEARSRR]"
			#echo " Pid                         : [$pid]"
			echo $pid >> /tmp/pidglx	
		
			# Sending information to TRC report
			echo "Glxgears,iteration #$count,pass," >> /home/$CUSER/Desktop/results/glxgears/glxgears_$dat.csv


			#if [[ `bc <<<"$GLXGEARSRR >= $criterionb && $GLXGEARSRR <= $criteriona"` == 1 ]]; then    #bc prints 1 or 0 to the standard output, which can be tested using bash's == string equality operator, so in this way bc does not print standar output
				 #echo "$count,$GLXGEARSRR,$currentrefreshrate,pass,criterion is : +- 4," >> /home/$CUSER/Desktop/results/glxgears/glxgears_$dat.csv
				 #echo " Status                       : `tput bold``tput setf 2`[PASS]`tput sgr0`"
				 #echo "glxgears,$GLXGEARSRR,$currentrefreshrate,pass,,criterion is : +- 5," >> /home/$CUSER/Desktop/results/glxgears/glxgears_$dat.csv
			#else
				#echo "$count,$GLXGEARSRR,$currentrefreshrate,fail,criterion is : +- 4" >> /home/$CUSER/Desktop/results/glxgears/glxgears_$dat.csv
				#echo " Status                       : `tput bold``tput setf 4`[FAIL]`tput sgr0`"
				#echo "glxgears,$GLXGEARSRR,$currentrefreshrate,fail,,criterion is : +- 5," >> /home/$CUSER/Desktop/results/glxgears/glxgears_$dat.csv
			#fi


			echo " ===================================================== " 
			let count+=1
			sleep 2
		done

	echo -ne "\n\n"
	echo "  Killing glxgears . . . "
		while read line
		do
			kill -9 $line
			wait $line 2> /dev/null   #this command hide the output of kill command      
		done < /tmp/pidglx	
			echo -ne "\n\n"
			total=$(expr $count - 1)
			passedtests=$(cat /home/$CUSER/Desktop/results/glxgears/glxgears_$dat.csv | grep -w "pass" | wc -l)
			failedtests=$(cat /home/$CUSER/Desktop/results/glxgears/glxgears_$dat.csv | grep -w "fail" | wc -l)
			pr=$(( passedtests + failedtests ))
			passrate=$( echo "scale =2; $passedtests*100/$pr" | bc)
			echo -ne "\n\n"
			echo -ne " -- Summary -- \n" | tee /home/$CUSER/Desktop/results/glxgears/summary-glxgears_$dat.csv
			echo -ne " Total of iterations realized  : [$total] \n" | tee -a /home/$CUSER/Desktop/results/glxgears/summary-glxgears_$dat.csv
			echo -ne " Passed tests                  : [$passedtests] \n" | tee -a /home/$CUSER/Desktop/results/glxgears/summary-glxgears_$dat.csv
			echo -ne " Failed tests                  : [$failedtests] \n" | tee -a /home/$CUSER/Desktop/results/glxgears/summary-glxgears_$dat.csv
			echo -ne " Pass rate                     : [$passrate%] \n" | tee -a /home/$CUSER/Desktop/results/glxgears/summary-glxgears_$dat.csv
			#echo -ne " The criterion was             : [+-5] \n" | tee -a /home/$CUSER/Desktop/results/glxgears/summary-glxgears_$dat.csv
			echo -ne "\n"
			echo -ne " a report was generate in --> /home/$CUSER/Desktop/results/glxgears/glxgears_$dat.csv \n"
			echo -ne " as well this summary was generate in --> /home/$CUSER/Desktop/results/glxgears/summary-glxgears_$dat.csv \n"

			
			pause(){
				local m="$@"
        		echo "$m"
			}

			while :
			do
				clear
				echo -ne " \n\n"
				echo -ne  " > Do you like to see the csv report in terminal in a friendly format ? \n\n"
				echo -ne " 1) Yes \n"
				echo -ne " 1) No \n\n"
				read -p " Your choose : " choose

					case $choose in
						1) 	cat /home/$CUSER/Desktop/results/glxgears/glxgears_$dat.csv | sed -e 's/,,/, ,/g' | column -s, -t | less -#5 -N -S > /tmp/report_$dat.csv
							echo -ne "\n\n" && cat /tmp/report_$dat.csv && echo -ne "\n\n" && exit 1 ;;
						2) 	echo -ne "\n\n"; exit 1 ;;
						*) pause ;;
					esac 

			done
