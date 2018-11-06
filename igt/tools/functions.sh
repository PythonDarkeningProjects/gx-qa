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

function start_time () {
	unset _DATE1
	_DATE1=$(date +"%s")
}

function stop_time () {
	unset _DATE2 _DIFF _MINUTES _SECONDS _HOURS _VAR_HOURS _VAR_MINUTES _VAR_SECONDS
	_DATE2=$(date +"%s")
	_DIFF=$(($_DATE2-$_DATE1))   # <-- There is seconds
	export _MINUTES=$(( (_DIFF / 60) %60 ))
	_SECONDS=$((($_DIFF % 60)))
	_HOURS=$((($_MINUTES / 60)))
	if [ ${_HOURS} != 0 ]; then _VAR_HOURS=$(echo "${_HOURS} Hours"); fi
	if [ ${_MINUTES} != 0 ]; then _VAR_MINUTES=$(echo "${_MINUTES} Minutes"); fi
	if [ ${_SECONDS} != 0 ]; then _VAR_SECONDS=$(echo "${_SECONDS} Seconds"); fi
	echo -e "($1) : ${_VAR_HOURS} ${_VAR_MINUTES} ${_VAR_SECONDS} "
}

function banners () {

    if [ -z "${_ITERATION_NUMBER}" ]; then _ITERATION_NUMBER=1
    else
        _ITERATION_NUMBER=`cat ${_MAIN_PATH}/scripts/.current_iteration 2> /dev/null`
    fi



    case $1 in 
        igt_basic) 
                    echo -ne "\n\n"
                    echo -ne " (( ${yellow}Iteration number${nc} : ${blue}${_ITERATION_NUMBER}/${igt_iterations}${nc} )) \n\n"
                    echo -e "${blue}+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ +-+-+-+-+-+ +-+-+-+-+-+${nc}"
                    echo -e "${yellow}|S|U|I|T|E|${nc} |i|n|t|e|l|-|g|p|u|-|t|o|o|l|s| |b|a|s|i|c| |t|e|s|t|s|"
                    echo -e "${blue}+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ +-+-+-+-+-+ +-+-+-+-+-+${nc}"
                    echo -ne "\n\n"
        ;;

        igt_fast_feedback) 
                    echo -ne "\n\n"
                    echo -ne " (( ${yellow}Iteration number${nc} : ${blue}${_ITERATION_NUMBER}/${igt_iterations}${nc} )) \n\n"
                    echo -e "${blue}+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ +-+-+-+-+-+ +-+-+-+-+-+-+-+${nc}"
                    echo -e "${yellow}|S|U|I|T|E|${nc} |i|n|t|e|l|-|g|p|u|-|t|o|o|l|s| |f|a|s|t|-|f|e|e|d|b|a|c|k|"
                    echo -e "${blue}+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ +-+-+-+-+-+ +-+-+-+-+-+-+-+${nc}"
                    echo -ne "\n\n"
        ;;
        
        igt_all) 
                    echo -ne "\n\n"
                    echo -ne " (( ${yellow}Iteration number${nc} : ${blue}${_ITERATION_NUMBER}/${igt_iterations}${nc} )) \n\n"
                    echo -e "${blue}+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ +-+-+-+-+-+ +-+-+-+-+-+${nc}"
                    echo -e "${yellow}|S|U|I|T|E|${nc} |i|n|t|e|l|-|g|p|u|-|t|o|o|l|s| |a|l|l|"
                    echo -e "${blue}+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ +-+-+-+-+-+ +-+-+-+-+-+${nc}"
                    echo -ne "\n\n"
        ;;

        igt_extended_list)
                echo -ne "\n\n"
                echo -ne " (( ${yellow}Iteration number${nc} : ${blue}${_ITERATION_NUMBER}/${igt_iterations}${nc} )) \n\n"
                echo -e "${blue}+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+-+${nc}"
                echo -e "${yellow}|S|U|I|T|E|${nc} |i|n|t|e|l|-|g|p|u|-|t|o|o|l|s| |e|x|t|e|n|d|e|d|-|l|i|s|t|${nc}"
                echo -e "${blue}+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+-+${nc}"
                echo -ne "\n\n"
        ;;

    esac
}

