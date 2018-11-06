#!/usr/bin/env bash

	##############################################################
	# Global variables                                           #
	##############################################################
	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	export _FUNCTIONS_SCRIPT="${_THISPATH}/functions.sh"
	export _CONFIG_FILE="/root/custom/config.cfg"
	export _ENV_FILE="/root/custom/env.vars"
	export TERM=xterm


	##############################################################
	# Load functions                                             #
	##############################################################
	source ${_FUNCTIONS_SCRIPT}
	source ${_CONFIG_FILE}


	##############################################################
	# Local variables                                            #
	##############################################################
	_FIRMWARES_PATH="/home/shared/firmwares"
	_FIRMWARES_INPUT="/home/firmwares"
	_SSH_PARAMS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=quiet"
	_FIRMWARES_OUTPUT="/mnt/home/custom/firmwares/"
	_DATA="$1"

	function verify () {
		STATE="$1"
		unset STATUS
		if [ "${STATE}" = "0" ]; then STATUS=DONE; else STATUS=FAIL; fi
		server_message INFO "${STATUS}"
	}


	mkdir -p ${_FIRMWARES_INPUT} &> /dev/null
	server_message INFO "mounting firmwares from : ${server_hostname}"
	start_spinner "- (info) - mounting firmwares from : ${server_hostname} ..."
		sleep .25; cd ${_FIRMWARES_INPUT} && sshfs ${_SSH_PARAMS} -o noatime "${server_user}@${server_hostname}:${_FIRMWARES_PATH}/" .
	stop_spinner $?

	verify "${_STATUS}"

	if [ "${_STATUS}" = 0 ]; then

		if [ ! -z "${guc}" ]; then

			_CHECK_GUC=`find ${_FIRMWARES_INPUT} -maxdepth 100 -type d -name "*${guc}*"`

			if [ ! -z "${_CHECK_GUC}" ]; then
				server_message INFO "copying guc to DUT into : ${_FIRMWARES_OUTPUT}"
				start_spinner "- (info) - copying guc to DUT ..."
					sleep .25
					mkdir -p ${_FIRMWARES_OUTPUT}/guc/"${guc}"
					cp -R ${_CHECK_GUC}/* ${_FIRMWARES_OUTPUT}/guc/"${guc}"
				stop_spinner $?

				verify "${_STATUS}"
			fi
		fi

		if [ ! -z "${dmc}" ]; then

			_CHECK_DMC=`find ${_FIRMWARES_INPUT} -maxdepth 100 -type d -name "*${dmc}*"`

			if [ ! -z "${_CHECK_DMC}" ]; then
				server_message INFO "copying dmc to DUT into : ${_FIRMWARES_OUTPUT}"
				start_spinner "- (info) - copying dmc to DUT ..."
					sleep .75
					mkdir -p ${_FIRMWARES_OUTPUT}/dmc/"${dmc}"
					cp -R ${_CHECK_DMC}/* ${_FIRMWARES_OUTPUT}/dmc/"${dmc}"
				stop_spinner $?

				verify "${_STATUS}"
			fi
		fi


		if [ ! -z "${huc}" ]; then

			_CHECK_HUC=`find ${_FIRMWARES_INPUT} -maxdepth 100 -type d -name "*${huc}*"`

			if [ ! -z "${_CHECK_HUC}" ]; then
				server_message INFO "copying huc to DUT into : ${_FIRMWARES_OUTPUT}"
				start_spinner ">>> (info) Copying huc to DUT ..."
					sleep .25
					mkdir -p ${_FIRMWARES_OUTPUT}/huc/"${huc}"
					cp -R ${_CHECK_HUC}/* ${_FIRMWARES_OUTPUT}/huc/"${huc}"
				stop_spinner $?

				verify "${_STATUS}"
			fi
		fi

	fi