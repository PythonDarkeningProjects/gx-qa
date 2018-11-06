#!/bin/bash

# Note : in bifrost to keep up-to-date the kernels i used this cronjob
# 30 */1 * * * bash /home/gfx/.updates/nightly.sh  &> /tmp/rsync_nightly.log
# to umount something with sshf is the same thing as when we mount manually : # umount <folder>

	##############################################################
	# Global variables                                           #
	##############################################################
	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	export _FUNCTIONS_SCRIPT="${_THISPATH}/functions.sh"
	export _CONFIG_FILE="$1"
	export _ENV_FILE="/root/custom/env.vars"
	export _DATA=`cat /root/custom/DATA`
	export TERM=xterm

	##############################################################
	# Load functions                                             #
	##############################################################
	source ${_FUNCTIONS_SCRIPT}
	source ${_CONFIG_FILE}

	function verify () {
		STATE="$1"
		unset STATUS
		if [ "${STATE}" = "0" ]; then STATUS=DONE; else STATUS=FAIL; fi
		timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) '${STATUS}'" >> '${_DATA}'/clonezilla'
	}

	##############################################################
	# Local variables                                            #
	##############################################################
	_BRANCH_PATH="/home/shared/kernels_mx"
	_KERNEL_INPUT="/home/${kernel_branch}"
	_SSH_PARAMS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=quiet"
	_KERNEL_OUTPUT="/mnt/home/custom/kernel/packages/"

	mkdir -p ${_KERNEL_INPUT} ${_KERNEL_OUTPUT} &> /dev/null

	timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Mounting '${kernel_branch}' from bifrost.intel.com ...   " >> '${_DATA}'/clonezilla'
	start_spinner ">>> (info) Mounting ${kernel_branch} from bifrost.intel.com"
		sleep .5; cd ${_KERNEL_INPUT} && sshfs ${_SSH_PARAMS} -o noatime "${server_user}@${server_hostname}:${_BRANCH_PATH}/${kernel_branch}" .
	stop_spinner $?

	verify "${_STATUS}"


	if [ "${_STATUS}" = 0 ]; then

		case "${kernel_branch}" in

		mainline)

            _CHECK_KERNEL_VERSION=`find ${_KERNEL_INPUT} -maxdepth 100 -type d -name "*${kernel_commit}*"`

			if [ ! -z "${_CHECK_KERNEL_VERSION}" ]; then

				timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Copying kernel debian packages to the system ...   " >> '${_DATA}'/clonezilla'
				start_spinner ">>> (info) Copying kernel debian packages to the system ..."
					sleep .75
					mkdir -p ${_KERNEL_OUTPUT}
					cp -R ${_CHECK_KERNEL_VERSION}/deb_packages/*.deb ${_KERNEL_OUTPUT}
					cp ${_CHECK_KERNEL_VERSION}/README ${_KERNEL_OUTPUT}/commit_info
				stop_spinner $?

				if [ "${_STATUS}" = 0 ]; then
					echo "kernel_status=DONE" >> ${_ENV_FILE}
				else
					echo "kernel_status=FAIL" >> ${_ENV_FILE}
				fi

				verify "${_STATUS}"

			else
				echo -e ">>> (err) ${red}Kernel version not found${nc} [${kernel_commit}]"
				timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (warn) Kernel version not found ['${kernel_commit}']" >> '${_DATA}'/clonezilla'
				timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (err) could not completed the setup due to kernel version" >> '${_DATA}'/clonezilla'
				echo "kernel_status=FAIL" >> ${_ENV_FILE}
				exit 1
			fi

		;;


		*)
			_LENGTH=${#kernel_commit}
			# Checking if a kernel needs to be added to gfx-stack
			if [ ! -z "${kernel_commit}" ] && [ "${_LENGTH}" -gt 5 ]; then

				_CHECK_COMMIT=`find ${_KERNEL_INPUT} -maxdepth 100 -type d -name "*${kernel_commit}*"`

				if [ ! -z "${_CHECK_COMMIT}" ]; then
					start_spinner ">>> (info) Copying kernel packages to DUT ..."
						sleep .75
						mkdir -p ${_KERNEL_OUTPUT}
						cp -R ${_CHECK_COMMIT}/deb_packages/*.deb ${_KERNEL_OUTPUT}
						cp ${_CHECK_COMMIT}/commit_info ${_KERNEL_OUTPUT}
					stop_spinner $?

						if [ "${_STATUS}" = 0 ]; then
							echo "kernel_status=DONE" >> ${_ENV_FILE}
						else
							echo "kernel_status=FAIL" >> ${_ENV_FILE}
						fi
				else
					echo -e ">>> (err) ${red}kernel commit not found${nc} [${kernel_commit}]"
					timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (warn) kernel commmit not found [${kernel_commit}]" >> '${_DATA}'/clonezilla'
					timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (err) could not completed the setup due to kernel commit" >> '${_DATA}'/clonezilla'
					echo "kernel_status=FAIL" >> ${_ENV_FILE}
					exit 1
				fi
			fi

		;;

		esac

	fi

