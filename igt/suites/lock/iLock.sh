#!/bin/bash

# ===========================================
# Variables 
# ===========================================
thispath=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
Me=`basename $0`
PostFile="/home/shared/suites/fastfeedback/post.py"
dataScript="/home/shared/suites/fastfeedback/getdata.py"


# ===========================================
# source scripts                      
# ===========================================
source /home/shared/suites/dev/igt/tools/functions.sh

function usage () {
    echo -ne " Usage : ${yellow}${Me}${nc} [options] \n\n"
    echo -e " (-h|-help)                                          : see this menu"
    echo -e " (lock|unlock) + raspberry number + switch number    : (lock|unlock platform)"
    echo -e  "  --> raspberry number values : [1-2]"
    echo -ne  "  --> switch number values    : [1-8] \n\n"
    echo -e "(lockA|unlockA) + file                               : (lock|unlock hostnames)"
    echo -ne  "  --> file must contains the hostnames \n\n"
}

function singleLock () {

	raspberry="$1"; switch="$2"

	case ${raspberry} in 
		1) oldStatus=`python ${dataScript} | head -8 | sed -n ${switch}p | awk '{print $9}'` ;;
		2) oldStatus=`python ${dataScript} | tail -8 | sed -n ${switch}p | awk '{print $9}'` ;;
	esac

	if [ "${oldStatus}" = "busy" ]; then
		echo -ne "--> ${yellow}this switch is already lock${nc} \n\n"; exit 1

	elif [ "${oldStatus}" = "available" ]; then

		oldStatus=`echo -e ${green}available${nc}`
		echo "--> old status : [${oldStatus}]"
		# Creating the python file to send a get to db
		echo "import requests" > ${PostFile}
		echo "try:" >> ${PostFile}
		echo '  r = requests.get("http://bifrost.intel.com:2020/power/busy-'${raspberry}'-'${switch}'")' >> ${PostFile}
		echo "except:" >> ${PostFile}
		echo '  print "--> Could not connect to database"'>> ${PostFile}

		start_spinner "--> locking switch : [${switch}] on raspberry [${raspberry}] ..."
		    sleep .5; python ${PostFile}
		stop_spinner $?

		case ${raspberry} in 
			1) newStatus=`python ${dataScript} | head -8 | sed -n ${switch}p | awk '{print $9}'` ;;
			2) newStatus=`python ${dataScript} | tail -8 | sed -n ${switch}p | awk '{print $9}'` ;;
		esac

		if [ "${newStatus}" = "busy" ]; then 
			newStatus=`echo -e ${red}busy${nc}`
			echo "--> new status : [${newStatus}]"
			exit 1
		else
			echo -e "${red}-->${nc} ${yellow}something was wrong${nc} blocking the switch [${switch}] on the raspberry [${raspberry}]"
		fi
	fi
}

function singleUnlock () {
	raspberry="$1"; switch="$2"

	case ${raspberry} in 
		1) oldStatus=`python ${dataScript} | head -8 | sed -n ${switch}p | awk '{print $9}'` ;;
		2) oldStatus=`python ${dataScript} | tail -8 | sed -n ${switch}p | awk '{print $9}'` ;;
	esac

	if [ "${oldStatus}" = "available" ]; then
		echo -ne "--> ${yellow}this switch is already unlock${nc} \n\n"; exit 1

	elif [ "${oldStatus}" = "busy" ]; then

		oldStatus=`echo -e ${red}busy${nc}`
		echo "--> old status : [${oldStatus}]"
		# Creating the python file to send a get to db
		echo "import requests" > ${PostFile}
		echo "try:" >> ${PostFile}
		echo '  r = requests.get("http://bifrost.intel.com:2020/power/free-'${raspberry}'-'${switch}'")' >> ${PostFile}
		echo "except:" >> ${PostFile}
		echo '  print "--> Could not connect to database"'>> ${PostFile}

		start_spinner "--> unlocking switch : [${switch}] on raspberry [${raspberry}] ..."
		    sleep .5; python ${PostFile}
		stop_spinner $?

		case ${raspberry} in 
			1) newStatus=`python ${dataScript} | head -8 | sed -n ${switch}p | awk '{print $9}'` ;;
			2) newStatus=`python ${dataScript} | tail -8 | sed -n ${switch}p | awk '{print $9}'` ;;
		esac

		if [ "${newStatus}" = "available" ]; then 
			newStatus=`echo -e ${green}available${nc}`
			echo "--> new status : [${newStatus}]"
			exit 1
		else
			echo -e "${red}-->${nc} ${yellow}something was wrong${nc} unblocking the switch [${switch}] on the raspberry [${raspberry}]"
		fi
	fi
}

