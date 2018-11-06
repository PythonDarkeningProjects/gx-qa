#!/usr/bin/env bash

	echo -ne "\n\n"
	# - looking for raspberry/switch -
	# The USB stick connected to each DUT corresponds to one raspberry and switch
	# in the automated system.

	# General variables
	export THIS_PATH=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd -P)
	readonly export WORK_DIR="/root/custom"
	readonly export SERVER_HOSTNAME="10.219.106.111"
	readonly export SERVER_USER="root"
	readonly export FUNCTIONS="${THIS_PATH}/functions.sh"
	readonly export USB_REMOTE_CFG="/home/shared/gitlist/gfx-qa-tools/raspberry/usb.cfg"
	readonly export OUTPUT_LOG_FOLDER="/root/custom/logs"
	readonly export OUTPUT_LOG_FILE="${OUTPUT_LOG_FOLDER}/clonezilla"
	export TERM=xterm
	# default sleep time for spinner operations.
	readonly export DEFAULT_SLEEP=.25
	readonly export USB_CFG_PATH="/root/usb.cfg"

	# SSH variables
	readonly export SSH_PARAM_SHKC="StrictHostKeyChecking=no"

	# Sourcing general scripts
	source ${WORK_DIR}/env.vars
	source ${FUNCTIONS}

	# Sourcing logger
	source "${THIS_PATH}"/log.sh

	mkdir -p ${OUTPUT_LOG_FOLDER}

	logger DEBUG "downloading usb.cfg from ${SERVER_HOSTNAME}"
	start_spinner " - (info) - downloading usb.cfg from ${SERVER_HOSTNAME}"
		sleep ${DEFAULT_SLEEP}
		scp -o "${SSH_PARAM_SHKC}" ${SERVER_USER}@${SERVER_HOSTNAME}:${USB_REMOTE_CFG} /root/ &> /dev/null
	stop_spinner $?

	logger DEBUG "sourcing : ${USB_CFG_PATH}"
	source "${USB_CFG_PATH}"

	readonly USB_SCRIPTS_UUID=$(blkid | grep "scripts" | awk '{print $3}' | sed -e 's/UUID=//g' -e 's/"//g')
	logger DEBUG "USB_SCRIPTS_UUID : ${USB_SCRIPTS_UUID}"

    # If more racks are added to the automated system, here we must add another
    # variable.
	RASPBERRY_01=$(echo "${_RASPBERRY_01_USB_UUID}" | grep -w "${USB_SCRIPTS_UUID}")
	RASPBERRY_02=$(echo "${_RASPBERRY_02_USB_UUID}" | grep -w "${USB_SCRIPTS_UUID}")
	RASPBERRY_03=$(echo "${_RASPBERRY_03_USB_UUID}" | grep -w "${USB_SCRIPTS_UUID}")
	RASPBERRY_04=$(echo "${_RASPBERRY_04_USB_UUID}" | grep -w "${USB_SCRIPTS_UUID}")

	if [[ ! -z "${RASPBERRY_01}" ]]; then
		readonly export CURRENT_RASPBERRY="raspberry-01"
	elif [[ ! -z "${RASPBERRY_02}" ]]; then
		readonly export CURRENT_RASPBERRY="raspberry-02"
	elif [[ ! -z "${RASPBERRY_03}" ]]; then
		readonly export CURRENT_RASPBERRY="raspberry-03"
	elif [[ ! -z "${RASPBERRY_04}" ]]; then
		readonly export CURRENT_RASPBERRY="raspberry-04"
	fi

    logger DEBUG "CURRENT_RASPBERRY : ${CURRENT_RASPBERRY}"

    # If more racks are added to the automated system, here we must add another
    # array.
	raspberry_01_array=(switch-01[${rasp_1_switch_1}] switch-02[${rasp_1_switch_2}] \
	        switch-03[${rasp_1_switch_3}] switch-04[${rasp_1_switch_4}] \
	        switch-05[${rasp_1_switch_5}] switch-06[${rasp_1_switch_6}] \
	        switch-07[${rasp_1_switch_7}] switch-08[${rasp_1_switch_8}]
	        )
	raspberry_02_array=(switch-01[${rasp_2_switch_1}] switch-02[${rasp_2_switch_2}] \
	        switch-03[${rasp_2_switch_3}] switch-04[${rasp_2_switch_4}] \
	        switch-05[${rasp_2_switch_5}] switch-06[${rasp_2_switch_6}] \
	        switch-07[${rasp_2_switch_7}] switch-08[${rasp_2_switch_8}]
	        )
	raspberry_03_array=(switch-01[${rasp_3_switch_1}] switch-02[${rasp_3_switch_2}] \
	        switch-03[${rasp_3_switch_3}] switch-04[${rasp_3_switch_4}] \
	        switch-05[${rasp_3_switch_5}] switch-06[${rasp_3_switch_6}] \
	        switch-07[${rasp_3_switch_7}] switch-08[${rasp_3_switch_8}]
	        )
	raspberry_04_array=(switch-01[${rasp_4_switch_1}] switch-02[${rasp_4_switch_2}] \
	        switch-03[${rasp_4_switch_3}] switch-04[${rasp_4_switch_4}] \
	        switch-05[${rasp_4_switch_5}] switch-06[${rasp_4_switch_6}] \
	        switch-07[${rasp_4_switch_7}] switch-08[${rasp_4_switch_8}]
	        )


    # If more racks are added to the automated system, here we must add another
    # case option.
	case "${CURRENT_RASPBERRY}" in
		raspberry-01)
			for element in "${raspberry_01_array[@]}"
			do
				ONLY_UUID=$(echo ${element} | awk -F "[" '{print $2}' | sed 's/\]//g')
				if [[ "${USB_SCRIPTS_UUID}" == "${ONLY_UUID}" ]]; then
					readonly export POWER_SWITCH=$(echo ${element} | awk -F"[" '{print $1}')
					break
				fi
			done
		;;

		raspberry-02)
			for element in "${raspberry_02_array[@]}"
			do
				ONLY_UUID=$(echo ${element} | awk -F "[" '{print $2}' | sed 's/\]//g')
				if [[ "${USB_SCRIPTS_UUID}" == "${ONLY_UUID}" ]]; then
					readonly export POWER_SWITCH=$(echo ${element} | awk -F"[" '{print $1}')
					break
				fi
			done
		;;

		raspberry-03)
			for element in "${raspberry_03_array[@]}"
			do
				ONLY_UUID=$(echo ${element} | awk -F "[" '{print $2}' | sed 's/\]//g')
				if [[ "${USB_SCRIPTS_UUID}" == "${ONLY_UUID}" ]]; then
					readonly export POWER_SWITCH=$(echo ${element} | awk -F"[" '{print $1}')
					break
				fi
			done
		;;

		raspberry-04)
			for element in "${raspberry_04_array[@]}"
			do
				ONLY_UUID=$(echo ${element} | awk -F "[" '{print $2}' | sed 's/\]//g')
				if [[ "${USB_SCRIPTS_UUID}" == "${ONLY_UUID}" ]]; then
					readonly export POWER_SWITCH=$(echo ${element} | awk -F"[" '{print $1}')
					break
				fi
			done
		;;
	esac

	logger DEBUG "POWER_SWITCH : ${POWER_SWITCH}"

	# environment variables
	readonly export SERVER_CONFIG_FILE_CFG="/home/shared/raspberry/${CURRENT_RASPBERRY}/${POWER_SWITCH}/custom/config.cfg"
	readonly export SERVER_CONFIG_FILE_YAML="/home/shared/raspberry/${CURRENT_RASPBERRY}/${POWER_SWITCH}/custom/config.yml"
	readonly export DEFAULT_CONFIG_FILE_CFG="/root/custom/config.cfg"
	readonly export DEFAULT_YAML_CONFIG_FILE="/root/custom/config.yml"
	# this folder comes from bifrost.intel.com
	readonly export UPDATE_FOLDER="/home/shared/gitlist/gfx-qa-tools/raspberry/clonezilla_usb/custom/"

    # banners
	readonly BANNER_SCRIPT="/root/custom/packages/banners/banner.sh"
	readonly export BANNER_IGT="${BANNER_SCRIPT} suite_igt"
	readonly export BANNER_EZBENCH="${BANNER_SCRIPT} suite_ezbench"
	readonly export BANNER_SETUP="${BANNER_SCRIPT} set_environment"
	readonly export BANNER_RESTORE="${BANNER_SCRIPT} set_image"
	readonly export BANNER_REBOOT_UPDATES="${BANNER_SCRIPT} reboot_for_updates"
	readonly export BANNER_APPLYING_UPDATES="${BANNER_SCRIPT} applying_updates"
	readonly export BANNER_UP_TO_DATE="${BANNER_SCRIPT} up_to_date"
	readonly export BANNER_SKIP_UPDATES="${BANNER_SCRIPT} skip_updates"
	readonly export BANNER_SKIP_STACK="${BANNER_SCRIPT} skip_installation gfx_stack"
	readonly export BANNER_SKIP_KERNEL="${BANNER_SCRIPT} skip_installation kernel"
	readonly export BANNER_EZBENCH_RENDERCHECK="${BANNER_SCRIPT} suite_ezbench_rendercheck"
	readonly export BANNER_EZBENCH_IGT="${BANNER_SCRIPT} suite_ezbench_igt"
	readonly export BANNER_EZBENCH_BENCHMARKS="${BANNER_SCRIPT} suite_ezbench_benchmarks"

	export DATA="/home/shared/raspberry/${CURRENT_RASPBERRY}/${POWER_SWITCH}"
	export REMOTE_LOG_FOLDER="${DATA}/clonezilla_logs"
	export SCRIPTS_PATH="/root/custom/packages/all"
	export TOOLS_PATH="/root/custom/tools"
	export ENV_FILE="/root/custom/env.vars"

	echo "DATA=${DATA}" >> ${ENV_FILE}

	if [ "$SYSTEM_READY" != "1" ]
	then
    	exit 1
	fi

	start_time

	# checking if the configuration files exists in bifrost.intel.com
	configuration_files=(${SERVER_CONFIG_FILE_CFG} ${SERVER_CONFIG_FILE_YAML})
	configuration_file_flag=0

	for config in ${configuration_files[*]}
	do
        if (ssh -o "${SSH_PARAM_SHKC}" -o ConnectTimeout=10 -q ${SERVER_USER}@${SERVER_HOSTNAME} '[ -f '${config}' ]'); then

            [[ "${config}" == "${SERVER_CONFIG_FILE_CFG}" ]] && \
                default_config="${DEFAULT_CONFIG_FILE_CFG}" || \
                default_config="${DEFAULT_YAML_CONFIG_FILE}"

            logger DEBUG "removing default configuration file : ${default_config}"
            start_spinner " - (info) - removing default configuration file : ${default_config}"
                sleep ${DEFAULT_SLEEP}
                rm -rf ${default_config}
            stop_spinner $?

            logger DEBUG "downloading configuration file from : ${SERVER_HOSTNAME}"
            start_spinner " - (info) - downloading configuration file from : ${SERVER_HOSTNAME}"
                sleep ${DEFAULT_SLEEP}
                scp -o "${SSH_PARAM_SHKC}" ${SERVER_USER}@${SERVER_HOSTNAME}:${config} /root/custom/
            stop_spinner $?

            [[ "${_STATUS}" -eq 0 ]] && ((configuration_file_flag++))

        fi

    done

    # stopping the script in the case that some configuration file could not be
    # downloaded.
    [[ ${configuration_file_flag} -ne 2 ]] && \
        logger ERROR "the configuration files could not be downloaded from bifrost.intel.com" \
        && exit 1

	readonly export CONFIG_FILE="${DEFAULT_CONFIG_FILE_CFG}"

	# sourcing CFG configuration file
	source ${CONFIG_FILE}

	# informative article.
	# can I save the image on the same USB drive of Clonezilla live ?
	# http://drbl.org/faq/fine-print.php?path=./2_System/120_image_repository_on_same_usb_stick.faq#120_image_repository_on_same_usb_stick.faq

	# checking if there is an update in bifrost.intel.com

