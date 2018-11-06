#!/bin/bash

	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	export _DATA=`cat /root/custom/DATA`
	export TERM=xterm

	# Loading functions
	source ${_THISPATH}/functions.sh
	source /root/custom/config.cfg

    if [ "${dut_user}" != "gfx" ]; then
        timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Changing username from (gfx) to ('${dut_user}') ..." >> '${_DATA}'/clonezilla'
        start_spinner ">>> (info) Changing username and home folder from (gfx) to (${dut_user}) ..."
            sleep .75
            usermod -l ${dut_user} -d /home/${dut_user} -m gfx
        stop_spinner $?
        verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"

        timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Changing group from (gfx) to ('${dut_user}') ..." >> '${_DATA}'/clonezilla'
        start_spinner ">>> (info) Changing group from (gfx) to (${dut_user}) ..."
            sleep .75
            groupmod -n ${dut_user} gfx
        stop_spinner $?
        verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"
    else
        timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) keeping the username by default ('${dut_user}') ..." >> '${_DATA}'/clonezilla'
    fi

    if [ "${dut_password}" != "linux" ]; then
        timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) Changing password from (linux) to ('${dut_password}') ..." >> '${_DATA}'/clonezilla'
        start_spinner ">>> (info) Changing password from (linux) to (${dut_password}) ..."
            sleep .75
            echo -e "${dut_password}\n${dut_password}" | passwd ${dut_user} 2> /dev/null
        stop_spinner $?
        verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"
    else
        timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo ">>> (info) keeping the password by default ('${dut_password}') ..." >> '${_DATA}'/clonezilla'
    fi
