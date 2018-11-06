#!/usr/bin/env bash

export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
export _DATA=`cat /root/custom/DATA`
export _DUT_WATCHER_DAEMON="/root/custom/packages/daemons/dutwatcher.service"
export _SENTINEL_DAEMON="/root/custom/packages/daemons/sentinel.service"
export TERM=xterm

# Loading functions
source ${_THISPATH}/functions.sh
source /root/custom/config.cfg

if [[ "${default_package}" == igt* ]]; then

    start_spinner "- (info) - changing (gfx) user to (${dut_user}) ..."
        sleep .25
        sed -i 's/gfx/'${dut_user}'/g' ${_DUT_WATCHER_DAEMON}
    stop_spinner $?

    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -q ${server_user}@${server_hostname} 'echo ">>> (info) copying igt daemons to (/etc/systemd/system) ..." >> '${_DATA}'/clonezilla'
    start_spinner "- (info) - copying igt daemons to (/etc/systemd/system) ..."
        sleep .25
        cp ${_DUT_WATCHER_DAEMON} /etc/systemd/system/
        cp ${_SENTINEL_DAEMON} /etc/systemd/system/
    stop_spinner $?
    verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"

    # enabling the daemon
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -q ${server_user}@${server_hostname} 'echo ">>> (info) enabling igt daemons ..." >> '${_DATA}'/clonezilla'
    start_spinner "- (info) - enabling igt daemons ..."
        sleep .25
        systemctl enable dutwatcher.service
        systemctl enable sentinel.service
    stop_spinner $?

    verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"

    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -q ${server_user}@${server_hostname} 'echo ">>> (info) starting igt daemons ..." >> '${_DATA}'/clonezilla'
    start_spinner "- (info) - starting igt daemons ..."
        sleep .25
        systemctl start dutwatcher.service
        systemctl start sentinel.service
    stop_spinner $?
    verify "${_STATUS}" "${server_user}" "${server_hostname}" "${_DATA}"

    # sending the current daemon status to clonezilla file
    IS_ENABLED_DUT_WATCHER=$(systemctl is-enabled dutwatcher.service)
    IS_ENABLED_SENTINEL=$(systemctl is-enabled sentinel.service)
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -q ${server_user}@${server_hostname} 'echo ">>> (info) dutwatcher.service status ('${IS_ENABLED_DUT_WATCHER}')" >> '${_DATA}'/clonezilla'
    ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=5 -q ${server_user}@${server_hostname} 'echo ">>> (info) sentinel.service status ('${IS_ENABLED_SENTINEL}')" >> '${_DATA}'/clonezilla'
fi

