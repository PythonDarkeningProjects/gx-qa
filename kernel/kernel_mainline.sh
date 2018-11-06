#!/bin/bash

# Filename : kernel_mainline.sh
#
#
#
# Notes : 
# characters that are not allowed in the name :  character '_' not allowed
# upper case are not allowed
#
# shows the info from a specific commit but only is the commit is already in the branch
# git show --name-only <commit>

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

	### Setting the global variables
	export maindate1=$(date +"%s")
	weekn=$(date +"%-V") # with this simbol '-' i can eliminite the 0 to do calculations
	export weekn=$(( weekn + 1 ))
	export month=$(date +"%b")
	export month=$(echo $month | tr "[:upper:]" "[:lower:]")  # convert month to lowercase
	export weekday=$(date +"%u")
	export age=$(date +"%G")
	export fday=$(date +"%d")
	export fullday=$(date +"%A")
	export hour=$(date +%I:%M:%S)
	export me=`basename $0`
	export thispath=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
	export processorn=$(cat /proc/cpuinfo | grep processor | wc -l)
	export x=$processorn
	export y=2
	export totalcores=$(( x + y ))
	export GIT_SSL_NO_VERIFY=1
	### Setting the global variables

	######################## < Optional proxy configuration> ########################
	# This proxy configuration works under ssh and ubuntu 15 for git
	# Proxy configuration
	 export ALL_PROXY=socks://proxy-socks.fm.intel.com:1080
	 export all_proxy=socks://proxy-socks.fm.intel.com:1080
	 export http_proxy=http://proxy.fm.intel.com:911
	 export https_proxy=https://proxy.fm.intel.com:911
	 export ftp_proxy=ftp://proxy.fm.intel.com:911
	 export socks_proxy=socks://proxy-socks.fm.intel.com:1080
	 export no_proxy=localhost,.intel.com,127.0.0.0/8,192.168.0.0/16,10.0.0.0/8
	######################## < Optional configuration> ########################
	

function start_time {

	unset date1
	date1=$(date +"%s")

}

function stop_time {

	unset date2 diff minutes seconds hours varhours varminutes varseconds
	date2=$(date +"%s")
	diff=$(($date2-$date1))   # <-- There is seconds
	minutes=$((($diff / 60)))
	seconds=$((($diff % 60)))
	hours=$((($minutes / 60)))

	if [ $hours != 0 ]; then varhours=$(echo "$hours Hours"); fi
	if [ $minutes != 0 ]; then varminutes=$(echo "$minutes Minutes"); fi
	if [ $seconds != 0 ]; then varseconds=$(echo "$seconds Seconds"); fi

	echo "++ $1 : $varhours $varminutes $varseconds "
	
}

function start_time_kernel {

	unset date1
	date1=$(date +"%s")

}

