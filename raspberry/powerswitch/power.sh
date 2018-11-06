#!/bin/bash

	# Prerequisites

	# sudo ls -s (this script) /usb/bin
	# added the following line to sudoers
	# pi ALL = (root) NOPASSWD: /usr/bin/(this script)

	# reference : http://comohacer.eu/gpio-raspberry-pi/
	# https://www.raspberrypi.org/documentation/usage/gpio-plus-and-raspi2/
	# http://pinout.xyz/pinout/pin12_gpio18
	# shc : http://www.thegeekstuff.com/2012/05/encrypt-bash-shell-script/?utm_source=tuicool

	############################################################
	#  Set global variables                                    @
	############################################################
	export GPIO_LIST="2 3 4 14 15 18 17 27"
	export _ME=`basename $0`

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

function check_root () {

	if [ "$EUID" -ne 0 ]; then
		clear &> /dev/null; echo -ne "\n\n"
		echo -ne "${red}==========================${nc} \n"
		echo -ne  "--> Please run as root \n"
		echo -ne "${red}==========================${nc} \n\n"
	  	exit 1
	fi

}

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

function start_spinner () {
    # $1 : msg to display
    _spinner "start" "${1}" &
    # set global spinner pid
    _sp_pid=$!
    disown

}

function stop_spinner () {
    # $1 : command exit status
    _spinner "stop" $1 $_sp_pid
    unset _sp_pid

}


function deactive_GPIOs () {

	check_root

	PIN="$1"
	SWITCH="$2"

	if [ -h "/sys/class/gpio/gpio${PIN}" ]; then

		clear &> /dev/null; echo -ne "\n\n"
		start_spinner ">>> (info) Deactivating GPIO [${PIN}] power switch [${SWITCH}] ..."
			sleep .5
			echo "${PIN}" > /sys/class/gpio/unexport
		stop_spinner $?
		echo -ne "\n\n"; exit 1
	else
		clear &> /dev/null; echo -ne "\n\n"
		echo -ne ">>> (info) the GPIO [${PIN}] ${yellow}is already deactivate${nc} \n\n"
		exit 2
	fi

}


function GPIO_configuration () {

	clear &> /dev/null
	echo -ne "\n\n"
	echo -e "  ${yellow}########################################################${nc}"
	echo -e "  ${yellow}#${nc}             ${cyan}GPIO CONFIGURATION${nc}                       ${yellow}#${nc}"
	echo -e "  ${yellow}#                                                      #${nc}"
	echo -e "  ${yellow}########################################################${nc}"
	echo -e "  ${yellow}#${nc} Relay (8 units) module pin  |  Raspberry 3 model b   ${yellow}#${nc}"
	echo -e "  ${yellow}#                                                      #${nc}"
	echo -e "  ${yellow}#${nc}  pin GND     ${blue}<-->${nc}    pin 6   - Name GND              ${yellow}#${nc}"
	echo -e "  ${yellow}#${nc}  pin IN1     ${blue}<-->${nc}    pin 3   - Name GPIO02           ${yellow}#${nc}"
	echo -e "  ${yellow}#${nc}  pin IN2     ${blue}<-->${nc}    pin 5   - Name GPIO03           ${yellow}#${nc}"
	echo -e "  ${yellow}#${nc}  pin IN3     ${blue}<-->${nc}    pin 7   - Name GPIOO4           ${yellow}#${nc}"
	echo -e "  ${yellow}#${nc}  pin IN4     ${blue}<-->${nc}    pin 8   - Name GPIO14           ${yellow}#${nc}"
	echo -e "  ${yellow}#${nc}  pin IN5     ${blue}<-->${nc}    pin 10  - Name GPIO15           ${yellow}#${nc}"
	echo -e "  ${yellow}#${nc}  pin IN6     ${blue}<-->${nc}    pin 12  - Name GPIO18           ${yellow}#${nc}"
	echo -e "  ${yellow}#${nc}  pin IN7     ${blue}<-->${nc}    pin 11  - Name GPIO17           ${yellow}#${nc}"
	echo -e "  ${yellow}#${nc}  pin IN8     ${blue}<-->${nc}    pin 13  - Name GPIO27           ${yellow}#${nc}"
	echo -e "  ${yellow}#${nc}  pin VCC     ${blue}<-->${nc}    pin 04  - Name DC power 5v      ${yellow}#${nc}"
	echo -e "  ${yellow}########################################################${nc}"
	echo -ne "\n\n"; exit 1

}

