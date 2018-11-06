#!/bin/bash

	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	

	##############################################################
	# Load functions                                             #
	##############################################################
	source ${_THISPATH}/functions.sh
	source /root/custom/config.cfg

	##############################################################
	# Local variables                                            #
	##############################################################
	export _KERNEL_OUTPUT="/home/custom/kernel/packages"
	export _GFX_STACK_OUTPUT="/home/custom/graphic_stack/packages"
	export _RSYSLOG="/root/custom/packages/system_logs/rsyslog"
	export _DATA=`cat /root/custom/DATA`
	export TERM=xterm

	if [ ! -z "${kernel_commit}" ]; then
		timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Installing kernel '${kernel_branch}' commit '${kernel_commit}' ..." >> '${_DATA}'/clonezilla'
		start_spinner ">>> (info) Installing kernel ${kernel_branch} commit-${kernel_commit} ..."
			dpkg -i ${_KERNEL_OUTPUT}/*.deb &> /dev/null
			sleep .5
		stop_spinner $?

		verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"
	fi

	if [ ! -z "${gfx_stack_code}" ]; then
		timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Installing Gfx stack ['${gfx_stack_code}'] ..." >> '${_DATA}'/clonezilla'
		start_spinner ">>> (info) Installing Gfx stack [${gfx_stack_code}] ..."
			dpkg -i --force-overwrite ${_GFX_STACK_OUTPUT}/*.deb &> /dev/null
		stop_spinner $?

		verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"
	fi

    # this part check if the graphic stack package contains xorg-xserver
    # in order to configure it.
    if grep -q xserver "${_GFX_STACK_OUTPUT}/easy-bugs"; then

		timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Configuring (xserver-xorg)" >> '${_DATA}'/clonezilla'

        if [ ! -f "/usr/bin/Xorg" ]; then
            timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (warn) (/usr/bin/Xorg) does not exists, copying it ..." >> '${_DATA}'/clonezilla'
            start_spinner ">>> (warn) (/usr/bin/Xorg) does not exists, copying it ..."
                sleep .75
                cp "${_GFX_STACK_OUTPUT}/Xorg" "/usr/bin"
            stop_spinner $?
            verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"
        else
            timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) (/usr/bin/Xorg) exists" >> '${_DATA}'/clonezilla'
        fi

        if [ ! -f "/etc/X11/xorg.conf" ]; then
            timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (warn) (/etc/X11/xorg.conf) does not exists, copying it ..." >> '${_DATA}'/clonezilla'
            start_spinner ">>> (warn) (/etc/X11/xorg.conf) does not exists, copying it ..."
                sleep .75
                cp "${_GFX_STACK_OUTPUT}/xorg.conf" "/etc/X11"
            stop_spinner $?
            verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"
        else
            timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) (/etc/X11/xorg.conf) exists" >> '${_DATA}'/clonezilla'
        fi


        timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) chown root.root /usr/bin/Xorg ..." >> '${_DATA}'/clonezilla'
        start_spinner ">>> (info) chown root.root /usr/bin/Xorg ..."
            sleep .75
            chown root.root /usr/bin/Xorg
        stop_spinner $?
        verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"

        timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) chmod 755 /usr/bin/Xorg ..." >> '${_DATA}'/clonezilla'
        start_spinner ">>> (info) chmod 755 /usr/bin/Xorg ..."
            sleep .75
            chmod 755 /usr/bin/Xorg
        stop_spinner $?
        verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"

        timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) chown root.root /etc/X11/xorg.conf ..." >> '${_DATA}'/clonezilla'
        start_spinner ">>> (info) chown root.root /etc/X11/xorg.conf ..."
            sleep .75
            chown root.root /etc/X11/xorg.conf
        stop_spinner $?
        verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"

        timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) chmod 755 /etc/X11/xorg.conf ..." >> '${_DATA}'/clonezilla'
        start_spinner ">>> (info) chmod 755 /etc/X11/xorg.conf ..."
            sleep .75
            chmod 755 /etc/X11/xorg.conf
        stop_spinner $?
        verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"

    else
        timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) this graphic stack does not contains (xserver-xorg)" >> '${_DATA}'/clonezilla'
    fi

	#start_spinner "--> Updating kernel..."
	#	update-initramfs -c -k ${_KERNEL_VERSION} &> /dev/null
	#	sleep .5
	#stop_spinner $?

    if [ ! -z "${grub_parameters}" ]; then
    	timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Updating grub parameters ..." >> '${_DATA}'/clonezilla'
        start_spinner ">>> (info) Updating grub parameters ..."
        	sleep .5
            _GRUB_CMD_LINE=`cat -n /etc/default/grub  | grep "GRUB_CMDLINE_LINUX_DEFAULT" | awk '{print $1}'`
            sed -i ''${_GRUB_CMD_LINE}'s|^.*$|GRUB_CMDLINE_LINUX_DEFAULT="quiet '"${grub_parameters}"'"|g' /etc/default/grub
        stop_spinner $?

        verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"
    else
    	timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Removing splash screen from grub ..." >> '${_DATA}'/clonezilla'
        start_spinner ">>> (info) Removing splash screen from grub ..."
        	sleep .5
            _GRUB_CMD_LINE=`cat -n /etc/default/grub  | grep "GRUB_CMDLINE_LINUX_DEFAULT" | awk '{print $1}'`
            sed -i ''${_GRUB_CMD_LINE}'s/^.*$/GRUB_CMDLINE_LINUX_DEFAULT="quiet"/g' /etc/default/grub
        stop_spinner $?

		verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"
    fi

    if [ ! -z "${kernel_commit}" ]; then
		export _KERNEL_VERSION=`ls /boot/ | grep vmlinuz | grep ${kernel_commit} | sed 's/vmlinuz-//g'`

		timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Updating grub with '${kernel_branch}' commit-'${kernel_commit}' ..." >> '${_DATA}'/clonezilla'
		start_spinner ">>> (info) Updating grub with ${kernel_branch} commit-${kernel_commit} ..."
			sleep .5
			_GRUB_LINE_DEFAULT=`cat -n /etc/default/grub  | grep "GRUB_DEFAULT" | awk '{print $1}'`
			sed -i ''${_GRUB_LINE_DEFAULT}'s/^.*$/GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux '${_KERNEL_VERSION}'"/g' /etc/default/grub
			update-grub &> /dev/null
		stop_spinner $?

		verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"
	fi

	if [ "${graphical_environment}" = "off" ]; then

		timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Disabling graphical interface ..." >> '${_DATA}'/clonezilla'
		start_spinner ">>> (info) Disabling graphical interface ..."
			# mx commands
			sleep .5
			systemctl enable multi-user.target --force &> /dev/null
			systemctl set-default multi-user.target &> /dev/null
		stop_spinner $?

		verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"
	fi

		# FR commands
		# systemctl set-default multi-user.target --force &> /dev/null
		# systemctl disable lightdm.service --force &> /dev/null
		# systemctl disable graphical.target --force &> /dev/null
		# systemctl disable plymouth.service --force &> /dev/null


	timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Setting TTYs autologin ..." >> '${_DATA}'/clonezilla'
	start_spinner ">>> (info) Setting TTYs autologin ..."
	    export _PATH_TTY=/etc/systemd/system/getty.target.wants
	    export _FILE_TTY=getty@tty1.service
	    export _LINE_TTY=`cat -n ${_PATH_TTY}/${_FILE_TTY} | grep -w "ExecStart" | awk '{print $1}'`
	    export _CURRENT_PARAMETER=`cat ${_PATH_TTY}/${_FILE_TTY} | grep -w "^ExecStart"`
		sleep .5
		# Doing a backup for getty@.service
		cp /lib/systemd/system/getty@.service /home/${dut_user}/getty@.service &> /dev/null
		sed -i ''${_LINE_TTY}'s|^.*$|ExecStart=-/sbin/agetty --autologin '${dut_user}' --noclear %I $TERM|g' /lib/systemd/system/getty@.service &> /dev/null
		touch /home/${dut_user}/._tty_done
	stop_spinner $?

	verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"

	timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Updating systemctl ..." >> '${_DATA}'/clonezilla'
	start_spinner ">>> (info) Updating systemctl ..."
		sleep .5; systemctl enable getty@tty1.service &> /dev/null
	stop_spinner $?

	verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"


	timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Setting rsyslog ..." >> '${_DATA}'/clonezilla'
	start_spinner ">>> (info) Setting rsyslog ..."
        sleep .75
        cp ${_RSYSLOG} /etc/logrotate.d/
	stop_spinner $?

	verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"