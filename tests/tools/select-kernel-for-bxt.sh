#!/bin/bash

	# initcall_debug <= this parameter causes issues when trying to resume from s3, i need to investigate more about it
	# ignore_loglevel <= this parameter shows a lot of messages at start
	# maxcpus=1 <== this command limit the max cpus in use
	# i915.enable_rc6=1 <== this command (you can check it with : dmesg | grep -i RC6 and it must shows as "on")
	# processor.max_cstate=2 <== this command limit the use of cstates in the DUT in order to get a good performance
	# idle=halt <== workaround for bad performance in APL, but we need to confirm it (this a temporal solution once the bios fixed this low performance)
	# acpi_enforce_resources=lax ??
	# i915.preliminary_hw_support=1 (needed for APl in order to enable i915 driver)
	# no_console_suspend ??
	# i915.enable_guc_submission=1 (enable guc in the DUT , checked by dmesg | grep -i guc)
	# nomodeset <== Disable i915 by kernel command line

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


	pause(){
		local m="$@"
		echo "$m"
	}		


	while : 
	do

		clear ; echo -ne "\n\n"
		echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
		ls /boot/ | grep initrd | sed 's/initrd.img-//g' | sort -r > /tmp/kernels

		number=""
		while [[ ! $number =~ ^[0-9]+$ ]]; do
			count=1
			clear ; echo -ne "\n\n"
			echo -ne " Intel® Graphics for Linux* | 01.org [under SSH] \n\n\n"
			echo -ne " Select a kernel to boot with BXT \n\n"
			
			while read line
			do
				echo -ne " $line \n" | sed 's/'"$line"'/'"$count"') '"$line"'/g'
				let count+=1
			done < /tmp/kernels
			
			echo 
    		echo -ne " Your choice : "
    		read number
			done
			export number


			check=$(cat -n /tmp/kernels | awk '{print $1}' | grep -w "$number")

			if [ -z "$check" ]; then
				echo -ne "\n\n"
				echo -ne " Please enter a valid option \n\n"
				echo -ne "\t Press any key to continue \t "; read -n 1; pause

			else
				export kernelname=$(sed -n "$number"p /tmp/kernels)
				echo -ne "\n\n"
				echo -ne " You've selected : [$kernelname] \n"
				echo -ne " Do you want to continue ? \n\n"
				echo -ne " 1) Yes \n"
				echo -ne " 2) No \n\n"
				read -e -p " Your choice : " choose


				case $choose in

					1) 
						clear ; echo -ne "\n\n"
						echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
						echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 2

						check_initrd=$(echo $PASSWORD | sudo -S ls /boot/efi/ | grep -w initrd.img)

						if [ ! -z "$check_initrd" ]; then 
							start_spinner "++ Deleting old initrd.img ..."
							echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 2
							echo $PASSWORD | sudo -S rm /boot/efi/initrd.img &> /dev/null
							stop_spinner $?
						fi

						check_vmlinuz=$(echo $PASSWORD | sudo -S ls /boot/efi/ | grep -w vmlinuz)

						if [ ! -z "$check_vmlinuz" ]; then
							start_spinner "++ Deleting old vmlinuz ..."
							echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 2
							echo $PASSWORD | sudo -S rm /boot/efi/vmlinuz &> /dev/null
							stop_spinner $?
						fi

						check_startup=$(echo $PASSWORD | sudo -S ls /boot/efi/ | grep -w startup.nsh)

						if [ ! -z "$check_startup" ]; then
							start_spinner "++ Deleting old startup.nsh ..."
								echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 2
								echo $PASSWORD | sudo -S rm /boot/efi/startup.nsh &> /dev/null
							stop_spinner $?

							start_spinner "++ Creating a startup.nsh ..."
							echo "FS0:" | sudo tee /boot/efi/startup.nsh &> /dev/null
							echo 'echo "BXT BOOT"' | sudo tee -a /boot/efi/startup.nsh &> /dev/null
							echo "vmlinuz root=/dev/sda2 initrd=initrd.img idle=halt log_buf_len=4M i915.enable_rc6=1 i915.preliminary_hw_support=1 drm.debug=14 i915.enable_guc_submission=1" | sudo tee -a /boot/efi/startup.nsh &> /dev/null
							stop_spinner $?
						else

							start_spinner "++ Creating a startup.nsh ..."
							echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 2
							echo "FS0:" | sudo tee /boot/efi/startup.nsh &> /dev/null
							echo 'echo "BXT BOOT"' | sudo tee -a /boot/efi/startup.nsh &> /dev/null
							echo "vmlinuz root=/dev/sda2 initrd=initrd.img idle=halt log_buf_len=4M i915.enable_rc6=1 i915.preliminary_hw_support=1 drm.debug=14 i915.enable_guc_submission=1" | sudo tee -a /boot/efi/startup.nsh &> /dev/null
							stop_spinner $?

						fi

						start_spinner "++ Adding [$kernelname] /boot/efi ..."
						echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 2
						echo $PASSWORD | sudo -S cp /boot/initrd.img-$kernelname /boot/efi/initrd.img #&> /dev/null
						echo $PASSWORD | sudo -S cp /boot/vmlinuz-$kernelname /boot/efi/vmlinuz #&> /dev/null
						stop_spinner $?

						echo -ne "\n\n"; exit 2
													
					;;


					2) pause ;;

				esac
			
			fi
							
		done

	done