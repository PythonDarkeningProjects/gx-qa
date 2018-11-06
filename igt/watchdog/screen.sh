#!/bin/bash

# this script run the watchdogX in a tmux session in order to keep alive it
	
	clear; echo -ne "\n\n"
	export THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	export ME=`basename $0`
	source ${THISPATH}/config.cfg

function create () {
	unset SESSION_NAME
	SESSION_NAME="tmux_watchdog0${raspberry_power_switch}"

	# Checking if session name already exits
	CHECK=`tmux ls | awk -F":" '{print $1}' | grep ${SESSION_NAME}`
	if [ ! -z "${CHECK}" ]; then 
		echo "--> Killing tmux session name : [${SESSION_NAME}]"
		tmux kill-session -t ${SESSION_NAME}
	fi

	echo "${SESSION_NAME}" > tmux_session_name
	tmux new-session -d -s ${SESSION_NAME} ${THISPATH}/watchdog.sh
	RESULT=$?

	if [ "${RESULT}" = 0 ]; then
		echo -ne "--> Session [${SESSION_NAME}] was created \n\n"; exit 1
	else
		echo -ne "--> an error was occured creating the session [${SESSION_NAME}] \n\n"; exit 1
	fi

}

function attach () {

	unset SESSION_NAME
	if [ -f "${THISPATH}/tmux_session_name" ]; then
		SESSION_NAME=`cat ${THISPATH}/tmux_session_name`
		CHECK=`tmux ls | awk -F":" '{print $1}' | grep ${SESSION_NAME}`
		if [ ! -z "${CHECK}" ]; then 
			tmux attach-session -d -t ${SESSION_NAME}
			exit 1
		else
			echo -ne "--> No session for watchdog : [${SESSION_NAME}]\n\n"
			exit 1
		fi
	else
		echo -ne "--> No session for watchdog : [${SESSION_NAME}] \n\n"
		exit 1
	fi
}

function kill () {

	unset SESSION_NAME
	if [ -f "${THISPATH}/tmux_session_name" ]; then
		SESSION_NAME=`cat ${THISPATH}/tmux_session_name`
		CHECK=`tmux ls | awk -F":" '{print $1}' | grep ${SESSION_NAME}`
		if [ ! -z "${CHECK}" ]; then 
			tmux kill-session -t ${SESSION_NAME}
			exit 1
		else
			echo -ne "--> No session for watchdog : [${SESSION_NAME}] \n\n"
			exit 1
		fi
	else
		echo -ne "--> No session for watchdog : [${SESSION_NAME}] \n\n"
		exit 1
	fi
}

function usage () {
    clear; echo -ne "\n\n"; echo -ne " ${cyan}Intel® Graphics for Linux* | 01.org${nc} \n\n"
    echo -ne " Usage : ${yellow}${ME}${nc} [options] \n\n"
    echo -ne "  -create    Create a new session for watchdog \n"
    echo -ne "  -attach    attach the current session for watchdog \n"
    echo -ne "  -kill      kill the current session for watchdog \n\n"; exit 1
}



$@ 2> /dev/null

	while test $# != 0
	do
		case $1 in
			-kill) kill ;;
			-attach) attach ;;
			-create) create ;;
			*) usage ;;
		esac

	done