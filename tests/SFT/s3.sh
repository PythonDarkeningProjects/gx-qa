#!/bin/bash

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


	export thispath=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd ) # <- current script path, even if i call from tux ;)
	source $thispath/common.sh

	clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
	start_spinner " ++ Starting ... "
	echo $PASSWORD | sudo -S ls &> /dev/null; sleep 5
	stop_spinner $?

	cat /sys/power/state | grep mem &> /dev/null
	if [ $? -eq 0 ]; then
		#date
		# Clear old alarm
		start_spinner " --> Cleaning the old alarm ... "
		sleep 2; echo "0" | sudo tee /sys/class/rtc/rtc0/wakealarm &> /dev/null
		stop_spinner $? | tee .log

		check=$(cat .log | grep "FAIL")

		if [ ! -z "$check" ]; then
			check_rc "echo 0 > /sys/class/rtc/rtc0/wakealarm" ${RC}
			echo -ne "\n\n"; exit 2
		fi

		start_spinner " --> Setting 15 seconds for wakeup ... "
		sleep 2; echo "+15" | sudo tee /sys/class/rtc/rtc0/wakealarm &> /dev/null
		stop_spinner $? | tee .log

		check=$(cat .log | grep "FAIL")

	        if [ ! -z "$check" ]; then
	                check_rc "echo 15 > /sys/class/rtc/rtc0/wakealarm" ${RC}
	               echo -ne "\n\n"; exit 2
	        fi
	#	to change to /sys/class/rtc/rtcN/wakeup in future kernel

		# Save dmesg before S3
		echo $PASSWORD | sudo -S dmesg -c >> dmesg
		start_spinner " --> Sending to S3 state for 15 seconds ... "
		sleep 3; echo mem | sudo tee /sys/power/state &> /dev/null	#S3
		stop_spinner $? | tee .log

		echo $PASSWORD | sudo -S dmesg -c >> dmesg

		check=$(cat .log | grep "FAIL")
	    
	        if [ ! -z "$check" ]; then
	                check_rc "echo mem > /sys/power/state" ${RC}
	               echo -ne "\n\n"; exit 2
	        fi

	#	date
	else
		echo -ne "\n\n"
		echo "${red}NOTE : S3 is not supported${nc}"
		echo -ne "\n\n"; exit 2
	fi

	echo -ne "\n\n"
	echo -ne " ${bold}${blue}suspend_resume test has finish${nc} \n\n\n"; exit 2
