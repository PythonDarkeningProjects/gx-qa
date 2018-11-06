#!/bin/bash

	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>
	export CUSER=$(whoami)
	export PASSWORD=linux
	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>

	############################################################
	#			LOCAL COLORS                                   #
	############################################################
	export nc="\e[0m"
	export underline="\e[4m"
	export bold="\e[1m"
	export green="\e[1;32m"
	export red="\e[1;31m"
	export yellow="\e[1;33m"
	export blue="\e[1;34m"
	export cyan="\e[1;36m"

	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	export _ME=`basename $0`

function usage () {

    clear ;echo -ne "\n\n"; echo -ne " ${cyan}Intel® Graphics for Linux* | 01.org${nc} \n\n"
    echo -ne " Usage : ${yellow}${_ME}${nc} [options] \n\n"
    echo -e "  -h  | --help       See this menu"
    echo -e "  -n  | --normal     Generate a original grub menu"
    echo -e "  -j  | --jobs       Generate a jobs grub menu \n\n\n"; exit 2
}



	$@ #2> /dev/null
	clear

	#while test $# != 0
	#do
		case $1 in
			-h | --help) usage ;;
			-n | --normal) export _GRUB="${_THISPATH}/EFI/boot/grub.cfg" ; export _FLAG="grub.cfg";  break 2> /dev/null ;;
			-j | --jobs) export _GRUB="${_THISPATH}/EFI/boot/jobs.cfg" ; export _FLAG="jobs.cfg";  break 2> /dev/null ;;

			*) usage ;;
		esac
	#done


	clear; echo -ne "\n\n\n"
	echo -ne "Intel® Graphics for Linux* | 01.org \n\n"
	echo ${PASSWORD} | sudo -S ls &> /dev/null; sleep .5

	############################################################
	#			LOCAL VARIABLES                                #
	############################################################
	#_MOUNTPOINT=`df -T | grep /media/${CUSER}/ | awk '{print $7}'`
	#_VERIFY=`df -T | grep /media/${CUSER}/ | awk '{print $1}'| wc -l`
	#_USBID=`sudo blkid ${_MOUNTPOINT} | awk -F"UUID=" '{print $2}' | awk '{print $1}' | sed 's/"//g'`

	export _CLONEZILLA_PARTITION=`sudo blkid | grep "CLONEZILLA" | awk -F":" '{print $1}' | sed 's|/dev/||g'`
	export _CLONEZILLA_PARTITION_TYPE=`sudo blkid | grep "CLONEZILLA" | awk -F"TYPE=" '{print $2}' | awk '{print $1}' | sed s'/"//'g`
	export _CLONEZILLA_MOUNTPOINT=`lsblk | grep "${_CLONEZILLA_PARTITION}" | awk '{print $7}'`
	export _CLONEZILLA_LOCAL_FOLDER="/home/ghost/clonezilla"
	export _SCRIPTS_PARTITION=`sudo blkid | grep "scripts" | awk -F":" '{print $1}' | sed 's|/dev/||g'`
	export _SCRIPTS_PARTITION_TYPE=`sudo blkid | grep "scripts" | awk -F"TYPE=" '{print $2}' | awk '{print $1}' | sed s'/"//'g`
	export _SCRIPTS_MOUNTPOINT=`lsblk | grep "${_SCRIPTS_PARTITION}" | awk '{print $7}'`
	export _SCRIPTS_LOCAL_FOLDER="/home/ghost/scripts"
	export _MAIN_USB=`echo ${_CLONEZILLA_PARTITION} | sed 's/[0-9]*//g'`
	export _COUNT=0 export _COUNT_B=0 export _COUNT_C=0


	############################################################
	# Loading functions file                                   #
	############################################################	
	source ${_THISPATH}/custom/packages/all/functions.sh



	############################################################
	#			USB CHECK                                      #
	############################################################

	if [ -z "${_CLONEZILLA_MOUNTPOINT}" -a ! -z "${_CLONEZILLA_PARTITION}" ]; then

		start_spinner "${bold}-->${nc} Mounting clonezilla partition ..."
			sudo mkdir -p ${_CLONEZILLA_LOCAL_FOLDER}
			sudo mount /dev/${_CLONEZILLA_PARTITION} ${_CLONEZILLA_LOCAL_FOLDER}
		stop_spinner $?

		export _CLONEZILLA_MOUNTPOINT=`lsblk | grep "${_CLONEZILLA_PARTITION}" | awk '{print $7}'`

	elif [ -z "${_CLONEZILLA_PARTITION}" ]; then
		echo -ne " ${red}NO CLONEZILLA USB CONNECTED${nc} \n"
		echo -ne " ${yellow}Please connect one CLONEZILLA USB stick to continue${nc} \n\n"
		exit 1
	fi	

	if [ -z "${_SCRIPTS_MOUNTPOINT}" -a ! -z "${_SCRIPTS_PARTITION}" ]; then

		start_spinner "${bold}-->${nc} Mounting scripts partition ..."
			sudo mkdir -p ${_SCRIPTS_LOCAL_FOLDER}
			sudo mount /dev/${_SCRIPTS_PARTITION} ${_SCRIPTS_LOCAL_FOLDER}
		stop_spinner $?

		export _SCRIPTS_MOUNTPOINT=`lsblk | grep "${_SCRIPTS_PARTITION}" | awk '{print $7}'`

	elif [ -z "${_SCRIPTS_PARTITION}" ]; then
		echo -ne " ${red}NO CLONEZILLA USB CONNECTED${nc} \n"
		echo -ne " ${yellow}Please connect one CLONEZILLA USB stick to continue${nc} \n\n"
		exit 1
	fi	

	if [ "${_CLONEZILLA_MOUNTPOINT}" != "${_CLONEZILLA_LOCAL_FOLDER}" ]; then export _CLONEZILLA_LOCAL_FOLDER="${_CLONEZILLA_MOUNTPOINT}"; fi
	if [ "${_SCRIPTS_MOUNTPOINT}" != "${_SCRIPTS_LOCAL_FOLDER}" ]; then export _SCRIPTS_LOCAL_FOLDER="${_SCRIPTS_MOUNTPOINT}"; fi
	

	############################################################
	#			COPYING FILES TO THE USB                       #
	############################################################

	# Deleting old files
	while read line
	do
		start_spinner "${cyan}-->${nc} Deleting ${_CLONEZILLA_LOCAL_FOLDER}/${line} ..."
			sleep .2; sudo rm -rf ${_CLONEZILLA_LOCAL_FOLDER}/${line} &> /dev/null
		stop_spinner $?
		wait
	done < ${_THISPATH}/list 
	
	wait
	
	# Copying new files
	start_spinner "${blue}-->${nc} sync custom folder to ${_SCRIPTS_LOCAL_FOLDER}/ ..."
		_EXCLUDE_FILES="grub.cfg"
		sudo rsync -avrz --exclude "${_EXCLUDE_FILES}" ${_THISPATH}/custom/ ${_SCRIPTS_LOCAL_FOLDER}/custom/ &> /dev/null
		#sleep .2; cp -r ${_THISPATH}/custom/ ${_MOUNTPOINT}/
	stop_spinner $?
	wait
	
	start_spinner "${blue}-->${nc} Copying grub.cfg to ${_CLONEZILLA_LOCAL_FOLDER}/ ..."
		sleep .2; sudo cp ${_GRUB} ${_CLONEZILLA_LOCAL_FOLDER}/EFI/boot/
		if [ "${_FLAG}" != "grub.cfg" ]; then
			sudo mv ${_CLONEZILLA_LOCAL_FOLDER}/EFI/boot/${_FLAG} ${_CLONEZILLA_LOCAL_FOLDER}/EFI/boot/grub.cfg &> /dev/null
		fi
	stop_spinner $?
	wait
	

	start_spinner "${blue}-->${nc} Copying syslinux.cfg to ${_CLONEZILLA_LOCAL_FOLDER}/ ..."
		sleep .2; sudo cp ${_THISPATH}/syslinux/syslinux.cfg ${_CLONEZILLA_LOCAL_FOLDER}/syslinux/
	stop_spinner $?
	wait

	start_spinner "${blue}-->${nc} Copying default_mount.sh to ${_CLONEZILLA_LOCAL_FOLDER}/ ..."
		sleep .2; sudo cp ${_THISPATH}/custom/default_mount.sh ${_CLONEZILLA_LOCAL_FOLDER}/
	stop_spinner $?
	wait

	start_spinner "${blue}-->${nc} Copying ocswp-grub2.png to ${_CLONEZILLA_LOCAL_FOLDER}/ ..."
		sleep .2; sudo cp ${_THISPATH}/EFI/boot/ocswp-grub2.png ${_CLONEZILLA_LOCAL_FOLDER}/EFI/boot/ocswp-grub2.png
	stop_spinner $?
	wait

	start_spinner "${green}-->${nc} Unmounting ${_CLONEZILLA_MOUNTPOINT} ..."
		sleep .2; sudo umount -f ${_CLONEZILLA_MOUNTPOINT} &> /dev/null
	stop_spinner $?

	if [ "${_STATUS}" = "1" ]; then ((_COUNT++)); fi

	start_spinner "${green}-->${nc} Unmounting ${_SCRIPTS_MOUNTPOINT} ..."
		sleep .2; sudo umount -f ${_SCRIPTS_MOUNTPOINT} &> /dev/null
	stop_spinner $?

	if [ "${_STATUS}" = "1" ]; then ((_COUNT++)); fi


	if [ "${_COUNT}" != "0" ]; then

		echo -e "--> ${yellow}Killing all USB process${nc} ..."
			_PROCESS_LIST_A=`sudo lsof ${_CLONEZILLA_MOUNTPOINT} 2> /dev/null | awk '{print $2}' | sed 's/[^0-9]*//g' | sed '/^\s*$/d'`
			_PROCESS_LIST_B=`sudo lsof ${_SCRIPTS_MOUNTPOINT} 2> /dev/null | awk '{print $2}' | sed 's/[^0-9]*//g' | sed '/^\s*$/d'`
			
		if [ ! -z "${_PROCESS_LIST_A}" ]; then
			for process in ${_PROCESS_LIST_A}; do
				start_spinner "--> Killing ${process} for clonezilla partition ..."
					sleep .2; sudo kill -9 ${process} &> /dev/null
				stop_spinner $?
				if [ "${_STATUS}" = "1" ]; then ((_COUNT_B++)); fi
			done
		fi

		if [ ! -z "${_PROCESS_LIST_B}" ]; then
			for process in ${_PROCESS_LIST_B}; do
				start_spinner "--> Killing ${process} for scripts partition ..."
					sleep .2; sudo kill -9 ${process} &> /dev/null
				stop_spinner $?
				if [ "${_STATUS}" = "1" ]; then ((_COUNT_B++)); fi
			done
		fi

		if [ "${_COUNT_B}" != "0" ]; then
			echo -e "--> ${red}ERROR${nc} : unable to kill USB's process ..."

			start_spinner "--> Trying to eject the USB ..."
				sleep .2; sudo eject ${_MAIN_USB} &> /dev/null
			stop_spinner $?

			if [ "${_STATUS}" = "1" ]; then echo -ne "--> Please disconnect the USB \n\n";notify-send  "The USB was eject successfully" "Please disconnect the USB"; exit 1; fi
			
		else

			export _CLONEZILLA_MOUNTPOINT=`lsblk | grep "${_CLONEZILLA_PARTITION}" | awk '{print $7}'`
			export _SCRIPTS_MOUNTPOINT=`lsblk | grep "${_SCRIPTS_PARTITION}" | awk '{print $7}'`

			if [ ! -z "${_CLONEZILLA_MOUNTPOINT}" ]; then
				start_spinner "--> Unmounting clonezilla partition ..."
					sleep .2; sudo umount -f ${_CLONEZILLA_MOUNTPOINT}
				stop_spinner $?
				if [ "${_STATUS}" = "1" ]; then ((_COUNT_C++)); fi
			fi

			if [ ! -z "${_SCRIPTS_MOUNTPOINT}" ]; then
				start_spinner "--> Unmounting scripts partition ..."
					sleep .2; sudo umount -f ${_SCRIPTS_MOUNTPOINT}
				stop_spinner $?
				if [ "${_STATUS}" = "1" ]; then ((_COUNT_C++)); fi
			fi

			if [ "${_COUNT_C}" != "0" ]; then
				echo -e "--> ${red}ERROR${nc} : unable to unmount the USB partitions ..."

				start_spinner "--> Trying to eject the USB ..."
					sleep .2; sudo eject ${_MAIN_USB} &> /dev/null
				stop_spinner $?

				if [ "${_STATUS}" = "1" ]; then echo -ne "--> Please disconnect the USB \n\n";notify-send "Unable to eject the USB" "Please disconnect the USB" ; exit 1; fi
			else
				start_spinner "${bold}-->${nc} Ejecting the USB ..."
					sleep .2; sudo eject ${_MAIN_USB} &> /dev/null
				stop_spinner $?
			fi
		fi

	else
		start_spinner "${bold}-->${nc} Ejecting the USB ..."
			sleep .2; sudo eject ${_MAIN_USB} &> /dev/null
		stop_spinner $?
	fi

	echo -ne "\n\n"
	echo -ne " ============================ \n"
	echo -ne " ========== ${cyan}FINISH${nc} ========== \n"
	echo -ne " ============================ \n\n"

	notify-send "Finish" "all files were synchronized successfully, now you can unplug the USB"

	exit 1

