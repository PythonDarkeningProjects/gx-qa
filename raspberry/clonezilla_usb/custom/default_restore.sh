#!/bin/bash

#==============================================================================#
#==============================================================================#
export nc="\e[0m"
export underline="\e[4m"
export bold="\e[1m"
export green="\e[1;32m"
export red="\e[1;31m"
export yellow="\e[1;33m"
export blue="\e[1;34m"
export cyan="\e[1;36m"

#==============================================================================#
#        GLOBAL VARIABLES                                                      #
#==============================================================================#

# The local work directory
WORKDIR="/root/custom"
source ${_THISPATH}/packages/all/functions.sh

# Config filepaths
_CONFIG_FILE="$1"
_ENV_FILE="${WORKDIR}/env.vars"

#==============================================================================#
#        CHANGING LENGUAJE SETTINS TO US                                       #
#==============================================================================#
clear; echo -ne "\n\n\n"
echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
echo -ne " --> ${yellow}Changing leguaje settings to US${nc} ...   "
loadkeys us
if [ $? = 0 ]; then echo -e "[${green}OK${nc}]"; else echo -e "[${red}FAIL${nc}]"; fi

#==============================================================================#
#        INITIALIZATION                                                        #
#==============================================================================#

# Source config files for default values
source ${_CONFIG_FILE}
source ${_ENV_FILE}

# Check if system setup is ready
if [ "$SYSTEM_READY" != "1" ]
then
	echo -ne " --> ${red}System not ready to restore disk!${nc} \n\n"
	exit 1
fi

#==============================================================================#
#        GHOST RESTORATION                                                     #
#==============================================================================#

# Check if ghost image exist in partimag directory
if [ -z "${default_image}" ]; then
	echo -ne " --> ${red}The default image is empty in config.cfg${nc} \n\n"
	exit 1
elif [ ! -z "${default_image}" ] && [ ! -d "${PARTIMAG}/${default_image}" ]; then
    echo -ne " --> Image : [${cyan}${default_image}${nc}] ${red}does not exist in${nc} ${PARTIMAG} \n\n"
    exit 1
fi


#==============================================================================#
#        Check for the default disk                                            #
#==============================================================================#
if [ -z "${default_disk}" ]; then
	#default_disk=`lsblk | grep sda | head -1 | awk '{print $1}'`

    # looking for the usb
    whereisUSB=`lsblk -S | grep usb | awk '{print $1}'`
    # getting the disk/eMMC attached to the DUT
    lsblk -d | grep -ve ${whereisUSB} -ve "filesystem.squashfs" -ve M > attachedDisk
    # selecting mayor disk capacity to clone
    howManyDisk=`cat attachedDisk | wc -l`

    # here i guess that the maximum disk in the DUT will be 2 in the worst case
    if [ ${howManyDisk} -eq 1 ];then
        echo -e "${blue}>>> (info)${nc} 1 disk was found in the DUT"
        default_disk=`cat attachedDisk | head -1 | awk '{print $1}'`

    elif [ ${howManyDisk} -eq 2 ];then
        echo -e "${blue}>>> (info)${nc} 2 disk was found in the DUT"
        echo -e "${blue}>>> (info)${nc} Selecting the highest capacity disk ..."
        disk_A=`cat attachedDisk | head -1 | awk '{print $1}'`
        disk_B=`cat attachedDisk | tail -1 | awk '{print $1}'`
        disk_A_capacity=`lsblk -b --output SIZE -n -d /dev/${disk_A}`
        disk_B_capacity=`lsblk -b --output SIZE -n -d /dev/${disk_B}`

        if [ ${disk_A_capacity} -gt ${disk_B_capacity} ]; then
            echo -e "${blue}>>> (info)${nc} dev/${disk_A} was selected"
            default_disk=${disk_A}
        elif [ ${disk_B_capacity} -gt ${disk_A_capacity} ]; then
            echo -e "${blue}>>> (info)${nc} dev/${disk_B} was selected"
            default_disk=${disk_B}
        fi

    elif [ ${howManyDisk} -eq 0 ];then
        echo -ne "\n\n"
        cat ${thispath}/asciiImages/homero
        echo -ne "${red}>>> (err)${nc} no disks were found in the DUT \n\n\n"
        exit 1
    fi
fi

#==============================================================================#
#        CHECKING IMAGE and DISK SIZE                                          #
#==============================================================================#
# restore_image_size=`cat ${PARTIMAG}/${default_image}/blkdev.list | grep -v KNAME | head -1 | awk '{print $3}' | tr -d "GBM"` # works only for Ubuntu 16.04 and below
restore_image_size=`cat ${PARTIMAG}/${default_image}/blkdev.list | grep -w "sda" | awk '{print $3}' | tr -d "GBM"` # works with all Ubuntu versions
#disk_size=`lsblk | grep sda | head -1 | awk '{print $4}' | tr -d "GBM"`
disk_size=`lsblk | grep -w ${default_disk} | head -1 | awk '{print $4}' | tr -d "GBM"`



if (( $(echo "${disk_size} < ${restore_image_size}" | bc -l )  )); then
    echo -ne "\n\n"
    echo -ne "${red}############################################################################${nc} \n"
    echo -ne " --> ${red}ERROR${nc} : The disk size is less than the image to restore \n"
    echo -ne " -- disk size             : [${disk_size}GB] \n"
    echo -ne " -- image to restore size : [${restore_image_size}GB] \n"
    echo -ne " --> please try with a hard drive equal or greater than : [${restore_image_size}GB] \n"
    echo -ne "${red}############################################################################${nc} \n\n\n"
    echo "restore_image=FAIL" >> ${_ENV_FILE}
    sleep 5; exit 1
fi


# Retrieve system's partition number
partition=`cat ${PARTIMAG}/${default_image}/parts | awk -F ' ' '{print $NF}' | grep -o [0-9]`

# Restore and resize disk
if [ ! -z "${default_image}" ] && [ ! -z "${default_disk}" ]
then
    echo "## Restore default image"
    ${TOOLS_DIR}/restore-disk "$default_image" "$default_disk" # || exit 1

    echo "restore_image=DONE" >> ${_ENV_FILE}
    #echo "## Resize partition"
    #${TOOLS_DIR}/resize-disk "/dev/${default_disk}" "$partition" "50GB" || exit 1
fi

#==============================================================================#
#        FINALIZATION                                                          #
#==============================================================================#

echo -e " ============================"
echo -e " ========== ${cyan}FINISH${nc} =========="
echo -ne " ============================ \n\n"
exit 0
