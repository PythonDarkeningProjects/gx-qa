#!/bin/bash

	##############################################################
	# Load functions                                             #
	##############################################################
	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	export _CONFIG_FILE="$1"
	export _FUNCTIONS_SCRIPT="${_THISPATH}/functions.sh"
	source ${_FUNCTIONS_SCRIPT}
	source ${_CONFIG_FILE}
	export _ENV_FILE="/root/custom/env.vars"

	##############################################################
	# Global variables                                           #
	##############################################################
	export _SSH_USER_PATH="/mnt/home/${dut_user}/.ssh"
	export _SSH_ROOT_PATH="/mnt/root/.ssh"
	export _KEYS_LIST_FOLDER="/root/custom/ssh"
	export _KEYS_LIST=`ls /root/custom/ssh/ | grep -v "ssh_tools"`
	export _SSH_TOOLS_PATH="/root/custom/ssh/ssh_tools"
	export _SSH_TOOLS_LIST=`ls /root/custom/ssh/ssh_tools/`
    export TERM=xterm

	mkdir -p ${_SSH_USER_PATH}
	mkdir -p ${_SSH_ROOT_PATH}

	for file in ${_KEYS_LIST}; do
		start_spinner ">>> (info) Setting [${file}] file for ${dut_user} ..."
			sleep .5; cp ${_KEYS_LIST_FOLDER}/${file} ${_SSH_USER_PATH}
		stop_spinner $?
	done

	for file in ${_KEYS_LIST}; do
		start_spinner ">>> (info) Setting [${file}] file for root ..."
			sleep .5; cp ${_KEYS_LIST_FOLDER}/${file} ${_SSH_ROOT_PATH}
		stop_spinner $?
	done

	# changing permission for id_rsa key to do not accessible by others and be able to connect to the server without password
	chmod 600 /mnt/root/.ssh/id_rsa
	chmod 600 /mnt/home/${dut_user}/.ssh/id_rsa

	# Setting ssh banners for logging in the system
	for file in ${_SSH_TOOLS_LIST}; do

		if [ "${file}" = "motd" ]; then 
			cp ${_SSH_TOOLS_PATH}/${file} /mnt/etc/
		else
			start_spinner ">>> (info) Copying [${file}] file in ssh system folder ..."
				sleep .5; cp ${_SSH_TOOLS_PATH}/${file} /mnt/etc/ssh/
			stop_spinner $?
		fi
	done

	touch /mnt/home/${dut_user}/.myssh.conf

	if [ "${_STATUS}" = 0 ]; then
		echo "ssh_keys=DONE" >> ${_ENV_FILE}
	else
		echo "ssh_keys=FAIL" >> ${_ENV_FILE}
	fi

	chown -R user.user ${_SSH_USER_PATH}