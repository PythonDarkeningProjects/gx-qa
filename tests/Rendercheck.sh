#!/bin/bash
#
#   Copyright (c) Intel, 2015
#
# File:         Rendercheck.sh
#
# Description:
#
# Author(s):    Humberto Perez <humberto.i.perez.rodriguez@intel.com>
#
# Date:         2015/07/11
#
# script <file> command capture everything and save a log and shows all output
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# "The idea is to stress a system to the breaking point in order to find bugs that will make that break potentially harmful.
# The system is not expected to process the overload without adequate resources, but to behave (e.g., fail) in an acceptable manner (e.g., not corrupting or losing data). "
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

	clear

	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>
	export CUSER=$(whoami)
	export PASSWORD=linux
	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>

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

	export rendercheckpath=/home/$CUSER/intel-graphics/rendercheck
	export renderfile=/home/$CUSER/intel-graphics/rendercheck/rendercheck
	export mainPath=/home/$CUSER/intel-graphics

	if [[ $3 != "no_check" ]]; then
		# Cheking that this script does not run via ssh, otherwise some tests could be skipped
		checkTTY=$(tty | awk -F"/dev/" '{print $2}')
		if [ ! -z "$SSH_CLIENT" ] || [ ! -z "$SSH_TTY" ] || [[ "$checkTTY" = "tty1"  || "$checkTTY" = "tty2" || "$checkTTY" = "tty3" || "$checkTTY" = "tty4" || "$checkTTY" = "tty5" || "$checkTTY" = "tty6" ]]; then echo -ne "\n\n";	echo -ne "${bold}${yellow} *************************************************${nc} \n"; echo -ne " ${bold}${red}RENDERCHECK needs to run under [X Window System]${nc} \n"; echo -ne " ${bold}${red}otherwise rendercheck will not run${nc} \n"; echo -ne " ${bold}${red}DO NOT RUN RENDERCHECK UNDER SSH${nc} \n"; echo -ne " ${bold}${yellow}*************************************************${nc} \n"; echo -ne "\n\n" ;exit 2; fi
	fi

	weekn=$(date +"%-V") # with this simbol '-' i can eliminite the 0 to do calculations
	export weekn=$(( weekn + 1 ))
	export getdate=$(date +"%b/%d/%Y")
	export hour=$(date +%I:%M:%S)
	export me=`basename $0`
	export thispath=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd ) # <- current script path, even if i call from tux ;)


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
                exit 2
            fi

            kill $3 > /dev/null 2>&1

            # inform the user uppon success or failure
            echo -en "\b["
            if [[ $2 -eq 0 ]]; then
                echo -en "${green}${on_success}${nc}"
            else
                echo -en "${red}${on_fail}${nc}"
            fi
            echo -e "]"
            ;;
        *)
            echo "invalid argument, try {start/stop}"
            exit 2
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

	unset date1
	date1=$(date +"%s")

}

function stop_time {

	unset date2 diff minutes seconds hours varhours varminutes varseconds
	date2=$(date +"%s")
	diff=$(($date2-$date1))   # <-- There is seconds
	# minutes=$((($diff / 60)))
	minutes=$(( (diff / 60) %60 ))
	seconds=$((($diff % 60)))
	hours=$((($minutes / 60)))

	if [ $hours != 0 ]; then varhours=$(echo "$hours Hours"); fi
	if [ $minutes != 0 ]; then varminutes=$(echo "$minutes Minutes"); fi
	if [ $seconds != 0 ]; then varseconds=$(echo "$seconds Seconds"); fi

	echo "++ $1 : $varhours $varminutes $varseconds "
	
}

checkdos2unix=$(dpkg -l dos2unix 2> /dev/null)
if [ -z "$checkdos2unix" ]; then start_spinner "++ Installing dos2unix ... "; echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 5; echo $PASSWORD | sudo -S apt-get install dos2unix -q=2 &> /dev/null; stop_spinner $?;fi
checkzenity=$(dpkg -l zenity 2> /dev/null)
if [ -z "$checkzenity" ]; then start_spinner "++ Installing zenity ... "; echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 5; echo $PASSWORD | sudo -S apt-get install zenity -q=2 &> /dev/null; stop_spinner $?;fi



