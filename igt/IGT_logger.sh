#!/bin/bash

THISPATH=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
CONFIG_CFG="/home/custom/config.cfg"

echo ">>> (info) checking if ($(basename ${CONFIG_CFG})) exists"
if [ ! -f "${CONFIG_CFG}" ]; then
	echo ">>> (err) (${CONFIG_CFG}) does not exists"
	exit 1
else
	echo ">>> (info) sourcing (${CONFIG_CFG})"
	source ${CONFIG_CFG}
fi


LOGS_FOLDER="/home/${dut_user}/igt_execution_logs"
if [ ! -d "${LOGS_FOLDER}" ]; then
	echo ">>> (info) creating folder (${LOGS_FOLDER})"
	mkdir -p "${LOGS_FOLDER}"
else
	echo ">>> (info) already exists ($(basename "${LOGS_FOLDER}"))"
fi

LOGS_NUMBER=$(find "${LOGS_FOLDER}" -maxdepth 1 -type f | wc -l)
LOGGER_NAME="intel-gpu-tools_log_"

if [ "${LOGS_NUMBER}" -eq 0 ]; then
	echo ">>> (info) creating log (1) for run_IGT.py"
	echo ">>> (info) recording sdout & sderr from run_IGT.py"
	# until this point the output in tty will be redirect to the log
	echo ">>> (cmd) python run_IGT.py"
	python "${THISPATH}"/run_IGT.py 2>&1 | tee "${LOGS_FOLDER}/${LOGGER_NAME}1"
	OUTPUT=$?
	echo ">>> (info) script output was (${OUTPUT})" | tee -a "${LOGS_FOLDER}/${LOGGER_NAME}1"
	echo ">>> (info) the log was created in the following path"
	echo ">>> (path) (${LOGS_FOLDER}/${LOGGER_NAME}1)"

else
	LOG_COUNT=$((LOGS_NUMBER + 1))
	echo ">>> (info) creating log (${LOG_COUNT}) for run_IGT.py"
	echo ">>> (info) recording sdout & sderr from run_IGT.py"
	# until this point the output in tty will be redirect to the log
	echo ">>> (cmd) python run_IGT.py"
	python "${THISPATH}"/run_IGT.py 2>&1 | tee "${LOGS_FOLDER}/${LOGGER_NAME}${LOG_COUNT}"
	OUTPUT=$?
	echo ">>> (info) script output was (${OUTPUT})" | tee -a "${LOGS_FOLDER}/${LOGGER_NAME}${LOG_COUNT}"
	echo ">>> (info) the log was created in the following path"
	echo ">>> (path) (${LOGS_FOLDER}/${LOGGER_NAME}${LOG_COUNT})"
fi