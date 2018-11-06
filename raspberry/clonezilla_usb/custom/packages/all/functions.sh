#!/usr/bin/env bash

# environment bash colors
export nc="\e[0m"
export underline="\e[4m"
export bold="\e[1m"
export green="\e[1;32m"
export red="\e[1;31m"
export yellow="\e[1;33m"
export blue="\e[1;34m"
export cyan="\e[1;36m"


function _spinner() {
    # $1 start/stop
    #
    # on start: $2 display message
    # on stop : $2 process exit status
    #           $3 spinner function pid (supplied from stop_spinner)

    local on_success="DONE"
    local on_fail="FAIL"
    local white="\e[1;37m"
    local green="\e[1;32m"
    local red="\e[1;31m"
    local nc="\e[0m"

    case $1 in
        start)
            # calculate the column where spinner and status msg will be displayed
            let column=$(tput cols)-${#2}-8
            # display message and position the cursor in $column column
            echo -ne ${2}
            printf "%${column}s"

            # start spinner
            i=1
            sp='\|/-'
            delay=${SPINNER_DELAY:-0.15}

            while :
            do
                printf "\b${sp:i++%${#sp}:1}"
                sleep ${delay}
            done

        ;;

        stop)
            if [[ -z ${3} ]]; then
                echo "spinner is not running.."
                exit 1
            fi

            kill $3 > /dev/null 2>&1

            # inform the user upon success or failure
            echo -en "\b["
            if [[ $2 -eq 0 ]]; then
                echo -en "${green}${on_success}${nc}"
                # logging the latest command status in the rotatory logs.
                logger DEBUG "latest command was : successful"
                export _STATUS=0
            else
                echo -en "${red}${on_fail}${nc}"
                # logging the latest command status in the rotatory logs.
                logger DEBUG "latest command was : failed"
                export _STATUS=1
            fi
            echo -e "]"
        ;;

        *)
            echo "invalid argument, try {start/stop}"
            exit 1
        ;;

    esac
}

function start_spinner {
    # $1 : msg to display
    _spinner "start" "${1}" &
    # set global spinner pid
    _sp_pid=$!
    disown
}

function stop_spinner {
    # $1 : command exit status
    _spinner "stop" $1 ${_sp_pid}
    unset _sp_pid
}


function main_start_time {
    unset _MAIN_DATE1
    _MAIN_DATE1=$(date +"%s")
}

function main_stop_time {
    unset _MAIN_DATE2 _MAIN_DIFF _MAIN_MINUTES _MAIN_SECONDS _MAIN_HOURS _MAIN_VAR_HOURS _MAIN_VAR_MINUTES _MAIN_VAR_SECONDS
    _MAIN_DATE2=$(date +"%s")
    _MAIN_DIFF=$(($_MAIN_DATE2-$_MAIN_DATE1))   # <-- There is seconds
    _MAIN_MINUTES=$(( (_MAIN_DIFF / 60) %60 ))
    _MAIN_SECONDS=$((($_MAIN_DIFF % 60)))
    _MAIN_HOURS=$((($_MAIN_MINUTES / 60)))
    if [ ${_MAIN_HOURS} != 0 ]; then _MAIN_VAR_HOURS=$(echo "${_MAIN_HOURS} Hours"); fi
    if [ ${_MAIN_MINUTES} != 0 ]; then _MAIN_VAR_MINUTES=$(echo "${_MAIN_MINUTES} Minutes"); fi
    if [ ${_MAIN_SECONDS} != 0 ]; then _MAIN_VAR_SECONDS=$(echo "${_MAIN_SECONDS} Seconds"); fi
    echo "($1) : ${_MAIN_VAR_HOURS} ${_MAIN_VAR_MINUTES} ${_MAIN_VAR_SECONDS} "
}

function start_time {
	unset _DATE1
	_DATE1=$(date +"%s")
}

function stop_time {
	unset _DATE2 _DIFF _MINUTES _SECONDS _HOURS _VAR_HOURS _VAR_MINUTES _VAR_SECONDS
	_DATE2=$(date +"%s")
	_DIFF=$(($_DATE2-$_DATE1))   # <-- There is seconds
	_MINUTES=$(( (_DIFF / 60) %60 ))
	_SECONDS=$((($_DIFF % 60)))
	_HOURS=$((($_MINUTES / 60)))
	if [ ${_HOURS} != 0 ]; then _VAR_HOURS=$(echo "${_HOURS} Hours"); fi
	if [ ${_MINUTES} != 0 ]; then _VAR_MINUTES=$(echo "${_MINUTES} Minutes"); fi
	if [ ${_SECONDS} != 0 ]; then _VAR_SECONDS=$(echo "${_SECONDS} Seconds"); fi
	echo "($1) : ${_VAR_HOURS} ${_VAR_MINUTES} ${_VAR_SECONDS} "
}