updates () {
    # Sync custom folder.

    # Synchronize custom folder with latest updates from github.intel.com in a
    # repository located in bifrost.intel.com.
    # params:
    # - latest_commit: the full commit message for gfx-qa-tools in bifrost.intel.com.
    # - only_latest_commit: the SHA for gfx-qa-tools in bifrost.intel.com.
    # - current_branch: the current branch for gfx-qa-tools in bifrost.intel.com

    local latest_commit="$1"
    local only_latest_commit="$2"
    local current_branch="$3"
    local exclude_files="config.*"

    # showing a banner.
	${BANNER_APPLYING_UPDATES}

    logger DEBUG "downloading updates for custom folder from ${server_hostname} into USB stick"
    server_message INFO "downloading updates for custom folder from ${server_hostname} into USB stick"

	start_spinner " - (info) - downloading updates for custom folder from ${server_hostname} into USB stick"
		sleep ${DEFAULT_SLEEP}
		rsync -avrz --exclude "${exclude_files}" -e "ssh -o ${SSH_PARAM_SHKC} -o UserKnownHostsFile" ${server_user}@${server_hostname}:${UPDATE_FOLDER} /root/custom/ | tee -a "${OUTPUT_LOG_FILE}"
	stop_spinner $?

    check_spinner_status

    logger INFO "current branch is : ${current_branch}"
    logger INFO "latest commit is : ${latest_commit}"
	echo "${only_latest_commit}" > /root/custom/latest_commit

	server_message INFO "the commit downloaded is :"
	server_message INFO "${only_latest_commit}"
	server_message INFO "the current branch is : ${current_branch}"
	server_message INFO "rebooting the system in order to apply the updates in the custom folder"

	# showing a banner.
	${BANNER_REBOOT_UPDATES}
    # WARNING : avoid to use : "sudo reboot -f" since this command erase
    # everything written in USB stick (only for clonezilla environment)
	sudo shutdown -r now
	exit 0
}
    if (ssh_command "[[ -d ${UPDATE_FOLDER} ]]" execute) && [[ "${usb_update_mode}" == "on" ]]; then

        latest_commit=$(ssh_command "git -C /home/shared/gitlist/gfx-qa-tools log -1")
        only_latest_commit=$(ssh_command "git -C /home/shared/gitlist/gfx-qa-tools rev-parse HEAD")
        current_branch=$(ssh_command "git -C /home/shared/gitlist/gfx-qa-tools rev-parse --abbrev-ref HEAD")

        if [[ ! -z "${only_latest_commit}" && ! -f "/root/custom/latest_commit" ]]; then
            # updating USB custom folder.
            updates "${latest_commit}" "${only_latest_commit}" "${current_branch}"
        else
            previous_commit=$(cat /root/custom/latest_commit)

            if [[ "${previous_commit}" != "${only_latest_commit}" ]]; then
                # updating USB custom folder.
                updates "${latest_commit}" "${only_latest_commit}" "${current_branch}"
            elif [[ "${previous_commit}" == "${only_latest_commit}" ]]; then
                logger INFO "current branch is : ${current_branch}"
                logger INFO "current commit is : ${only_latest_commit}"
                server_message INFO "USB custom folder is up-to-date"
                server_message INFO "current branch is : ${current_branch}"
                # showing a banner.
                ${BANNER_UP_TO_DATE}
            fi
        fi

    elif (ssh_command "[[ ! -d ${UPDATE_FOLDER} ]]" execute) && [[ "${usb_update_mode}" == "on" ]]; then

        logger WARN "usb_update_mode key is set to on but ${UPDATE_FOLDER} does not exists in ${server_hostname}"
        logger WARN "skipping USB updates"
        server_message WARN "usb_update_mode key is set to on but ${UPDATE_FOLDER} does not exists in ${server_hostname}"
        server_message WARN "skipping USB updates"

    elif [[ "${usb_update_mode}" != "on" ]]; then

        server_message WARN "skipping USB updates"
        # showing a banner.
        ${BANNER_SKIP_UPDATES}
    fi


	if [ ! -z "${default_package}" ]; then

		case "${default_package}" in
			igt*) ${BANNER_IGT} ;;
			ezbench_rendercheck) ${BANNER_EZBENCH_RENDERCHECK} ;;
			ezbench_benchmarks) ${BANNER_EZBENCH_BENCHMARKS} ;;
			ezbench_igt) ${BANNER_EZBENCH_IGT} ;;
			setup_image) ${BANNER_RESTORE} ;;
		esac

		main_start_time

		service ssh start
		mount devpts /dev/pts -t devpts
		readonly export clonezilla_ip=`hostname -I | sed 's/ //g'`
		server_message INFO "clonezilla IP address : ${clonezilla_ip}"

        # ============================
		# ◉ 1 ◉ (default_restore.sh)
		# ============================
		start_time
		server_message INFO "restoring image : ${default_image}"
		bash /root/custom/default_restore.sh "${CONFIG_FILE}" #### 1
		source ${ENV_FILE}
		ELAPSED_TIME=`stop_time "elapsed time"`
		server_message INFO "${restore_image}"
		server_message INFO "${ELAPSED_TIME}"
		if [ "${restore_image}" = "FAIL" ]; then exit 1; fi

		${BANNER_SETUP}

        # =========================
		# ◉ 2 ◉ (01_mount_system.sh)
		# =========================
		start_time
		server_message INFO "mounting system"
		bash ${SCRIPTS_PATH}/01_mount_system.sh #### 2
		source ${ENV_FILE}; unset ELAPSED_TIME
		ELAPSED_TIME=`stop_time "elapsed time"`
		server_message INFO "${mount_image}"
		server_message INFO "${ELAPSED_TIME}"
		echo "${DATA}" > /root/custom/DATA

        export _LOGS_FOLDER="/mnt/home/custom/clonezilla_logs"
        mkdir -p "${_LOGS_FOLDER}"
        # =============================
		# ◉ 3 ◉ (02_download_kernel.sh)
		# =============================
		if [ -z "${kernel_commit}" ]; then
			${BANNER_SKIP_KERNEL}
			server_message WARN "skipping kernel installation"
		else
			start_time
			server_message INFO "downloading kernel : ${kernel_branch}"
			bash ${SCRIPTS_PATH}/02_download_kernel.sh "${CONFIG_FILE}" 2>&1 | tee ${_LOGS_FOLDER}/02_download_kernel.log #### 3
			source ${ENV_FILE}; unset ELAPSED_TIME
			ELAPSED_TIME=`stop_time "elapsed time"`
			server_message INFO "${kernel_status}"
			server_message INFO "${ELAPSED_TIME}"
			if [ "${kernel_status}" = "FAIL" ]; then echo -ne "--> Leaving the script ....\n\n"; exit 1; fi
		fi

        # ================================
		# ◉ 4 ◉ (03_download_gfx_stack.sh)
		# ================================
		if [ -z "${gfx_stack_code}" ]; then
			${BANNER_SKIP_STACK}
			server_message WARN "skipping graphic stack installation"
		else
			start_time
			server_message INFO "downloading Graphic Stack"
			bash ${SCRIPTS_PATH}/03_download_gfx_stack.sh "${CONFIG_FILE}" 2>&1 | tee ${_LOGS_FOLDER}/03_download_gfx_stack.log #### 4
			source ${ENV_FILE}; unset ELAPSED_TIME
			ELAPSED_TIME=`stop_time "elapsed time"`
			server_message INFO "${stack_status}"
			server_message INFO "${ELAPSED_TIME}"
			if [ "${stack_status}" = "FAIL" ]; then echo -ne ">>> (err) Leaving the script ....\n\n"; exit 1; fi
		fi

        # ===============================================================
        # ◉ 5 ◉ (11_chroot.sh.sh)
        # ===============================================================
        # Changing dut_user and dut_password at the end in order to avoid
        # any kind of issues
        bash ${SCRIPTS_PATH}/11_chroot.sh ${_LOGS_FOLDER} 2>&1 | tee ${_LOGS_FOLDER}/11_chroot.sh; wait

        # =====================
		# ◉ 6 ◉ (06_ssh_keys.sh)
		# =====================
		start_time
		server_message INFO "setting ssh keys"
		bash ${SCRIPTS_PATH}/06_ssh_keys.sh "${CONFIG_FILE}" 2>&1 | tee ${_LOGS_FOLDER}/06_ssh_keys.log #### 5
		source ${ENV_FILE}; unset ELAPSED_TIME
		ELAPSED_TIME=`stop_time "elapsed time"`
		server_message INFO "${ssh_keys}"
		server_message INFO "${ELAPSED_TIME}"

        # ===================
		# ◉ 7 ◉ (04_chroot.sh)
		# ===================
		start_time
		server_message INFO "installing deb packages"
		bash ${SCRIPTS_PATH}/04_chroot.sh 2>&1 | tee ${_LOGS_FOLDER}/04_chroot.log #### 6
		source ${ENV_FILE}; unset ELAPSED_TIME
		ELAPSED_TIME=`stop_time "elapsed time"`
		server_message INFO "${deb_packages}"
		server_message INFO "${ELAPSED_TIME}"

        # ===========================
		# ◉ 8 ◉ (05_env_variables.sh)
		# ===========================
		start_time
		server_message INFO "setting DUT environment"
		bash ${SCRIPTS_PATH}/05_env_variables.sh "${CONFIG_FILE}" "${DATA}" "${DEFAULT_YAML_CONFIG_FILE}" 2>&1 | tee ${_LOGS_FOLDER}/05_env_variables.log #### 7
		source ${ENV_FILE}; unset ELAPSED_TIME
		ELAPSED_TIME=`stop_time "elapsed time"`
		server_message INFO "${ELAPSED_TIME}"

        # ============================
		# ◉ 9 ◉ (07_swap_partition.sh)
		# ============================
		start_time
		server_message INFO "fixing swap partition"
		bash ${SCRIPTS_PATH}/07_swap_partition.sh "${CONFIG_FILE}" 2>&1 | tee ${_LOGS_FOLDER}/07_swap_partition.log #### 8
		source ${ENV_FILE}; unset ELAPSED_TIME
		ELAPSED_TIME=`stop_time "elapsed time"`
		server_message INFO "${swap_partition}"
		server_message INFO "${ELAPSED_TIME}"

        # ============================
		# ◉ 10 ◉ (08_crontab_chroot.sh)
		# ============================
		start_time
		server_message INFO "setting crontab for : ${default_package}"
		bash ${SCRIPTS_PATH}/08_crontab_chroot.sh 2>&1 | tee ${_LOGS_FOLDER}/08_crontab_chroot.log
		source ${ENV_FILE}; unset ELAPSED_TIME
		ELAPSED_TIME=`stop_time "elapsed time"`
		server_message INFO "${ELAPSED_TIME}"
		if [ "${cron_status}" = "FAIL" ]; then echo -ne ">>> (err) Leaving the script ....\n\n"; exit 1; fi


        # ============================
		# ◉ 11 ◉ (12_daemon_chroot.sh)
		# ============================
		start_time
		bash ${SCRIPTS_PATH}/12_daemon_chroot.sh 2>&1 | tee ${_LOGS_FOLDER}/12_daemon_chroot.log
		source ${ENV_FILE}; unset ELAPSED_TIME
		ELAPSED_TIME=`stop_time "elapsed time"`
		server_message INFO "${ELAPSED_TIME}"


		case ${default_package} in

			igt_all)

				case "${blacklist_file}" in

					"no") server_message INFO "setting default (all.testlist) from graphic stack" ;;

					"yes")
						export _SERVER_BLACKLIST_FILE="/home/shared/raspberry/${CURRENT_RASPBERRY}/${POWER_SWITCH}/all.testlist"
						export blacklistFile=`basename ${_SERVER_BLACKLIST_FILE}`

						if (timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} '[ -f '${_SERVER_BLACKLIST_FILE}' ]'); then

							server_message INFO "downloading ${blacklistFile} from ${server_hostname}"
							start_spinner " - (info) - downloading ${blacklistFile} file from ${SERVER_HOSTNAME} ..."
							    server_message INFO "setting ${blacklistFile} for intel-gpu-tools"
								sleep .25; scp -o "${SSH_PARAM_SHKC}" ${server_user}@${server_hostname}:${_SERVER_BLACKLIST_FILE} /root/custom/ &> /dev/null
								cp /root/custom/${blacklistFile} /mnt/home/${dut_user}/intel-graphics/intel-gpu-tools/tests/intel-ci &> /dev/null
							stop_spinner $?

						else
							server_message ERROR "${blacklistFile} :  not found in ${SERVER_HOSTNAME}"
							echo -ne "\n\n"
							echo -ne " - (${red}err${nc}) - ${yellow} [${blacklistFile}] not found${nc} in [${SERVER_HOSTNAME}] \n"
							echo -ne " - (${red}err${nc}) - in order to run intel-gpu-tools all you need to specify a ${blacklistFile} \n\n"
							exit 1
						fi
					;;
				esac
			;;

			igt_clone_testing)

				export _SERVER_BLACKLIST_FILE="/home/shared/raspberry/${CURRENT_RASPBERRY}/${POWER_SWITCH}/clone.testlist"
				export blacklistFile=`basename ${_SERVER_BLACKLIST_FILE}`

				if (timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} '[ -f '${_SERVER_BLACKLIST_FILE}' ]'); then

					server_message INFO "downloading ${blacklistFile} from ${server_hostname}"
					start_spinner ">>> (info) Downloading ${blacklistFile} file from ${SERVER_HOSTNAME} ..."
						server_message INFO "setting  ${blacklistFile} for intel-gpu-tools"
						sleep .25; scp -o "${SSH_PARAM_SHKC}" ${server_user}@${server_hostname}:${_SERVER_BLACKLIST_FILE} /root/custom/ &> /dev/null
						cp /root/custom/${blacklistFile} /mnt/home/${dut_user}/intel-graphics/intel-gpu-tools/tests/intel-ci &> /dev/null
					stop_spinner $?
				else
				    server_message ERROR "${blacklistFile} :  not found in ${SERVER_HOSTNAME}"
					echo -ne "\n\n"
					echo -ne " - (${red}err${nc}) - ${yellow} [${blacklistFile}] not found${nc} in [${SERVER_HOSTNAME}] \n"
					echo -ne " - (${red}err${nc}) - in order to run intel-gpu-tools all you need to specify a ${blacklistFile} \n\n"
					exit 1
				fi
			;;

		esac

		if [ ! -z "${guc}" -o ! -z "${dmc}" -o ! -z "${huc}" ]; then
            # ============================
            # ◉ 12 ◉ (10_firmwares.sh)
            # ============================
			start_time
			server_message INFO "copying firmwares to : ${dut_hostname}"
			bash ${SCRIPTS_PATH}/10_firmwares.sh "${DATA}" 2>&1 | tee ${_LOGS_FOLDER}/10_firmwares.log; wait
			source ${ENV_FILE}; unset ELAPSED_TIME
			ELAPSED_TIME=`stop_time "elapsed time"`
			server_message INFO "${firmwares}"
			server_message INFO "${ELAPSED_TIME}"
		fi

        # =================================================================
        # ◉ xserver-xorg ◉ (WA)
        # =================================================================
        # clonezilla for some unknown reason renames the file located in
        # /etc/X11/xorg.conf to /etc/X11/xorg.conf.<some_random_number> in
        # order to avoid this we have to check the file at the end before
        # this script turn off the DUT
        XORG_SYSTEM_FILE_NAME=$(ls /mnt/etc/X11/ | grep xorg.conf)
        XORG_ORIGINAL_NAME="xorg.conf"

        if [[ ! -z "${XORG_SYSTEM_FILE_NAME}" && "${XORG_SYSTEM_FILE_NAME}" != "${XORG_ORIGINAL_NAME}" ]]; then
            server_message WARN " xorg.conf name is (${XORG_SYSTEM_FILE_NAME}) changing to default (xorg.conf)"
            start_spinner " - (warn) - xorg.conf name is (${XORG_SYSTEM_FILE_NAME}) changing to default (xorg.conf) ...  "
                sleep .25
                mv /mnt/etc/X11/${XORG_SYSTEM_FILE_NAME} /mnt/etc/X11/${XORG_ORIGINAL_NAME}
            stop_spinner $?
            verify "${_STATUS}" "${server_user}" "${server_hostname}" "${DATA}"
        elif [[ ! -z "${XORG_SYSTEM_FILE_NAME}" ]]; then
            # XORG_SYSTEM_FILE_NAME could be empty if a graphic stack package
            # does not contain xserver-xorg
            server_message INFO "xorg.conf system name is  : ${XORG_SYSTEM_FILE_NAME}"
        fi



		_MAIN_ELAPSED_TIME=`main_stop_time "overall elapsed time"`
		server_message INFO "${_MAIN_ELAPSED_TIME}"
		timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo "clonezilla has finished" >> '${DATA}'/clonezilla'
		echo -ne "\n\n"
		echo " - (info) - ${_MAIN_ELAPSED_TIME}"

	elif [ -z "${default_package}" ]; then
		echo -ne "\n\n"
		server_message ERROR "(default_package) is empty, please fill out this variable to continue"
		echo -ne " - (err) - ${red}default_package is empty${nc}, please fill out this variable to continue \n\n"
		exit 1
	fi

    # =================================================
    # Turn off usb cutter (only if raspberry is online)
    # =================================================
    start_spinner "-(info) - check for raspberry status ..."
        timeout 2 ping -c1 ${raspberry_ip} &> /dev/null
    stop_spinner $?

    if [ "${_STATUS}" = "0" ]; then

        # turn off power cutter
        timeout 70 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${raspberry_user}@${raspberry_ip} "PYTHONPATH=${PYTHONPATH}:/home/pi/dev python -u /home/pi/dev/raspberry/clewarecontrol/cutter.py -c ${usb_cutter_serial} -a off"

    else
        echo -ne "${yellow}===================================${nc} \n"
        echo -ne " - (warn) - raspberry is ${red}offline${nc} ... \n"
        echo -ne "${yellow}===================================${nc} \n\n"
    fi

    ###########################################################################
    # in this point the system (clonezilla) is on read-system only for a unknown
    # reason but the mounted partition from the hard disk is still there into
    # /mnt, so taking this in mind we can call the scripts from there.
    ###########################################################################

    # forcing the reboot after clonezilla finish, this is useful for all DUTs
    # especially for CNL, otherwise CNL never will exit from clonezilla environment.
    # WARNING : avoid to use : "sudo reboot -f" since this command erase
    # everything written in USB stick (only for clonezilla environment)
    echo "- (info) - rebooting the system"
    sudo shutdown -r now
