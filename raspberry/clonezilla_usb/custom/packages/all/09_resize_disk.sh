#!/bin/bash

#if [ $# -lt 3 ]
#then
#    echo "Usage: ${0##*/} DISK PARTITION SIZE"
#    echo "       e.g: ${0##*/} /dev/sda 2 30GB"
#    exit 1
#fi

#parted -s "$1" resizepart "$2" "$3" || exit 1
#e2fsck -y -f "${1}${2}"
#resize2fs "${1}${2}"

#exit 0


# parted -s /dev/ resizepart 1 XGB/XMB
# te toma lo que ya tienes y te pone lo restante
# shrink = decrementar
# https://www.gnu.org/software/parted/manual/html_chapter/parted_2.html#SEC30

####################################################################
# In order to use this script you need to create a linux image
# with the following partitions
# i    - (logical partition) 500MB for efi 
# ii   - primary partition (SWAP) (3GB) (3072MB)
# iii  - primary partion (/) ext4 (8GB) (8192MB)
#
# Please follow the next steps to create this partitions
# Once in linux live CD 
# Installation type > Something else > next
# please eliminate all partitions linux has
# 
# For EFI PARTITION
# add buttnm 
# Size : 500MB
# Type for the new partition : logical
# Location for the new partition : Beginning of this space
# Use as  : EFI System Partition 
#
# For SWAP partition
# add buttom
# Type for the new partition : Primary
# Location for the new partition : Beginning of this space
# Use as  : swap area 
#
# For root partition
# add buttom
# Type for the new partition : Primary
# Location for the new partition : Beginning of this space
# Use as  : Ext4 journaling file system
# Mount point : /
#
#
####################################################################

	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`

	##############################################################
	# Load functions                                             #
	##############################################################
	source ${_THISPATH}/functions.sh
	source /root/custom/config.cfg


	#_SPACE_AVAILABLE=`df -h | grep sda | head -1 | awk '{print $4}'`
	#_TOTAL_SPACE=`lsblk | grep -w "sda" | awk '{print $4}'`
	#_MOUNT_POINT=`lsblk | grep sda | head -1 | awk '{print $1}'` # sdX
	#_PARTITION_DISK=`df -h | grep sda | grep -w "/" | awk '{print $1}' | sed 's/[^0-9]//g'` # like 2
	_TOTAL_SPACE=`parted -s /dev/sda unit GB print free | grep "Free Space" | tail -n1 | awk '{print $3}'`
	_PARTITION_DISK=`parted -s /dev/sda unit GB print free | grep "ext4" | awk '{print $1}'`
	_PARTIMAG="/home/partimag"
	
	_RESTORE_IMAGE_SIZE=`cat ${_PARTIMAG}/${default_image}/blkdev.list | grep -v KNAME | head -1 | awk '{print $3}' | tr -d "GBM"`

	start_spinner "--> Resizing ${_MOUNT_POINT} ..."
		sleep .5
		parted -s /dev/sda resizepart ${_PARTITION_DISK} ${_RESTORE_IMAGE_SIZE}
	stop_spinner $?

# Example :
# parted -s /dev/sda resizepart 2 935GB