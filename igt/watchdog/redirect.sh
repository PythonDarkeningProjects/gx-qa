#!/bin/bash


	export THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	source ${THISPATH}/tools/watchdog_functions.sh
	export ME=`basename $0`
	export PID=`cat ${THISPATH}/pid`
	export FILE="${THISPATH}/output.log"
	export REDIRECT_PID=$BASHPID


function read_process () {

	if [ -f "${FILE}" ]; then
		while true; do
			clear
			if [ -f "${FILE}" ]; then
				cat "${FILE}"
				sleep .75
			else
				clear; echo -ne "\n\n"
				echo -ne "--> ${yellow}Warning${nc} : the process id [${PID}] was killed \n"
				echo -ne "--> leaving ${ME} ...\n"
				sleep 2
				kill -9 ${FUNCTIONS_PID} > /dev/null 2>&1
				kill -9 ${REDIRECT_PID} > /dev/null 2>&1
				exit 1
			fi
		done
	else
		clear; echo -ne "\n\n"
		echo -ne "--> Please run ${ME} --divert \n\n"
		echo -ne "--> to be able for read the watchdog process \n\n"
		exit 1
	fi

}



function divert () {

	if [ -f "${THISPATH}/pid" ]; then

		CHECK_PROCESS=` ps -p ${PID} | grep -w "${PID}"`

		if [ ! -z "${CHECK_PROCESS}" ]; then
			clear; echo -ne "\n\n"
			echo -e "--> Rerouting process id ${PID} ...."
				sleep 1.5
				rm -rf ${THISPATH}/output.log &> /dev/null
				sudo reredirect -m ${FILE} ${PID} &> /dev/null

			echo -e "${blue}-->${nc} reading process id [${PID}] ..."
				sleep 3
				read_process
		
		elif [ -z "${CHECK_PROCESS}" ]; then
			clear; echo -ne "\n\n"
			echo -ne "--> The process id [${yellow}${PID}${nc}] ${red}does not exist${nc} \n"
			echo -ne "--> this could be due to it was killed \n"
			echo -ne "--> run watchdog.sh ro divert the pid to a file \n\n"
			exit 1
		fi

	elif [ ! -f "${THISPATH}/pid" ]; then
		clear; echo -ne "\n\n"
		echo -ne "${yellow}-->${nc} watchdog is not running \n"
		echo -ne "${yellow}-->${nc} please run watchdog.sh to divert the process \n\n"
		exit 1
	fi
}


function kill_process () {

	if [ -f "${THISPATH}/pid" ]; then

		CHECK_PROCESS=` ps -p ${PID} | grep -w "$PID"`

		if [ ! -z "${CHECK_PROCESS}" ]; then

			clear; echo -ne "\n\n"
			echo -e "${red}-->${nc} killing process id [${blue}${PID}${nc}] ..."
				sleep 1.5
				rm -rf ${THISPATH}/pid ${FILE} &> /dev/null
				kill -9 ${PID} > /dev/null 2>&1

			echo -ne "\n\n"; exit 1

		elif [ -z "${CHECK_PROCESS}" ]; then
			clear; echo -ne "\n\n"
			echo -ne "--> process id [${yellow}${PID}${nc}] ${red}does not exist${nc} \n\n"
			exit 1
		fi
	
	else
		clear; echo -ne "\n\n"
		echo -ne "--> watchdog is not running \n"
		echo -ne "--> please run watchdog.sh to divert the process \n\n"
		exit 1
	fi

}



function usage () {

    clear; echo -ne "\n\n"; echo -ne " ${cyan}Intel® Graphics for Linux* | 01.org${nc} \n\n"
    echo -ne " Usage : ${yellow}${ME}${nc} [options] \n\n"
    echo -ne "  -h | --help     See this menu \n"
    echo -ne "  -d | --divert   divert current watchdog process id to a file \n"
    echo -ne "  -r | --read     read current watchdog process id \n"
    echo -ne "  -k | --kill     kill current watchdog process id \n\n\n"; exit 1
}



	$@ 2> /dev/null
	clear

	while test $# != 0
	do
		case $1 in
			-d | --divert) divert ;;
			-r | --read) read_process ;;
			-k | --kill) kill_process ;;
			-h | --help) usage ;;
			*) usage ;;
		esac
	done