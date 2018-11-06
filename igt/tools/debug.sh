#!/bin/bash

	##############################################################
	# LOAD config.cfg / functions.sh                             #
	##############################################################
	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`

	source ${_THISPATH}/functions.sh
	export -f _spinner start_spinner stop_spinner start_time stop_time


	clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
	start_spinner "--> Reseting terminal ..."
		reset &> /dev/null; echo ${_PASSWORD} | sudo -S ls &> /dev/null; sleep 2
	stop_spinner $?


	########################################
	# Local variables                      #
	########################################
	export _USER=`whoami`
	export _PASSWORD="linux"
	export _LIST=`cat ${_THISPATH}/debug_file`
	export fail=0 export pass=0 export skip=0
	export _FILE=/home/${_USER}/dmesg_issues/dmesg_fail.log
	export _GET_DATE=$(date +"%b_%d_%Y")
	export _HOUR=$(date +%I-%M-%S)
	export _DEBUG_LOG_FILE="intel-gpu-tools_${_GET_DATE}-${_HOUR}.log"
	export _RESULTS_FILE="intel-gpu-tools_results_${_GET_DATE}-${_HOUR}.csv"
	export _FIND_IGT_FILE=`locate -n1 -w run-tests.sh`
	export _IGT_PATH=`dirname ${_FIND_IGT_FILE} | sed 's|/scripts||g'`
	export _DMESG_OUTPUT_FOLDER="{_IGT_PATH}/tools/dmesg_output"


	########################################
	# Checking for a debug_file            #
	########################################

	if [ ! -f "${_THISPATH}/debug_file" ]; then
		clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
		echo -ne " --> debug_file ${red} does not exists${nc}, please create it in : [${_THISPATH}] \n\n"; exit 1
	else
		# Removing empty lines from debug_file
		sed -i '/^\s*$/d' ${_THISPATH}/debug_file
		if [ ! -s "${_THISPATH}/debug_file" ]; then
			echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
			echo -ne " --> debug_file ${red} is empty${nc}, please add some tests in the following format \n"
			echo -ne " --> igt@<family>@<subtest> \n\n"; exit 1
		fi
	fi

	# Removing empty lines from debug_file
	sed -i '/^\s*$/d' ${_THISPATH}/debug_file

	if [ ! -d "${_DMESG_OUTPUT_FOLDER}" ]; then mkdir -p ${_DMESG_OUTPUT_FOLDER} &> /dev/null; fi

function _check_tests_debug_file () {

    ####################################################################################
    # # Checking if the tests are compiled in the current intel-gpu-tools commit / tag #
    ####################################################################################

    if [ ! -f "${_IGT_PATH}/scripts/.families_with_subtests" ] || [ ! -f "${_IGT_PATH}/scripts/.families_without_subtests" ]; then
        _TEST_LIST=`cat "${_IGT_PATH}/tests/test-list.txt" | sed -e '/TESTLIST/d' -e 's/ /\n/g'`

        for test in ${_TEST_LIST}; do
             SUBTESTS=`"${_IGT_PATH}/tests/${test}" --list-subtests`
                if [ -z "$SUBTESTS" ]; then
                    echo "${test}" >> ${_IGT_PATH}/scripts/.families_without_subtests
                else
                    for subtest in ${SUBTESTS}; do
                        echo "${test}@${subtest}" >> ${_IGT_PATH}/scripts/.families_with_subtests
                     done
                fi
        done
    fi

    rm -rf /tmp/full_test.txt &> /dev/null
    cat ${_IGT_PATH}/scripts/.families_without_subtests >> /tmp/full_test.txt
    cat ${_IGT_PATH}/scripts/.families_with_subtests >> /tmp/full_test.txt

    unset _NOTIFICATION
    _NOTIFICATION=0 _TESTS_NOT_FOUND="" _FLAG=0

    start_spinner "--> Validating the tests entered in debug_file ..."

    rm -rf ${_IGT_PATH}/scripts/test_not_found &> /dev/null
    
    while read -r line; do

    		_ONLY_TEST=`echo "${line}" | sed 's/igt@//g'`
            _CHECK_TEST=`cat /tmp/full_test.txt | grep -w "${_ONLY_TEST}"`
            if [ -z "${_CHECK_TEST}" ]; then
                if [ "${_NOTIFICATION}" -eq 0 ]; then clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"; ((_NOTIFICATION++)); _FLAG=1; fi
                echo "${line}" >> ${_IGT_PATH}/scripts/test_not_found
                _TESTS_NOT_FOUND="${_TESTS_NOT_FOUND} ${line}"
            fi

    done < ${_THISPATH}/debug_file

    stop_spinner $?

    if [ "${_FLAG}" -eq 1 ]; then 
        echo -ne "\n\n"
        echo -ne "--> ${yellow}The following tests were${nc} ${red}NOT FOUND${nc} ${yellow}in intel-gpu-tools${nc} \n\n"
        cat ${_IGT_PATH}/scripts/test_not_found; echo -ne "\n\n"
        echo -ne "--> Please check the debug_file and remove/modify this tests to continue \n"
        echo -ne "--> You can also find this tests on : ${_IGT_PATH}/scripts/test_not_found \n\n"
        exit 1
    fi

}

	######################################################
	# Checking if the tests entered in debug_file exists #
	######################################################
	_check_tests_debug_file

	echo -ne "\n\n"
	start_spinner "--> Recording a log file ..."
		sleep 1.2
	stop_spinner $?
	# Creating a new results file
	touch ${_IGT_PATH}/tests/${_RESULTS_FILE}
	main_start_time

	_TOTAL_TESTS=`cat ${_THISPATH}/debug_file | wc -l`
	_COUNT=1

	for value in ${_LIST}; do
		unset _WARNING_FLAG _CURRENT_TEST _NO_OUTPUT_FLAG
		echo -ne "\n\n" 																					
		# echo -e "${blue}######################################################${nc}" 						
		start_spinner "--> Erasing dmesg information ..." 													
			echo ${_PASSWORD} | sudo -S dmesg -C &> /dev/null
		stop_spinner $? 																					
		
		family=`echo $value | awk -F"@" '{print $2}'`
		subtest=`echo $value | awk -F"@" '{print $3}'`
		if [ ! -z "${subtest}" ]; then
			echo -ne "--> ${yellow}testing${nc} : ${bold}${family}@${subtest}${nc} [${_COUNT}/${_TOTAL_TESTS}] ... \n\n"				
			start_time
			echo ${_PASSWORD} | sudo -S ${_IGT_PATH}/tests/${family} --run-subtest ${subtest} --debug
			result=$? 		
			echo																							
			stop_time "${bold}test time was${nc}"															
			_CURRENT_TEST="echo ${family}@${subtest}"
		else
			echo -ne "--> ${yellow}testing${nc} : ${bold}${family}${nc} ... \n\n"							
			start_time
			echo ${_PASSWORD} | sudo -S ${_IGT_PATH}/tests/${family} --debug
			result=$?						
			echo																							
			stop_time "${bold}test time was${nc}"															
			_CURRENT_TEST="echo ${family}"
		fi

		if [ ! -z "${_MINUTES}" ]; then 
			if [ ${_MINUTES} != 0 -a ${_MINUTES} -gt 10 ]; then _WARNING_FLAG=1; fi
		fi

		########################################
		# igt error codes                      #
		########################################

		# 139 = Segmentation faul (core dumped)
		# 77  = skip (some times due to "Not gpu found")
		# 0   = pass
		# 99  = fail

		_PASS="0" _SKIP="77" _COUNT_DMESG_FAIL="0" _PASS_WITHOUT_OUTPUT="0"

		if [ "${result}" = "${_PASS}" ]; then

				((pass++)); echo -ne "\n\n"
	            echo -e " ${bold}[[Status]]${nc} : ${green}PASS${nc}"										
				
				# Checking for dmesg errors
				cdmesg &> /dev/null	
				if [ -f ${_FILE} ]; then
					echo -ne " ${cyan}------ dmesg information ------${nc} \n\n"								
					cat ${_FILE}																				
					echo -ne "\n\n"																				
					((_COUNT_DMESG_FAIL++))
				else
					echo -e "--> this test does not generated error conditions on dmesg"						
				fi

				if [ "${_WARNING_FLAG}" = 1 ]; then
					echo -e "${yellow}---------------------------------------------------${nc}"				
					echo -e "--> the result for : [${_CURRENT_TEST}] is pass"								
					echo -e "--> however the test took more than 10 minutes"								
					echo -e "--> and this result need to be reported in FDO"								
					echo -e "--> https://bugs.freedesktop.org/"												
					echo -ne "${yellow}---------------------------------------------------${nc} \n\n"		
					echo -e "${blue}######################################################${nc}"			
					echo "igt,${value},pass,,code ${result},this test took more than 10 minutes and needs to be reported in https://bugs.freedesktop.org/," >> ${_IGT_PATH}/tests/${_RESULTS_FILE}
				else
					echo "igt,${value},pass,,code ${result}," >> ${_IGT_PATH}/tests/${_RESULTS_FILE}
					echo -e "${blue}######################################################${nc}"			
				fi

		elif [ "${result}" = "${_SKIP}" ]; then
				((skip++)); echo "igt,${value},skip,,code ${result}," >> ${_IGT_PATH}/tests/${_RESULTS_FILE}
	            echo -ne "\n\n"																				
	            echo -e " ${bold}[[Status]]${nc} : ${yellow}SKIP${nc}"										
			    echo -e "${blue}######################################################${nc}"				
		else 
			((fail++)); echo "igt,${value},fail,,code ${result}," >> ${_IGT_PATH}/tests/${_RESULTS_FILE}
			echo -ne "\n\n"																					
			cdmesg &> /dev/null
			if [ -f ${_FILE} ]; then
				echo -ne " ${cyan}------ dmesg information ------${nc} \n\n"								
				cat ${_FILE}																				
				echo -ne "\n\n"																				
				((_COUNT_DMESG_FAIL++))
			else
				echo -e "--> this test does not generated error conditions on dmesg"						
			fi
			echo -e " ${bold}[[Status]]${nc} : ${red}FAIL${nc}"												
			echo -e "${blue}######################################################${nc}"					
		fi
	
		((_COUNT++))

		# Generating dmesg for each tests
		mkdir -p ${_DMESG_OUTPUT_FOLDER}/${_CURRENT_TEST} &> /dev/null
		dmesg > ${_DMESG_OUTPUT_FOLDER}/${_CURRENT_TEST}/${_CURRENT_TEST}_dmesg.log &> /dev/null
		cp /home/${_USER}/dmesg_issues/* ${_DMESG_OUTPUT_FOLDER}/${_CURRENT_TEST}/ &> /dev/null

	done

	total=$((pass + fail + skip)) 

	echo -ne  "\n\n"																						
	echo -ne "######### Summary ######### \n\n"																
	if [ "${pass}" != 0 ]; then 
		echo -ne "--> ${green}Pass${nc}                      : [${pass}] \n"
		if [ "${_COUNT_DMESG_FAIL}" != 0 ]; then
			echo -ne "--> ${red}Error logs${nc}                : [${_COUNT_DMESG_FAIL}] \n"
		fi
	fi
	
	if [ "${fail}" != 0 ]; then 
		echo -ne "--> ${red}Fail${nc}                      : [${fail}] \n"									
		echo -ne "--> ${red}Error logs${nc}                : [${_COUNT_DMESG_FAIL}] \n"
	fi
	
	if [ "${skip}" != 0 ]; then 
		echo -ne "--> ${cyan}Skip${nc}                      : [${skip}] \n"									
	fi
	echo -ne "--> Total tests               : [${total}] \n"												
	main_stop_time "Overal time"

	echo																			
	echo " -- dmesg logs     : ${_DMESG_OUTPUT_FOLDER}"
	echo " -- Results file   : ${_IGT_PATH}/tests/${_RESULTS_FILE}"

	exit 1
