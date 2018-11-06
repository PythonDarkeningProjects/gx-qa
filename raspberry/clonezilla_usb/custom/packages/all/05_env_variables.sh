#!/usr/bin/env bash

	##############################################################
	# Global variables                                           #
	##############################################################
	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	export _FUNCTIONS_SCRIPT="${_THISPATH}/functions.sh"
	export _CONFIG_FILE="$1"
	export _DATA="$2"
	export _YAML_CONFIG_FILE="$3"
	export _NETWORK_FOLDER="/root/custom/packages/all/network"
	export _IP=$(hostname -I)
	export _INTERFACE=$(ip link show | grep -E "^[0-9]: " | awk -F ": " '{print $2}' | grep -v "lo" | tail -1)
	export _ENV_FILE="/root/custom/env.vars"
	export TYPE_MOTHERBOARD_A=`dmidecode -t 2 | grep "Product Name" | awk -F": " '{print $2}' | sed 's/ //g'`
	export _SERVER_HOSTNAME="10.219.106.111"
	export _SERVER_USER="root"

	##############################################################
	# Load functions                                             #
	##############################################################
	source ${_FUNCTIONS_SCRIPT}
	source ${_CONFIG_FILE}


	##############################################################
	# Local variables                                            #
	##############################################################
	export _CURRENT_HOSTNAME=`cat /mnt/etc/hostname`
	export _NEW_HOSTNAME="${dut_hostname}"
	export _NEW_STATIC_IP="${dut_static_ip}"
	export _GFX_QA_TOOLS_IN_BIFROST="/home/shared/gitlist/gfx-qa-tools"
	export TERM=xterm

	function verify () {
		STATE="$1"
		unset STATUS
		if [ "${STATE}" = "0" ]; then STATUS=DONE; else STATUS=FAIL; fi
		server_message INFO "${STATUS}"
	}

	if [ ! -z "${dut_hostname}" ]; then
		server_message INFO "setting system hostname"
		start_spinner " - (info) - setting system hostname ..."
			sleep .5
			_LINE=`cat -n /mnt/etc/hosts | grep "${_CURRENT_HOSTNAME}" | awk '{print $1}'`

		   case "${TYPE_MOTHERBOARD_A}" in
		        "BRASWELL")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-BRASWELL/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-BRASWELL/g' /mnt/etc/hostname
				;;
		        "LenovoG50-80")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-LenovoG50-80/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-LenovoG50-80/g' /mnt/etc/hostname
				;;
				"NUC5i7RYB")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-NUC5i7RYB/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-NUC5i7RYB/g' /mnt/etc/hostname
				;;
				"NUC5i5MYBE")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-NUC5i5MYBE/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-NUC5i5MYBE/g' /mnt/etc/hostname
				;;
		        "NUC5i5RYB")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-NUC5i5RYB/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-NUC5i5RYB/g' /mnt/etc/hostname
				;;
		        "06D7TR")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-06D7TR/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-06D7TR/g' /mnt/etc/hostname
				;;
		        "0XR1GT")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-0XR1GT/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-0XR1GT/g' /mnt/etc/hostname
				;;
		        "02HK88")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-02HK88/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-02HK88/g' /mnt/etc/hostname
				;;
		        "NOTEBOOK")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-NOTEBOOK/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-NOTEBOOK/g' /mnt/etc/hostname
				;;
		        "SkylakeYLPDDR3RVP3")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-SkylakeYLPDDR3RVP3/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-SkylakeYLPDDR3RVP3/g' /mnt/etc/hostname
				;;
		        "SkylakeUDDR3LRVP7")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-SkylakeUDDR3LRVP7/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-SkylakeUDDR3LRVP7/g' /mnt/etc/hostname
				;;
		        "PortablePC")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-PortablePC/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-PortablePC/g' /mnt/etc/hostname
				;;
		        "D54250WYK")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-D54250WYK/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-D54250WYK/g' /mnt/etc/hostname
				;;
		        "NUC6i5SYB")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-NUC6i5SYB/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-NUC6i5SYB/g' /mnt/etc/hostname
				;;
		        #"NUC5i5RYB") export MODEL="BDW-Nuc" ;;
		        "NUC6i7KYB")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-NUC6i7KYB/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-NUC6i7KYB/g' /mnt/etc/hostname
				;;

				"MS-B1421")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-MS-B1421/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-MS-B1421/g' /mnt/etc/hostname
				;;

				"GLKRVP1DDR4(05)")
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'-GLKRVP1DDR4(05)/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'-GLKRVP1DDR4(05)/g' /mnt/etc/hostname
				;;

				*)
					sed -i ''${_LINE}'s/^.*$/127.0.1.1	'${_NEW_HOSTNAME}'/g' /mnt/etc/hosts
					sed -i 's/'${_CURRENT_HOSTNAME}'/'${_NEW_HOSTNAME}'/g' /mnt/etc/hostname
				;;
	    	esac

		stop_spinner $?

		verify "${_STATUS}"
	fi

	if [ ! -z "${dut_static_ip}" ]; then
		server_message INFO "setting DUT static IP"
		start_spinner "- (info) - setting DUT static IP ..."
			sleep .5
			_VLAN=`echo ${_IP} | awk -F"." '{print $3}'`
			# Creating a backup for interfaces file
			mv /mnt/etc/network/interfaces /mnt/etc/network/interfaces.bkp
			# the vlans for linuxgraphics are 128,114,106 (the 114 is the good one for lab)
			cp ${_NETWORK_FOLDER}/interfaces_vlan_${_VLAN} /mnt/etc/network/interfaces
			sed -i '3s/^.*$/allow-hotplug '${_INTERFACE}'/g' /mnt/etc/network/interfaces
			sed -i '4s/^.*$/iface '${_INTERFACE}' inet static/g' /mnt/etc/network/interfaces
			sed -i '5s/^.*$/address '${_NEW_STATIC_IP}'/g' /mnt/etc/network/interfaces

		stop_spinner $?

		verify "${_STATUS}"
	fi

	server_message INFO "updating gfx-qa-tools repository from bifrost.intel.com"
	start_spinner ">>> (info) Updating gfx-qa-tools repository from bifrost.intel.com ..."
		sleep .5; rm -rf /mnt/home/${dut_user}/gfx-qa-tools &> /dev/null
		scp -r -o "StrictHostKeyChecking no" ${server_user}@${server_hostname}:${_GFX_QA_TOOLS_IN_BIFROST} /mnt/home/${dut_user}/ &> /dev/null
		# Setting vim config file
		rm -rf /mnt/home/${dut_user}/.vimrc &> /dev/null; cp /mnt/home/${dut_user}/gfx-qa-tools/tests/tools/vimrc /mnt/home/${dut_user}/.vimrc
		chown -R user.user /mnt/home/${dut_user}/
		chown -R user.user /mnt/home/custom/
	stop_spinner $?

	verify "${_STATUS}"

	server_message INFO "copying config.cfg to the DUT"
	start_spinner "- (info) - copying config.cfg to DUT ..."
		sleep .5; cp ${_CONFIG_FILE} /mnt/home/custom/
		chown -R user.user /mnt/home/custom/
	stop_spinner $?

	verify "${_STATUS}"

	server_message INFO "copying config.yml to the DUT"
	start_spinner "- (info) - copying config.yml to DUT ..."
		sleep .5; cp ${_YAML_CONFIG_FILE} /mnt/home/custom/
		chown -R user.user /mnt/home/custom/
	stop_spinner $?

	verify "${_STATUS}"


	server_message INFO "copying hardware specs to DUT"
	start_spinner "- (info) - copying hardware specs to DUT ..."

	   case "${TYPE_MOTHERBOARD_A}" in
	        "BRASWELL") export MODEL="BSW" ;;
	        "LenovoG50-80"|"NUC5i7RYB"| "NUC5i5MYBE"|"NUC5i5RYB") export MODEL="BDW" ;;
	        "06D7TR") export MODEL="SNB" ;;
	        "0XR1GT") export MODEL="IVB" ;;
	        "02HK88") export MODEL="SKL" ;;
	        "NOTEBOOK") export MODEL="BXT-P" ;;
	        "SkylakeYLPDDR3RVP3") export MODEL="SKL-Y to KBL (RVP3)" ;;
	        "SkylakeUDDR3LRVP7") export MODEL="KBL (RVP7)" ;;
	        "PortablePC") export MODEL="BYT-M (Toshiba)" ;;
	        "1589") export MODEL="HP Z420 Workstation" ;;
	        "D54250WYK") export MODEL="HSW-Nuc" ;;
	        "NUC6i5SYB") export MODEL="SKL-Nuc" ;;
	        #"NUC5i5RYB") export MODEL="BDW-Nuc" ;;
	        "NUC6i7KYB") export MODEL="SKL Canyon" ;;
			"MS-B1421") export MODEL="KBL-Nuc" ;;
			"GLKRVP1DDR4(05)") export MODEL="GLK"
    	esac

    	hardware_specs "${TYPE_MOTHERBOARD_A}"

		chown -R user.user /mnt/home/custom/
	stop_spinner $?

	verify "${_STATUS}"

	server_message INFO "setting sudoers file"
	start_spinner "- (info) - setting sudoers file ..."
		sleep .5
		# no ask for password to the user
		echo "${dut_user} ALL=(ALL) NOPASSWD: ALL" >> /mnt/etc/sudoers
	stop_spinner $?

	verify "${_STATUS}"

	server_message INFO "setting hwclock for rtcwake"
	start_spinner "- (info) - setting hwclock for rtcwake ..."
		sleep .5
		hwclock -w
	stop_spinner $?

	verify "${_STATUS}"

	_PARTITION_DISK=`parted -s /dev/sda unit GB print free | grep "ext4" | awk '{print $1}'`
	# tune2fs reference : http://manpages.ubuntu.com/manpages/xenial/en/man8/tune2fs.8.html

	server_message INFO "setting tune2fs (disable filesystem check on boot)"
	start_spinner "- (info) - Setting tune2fs (disable filesystem check on boot) ..."
		sleep .5
		# The following parameters should only be used in a test environment where you may be carrying out multiple reboots during the course of the day. The Mount Count and check interval values below are set to "-1" which disables any checking!
		tune2fs -i -2m /dev/sda${_PARTITION_DISK} &> /dev/null
		tune2fs -c -1 /dev/sda${_PARTITION_DISK} &> /dev/null
	stop_spinner $?

	verify "${_STATUS}"

	server_message INFO "setting tune2fs (change the behavior of the kernel code when errors are detected)"
	start_spinner "- (info) - setting tune2fs (change the behavior of the kernel code when errors are detected) ..."
		sleep .25
		# change the behavior of the kernel code when errors are detected.
		tune2fs -e continue /dev/sda${_PARTITION_DISK} &> /dev/null
	stop_spinner $?

	verify "${_STATUS}"

	CURRENT_ERROR_BEHAVIOUR=`tune2fs -l /dev/sda${_PARTITION_DISK} | grep "Errors behavior" | sed 's| ||g' | awk -F: '{print $2}'`
	server_message INFO "tune2fs current error behavior : ${CURRENT_ERROR_BEHAVIOUR}"

	server_message INFO "adding to ${dut_user} to tty group"
	start_spinner "- (info) - adding to ${dut_user} to tty group ..."
		sleep .25; usermod -a -G tty user
	stop_spinner $?

	verify "${_STATUS}"

	# Reference : https://help.ubuntu.com/community/AutoLogin
	if [ "${graphical_environment}" = "on" -a "${autologin}" = "yes" ]; then
		server_message INFO "enabling autologin on X"
		start_spinner "- (info) - enabling autologin on X ..."
			sleep .25; mkdir -p /mnt/etc/lightdm/lightdm.conf.d
            echo "[SeatDefaults]" > /mnt/etc/lightdm/lightdm.conf.d/50-myconfig.conf
            echo "autologin-user=${dut_user}" >> /mnt/etc/lightdm/lightdm.conf.d/50-myconfig.conf
		stop_spinner $?

		verify "${_STATUS}"
	fi

    # Setting PYTHONPATH environment variable
    server_message INFO "setting (PYTHONPATH) environment variable for gfx-qa-tools project"
    start_spinner "- (info) - setting (PYTHONPATH) environment variable for gfx-qa-tools project ..."
        sleep .25
        echo 'export PYTHONPATH="${PYTHONPATH}":/home/'${dut_user}'/gfx-qa-tools/' >> /mnt/root/.bashrc
        echo 'export PYTHONPATH="${PYTHONPATH}":/home/'${dut_user}'/gfx-qa-tools/' >> /mnt/home/${dut_user}/.bashrc
    stop_spinner $?

    # Setting resolved.conf (dns file)
    server_message INFO "setting resolved.conf (for dns) "
    start_spinner "- (info) - setting resolved.conf (for dns) ..."
        sleep .25
        cp /root/custom/packages/dns/resolved.conf /mnt/etc/systemd
    stop_spinner $?


	#echo "set_environment=DONE" >> ${_ENV_FILE}