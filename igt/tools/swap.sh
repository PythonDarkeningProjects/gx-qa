#!/bin/bash

# How to fix swap partition
# http://linux.goeszen.com/activating-swap-failed-on-debian-squeeze.html
# looks like something corrupted my swap. Or the swap might not be formatted. Thus, I created/formatted it anew with:
# mkswap /dev/sda5
# which gave the device a new UUID. After adding the new UUID to /etc/fstab the swapon command worked and swap was there. Looking at the boot sequence is a todo.
# All this might have resulted from a strange hiccup before I possibly never will find out about.
# swapoff /dev/sdaX
# swapon /dev/sdaX

	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR THE CURRENT LINUX MACHINE -->>
	export CUSER=`whoami`
	export PASSWORD=linux
	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR THE CURRENT LINUX MACHINE -->>

    export _THISPATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd ) # <- current script path, even if i call from tux ;)
    export _COUNT=0

    source ${_THISPATH}/functions.sh
    clear
    echo -ne "\n\n"

    start_spinner " --> Checking if swap partition was enabled in the kernel during boot process ..."
    	echo ${PASSWORD} | sudo -S ls &> /dev/null; sleep .5
    	_swap_on_kernel=`echo ${PASSWORD} | sudo -S journalctl -b | grep swap | grep "Activated swap"`
    stop_spinner $?

    echo -ne "\n\n"

    disk_id=`systemctl -l | grep swap | grep dev-disk | awk '{print $1}'`
    check=`systemctl status ${disk_id} | grep Active | awk '{print $2}'`

    if [ "${check}" = "active" ]; then
    	echo -ne " ${green}●${nc}  swap partition status     : Active \n"
        ((_COUNT++))
    else
    	echo -ne " ${red}●${nc}  swap partition status       : Inactive \n"
    fi


    _check_swap_on_kernel=`echo $_swap_on_kernel | grep "Activated swap"`

    if [ ! -z "${_check_swap_on_kernel}" ]; then
    	echo -ne " ${green}●${nc}  swap loaded in the kernel : Yes \n"
        ((_COUNT++))
    else
    	echo -ne " ${red}●${nc}  swap loaded in the kernel   : No \n"
    fi

    # this two variables must be exactly the same
    UUID_FSTAB=`cat /etc/fstab | grep swap | grep UUID | awk '{print $1}' | sed 's/UUID=//g'`
    UUID_BLKID=`sudo blkid | grep swap | awk '{print $2}' | sed -e 's/UUID=//g' -e 's/"//g'`

    if [ "$UUID_FSTAB" != "$UUID_BLKID" ]; then 
    	echo -ne " ${red}●${nc}  FSTAB_UUID & blkidD        : doesn't match \n"
    	cat ${_THISPATH}/swap_fix; echo -ne "\n\n"; exit 1
    else 
    	echo -ne " ${green}●${nc}  FSTAB_UUID & BLKID        : match \n"
        ((_COUNT++))
    fi

    if [ "${_COUNT}" = "3" ]; then touch /home/${CUSER}/.swap_ready; fi


    echo -ne "\n\n"