function stop_time_kernel {

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
            else
                echo -en "${red}${on_fail}${nc}"
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


# Checking for empty line in 
file2c=.compare_last_mainline
path2c=/home/$CUSER/kernel

if [ -f "${path2c}/${file2c}" ]; then sed -i '/^$/d' ${path2c}/${file2c}; fi


function notification_new_commit {

	### Getting the total time ###
	maindate2=$(date +"%s")
	diff=$(($maindate2-$maindate1))   # <-- There is seconds
	minutes=$((($diff / 60)))
	seconds=$((($diff % 60)))
	hours=$((($minutes / 60)))

	if [ $hours != 0 ]; then varhours=$(echo "$hours Hours"); fi
	if [ $minutes != 0 ]; then varminutes=$(echo "$minutes Minutes"); fi
	if [ $seconds != 0 ]; then varseconds=$(echo "$seconds Seconds"); fi
	### Getting the total time ###
	path_deb=/home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel
	deb_size=($(du -sh ${path_deb}/deb_packages))
	user_email_list="humberto.i.perez.rodriguez@intel.com,jairo.daniel.miramontes.caton@intel.com,elio.martinez.monroy@intel.com,luis.botello.ortega@intel.com,maria.g.perez.ibarra@intel.com,florencio.navarro@intel.com,"

	start_spinner "++ Sending a notification ..."
		echo "Subject: a new mainline kernel was found from kernel.org [$month-WW$weekn-0$weekday-$hour]"					> /tmp/kernel_mainline_msg
		echo "From: kernel_watcher@automated.com" 																			>> /tmp/kernel_mainline_msg
		echo "To: ${user_email_list}"																						>> /tmp/kernel_mainline_msg
		echo -ne "\n\n" 																									>> /tmp/kernel_mainline_msg
		echo -ne " --> Branch : mainline \n"	 																			>> /tmp/kernel_mainline_msg
		echo -ne " --> Version : $kernel_version \n"																		>> /tmp/kernel_mainline_msg
		echo -ne " --> Architecture : $architecture \n"																		>> /tmp/kernel_mainline_msg
		echo -ne " --> Homepage : $home_page \n"																			>> /tmp/kernel_mainline_msg
		echo -ne "\n\n" 																									>> /tmp/kernel_mainline_msg
		echo -ne " --> Package list : \n\n" 																				>> /tmp/kernel_mainline_msg
		cat ${path_deb}/package_list																						>> /tmp/kernel_mainline_msg
		echo -ne "\n\n" 																									>> /tmp/kernel_mainline_msg
		echo -ne " --> deb packages size : [$deb_size] \n"																	>> /tmp/kernel_mainline_msg
		echo -ne "\n\n" 																									>> /tmp/kernel_mainline_msg
		echo -ne " This new mainline kernel is located in : \n"																>> /tmp/kernel_mainline_msg
		echo -ne " http://linuxgraphics.intel.com/kernels/mainline/$last_mainline_version/$last_mainline_kernel \n"			>> /tmp/kernel_mainline_msg
		echo -ne "\n\n" 																									>> /tmp/kernel_mainline_msg
		echo -ne "================================== \n"	 																>> /tmp/kernel_mainline_msg
		echo -ne " Total time : $varhours $varminutes $varseconds \n" 														>> /tmp/kernel_mainline_msg
		echo -ne "================================== \n\n"	 																>> /tmp/kernel_mainline_msg
		echo "This is an automated message from the kernel_watcher@automated.com server please do not reply" 				>> /tmp/kernel_mainline_msg
		echo -ne "\n\n" 																									>> /tmp/kernel_mainline_msg
		echo -ne "Project: 01.org Intel Open Source \n" 																	>> /tmp/kernel_mainline_msg
		echo -ne "Intel Graphics for Linux \n" 																				>> /tmp/kernel_mainline_msg
		# /usr/sbin/sendmail humberto.i.perez.rodriguez@intel.com < /tmp/kernel_nightly_msg
		/usr/sbin/sendmail -t < /tmp/kernel_mainline_msg # When needed several recipients
		# Reference : http://backreference.org/2013/05/22/send-email-with-attachments-from-script-or-command-line/
		wait; sleep 2
	stop_spinner $?
	echo -ne "\n\n"; exit 2

}


function notification_no_commit {

	user_email_list="humberto.i.perez.rodriguez@intel.com"

	start_spinner "++ Sending a notification ..."
		echo "Subject: Not new mainline kernel was found kernel.org [$month-WW$weekn-0$weekday-$hour]"			> /tmp/kernel_mainline_msg
		echo "From: kernel_watcher@automated.com"																>> /tmp/kernel_mainline_msg
		echo "To: ${user_email_list}"																			>> /tmp/kernel_mainline_msg
		echo -ne "\n\n" 																						>> /tmp/kernel_mainline_msg
		echo -ne " The latest mainline kernel version is : ${last_mainline_kernel} \n\n"						>> /tmp/kernel_mainline_msg
		echo "This is an automated message from the kernel_watcher@automated.com server please do not reply" 	>> /tmp/kernel_mainline_msg
		echo -ne "\n\n" 																						>> /tmp/kernel_mainline_msg
		echo -ne "Project: 01.org Intel Open Source \n" 														>> /tmp/kernel_mainline_msg
		echo -ne "Intel Graphics for Linux \n" 																	>> /tmp/kernel_mainline_msg
		# /usr/sbin/sendmail humberto.i.perez.rodriguez@intel.com < /tmp/kernel_nightly_msg
		/usr/sbin/sendmail -t < /tmp/kernel_mainline_msg # When needed several recipients
		wait; sleep 2
	stop_spinner $?
	echo -ne "\n\n"; exit 2

}

function notification_fail_to_build {

	start_spinner "++ Sending a notification ..."
		echo "Subject: kernel build error for mainline [$month-WW$weekn-0$weekday-$hour]"						> /tmp/kernel_mainline_msg
		echo "From: kernel_watcher@automated.com" 																>> /tmp/kernel_mainline_msg
		echo -ne "\n\n" 																						>> /tmp/kernel_mainline_msg
		echo -ne "an error was occurred when trying to compile the kernel"										>> /tmp/kernel_mainline_msg
		echo -ne "kernel : mainline"																			>> /tmp/kernel_mainline_msg
		echo -ne "\n\n" 																						>> /tmp/kernel_mainline_msg
		echo "This is an automated message from the kernel_watcher@automated.com server please do not reply" 	>> /tmp/kernel_mainline_msg
		echo -ne "\n\n" 																						>> /tmp/kernel_mainline_msg
		echo -ne "Project: 01.org Intel Open Source \n" 														>> /tmp/kernel_mainline_msg
		echo -ne "Intel Graphics for Linux \n" 																	>> /tmp/kernel_mainline_msg
		/usr/sbin/sendmail humberto.i.perez.rodriguez@intel.com < /tmp/kernel_mainline_msg
		wait; sleep 2
	stop_spinner $?
	echo -ne "\n\n"; exit 2

}


function build_mainline_kernel {

	clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
	start_time

	# For now we are using the latest config for skl of ubuntu 15 64bit
	export CONFIG_IN_USE=${thispath}/config_files/ubuntu_15.10_64bit/skl/config-4.2.0-16-generic

	if [ -d "/home/$CUSER/kernel/mainline" ]; then 
		start_spinner "++ Removing mainline folder ..."
			echo $PASSWORD | sudo -S ls &> /dev/null; sleep 3; echo $PASSWORD | sudo -S rm -r /home/$CUSER/kernel/mainline &> /dev/null
		stop_spinner $?
	fi

	start_time_kernel

	start_spinner "++ Downloading $last_mainline_kernel ..."
		mkdir -p /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel; cd /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel
		wget -np -nd -m -E -k -K -e robots=off -l 1 https://www.kernel.org/pub/linux/kernel/$last_mainline_version/$last_mainline_kernel.tar.gz &> /dev/null; wait
		# Uncompress the folder
		tar -xf /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/$last_mainline_kernel.tar.gz &> /dev/null
	stop_spinner $?

	size=($(du -sh /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/$last_mainline_kernel.tar.gz))
	stop_time_kernel "[$size] in"

	start_spinner "++ Copying SKL config to $last_mainline_kernel ..."
		sleep 2
		cp ${CONFIG_IN_USE} /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/$last_mainline_kernel/arch/x86/configs/mainline_defconfig  &> /dev/null
	stop_spinner $?

	start_spinner "++ Naming the kernel ..."
		export mainline_version=$(echo $last_mainline_kernel | sed 's/linux-//g')
		local_version_line=$(cat -n /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/$last_mainline_kernel/arch/x86/configs/mainline_defconfig | grep -w CONFIG_LOCALVERSION="" | awk '{print $1}')
		sed -i ''$local_version_line's/CONFIG_LOCALVERSION=""/CONFIG_LOCALVERSION="-mainline-ww'$weekn'-version-'$mainline_version'"/g' /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/$last_mainline_kernel/arch/x86/configs/mainline_defconfig &> /dev/null
	stop_spinner $?


	# Checking if CONFIG_DEBUG_INFO flag is set
	cat /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/$last_mainline_kernel/arch/x86/configs/mainline_defconfig | grep -w CONFIG_DEBUG_INFO="y" &> /tmp/config_debug_info_flag

		if [ $? = 0 ]; then
		
			# Setting CONFIG_DEBUG_INFO to false in order to no create a debug package for reduce the kernel's build time		
			start_spinner "++ Setting CONFIG_DEBUG_INFO to false ..."
				config_debug_line=$(cat -n /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/$last_mainline_kernel/arch/x86/configs/mainline_defconfig | grep -w CONFIG_DEBUG_INFO="y" | awk '{print $1}')
				sed -i ''$config_debug_line's/CONFIG_DEBUG_INFO=y/CONFIG_DEBUG_INFO=n/g' /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/$last_mainline_kernel/arch/x86/configs/mainline_defconfig &> /dev/null
			stop_spinner $?

		else
			echo
			echo "++ ${bold}${yellow}CONFIG_DEBUG_INFO is not set${nc} \n"
				if [ -f "/tmp/config_debug_info_flag" ]; then echo -ne "  the current value is : \n\n"; ${blue} cat /tmp/config_debug_info_flag ${nc}; echo -ne "\n\n"; fi
		fi

	# Cheking if CONFIG_DRM_AMDGPU flag if set
	cat /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/$last_mainline_kernel/arch/x86/configs/mainline_defconfig | grep -w CONFIG_DRM_AMDGPU=m &> /tmp/config_drm_amdgpu_flag

	if [ $? = 0 ]; then

		# Setting CONFIG_DRM_AMDGPU=m to false in order to build without issues drm-intel-nightly kernel
		start_spinner "++ Setting CONFIG_DRM_AMDGPU to false ..."
			config_drm_amdgpu_line=$(cat -n /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/$last_mainline_kernel/arch/x86/configs/mainline_defconfig | grep -w CONFIG_DEBUG_INFO="y" | awk '{print $1}')
			sed -i ''$config_drm_amdgpu_line's/CONFIG_DRM_AMDGPU=m/CONFIG_DRM_AMDGPU=n/g' /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/$last_mainline_kernel/arch/x86/configs/mainline_defconfig &> /dev/null
		stop_spinner $?

	else
		echo
		echo "++ ${bold}${yellow}CONFIG_DRM_AMDGPU is not set${nc} \n"
		if [ -f "/tmp/config_drm_amdgpu_flag" ]; then echo -ne "  the current value is : \n\n"; ${blue} cat /tmp/config_drm_amdgpu_flag ${nc}; echo -ne "\n\n"; fi

	fi


	start_spinner "++ Creating config file to build the kernel ..."
		# This command write the previous file into .config (for no use make manuconfig conmmand)
		cd /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/$last_mainline_kernel/ && make mainline_defconfig &> /dev/null
	stop_spinner $?

	start_spinner "++ Compiling the kernel ..."
		cd /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/$last_mainline_kernel/ && make -j${totalcores} deb-pkg &> /tmp/kernel_build_mainline.log
	stop_spinner $? | tee .log

	check=$(cat .log | grep "FAIL")

	if [ ! -z "$check" ]; then
		echo -ne "\n\n"
		echo -ne "++ ${bold}${red}an error was occurred when trying to compile the kernel${nc} \n\n"
			if [ -f "/tmp/kernel_build_mainline.log" ]; then
				cat /tmp/kernel_build_mainline.log | tail -n 50
				echo -ne "\n\n"
				notification_fail_to_build
			fi
	fi


	start_spinner "++ structuring the shared folder ..." 

		# Checking if exists ChangeLog version file to download it
		export number_version=$(echo $last_mainline_kernel | sed 's/linux-//g')
		changelog=$(w3m https://www.kernel.org/pub/linux/kernel/$last_mainline_version/ | awk '{print $1}' |  grep -w "ChangeLog-$number_version$")
		if [ ! -z "$changelog" ]; then
			cd /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/
			wget -np -nd -m -E -k -K -e robots=off -l 1 https://www.kernel.org/pub/linux/kernel/$last_mainline_version/$changelog &> /dev/null; wait
		fi

		# Checking if exists a patch to download it
		patch=$(w3m https://www.kernel.org/pub/linux/kernel/$last_mainline_version/ | awk '{print $1}' |  grep -w "patch-$number_version.xz")
		if [ ! -z "$patch" ]; then
			cd /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/
			wget -np -nd -m -E -k -K -e robots=off -l 1 https://www.kernel.org/pub/linux/kernel/$last_mainline_version/$patch &> /dev/null; wait	
		fi

		changes_file_path=/home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel
		changes_file=$(ls ${changes_file_path} | grep .changes$)

		export kernel_version=$(cat ${changes_file_path}/${changes_file} | grep -w "Version:" | awk '{print $2}' | sed 's/-mainline-ww'$weekn'-version-'$mainline_version'-1//g')  # Here i put (+-1) i need to investigate why ? maybe the make comand it wrote by default
		export architecture=$(cat ${changes_file_path}/${changes_file} | grep -w "Architecture:" | awk -F"Architecture: " '{print $2}')

		# Getting information from dsc file
		dsc_file=$(ls ${changes_file_path} | grep .dsc$)
		export home_page=$(cat ${changes_file_path}/${dsc_file} | grep -w "Homepage:" | awk -F"Homepage: " '{print $2}')
		cat ${changes_file_path}/${dsc_file} | egrep "^ linux-" > ${changes_file_path}/package_list  # <<-- package_list

		# Creating the folders
		# mkdir -p /home/$CUSER/kernel/deb_packages/mainline/$month-WW$weekn-0$weekday-$last_mainline_kernel-$hour
		# mkdir -p /home/$CUSER/kernel/deb_packages/mainline/$month-WW$weekn-0$weekday-$last_mainline_kernel-$hour/deb_packages
		mkdir -p /home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel/deb_packages

		# Copying the deb packages
		cp /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/*.deb$* /home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel/deb_packages/
		# Creaing a info file
		echo "Main page : linuxgraphics.intel.com" 						> /home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel/README
		# Adding information to the README file
		echo "Kernel version : $kernel_version"	 						>> /home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel/README
		echo "Architecture : $architecture" 							>> /home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel/README
		echo "Homepage : $home_page" 									>> /home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel/README
		echo "Kernel build date : WW${weekn} / ${fullday} "				>> /home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel/README
		echo "Kernel build hour : ${hour}" 								>> /home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel/README
		echo "Maintainer email : humberto.i.perez.rodriguez@intel.com" 	>> /home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel/README
		# Copyng the package list
		cp /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/package_list /home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel/
		# Copying amd64.changes & dsc files
		cp /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/*.changes$* /home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel/
		cp /home/$CUSER/kernel/mainline/$last_mainline_version/$last_mainline_kernel/*.dsc$* /home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel/

		# Copying changelog file if exists
		if [ -f "${changes_file_path}/${changelog}" ]; then
			cp ${changes_file_path}/${changelog} /home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel/ &> /dev/null
		fi

		# Copying patch file if exists
		if [ -f "${changes_file_path}/${patch}" ]; then
			cp ${changes_file_path}/${patch} /home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel/ &> /dev/null
		fi

		# adding latest_mainline kernel version to /home/$CUSER/kernel/.compare_last_mainline for future comparations
		echo "$last_mainline_kernel" >> /home/$CUSER/kernel/.compare_last_mainline

		# Copying the CONFIG IN USE to the deb packages folder
		cp ${CONFIG_IN_USE} /home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel/config


	stop_spinner $?

	stop_time "mainline kernel build time was"

		ip=$(ifconfig | awk '/inet addr/{print substr($2,6)}' | grep -v "^127")
		if [[ $ip =~ ^19 ]]; then 
			# SEDLINE CONNECTION
			notification_new_commit

		else 
			# Uploading deb package to linuxgraphics.intel.com (INTRANET CONNECTION)
			start_spinner "++ Uploading kernel deb package ..."
				# Creating a folder in linuxgraphics.intel.com server
				sshpass -p linuxgfx ssh gfxserver@10.219.106.67 "mkdir -p /var/www/html/linuxkernel.com/kernels/mainline/$last_mainline_version" &> /dev/null
				# Copying the deb files
				sshpass -p linuxgfx scp -o "StrictHostKeyChecking no" -r /home/$CUSER/kernel/deb_packages/mainline/WW$weekn/$last_mainline_version/$last_mainline_kernel/ gfxserver@10.219.106.67:/var/www/html/linuxkernel.com/kernels/mainline/$last_mainline_version &> /dev/null
			stop_spinner $?
			notification_new_commit

		fi


}

#######################################################
# This is for generates all mainline kernels you want #
# REMOVE WHEN NOT NEEDED #
# export last_mainline_version=v4.x	# example v4.1
# export last_mainline_kernel=linux-4.4 		# example linux-4.0.1
# build_mainline_kernel
######################################################


function check_for_mainline {

	clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"

	mkdir -p /home/$CUSER/kernel &> /dev/null
	# Downloading the list
	start_spinner "++ Downloading mainline list ..."
		w3m https://www.kernel.org/pub/linux/kernel/ | grep "^v" > /tmp/mainline_list
		export last_mainline_version=$(cat /tmp/mainline_list | awk '{print $1}' | tail -1 | sed 's|/||g') # example v4.1
		w3m https://www.kernel.org/pub/linux/kernel/$last_mainline_version | grep -w "tar.gz" > /tmp/lv # Getting the last kernel versions
		export last_mainline_kernel=$(cat /tmp/lv | tail -1 | awk '{print $1}' | sed 's/.tar.gz//g') # example linux-4.0.1
	stop_spinner $?

	# Making a comparation vs the last kernel mainline builded
	file=/home/$CUSER/kernel/.compare_last_mainline

	if [ -f "$file" ]; then

		# Here the comparation is based in a file previously created (that contains the last commit builded) supposing that this is not the first time that this script was executed
		export current_mainline_version=$(cat ${file} | tail -1)

		if [ "$last_mainline_kernel" != "$current_mainline_version" ]; then
			
			echo -ne "++ Current kernel mainline version : ${yellow}${underline}$current_mainline_version${nc} \n"
			echo -ne "++ ${bold}${green}There is a new kernel from kernel.org${nc} : (${blue}$last_mainline_kernel${nc}) \n"

			build_mainline_kernel

		elif [ "$last_mainline_kernel" = "$current_mainline_version" ]; then
			
			# echo -ne "++ Current kernel mainline version : ${yellow}${underline}$current_mainline_version${nc} \n"
			# Getting the full info from the current commit
			echo -ne "++ ${bold}${yellow}There is no new kernel mainline version${nc} \n"
			echo -ne "++ ${bold}${yellow}Current kernel mainline is${nc} : $current_mainline_version\n\n"
			# See the way to how to show the information from the latest mainline kernel
			# echo -ne "${blue}$full_info${nc} \n\n"
			notification_no_commit
		fi

	else

		# Here cannot we comparation because this the first time that run this script and thus we'll build the latest available mainline kernel
		build_mainline_kernel

	fi


}


function dependencies {


	if [ -f "/home/$CUSER/.kernel_dep" ]; then check_for_mainline; fi

	clear; echo -ne "\n\n"
	echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
	start_spinner "++ Installing dependencies ... "

		echo $PASSWORD | sudo -S ls &> /dev/null; sleep 5

		check_distribution=$(lsb_release -r | awk '{print $2}')

		if [ "$check_distribution" = "14.04" ]; then

				# Ubuntu 14.04 comes with gcc version 4.8 and this script needs gcc version 4.9 or higher, install the gcc 4.9 for ubuntu 14.04 is needed
				sudo -E add-apt-repository -y ppa:ubuntu-toolchain-r/test &> /dev/null
				echo $PASSWORD | sudo -S apt-get update -q=2 &> /dev/null
				echo $PASSWORD | sudo -S apt-get install gcc-4.9 g++-4.9 -q=2 &> /dev/null
				echo $PASSWORD | sudo -S update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.9 60 --slave /usr/bin/g++ g++ /usr/bin/g++-4.9 &> /dev/null # this command link the new gcc's version downloaded previously
		fi

		# Libraries required for “make menuconfig” most commonly used
		echo $PASSWORD | sudo -S apt-get install libncurses5-dev -q=2 &> /dev/null
		echo $PASSWORD | sudo -S apt-get install libssl-dev -q=2 &> /dev/null
		echo $PASSWORD | sudo -S apt-get install dpkg-dev -q=2 &> /dev/null
		echo $PASSWORD | sudo -S apt-get install libncursesw5-dev -q=2 &> /dev/null
		# Libraries requiered for make xconfig tool, this tool is alternative to “make menuconfig”
		echo $PASSWORD | sudo -S apt-get install pkg-config -q=2 &> /dev/null
		echo $PASSWORD | sudo -S apt-get install libqt4-dev -q=2 &> /dev/null
		# Additional packages
		echo $PASSWORD | sudo -S apt-get install sendmail -q=2 &> /dev/null
		echo $PASSWORD | sudo -S apt-get install sshpass -q=2 &> /dev/null
		echo $PASSWORD | sudo -S apt-get install w3m -q=2 &> /dev/null
	stop_spinner $? | tee .log

	check=$(cat .log | grep "FAIL")

	if [ -z "$check" ]; then touch /home/$CUSER/.kernel_dep; check_for_mainline; else echo -ne "\n\n"; echo -ne "++ ${bold}${red}There was a problem installing the dependencies${nc} \n\n"; exit 2; fi

}


dependencies
# $@