#!/bin/bash

	##############################################################
	# Global variables                                           #
	##############################################################
	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	export _FUNCTIONS_SCRIPT="${_THISPATH}/functions.sh"
	export _CONFIG_FILE="$1"
	export _ENV_FILE="/root/custom/env.vars"


	##############################################################
	# Load functions                                             #
	##############################################################
	source ${_FUNCTIONS_SCRIPT}
	source ${_CONFIG_FILE}


	##############################################################
	# Local variables                                            #
	##############################################################
	export _GFX_STACK_INPUT="/home/gfx_stack/"
	export _GFX_STACK_OUTPUT="/mnt/home/custom/graphic_stack/packages"
	export _GFX_STACK_PATH="/home/shared/gfx_stack/packages"
	export _SSH_PARAMS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=quiet"
	export _LOGS_FOLDER="/mnt/home/custom/clonezilla_logs"
    export TERM=xterm

	mkdir -p ${_GFX_STACK_INPUT}
	start_spinner ">>> (info) Mounting Gfx Stack from bifrost.intel.com"
		sleep .5
		cd ${_GFX_STACK_INPUT} && sshfs ${_SSH_PARAMS} -o noatime "${server_user}@${server_hostname}:${_GFX_STACK_PATH}/" .
	stop_spinner $?


	if [ "${_STATUS}" = 0 ] && [ ! -z "${gfx_stack_code}" ]; then

		export _CHECK_STACK=`find ${_GFX_STACK_INPUT} -maxdepth 100 -type f -name "*${gfx_stack_code}*"`
		export _PATH_TO_GFX_STACK=`find ${_GFX_STACK_INPUT} -maxdepth 100 -type f -name "*${gfx_stack_code}*" | awk 'BEGIN{FS=OFS="/"}{NF--; print}'`

		if [ ! -z "${_CHECK_STACK}" ]; then

			CHECK_FOR_IGT=`cat ${_PATH_TO_GFX_STACK}/easy-bugs | grep -w "intel-gpu-tools"`
			timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) default package is ('${default_package}')" >> '${_DATA}'/clonezilla'

			if [[ "${default_package}" == igt* ]] && [ -z "${CHECK_FOR_IGT}" ]; then
				timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (err) This Gfx stack ['${gfx_stack_code}'] does not contain intel-gpu-tools" >> '${_DATA}'/clonezilla'
				timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Please provide a Gfx stack with intel-gpu-tools" >> '${_DATA}'/clonezilla'
				echo -e ">>> (err) This Gfx stack [${gfx_stack_code}] does not contain intel-gpu-tools"
				echo -ne ">>> (info) Please provide a Gfx stack with intel-gpu-tools \n\n"
				echo "stack_status=FAIL" >> ${_ENV_FILE}
				exit 1

			elif [[ "${default_package}" == igt* ]] && [ ! -z "${CHECK_FOR_IGT}" ]; then

				start_spinner ">>> (info) Copying Gfx Stack to DUT ..."
					sleep .5; mkdir -p ${_GFX_STACK_OUTPUT}
					cp ${_CHECK_STACK} ${_GFX_STACK_OUTPUT}
					cp "${_PATH_TO_GFX_STACK}"/config.cfg "${_PATH_TO_GFX_STACK}"/easy-bugs ${_GFX_STACK_OUTPUT}
				stop_spinner $?

				if [ "${_STATUS}" = 0 ]; then
					echo "stack_status=DONE" >> ${_ENV_FILE}
				else
					echo "stack_status=FAIL" >> ${_ENV_FILE}
				fi

			elif [[ ! "${default_package}" == igt* ]]; then

				start_spinner ">>> (info) Copying Gfx Stack to DUT ..."
					sleep .5; mkdir -p ${_GFX_STACK_OUTPUT}
					cp ${_CHECK_STACK} ${_GFX_STACK_OUTPUT}
				stop_spinner $?

				if [ "${_STATUS}" = 0 ]; then
					echo "stack_status=DONE" >> ${_ENV_FILE}
				else
					echo "stack_status=FAIL" >> ${_ENV_FILE}
				fi

				list_of_configs=(config.cfg easy-bugs Xorg xorg.conf)

                for element in ${list_of_configs[*]}; do
                    if [ -f "${_PATH_TO_GFX_STACK}"/${element} ]; then
                        timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Copying ('${element}') to ('${_GFX_STACK_OUTPUT}') ..." >> '${_DATA}'/clonezilla'
                        start_spinner ">>> (info) Copying (${element}) to (${_GFX_STACK_OUTPUT}) ..."
                            sleep .75
                            cp "${_PATH_TO_GFX_STACK}/${element}" "${_GFX_STACK_OUTPUT}" | tee -a ${_LOGS_FOLDER}/03_download_gfx_stack.log
                        stop_spinner $?
                        verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"
                    fi
                done
			fi

		else
			echo -e ">>> (err) ${red}Gfx stack is not found${nc} [${gfx_stack_code}]"
			timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (err) Gfx stack not found [${gfx_stack_code}]" >> '${_DATA}'/clonezilla'
			timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) could not completed the setup due to gfx stack" >> '${_DATA}'/clonezilla'
			echo "stack_status=FAIL" >> ${_ENV_FILE}
			exit 1
		fi
	fi


