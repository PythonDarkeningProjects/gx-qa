#!/bin/bash

# How to fix swap partition
# http://linux.goeszen.com/activating-swap-failed-on-debian-squeeze.html
# looks like something corrupted my swap. Or the swap might not be formatted. Thus, I created/formatted it anew with:
# mkswap /dev/sda5
# which gave the device a new UUID. After adding the new UUID to /etc/fstab the swapon command worked and swap was there. Looking at the boot sequence is a todo.
# All this might have resulted from a strange hiccup before I possibly never will find out about.
# swapoff /dev/sdaX
# swapon /dev/sdaX

    ##############################################################
    # Global variables                                           #
    ##############################################################
    export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
    export _FUNCTIONS_SCRIPT="${_THISPATH}/functions.sh"
    export _FLAG=0
    export _PACKAGES_SCRIPT="/root/custom/packages/igt/07_2_update-grub.sh"
    export disk_label=`lsblk | grep sda | head -1 | awk '{print $1}'`
    export TERM=xterm

    ##############################################################
    # Load functions                                             #
    ##############################################################
    source ${_FUNCTIONS_SCRIPT}
    source /root/custom/config.cfg


        CHECK_FOR_SSD=$(fdisk -l 2> /dev/null | grep -v "Disk /dev/ram*" | grep "^/dev" | grep -ve "/dev/sd*" -ve "/dev/mmc*")

        if [ ! -z "${CHECK_FOR_SSD}" ]; then
            # this mean that the DUT does not has SSD, maybe has a eMMC or other kind of hard drive
           export _SWAP_PARTITION=$(fdisk -l | grep ^/dev | grep -v sda | grep swap | awk '{print $1}')
        else
            # this mean that the DUT has SSD
            export _SWAP_PARTITION=`cat /etc/fstab | grep -i "swap was on" | sed 's/# swap was on //g' | awk '{print $1}'`

            start_spinner ">>> (info) Unmounting swap partition ..."
                swapoff ${_SWAP_PARTITION} &> /dev/null; sleep .2
            stop_spinner $?
        fi

        start_spinner ">>> (info) Creating a new UUID for swap partition ..."
          sleep .2; mkswap ${_SWAP_PARTITION} 2> /dev/null > /tmp/swap.log
          export _NEW_UUID=`cat /tmp/swap.log | grep UUID | sed -e 's/no label, //g' -e s'/UUID=//'g`
        stop_spinner $?

        # if we do this part in the wrong way we'll have issues with hibernate(s4)
        start_spinner ">>> (info) Adding the new UUID to fstab ..."
            sleep .2
            export _SWAP_LINE=`cat -n /etc/fstab | grep "swap was on" | awk '{print $1}'`
            ((_SWAP_LINE++))
            _OLD_UUID=`cat -n /etc/fstab | grep ${_SWAP_LINE} | grep swap | awk '{print $2}'`
            sed -i ''${_SWAP_LINE}'s/'${_OLD_UUID}'/UUID='${_NEW_UUID}'/g' /etc/fstab
        stop_spinner $?

        start_spinner ">>> (info) Mounting swap partition on [${_SWAP_PARTITION}] ..."
            sleep .2
            swapon ${_SWAP_PARTITION}
        stop_spinner $?

        start_spinner ">>> (info) adding resume partition in grub ..."
            sleep .2
            # this as workaruoud otherwise resume will not works
            # reference : https://help.ubuntu.com/community/PowerManagement/Hibernate
            export _GRUB_CMD_LINE=`cat -n /etc/default/grub  | grep "GRUB_CMDLINE_LINUX_DEFAULT" | awk '{print $1}'`
            export _OLD_PARAMETERS=`cat -n /etc/default/grub  | grep "GRUB_CMDLINE_LINUX_DEFAULT" | awk -F"GRUB_CMDLINE_LINUX_DEFAULT=" '{print $2}' | sed 's/"//g'`
            sed -i ''${_GRUB_CMD_LINE}'s|^.*$|GRUB_CMDLINE_LINUX_DEFAULT="'"${_OLD_PARAMETERS}"' resume='${_SWAP_PARTITION}'"|g' /etc/default/grub
        stop_spinner $?

    #fi


    # ====================================================================================================================
    # changing fstab errors=remount-ro to defaults in order to avoid system unsable (read-only) after some igt tests
    # defaults = rw, suid, dev, exec, auto, nouser, and async
    start_spinner ">>> (info) adding defaults option to fstab ..."
        sleep .75; EXT4_LINE=`cat -n /etc/fstab | grep ext4 | awk '{print $1}'`; sed -i ''${EXT4_LINE}'s/errors=remount-ro/defaults/g' /etc/fstab
    stop_spinner $?

    # adding fastboot to grub in order to skip fsck when the DUT reboot (it helps if the system became in unsable and in this way can access it)
    # Reference : https://www.cyberciti.biz/faq/linux-unix-bypassing-fsck/

    start_spinner ">>> (info) adding fastboot parameter in grub ..."
        sleep .2
        export _GRUB_CMD_LINE=`cat -n /etc/default/grub  | grep "GRUB_CMDLINE_LINUX_DEFAULT" | awk '{print $1}'`
        export _OLD_PARAMETERS=`cat -n /etc/default/grub  | grep "GRUB_CMDLINE_LINUX_DEFAULT" | awk -F"GRUB_CMDLINE_LINUX_DEFAULT=" '{print $2}' | sed 's/"//g'`
        sed -i ''${_GRUB_CMD_LINE}'s|^.*$|GRUB_CMDLINE_LINUX_DEFAULT="'"${_OLD_PARAMETERS}"' fastboot"|g' /etc/default/grub
    stop_spinner $?

    start_spinner ">>> (info) Updating grub ..."
        sleep .2
        update-grub &> /dev/null
    stop_spinner $?

    start_spinner ">>> (info) Disabling the printing of messages to the console ..."
        sleep .75; dmesg -D
    stop_spinner $?

    start_spinner ">>> (info) Decreasing raise network interfaces at the beginning to 15 sec ..."
        timeoutLine=`cat -n /etc/systemd/system/network-online.target.wants/networking.service | grep "TimeoutStartSec" | awk '{print $1}'`
        sed -i ''${timeoutLine}'s|^.*$|TimeoutStartSec=15sec|g' /etc/systemd/system/network-online.target.wants/networking.service
    stop_spinner $?

    start_spinner ">>> (info) Restarting the network daemon for apply the changes ..."
        sleep .75; sudo systemctl daemon-reload
    stop_spinner $?

    # ====================================================================================================================

    # Adding DUT information to issue.net
    UbuntuVersion=`cat /etc/*-release | grep -w "PRETTY_NAME" | awk -F"PRETTY_NAME=" '{print $2}' | sed 's/"//g'`
    MemoryRam=`dmidecode –t 17 | grep "Range Size" | head -n 1 | awk -F": " '{print $2}'`
    Cpu=`cat /proc/cpuinfo | grep "model name" | head -n 1 | awk -F": " '{print $2}'`
    CPuCores=`cat /proc/cpuinfo | grep processor | wc -l`
    GpuCard=`lspci -v -s $(lspci |grep "VGA compatible controller" |cut -d" " -f 1) | grep "VGA compatible controller" | awk -F": " '{print $2}'`
    DiskCapacity=`lshw | grep -A 20 "*-scsi" | grep -A 10 "*-disk" | grep "size:" | sed 's/ *size: //g' | head -1` # careful if there is more than 1 disk connect to the system
    if [ `getconf LONG_BIT` = "64" ]; then arch="64-bit"; else arch="32-bit"; fi

    sed -i '3s|^.*$|Distro        : '"${UbuntuVersion}"'|g' /etc/ssh/issue.net
    sed -i '4s|^.*$|Memory        : '"${MemoryRam}"'|g' /etc/ssh/issue.net
    sed -i '5s|^.*$|Processor     : '"${Cpu}"'|g' /etc/ssh/issue.net
    sed -i '6s|^.*$|Graphic card  : '"${GpuCard}"'|g' /etc/ssh/issue.net
    sed -i '7s|^.*$|OS-Type       : '"${arch}"'|g' /etc/ssh/issue.net
    sed -i '8s|^.*$|Disk          : '"${DiskCapacity}"'|g' /etc/ssh/issue.net
    sed -i '9s|^.*$|Hostname      : '"${dut_hostname}"'|g' /etc/ssh/issue.net