function verify_GPIO_state () {

	PIN="$1"
	VALUE="$2"

	if [ -f "/sys/class/gpio/gpio${PIN}/value" -a "${VALUE}" = "on" ]; then
		STATE=`cat "/sys/class/gpio/gpio${PIN}/value"`
		if [ "${STATE}" = "1" ]; then
			echo "the power switch (${SWITCH}) is already on"
			exit 77
		fi
	elif [ -f "/sys/class/gpio/gpio${PIN}/value" -a "${VALUE}" = "off" ]; then
		STATE=`cat "/sys/class/gpio/gpio${PIN}/value"`
		if [ "${STATE}" = "0" ]; then
			echo "the power switch (${SWITCH}) is already off"
			exit 77
		fi
	fi

}

function switch_on () {

	check_root

	PIN="$1"

	case "${PIN}" in
		2)  export SWITCH="1" ;;
		3)  export SWITCH="2" ;;
		4)  export SWITCH="3" ;;
		14) export SWITCH="4" ;;
		15) export SWITCH="5" ;;
		18) export SWITCH="6" ;;
		17) export SWITCH="7" ;;
		27) export SWITCH="8" ;;
	esac

	if [ -h "/sys/class/gpio/gpio${PIN}" ]; then

		verify_GPIO_state "${PIN}" "on"

		echo "turn on switch (${SWITCH})"
			sleep 1.5
			echo out > /sys/class/gpio/gpio"${PIN}"/direction
			echo 1 > /sys/class/gpio/gpio"${PIN}"/value
	else
		# 1- Creating a file with GPIO structure to be manipulated
		# 2- Configuration the file created as output
		# 3- turn on the relay

		verify_GPIO_state "${PIN}" "on"

		echo "turn on switch (${SWITCH})"
			sleep 1.5
			echo ${PIN} > /sys/class/gpio/export
			echo out > /sys/class/gpio/gpio"${PIN}"/direction
			echo 1 > /sys/class/gpio/gpio"${PIN}"/value
	fi

}

function switch_off () {

	check_root

	PIN="$1"

	case "${PIN}" in
		2)  export SWITCH="1" ;;
		3)  export SWITCH="2" ;;
		4)  export SWITCH="3" ;;
		14) export SWITCH="4" ;;
		15) export SWITCH="5" ;;
		18) export SWITCH="6" ;;
		17) export SWITCH="7" ;;
		27) export SWITCH="8" ;;
	esac

	if [ -h "/sys/class/gpio/gpio${PIN}" ]; then

		verify_GPIO_state "${PIN}" "off"

		echo "turn off switch (${SWITCH})"
			sleep 1.5
			echo out > /sys/class/gpio/gpio"${PIN}"/direction
			echo 0 > /sys/class/gpio/gpio"${PIN}"/value
	else
		# 1- Creating a file with GPIO structure to be manipulated
		# 2- Configuration the file created as output
		# 3- turn on the relay

		verify_GPIO_state "${PIN}" "off"

		echo "turn off switch (${SWITCH})"
			sleep 1.5
			echo ${PIN} > /sys/class/gpio/export
			echo out > /sys/class/gpio/gpio"${PIN}"/direction
			echo 0 > /sys/class/gpio/gpio"${PIN}"/value
	fi

}