function hardware_specs () {

    case "$1" in

        "06D7TR")
            # Platform SNB tower (raspberry 2)
            # Reference : http://ark.intel.com/products/52213/Intel-Core-i7-2600-Processor-8M-Cache-up-to-3_80-GHz
            sleep .75; cp /mnt/home/${dut_user}/gfx-qa-tools/tests/platforms_specs/SNB_06D7TR_specs.cfg /mnt/home/custom/ 2> /dev/null
        ;;

        "D54250WYK")
            # Platform HSW-NUC (raspberry 2)
            # Reference : http://ark.intel.com/products/75028/Intel-Core-i5-4250U-Processor-3M-Cache-up-to-2_60-GHz
            sleep .75; cp /mnt/home/${dut_user}/gfx-qa-tools/tests/platforms_specs/HSW_D54250WYK_specs.cfg /mnt/home/custom/ 2> /dev/null
        ;;

        "LenovoG50-80")
            # Platform BDW lap
            echo ">>> (info) Not finish for MODEL : LenovoG50"
        ;;

        "NUC5i7RYB")
            # Platform BDW nuc
            echo ">>> (info) Not finish for MODEL : NUC5i7RYB"
        ;;

        "NUC5i5MYBE")
            # Platform BDW nuc
            sleep .75; cp /mnt/home/${dut_user}/gfx-qa-tools/tests/platforms_specs/BDW_NUC5i5MYBE_specs.cfg /mnt/home/custom/ 2> /dev/null
        ;;


        "NUC5i5RYB")
            # Platform BDW nuc (raspberry 2)
            # Reference : http://ark.intel.com/products/84984/Intel-Core-i5-5250U-Processor-3M-Cache-up-to-2_70-GHz
            sleep .75; cp /mnt/home/${dut_user}/gfx-qa-tools/tests/platforms_specs/BDW_NUC5i5RYB_specs.cfg /mnt/home/custom/ 2> /dev/null
        ;;

        "0XR1GT")
            # Platform IVB tower
            # Reference : http://ark.intel.com/products/65509/Intel-Core-i5-3330-Processor-6M-Cache-up-to-3_20-GHz
            sleep .75; cp /mnt/home/${dut_user}/gfx-qa-tools/tests/platforms_specs/IVB_0XR1GT_specs.cfg /mnt/home/custom/ 2> /dev/null
        ;;


        "NOTEBOOK")
            # Platform BXT-P
            sleep .75; echo "Not available for BXT-P"
        ;;


        "NUC6i5SYB")
            # Platform SKL-Nuc
            # Reference : http://ark.intel.com/products/91160/Intel-Core-i5-6260U-Processor-4M-Cache-up-to-2_90-GHz
            sleep .75; cp /mnt/home/${dut_user}/gfx-qa-tools/tests/platforms_specs/SKL_NUC6i5SYB_specs.cfg /mnt/home/custom/ 2> /dev/null
        ;;

        "SkylakeUDDR3LRVP7")
            # Platform KBL
            echo " >>> (info) Not available yet for KBL"
        ;;

        "SkylakeUDDR3LRVP7")
            # Platform KBL
            echo ">>> (info) Not available yet for KBL"
        ;;

        "BRASWELL")
            # Platform BSW
            # Reference : http://ark.intel.com/products/87261/Intel-Pentium-Processor-N3700-2M-Cache-up-to-2_40-GHz
            sleep .75; cp /mnt/home/${dut_user}/gfx-qa-tools/tests/platforms_specs/BSW_specs.cfg /mnt/home/custom/ 2> /dev/null
        ;;

        "02HK88")
            # Platform SKL laptop
            # Reference : http://ark.intel.com/products/88194/Intel-Core-i7-6500U-Processor-4M-Cache-up-to-3_10-GHz
            sleep .75; cp /mnt/home/${dut_user}/gfx-qa-tools/tests/platforms_specs/SKL_02HK88_specs.cfg /mnt/home/custom/ 2> /dev/null
        ;;

        "MS-B1421")
            # Platform KBL-Nuc
            # Reference : http://ark.intel.com/products/95451/Intel-Core-i7-7500U-Processor-4M-Cache-up-to-3_50-GHz
            sleep .75; cp /mnt/home/${dut_user}/gfx-qa-tools/tests/platforms_specs/KBL_MS-B1421_specs.cfg /mnt/home/custom/ 2> /dev/null
        ;;

        "GLK")
            _SPECS="/home/shared/platformSpecs/GLK/GLK_RVP1.cfg"
            # sleep .75; scp -o "StrictHostKeyChecking no" ${_SERVER_USER}@${_SERVER_HOSTNAME}:${_SPECS} /mnt/home/custom/GLK_specs.cfg &> /dev/null
            sleep .75; scp -o "StrictHostKeyChecking no" ${_SERVER_USER}@$10.219.106.111:${_SPECS} /mnt/home/custom/GLK_specs.cfg &> /dev/null
           ;;

    esac

}

