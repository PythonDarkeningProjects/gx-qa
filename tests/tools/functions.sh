#!/bin/bash

    ##############################################################
    # LOCAL COLORS                                               #
    ##############################################################
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
                sleep $delay
            done
            ;;
        stop)
            if [[ -z ${3} ]]; then
                echo "spinner is not running.."
                exit 1
            fi

            kill $3 > /dev/null 2>&1

            # inform the user uppon success or failure
            echo -en "\b["
            if [[ $2 -eq 0 ]]; then
                echo -en "${green}${on_success}${nc}"
                _STATUS=0
            else
                echo -en "${red}${on_fail}${nc}"
                _STATUS=1
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
    _spinner "stop" $1 $_sp_pid
    unset _sp_pid
}

function start_time {
    unset _DATE1
    if [ -z "$1" ]; then
        _DATE1=$(date +"%s")
    else
        _DATE1=$(date -r "$1" +%s)
    fi
}

function stop_time {
    unset _DATE2 _DIFF _MINUTES _SECONDS _HOURS _VAR_HOURS _VAR_MINUTES _VAR_SECONDS
    _DATE2=$(date +"%s")
    _DIFF=$(($_DATE2-$_DATE1))   # <-- There is _SECONDS

    _MINUTES=$(( (_DIFF / 60) %60 ))
    _SECONDS=$((($_DIFF % 60)))
    _HOURS=$((($_MINUTES / 60)))

    if [ $_HOURS != 0 ]; then _VAR_HOURS=$(echo "$_HOURS HOURS"); fi
    if [ $_MINUTES != 0 ]; then _VAR_MINUTES=$(echo "$_MINUTES MINUTES"); fi
    if [ $_SECONDS != 0 ]; then _VAR_SECONDS=$(echo "$_SECONDS SECONDS"); fi
    echo "--> [$1] : ${_VAR_HOURS} ${_VAR_MINUTES} ${_VAR_SECONDS}"
}