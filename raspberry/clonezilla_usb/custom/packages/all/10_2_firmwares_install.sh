#!/bin/bash


	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	export _INSTALL_SCRIPT="/root/custom/packages/firmwares/install.sh"
	export TERM=xterm


	##############################################################
	# Load functions                                             #
	##############################################################
	source ${_THISPATH}/functions.sh
	source /root/custom/config.cfg
	source /root/custom/env.vars # this contains _DATA variable

	##############################################################
	# Local variables                                            #
	##############################################################
	_GUC="/home/custom/firmwares/guc/${guc}"
	_DMC="/home/custom/firmwares/dmc/${dmc}"
	_HUC="/home/custom/firmwares/huc/${huc}"

	if [ ! -z "${guc}" ]; then
		timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Installing ('${guc}') ..." >> '${_DATA}'/clonezilla'
		echo -e ">>> (info) ${cyan}Installing${nc} (${guc}) ..."
			sleep .5 #cp "${_INSTALL_SCRIPT}" "${_GUC}"
			cd "${_GUC}"; bash install.sh
	fi


	if [ ! -z "${dmc}" ]; then
		timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Installing ('${dmc}') ..." >> '${_DATA}'/clonezilla'
			echo -e ">>> (info) ${cyan}Installing${nc} (${dmc}) ..."
				sleep .5 #cp "${_INSTALL_SCRIPT}" "${_DMC}"
				cd "${_DMC}"; bash install.sh
	fi


	if [ ! -z "${huc}" ]; then
		timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Installing ('${huc}') ..." >> '${_DATA}'/clonezilla'
		echo -e  ">>> (info) ${cyan}Installing${nc} (${huc}) ..."
			sleep .5 #cp "${_INSTALL_SCRIPT}" "${_HUC}"
			cd "${_HUC}"; bash install.sh
	fi