function report {

	date2=$(date +"%s")
	mkdir -p $mainPath/rendercheck &> /dev/null
	if [ ! -z "$date1" ]; then diff=$(($date2-$date1)); fi   # <-- There is seconds
	if [ ! -z "$diff" ]; then minutes=$(( (diff / 60) %60 )); fi
	if [ ! -z "$diff" ]; then seconds=$((($diff % 60))); fi
	if [ ! -z "$minutes" ]; then hours=$((($minutes / 60))); fi 

	if [ ! -z "$hours" ] && [ $hours != 0 ]; then varhours=$(echo "$hours Hours");fi
	if [ ! -z "$minutes" ] && [ $minutes != 0 ]; then varminutes=$(echo "$minutes Minutes");fi
	if [ ! -z "$seconds" ] && [ $seconds != 0 ]; then varseconds=$(echo "$seconds Seconds");fi
	
	if [ ! -f "$2" ]; then 
		echo -ne "\n\n"; echo -ne " ${bold}${yellow}The file${nc} ${bold}${blue}[$2]${nc} ${bold}${yellow}does not exits${nc} \n"
		echo -ne " Please enter a valid file \n\n\n"; exit 2; 
	else 
		cp "$2" $mainPath/rendercheck/summary &> /dev/null; echo -ne "\n\n"
		start_spinner "++ Converting the file to unix format ... "
			sleep 2; dos2unix -f $mainPath/rendercheck/summary &> .dos2unix_error
		stop_spinner $?

		cwf=$(cat .dos2unix_error | grep -w "converting file")

		if [ -z "$cwf" ]; then
			echo -ne "\n\n"
			echo -ne "${bold}${red}Maybe this file comes from windows machine${nc} \n"
			echo -ne "${bold}${red}and the final file can has with errors${nc} \n\n\n"
		else
			echo -ne "\n\n"
		fi

	fi
	
	cd $mainPath/rendercheck

	#filename=$(awk 'END{print NR-1}' RS="/" /tmp/rfile)
	#if [ "$filename" = 0 ]; then export summary="$1"; else export summary=$("$1" | awk -v M=$(( filename+ 1 )) -F"/" '{print $M}') # where summary is the file's name
	
	# Deleting unnecessary lines from summary file
	cat summary | grep -ve "rendercheck" -ve "Found server" -ve "Script started" -ve "Script done" > 1
	rm summary &> /dev/null; mv 1 summary &> /dev/null

	cat -n summary > summaryl
	#if [ -z $1 ]; then echo -ne " > rendercheck has finish - Execution time : $varhours $varminutes $varseconds \n"; fi
	if [ ! -z "$varhours" ] || [ ! -z "$varminutes" ] || [ ! -z "$varseconds" ]; then echo -ne " --> ${yellow}${underline}rendercheck has finish${nc} - Execution time : $varhours $varminutes $varseconds \n"; fi
	echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
	start_time
	start_spinner "++ Generating TRC report ... "
	file=rendercheck_results_tmp.csv
	if  [ -f $file ]; then rm $file;fi

	# Counting the total lines
	export total_lines=$(cat -n summary | wc -l)
	export ten=$(( 10 * total_lines / 100 ))
	export twenty=$(( 20 * total_lines / 100 ))
	export thirty=$(( 30 * total_lines / 100 ))
	export fourty=$(( 40 * total_lines / 100 ))
	export fifty=$(( 50 * total_lines / 100 ))
	export sixty=$(( 60 * total_lines / 100 ))
	export seventy=$(( 70 * total_lines / 100 ))
	export eighty=$(( 80 * total_lines / 100 ))
	export ninety=$(( 90 * total_lines / 100 ))
	export hundred=$(( 100 * total_lines / 100 ))


	while read line 
	do

		linenumber=$(echo $line | awk '{print $1}')

		if [ "$linenumber" = "$ten" ]; then echo; echo -e " ${yellow}10%${nc} ..."; fi
		if [ "$linenumber" = "$twenty" ]; then echo; echo -e " ${yellow}20%${nc} ..."; fi
		if [ "$linenumber" = "$thirty" ]; then echo -e " ${yellow}30%${nc} ..."; fi
		if [ "$linenumber" = "$fourty" ]; then echo -e " ${cyan}40%${nc} ..."; fi
		if [ "$linenumber" = "$fifty" ]; then echo -e " ${cyan}50%${nc} ..."; fi
		if [ "$linenumber" = "$sixty" ]; then echo -e " ${cyan}60%${nc} ..."; fi
		if [ "$linenumber" = "$seventy" ]; then echo -e " ${cyan}70%${nc} ..."; fi
		if [ "$linenumber" = "$eighty" ]; then echo -e " ${blue}80%${nc} ..."; fi
		if [ "$linenumber" = "$ninety" ]; then echo -e " ${blue}90%${nc} ..."; fi
		if [ "$linenumber" = "$hundred" ]; then echo -e " ${blue}100%${nc} ..."; echo; fi


		nextline=$(( linenumber+ 1 ))
		verify=$(awk 'NR=='$nextline'' summary | awk '{print $1}')  # This means beginning
		onlyname=$(sed -n ${linenumber}p summary)

		verify2=$(awk 'NR=='$nextline'' summary | awk '{print $2}')

		if [ "$verify" == "Beginning" ] || [ "$verify2" == "tests" ]; then
			echo -ne "$onlyname,pass, \n" >> rendercheck_results_tmp.csv
		elif [ "$verify" != "Beginning" ] && [ "$verify" != "" ] && [ "$verify2" != "tests" ]; then
			echo -ne "$onlyname,fail, \n" >> rendercheck_results_tmp.csv
		fi

	done < summaryl

	# Getting the results
	mkdir -p /home/$CUSER/Desktop/results/rendercheck/ &> /dev/null
	echo "Component,Name,Status,Bug,Comment," > /home/$CUSER/Desktop/results/rendercheck/rendercheck_WW$weekn-$hour.csv
	
	cat rendercheck_results_tmp.csv | grep -w Beginning | grep pass | awk -F"Beginning " '{print $2}' > passfile
	while read line;do echo -ne "Rendercheck,$line, \n" >> /home/$CUSER/Desktop/results/rendercheck/rendercheck_WW$weekn-$hour.csv;done < passfile

	cat rendercheck_results_tmp.csv | grep -w Beginning | grep fail | awk -F"Beginning " '{print $2}' > failfile
	while read line;do echo -ne "Rendercheck,$line, \n" >> /home/$CUSER/Desktop/results/rendercheck/rendercheck_WW$weekn-$hour.csv;done < failfile

	# cleaning files
	s1=$mainPath/summary
	s2=$mainPath/summaryl
	if [ -f "$s1" ]; then rm $s1;fi
	if [ -f "$s2" ]; then rm $s2;fi

	stop_spinner $?

	# Statistics
	totaltests=$(cat /home/$CUSER/Desktop/results/rendercheck/rendercheck_WW$weekn-$hour.csv | wc -l )
	passedtests=$(cat /home/$CUSER/Desktop/results/rendercheck/rendercheck_WW$weekn-$hour.csv | grep pass | wc -l )
	failedtests=$(cat /home/$CUSER/Desktop/results/rendercheck/rendercheck_WW$weekn-$hour.csv | grep fail | wc -l )
	totaltests=$(cat /home/$CUSER/Desktop/results/rendercheck/rendercheck_WW$weekn-$hour.csv | grep -v "Component" |wc -l )
	passrate=$(echo "scale =2; $passedtests*100/$totaltests" | bc)
	
	echo -ne "\n\n"
	echo -ne " --- Summary --- \n" | tee /home/$CUSER/Desktop/results/rendercheck/summary-rendercheck_WW$weekn-$hour.csv
	echo -ne "  > Total tests   : [$totaltests] \n" | tee -a /home/$CUSER/Desktop/results/rendercheck/summary-rendercheck_WW$weekn-$hour.csv
	echo -ne "  > Passed tests  : [${green}$passedtests${nc}] \n" | tee -a /home/$CUSER/Desktop/results/rendercheck/summary-rendercheck_WW$weekn-$hour.csv
	echo -ne "  > Failed tests  : [${red}$failedtests${nc}] \n" | tee -a /home/$CUSER/Desktop/results/rendercheck/summary-rendercheck_WW$weekn-$hour.csv
	echo -ne "  > Pass rate     : [${blue}$passrate%${nc}] \n" | tee -a /home/$CUSER/Desktop/results/rendercheck/summary-rendercheck_WW$weekn-$hour.csv
	echo
	stop_time "Time elapsed"
	echo

	# Creating a folder for the current execution
	mkdir -p /home/$CUSER/Desktop/results/rendercheck/rendercheck_WW$weekn-$hour &> /dev/null
	# Moving the files created by the report
	mv /home/$CUSER/Desktop/results/rendercheck/summary-rendercheck_WW$weekn-$hour.csv /home/$CUSER/Desktop/results/rendercheck/rendercheck_WW$weekn-$hour &> /dev/null
	mv /home/$CUSER/Desktop/results/rendercheck/rendercheck_WW$weekn-$hour.csv /home/$CUSER/Desktop/results/rendercheck/rendercheck_WW$weekn-$hour &> /dev/null

	echo -ne " ${bold}${yellow}a report was generate in the folder ${nc}  --> [Desktop/results/rendercheck/rendercheck_WW$weekn-$hour] \n\n\n"s
	exit 2

}



