#!/bin/bash

	# <<-- Setting the global colors -->
	# http://misc.flogisoft.com/bash/tip_colors_and_formatting
	# The right colors that works under TTys are : https://wiki.archlinux.org/index.php/Color_Bash_Prompt_(Espa%C3%B1ol)#Indicadores_Basicos
	export nc="\e[0m"
	export underline="\e[4m"
	export bold="\e[1m"
	export green="\e[1;32m"
	export red="\e[1;31m"
	export yellow="\e[1;33m"
	export blue="\e[1;34m"
	export cyan="\e[1;36m"
	# <<-- Setting the global colors -->

	export thispath=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd ) # <- current script path, even if i call from tux ;)
	source $thispath/common.sh

	clear; echo -ne "\n\n"
	echo -ne " --> ${bold}${yellow}rendercheck -t fill -f a8r8g8b8${nc} \n\n"
	rendercheck -t fill -f a8r8g8b8 | tee /tmp/renderSFT
	check_rc "rendercheck/fill" $?
	echo -ne "\n\n"; sleep 3

	echo -ne " --> ${bold}${yellow}rendercheck -t dcoords -f a8r8g8b8${nc} \n\n"
	rendercheck -t dcoords -f a8r8g8b8 | tee -a /tmp/renderSFT
	check_rc "rendercheck/dcoords" $?
	echo -ne "\n\n"; sleep 3

	echo -ne " --> ${bold}${yellow}rendercheck -t scoords -f a8r8g8b8${nc} \n\n"
	rendercheck -t scoords -f a8r8g8b8 | tee -a /tmp/renderSFT
	check_rc "rendercheck/scoords" $?
	echo -ne "\n\n"; sleep 3

	echo -ne " --> ${bold}${yellow}rendercheck -t mcoords -f a8r8g8b8${nc} \n\n"
	rendercheck -t mcoords -f a8r8g8b8 | tee -a /tmp/renderSFT
	check_rc "rendercheck/mcoords" $?
	echo -ne "\n\n"; sleep 3

	echo -ne " --> ${bold}${yellow}rendercheck -t tscoords -f a8r8g8b8${nc} \n\n"
	rendercheck -t tscoords -f a8r8g8b8 | tee -a /tmp/renderSFT
	check_rc "rendercheck/tscoords" $?
	echo -ne "\n\n"; sleep 3

	echo -ne " --> ${bold}${yellow}rendercheck -t tmcoords -f a8r8g8b8${nc} \n\n"
	rendercheck -t tmcoords -f a8r8g8b8 | tee -a /tmp/renderSFT
	check_rc "rendercheck/tmcoords" $?
	echo -ne "\n\n"; sleep 3

	echo -ne " --> ${bold}${yellow}rendercheck -t triangles -f a8r8g8b8${nc} \n\n"
	rendercheck -t triangles -f a8r8g8b8 | tee -a /tmp/renderSFT
	check_rc "rendercheck/triangles" $?
	echo -ne "\n\n"; sleep 3

	# Getting a summary

	if [ -f "/tmp/renderSFT" ]; then
		cat /tmp/renderSFT | grep -w "tests" > /tmp/renderSFT_result

		while read line
		do
			criterion=$(echo $line | awk '{print $3}')

			if [ "$criterion" = "passed" ]; then
				total_passed_tests=$(echo $line | awk '{print $1}') #left
				passed_tests=$((passed_tests + total_passed_tests))
				total_tests=$(echo $line | awk '{print $5}')
				count_total_tests=$(( count_total_tests + total_tests ))
			elif [ "$criterion" = "failed" ]; then
				total_failed_tests=$(echo $line | awk '{print $1}') #left
				failed_tests=$((failed_tests + total_failed_tests))
				total_tests=$(echo $line | awk '{print $5}')
				count_total_tests=$(( count_total_tests + total_tests ))
			fi

		done < /tmp/renderSFT_result

		if [ -z "$failed_tests" ]; then failed_tests=0; fi
		passrate=$(echo "scale =2; $passed_tests*100/$count_total_tests" | bc)

		echo -ne "\n\n"
		echo -ne " Summary \n\n"
		echo -ne " Passed tests : (${green}$passed_tests${nc}) \n"
		echo -ne " Failed tests : (${red}$failed_tests${nc}) \n"
		echo -ne " Total tests  : ($count_total_tests) \n"
		echo -ne " Pass rate    : (${blue}$passrate%${nc}) \n\n"


	fi

	echo -ne "${bold}${blue}rendercheck has finished${nc} \n\n\n"; exit 2
	#fill,dcoords,scoords,mcoords,tscoords,
	#                tmcoords,blend,composite,cacomposite,gradients,repeat,triangles,
	#                bug7366