function show_switch_states () {

	check_root

	LIST=`ls /sys/class/gpio | grep ^gpio[0-9] | sort --version-sort`

	if [ -z "${LIST}" ]; then
		clear &> /dev/null; echo -ne "\n\n"
		echo -ne ">>> (info) ${yellow}There is not switch enabled${nc} \n\n"
		exit 1
	else
		if [ "$1" != "no_message" ]; then clear &> /dev/null; echo -ne "\n\n"; fi

		start_spinner ">>> (info) Getting list ..."

			sleep .5
			FILE="/tmp/status"
			echo -e "${yellow}##################################${nc}" > ${FILE}
			echo -e "${yellow}#${nc}  ${blue}<Switch>  <Status>    <GPIO>${nc}  ${yellow}#${nc}" >> ${FILE}

			for switch in ${LIST}; do

				case "${switch}" in
					gpio2)  export SWITCH="1" ; GPIO="gpio02" ;;
					gpio3)  export SWITCH="2" ; GPIO="gpio03" ;;
					gpio4)  export SWITCH="3" ; GPIO="gpio04" ;;
					gpio14) export SWITCH="4" ; GPIO="gpio14" ;;
					gpio15) export SWITCH="5" ; GPIO="gpio15" ;;
					gpio18) export SWITCH="6" ; GPIO="gpio18" ;;
					gpio17) export SWITCH="7" ; GPIO="gpio17" ;;
					gpio27) export SWITCH="8" ; GPIO="gpio27" ;;
				esac

				STATE=`cat "/sys/class/gpio/${switch}/value"`

				if [ "${STATE}" = "0" ]; then
					echo -e "${yellow}#${nc}     ${SWITCH}       ${red}disabled${nc}   ${GPIO}  ${yellow}#${nc}" >> ${FILE}
				elif [ "${STATE}" = "1" ]; then
					echo -e "${yellow}#${nc}     ${SWITCH}       ${green}enabled${nc}    ${GPIO}  ${yellow}#${nc}" >> ${FILE}
				fi
			done
			echo -e "${yellow}##################################${nc}" >> ${FILE}
		stop_spinner $?

		echo -ne "\n\n"
		cat ${FILE}
		echo -ne "\n\n"; exit 1

	fi

}


function verify_gpio_pins () {

	MODE="$1" PIN="$2"

	VERIFY=`echo ${GPIO_LIST} | grep -w "${PIN}"`

	if [ -z "${VERIFY}" ]; then
		echo -ne "\n\n"
		echo -ne ">>> (err) ${red}GPIO pin not found${nc}, this are the GPIO pin allowed \n\n"
		echo -ne "${GPIO_LIST} \n\n"; exit 1
	else
		if [ "${MODE}" = "-on" ]; then
			switch_on "${PIN}"
		elif [ "${MODE}" = "-off" ]; then
			switch_off "${PIN}"
		elif [ "${MODE}" = "-d" ]; then

			case "${PIN}" in
				2)  export SWITCH="1" ;;
				3)  export SWITCH="2" ;;
				4)  export SWITCH="3" ;;
				14) export SWITCH="4" ;;
				15) export SWITCH="5" ;;
				18) export SWITCH="6" ;;
				17) export SWITCH="7" ;;
				27) export SWITCH="8" ;;
			esac

			pause(){
				local m="$@"
				echo "$m"
			}

			while :
			do
				clear &> /dev/null; echo -ne "\n\n"
				echo -ne ">>> (${red}warn${nc}) : this option will apply the following actions \n\n"
				echo -ne " A) turn off the power switch [${SWITCH}] \n"
				echo -ne " B) remove the entry for this GPIO [${PIN}] causing that when you run this script with \n"
				echo -ne "     option -s the related power switch will not appears \n\n"
				echo -ne " Do you want to continue ? \n\n"
				echo -ne " 1) Yes \n"
				echo -ne " 2) No \n\n"
				read -e -p " Your choice: " choose

				case ${choose} in
					1) deactive_GPIOs "${PIN}" "${SWITCH}" ;;
					2) echo -ne "\n\n"; exit 1 ;;
					*) pause ;;
				esac
			done
		fi
	fi

}


