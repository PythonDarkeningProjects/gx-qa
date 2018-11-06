#!/bin/bash

	##############################################################
	# Local variables                                            #
	##############################################################
	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	export _SWAP_SCRIPT="/root/custom/packages/all/07_2_swap_partition.sh"
	export _ENV_FILE="/root/custom/env.vars"
	export TERM=xterm

	##############################################################
	# Load functions                                             #
	##############################################################
	source ${_THISPATH}/functions.sh

	echo ">>> (info) chroot /mnt /bin/bash"
	mount --bind /proc /mnt/proc
	mount --bind /sys /mnt/sys
	mount --bind /dev /mnt/dev
	chroot /mnt /bin/bash -c 'su - -c \"${_SWAP_SCRIPT}\"' # this is temporaly until the script is finish

	echo "swap_partition=DONE" >> ${_ENV_FILE}

