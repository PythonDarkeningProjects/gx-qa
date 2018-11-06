#!/usr/bin/env bash

# How to use this bash logger.
# 1) import this script as a module, e.g:
# source ../log.sh
# 2) call to the function logger like this:
# logger INFO "some message"
# Note: if the environment variable OUTPUT_LOG_FILE is not set, the default log
# file name is set to clonezilla and it will be write in this script location.


check_rotatory_logs() {
    # check for rotatory logs.

    # The aim of this function is to check for rotatory logs in order to decide
    # in which rotatory logs will be write this script.
    # param:
    # - log_file: the log file path, this could be a relative/absolute path.
    # return:
    # - next_rotatory_log_number: which is the next rotatory log number to write
    #                             the messages.

    declare log_file="$1"
    declare max_size_log_bytes="10000"
    declare log_file_path="$(cd $(dirname ${log_file}); pwd -P)"
    # declaring an array for the rotatory_files.
    declare -a rotatory_files=($(ls ${log_file_path} | grep "^${log_file}"))

    # removing rotatory logs greater than 10MB and checking which is the rotatory
    # file to write.

    case ${#rotatory_files[*]} in

        1)
            rotatory_file_a_size=$(( $( stat -c '%s' ${log_file} ) / 1024))

            if [[ "${rotatory_file_a_size}" -lt "${max_size_log_bytes}" ]]; then
                next_rotatory_log_number=""
            elif [[ "${rotatory_file_a_size}" -gt "${max_size_log_bytes}" ]]; then
                next_rotatory_log_number=".1"
            fi
        ;;

        2)
            rotatory_file_b_size=$(( $( stat -c '%s' ${log_file}.1 ) / 1024))

            if [[ "${rotatory_file_b_size}" -gt "${max_size_log_bytes}" ]]; then
                next_rotatory_log_number=".2"
            elif [[ "${rotatory_file_b_size}" -lt "${max_size_log_bytes}" ]]; then
                next_rotatory_log_number=".1"
            fi
        ;;

        3)
            rotatory_file_c_size=$(( $( stat -c '%s' ${log_file}.2 ) / 1024))

            if [[ "${rotatory_file_c_size}" -gt "${max_size_log_bytes}" ]]; then
                next_rotatory_log_number=".3"
            elif [[ "${rotatory_file_c_size}" -lt "${max_size_log_bytes}" ]]; then
                next_rotatory_log_number=".2"
            fi
        ;;

        4)
            rotatory_file_d_size=$(( $( stat -c '%s' ${log_file}.3 ) / 1024))
            if [[ "${rotatory_file_d_size}" -gt "${max_size_log_bytes}" ]]; then
                # removing latest log
                rm -rf ${log_file}
                # renaming the logs
                mv ${log_file}.1 ${log_file}
                mv ${log_file}.2 ${log_file}.1
                mv ${log_file}.3 ${log_file}.2
                # creating the first log
                touch ${log_file}.3
                next_rotatory_log_number=".3"
             elif [[ "${rotatory_file_d_size}" -lt "${max_size_log_bytes}" ]]; then
                next_rotatory_log_number=".3"
            fi
        ;;

    esac

    echo ${next_rotatory_log_number} && return
}

check_array() {
    # Check if a value exists in an array.

    # params:
    # - sought_value: the value to find.
    # - array: the array to be checked.
    # return
    # - 0: if the array contains the value.
    # - 1: if the array does not contains the value.

    local sought_value="$1"
    # removing the first element to built the array
    shift
    local array="${@}"

    for item in ${array[@]}
    do
        [[ "${item}" == "${sought_value}" ]] && echo 0 && return
    done

    # the command `echo` is needed in order to capture the return the function.
    echo 1 && return

}

logger (){
    # logger for bash.

    # The aim of this function is to get a common logger for bash (pretty similar)
    # to the one for python.
    # The supported log levels (priorities) are:
    # EMERGENCY - system is unusable
    # ALERT     - action must be taken immediately
    # CRITICAL  - critical conditions
    # ERROR     - error conditions
    # WARN      - warning conditions
    # NOTICE    - normal but significant condition
    # INFO      - informational
    # DEBUG     - debug-level messages
    #
    # param:
    # - message_type: the message type, see log levels priorities.
    # - message_to_display: the message to be displayed in console.
    # environment variables:
    # - OUTPUT_LOG_FILE: file to write the logger messages (optional argument).

    # validating the numbers of arguments passed.
    [[ $# -ne 2 ]] && echo " - (ERROR) - Illegal number of parameters" && return

    # setting local variables
    local message_type="$1"
    local message_to_display="$2"
    local yy_mm_dd=$(date +%F)
    local hh_mm_ss=$(date +%H:%M:%S)
    local script_source=$(basename "$0")
    # if the environment variable "OUTPUT_LOG_FILE" is not set, the default value
    # will be "clonezilla" and the output_log will be created in the same level
    # as this script. This will be useful to write logs in the USB stick script
    # partition.
    local output_log="${OUTPUT_LOG_FILE:-clonezilla}"

    # if OUTPUT_LOG_FILE is set, checking if the path exists, otherwise this
    # will create it.
    [[ ! -z "${OUTPUT_LOG_FILE}" && ! -d $(dirname ${OUTPUT_LOG_FILE}) ]] && \
        mkdir -p $(dirname ${OUTPUT_LOG_FILE})

    # setting the array that contains the supported log levels priorities.
    supported_messages=(DEBUG INFO NOTICE WARN ERROR CRITICAL ALERT EMERGENCY)
    # excluding the following messages from the output.
    exclude_messages=(DEBUG)

    # checking if message_type is in the supported log levels priorities.
    check_array_value=$(check_array "${message_type}" ${supported_messages[*]})

    [[ "${check_array_value}" -ne 0 ]] && \
        echo " - (ERROR) - unrecognized log level : ${message_type}" && return 1

    logger_format="${yy_mm_dd} ${hh_mm_ss} - ${script_source} - \
(${message_type}) - ${message_to_display}"

    # check for the rotatory log to write.
    rotatory_log=$(check_rotatory_logs "${output_log}")
    # checking if the output must to be hide and only direct it to a rotatory log.
    exclude_message_value=$(check_array "${message_type}" ${exclude_messages[*]})

    # checking if the output_log does not exists to set addressing variable.
    [[ ! -f "${output_log}" ]] && addressing="" || addressing="-a"

    # checking if the message needs to be exclude from the output.
    if [[ "${exclude_message_value}" -eq 0 ]]; then
        # logging the message.
        echo "${logger_format}" >> ${output_log}${rotatory_log}
    else
        # logging the message.
        echo "${logger_format}" | tee ${addressing} ${output_log}${rotatory_log}
    fi


}