function massive_power () {

	check_root

	ACTION="$1"

	# Creating the entries if not exists
	echo -ne "\n\n"
	for pin in ${GPIO_LIST}; do
		if [ ! -h "/sys/class/gpio/gpio${pin}" ]; then
			start_spinner ">>> (info) Creating entry for gpio pin [#${pin}] ..."
				sleep .5
				echo ${pin} > /sys/class/gpio/export
				echo out > /sys/class/gpio/gpio"${pin}"/direction
			stop_spinner $?
		fi
	done

	COUNT_ON="0" COUNT_OFF="0"

	for pin in ${GPIO_LIST}; do
		STATE=`cat "/sys/class/gpio/gpio${pin}/value"`
		if [ "${STATE}" = "1" ]; then
			((COUNT_ON++))
		elif [ "${STATE}" = "0" ]; then
			((COUNT_OFF++))
		fi
	done

	if [ "${COUNT_ON}" -eq "8" -a "${ACTION}" = "on" ]; then
		echo -ne "\n\n"
		echo -ne ">>> (info) all power switches are ${green}enabled${nc} \n"
		show_switch_states "no_message"
	elif [ "${COUNT_OFF}" -eq "8" -a "${ACTION}" = "off" ]; then
		echo -ne "\n\n"
		echo -ne ">>> (info) all power switches are ${red}disabled${nc} \n"
		show_switch_states "no_message"
	fi

	LIST=`ls /sys/class/gpio | grep ^gpio[0-9] | sort --version-sort`

	if [ "${ACTION}" = "on" ]; then

		echo -ne "\n\n"
		for gpio in ${LIST}; do

			case "${gpio}" in
				gpio2)  export SWITCH="1" ;;
				gpio3)  export SWITCH="2" ;;
				gpio4)  export SWITCH="3" ;;
				gpio14) export SWITCH="4" ;;
				gpio15) export SWITCH="5" ;;
				gpio18) export SWITCH="6" ;;
				gpio17) export SWITCH="7" ;;
				gpio27) export SWITCH="8" ;;
			esac

			STATE=`cat "/sys/class/gpio/${gpio}/value"`

			if [ "${STATE}" = "0" ]; then
				start_spinner ">>> (info) turn on switch [${SWITCH}] [${gpio}] ${green}...${nc} "
					sleep .5
					echo out > /sys/class/gpio/"${gpio}"/direction
					echo 1 > /sys/class/gpio/"${gpio}"/value
				stop_spinner $?
			fi

		done

		show_switch_states "no_message"

	elif [ "${ACTION}" = "off" ]; then

		echo -ne "\n\n"
		for gpio in ${LIST}; do

			case "${gpio}" in
				gpio2)  export SWITCH="1" ;;
				gpio3)  export SWITCH="2" ;;
				gpio4)  export SWITCH="3" ;;
				gpio14) export SWITCH="4" ;;
				gpio15) export SWITCH="5" ;;
				gpio18) export SWITCH="6" ;;
				gpio17) export SWITCH="7" ;;
				gpio27) export SWITCH="8" ;;
			esac

			STATE=`cat "/sys/class/gpio/${gpio}/value"`

			if [ "${STATE}" = "1" ]; then
				start_spinner ">>> (info) turn off switch (${SWITCH}) (${gpio}) ${red}...${nc} "
					sleep .5
					echo out > /sys/class/gpio/"${gpio}"/direction
					echo 0 > /sys/class/gpio/"${gpio}"/value
				stop_spinner $?
			fi

		done

		show_switch_states "no_message"
	fi

}


function usage () {

    clear &> /dev/null; echo -ne "\n\n"; echo -ne " ${cyan}Intel® Graphics for Linux* | 01.org${nc} \n\n"
    echo -ne " Usage : ${yellow}${_ME}${nc} [options] \n\n"
    echo -ne "  -h               See this menu \n"
    echo -ne "  -g               Show GPIO Configuration \n"
    echo -ne "  -s               Show power switch actives/inactives \n"
    echo -ne "  -d   <gpio pin>  Deactivate a power switch \n"
    echo -ne "  -on  <gpio pin>  turn on the power switch related gpio ping \n"
    echo -ne "  -off <gpio pin>  turn off the power switch related gpio ping \n"
    echo -ne "  -on  all         turn on all power switches \n"
    echo -ne "  -off all         turn off all power switches \n\n"; exit 1
}

clear &> /dev/null
$@ 2> /dev/null
	case $1 in
		-h ) usage ;;
        -g ) GPIO_configuration ;;
        -s ) show_switch_states ;;
        -d ) verify_gpio_pins "$1" "$2" ;;
		-on )
			if [ "${2}" = "all" ]; then massive_power "on"; fi
			verify_gpio_pins "$1" "$2" ;;
		-off ) if [ "${2}" = "all" ]; then massive_power "off"; fi
			verify_gpio_pins "$1" "$2" ;;
		*) usage ;;
	esac