server_message(){
    # sent a message to clonezilla file in the server.

    # The aim of this function is to send messages as a logger format.
    # The supported log levels (priorities) are:
    # EMERGENCY - system is unusable
    # ALERT     - action must be taken immediately
    # CRITICAL  - critical conditions
    # ERROR     - error conditions
    # WARN      - warning conditions
    # NOTICE    - normal but significant condition
    # INFO      - informational
    # DEBUG     - debug-level messages
    #
    # param:
    # - message_to_display: the message to be displayed in console.
    # - message_level: the message level to be displayed.
    # - timeout: ssh connection timeout (default is 5).

    # validating the numbers of arguments passed.
    [[ $# -lt 2 ]] && echo " - (ERROR) - Illegal number of parameters" && return

    # parameters variables
    local message_level="$1"
    local message_to_display="$2"
    local timeout="${3:-5}"

    # local variables
    local yy_mm_dd=$(date +%F)
    local hh_mm_ss=$(date +%H:%M:%S)
    local script_source=$(basename "$0")
    local output_file="${DATA}/clonezilla"

    case ${message_level} in
        1) message_level="INFO";;
        2) message_level="DEBUG";;
        3) message_level="NOTICE";;
        4) message_level="WARN";;
        5) message_level="ERROR";;
        6) message_level="CRITICAL";;
        7) message_level="ALERT";;
        8) message_level="EMERGENCY";;
    esac

    message_format="${yy_mm_dd} ${hh_mm_ss} - ${script_source} - \
(${message_level}) - ${message_to_display}"

    ssh -o "${SSH_PARAM_SHKC}" -o ConnectTimeout=${timeout} -q \
    ${server_user}@${server_hostname} 'echo "'${message_format}'" >> '${output_file}''

}


function verify () {
    STATE="$1"
    SERVER_USER="$2"
    SERVER_HOSTNAME="$3"
    SERVER_DATA="$4"
    unset STATUS
    if [ "${STATE}" = "0" ]; then STATUS=DONE; else STATUS=FAIL; fi
    timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${SERVER_USER}@${SERVER_HOSTNAME} 'echo ">>> (info) '${STATUS}'" >> '${SERVER_DATA}'/clonezilla'
}


check_spinner_status(){
    # Check spinner exit status.

    # The aim of this function is to check the latest spinner exit status and
    # send it to clonezilla file.
    # param:
    # - status: which is the exit status from the _spinner function.

    local status="${_STATUS}"

    case "${status}" in
        1) server_message INFO "DONE" ;;
        2) server_message INFO "FAIL" ;;
    esac
}

ssh_command(){
    # Perform a ssh command in a external system.

    # params:
    # - cmd: the command to perform externally.
    # - action: the possible values are:
    #   - execute: the command will be executed (the default action is to
    #              return the output)
    local cmd="$1"
    local action="${2:-noset}"
    local timeout=10

    [[ "${action}" != "noset" && "${action}" != "execute" ]] && \
        echo " - (ERROR) - Invalid parameter : ${action}" && return

    # return the output from the command.
    if [[ "${action}" == "noset" ]]; then
        output=$(ssh -o "${SSH_PARAM_SHKC}" -o ConnectTimeout=${timeout} -q ${server_user}@${server_hostname} "${cmd}")
        echo "${output}" && return
    else
        ssh -o "${SSH_PARAM_SHKC}" -o ConnectTimeout=${timeout} -q ${server_user}@${server_hostname} "${cmd}"
        return $?
    fi
}