function lockAll () {

	source "$1"

	for hostname in ${Raspberry01} ${Raspberry02}; do

		unset raspberry switchNumber switchStatus
		raspberry=`python ${dataScript} | grep -w ${hostname} | awk '{print $1}'`
		switch=`python ${dataScript} | grep -w ${hostname} | awk '{print $3}'`
		switchStatus=`python ${dataScript} | grep -w ${hostname} | awk '{print $9}'`
		if [ "${switchStatus}" = "busy" ]; then
			echo -e "[${hostname}] is already ${yellow}locked${nc}"
		elif [ "${switchStatus}" = "available" ]; then
			# Creating the python file to send a get to db
			echo "import requests" > ${PostFile}
			echo "try:" >> ${PostFile}
			echo '  r = requests.get("http://bifrost.intel.com:2020/power/busy-'${raspberry}'-'${switch}'")' >> ${PostFile}
			echo "except:" >> ${PostFile}
			echo '  print "--> Could not connect to database"'>> ${PostFile}

			start_spinner "--> locking hostname [${hostname}] ..."
			    sleep .5; python ${PostFile}
			stop_spinner $?

			unset switchStatus
			switchStatus=`python ${dataScript} | grep -w ${hostname} | awk '{print $9}'`

			if [ "${switchStatus}" = "busy" ]; then
				echo -e "--> [${hostname}] status : [${red}locked${nc}]"
			elif [ "${switchStatus}" = "available" ]; then
				echo -e "${red}-->${nc} ${yellow}something was wrong${nc} blocking [${hostname}]"
			fi
		fi

	done

}

function unlockAll () {
	source "$1"

	for hostname in ${Raspberry01} ${Raspberry02}; do

		unset raspberry switchNumber switchStatus
		raspberry=`python ${dataScript} | grep -w ${hostname} | awk '{print $1}'`
		switch=`python ${dataScript} | grep -w ${hostname} | awk '{print $3}'`
		switchStatus=`python ${dataScript} | grep -w ${hostname} | awk '{print $9}'`
		if [ "${switchStatus}" = "available" ]; then
			echo -e "[${hostname}] is already ${yellow}unlock${nc}"
		elif [ "${switchStatus}" = "busy" ]; then
			# Creating the python file to send a get to db
			echo "import requests" > ${PostFile}
			echo "try:" >> ${PostFile}
			echo '  r = requests.get("http://bifrost.intel.com:2020/power/free-'${raspberry}'-'${switch}'")' >> ${PostFile}
			echo "except:" >> ${PostFile}
			echo '  print "--> Could not connect to database"'>> ${PostFile}

			start_spinner "--> unlocking hostname [${hostname}] ..."
			    sleep .5; python ${PostFile}
			stop_spinner $?

			unset switchStatus
			switchStatus=`python ${dataScript} | grep -w ${hostname} | awk '{print $9}'`

			if [ "${switchStatus}" = "available" ]; then
				echo -e "--> [${hostname}] status : [${green}unlocked${nc}]"
			elif [ "${switchStatus}" = "busy" ]; then
				echo -e "${red}-->${nc} ${yellow}something was wrong${nc} unlocking [${hostname}]"
			fi
		fi

	done
}


Option="$1"

case "${Option}" in 
	help|h) usage ;;
	lock) singleLock "$2" "$3" ;;
	unlock) singleUnlock "$2" "$3" ;;
	lockA) lockAll "$2";;
	unlockA) unlockAll "$2" ;;
	*) usage ;;
esac


# /home/hiperezr/bkp/dev/igt/suites/fastfeedback/whitelist