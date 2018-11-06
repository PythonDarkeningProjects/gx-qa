#!/bin/bash
#
#   Copyright (c) Intel, 2015
#
# File:         DriversInformation.sh
#
# Description:
#
# Author(s):    Humberto Perez <humberto.i.perez.rodriguez@intel.com>
#
# Date:         2015/20/12
#
# Script to get debug logs for IGT tests
#
# Debugging log_buf_len kernel parameter To capture a full drm log from the boot, one need to make the kernel log buffer large enough, say 4MB. The KConfig option is limited to 2MB but the log buffer size can be overridden on kernel command line with: log_buf_len=4M

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


	
		
function debug {

	clear ;	echo $PASSWORD | sudo -S ls -l /tmp &> /dev/null ; sleep 2; echo -ne "\n\n"
	echo " -- Checking GRUB Menu for - initcall_debug & drm.debug=0xe & log_buf_len=4M - flags --"
	sleep 2
	
	# Check if the line 11 of the GRUB menu has a diferent value than GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
	# in that case that the user has a diferent ones

	check=$(cat -n /etc/default/grub | grep -w 11 | awk -F"11" '{print $2}' | awk -F"\t" '{print $2}')
	value='GRUB_CMDLINE_LINUX_DEFAULT="quiet splash initcall_debug drm.debug=0xe log_buf_len=4M"'

		if [ "$check" == "$value" ]; then

			echo " -- `tput bold``tput setf 6`GRUB already has the flags - initcall_debug & drm.debug=0xe & log_buf_len=4M-`tput sgr0`"
			echo -ne "\n"
		else
			echo -ne " Adding flags - initcall_debug & drm.debug=0xe & log_buf_len=4M - to GRUB ... "
			echo $PASSWORD | sudo -S sed -i '11s/^.*$/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash initcall_debug drm.debug=0xe log_buf_len=4M"/g' /etc/default/grub 
				if [ $? = 0 ]; then echo -ne " [`tput bold``tput setf 2`OK`tput sgr0`] \n"; sleep 2; fi
			echo " The DUT will reboot in 7 seconds in order to update GRUB"
			echo " `tput bold``tput setf 6`Please run again this script after rebooting the DUT`tput sgr0`"
			echo $PASSWORD | sudo -S update-grub &> /dev/null
			start_spinner ' > rebooting ...'
			sleep 7
			stop_spinner $?
			echo $PASSWORD | sudo -S reboot
			exit 1
			echo -ne "\n\n"
		fi

	echo " -- Checking if [ IGT_LOG_DEBUG=debug ] flag exists in your file [~/.bashrc] --"
	cat /home/$CUSER/.bashrc | grep "export IGT_LOG_DEBUG=debug" &> /dev/null
	# 0 mean successful / 1 mean that doesn't found the value
	
	if [ $? -eq 1 ]; then
    	#exporting the parameter
    	echo 'export IGT_LOG_DEBUG=debug' >> /home/$CUSER/.bashrc
    	echo 
    	echo " -- `tput bold``tput setf 6`Parameter [IGT_LOG_DEBUG=debug] exported your .bashrc`tput sgr0` --"
  	else
    	echo " -- `tput bold``tput setf 6`You already have [IGT_LOG_DEBUG=debug] in your .bashrc`tput sgr0` --"
 	fi  

 	if [ -z "$IGT_LOG_DEBUG" ]; then
 		echo -ne "\n\n"
 		echo -ne " --> `tput bold``tput setf 4`Please reload your bashrc with the next command`tput sgr0` \n"
 		echo -ne " --> `tput bold``tput setf 4`bash`tput sgr0` \n"
 		echo -ne " --> `tput bold``tput setf 4`and then run again this script`tput sgr0` \n\n"
 		exit 1
 	fi
	
	sleep 3

		pause(){
			local m="$@"
        	echo "$m"
		}

		while :
		do
			clear
			echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
			echo -ne " - `tput bold``tput setf 6`In order to get only the specific kernel log called dmesg`tput sgr0` \n"
			echo -ne " - `tput bold``tput setf 6`a good practice is to delete it then reboot, then reproduce your bug`tput sgr0` \n" 
			echo -ne " - `tput bold``tput setf 6`so the file will contain only the logs dealing with your bug`tput sgr0` \n\n"  
			echo " ** Do you want to reboot in order to get only the dealing logs? ** "
			echo -ne " 1) Yes \n"
			echo -ne " 2) No \n\n"
			read -e -p " Your choose : " choose

    		case $choose in
	        	1 ) clear 
					echo " -- Restaring the DUT ..."; 
					echo " -- Next time you need to select [No] option in order to getting Kernel logs -- "
					echo
					echo "    Press any key to continue"
					read -n 1 line
					echo " -- Deleting kernel_log located in [/var/log/kernel.log] ... "
					echo $PASSWORD | sudo -S rm /var/log/kern.log
					start_spinner ' > rebooting ...'
					sleep 7
					stop_spinner $?
					echo $PASSWORD | sudo -S reboot
					exit 1 ;;
        	
        		2 ) clear
					echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
					echo -ne " -- Getting Kernel Logs -- \n\n"
					sleep 3
					mkdir -p /home/$CUSER/Desktop/results/debug-logs 2> /dev/null
				
					start_spinner ' - Getting dmesg log ...'
					sleep 5; dmesg > /home/$CUSER/Desktop/results/debug-logs/dmesg.log; stop_spinner $?
	
					start_spinner ' - Getting GPU hang log ...'
					sleep 5; echo $PASSWORD | sudo -S cat /sys/kernel/debug/dri/0/i915_error_state > /home/$CUSER/Desktop/results/debug-logs/GPU_hang.log; stop_spinner $?
	
					start_spinner ' - Getting GPU crash dump file ...'
					sleep 5; echo $PASSWORD | sudo -S cat /sys/class/drm/card0/error > /home/$CUSER/Desktop/results/debug-logs/GPU_crash_dump_file.log; stop_spinner $?
	
					start_spinner ' - Getting Xorg log ...'
					sleep 5; echo $PASSWORD | sudo -S cat /var/log/Xorg.0.log > /home/$CUSER/Desktop/results/debug-logs/Xorg.log; stop_spinner $?
	
						#cat /opt/X11R7/log/Xorg.0.log > /home/$CUSER/dev/kernel_log/Xorg.rtf   # This is the correct one, im not sure =(

					echo -ne "\n\n"
					echo " -- Summary --"
					echo
					totalfiles=$(ls /home/$CUSER/Desktop/results/debug-logs | wc -l)
					filez=$(du -sh /home/$CUSER/Desktop/results/debug-logs | awk '{print $1}')
					echo -ne " Log files  : [$totalfiles] \n"
					echo -ne " File sizes : [$filez] \n"
					echo -ne " Debug logs were save in : /home/$CUSER/Desktop/results/debug-logs \n\n"
					echo -ne "\n\n"
					exit 1 ;;

				*) pause ;;

    		esac
    
		done



}

		pause(){
			local m="$@"
        	echo "$m"
		}

	while :
	do
		clear
		echo -ne "\n\n"
		echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
		echo -ne " This script is valid to get debug logs for IGT tests \n"
		echo -ne " Do you want to continue ? \n\n"
		echo -ne " 1) Yes \n"
		echo -ne " 2) No \n\n"
		read -e -p " Your choose : " choose
	
			case $choose in 

				1) if [ "$1" = "menu" ]; then debug "menu"; elif [ -z "$1"]; then debug; fi ;;


				2) echo -ne "\n\n\n"; exit 1 ;;


				*) pause ;;


			esac		

	done