function usage {
	
	echo -ne "\n\n"
    echo -ne " Usage : $me [options] \n\n"
    echo -ne "	-m <file1.csv> <file2.csv>	Merge 2 CSVs files \n"
    echo -ne "	-c <path to file>         	Create a CSV TRC report from a given file \n"
    echo -ne "	-i (interactive mode)		Select a file to create a report (only under X window) \n\n\n" 
    exit 2

}


function run {

	clear

	if [[ "$1" = "specify" ]]; then
		version=$($rendercheckpath/rendercheck --version)
		$mainPath/rendercheck/rendercheck -h 2> $mainPath/rendercheck/availabletests && echo -ne "\n\n"
		echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
		echo -ne " Version : [${cyan}${version}${nc}] \n\n" 
		sed -n 5,9p $mainPath/rendercheck/availabletests
		echo -ne "\n\n"
		read -p " > Type the test to run separate by [,] : " tests
		export tests
		#validate=$(echo "$tests" | grep -e "composite" -e "cacomposite" -e "blend" -e "repeat" -e "gradients") # This test opens a graphic window, doesn't display text to standard output

		#if [ ! -z "$validate" ]; then
		sleep 2
		echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
		echo -ne " > ./rendercheck -t $tests \n\n\n"
		# Counting the time that run the the next command
		export date1=$(date +"%s")
		sleep 3	
		script $mainPath/rendercheck/summary bash -c '$mainPath/rendercheck/rendercheck -t $tests'
			
			check=$(cat $mainPath/rendercheck/summary | grep usage)
			if [ ! -z "$check" ]; then echo -ne " > Something is wrong, please recheck the entered tests \n\n";exit 2; fi

			if [ $? = 0 ] || [ $? = 1 ]; then 
				dos2unix -f $mainPath/rendercheck/summary &> /dev/null
				report "file" "$mainPath/rendercheck/summary"
			else 
				echo -ne "\n\n\n"
				echo -ne " ${bold}`tput setf 4`[ >> RENDERCHECK DID NOT FINISH AS EXPECTED << ]${nc} \n"
				echo -ne "\n\n\n"
				exit 2
			fi   #rendercheck has two possible exit status 0 and 1

	fi


	if [[ "$1" = "all" ]]; then
		echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
		echo -ne " > ./rendercheck \n\n\n"
		 # Counting the time that run the the next command
		export date1=$(date +"%s")	
		sleep 3
		script $mainPath/rendercheck/summary bash -c '$mainPath/rendercheck/rendercheck'
		check=$(cat $mainPath/rendercheck/summary | grep usage)
				if [ ! -z "$check" ]; then echo -ne " > Something is wrong with rendercheck \n\n";exit 2;fi

		#wait # until script command finish
		
		if [ $? = 0 ] || [ $? = 1 ]; then 
			dos2unix -f $mainPath/rendercheck/summary &> /dev/null
			report "file" "$mainPath/rendercheck/summary"
		else 
			echo -ne "\n\n\n"
			echo -ne " ${bold}`tput setf 4`[ >> RENDERCHECK DID NOT FINISH AS EXPECTED << ]${nc} \n"
			echo -ne "\n\n\n"
			exit 2
		fi   #rendercheck has two possible exit status 0 and 1

	fi


	if [[ "$1" = "except" ]]; then
		echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
		echo -ne " > ./rendercheck -t fill,dcoords,scoords,mcoords,tscoords,tmcoords,blend,repeat,triangles,bug7366,gtk_argb_xbgr,libreoffice_xrgb,shmblend \n\n\n"
		# Counting the time that run the the next command
		export date1=$(date +"%s")	
		sleep 3
		script $mainPath/rendercheck/summary bash -c '$mainPath/rendercheck/rendercheck -t fill,dcoords,scoords,mcoords,tscoords,tmcoords,blend,repeat,triangles,bug7366,gtk_argb_xbgr,libreoffice_xrgb,shmblend'
		check=$(cat $mainPath/rendercheck/summary | grep usage)
			if [ ! -z "$check" ]; then echo -ne " > Something is wrong, please recheck the entered tests \n\n";exit 2;fi


		if [ $? = 0 ] || [ $? = 1 ]; then 
			dos2unix -f $mainPath/rendercheck/summary &> /dev/null
			report "file" "$mainPath/rendercheck/summary"
		else 
			echo -ne "\n\n\n"
			echo -ne " ${bold}`tput setf 4`[ >> RENDERCHECK DID NOT FINISH AS EXPECTED << ]${nc} \n"
			echo -ne "\n\n\n"
			exit 2
		fi   #rendercheck has two possible exit status 0 and 1

	fi


}


