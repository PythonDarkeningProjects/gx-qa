#!/bin/bash

	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	export _ENV_FILE="/root/custom/env.vars"
	export TERM=xterm

	##############################################################
	# LOAD functions                                             #
	##############################################################

	source ${_THISPATH}/functions.sh


	# looking for the usb
	whereisUSB=`lsblk -S | grep usb | awk '{print $1}'`
	# getting the disk/eMMC attached to the DUT
	lsblk -d | grep -ve ${whereisUSB} -ve "filesystem.squashfs" -ve M > attachedDisk
	# selecting mayor disk capacity to clone
	howManyDisk=`cat attachedDisk | wc -l`

	# here i guess that the maximum disk in the DUT will be 2 in the worst case
	if [ ${howManyDisk} -eq 1 ];then
		echo -e "${blue}>>> (info)${nc} 1 disk was found in the DUT"
		export disk_label=`cat attachedDisk | head -1 | awk '{print $1}'`

	elif [ ${howManyDisk} -eq 2 ];then
		echo -e "${blue}>>> (info)${nc} 2 disk was found in the DUT"
		echo -e "${blue}>>> (info)${nc} Selecting the highest capacity disk ..."
		disk_A=`cat attachedDisk | head -1 | awk '{print $1}'`
		disk_B=`cat attachedDisk | tail -1 | awk '{print $1}'`
		disk_A_capacity=`lsblk -b --output SIZE -n -d /dev/${disk_A}`
		disk_B_capacity=`lsblk -b --output SIZE -n -d /dev/${disk_B}`

		if [ ${disk_A_capacity} -gt ${disk_B_capacity} ]; then
			echo -e "${blue}>>> (info)${nc} dev/${disk_A} was selected"
			export disk_label=${disk_A}
		elif [ ${disk_B_capacity} -gt ${disk_A_capacity} ]; then
			echo -e "${blue}>>> (info)${nc} dev/${disk_B} was selected"
			export disk_label=${disk_B}
		fi

	elif [ ${howManyDisk} -eq 0 ];then
		echo -ne "\n\n"
		cat ${thispath}/asciiImages/homero
		echo -ne "${red}>>> (err)${nc} no disks were found in the DUT \n\n\n"
		exit 1
	fi

	#export _MOUNT_POINT=`lsblk | grep sda | head -1 | awk '{print $1}'`
	export _MOUNT_POINT=${disk_label}
	export _FORMAT="ext4"

	export _EXT4_PARTITION=`file -sL /dev/${_MOUNT_POINT}* | grep ${_FORMAT} |awk '{print $1}' | sed 's/://g'`

	start_spinner ">>> (info) Mounting ${_EXT4_PARTITION} ..."
		sleep 1.75
		mount -t ${_FORMAT} -o rw ${_EXT4_PARTITION} /mnt
		# --> mounting system folders in order to install deb packages
		mount --bind /dev /mnt/dev
		mount --bind /proc /mnt/proc
		mount --bind /sys /mnt/sys
	stop_spinner $?

	if [ "${_STATUS}" = 0 ]; then
		echo "mount_image=DONE" >> ${_ENV_FILE}
	else
		echo "mount_image=FAIL" >> ${_ENV_FILE}
	fi

	# resolv.conf file has the DNS for clonezilla environment (this as WA when clonezilla is in a subshell into /mnt)
	start_spinner ">>> (info) Copying resolv.conf to /mnt ..."
		sleep 1.75
		cp /etc/resolv.conf /mnt/etc/
	stop_spinner $?
