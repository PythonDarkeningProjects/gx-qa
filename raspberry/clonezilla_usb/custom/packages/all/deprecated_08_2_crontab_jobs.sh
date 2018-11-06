#!/bin/bash
	
	##############################################################
	# Load functions                                             #
	##############################################################

	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	_USER=gfx
	_PASSWORD="linux"
	source ${_THISPATH}/functions.sh


	_CRON_FILE="/home/${_USER}/.cron_jobs"
	_CRON_FILE_2="/home/${_USER}/.cron_file"

	if [ ! -f "${_CRON_FILE}" ]; then
		clear; echo -ne "\n\n"
		echo -ne "--> Setting crontab jobs for [${_USER}] ...   "
			sleep 3

			(crontab -u ${_USER} -l; echo "SHELL=/bin/bash") | crontab - &> /dev/null
			(crontab -u ${_USER} -l; echo "PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin") | crontab - &> /dev/null
			(crontab -u ${_USER} -l; echo "BASH_ENV=/home/${_USER}/.bashrc") | crontab - &> /dev/null
			(crontab -u ${_USER} -l; echo "TERM=xterm") | crontab - &> /dev/null

			(crontab -u ${_USER} -l; echo "@reboot sleep 10; chvt 1") | crontab - &> /dev/null
			#(crontab -u ${_USER} -l; echo "@reboot sleep 25; /home/${_USER}/dev/igt/run_IGT.sh --basic | tee /dev/tty1") | crontab - &> /dev/null
			(crontab -u ${_USER} -l; echo "@reboot sleep 35; /home/${_USER}/dev/igt/run_IGT.sh 2>&1 > /dev/tty1") | crontab - &> /dev/null
			(crontab -u ${_USER} -l; echo "@reboot sleep 45; /home/${_USER}/dev/igt/tools/IGT_dmesg_daemon 2>&1 > /dev/tty2") | crontab - &> /dev/null
			touch ${_CRON_FILE} ${_CRON_FILE_2}
		echo -ne "[${green}Ok${nc}]"

		echo -e "--> ${yellow}Rebooting${nc} ..."
			echo ${_PASSWORD} | sudo -S ls &> /dev/null; sleep 5
			echo ${_PASSWORD} | sudo -S reboot

		exit 2
	fi