function select_run {

	if [ -d "$rendercheckpath" ] && [ -f "$renderfile" ]; then

			pause(){
				local m="$@"
        		echo "$m"
			}

		while :
		do
			clear
			version=$($rendercheckpath/rendercheck --version)
			echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
			echo -ne " Version : [$version] \n\n\n"
			echo -ne " ${bold}${cyan}====================================================================${nc} \n"
			echo -ne "  - You can run all tests of only part of them \n"
			echo -ne "  - Remeber always run by separate the following tests \n"
			echo -ne "  - ${bold}${yellow}[ > COMPOSITE / CACOMPOSITE < ]${nc} & ${bold}${yellow}[ > GRADIENTS < ]${nc} \n"
			echo -ne " ${bold}${cyan}====================================================================${nc} \n\n\n"

			echo -ne " 1) Run all tests \n"
			echo -ne " 2) Run only specify tests \n" 
            echo -ne " 3) Run all (${yellow}except composite, cacomposite. gradients${nc}) \n\n"
			read -p " Your choice : " choose

					case $choose in
						1) run "all" ;;
						2) run "specify" ;;
						3) run "except" ;;
						*) pause ;;
					esac 
				
		done

	else 

			pause(){
				local m="$@"
        		echo "$m"
			}

			while :
			do
				clear ; echo -ne "\n\n"
				echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
				echo -ne " The folder rendercheck not exists, building rendercheck from scratch \n\n"
				echo -ne " Select one option \n\n"
				echo -ne " 1) Rendercheck for Installer Release \n"
				echo -ne " 2) Rendercheck for Graphics Stack \n\n"
				read -p " Your choice: " choose

				case $choose in

					1) export varprefix=/usr; break ;;

					2) export varprefix=/opt/X11R7; break ;;

					3) pause ;;

				esac


			done



		echo -ne "\n\n"; echo -ne " ${bold}${yellow}Building rendercheck from scratch${nc} \n\n"

			if [ -f "/home/$CUSER/.dependencies-rendercheck" ]; then 
				echo -e " ${bold}${green}dependencies are already installed${nc}"
			else
				ip=$(ifconfig | awk '/inet addr/{print substr($2,6)}' | grep -v "^127")
				if [[ $ip =~ ^19 ]]; then connection=${green}SEDLINE${nc}; else connection=${cyan}INTRANET${nc}; fi

				echo -ne " ${blue}IP${nc} : [${bold}$ip${nc}] [$connection] \n\n"	

				start_spinner "++ Installing dependencies ... "
					echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 3
					echo $PASSWORD | sudo -S apt-get update -q=2 &> /dev/null # do this in order to allow install unauthenticated packages like "dh-autoreconf"
					echo $PASSWORD | sudo -S apt-get install dh-autoreconf -q=2 &> /dev/null
					echo $PASSWORD | sudo -S apt-get install xutils-dev -q=2 &> /dev/null
					echo $PASSWORD | sudo -S apt-get install libx11-xcb-dev -q=2 &> /dev/null
					echo $PASSWORD | sudo -S apt-get install x11proto-dri2-dev -q=2 &> /dev/null
					echo $PASSWORD | sudo -S apt-get install x11proto-dri3-dev -q=2 &> /dev/null
					echo $PASSWORD | sudo -S apt-get install x11proto-xf86dri-dev -q=2 &> /dev/null
					echo $PASSWORD | sudo -S apt-get install x11proto-gl-dev -q=2 &> /dev/null
					echo $PASSWORD | sudo -S apt-get install x11proto-present-dev -q=2 &> /dev/null
					echo $PASSWORD | sudo -S apt-get install x11proto-gl-dev -q=2 &> /dev/null
					echo $PASSWORD | sudo -S apt-get install x11proto-dri3-dev -q=2 &> /dev/null
					echo $PASSWORD | sudo -S apt-get install x11proto-present-dev -q=2 &> /dev/null
					echo $PASSWORD | sudo -S apt-get install libxrender1 -q=2 &> /dev/null
					echo $PASSWORD | sudo -S apt-get install libxrender-dev -q=2 &> /dev/null
				stop_spinner $? | tee .log
				unset check
				check=$(cat .log | grep "FAIL")

				if [ -z "$check" ]; then
					touch /home/$CUSER/.dependencies-rendercheck &> /dev/null
				else
					echo -ne "\n\n"; echo " ${bold}${yellow}something is wrong, maybe dpkg is lock${nc}"; echo " ${bold}${yellow}Please restart the DUT and run again this script${nc}"; echo -ne "\n\n"; exit 2
				fi	

			fi

				# adding proxy settings in order to clone rendercheck
				# exec $mainPath/tools/git-proxy.sh & 
				# wait # for the script finish 

				start_spinner "++ git clone http://anongit.freedesktop.org/git/xorg/app/rendercheck.git ... "
					echo; echo $PASSWORD | sudo -S ls -l &> /dev/null; sleep 3
					#cd $mainPath; git clone git://anongit.freedesktop.org/xorg/app/rendercheck &> /dev/null
					cd $mainPath; git clone http://anongit.freedesktop.org/git/xorg/app/rendercheck.git ./rendercheck &> /dev/null
				stop_spinner $? | tee .log
	
				unset check
				check=$(cat .log | grep "FAIL")
					if [ ! -z "$check" ]; then echo -ne "++ ${red}Could not clone rendercheck${nc} \n\n\n"; exit 2; fi

				cd $mainPath/rendercheck/
				start_spinner "++ ./autogen.sh --prefix=$varprefix ... "
					./autogen.sh --prefix=$varprefix &> /dev/null
				stop_spinner $? | tee .log
				unset check
				check=$(cat .log | grep "FAIL")

					if [ ! -z "$check" ]; then echo -ne "++ Debug :(${red}autogen${nc}) command was not successfully \n\n\n"; exit 2; fi

				export x=$(nproc --all)
				export totalcores=$(( x + 2 ))

				start_spinner "++ make -j$totalcores ... "
					make -j$totalcores  &> /dev/null
				stop_spinner $? | tee .log
				unset check
				check=$(cat .log | grep "FAIL")

					if [ ! -z "$check" ]; then echo -ne "++ Debug : (${red}make -j$totalcores${nc}) command was not successfully \n\n\n"; exit 2; fi				
				
				start_spinner "++ sudo make install ... "
					echo $PASSWORD | sudo -S make install  &> /dev/null
				stop_spinner $? | tee .log
				unset check
				check=$(cat .log | grep "FAIL")				

					if [ ! -z "$check" ]; then echo -ne "++ Debug : (${red}sudo make install${nc}) command was not successfully \n\n\n"; exit 2; fi				

				sleep 5; cd $mainPath; select_run

	fi

}

