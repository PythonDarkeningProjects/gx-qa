#!/bin/bash

	##############################################################
	# Local variables                                            #
	##############################################################
	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	export _PACKAGES_SCRIPT="/root/custom/packages/all/10_2_firmwares_install.sh"
	export _ENV_FILE="/root/custom/env.vars"
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

	echo "--> chroot /mnt /bin/bash"
	mount --bind /proc /mnt/proc
	mount --bind /sys /mnt/sys
	mount --bind /dev /mnt/dev
	#chroot /mnt /bin/bash -c 'su - -c \"/root/custom/packages/igt/04_2_install_deb_packages.sh\"' # this is temporaly until the script is finish
	chroot /mnt /bin/bash -c 'su - -c \"${_PACKAGES_SCRIPT}\"' # this is temporaly until the script is finish


	echo "firmwares=DONE" >> ${_ENV_FILE}
