#!/usr/bin/env bash

	export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`

	# ==============
	# Load functions
	# ==============
	source ${_THISPATH}/functions.sh
	source /root/custom/config.cfg

	export _IGT_FAST_FEEDBACK_FILE="/root/custom/packages/crontab/customized_igt_fast_feedback"
	export _IGT_CLONES_FILE="/root/custom/packages/crontab/customized_igt_clones"
	export _IGT_ALL_FILE="/root/custom/packages/crontab/customized_igt_all"
	export _GENERAL_POST_UI="/root/custom/packages/crontab/general_post_UI"
	export _GENERAL_POST="/root/custom/packages/crontab/general_post"
	export _EZBENCH_IGT_FILE="/root/custom/packages/crontab/customized_ezbench_for_igt"
	export _EZBENCH_BENCHMARKS_FILE="/root/custom/packages/crontab/customized_ezbench_for_benchmarks"
	export _EZBENCH_RENDERCHECK_FILE="/root/custom/packages/crontab/customized_ezbench_for_rendercheck"
	export _ENV_FILE="/root/custom/env.vars"
	export _DATA=`cat /root/custom/DATA`
	export TERM=xterm

	function verify () {
		STATE="$1"
		unset STATUS
		if [ "${STATE}" = "0" ]; then STATUS=DONE; echo "cron_status=DONE" >> ${_ENV_FILE}; else STATUS=FAIL; echo "cron_status=FAIL" >> ${_ENV_FILE}; fi
		server_message INFO "${STATUS}"
	}

	if [ -z "${default_package}" ]; then
		echo "cron_status=FAIL" >> ${_ENV_FILE}
	else

		case "${default_package}" in

			"igt_fast_feedback" ) TEST_SUITE=${_IGT_FAST_FEEDBACK_FILE} ;;

			"igt_clone_testing") TEST_SUITE=${_IGT_CLONES_FILE} ;;

			"igt_all"|"igt_extended_list") TEST_SUITE=${_IGT_ALL_FILE} ;;

			"ezbench_igt") TEST_SUITE=${_EZBENCH_IGT_FILE} ;;

			"ezbench_benchmarks") TEST_SUITE=${_EZBENCH_BENCHMARKS_FILE} ;;

			"ezbench_rendercheck") TEST_SUITE=${_EZBENCH_RENDERCHECK_FILE} ;;

			"setup_image" )
				if [ "${graphical_environment}" = "off" ]; then
					TEST_SUITE=${_GENERAL_POST}
				elif [ "${graphical_environment}" = "on" ]; then
					TEST_SUITE=${_GENERAL_POST_UI}
				fi
			;;

			*) echo "cron_status=FAIL" >> ${_ENV_FILE} ;;
		esac

		if [ ! -z ${TEST_SUITE} ]; then
			server_message INFO "setting crontab for  : ${default_package}"
			start_spinner "- (info) - setting crontab for  : ${default_package} ..."
				sleep .25
				sed -i 's/gfx/'${dut_user}'/g' ${TEST_SUITE}
				crontab -u ${dut_user} ${TEST_SUITE}
			stop_spinner $?

			verify "${_STATUS}"
		fi

	fi