# Put this before test command in order to call functions from another script 
# NOTICE THAT THIS PARAMETER MUST BE BELOW ALL THE FUNCTIONS AS WELL THE TEST COMMAND BELOW
$@ #2> /dev/null
clear

while test $# != 0
do
	case $1 in
		-h | --help ) usage ;;
		-m | --merge ) 

			if [ -z "$2" ] && [ -z "$3" ]; then echo -ne " > You must need specify two CSVs files \n\n";usage;fi 
			if [ -z "$2" ] && [ ! -z "$3" ]; then echo -ne " > You must need specify two CSVs files \n\n"; echo "file 1 is empty";usage;fi  # this condition never will meet
			if [ ! -z "$2" ] && [ -z "$3" ]; then echo -ne " > You must need specify two CSVs files : "; echo -ne "File 2 is empty \n\n";usage;fi 

			# Cheking if those files are CSVs
 			#zenity=$(dpkg -l zenity 2> /dev/null)
			#if [ -z "$checkzenity" ]; then echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 5; echo $PASSWORD | sudo -S apt-get install zenity -q=2 &> /dev/null; fi
			checkfile1=$(echo "$2" | sed 's/.*\(....\)/\1/')
			checkfile2=$(echo "$3" | sed 's/.*\(....\)/\1/')

			if [[ "$checkfile1" != ".csv" || "$checkfile2" != ".csv" ]]; then echo -ne "\n\n"; echo -ne " ${bold}`tput setf 4`The given files are not CSVs files${nc}"; echo -ne ", please specify 2 valid CSVs files "; echo -ne "\n\n"; exit 2; fi
			
			# Checking if the files exist and arent empty
			if [ ! -f "$2" ]; then echo -ne "\n\n"; echo -ne " ${bold}`tput setf 6`The given file [$2] does not exist${nc} \n"; echo -ne "\n\n"; exit 2; elif [ -f "$2" ] && [ ! -s "$2" ]; then echo -ne "\n\n"; echo -ne " ${bold}`tput setf 6`The file [$2] exits but is empty${nc} \n"; echo -ne "\n\n"; exit 2; fi
			if [ ! -f "$3" ]; then echo -ne "\n\n"; echo -ne " ${bold}`tput setf 6`The given file [$3] does not exist${nc} \n"; echo -ne "\n\n"; exit 2; elif [ -f "$3" ] && [ ! -s "$3" ]; then echo -ne "\n\n"; echo -ne " ${bold}`tput setf 6`The file [$3] exits but is empty${nc} \n"; echo -ne "\n\n"; exit 2; fi


			echo -ne "\n\n"
			clear
			echo -ne "\n\n"
			start_spinner ' > Merging CSVs files ...'
			cat $2 | grep -v "Component,Name,Status,Bug,Comment" > /tmp/file1.csv
			cat $3 | grep -v "Component,Name,Status,Bug,Comment" > /tmp/file2.csv
			# Merging
			mkdir -p /home/$CUSER/Desktop/results/rendercheck/merge-results
			cat /tmp/file1.csv /tmp/file2.csv > /home/$CUSER/Desktop/results/rendercheck/merge-results/rendercheck_merge_WW$weekn-$hour.csv
			sed -i '1i Component,Name,Status,Bug,Comment' /home/$CUSER/Desktop/results/rendercheck/merge-results/rendercheck_merge_WW$weekn-$hour.csv
			sleep 10
			stop_spinner $?

			# Statistics
			totaltests=$(cat /home/$CUSER/Desktop/results/rendercheck/merge-results/rendercheck_merge_WW$weekn-$hour.csv | wc -l )
			passedtests=$(cat /home/$CUSER/Desktop/results/rendercheck/merge-results/rendercheck_merge_WW$weekn-$hour.csv | grep pass | wc -l )
			failedtests=$(cat /home/$CUSER/Desktop/results/rendercheck/merge-results/rendercheck_merge_WW$weekn-$hour.csv | grep fail | wc -l )
			totaltests=$(cat /home/$CUSER/Desktop/results/rendercheck/merge-results/rendercheck_merge_WW$weekn-$hour.csv | grep -v "Component" |wc -l )
			passrate=$( echo "scale =2; $passedtests*100/$totaltests" | bc)

			echo -ne "\n\n"
			echo -ne " ===== Summary ===== \n" | tee /home/$CUSER/Desktop/results/rendercheck/merge-results/summary-rendercheck_merge_WW$weekn-$hour.csv
			echo -ne "  - Total tests   : [$totaltests] \n" | tee -a /home/$CUSER/Desktop/results/rendercheck/merge-results/summary-rendercheck_merge_WW$weekn-$hour.csv
			echo -ne "  - Passed tests  : [${green}$passedtests${nc}] \n" | tee -a /home/$CUSER/Desktop/results/rendercheck/merge-results/summary-rendercheck_merge_WW$weekn-$hour.csv
			echo -ne "  - Failed tests  : [${red}$failedtests${nc}] \n" | tee -a /home/$CUSER/Desktop/results/rendercheck/merge-results/summary-rendercheck_merge_WW$weekn-$hour.csv
			echo -ne "  - Pass rate     : [${blue}$passrate%${nc}] \n\n" | tee -a /home/$CUSER/Desktop/results/rendercheck/merge-results/summary-rendercheck_merge_WW$weekn-$hour.csv
			echo -ne " ++ a merge file was create in --> [Desktop/results/rendercheck/merge-results/rendercheck_merge_WW$weekn-$hour.csv] \n"
			echo -ne " ++ a summary was generate in  --> [Desktop/results/rendercheck/merge-results/summary-rendercheck_merge_WW$weekn-$hour.csv] \n"
			echo -ne "\n\n"
			exit 2
			;;

		-c | --create )
			echo -ne "\n\n"; clear; echo -ne "\n\n"; report "file" "$2" ;;

		-i | --interactive ) 
			checkTTY=$(tty | awk -F"/dev/" '{print $2}')
			if [ ! -z "$SSH_CLIENT" ] || [ ! -z "$SSH_TTY" ] || [[ "$checkTTY" = "tty1"  || "$checkTTY" = "tty2" || "$checkTTY" = "tty3" || "$checkTTY" = "tty4" || "$checkTTY" = "tty5" || "$checkTTY" = "tty6" ]]; then
				# Under SSH
				echo -ne "\n\n"
				echo -ne "+++++++++++++++++++++++++++++++++++++++++++++++ \n"
				echo -ne " --> This option only run in Graphical mode <-- \n"
				echo -ne "+++++++++++++++++++++++++++++++++++++++++++++++ \n\n"
				exit 2

			else	
				path=$(zenity --file-selection --filename=/home/$CUSER/ 2> /dev/null)

				if [ ! -z "$path" ]; then
					clear; echo -ne "\n\n"; echo -ne "Intel® Graphics for Linux* | 01.org \n\n\n"; report "file" "$path"
				else
					zenity --error --title "Intel® Graphics for Linux* | 01.org" --text="You did not choose any file" 2> /dev/null; wait; exit 2
				fi
			fi
			;;

	esac
    	
done


if [ -z "$1" ]; then select_run; fi
