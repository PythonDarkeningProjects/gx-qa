#!/bin/bash

	##############################################################
	# Local variables                                            #
	##############################################################
	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	export _PACKAGES_SCRIPT="/root/custom/packages/all/11_1_change_username_and_password.sh"
	export _ENV_FILE="/root/custom/env.vars"
	export _LOGS_FOLDER=$1
	export TERM=xterm

	##############################################################
	# Load functions                                             #
	##############################################################
	source ${_THISPATH}/functions.sh


	# Chroot into DUT's filesystem and run deployment script (to allow install deb packages)

	if [ ! -d "/mnt/root/custom" ]; then
		start_spinner ">>> (info) Copying custom folder to /mnt/root ..."
			sleep .75; cp -R /root/custom/ /mnt/root/
		stop_spinner $?
	fi

	echo ">>> (info) chroot /mnt /bin/bash"
	mount --bind /proc /mnt/proc
	mount --bind /sys /mnt/sys
	mount --bind /dev /mnt/dev
	chroot /mnt /bin/bash -c 'su - -c \"${_PACKAGES_SCRIPT}\"' # this is temporaly until the script is finish

	echo "crontab=DONE" >> ${_ENV_FILE}