function statistics () {

    # ===========================================================================================================================
    # Statistics before to run IGT
    # ===========================================================================================================================

    # ===========================================================================================================================
    # Getting the families and subtests in a file
    # ===========================================================================================================================
    if [ ! -f "${_MAIN_PATH}/scripts/.families_with_subtests" ] || [ ! -f "${_MAIN_PATH}/scripts/.families_without_subtests" ]; then
        
        rm ${_MAIN_PATH}/scripts/.families_with_subtests ${_MAIN_PATH}/scripts/.families_without_subtests &> /dev/null
        _TEST_LIST=`cat "${_MAIN_PATH}/tests/test-list.txt" | sed -e '/TESTLIST/d' -e 's/ /\n/g'`
        families=''
        subtests=''

        for test in ${_TEST_LIST}; do
             SUBTESTS=`"${_MAIN_PATH}/tests/$test" --list-subtests`
                if [ -z "$SUBTESTS" ]; then
                    echo "$test" >> ${_MAIN_PATH}/scripts/.families_without_subtests
                    ((families++))
                else
                    for subtest in $SUBTESTS; do
                        echo "$test@$subtest" >> ${_MAIN_PATH}/scripts/.families_with_subtests
                        ((subtests++))
                     done
                fi
        done
    fi

    # ===========================================================================================================================
    # Removing empty lines from blacklist file
    # ===========================================================================================================================
    sed -i '/^\s*$/d' ${_MAIN_PATH}/scripts/blacklist
    # ===========================================================================================================================
    # Changing the "/" for "@" from blacklist file
    # ===========================================================================================================================
    sed -i 's|/|@|g' ${_MAIN_PATH}/scripts/blacklist


    if [ "$1" = "info" ]; then clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"; fi
    start_spinner "--> Getting IGT statistics ..."

        # ===========================================================================================================================
        # Getting the total IGT test by number to improve times in this script
        # ===========================================================================================================================
        if [ ! -f "${_MAIN_PATH}/scripts/.total_IGT_tests_number" ] || [ ! -s "${_MAIN_PATH}/scripts/.total_IGT_tests_number" ]; then
            ${_MAIN_PATH}/scripts/run-tests.sh -l | wc -l > ${_MAIN_PATH}/scripts/.total_IGT_tests_number
            export totalIGT_tests_number=$(cat ${_MAIN_PATH}/scripts/.total_IGT_tests_number) # this is a number
        else
            export totalIGT_tests_number=$(cat ${_MAIN_PATH}/scripts/.total_IGT_tests_number) # this is a number
        fi

        # ===========================================================================================================================
        # Getting the total IGT tests by name to improve times in this script
        # ===========================================================================================================================
        if [ ! -f "${_MAIN_PATH}/scripts/.total_IGT_tests_name" ]; then
            ${_MAIN_PATH}/scripts/run-tests.sh -l > ${_MAIN_PATH}/scripts/.total_IGT_tests_name
        fi

        # ===========================================================================================================================
        # Validating the blacklist file
        # ===========================================================================================================================
        exclude_tests=$(sed -n '/^-x/p' ${_MAIN_PATH}/scripts/blacklist)
        include_tests=$(sed -n '/^-t/p' ${_MAIN_PATH}/scripts/blacklist)

        if [ ! -z "$exclude_tests" ] && [ -z "$include_tests" ]; then
            # Condition for exclude_tests
            validate_blacklist=et

        elif [ -z "$exclude_tests" ] && [ ! -z "$include_tests" ]; then
            # Condition for include_tests
            validate_blacklist=it

        elif [ ! -z "$exclude_tests" ] && [ ! -z "$include_tests" ]; then
            # Condition for both (exclude & include tests)
            validate_blacklist=both
        fi


        case $validate_blacklist in

            et)
                # ===========================================================================================================================
                # Only the back_LIST has -x
                # ===========================================================================================================================
                echo ${_PASSWORD} | sudo -S rm -r /tmp/* &> /dev/null
                sed -n '/^-x/p' ${_MAIN_PATH}/scripts/blacklist > /tmp/without_x
                sed -i 's/-x //g' /tmp/without_x

                _TESTS_TO_NOT_RUN=''
                _LIST=`cat /tmp/without_x`

                for test in ${_LIST}; do
                    _CHECK_WILDCARD=`echo ${test} | grep -e [*] -e [.] -e [?] -e [$]`
                    if [ -z "${_CHECK_WILDCARD}" ]; then _test="^$test$"; else _test="$test"; fi
                    validate_A=`cat ${_MAIN_PATH}/scripts/.families_with_subtests | grep ${_test} | wc -l`
                        if [ "$validate_A" -eq 0 ]; then
                            validate_B=`cat ${_MAIN_PATH}/scripts/.families_without_subtests | grep ${_test} | wc -l`
                            if [ "${validate_B}" -ne 0 ]; then _TESTS_TO_NOT_RUN=$((validate_B+_TESTS_TO_NOT_RUN)); fi
                        else
                            _TESTS_TO_NOT_RUN=$((validate_A+_TESTS_TO_NOT_RUN))
                        fi
                done

                _TEST_TO_RUN=$((totalIGT_tests_number-_TESTS_TO_NOT_RUN))
                _PORCENTAGE_TO_RUN=$(echo "scale =4; ${_TEST_TO_RUN}*100/$totalIGT_tests_number" | bc)
                _PORCENTAGE_blacklist=$(echo "scale =4; 100 - ${_PORCENTAGE_TO_RUN}" | bc)
                _WITHOUT_S=`cat ${_MAIN_PATH}/scripts/.families_without_subtests | wc -l`
                _WITH_S=`cat ${_MAIN_PATH}/scripts/.families_with_subtests | wc -l`
                _LAST_ITERATION_FOLDER=$(ls -tr ${_MAIN_PATH}/scripts/ | grep iteration | tail -1)
                if [ -d "${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/tests" ]; then _CURRENT_TESTS=$(ls ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/tests | wc -l); fi 

                echo -ne "\n\n" 
                echo -ne " ${blue}=============================================${nc} \n"
                echo -ne " Total IGT tests             : ${totalIGT_tests_number} (${blue}100%${nc}) \n"
                echo -ne " Families without subtests   : ${_WITHOUT_S} \n"
                echo -ne " Families with subtests      : ${_WITH_S} \n"
                echo -ne " IGT test to run             : ${_TEST_TO_RUN}  (${cyan}${_PORCENTAGE_TO_RUN}%${nc})\n"
                echo -ne " IGT blacklisted tests       : ${_TESTS_TO_NOT_RUN} (${yellow}${_PORCENTAGE_blacklist}%${nc}) \n"
                echo -ne " You will run only           : (${green}${_PORCENTAGE_TO_RUN}%${nc}) of IGT \n"
                if [ ! -z "${_CURRENT_TESTS}" ]; then
                _CURRENT_PORCENTAGE=$(echo "scale =4; ${_CURRENT_TESTS}*100/${_TEST_TO_RUN}" | bc)
                echo -ne " The current progress is     : ${_CURRENT_TESTS}/${_TEST_TO_RUN} (${yellow}${_CURRENT_PORCENTAGE}%${nc}) \n"
                fi
                echo -ne " ${blue}=============================================${nc} \n\n\n"
                
                # Getting the statistics in a file to view in check_IP.sh script
                echo "$totalIGT_tests_number" > ${_MAIN_PATH}/scripts/.statistics
                echo "${_TEST_TO_RUN}" >> ${_MAIN_PATH}/scripts/.statistics
                echo "$_TESTS_TO_NOT_RUN" >> ${_MAIN_PATH}/scripts/.statistics #empty
                echo "${_PORCENTAGE_TO_RUN}" >> ${_MAIN_PATH}/scripts/.statistics
                echo "$_WITHOUT_S" >> ${_MAIN_PATH}/scripts/.statistics
                echo "$_WITH_S" >> ${_MAIN_PATH}/scripts/.statistics

                echo -ne "\n\n"
                stop_spinner $?

                if [ "$1" = "info" ]; then exit 2; fi

                ;;

            it)
                # ===========================================================================================================================
                # Only the back_LIST has -t
                # ===========================================================================================================================
                echo ${_PASSWORD} | sudo -S rm -r /tmp/* &> /dev/null
                sed -n '/^-t/p' ${_MAIN_PATH}/scripts/blacklist > /tmp/without_t
                sed -i 's/-t //g' /tmp/without_t
                # Getting the full tests from .total_IGT_tests_name (to improve times) but without "/" prefix
                cat ${_MAIN_PATH}/scripts/.total_IGT_tests_name | sed 's|/|@|g' > /tmp/full_test_without_prefix
                #echo -ne "grep" > /tmp/_LIST_to_run

                _TEST_TO_RUN=''
                _LIST=`cat /tmp/without_t`
                for test in $_LIST; do
                    _CHECK_WILDCARD=`echo ${test} | grep -e [*] -e [.] -e [?] -e [$]`
                    if [ -z "${_CHECK_WILDCARD}" ]; then _test="^$test$"; else _test="$test"; fi
                    validate_A=`cat ${_MAIN_PATH}/scripts/.families_with_subtests | grep ${_test} | wc -l`
                        if [ "$validate_A" -eq 0 ]; then
                            validate_B=`cat ${_MAIN_PATH}/scripts/.families_without_subtests | grep ${_test} | wc -l`
                           if [ "${validate_B}" -ne 0 ]; then _TEST_TO_RUN=$((validate_B+_TEST_TO_RUN)); fi
                        else
                            _TEST_TO_RUN=$((validate_A+_TEST_TO_RUN))
                        fi
                done

                _PORCENTAGE_TO_RUN=$(echo "scale =4; ${_TEST_TO_RUN}*100/$totalIGT_tests_number" | bc)
                _WITHOUT_S=`cat ${_MAIN_PATH}/scripts/.families_without_subtests | wc -l`
                _WITH_S=`cat ${_MAIN_PATH}/scripts/.families_with_subtests | wc -l`
                _LAST_ITERATION_FOLDER=$(ls -tr ${_MAIN_PATH}/scripts/ | grep iteration | tail -1)
                if [ -d "${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/tests" ]; then _CURRENT_TESTS=$(ls ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/tests | wc -l); fi 

                echo -ne "\n\n" 
                echo -ne " ${blue}=============================================${nc} \n"
                echo -ne " Total IGT tests             : ${totalIGT_tests_number} (${blue}100%${nc}) \n"
                echo -ne " Families without subtests   : ${_WITHOUT_S} \n"
                echo -ne " Families with subtests      : ${_WITH_S} \n"
                echo -ne " IGT test to run             : ${_TEST_TO_RUN}  (${cyan}${_PORCENTAGE_TO_RUN}%${nc})\n"
                echo -ne " You will run only           : (${green}${_PORCENTAGE_TO_RUN}%${nc}) of IGT \n"
                if [ ! -z "${_CURRENT_TESTS}" ]; then
                _CURRENT_PORCENTAGE=$(echo "scale =4; ${_CURRENT_TESTS}*100/${_TEST_TO_RUN}" | bc)
                echo -ne " The current progress is     : ${_CURRENT_TESTS}/${_TEST_TO_RUN} (${yellow}${_CURRENT_PORCENTAGE}%${nc}) \n"
                fi
                echo -ne " ${blue}=============================================${nc} \n\n\n"
                
                # Getting the statistics in a file to view in check_IP.sh script
                echo "$totalIGT_tests_number" > ${_MAIN_PATH}/scripts/.statistics
                echo "${_TEST_TO_RUN}" >> ${_MAIN_PATH}/scripts/.statistics
                echo  >> ${_MAIN_PATH}/scripts/.statistics #empty
                echo "${_PORCENTAGE_TO_RUN}" >> ${_MAIN_PATH}/scripts/.statistics
                echo "$_WITHOUT_S" >> ${_MAIN_PATH}/scripts/.statistics
                echo "$_WITH_S" >> ${_MAIN_PATH}/scripts/.statistics
                
                echo -ne "\n\n"
                stop_spinner $?

                if [ "$1" = "info" ]; then exit 2; fi

                ;;

            both)
                # ===========================================================================================================================
                # The back_LIST has -t and -x
                # ===========================================================================================================================
                echo ${_PASSWORD} | sudo -S rm -r /tmp/* &> /dev/null
                sed -n '/^-t/p' ${_MAIN_PATH}/scripts/blacklist > /tmp/without_t
                sed -n '/^-x/p' ${_MAIN_PATH}/scripts/blacklist > /tmp/without_x

                sed -i 's/-t //g' /tmp/without_t; sed -i 's/-x //g' /tmp/without_x

                _TESTS_TO_NOT_RUN=''
                _LIST=`cat /tmp/without_x`
                for test in $_LIST; do
                    _CHECK_WILDCARD=`echo ${test} | grep -e [*] -e [.] -e [?] -e [$]`
                    if [ -z "${_CHECK_WILDCARD}" ]; then _test="^$test$"; else _test="$test"; fi
                    validate_A=`cat ${_MAIN_PATH}/scripts/.families_with_subtests | grep ${_test} | wc -l`
                        if [ "$validate_A" -eq 0 ]; then
                            validate_B=`cat ${_MAIN_PATH}/scripts/.families_without_subtests | grep ${_test} | wc -l`
                            if [ "${validate_B}" -ne 0 ]; then _TESTS_TO_NOT_RUN=$((validate_B+_TESTS_TO_NOT_RUN)); fi
                        else
                            _TESTS_TO_NOT_RUN=$((validate_A+_TESTS_TO_NOT_RUN))
                        fi
                done

                _TEST_TO_RUN=''
                _LIST=`cat /tmp/without_t`
                for test in $_LIST; do
                    _CHECK_WILDCARD=`echo ${test} | grep -e [*] -e [.] -e [?] -e [$]`
                    if [ -z "${_CHECK_WILDCARD}" ]; then _test="^$test$"; else _test="$test"; fi
                    validate_A=`cat ${_MAIN_PATH}/scripts/.families_with_subtests | grep ${_test} | wc -l`
                        if [ "$validate_A" -eq 0 ]; then
                            validate_B=`cat ${_MAIN_PATH}/scripts/.families_without_subtests | grep ${_test} | wc -l`
                            if [ "${validate_B}" -ne 0 ]; then _TEST_TO_RUN=$((validate_B+_TEST_TO_RUN)); fi
                        else
                            _TEST_TO_RUN=$((validate_A+_TEST_TO_RUN))
                        fi
                done

                _PORCENTAGE_TO_RUN=$(echo "scale =4; ${_TEST_TO_RUN}*100/$totalIGT_tests_number" | bc)
                _PORCENTAGE_blacklist=$(echo "scale =4; $_TESTS_TO_NOT_RUN*100/$totalIGT_tests_number" | bc)
                _WITHOUT_S=`cat ${_MAIN_PATH}/scripts/.families_without_subtests | wc -l`
                _WITH_S=`cat ${_MAIN_PATH}/scripts/.families_with_subtests | wc -l`

                _LAST_ITERATION_FOLDER=$(ls -tr ${_MAIN_PATH}/scripts/ | grep iteration | tail -1)
                if [ -d "${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/tests" ]; then _CURRENT_TESTS=$(ls ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/tests | wc -l); fi

                echo -ne "\n\n"
                echo -ne " ${blue}============================================${nc} \n"
                echo -ne " Total IGT tests             : ${totalIGT_tests_number} (${blue}100%${nc}) \n"
                echo -ne " Families without subtests   : ${_WITHOUT_S} \n"
                echo -ne " Families with subtests      : ${_WITH_S} \n"
                echo -ne " IGT test to run             : ${_TEST_TO_RUN}  (${cyan}${_PORCENTAGE_TO_RUN}%${nc})\n"
                echo -ne " IGT blacklisted tests       : ${_TESTS_TO_NOT_RUN} (${yellow}${_PORCENTAGE_blacklist}%${nc}) \n"
                echo -ne " You will run only           : (${green}${_PORCENTAGE_TO_RUN}%${nc}) of IGT \n"
                if [ ! -z "${_CURRENT_TESTS}" ]; then
                _CURRENT_PORCENTAGE=$(echo "scale =4; ${_CURRENT_TESTS}*100/${_TEST_TO_RUN}" | bc)
                echo -ne " The current progress is     : ${_CURRENT_TESTS}/${_TEST_TO_RUN} (${yellow}${_CURRENT_PORCENTAGE}%${nc}) \n"
                fi
                echo -ne " ${blue}=============================================${nc} \n\n\n"
                
                # ===========================================================================================================================
                # Getting the statistics in a file to view in check_IP.sh script
                # ===========================================================================================================================
                echo "$totalIGT_tests_number" > ${_MAIN_PATH}/scripts/.statistics
                echo "${_TEST_TO_RUN}" >> ${_MAIN_PATH}/scripts/.statistics
                echo "$_TESTS_TO_NOT_RUN" >> ${_MAIN_PATH}/scripts/.statistics
                echo "${_PORCENTAGE_TO_RUN}" >> ${_MAIN_PATH}/scripts/.statistics
                echo "$_WITHOUT_S" >> ${_MAIN_PATH}/scripts/.statistics
                echo "$_WITH_S" >> ${_MAIN_PATH}/scripts/.statistics
                
                echo -ne "\n\n"
                stop_spinner $?
                
                if [ "$1" = "info" ]; then exit 2; fi

                ;;

        esac
}

function main_start_time () {
    unset _MAIN_DATE1
    _MAIN_DATE1=$(date +"%s")
}

function main_stop_time () {
    unset _MAIN_DATE2 _MAIN_DIFF _MAIN_MINUTES _MAIN_SECONDS _MAIN_MAIN_HOURS _MAIN_VAR_HOURS _MAIN_VAR_MINUTES _MAIN_VAR_SECONDS
    _MAIN_DATE2=$(date +"%s")
    _MAIN_DIFF=$(($_MAIN_DATE2-$_MAIN_DATE1))   # <-- There is seconds
    export _MAIN_MINUTES=$(( (_MAIN_DIFF / 60) %60 ))
    _MAIN_SECONDS=$((($_MAIN_DIFF % 60)))
    _MAIN_HOURS=$((($_MAIN_MINUTES / 60)))
    if [ ${_MAIN_HOURS} != 0 ]; then _MAIN_VAR_HOURS=$(echo "${_MAIN_HOURS} Hours"); fi
    if [ ${_MAIN_MINUTES} != 0 ]; then _MAIN_VAR_MINUTES=$(echo "${_MAIN_MINUTES} Minutes"); fi
    if [ ${_MAIN_SECONDS} != 0 ]; then _MAIN_VAR_SECONDS=$(echo "${_MAIN_SECONDS} Seconds"); fi
    echo -e "($1)   : ${_MAIN_VAR_HOURS} ${_MAIN_VAR_MINUTES} ${_MAIN_VAR_SECONDS} "
}

function CheckDmesgInfo () {

  # Setting dmesg level logs
  _d_emerg=$(dmesg --level=emerg | wc -l)
  _d_alert=$(dmesg --level=alert | wc -l)
  _d_crit=$(dmesg --level=crit | wc -l)
  _d_err=$(dmesg --level=err | wc -l)
  _d_warn=$(dmesg --level=warn | wc -l)
  _d_debug=$(dmesg --level=debug | wc -l)

  _d_notice=$(dmesg --level=notice | wc -l)
  _d_info=$(dmesg --level=info | wc -l)

  # Setting logs files
  mPATH="$1"
 _EMERGENCY_LOG_FILE=${mPATH}/dmesg_emergency.log
 _ALERT_LOG_FILE=${mPATH}/dmesg_alert.log
 _CRITICAL_LOG_FILE=${mPATH}/dmesg_critical.log
 _ERROR_LOG_FILE=${mPATH}/dmesg_error.log
 _WARN_LOG_FILE=${mPATH}/dmesg_warning.log
 _NOTICE_LOG_FILE=${mPATH}/dmesg_notice.log
 _INFO_LOG_FILE=${mPATH}/dmesg_information.log
 _DEBUG_LOG_FILE=${mPATH}/dmesg_debug.log

  if [ ${_d_emerg} -ne 0 ]; then
    echo -ne "${cyan}-->${nc} dmesg ${cyan}EMERGENCY${nc} : (${bold}${_d_emerg}${nc}) msg \n"
    script ${_EMERGENCY_LOG_FILE} bash -c 'dmesg --level=emerg -x -T' > /dev/null
    sed -i '1d' ${_EMERGENCY_LOG_FILE}; sed -i -e '$ d' ${_EMERGENCY_LOG_FILE} # removing Script command lines
    sed -i '/^\s*$/d' ${_EMERGENCY_LOG_FILE}
  fi

  if [ ${_d_alert} -ne 0 ]; then
    echo -ne "${cyan}-->${nc} dmesg ${blue}ALERT${nc}     : (${bold}${_d_alert}${nc}) msg \n"
    script ${_ALERT_LOG_FILE} bash -c 'dmesg --level=alert -x -T' > /dev/null
    sed -i '1d' ${_ALERT_LOG_FILE}; sed -i -e '$ d' ${_ALERT_LOG_FILE} # removing Script command lines
    sed -i '/^\s*$/d' ${_ALERT_LOG_FILE}
  fi

  if [ ${_d_crit} -ne 0 ]; then
    echo -ne "${cyan}-->${nc} dmesg ${red}CRIT1CAL${nc}   : (${bold}${_d_crit}${nc}) msg \n"
    script ${_CRITICAL_LOG_FILE} bash -c 'dmesg --level=crit -x -T' > /dev/null
    sed -i '1d' ${_CRITICAL_LOG_FILE}; sed -i -e '$ d' ${_CRITICAL_LOG_FILE} # removing Script command lines
    sed -i '/^\s*$/d' ${_CRITICAL_LOG_FILE}
  fi

  if [ ${_d_err} -ne 0 ]; then
    echo -ne "${cyan}-->${nc} dmesg ${red}ERROR${nc}   : (${bold}${_d_err}${nc}) msg \n"
    script ${_ERROR_LOG_FILE} bash -c 'dmesg --level=err -x -T' > /dev/null
    sed -i '1d' ${_ERROR_LOG_FILE}; sed -i -e '$ d' ${_ERROR_LOG_FILE} # removing Script command lines
    sed -i '/^\s*$/d' ${_ERROR_LOG_FILE}
  fi

  if [ ${_d_warn} -ne 0 ]; then
    echo -ne "${cyan}-->${nc} dmesg ${yellow}WARNING${nc} : (${bold}${_d_warn}${nc}) msg \n"
    script ${_WARN_LOG_FILE} bash -c 'dmesg --level=warn -x -T' > /dev/null
    sed -i '1d' ${_WARN_LOG_FILE}; sed -i -e '$ d' ${_WARN_LOG_FILE} # removing Script command lines
    sed -i '/^\s*$/d' ${_WARN_LOG_FILE}
  fi

  if [ ${_d_notice} -ne 0 ]; then
    echo -ne "${cyan}-->${nc} dmesg ${yellow}NOTICE${nc}  : (${bold}${_d_notice}${nc}) msg \n"
    script ${_NOTICE_LOG_FILE} bash -c 'dmesg --level=notice -x -T' > /dev/null
    sed -i '1d' ${_NOTICE_LOG_FILE}; sed -i -e '$ d' ${_NOTICE_LOG_FILE} # removing Script command lines
    sed -i '/^\s*$/d' ${_NOTICE_LOG_FILE}
  fi

  if [ ${_d_info} -ne 0 ]; then
    echo -ne "${cyan}-->${nc} dmesg ${yellow}INFO${nc}    : (${bold}${_d_info}${nc}) msg \n"
    script ${_INFO_LOG_FILE} bash -c 'dmesg --level=info -x -T' > /dev/null
    sed -i '1d' ${_INFO_LOG_FILE}; sed -i -e '$ d' ${_INFO_LOG_FILE} # removing Script command lines
    sed -i '/^\s*$/d' ${_INFO_LOG_FILE}
  fi

  if [ ${_d_debug} -ne 0 ]; then
    echo -ne "${cyan}-->${nc} dmesg ${blue}DEBUG${nc}   : (${bold}${_d_debug}${nc}) msg \n"
    script ${_DEBUG_LOG_FILE} bash -c 'dmesg --level=debug -x -T' > /dev/null
    sed -i '1d' ${_DEBUG_LOG_FILE}; sed -i -e '$ d' ${_DEBUG_LOG_FILE} # removing Script command lines
    sed -i '/^\s*$/d' ${_DEBUG_LOG_FILE}
  fi

  #echo -ne " Supported log levels (priorities) : \n\n"
  #echo -ne " emerg     - system is unusable \n"
  #echo -ne " alert     - action must be taken immediately \n"
  #echo -ne " crit      - critical conditions \n"
  #echo -ne " err       - error conditions \n"
  #echo -ne " warn      - warning conditions \n"
  #echo -ne " notice    - normal but significant condition \n"
  #echo -ne " info      - informational \n"
  #echo -ne " debug     - debug-level messages \n\n\n"
}

function blacklist () {

    if [ ! -d "${_MAIN_PATH}" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne " --> ${red}intel-gpu-tools folder does not exists${nc} \n"
        echo -ne " --> into [/home/${_USER}/intel-graphics] \n"
        echo -ne " --> please install the MX Gfx stack or put intel-gpu-tools in the above path \n\n\n"; exit 2
    fi

    # ===========================================================================================================================
    # Checking for Piglit folder inside Intel-GPU-Tools
    # ===========================================================================================================================
    if [ ! -d "${_MAIN_PATH}/piglit" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne "--> ${red}Piglit was not found${nc} <-- into ${_MAIN_PATH} \n"
        echo -ne "--> ${yellow}Please download Piglit into before to continue${nc} \n"
        echo -ne "--> git clone http://anongit.freedesktop.org/git/piglit.git ${_MAIN_PATH} \n\n"; exit 2
    fi

    if [ ! -f "${_MAIN_PATH}/scripts/blacklist.example" -a ! -f "${_MAIN_PATH}/scripts/blacklist" -a -f "${_MAIN_PATH}/tests/test-list.txt" ]; then
        echo -ne "\n\n"
        start_spinner "--> Generating a blacklist.example ..."
            sleep 2; _TEST_LIST_BY_FAMILY=$(cat "${_MAIN_PATH}/tests/test-list.txt" | sed -e '/TESTLIST/d' -e 's/ /\n/g')
            echo "${_TEST_LIST_BY_FAMILY}" > ${_MAIN_PATH}/scripts/blacklist.example
        stop_spinner $?
    elif [ ! -f "${_MAIN_PATH}/tests/test-list.txt" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne "--> ${yellow}Warning${nc} : intel-gpu-tools ${red}is not compiled${nc} \n"
        echo -ne "--> please compile intel-gpu-tools to continue \n\n"; exit 2
    fi

    # ===========================================================================================================================
    # Checking for blacklist file
    # ===========================================================================================================================
    if [ -f "${_MAIN_PATH}/tests/test-list.txt" ] && [ -f "${_MAIN_PATH}/tests/test-list-full.txt" ]; then
        # Making a comparision of the IGT tests that were not compiled (if exists)
        rm /tmp/not_compiled /tmp/tests_not_compiled ${_MAIN_PATH}/tests/tests_not_compiled &> /dev/null
        cat ${_MAIN_PATH}/tests/test-list.txt | sed -e '/TESTLIST/d' -e 's/ /\n/g' > ${_MAIN_PATH}/tests/normal
        cat ${_MAIN_PATH}/tests/test-list-full.txt | sed -e '/TESTLIST/d' -e 's/ /\n/g' > ${_MAIN_PATH}/tests/full
        cp ${_THISPATH}/tools/compare.py ${_MAIN_PATH}/tests
        python ${_MAIN_PATH}/tests/compare.py ${_MAIN_PATH}/tests/full ${_MAIN_PATH}/tests/normal > /tmp/tests_not_compiled # the order in the files matters a lot
        sed -i 's/ has changed//g' /tmp/tests_not_compiled

        while read line; do
            echo -ne "\t $line \n" >> ${_MAIN_PATH}/tests/tests_not_compiled # the path where will saved the tests not compiled (if exists)
        done < /tmp/tests_not_compiled
    fi

    _COUNT_FAMILY=$(cat "${_MAIN_PATH}/scripts/blacklist.example" 2> /dev/null| wc -l)
    if [ ! -f "${_MAIN_PATH}/scripts/blacklist" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne " >> ${red}blacklist file not found${nc} << \n\n"
        echo -ne "--> Please create the file (blacklist) into [${_MAIN_PATH}/scripts] \n"
        echo -ne "--> and follow the next structure \n"
        echo -ne "--> in a separate line type down the test that you want / you dont want to run with IGT \n"
        echo -ne "--> example : \n\n"
        echo -ne "-t <test to run> \n"
        echo -ne "-x <test to not run> \n\n"
        echo -ne "${cyan}================================================================${nc} \n"
        echo -ne "--> Please see the ${yellow}${underline}blacklist.example${nc} file located in \n"
        echo -ne "--> [${_MAIN_PATH}/scripts/] \n"
        echo -ne "--> this file contains all tests by family, where you can see \n"
        echo -ne "--> which tests will excluded or included in the IGT execution \n\n"
        echo -ne "--> IGT's families : [${blue}${_COUNT_FAMILY}${nc}] \n"
        if [ -f "${_MAIN_PATH}/tests/tests_not_compiled" ] && [ -s "${_MAIN_PATH}/tests/tests_not_compiled" ]; then
            echo -e "--> ${cyan}Information${nc} : the following IGT families have not been compiled"
            echo -ne "--> for this [tag / commit] \n\n"
            cat ${_MAIN_PATH}/tests/tests_not_compiled; echo
        fi
        echo -ne "${cyan}================================================================${nc} \n\n\n"
        exit 2
    fi

    # Removing empty lines from blacklist file
    sed -i '/^\s*$/d' ${_MAIN_PATH}/scripts/blacklist
    # Changing the "/" for "@" from blacklist file
    sed -i 's|/|@|g' ${_MAIN_PATH}/scripts/blacklist

    if [ "$1" = "info" ]; then statistics "info"; fi
}

function blacklist_fast_feedback () {

    _COUNT_FAMILY=$(cat "${_MAIN_PATH}/scripts/blacklist.example" 2> /dev/null | wc -l)
    if [ ! -f "${_MAIN_PATH}/scripts/blacklist" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne " >> ${red}blacklist file not found${nc} << \n\n"
        echo -ne "--> Please create the file (blacklist) into [${_MAIN_PATH}/scripts] \n"
        echo -ne "--> and follow the next structure \n"
        echo -ne "--> in a separate line type down the test that you want / you dont want to run with IGT \n"
        echo -ne "--> example : \n\n"
        echo -ne "-t <test to run> \n"
        echo -ne "-x <test to not run> \n\n"
        echo -ne "${cyan}================================================================${nc} \n\n\n"
        exit 2
    fi

    # Removing empty lines from blacklist file
    sed -i '/^\s*$/d' ${_MAIN_PATH}/scripts/blacklist
    # Changing the "/" for "@" from blacklist file
    sed -i 's|/|@|g' ${_MAIN_PATH}/scripts/blacklist

    if [ "$1" = "info" ]; then statistics "info"; fi
}

function check_blacklist () {

    cat -n ${_MAIN_PATH}/scripts/blacklist > /tmp/blacklist
    _FILE1="${_MAIN_PATH}/scripts/blacklist"
    _FILE2="/tmp/blacklist"

    if [ ! -s ${_FILE1} ]; then
        echo -ne "\n\n"
        echo "--> The blacklist file could not be empty"
        echo -ne "--> Please specify the tests to run/not run \n\n"; exit 1
    fi

    #########################################
    # Checking if the blacklist's format    #
    #########################################
    _NOTIFICATION=0 _FAILURE=0

    clear; echo -ne "\n\n"
    start_spinner "--> Checking for errors on blacklist file ..."

    while read line; do
        _LINE=`echo ${line} | awk '{print $1}'`
        _CHECK=`echo ${line} | awk '{print $2}'`
        _TEST=`echo ${line} | awk '{sub($1 FS,"" );print}'` # print all except the first value

        if [ "${_CHECK}" != "-x" -a "${_CHECK}" != "-t" ]; then
            if [ ${_NOTIFICATION} -eq 0 ]; then clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"; echo -ne "--> ${yellow}The blacklist file has an unexpected format${nc} \n\n"; ((_NOTIFICATION++)); fi
            echo -e "--> ${red}Line wrong${nc} [${_LINE}] value : [${_TEST}] / expected value (-x or -t)"
            ((_FAILURE++))
        fi
    done < ${_FILE2}

    stop_spinner $?

    if [ "${_FAILURE}" -ge 1 ]; then echo -ne "\n\n"; exit 1; fi

    ####################################################################################
    # # Checking if the tests are compiled in the current intel-gpu-tools commit / tag #
    ####################################################################################

    if [ ! -f "${_MAIN_PATH}/scripts/.families_with_subtests" ] || [ ! -f "${_MAIN_PATH}/scripts/.families_without_subtests" ]; then
        _TEST_LIST=`cat "${_MAIN_PATH}/tests/test-list.txt" | sed -e '/TESTLIST/d' -e 's/ /\n/g'`

        for test in ${_TEST_LIST}; do
             SUBTESTS=`"${_MAIN_PATH}/tests/${test}" --list-subtests`
                if [ -z "$SUBTESTS" ]; then
                    echo "${test}" >> ${_MAIN_PATH}/scripts/.families_without_subtests
                else
                    for subtest in ${SUBTESTS}; do
                        echo "${test}@${subtest}" >> ${_MAIN_PATH}/scripts/.families_with_subtests
                     done
                fi
        done
    fi

    rm -rf /tmp/full_test.txt &> /dev/null
    cat ${_MAIN_PATH}/scripts/.families_without_subtests >> /tmp/full_test.txt
    cat ${_MAIN_PATH}/scripts/.families_with_subtests >> /tmp/full_test.txt
    if [ -f "${_MAIN_PATH}/tests/tests_not_compiled" ] && [ ! -s "${_MAIN_PATH}/tests/tests_not_compiled" ]; then cat ${_MAIN_PATH}/tests/tests_not_compiled | awk '{print $1}' >> /tmp/full_test.txt; fi

    rm -rf ${_FILE2} &> /dev/null
    _EXCLUDE_TESTS=$(sed -n '/^-x/p' ${_FILE1} | sed 's/-x //g')
    _INCLUDE_TESTS=$(sed -n '/^-t/p' ${_FILE1} | sed 's/-t //g')

    if [ ! -z "${_EXCLUDE_TESTS}" ]; then echo "${_EXCLUDE_TESTS}" >> /tmp/blacklist; fi
    if [ ! -z "${_INCLUDE_TESTS}" ]; then echo "${_INCLUDE_TESTS}" >> /tmp/blacklist; fi


    unset _NOTIFICATION
    _NOTIFICATION=0 _TESTS_NOT_FOUND="" _FLAG=0

    if [ -f "/home/${_USER}/intel-graphics/intel-gpu-tools/scripts/test_not_found" ]; then rm -rf /home/${_USER}/intel-graphics/intel-gpu-tools/scripts/test_not_found &> /dev/null; fi
    
    start_spinner "--> Validating the tests entered in blacklist file ..."

    rm /home/${_USER}/intel-graphics/intel-gpu-tools/scripts/test_not_found &> /dev/null
    
    while read -r line; do

        _CHECK_WILDCARD=`echo ${line} | grep -e [*] -e [.] -e [?] -e [$]` # Skipping the tests with wildcards
        if [ -z "${_CHECK_WILDCARD}" ]; then
            _CHECK_TEST=`cat /tmp/full_test.txt | grep -w "${line}"`
            if [ -z "${_CHECK_TEST}" ]; then
                if [ "${_NOTIFICATION}" -eq 0 ]; then clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"; ((_NOTIFICATION++)); _FLAG=1; fi
                echo "${line}" >> /home/${_USER}/intel-graphics/intel-gpu-tools/scripts/test_not_found
                _TESTS_NOT_FOUND="${_TESTS_NOT_FOUND} ${line}"
            fi
        fi

    done < ${_FILE2}

    stop_spinner $?

    if [ "${_FLAG}" -eq 1 ]; then 
        echo -ne "\n\n"
        echo -ne "--> ${yellow}The following tests were${nc} ${red}NOT FOUND${nc} ${yellow}in intel-gpu-tools${nc} \n\n"
        cat /home/${_USER}/intel-graphics/intel-gpu-tools/scripts/test_not_found; echo -ne "\n\n"
        echo -ne "--> Please check the blacklist file and remove/modify this tests to continue \n"
        echo -ne "--> You can also find this tests on : /home/${_USER}/intel-graphics/intel-gpu-tools/scripts/test_not_found \n\n"
        exit 1
    fi
}

function auto_notify () {

    export Sender="fastfeedback@noreply.com"
    case $1 in 

        "ok")
            rm -rf ${MainEmailer} &> /dev/null
            cp ${attachmentsEmailerFile} ${MainEmailer}
            SingleHostname=`echo ${SingleHostname[@]} | sed -e 's/ //g' -e 's/.$//'`

            echo -e "--> Sending (auto) email notification ..."
            sed -i '24s/^.*$/toaddr = ['${default_mailing_list}']/g' ${MainEmailer}
            sed -i '25s/^.*$/sub = "[auto] intel-gpu-tools fastfeedback was launched on '${DateToday}' at '${Hour}'"/g' ${MainEmailer}
            sed -i '34s|^.*$| Hi : |g' ${MainEmailer}
            sed -i '36s|^.*$| intel-gpu-tools fastfeedback was launched in the following platforms : |g' ${MainEmailer}
            sed -i "38s|^.*$| --> Hostnames : [${SingleHostname}] |g" ${MainEmailer}
            sed -i '40s/^.*$/ Intel Graphics for Linux* | 01.org/g' ${MainEmailer}
            sed -i '41s/^.*$/ This is an automated message please do not reply/g' ${MainEmailer}
            sed -i '65s|^.*$|folder = "'${LOG_FOLDER}'"|g' ${MainEmailer} # only filepath
            sleep .5
            python ${MainEmailer}; wait
            # rm ${MainEmailer} &> /dev/null
        ;;

        "error")

            rm -rf ${MainEmailer} &> /dev/null
            cp ${EmailerFile} ${MainEmailer}
            Comment="$2"
            echo -e "--> Sending (auto) email notification ..."
            sed -i '21s/^.*$/receivers = ['$default_mailing_list']/g' ${MainEmailer}
            export default_mailing_list=`echo "${default_mailing_list}" | tr -d "'"`
            sed -i '23s/^.*$/To: '${default_mailing_list}'/g' ${MainEmailer}
            sed -i '24s|^.*$|Subject: (auto) IGT fastfeedback could not be launched due to an error|g' ${MainEmailer}
            sed -i '26s|^.*$| Hi : |g' ${MainEmailer}
            sed -i '28s/^.*$/ (auto) IGT fastfeedback could not be launched due to the following error./g' ${MainEmailer}
            sed -i "29s|^.*$| error : ${Comment}.|g" ${MainEmailer}
            sed -i '31s/^.*$/ Intel Graphics for Linux* | 01.org./g' ${MainEmailer}
            sed -i '32s/^.*$/ This is an automated message please do not reply/g' ${MainEmailer}
            sleep .5
            python ${MainEmailer}; wait
            #rm ${MainEmailer} &> /dev/null
        ;;
    esac

}

function email_template () {

    export mDateToday=`date +"%Y-%m-%d"`
    export Hour=`date +%I:%M:%S`
    export GZIP=-9

    if [ ! -z "${_BASIC}" -a "$1" = "finish" ]; then

        ##############################################################
        # Compress the attachments                                   #
        ##############################################################
        echo ${_PASSWORD} | sudo -S ls &> /dev/null; sleep .5
        echo ${_PASSWORD} | sudo -S rm -rf /tmp/* &> /dev/null
        export _LAST_ITERATION_FOLDER="iteration1"
        mkdir -p /tmp/trc/html
        outputFolders="/tmp/trc/html /tmp/${_LAST_ITERATION_FOLDER}/"
        Message="Please find this report as well in http://linuxgraphics.intel.com/igt-reports/${_YEAR}/${default_package}/${currentPlatform}/${_WEEKn}/${mDateToday}/${Hour}"
        export _OUTPUT_IGT_DIR="/home/${_USER}/Desktop/results/intel-gpu-tools"
        export _OUTPUT_IGT_NAME="${default_package}_${dut_hostname}_TRC_summary_${_WEEKn}_${_HOUR}.csv"
        if [ "${igt_iterations}" -gt 1 ]; then blacklistFile="${_MAIN_PATH}/scripts/blacklist.1"; elif [ "${igt_iterations}" -eq 1 ]; then blacklistFile="${_MAIN_PATH}/scripts/blacklist"; fi

        if [ "${trc_report}" = "yes" ]; then
            echo -ne "${yellow}-->${nc} Uploading results to TRC [${currentEnv}] ... \n\n"
            # Folder for upload to TRC
            cp ${_MAIN_PATH}/scripts/dmesg_and_kern_logs.tar.gz  /tmp/trc/html 2> /dev/null
            cp ${_OUTPUT_DIR}/${_OUTPUT_NAME_BACKTRACE} /tmp/trc/html 2> /dev/null
            cp -r ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/html/ /tmp/trc/
            rm -rf /tmp/trc/html/${_LAST_ITERATION_FOLDER}
            cp /home/custom/config.cfg /tmp/trc/html/dutConfig.cfg
            cp /home/custom/config.yml /tmp/trc/html/dutConfig.yml
            cp /home/custom/kernel/packages/commit_info /tmp/trc/html/kernel_commit_information.cfg
            cp /home/custom/graphic_stack/packages/config.cfg /tmp/trc/html/gfx_stack.cfg
            cp /home/custom/*specs.cfg /tmp/trc/html/ 2> /dev/null
            cp /home/custom/graphic_stack/packages/easy-bugs /tmp/trc/html/gfx_stack_easy_bugs.cfg
            cp ${blacklistFile} /tmp/trc/html/blacklist.cfg 2> /dev/null
            cp ${_MAIN_PATH}/scripts/iteration1/results.json /tmp/trc/html/ 2> /dev/null
            cp ${_OUTPUT_DIR}/*runtime* /tmp/trc/html 2> /dev/null
            #################################################################################################################
            # Compress results.json in order to upload it to TRC (rule is if the file is less than 20MB it will be uploaded)
            cd /tmp/trc/html/; tar cvzf results.json.tar.gz /tmp/trc/html/results.json; rm results.json 2> /dev/null
            # Checking if the file size meet with the rule
            resultsJsonSize=`du -s /tmp/results.json.tar.gz | awk '{print $1}'`
            ruleSize=10000
            if [ ${resultsJsonSize} -gt ${ruleSize} ];then
                echo "--> results.json.tar.gz weight (${resultsJsonSize}) is not allowed, removing it ..."
                rm /tmp/results.json.tar.gz 2> /dev/null
            fi
            # Checking dmesg size
            dmesgSize=`du -s /tmp/trc/html/dmesg_and_kern_logs.tar.gz | awk '{print $1}'`
            #ruleSize=10000
            #if [ ${dmesgSize} -gt ${ruleSize} ];then
            #    echo "--> dmesg_and_kern_logs.tar.gz weight (${dmesgSize}) is not allowed in TRC, removing it ..."
            #    rm /tmp/trc/html/dmesg_and_kern_logs.tar.gz 2> /dev/null
            #fi

            # size to check :10M
            if [[ $(find /tmp/trc/html/dmesg_and_kern_logs.tar.gz -type f -size +10485760c 2>/dev/null) ]]; then
                echo "--> dmesg_and_kern_logs.tar.gz weight (${dmesgSize}) is not allowed in TRC, removing it ..."
                rm /tmp/trc/html/dmesg_and_kern_logs.tar.gz 2> /dev/null
            fi
            #################################################################################################################

            echo ${_PASSWORD} | sudo -S cat /sys/kernel/debug/dri/0/i915_display_info > /tmp/trc/html/attachedDisplays.cfg
            if [ "${upload_reports}" = "yes" ]; then echo ${Message} > /tmp/trc/html/BackupReport.cfg; fi
            echo "python /home/${_USER}/dev/igt/autouploader/autoUploader.py -s ${currentSuite} -r ${currentRelease} -t ${currentTittle} -p ${currentPlatform} -f ${_OUTPUT_IGT_DIR}/${_OUTPUT_IGT_NAME} -a /tmp/trc/html/" > /home/${dut_user}/pythonCommandTRC.log
            python /home/${_USER}/dev/igt/autouploader/autoUploader.py -s "${currentSuite}" -r "${currentRelease}" -t "${currentTittle}" -p "${currentPlatform}" -f "${_OUTPUT_IGT_DIR}/${_OUTPUT_IGT_NAME}" -a /tmp/trc/html/ 2> /dev/null | tee /tmp/trc.log
            export _TRC_LINK=`cat /tmp/trc2.log`
            echo "${_TRC_LINK}" > /home/${dut_user}/.trc_link

            # making a backup
            cp /tmp/trc.log /home/${dut_user}/ &> /dev/null
            cp /tmp/trc2.log /home/${dut_user}/ &> /dev/null
            cp -R /tmp/trc/ /home/${dut_user}/ &> /dev/null

            if [ "${upload_reports}" = "yes" ]; then

                #############################################################
                # Creating scan folder
                #############################################################
                mkdir -p /tmp/scan/i915
                echo ${_PASSWORD} | sudo -S blkid > /tmp/scan/blkid
                cat /proc/cpuinfo > /tmp/scan/cpuinfo
                echo ${_PASSWORD} | sudo -S dmidecode > /tmp/scan/dmidecode
                echo ${_PASSWORD} | sudo -S fdisk -l > /tmp/scan/fdisk
                lsb_release -a > /tmp/scan/lsb_release
                lsblk > /tmp/scan/lsblk
                echo ${_PASSWORD} | sudo -S lshw > /tmp/scan/lshw
                lspci > /tmp/scan/lspci
                vmstat -s > /tmp/scan/vmstat
                cat /proc/meminfo > /tmp/scan/meminfo
                uname -a > /tmp/scan/uname
                echo ${_PASSWORD} | sudo -S parted -l -s > /tmp/scan/parted
                cat /etc/fstab > /tmp/scan/fstab
                list=`echo ${_PASSWORD} | sudo -S ls /sys/kernel/debug/dri/0/ | grep i915`
                for element in ${list}; do echo ${_PASSWORD} | sudo -S cp /sys/kernel/debug/dri/0/${element} /tmp/scan/i915/ 2> /dev/null; done
                cat /etc/default/grub > /tmp/scan/grub

                # making a backup
                cp -R /tmp/scan/ /home/${dut_user}/ &> /dev/null

                #export PATH_UPLOAD_REPORTS="/var/www/html/reports/intel-gpu-tools/${_WEEKn}/${default_package}/${currentPlatform}/${mDateToday}/${Hour}"
                export PATH_UPLOAD_REPORTS="/var/www/html/reports/intel-gpu-tools/${_YEAR}/${default_package}/${currentPlatform}/${_WEEKn}/${mDateToday}/${Hour}"

                if (timeout 2 ssh -C -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${LINUXGRAPHICS_USER}@${ALIAS_SERVER} '[ -d '${PATH_UPLOAD_REPORTS}' 2> /dev/null ]'); then
                    echo -ne "\n\n"
                    echo -e "${yellow}=========================================================================================================${nc}"
                    echo -e "--> linuxgraphics.intel.com server already has this report for the current ${default_package} execution"
                    echo -ne "${yellow}=========================================================================================================${nc} \n\n"
                else

                    # Uploading reports to linuxgraphics.intel.com

                    # in case that this file was deleted previously due to size limit for TRC
                    if [ ! -f "/tmp/trc/html/dmesg_and_kern_logs.tar.gz" ]; then
                        if [ -f "${_MAIN_PATH}/scripts/dmesg_and_kern_logs.tar.gz" ]; then
                            echo "--> copying dmesg_and_kern_logs.tar.gz to /tmp/trc/html/ folder ..."
                            cp ${_MAIN_PATH}/scripts/dmesg_and_kern_logs.tar.gz /tmp/trc/html/
                        else
                            echo "--> [dmesg_and_kern_logs.tar.gz] does not exists in nowhere ..."
                        fi
                    fi

                    ScanFolder="/tmp/scan/"
                    HTML_FOLDER="/tmp/trc/html"
                    HTML_FOLDER_2="${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/html/${_LAST_ITERATION_FOLDER}/" # Note : all the folders must be in a variable for scp command
                    start_spinner "->> Creating a folder in linuxgraphics.intel.com server ..."
                        sleep .75; ssh "${LINUXGRAPHICS_USER}"@"${ALIAS_SERVER}" "mkdir -p ${PATH_UPLOAD_REPORTS}" &> /dev/null
                    stop_spinner $?
                
                    start_spinner "--> Uploading html folder to linuxgraphics.intel.com ..."
                        sleep .75; scp -o "StrictHostKeyChecking no" -r "${HTML_FOLDER}" "${LINUXGRAPHICS_USER}"@"${ALIAS_SERVER}":"${PATH_UPLOAD_REPORTS}/html/" &> /dev/null
                        sleep .75; scp -o "StrictHostKeyChecking no" -r "${HTML_FOLDER_2}" "${LINUXGRAPHICS_USER}"@"${ALIAS_SERVER}":"${PATH_UPLOAD_REPORTS}/html/" &> /dev/null
                    stop_spinner $?

                    start_spinner "--> Uploading ${_LAST_ITERATION_FOLDER} files to linuxgraphics.intel.com ..."
                        mkdir -p /tmp/upload/; cp -R /tmp/trc/html/* /tmp/upload/; cd /tmp/upload/; rm *.html *.css 2> /dev/null
                        cp ${_OUTPUT_IGT_DIR}/${_OUTPUT_IGT_NAME} /tmp/upload 2> /dev/null
                        sleep .75; scp -o "StrictHostKeyChecking no" -r /tmp/upload/* "${LINUXGRAPHICS_USER}"@"${ALIAS_SERVER}":"${PATH_UPLOAD_REPORTS}" &> /dev/null
                    stop_spinner $?

                    start_spinner "--> Uploading scan folder to linuxgraphics.intel.com ..."
                        sleep .75; scp -o "StrictHostKeyChecking no" -r "${ScanFolder}" "${LINUXGRAPHICS_USER}"@"${ALIAS_SERVER}":"${PATH_UPLOAD_REPORTS}/scan/" &> /dev/null
                        echo
                    stop_spinner $?

                    # creating a file with the link to the backup report in linuxgraphics.intel.com
                    echo "http://linuxgraphics.intel.com/igt-reports/${_YEAR}/${default_package}/${currentPlatform}/${_WEEKn}/${mDateToday}/${Hour}" > /tmp/backupReport.log
                    cp /tmp/backupReport.log /home/${dut_user}/ &> /dev/null
                fi
            fi
        fi


    elif [ ! -z "${_BASIC}" -a "$1" = "not_finish" ]; then
        # Removing empty lines from blacklist file and changing the "/" for "@" from blacklist file
        sed -i '/^\s*$/d' ${_MAIN_PATH}/scripts/blacklist ; sed -i 's|/|@|g' ${_MAIN_PATH}/scripts/blacklist

        # Getting statistics (if this function only need the variable "test_to_run")
        statistics &> /dev/null
        wait

        echo -e "--> Sending email notification ..."
        sleep 2
        _CURRENT_TESTS=$(ls ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/tests | wc -l)
        _CURRENT_PORCENTAGE=$(echo "scale =4; ${_CURRENT_TESTS}*100/${_TEST_TO_RUN}" | bc)
        rm -rf ${_THISPATH}/tools/emailer.py &> /dev/null; cp ${_THISPATH}/tools/emailer.py.bkp ${_THISPATH}/tools/emailer.py

        _LAST_NUMBER_TEST=$(echo ${_LAST_TEST} | tr -d ".json")
        #_IP=$(/sbin/ifconfig | awk '/inet addr/{print substr($2,6)}' | grep -v "^127")
        _IP=`/sbin/ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'`
        # a strange thing here is that the following variable without ssh will contain strange symbols ... () ...
        _LAST_TEST_STATUS=`python '${_THISPATH}'/tools/getResult.py --current 2> /dev/null`

        sed -i '21s/^.*$/receivers = ['$_EMAILER_USER']/g' ${_THISPATH}/tools/emailer.py
        export _EMAILER_USER=`echo "${_EMAILER_USER}" | tr -d "'"`
        sed -i '23s/^.*$/To: '${_EMAILER_USER}'/g' ${_THISPATH}/tools/emailer.py
        # <<Subject>>
        sed -i '24s|^.*$|Subject: intel-gpu-tools basic tests were not completed successfully [iteration'"${_ITERATION_NUMBER}"'] [test : '"${_CURRENT_TESTS}"'/'"${_TEST_TO_RUN}"'] ('"${_CURRENT_PORCENTAGE}"'%) for '${MODEL}'|g' ${_THISPATH}/tools/emailer.py
        # <<Body message>>
        sed -i '26s/^.*$/ Hi : /g' ${_THISPATH}/tools/emailer.py
        sed -i '28s/^.*$/ The last execution of intel-gpu-tools on '"${_IP}"' for ['"${MODEL}"']  Hostname ['"${HOSTNAME}"'] was not successful, please find the details below./g' ${_THISPATH}/tools/emailer.py
        sed -i '29s/^.*$/ the test that caused issues with the execution was../g' ${_THISPATH}/tools/emailer.py
        sed -i '30s/^.*$/ --> test name                  : '"${_LAST_TEST_NAME}"'/g' ${_THISPATH}/tools/emailer.py
        sed -i '31s/^.*$/ --> test number              : '"${_LAST_NUMBER_TEST}"'/g' ${_THISPATH}/tools/emailer.py
        sed -i '32s/^.*$/ --> test status                  : '"${_LAST_TEST_STATUS}"'/g' ${_THISPATH}/tools/emailer.py
        sed -i '33s/^.*$/ --> last iteration              : ['"${_ITERATION_NUMBER}"']/g' ${_THISPATH}/tools/emailer.py
        sed -i '34s|^.*$| --> current progress      : '"${_CURRENT_TESTS}"'/'"${_TEST_TO_RUN}"' ('"${_CURRENT_PORCENTAGE}"'%)|g' ${_THISPATH}/tools/emailer.py
        sed -i '36s/^.*$/ intel-gpu-tools will resume automatically the execution./g' ${_THISPATH}/tools/emailer.py
        sed -i '37s/^.*$/ Intel Graphics for Linux* | 01.org./g' ${_THISPATH}/tools/emailer.py
        sed -i '38s/^.*$/ This is an automated message please do not reply/g' ${_THISPATH}/tools/emailer.py
        
        sleep .5
        python ${_THISPATH}/tools/emailer.py; wait
        rm ${_THISPATH}/tools/emailer.py &> /dev/null

    elif [ -z "${_BASIC}" -a "$1" = "finish" ]; then
        
        ##############################################################
        # Compress the attachments                                   #
        ##############################################################
        echo ${_PASSWORD} | sudo -S ls &> /dev/null; sleep .5
        echo ${_PASSWORD} | sudo -S rm -rf /tmp/* &> /dev/null
        export _LAST_ITERATION_FOLDER="iteration1"
        mkdir -p /tmp/trc/html
        outputFolders="/tmp/trc/html /tmp/${_LAST_ITERATION_FOLDER}/"
        Message="Please find this report as well in http://linuxgraphics.intel.com/igt-reports/${_YEAR}/${default_package}/${currentPlatform}/${_WEEKn}/${mDateToday}/${Hour}"
        export _OUTPUT_IGT_DIR="/home/${_USER}/Desktop/results/intel-gpu-tools"
        export _OUTPUT_IGT_NAME="${default_package}_${dut_hostname}_TRC_summary_${_WEEKn}_${_HOUR}.csv"
        if [ "${igt_iterations}" -gt 1 ]; then blacklistFile="${_MAIN_PATH}/scripts/blacklist.1"; elif [ "${igt_iterations}" -eq 1 ]; then blacklistFile="${_MAIN_PATH}/scripts/blacklist"; fi

        
        if [ "${trc_report}" = "yes" ]; then
            echo -ne "${yellow}-->${nc} Uploading results to TRC [${currentEnv}] ... \n\n"
            # Folder for upload to TRC
            cp ${_MAIN_PATH}/scripts/dmesg_and_kern_logs.tar.gz  /tmp/trc/html 2> /dev/null
            cp ${_OUTPUT_DIR}/${_OUTPUT_NAME_BACKTRACE} /tmp/trc/html 2> /dev/null
            cp -r ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/html/ /tmp/trc/
            rm -rf /tmp/trc/html/${_LAST_ITERATION_FOLDER}
            cp /home/custom/config.cfg /tmp/trc/html/dutConfig.cfg
            cp /home/custom/config.yml /tmp/trc/html/dutConfig.yml
            cp /home/custom/kernel/packages/commit_info /tmp/trc/html/kernel_commit_information.cfg
            cp /home/custom/graphic_stack/packages/config.cfg /tmp/trc/html/gfx_stack.cfg
            cp /home/custom/*specs.cfg /tmp/trc/html/ 2> /dev/null
            cp /home/custom/graphic_stack/packages/easy-bugs /tmp/trc/html/gfx_stack_easy_bugs.cfg
            cp ${blacklistFile} /tmp/trc/html/blacklist.cfg 2> /dev/null
            cp ${_MAIN_PATH}/scripts/iteration1/results.json /tmp/trc/html/ 2> /dev/null
            cp ${_OUTPUT_DIR}/*runtime* /tmp/trc/html 2> /dev/null

            #################################################################################################################
            # Compress results.json in order to upload it to TRC (rule is if the file is less than 20MB it will be uploaded)
            cd /tmp/trc/html/; tar cvzf results.json.tar.gz /tmp/trc/html/results.json; rm results.json 2> /dev/null
            # Checking if the file size meet with the rule
            resultsJsonSize=`du -s /tmp/results.json.tar.gz | awk '{print $1}'`
            ruleSize=10000
            if [ ${resultsJsonSize} -gt ${ruleSize} ];then
                echo "--> results.json.tar.gz weight (${resultsJsonSize}) is not allowed, removing it ..."
                rm /tmp/results.json.tar.gz 2> /dev/null
            fi
            # Checking dmesg size
            dmesgSize=`du -s /tmp/trc/html/dmesg_and_kern_logs.tar.gz | awk '{print $1}'`
            #ruleSize=10000
            #if [ ${dmesgSize} -gt ${ruleSize} ];then
            #    echo "--> dmesg_and_kern_logs.tar.gz weight (${dmesgSize}) is not allowed in TRC, removing it ..."
            #    rm /tmp/trc/html/dmesg_and_kern_logs.tar.gz 2> /dev/null
            #fi

            # size to check :10M
            if [[ $(find /tmp/trc/html/dmesg_and_kern_logs.tar.gz -type f -size +10485760c 2>/dev/null) ]]; then
                echo "--> dmesg_and_kern_logs.tar.gz weight (${dmesgSize}) is not allowed in TRC, removing it ..."
                rm /tmp/trc/html/dmesg_and_kern_logs.tar.gz 2> /dev/null
            fi
            #################################################################################################################
            echo ${_PASSWORD} | sudo -S cat /sys/kernel/debug/dri/0/i915_display_info > /tmp/trc/html/attachedDisplays.cfg
            if [ "${upload_reports}" = "yes" ]; then echo ${Message} > /tmp/trc/html/BackupReport.cfg; fi
            echo "python /home/${_USER}/dev/igt/autouploader/autoUploader.py -s ${currentSuite} -r ${currentRelease} -t ${currentTittle} -p ${currentPlatform} -f ${_OUTPUT_IGT_DIR}/${_OUTPUT_IGT_NAME} -a /tmp/trc/html/" > /home/${dut_user}/pythonCommandTRC.log
            python /home/${_USER}/dev/igt/autouploader/autoUploader.py -s "${currentSuite}" -r "${currentRelease}" -t "${currentTittle}" -p "${currentPlatform}" -f "${_OUTPUT_IGT_DIR}/${_OUTPUT_IGT_NAME}" -a /tmp/trc/html/ 2> /dev/null | tee /tmp/trc.log
            export _TRC_LINK=`cat /tmp/trc2.log`
            echo "${_TRC_LINK}" > /home/${dut_user}/.trc_link

            # making a backup
            cp /tmp/trc.log /home/${dut_user}/ &> /dev/null
            cp /tmp/trc2.log /home/${dut_user}/ &> /dev/null
            cp -R /tmp/trc/ /home/${dut_user}/ &> /dev/null

            if [ "${upload_reports}" = "yes" ]; then

                #############################################################
                # Creating scan folder
                #############################################################
                mkdir -p /tmp/scan/i915
                echo ${_PASSWORD} | sudo -S blkid > /tmp/scan/blkid
                cat /proc/cpuinfo > /tmp/scan/cpuinfo
                echo ${_PASSWORD} | sudo -S dmidecode > /tmp/scan/dmidecode
                echo ${_PASSWORD} | sudo -S fdisk -l > /tmp/scan/fdisk
                lsb_release -a > /tmp/scan/lsb_release
                lsblk > /tmp/scan/lsblk
                echo ${_PASSWORD} | sudo -S lshw > /tmp/scan/lshw
                lspci > /tmp/scan/lspci
                vmstat -s > /tmp/scan/vmstat
                cat /proc/meminfo > /tmp/scan/meminfo
                uname -a > /tmp/scan/uname
                echo ${_PASSWORD} | sudo -S parted -l -s > /tmp/scan/parted
                cat /etc/fstab > /tmp/scan/fstab
                list=`echo ${_PASSWORD} | sudo -S ls /sys/kernel/debug/dri/0/ | grep i915`
                for element in ${list}; do echo ${_PASSWORD} | sudo -S cp /sys/kernel/debug/dri/0/${element} /tmp/scan/i915/ 2> /dev/null; done
                cat /etc/default/grub > /tmp/scan/grub

                # making a backup
                cp -R /tmp/scan/ /home/${dut_user}/ &> /dev/null

                #export PATH_UPLOAD_REPORTS="/var/www/html/reports/intel-gpu-tools/${_WEEKn}/${default_package}/${currentPlatform}/${mDateToday}/${Hour}"
                export PATH_UPLOAD_REPORTS="/var/www/html/reports/intel-gpu-tools/${_YEAR}/${default_package}/${currentPlatform}/${_WEEKn}/${mDateToday}/${Hour}"

                if (timeout 2 ssh -C -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${LINUXGRAPHICS_USER}@${ALIAS_SERVER} '[ -d '${PATH_UPLOAD_REPORTS}' 2> /dev/null ]'); then
                    echo -ne "\n\n"
                    echo -e "${yellow}=========================================================================================================${nc}"
                    echo -e "--> linuxgraphics.intel.com server already has this report for the current ${default_package} execution"
                    echo -ne "${yellow}=========================================================================================================${nc} \n\n"
                else

                    # Uploading reports to linuxgraphics.intel.com

                    # in case that this file was deleted previously due to size limit for TRC
                    if [ ! -f "/tmp/trc/html/dmesg_and_kern_logs.tar.gz" ]; then
                        if [ -f "${_MAIN_PATH}/scripts/dmesg_and_kern_logs.tar.gz" ]; then
                            echo "--> copying dmesg_and_kern_logs.tar.gz to /tmp/trc/html/ folder ..."
                            cp ${_MAIN_PATH}/scripts/dmesg_and_kern_logs.tar.gz /tmp/trc/html/
                        else
                            echo "--> [dmesg_and_kern_logs.tar.gz] does not exists in nowhere ..."
                        fi
                    fi

                    ScanFolder="/tmp/scan/"
                    HTML_FOLDER="/tmp/trc/html"
                    HTML_FOLDER_2="${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/html/${_LAST_ITERATION_FOLDER}/"
                    start_spinner "--> Creating a folder in linuxgraphics.intel.com server ..."
                        sleep .75; ssh "${LINUXGRAPHICS_USER}"@"${ALIAS_SERVER}" "mkdir -p ${PATH_UPLOAD_REPORTS}" &> /dev/null
                    stop_spinner $?
                
                    start_spinner "--> Uploading html folder to linuxgraphics.intel.com ..."
                        sleep .75; scp -o "StrictHostKeyChecking no" -r "${HTML_FOLDER}" "${LINUXGRAPHICS_USER}"@"${ALIAS_SERVER}":"${PATH_UPLOAD_REPORTS}/html/" &> /dev/null
                        sleep .75; scp -o "StrictHostKeyChecking no" -r "${HTML_FOLDER_2}" "${LINUXGRAPHICS_USER}"@"${ALIAS_SERVER}":"${PATH_UPLOAD_REPORTS}/html/" &> /dev/null
                    stop_spinner $?

                    start_spinner "--> Uploading ${_LAST_ITERATION_FOLDER} files to linuxgraphics.intel.com ..."
                        mkdir -p /tmp/upload/; cp -R /tmp/trc/html/* /tmp/upload/; cd /tmp/upload/; rm *.html *.css 2> /dev/null
                        cp ${_OUTPUT_IGT_DIR}/${_OUTPUT_IGT_NAME} /tmp/upload 2> /dev/null
                        sleep .75; scp -o "StrictHostKeyChecking no" -r /tmp/upload/* "${LINUXGRAPHICS_USER}"@"${ALIAS_SERVER}":"${PATH_UPLOAD_REPORTS}" &> /dev/null
                    stop_spinner $?

                    start_spinner "--> Uploading scan folder to linuxgraphics.intel.com ..."
                        sleep .75; scp -o "StrictHostKeyChecking no" -r "${ScanFolder}" "${LINUXGRAPHICS_USER}"@"${ALIAS_SERVER}":"${PATH_UPLOAD_REPORTS}/scan/" &> /dev/null
                        echo
                    stop_spinner $?

                    # creating a file with the link to the backup report in linuxgraphics.intel.com
                    echo "http://linuxgraphics.intel.com/igt-reports/${_YEAR}/${default_package}/${currentPlatform}/${_WEEKn}/${mDateToday}/${Hour}" > /tmp/backupReport.log

                    cp /tmp/backupReport.log /home/${dut_user}/ &> /dev/null
                fi
            fi


        fi


    elif [ -z "${_BASIC}" -a "$1" = "not_finish" ]; then

        # Removing empty lines from blacklist file and changing the "/" for "@" from blacklist file
        sed -i '/^\s*$/d' ${_MAIN_PATH}/scripts/blacklist ; sed -i 's|/|@|g' ${_MAIN_PATH}/scripts/blacklist

        # Getting statistics (if this function only need the variable "test_to_run")
        statistics &> /dev/null
        wait

        echo -e "--> Sending email notification ..."
        sleep 2
        _CURRENT_TESTS=$(ls ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/tests | wc -l)
        _CURRENT_PORCENTAGE=$(echo "scale =4; ${_CURRENT_TESTS}*100/${_TEST_TO_RUN}" | bc)
        rm -rf ${_THISPATH}/tools/emailer.py &> /dev/null; cp ${_THISPATH}/tools/emailer.py.bkp ${_THISPATH}/tools/emailer.py

        _LAST_NUMBER_TEST=$(echo ${_LAST_TEST} | tr -d ".json")
        #_IP=$(/sbin/ifconfig | awk '/inet addr/{print substr($2,6)}' | grep -v "^127")
        _IP=`/sbin/ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'`
        # a courios thing here is that the following variable without ssh will contain strange symbols ... () ...
        _LAST_TEST_STATUS=`python ${_THISPATH}/tools/getResult.py --current 2> /dev/null`

        sed -i '21s/^.*$/receivers = ['$_EMAILER_USER']/g' ${_THISPATH}/tools/emailer.py
        export _EMAILER_USER=`echo "${_EMAILER_USER}" | tr -d "'"`
        sed -i '23s/^.*$/To: '${_EMAILER_USER}'/g' ${_THISPATH}/tools/emailer.py
        # <<Subject>>
        sed -i '24s|^.*$|Subject: intel-gpu-tools tests were not completed successfully [iteration'"${_ITERATION_NUMBER}"'] [test : '"${_CURRENT_TESTS}"'/'"${_TEST_TO_RUN}"'] ('"${_CURRENT_PORCENTAGE}"'%) for ['${MODEL}'] |g' ${_THISPATH}/tools/emailer.py
        # <<Body message>>
        sed -i '26s/^.*$/ Hi : /g' ${_THISPATH}/tools/emailer.py
        sed -i '28s/^.*$/ The last execution of intel-gpu-tools on '"${_IP}"' ['"${MODEL}"'] was not successful, please find the details below./g' ${_THISPATH}/tools/emailer.py
        sed -i '29s/^.*$/ the test that caused issues with the execution was../g' ${_THISPATH}/tools/emailer.py
        sed -i '30s/^.*$/ --> test name                  : '"${_LAST_TEST_NAME}"'/g' ${_THISPATH}/tools/emailer.py
        sed -i '31s/^.*$/ --> test number              : '"${_LAST_NUMBER_TEST}"'/g' ${_THISPATH}/tools/emailer.py
        sed -i '32s/^.*$/ --> test status                  : '"${_LAST_TEST_STATUS}"'/g' ${_THISPATH}/tools/emailer.py
        sed -i '33s/^.*$/ --> last iteration              : ['"${_ITERATION_NUMBER}"']/g' ${_THISPATH}/tools/emailer.py
        sed -i '34s|^.*$| --> current progress      : '"${_CURRENT_TESTS}"'/'"${_TEST_TO_RUN}"' ('"${_CURRENT_PORCENTAGE}"'%)|g' ${_THISPATH}/tools/emailer.py
        sed -i '36s/^.*$/ intel-gpu-tools will resume automatically the execution./g' ${_THISPATH}/tools/emailer.py
        sed -i '37s/^.*$/ Intel Graphics for Linux* | 01.org./g' ${_THISPATH}/tools/emailer.py
        sed -i '38s/^.*$/ This is an automated message please do not reply/g' ${_THISPATH}/tools/emailer.py
        
        sleep .5
        python ${_THISPATH}/tools/emailer.py; wait
        rm ${_THISPATH}/tools/emailer.py &> /dev/null

    fi
}

function check_igt_iterations () {

    Folder="${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}"


    if [ -f "${Folder}/results.json.bz2" -a -d "${Folder}/html" -a ! -f "${Folder}/.control" ]; then
        touch ${Folder}/.control

        if [ "${igt_iterations}" = "${_ITERATION_NUMBER}" ]; then 
            echo -ne "\n\n"
            echo -e "${green}=================================================${nc}"
            echo -e " == ${blue}the (${igt_iterations}) campains has been finished${nc} == "
            echo -e "${green}=================================================${nc}"
        else

            # Changing permissions as WA
            start_spinner "--> Changing owner for ${_LAST_ITERATION_FOLDER} to ${_USER} ..."
                echo ${_PASSWORD} | sudo -S ls &> /dev/null; sleep .75
                echo ${_PASSWORD} | sudo -S chown -R ${_USER}:${_USER} ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER} &> /dev/null
            stop_spinner $?

            # Checking if the last results.json has some failure like : fail,crash,timeout,incomplete,dmesg_fail

            bzip2 -d ${Folder}/results.json.bz2
            buzipFile="${Folder}/results.json"

            validateNextCampaign=`python ${_MAIN_PATH}/scripts/getResult.py --getjsonstatistics ${buzipFile} 'check_failures' 'None'` # returns True or False

            if [ "${validateNextCampaign}" = "True" ]; then 
                echo -ne "\n --> ${yellow}The last results.json from (${_LAST_ITERATION_FOLDER}) has some failures to run${nc} \n"

                rm -rf ${Folder}/IGT_run* 2> /dev/null
                NextIteration=$((_ITERATION_NUMBER +1))

                # Generating a new blacklist
                mv ${_MAIN_PATH}/scripts/blacklist ${_MAIN_PATH}/scripts/blacklist.${_ITERATION_NUMBER}
                echo "${NextIteration}" > ${_MAIN_PATH}/scripts/.current_iteration
                #bzip2 -d ${Folder}/results.json.bz2

                start_spinner "--> Generating news blacklist & IGT_run files with the failed ones ..."
                    sleep .75; python ${_MAIN_PATH}/scripts/getResult.py --totalfails ${Folder}/results.json ${NextIteration}
                stop_spinner $?

                start_spinner "--> Restarting the DUT in order to run the iteration (${NextIteration}) ..."
                    sleep 5; sudo reboot
                stop_spinner $?

            elif [ "${validateNextCampaign}" = "False" ]; then
                echo -ne "--> ${yellow}You are setup (${igt_iterations}) campaigns, but the last results.json from (${_LAST_ITERATION_FOLDER}) has not failures \n\n"
                sleep 5 | pv
            fi
        fi

    elif [ -f "${Folder}/.control" ]; then
        echo -ne "\n\n"
        echo ">> the (${igt_iterations}) campains has been finished <<"
    fi
}


function check_last_iteration () {

    if [ ! -f "/home/${_USER}/.model" ]; then

        start_spinner "--> Getting Platform MODEL ..."
            echo ${_PASSWORD} | sudo -S ls &> /dev/null; sleep .5
            export typem=$(echo ${_PASSWORD} | sudo -S dmidecode -t 2 | grep "Product Name" | awk -F": " '{print $2}' | sed 's/ //g') # this is the type of motherboard 

            case "${typem}" in 
                "BRASWELL") export MODEL="BSW" ;;
                "LenovoG50-80"|"NUC5i7RYB"| "NUC5i5MYBE") export MODEL="BDW" ;;
                "06D7TR") export MODEL="SNB" ;;
                "0XR1GT") export MODEL="IVB" ;;
                "02HK88") export MODEL="SKL" ;;
                "NOTEBOOK") export MODEL="BXT-P" ;;
                "SkylakeYLPDDR3RVP3") export MODEL="SKL-Y to KBL (RVP3)" ;;
                "SkylakeUDDR3LRVP7") export MODEL="KBL (RVP7)" ;;
                "PortablePC") export MODEL="BYT-M (Toshiba)" ;;
                "1589") export MODEL="HP Z420 Workstation" ;;
                "D54250WYK") export MODEL="HSW-Nuc" ;;
                "NUC6i5SYB") export MODEL="SKL-Nuc" ;;
                "NUC5i5RYB") export MODEL="BDW-Nuc" ;;
                "NUC6i7KYB") export MODEL="SKL Canyon" ;;
                "MS-B1421") export MODEL="KBL-Nuc" ;;
                "GLKRVP1DDR4(05)") export MODEL="Geminilake" ;;
                "18F8") export MODEL="IVB" ;;
            esac

            echo "${MODEL}" > /home/${_USER}/.model
        stop_spinner $?

    fi

    export MODEL=`cat /home/${_USER}/.model`

    # Checking if the last iteration was successfully
    # export _LAST_ITERATION_FOLDER=$(ls -tr ${_MAIN_PATH}/scripts/ | grep iteration | tail -1)
    export _LAST_ITERATION_FOLDER=`ls ${_MAIN_PATH}/scripts/ | grep "^iteration" | sort -n | tail -1`
    export _ITERATION_NUMBER=$(echo ${_LAST_ITERATION_FOLDER} | sed 's/iteration//g')

    if [ -d "${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/tests" ]; then
        # this means not
        export IterationStatus="1"
        # changing the permission of the last iteration folder
        _CHECK_FOR_ROOT=$(ls -ld ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER} | awk '{print $3}')
        if [ "${_CHECK_FOR_ROOT}" = "root" ]; then
            echo -ne "\n\n"
            start_spinner "--> Changing owner for ${_LAST_ITERATION_FOLDER} to ${_USER} ..."
                echo ${_PASSWORD} | sudo -S ls &> /dev/null; sleep 2
                echo ${_PASSWORD} | sudo -S chown -R ${_USER}:${_USER} ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER} &> /dev/null
            stop_spinner $?
        fi

        echo -e "--> The last execution (${yellow}${_LAST_ITERATION_FOLDER}${nc}) was not successfully"
            export _LAST_TEST=$(ls -tr ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/tests | tail -1) # json file
            export _LAST_TEST_NAME=$(cat ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/tests/${_LAST_TEST} 2> /dev/null | awk -F ":" '{print $1}' | sed -e 's/{"igt@//g' -e 's/"//g')
            export _LAST_TEST_STATUS=$(cat ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/tests/${_LAST_TEST} 2> /dev/null | awk -F ":" '{print $6}' | awk '{print $1}' | sed -e 's/",//g' -e 's/"//g')

        # Cheking if the incomplete_tests is already created and checking if the tests is already in the file
        if [ -f "${_MAIN_PATH}/scripts/incomplete_tests" ]; then
            _CHECK_LAST_TEST=$(cat ${_MAIN_PATH}/scripts/incomplete_tests | grep -w "${_LAST_TEST_NAME}")
        fi

        if [ "${_LAST_TEST_STATUS}" = "incomplete" ] && [ -z "${_CHECK_LAST_TEST}" ]; then
            # Sending the incomplete test to a file
            start_spinner "--> adding ${_LAST_TEST_NAME} to incomplete_tests file ..."
                sleep .5; echo "${_LAST_TEST_NAME}" >> ${_MAIN_PATH}/scripts/incomplete_tests
            stop_spinner $?
        fi


        _LAST_IGT_RUN_FILE=$(ls ${_MAIN_PATH}/scripts/ | grep "^IGT_run" | sort -n | tail -1)
        _CURRENT_IGT_RUN_NUMBER=$(echo ${_LAST_IGT_RUN_FILE} | sed 's/IGT_run//g')

        if [ "${default_package}" != "igt_extended_list" ]; then

            start_spinner "--> adding -n & -R options to (IGT_run${_CURRENT_IGT_RUN_NUMBER}) ..."
                sleep .5
                # Generating a new IGT_run file
                _NEXT_IGT_NUMBER=$(( _CURRENT_IGT_RUN_NUMBER + 1 ))
                _VAR_NOT_RUN=`cat ${_MAIN_PATH}/scripts/.not_run_tests 2> /dev/null` # this are the tests that will not run
                _VAR_RUN=`cat ${_MAIN_PATH}/scripts/.only_test_to_run 2> /dev/null` # this are the tests that will run
                # Deleting the current IGT_runX in order to add -n and -R option to continue testing
                echo -ne "bash ${_MAIN_PATH}/scripts/run-tests.sh -n -R -s -r ${_MAIN_PATH}/scripts/iteration${_ITERATION_NUMBER} ${_VAR_NOT_RUN} ${_VAR_RUN}" > ${_MAIN_PATH}/scripts/IGT_run${_CURRENT_IGT_RUN_NUMBER}
                chmod 775 ${_MAIN_PATH}/scripts/IGT_run${_CURRENT_IGT_RUN_NUMBER} &> /dev/null
            stop_spinner $?

        else
            echo "--> Default package is (${default_package})"
            start_spinner "--> adding -n & -R options to (IGT_run${_CURRENT_IGT_RUN_NUMBER}) ..."
                echo -ne "bash ${_MAIN_PATH}/scripts/run-tests.sh -n -R -s -r ${_MAIN_PATH}/scripts/iteration${_ITERATION_NUMBER} -T ${_MAIN_PATH}/tests/intel-ci/extended.testlist" > ${_MAIN_PATH}/scripts/IGT_run${_CURRENT_IGT_RUN_NUMBER}
                chmod 775 ${_MAIN_PATH}/scripts/IGT_run${_CURRENT_IGT_RUN_NUMBER} &> /dev/null
            stop_spinner $?
        fi

        # Sending a email to notify that the last IGT was not successfully
        # ================================================================

        if [ "$_CONNECTION" = "INTRANET" ]; then email_template "not_finish"; fi

    elif [ ! -d "${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/tests" ] && [ -f "${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/results.json.bz2" ] && [ ! -f "${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/.igt_done" ]; then

        ##################################################################################################################
        #if [ "${igt_iterations}" = "2" ]; then check_igt_iterations; fi
        if [ ! -z "${igt_iterations}" ]; then check_igt_iterations; fi
        ##################################################################################################################

        # this means that IGT has finished
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne "  ${green}===============================${nc} \n"
        echo -ne "  ${green}intel-gpu-tools has finished${nc} \n"
        echo -ne "  ${green}===============================${nc} \n\n"

        # Changing the permission as WA
        start_spinner "--> Changing owner for ${_LAST_ITERATION_FOLDER} to ${_USER} ..."
            echo ${_PASSWORD} | sudo -S ls &> /dev/null; sleep 2
            echo ${_PASSWORD} | sudo -S chown -R ${_USER}:${_USER} ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER} &> /dev/null
        stop_spinner $?


        # =================================================
        # Generating the dmesg for the full igt execution #
        # =================================================
        echo -e "--> Generating full dmesg for the whole igt execution ..."
        export dName="dmesg_and_kern_logs_hostname_${dut_hostname}_gfxStackCode_${gfx_stack_code}_kernelBranch_${kernel_branch}_kernelCommit_${kernel_commit}"
        mkdir -p ${_MAIN_PATH}/scripts/${dName}
        CheckDmesgInfo "${_MAIN_PATH}/scripts/${dName}"
        dmesg > ${_MAIN_PATH}/scripts/${dName}/dmesg.log
        cp /var/log/kern.log ${_MAIN_PATH}/scripts/${dName}/
        # Compress at maximum the dmesg in order to upload it to TRC
        export GZIP=-9
        #cd ${_MAIN_PATH}/scripts/; tar -zcf dmesg_and_kern_logs.tar.gz ./${dName}; rm -rf ${_MAIN_PATH}/scripts/${dName}/
        cd ${_MAIN_PATH}/scripts/; tar czf dmesg_and_kern_logs.tar.gz ./${dName}; rm -rf ${_MAIN_PATH}/scripts/${dName}/ 2> /dev/null
        
        rm -rf ${_MAIN_PATH}/scripts/${dName}/kern.log 2> /dev/null
        


        #if [ "${default_package}" = "igt_extended_list" ]; then
        #    start_spinner "--> Generating html files with piglit ..."
        #        mkdir -p ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/html
        #        cp ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/results.json.bz2 ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/html/
        #        python ${_MAIN_PATH}/piglit/piglit summary html ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/html ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/html #2> /dev/null
        #        rm ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/html/results.json.bz2
        #    stop_spinner $?
        #fi

        #start_spinner "--> Generating a csv file with piglit ..."
            #echo ${_PASSWORD} | sudo -S ls &> /dev/null; sleep .5
            # Changing the permissions of the last iteration folder
            #echo ${_PASSWORD} | sudo -S chown -R ${_USER}:${_USER} ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}
            # Generating a csv file from results.json.bz2
            #_OUTPUT_DIR="/home/${_USER}/Desktop/results/intel-gpu-tools"
            #_OUTPUT_NAME="${default_package}_${dut_hostname}_TRC_summary_${_WEEKn}_${_HOUR}.csv"
            #mkdir -p ${_OUTPUT_DIR} &> /dev/null
            #${_MAIN_PATH}/piglit/piglit summary csv ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/results.json.bz2 | tee ${_OUTPUT_DIR}/${_OUTPUT_NAME} &> /dev/null
        #stop_spinner $?

        export _OUTPUT_DIR="/home/${_USER}/Desktop/results/intel-gpu-tools"
        export _OUTPUT_NAME="${default_package}_${dut_hostname}_TRC_summary_${_WEEKn}_${_HOUR}.csv"
        export _OUTPUT_NAME_BACKTRACE="${default_package}_${dut_hostname}_backtrace_${_WEEKn}_${_HOUR}.xls"
        export _OUTPUT_NAME_RUNTIME="${default_package}_${dut_hostname}_runtime_${_WEEKn}_${_HOUR}.csv"
        mkdir -p ${_OUTPUT_DIR} &> /dev/null

        bzipFile="${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/results.json.bz2"

        if [ -f "${bzipFile}" ]; then bzip2 -d ${bzipFile}; fi

        #buzipFile="${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/results.json"
        buzipFile="${_MAIN_PATH}/scripts/iteration1/results.json"

        start_spinner "--> Merging all json files ..."
            sleep .75; python ${_MAIN_PATH}/scripts/getResult.py --getjsonfiles
        stop_spinner $?
        
        start_spinner "--> Generating generic csv file for TRC ..."
            sleep .75 ; python ${_MAIN_PATH}/scripts/getResult.py --csvreport ${buzipFile} ${_OUTPUT_DIR}/${_OUTPUT_NAME}
        stop_spinner $?

        start_spinner "--> Generating xls backtrace file"
            sleep .75 ; python ${_MAIN_PATH}/scripts/getResult.py --backtraceReport ${buzipFile} ${_OUTPUT_DIR}/${_OUTPUT_NAME_BACKTRACE}
        stop_spinner $?
        
        start_spinner "--> Generating runtime files"
            sleep .75 ; python ${_MAIN_PATH}/scripts/getResult.py --runtime ${buzipFile} ${_OUTPUT_DIR}/${_OUTPUT_NAME_RUNTIME}
        stop_spinner $?

        
        start_spinner "--> Adding bugs to csv file from API ..."
            sleep .75; python ${_MAIN_PATH}/scripts/getResult.py --updatecsv ${_OUTPUT_DIR}/${_OUTPUT_NAME} ${currentPlatform} ${_OUTPUT_DIR}
        stop_spinner $?

        # Renaming the final csv file (with bugs)
        if [ -f "${_OUTPUT_DIR}/tmp.csv" ]; then
            rm -rf ${_OUTPUT_DIR}/${_OUTPUT_NAME} 2> /dev/null
            mv ${_OUTPUT_DIR}/tmp.csv ${_OUTPUT_DIR}/${_OUTPUT_NAME} 2> /dev/null
        fi

        #start_spinner "--> Converting the csv file generated to TRC format ..."
    
            #echo "COMPONENT,NAME,STATUS,BUG,COMMENT" > ${_OUTPUT_DIR}/tmp.csv
            #while read line
            #do
                #_TEST_NAME=$(echo $line | awk -F"," '{print $1}' | sed 's/igt@//g')
                #_TEST_RESULT=$(echo $line | awk -F"," '{print $4}')

                #case ${_TEST_RESULT} in 
                    #pass) echo "igt,igt@${_TEST_NAME},pass,,,"                                        >> ${_OUTPUT_DIR}/tmp.csv ;;
                    #fail) echo "igt,igt@${_TEST_NAME},fail,,this test was fail,,,"                    >> ${_OUTPUT_DIR}/tmp.csv ;;
                    #crash) echo "igt,igt@${_TEST_NAME},fail,,this test was crash,,,"                  >> ${_OUTPUT_DIR}/tmp.csv ;;
                    #skip) echo "igt,igt@${_TEST_NAME},not run,,this test was skipped,,,"              >> ${_OUTPUT_DIR}/tmp.csv ;;
                    #timeout) echo "igt,igt@${_TEST_NAME},not run,,this test was timeout,,,"           >> ${_OUTPUT_DIR}/tmp.csv ;;
                    #incomplete) echo "igt,igt@${_TEST_NAME},not run,,this test was incomplete,,,"     >> ${_OUTPUT_DIR}/tmp.csv ;;
                    #dmesg-warn) echo "igt,igt@${_TEST_NAME},pass,,this test was dmesg-warn,,,"        >> ${_OUTPUT_DIR}/tmp.csv ;;
                    #warn) echo "igt,igt@${_TEST_NAME},pass,,this test was warn,,,"                    >> ${_OUTPUT_DIR}/tmp.csv ;;
                    #dmesg-fail) echo "igt,igt@${_TEST_NAME},fail,,this test was dmesg-fail,,,"        >> ${_OUTPUT_DIR}/tmp.csv ;;
                #esac
            #done < ${_OUTPUT_DIR}/${_OUTPUT_NAME}
        #stop_spinner $?

        # Renanming tmp.csv file
        #rm ${_OUTPUT_DIR}/${_OUTPUT_NAME} &> /dev/null; mv ${_OUTPUT_DIR}/tmp.csv ${_OUTPUT_DIR}/${_OUTPUT_NAME} &> /dev/null

        # Creating a control file in order to NOT run the next time because is supposed that IGT has finished
        touch ${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/.igt_done

        # Get statistics from json file
        jsonFinalFile="${_MAIN_PATH}/scripts/iteration1/results.json" 
        python ${_MAIN_PATH}/scripts/getResult.py --getjsonstatistics ${jsonFinalFile} "all" "none"

        # Showing statistics
        #export _SUMMARY_FILE="${_OUTPUT_DIR}/${_OUTPUT_NAME}"
        #export _TT=$(cat ${_SUMMARY_FILE} | grep -v "COMPONENT" | wc -l)
        #export _TT_FOR_PASS_RATE=$(cat ${_SUMMARY_FILE} | grep -ve "COMPONENT" -ve "this test was skipped" | wc -l) # this does not contain the sk_IP tests
        #export _PT=$(cat ${_SUMMARY_FILE} | grep -w "pass" | grep -ve "this test was dmesg-warn" -ve "this test was warn" |wc -l)
        #export _FT=$(cat ${_SUMMARY_FILE} | grep -w "this test was fail" | wc -l)
        #export _CT=$(cat ${_SUMMARY_FILE} | grep -w "this test was crash" | wc -l)
        #export _ST=$(cat ${_SUMMARY_FILE} | grep -w "this test was skipped" | wc -l)
        #export _TOT=$(cat ${_SUMMARY_FILE} | grep -w "this test was timeout" | wc -l)
        #export _IT=$(cat ${_SUMMARY_FILE} | grep -w "this test was incomplete" | wc -l)
        #export _DWT=$(cat ${_SUMMARY_FILE} | grep -w "this test was dmesg-warn" | wc -l)
        #export _WT=$(cat ${_SUMMARY_FILE} | grep -w "this test was warn" | wc -l)
        #export _DFT=$(cat ${_SUMMARY_FILE} | grep -w "this test was dmesg-fail" | wc -l)
        #export _FOR_PASS_RATE=$(( _WT + _DWT + _PT ))
        #export _PASSRATE=$(echo "scale =2; ${_FOR_PASS_RATE}*100/${_TT_FOR_PASS_RATE}" | bc)

        #echo -ne "\n\n"
        #echo -ne " |=== IGT Summary ===| \n\n"                                   | tee ${_OUTPUT_DIR}/summary_Ww${_WEEKn}-${_HOUR}
        #echo -ne " -- Total tests       : (${cyan}${_TT}${nc}) \n"               | tee -a ${_OUTPUT_DIR}/summary_Ww${_WEEKn}-${_HOUR}
        #echo -ne " -- Passed tests      : (${green}${_PT}${nc}) \n"              | tee -a ${_OUTPUT_DIR}/summary_Ww${_WEEKn}-${_HOUR}
        #echo -ne " -- Failed tests      : (${red}${_FT}${nc}) \n"                | tee -a ${_OUTPUT_DIR}/summary_Ww${_WEEKn}-${_HOUR}
        #echo -ne " -- Crash tests       : (${yellow}${_CT}${nc}) \n"             | tee -a ${_OUTPUT_DIR}/summary_Ww${_WEEKn}-${_HOUR}
        #echo -ne " -- Skipped tests     : (${_ST}) \n"                           | tee -a ${_OUTPUT_DIR}/summary_Ww${_WEEKn}-${_HOUR}
        #echo -ne " -- Timeout tests     : (${_TOT}) \n"                          | tee -a ${_OUTPUT_DIR}/summary_Ww${_WEEKn}-${_HOUR}
        #echo -ne " -- Incomplete tests  : (${cyan}${_IT}${nc}) \n"               | tee -a ${_OUTPUT_DIR}/summary_Ww${_WEEKn}-${_HOUR}
        #echo -ne " -- dmesg-warn tests  : (${_DWT}) \n"                          | tee -a ${_OUTPUT_DIR}/summary_Ww${_WEEKn}-${_HOUR}
        #echo -ne " -- Warn tests        : (${_WT}) \n"                           | tee -a ${_OUTPUT_DIR}/summary_Ww${_WEEKn}-${_HOUR}
        #echo -ne " -- dmesg-fail tests  : (${_DFT}) \n"                          | tee -a ${_OUTPUT_DIR}/summary_Ww${_WEEKn}-${_HOUR}
        #echo -ne " -- Pass rate         : (${blue}${_PASSRATE}%${nc}) \n\n"      | tee -a ${_OUTPUT_DIR}/summary_Ww${_WEEKn}-${_HOUR}

        echo -ne "--> (${_OUTPUT_NAME}) was created in : [Desktop/results/intel-gpu-tools] \n\n"

        # Sending a email to notify that the last IGT has successfully
        # ================================================================
        if [ "${_CONNECTION}" = "INTRANET" ]; then email_template "finish"; fi
        wait
        # Releasing the DUT
        start_spinner "--> Releasing the DUT in watchdog ..."
            python ${_MAIN_PATH}/scripts/getResult.py --release free
        stop_spinner $?
        exit 2

    elif [ -f "${_MAIN_PATH}/scripts/${_LAST_ITERATION_FOLDER}/.igt_done" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -e "${cyan}=======================================================${nc}"
        echo "--> intel-gpu-tools has finished"
        echo -e "--> Please see the file ${yellow}intel-gpu-tools_TRC_summary_${_WEEKn}.csv${nc}"
        echo "--> located in [Desktop/results/intel-gpu-tools]"
        echo -ne "${cyan}=======================================================${nc} \n\n"

        # Showing the most recent statistics from the last IGT execution
        #_MOST_RECENT_SF=$(ls -t /home/${_USER}/Desktop/results/intel-gpu-tools/ | grep ^summary_Ww | head -1)
        echo -ne "--> ${yellow}This are the statistics form the last IGT execution${nc} \n\n"
        #_OUTPUT_DIR="/home/${_USER}/Desktop/results/intel-gpu-tools"
        #cat ${_OUTPUT_DIR}/${_MOST_RECENT_SF}; echo -ne "\n\n"
        # Get statistics from json file
        jsonFinalFile="${_MAIN_PATH}/scripts/iteration1/results.json" 
        python ${_MAIN_PATH}/scripts/getResult.py --getjsonstatistics ${jsonFinalFile} "all" "None"

        echo "--> If you want to run againg the failure tests please do the following steps :"
        echo "--> 1) remove/backup all iterations folders inside scripts folder"
        echo "--> 2) remove all IGT_run files inside scripts folder"
        echo "--> 3) run this script as : ${_ME} --rerun <file.json>"
        echo "--> 4) finally run againg : ${_ME} <without option>"
        echo -ne "\n\n"; exit 1

    fi

}

function check_IGT_run1 () {

    if [ ! -f "${_MAIN_PATH}/scripts/IGT_run1" ]; then

        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"

        if [ "${default_package}" != "igt_extended_list" ]; then

            validateLines=`cat ${_MAIN_PATH}/scripts/blacklist | wc -l`

            if [ "${validateLines}" -eq 0 ]; then
                echo -en '\n' >> ${_MAIN_PATH}/scripts/blacklist
            fi           

            start_spinner "--> Creating IGT_run1 for the first iteration ..."
                sleep .75

                _EXCLUDE_TESTS=$(sed -n '/^-x/p' ${_MAIN_PATH}/scripts/blacklist)
                _INCLUDE_TESTS=$(sed -n '/^-t/p' ${_MAIN_PATH}/scripts/blacklist)

                if [ ! -z "${_EXCLUDE_TESTS}" ] && [ -z "${_INCLUDE_TESTS}" ]; then
                    # Condition for _EXCLUDE_TESTS
                    _VALIDATE_BLACKLIST=et
                elif [ -z "${_EXCLUDE_TESTS}" ] && [ ! -z "${_INCLUDE_TESTS}" ]; then
                    # Condition for _INCLUDE_TESTS
                    _VALIDATE_BLACKLIST=it
                elif [ ! -z "${_EXCLUDE_TESTS}" ] && [ ! -z "${_INCLUDE_TESTS}" ]; then
                    # Condition for both (exclude & include tests)
                    _VALIDATE_BLACKLIST=both
                fi

                    case ${_VALIDATE_BLACKLIST} in 

                        et) 
                            rm ${_MAIN_PATH}/scripts/.only_test_to_run ${_MAIN_PATH}/scripts/.not_run_tests 2> /dev/null
                            while read line; do 
                                _CHECK_WILDCARD=`echo ${line} | grep -e [*] -e [.] -e [?] -e [$]` # Skipping the tests with wildcards
                                if [ -z "${_CHECK_WILDCARD}" ]; then
                                    echo -ne "${line}$ " >> ${_MAIN_PATH}/scripts/.not_run_tests
                                else
                                    echo -ne "${line} " >> ${_MAIN_PATH}/scripts/.not_run_tests
                                fi
                            done < ${_MAIN_PATH}/scripts/blacklist

                            _VAR_NOT_RUN=`cat ${_MAIN_PATH}/scripts/.not_run_tests`
                            echo -ne "bash ${_MAIN_PATH}/scripts/run-tests.sh -s -r ${_MAIN_PATH}/scripts/iteration1 ${_VAR_NOT_RUN}" > ${_MAIN_PATH}/scripts/IGT_run1
                            chmod 775 ${_MAIN_PATH}/scripts/IGT_run1 &> /dev/null

                        ;;

                        it) 
                            rm ${_MAIN_PATH}/scripts/.only_test_to_run &> /dev/null

                            while read line; do 
                                _CHECK_WILDCARD=`echo ${line} | grep -e [*] -e [.] -e [?] -e [$]` # Skipping the tests with wildcards
                                if [ -z "${_CHECK_WILDCARD}" ]; then
                                    echo -ne "${line}$ " >> ${_MAIN_PATH}/scripts/.only_test_to_run
                                else
                                    echo -ne "${line} " >> ${_MAIN_PATH}/scripts/.only_test_to_run
                                fi

                            done < ${_MAIN_PATH}/scripts/blacklist
                            
                            _VAR_RUN=`cat ${_MAIN_PATH}/scripts/.only_test_to_run`
                            echo -ne "bash ${_MAIN_PATH}/scripts/run-tests.sh -s -r ${_MAIN_PATH}/scripts/iteration1 ${_VAR_RUN}" > ${_MAIN_PATH}/scripts/IGT_run1
                            chmod 775 ${_MAIN_PATH}/scripts/IGT_run1 &> /dev/null
                        ;;

                        both) 
                            sed -n '/^-x/p' ${_MAIN_PATH}/scripts/blacklist > /tmp/only_x
                            sed -n '/^-t/p' ${_MAIN_PATH}/scripts/blacklist > /tmp/only_t

                            rm ${_MAIN_PATH}/scripts/.only_test_to_run ${_MAIN_PATH}/scripts/.not_run_tests &> /dev/null

                            while read line; do 
                                _CHECK_WILDCARD=`echo ${line} | grep -e [*] -e [.] -e [?] -e [$]` # Skipping the tests with wildcards
                                if [ -z "${_CHECK_WILDCARD}" ]; then
                                    echo -ne "${line}$ " >> ${_MAIN_PATH}/scripts/.only_test_to_run
                                else
                                    echo -ne "${line} " >> ${_MAIN_PATH}/scripts/.only_test_to_run
                                fi
                            done < /tmp/only_t

                            while read line; do 
                                _CHECK_WILDCARD=`echo ${line} | grep -e [*] -e [.] -e [?] -e [$]` # Skipping the tests with wildcards
                                if [ -z "${_CHECK_WILDCARD}" ]; then
                                    echo -ne "${line}$ " >> ${_MAIN_PATH}/scripts/.not_run_tests
                                else
                                    echo -ne "${line} " >> ${_MAIN_PATH}/scripts/.not_run_tests
                                fi
                            done < /tmp/only_x

                            _VAR_NOT_RUN=`cat ${_MAIN_PATH}/scripts/.not_run_tests`
                            _VAR_RUN=`cat ${_MAIN_PATH}/scripts/.only_test_to_run`
                            echo -ne "bash ${_MAIN_PATH}/scripts/run-tests.sh -s -r ${_MAIN_PATH}/scripts/iteration1 ${_VAR_NOT_RUN} ${_VAR_RUN}" > ${_MAIN_PATH}/scripts/IGT_run1
                            chmod 775 ${_MAIN_PATH}/scripts/IGT_run1 &> /dev/null
                        ;;

                    esac

            stop_spinner $?

        else
            echo "--> Default package is (${default_package})"
            echo -ne "bash ${_MAIN_PATH}/scripts/run-tests.sh -s -r ${_MAIN_PATH}/scripts/iteration1 -T ${_MAIN_PATH}/tests/intel-ci/extended.testlist" > ${_MAIN_PATH}/scripts/IGT_run1
            chmod 775 ${_MAIN_PATH}/scripts/IGT_run1 &> /dev/null
        fi

        sleep 3
    fi

}

function autologin_tty () {

    # This is for Systemd (Ubuntu 15.10 and higher) and only works if X is disabled
    # for reference in [/etc/systemd/system/getty.target.wants] : lrwxrwxrwx 1 root root 34 abr 10 20:25 getty@tty1.service -> /lib/systemd/system/getty@.service
    _PATH_TTY=/etc/systemd/system/getty.target.wants
    _FILE_TTY=getty@tty1.service
    _LINE_TTY=$(cat -n ${_PATH_TTY}/${_FILE_TTY} | grep -w "ExecStart" | awk '{print $1}')
    _CURRENT_PARAMETER=$(cat ${_PATH_TTY}/${_FILE_TTY} | grep -w "^ExecStart")
    _PARAMETER_TTY='ExecStart=-/sbin/agetty --autologin ${_USER} --noclear %I $TERM'
    
    if [ ! -f /home/${_USER}/._tty_done ]; then
        if [ "${_CURRENT_PARAMETER}" != "${_PARAMETER_TTY}" ]; then
            echo -ne "\n\n"
            start_spinner "--> Setting TTYs autologin ..."
                echo ${_PASSWORD} | sudo -S ls &> /dev/null; sleep 2
                # doing a backuo for getty@.service
                echo ${_PASSWORD} | sudo -S cp /lib/systemd/system/getty@.service /home/gfx/getty@.service &> /dev/null
                echo ${_PASSWORD} | sudo -S sed -i ''${_LINE_TTY}'s|^.*$|ExecStart=-/sbin/agetty --autologin '${_USER}' --noclear %I $TERM|g' /lib/systemd/system/getty@.service &> /dev/null
            stop_spinner $?
            start_spinner "--> Updating systemctl ..."
                sleep 2; echo ${_PASSWORD} | sudo -S systemctl enable getty@tty1.service &> /dev/null
            stop_spinner $?

            touch /home/${_USER}/._tty_done
        fi
    fi
}

function crontab_file (){

    # Important Note : is very immportant that run_IGT.sh goes to the beggining in the crontab before other scripts otherwise run_IGT.sh will not starts

    _CRON_FILE_CHECK=/home/${_USER}/.cron_file

    if [ ! -f "${_CRON_FILE_CHECK}" ]; then
        echo -ne "\n\n"
        start_spinner "--> Setting crontab example ..."
            echo ${_PASSWORD} | sudo -S ls &> /dev/null; sleep 2
            echo ${_PASSWORD} | sudo -S mv /etc/crontab /etc/crontab.bkp
            echo ${_PASSWORD} | sudo -S cp ${_THISPATH}/tools/crontab /etc/crontab
            echo ${_PASSWORD} | sudo -S sed -i '19s|^|@reboot sleep 30; '${_THISPATH}'/'${_ME}' |' /etc/crontab # this is the main igt script
            echo ${_PASSWORD} | sudo -S sed -i '20s|^|@reboot sleep 60; '${_THISPATH}'/tools/IGT_dmesg_daemon.sh |' /etc/crontab # this daemon check for dmesg issues
            touch /home/${_USER}/.cron_file &> /dev/null
        stop_spinner $?
    fi

    crontab -l &> /tmp/cronjobs
    _VALIDATE_CRON_JOBS=$(cat /tmp/cronjobs)
    _ADD_CHECK=$(crontab -l 2>&1 | grep "chvt 1")
    _CHECK1=$(crontab -l 2>&1 | grep "run_IGT.sh")
    _ADD_TASK=$(cat -n /etc/crontab | grep 18 | sed 's/18//g' | sed -e 's/\t//g' -e 's/^    //g') # change to virtual terminal 1 after reboot
    _FIRST_TASK=$(cat -n /etc/crontab | grep 19 | sed 's/19//g' | sed -e 's/\t//g' -e 's/^    //g')
    _SECOND_TASK=$(cat -n /etc/crontab | grep 20 | sed 's/20//g' | sed -e 's/\t//g' -e 's/^    //g')

    if [ "${_VALIDATE_CRON_JOBS}" = "no crontab for ${_USER}" ]; then
        echo -ne "--> ${bold}Please set jobs for crontab in order to run IGT${nc} <-- \n\n"
        echo -ne "   ${blue}1)${nc} type (${yellow}crontab -e${nc}) and add at the end of the file the following lines : \n\n"
        echo -ne "SHELL=/bin/bash \n"
        echo -ne "PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin \n"
        echo -ne "BASH_ENV=/home/${_USER}/.bashrc \n"
        echo -ne "TERM=xterm \n"
        echo -ne "${_ADD_TASK} \n"
        echo -ne "${_FIRST_TASK} \n"
        echo -ne "${_SECOND_TASK} \n\n\n"; exit 1
    elif [ -z "${_ADD_CHECK}" ] || [ -z "${_CHECK1}" ]; then
        echo -ne "--> ${bold}Please set jobs for crontab in order to run IGT${nc} <-- \n\n"
        echo -ne "   ${blue}1)${nc} type (crontab -e) and add at the end of the file the following lines : \n\n"
        echo -ne "SHELL=/bin/bash \n"
        echo -ne "PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin \n"
        echo -ne "BASH_ENV=/home/${_USER}/.bashrc \n"
        echo -ne "TERM=xterm \n"
        echo -ne "${_ADD_TASK} \n"
        echo -ne "${_FIRST_TASK} \n"
        echo -ne "${_SECOND_TASK} \n\n\n"; exit 1
    fi
}

function rerun () {

    if [ -z "$1" ]; then
        echo -ne "\n\n"; echo -ne " Please specify a results.json file \n\n"; exit 2
    else
        python ${_THISPATH}/tools/getResult.py "--getfail" "$1"
    fi
    exit 2
}

function usage () {

    clear; echo -ne "\n\n"; echo -ne " ${cyan}Intel® Graphics for Linux* | 01.org${nc} \n\n"
    echo -ne " Usage : ${yellow}${_ME}${nc} [options] \n\n"
    echo -e "  -h | --help                     See this menu"
    echo -e "  -s | --statistics               Show the statistics for the blacklist file"
    echo -e "  -b | --basic                    run intel-gpu-tools basic tests"
    echo -e "  -f | --fastfeedback             run intel-gpu-tools fast-feedback tests"
    echo -ne "  -r | --rerun <results.json>     rerun IGT from a giving json file \n\n\n"; exit 1
}

function check_i915 () {

    clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
    echo -ne  "--> Checking for i915 ... "
    echo ${_PASSWORD} | sudo -S ls &> /dev/null; sleep 2
    _DRIVER_IN_USE=$(echo ${_PASSWORD} | sudo -S lspci -v -s $(lspci |grep "VGA compatible controller" |cut -d" " -f 1) | grep "Kernel driver in use"  | awk -F": " '{print $2}')

    if [ -z "${_DRIVER_IN_USE}" ]; then
        echo -ne "[${red}FAIL${nc}] \n"
        echo -ne "--> ${red}i915 driver is not in use${nc} \n"
        echo -ne "--> to be able to continue please add the following parameter to grub \n"
        echo -ne "--> ${yellow}i915.preliminary_hw_support=1${nc} \n"
        echo -ne "--> this parameter is used to enable i915 driver in (6th gen.) GPUs and newer \n\n"; exit 2
    else
        # i915 driver is in use
        echo -ne "[${green}OK${nc}] \n"; sleep .05
    fi
}

function check_X () {
    
    _CHECK_X=$(ps -e | grep X) # for Ubuntu 16

    if [ ! -z "${_CHECK_X}" ]; then
        echo -ne "\n\n"
        echo -ne "${red}===========================================================${nc} \n"
        echo -ne "--> ${yellow}X must be disabled${nc} before to run IGT \n"
        echo -ne "--> Please run tux.sh and select the following options \n"
        echo -ne "--> Option 4 > option 10 > option 2 and then restart the DUT \n\n"
        echo -ne "${red}===========================================================${nc} \n\n"; exit 2
    fi
}

function check_swap_partition () {

    if [ ! -f "/home/${_USER}/.swap_ready" ]; then
        ${_THISPATH}/tools/swap.sh
    fi
}

function basic_tests () {

    if [ ! -d "${_MAIN_PATH}" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne " --> ${red}intel-gpu-tools folder does not exists${nc} \n"
        echo -ne " --> into [/home/${_USER}/intel-graphics] \n"
        echo -ne " --> please install the MX Gfx stack or put intel-gpu-tools in the above path \n\n\n"; exit 2
    fi

    # ===========================================================================================================================
    # Checking for Piglit folder inside Intel-GPU-Tools
    # ===========================================================================================================================
    if [ ! -d "${_MAIN_PATH}/piglit" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne "--> ${red}Piglit was not found${nc} <-- into ${_MAIN_PATH} \n"
        echo -ne "--> ${yellow}Please download Piglit into before to continue${nc} \n"
        echo -ne "--> git clone http://anongit.freedesktop.org/git/piglit.git ${_MAIN_PATH} \n\n"; exit 2
    fi

    if [ ! -f "${_MAIN_PATH}/tests/test-list.txt" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne "--> ${yellow}Warning${nc} : intel-gpu-tools ${red}is not compiled${nc} \n"
        echo -ne "--> please compile intel-gpu-tools to continue \n\n"; exit 2
    fi
        # ===========================================================================================================================
        # Getting the total IGT tests by name to improve times in this script
        # ===========================================================================================================================
        if [ ! -f "${_MAIN_PATH}/scripts/.total_IGT_tests_name" ]; then
            ${_MAIN_PATH}/scripts/run-tests.sh -l > ${_MAIN_PATH}/scripts/.total_IGT_tests_name
        fi

    if [ ! -f "${_MAIN_PATH}/scripts/blacklist" ]; then
        start_spinner "--> Generating blacklist for basic tests ..."
            sleep 2; sed 's|/|@|g' ${_MAIN_PATH}/scripts/.total_IGT_tests_name | grep basic > ${_MAIN_PATH}/scripts/tmp.blacklist
            rm ${_MAIN_PATH}/scripts/blacklist &> /dev/null
            while read line; do
                echo "-t ${line}" >> ${_MAIN_PATH}/scripts/blacklist
            done < ${_MAIN_PATH}/scripts/tmp.blacklist
            rm ${_MAIN_PATH}/scripts/tmp.blacklist &> /dev/null
        stop_spinner $?
    fi

	touch ${_MAIN_PATH}/scripts/.basic     

}

function fast_feedback () {

    if [ ! -d "${_MAIN_PATH}" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne " --> ${red}intel-gpu-tools folder does not exists${nc} \n"
        echo -ne " --> into [/home/${_USER}/intel-graphics] \n"
        echo -ne " --> please install the MX Gfx stack or put intel-gpu-tools in the above path \n\n\n"; exit 2
    fi

    # ===========================================================================================================================
    # Checking for Piglit folder inside Intel-GPU-Tools
    # ===========================================================================================================================
    if [ ! -d "${_MAIN_PATH}/piglit" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne "--> ${red}Piglit was not found${nc} <-- into ${_MAIN_PATH} \n"
        echo -ne "--> ${yellow}Please download Piglit into before to continue${nc} \n"
        echo -ne "--> git clone http://anongit.freedesktop.org/git/piglit.git ${_MAIN_PATH} \n\n"; exit 2
    fi

    if [ ! -f "${_MAIN_PATH}/tests/test-list.txt" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne "--> ${yellow}Warning${nc} : intel-gpu-tools ${red}is not compiled${nc} \n"
        echo -ne "--> please compile intel-gpu-tools to continue \n\n"; exit 2
    fi

    if [ ! -f "${_FAST_FEEDBACK_LIST}" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne "--> ${yellow}Warning${nc} : fast-feedback.testlist ${red}was not found in this intel-gpu-tools commit${nc} \n"
        echo -ne "--> please compile a intel-gpu-tools commit that contains fast-feedback.testlist \n\n"; exit 2
    fi

        # ===========================================================================================================================
        # Getting the total IGT tests by name to improve times in this script
        # ===========================================================================================================================
        if [ ! -f "${_MAIN_PATH}/scripts/.total_IGT_tests_name" ]; then
            ${_MAIN_PATH}/scripts/run-tests.sh -l > ${_MAIN_PATH}/scripts/.total_IGT_tests_name
        fi

    if [ ! -f "${_MAIN_PATH}/scripts/blacklist" ]; then
        start_spinner "--> Generating blacklist for fast-feedback tests ..."
            sleep .75; rm ${_MAIN_PATH}/scripts/blacklist &> /dev/null
            # Cleaning the fast-feedback.testlist
            sed 's/igt@/-t /g' ${_FAST_FEEDBACK_LIST} > ${_MAIN_PATH}/scripts/blacklist
            #tr '\n' ' ' < ${_MAIN_PATH}/scripts/tmp.blacklist > ${_MAIN_PATH}/scripts/tmp.blacklist2
        stop_spinner $?
    fi

    touch ${_MAIN_PATH}/scripts/.fastfeedback

}

function extended () {

    if [ ! -d "${_MAIN_PATH}" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne " --> ${red}intel-gpu-tools folder does not exists${nc} \n"
        echo -ne " --> into [/home/${_USER}/intel-graphics] \n"
        echo -ne " --> please install the MX Gfx stack or put intel-gpu-tools in the above path \n\n\n"; exit 2
    fi

    # ===========================================================================================================================
    # Checking for Piglit folder inside Intel-GPU-Tools
    # ===========================================================================================================================
    if [ ! -d "${_MAIN_PATH}/piglit" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne "--> ${red}Piglit was not found${nc} <-- into ${_MAIN_PATH} \n"
        echo -ne "--> ${yellow}Please download Piglit into before to continue${nc} \n"
        echo -ne "--> git clone http://anongit.freedesktop.org/git/piglit.git ${_MAIN_PATH} \n\n"; exit 2
    fi

    if [ ! -f "${_MAIN_PATH}/tests/test-list.txt" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne "--> ${yellow}Warning${nc} : intel-gpu-tools ${red}is not compiled${nc} \n"
        echo -ne "--> please compile intel-gpu-tools to continue \n\n"; exit 2
    fi

    if [ ! -f "${_EXTENDED_TEST_LIST}" ]; then
        clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
        echo -ne "--> ${yellow}Warning${nc} : extended.testlist ${red}was not found in this intel-gpu-tools commit${nc} \n"
        echo -ne "--> please compile a intel-gpu-tools commit that contains extended.testlist \n\n"; exit 2
    fi

        # ===========================================================================================================================
        # Getting the total IGT tests by name to improve times in this script
        # ===========================================================================================================================
        if [ ! -f "${_MAIN_PATH}/scripts/.total_IGT_tests_name" ]; then
            ${_MAIN_PATH}/scripts/run-tests.sh -l > ${_MAIN_PATH}/scripts/.total_IGT_tests_name
        fi

    if [ ! -f "${_MAIN_PATH}/scripts/blacklist" ]; then
        start_spinner "--> Generating blacklist for extended tests ..."
            sleep .75; rm ${_MAIN_PATH}/scripts/blacklist &> /dev/null
            # Cleaning the fast-feedback.testlist
            sed 's/igt@/-t /g' ${_EXTENDED_TEST_LIST} > ${_MAIN_PATH}/scripts/blacklist
            #tr '\n' ' ' < ${_MAIN_PATH}/scripts/tmp.blacklist > ${_MAIN_PATH}/scripts/tmp.blacklist2
        stop_spinner $?
    fi

    touch ${_MAIN_PATH}/scripts/.extended

}

function auto_post () {

    case "$1" in 

        "auto_setup")
            
            source "${ConfigFile}"
            LinuxImage=`echo "${default_image}" | awk -F"_" '{print $2}'`
            if [ "${LinuxImage}" = "16.10" ]; then Distro="Ubuntu 16.10 yakkety"; fi

            echo "import requests" > ${PostFile}
            echo "data = {" >> ${PostFile}
            echo '"RaspberryNumber":"'${raspberry_number}'",'  >> ${PostFile}
            echo '"PowerSwitchNumber":"'${raspberry_power_switch}'",' >> ${PostFile}            
            echo '"Status":"[auto setup]",' >> ${PostFile}
            echo '"Suite" : "[auto] '${currentSuite}'",' >> ${PostFile}
            echo '"DutHostname":"'${dut_hostname}'",' >> ${PostFile}
            echo '"DutIP":"'${dut_static_ip}'",' >> ${PostFile}
            echo '"KernelBranch" : "'${kernel_branch}'",' >> ${PostFile}
            echo '"KernelCommit" : "'${kernel_commit}'",' >> ${PostFile}
            echo '"GfxStackCode" : "'${gfx_stack_code}'",' >> ${PostFile}
            echo '"GrubParameters" : "'${grub_parameters}'",' >> ${PostFile}
            if [ ! -z "${dmc}" ]; then echo '"dmc" : "'${dmc}'",' >> ${PostFile}; else echo '"dmc" : " ",' >> ${PostFile}; fi
            if [ ! -z "${guc}" ]; then echo '"guc" : "'${guc}'",' >> ${PostFile}; else echo '"guc" : " ",' >> ${PostFile}; fi
            if [ ! -z "${huc}" ]; then echo '"huc" : "'${huc}'",' >> ${PostFile}; else echo '"huc" : " ",' >> ${PostFile}; fi
            echo '"Blacklist":"'${blacklist_file}'",' >> ${PostFile}
            echo '"DutUptime":" ",' >> ${PostFile}
            echo '"OverallTime":" ",' >> ${PostFile}
            echo '"Distro":"'${Distro}'",' >> ${PostFile}
            echo '"TRCLink":" ",' >> ${PostFile}
            echo '"CurrentTestName":" ",' >> ${PostFile}
            echo '"CurrentTestTime":" ",' >> ${PostFile}
            echo '"CurrentTestNumber":" ",' >> ${PostFile}
            echo '"ETA":" ",' >> ${PostFile}
            echo '"TotalTest":" ",' >> ${PostFile}
            echo '"TestsToRun":" ",' >> ${PostFile}
            echo '"TestsToNotRun":" ",' >> ${PostFile}
            echo '"LastTestStatus":" ",' >> ${PostFile}
            echo '"BasicPassRate":" ",' >> ${PostFile}
            echo '"Pass":" ",' >> ${PostFile}
            echo '"Fail":" ",' >> ${PostFile}
            echo '"Crash":" ",' >> ${PostFile}
            echo '"Skip":" ",' >> ${PostFile}
            echo '"Timeout":" ",' >> ${PostFile}
            echo '"Incomplete":" ",' >> ${PostFile}
            echo '"DmesgWarn":" ",' >> ${PostFile}
            echo '"Warn":" ",' >> ${PostFile}
            echo '"DmesgFail":" ",' >> ${PostFile}
            echo '"PassRate":" ",' >> ${PostFile}
            echo "}" >> ${PostFile}
            echo "try:" >> ${PostFile}
            echo '  r = requests.post("http://bifrost.intel.com:2020/watchdog",data)' >> ${PostFile}
            echo "except:" >> ${PostFile}
            echo '  print "--> Could not connect to database"'>> ${PostFile}

            start_spinner "--> Sending [auto setup] post to data base ..."
                sleep .5; python ${PostFile}
            stop_spinner $?

            ;;

        esac
}
