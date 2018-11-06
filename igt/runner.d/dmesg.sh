#!/bin/bash

function CheckDmesgInfo () {

  # Setting dmesg level logs
  _d_emerg=$(dmesg --level=emerg | wc -l)
  _d_alert=$(dmesg --level=alert | wc -l)
  _d_crit=$(dmesg --level=crit | wc -l)
  _d_err=$(dmesg --level=err | wc -l)
  _d_warn=$(dmesg --level=warn | wc -l)
  _d_debug=$(dmesg --level=debug | wc -l)

  _d_notice=$(dmesg --level=notice | wc -l)
  _d_info=$(dmesg --level=info | wc -l)

  # Setting logs files
  mPATH="$1"
 _EMERGENCY_LOG_FILE=${mPATH}/dmesg_emergency.log
 _ALERT_LOG_FILE=${mPATH}/dmesg_alert.log
 _CRITICAL_LOG_FILE=${mPATH}/dmesg_critical.log
 _ERROR_LOG_FILE=${mPATH}/dmesg_error.log
 _WARN_LOG_FILE=${mPATH}/dmesg_warning.log
 _NOTICE_LOG_FILE=${mPATH}/dmesg_notice.log
 _INFO_LOG_FILE=${mPATH}/dmesg_information.log
 _DEBUG_LOG_FILE=${mPATH}/dmesg_debug.log

  if [ ${_d_emerg} -ne 0 ]; then
    echo -ne "${cyan}-->${nc} dmesg ${cyan}EMERGENCY${nc} : (${bold}${_d_emerg}${nc}) msg \n"
    script ${_EMERGENCY_LOG_FILE} bash -c 'dmesg --level=emerg -x -T' > /dev/null
    sed -i '1d' ${_EMERGENCY_LOG_FILE}; sed -i -e '$ d' ${_EMERGENCY_LOG_FILE} # removing Script command lines
    sed -i '/^\s*$/d' ${_EMERGENCY_LOG_FILE}
  fi

  if [ ${_d_alert} -ne 0 ]; then
    echo -ne "${cyan}-->${nc} dmesg ${blue}ALERT${nc}     : (${bold}${_d_alert}${nc}) msg \n"
    script ${_ALERT_LOG_FILE} bash -c 'dmesg --level=alert -x -T' > /dev/null
    sed -i '1d' ${_ALERT_LOG_FILE}; sed -i -e '$ d' ${_ALERT_LOG_FILE} # removing Script command lines
    sed -i '/^\s*$/d' ${_ALERT_LOG_FILE}
  fi

  if [ ${_d_crit} -ne 0 ]; then
    echo -ne "${cyan}-->${nc} dmesg ${red}CRIT1CAL${nc}   : (${bold}${_d_crit}${nc}) msg \n"
    script ${_CRITICAL_LOG_FILE} bash -c 'dmesg --level=crit -x -T' > /dev/null
    sed -i '1d' ${_CRITICAL_LOG_FILE}; sed -i -e '$ d' ${_CRITICAL_LOG_FILE} # removing Script command lines
    sed -i '/^\s*$/d' ${_CRITICAL_LOG_FILE}
  fi

  if [ ${_d_err} -ne 0 ]; then
    echo -ne "${cyan}-->${nc} dmesg ${red}ERROR${nc}   : (${bold}${_d_err}${nc}) msg \n"
    script ${_ERROR_LOG_FILE} bash -c 'dmesg --level=err -x -T' > /dev/null
    sed -i '1d' ${_ERROR_LOG_FILE}; sed -i -e '$ d' ${_ERROR_LOG_FILE} # removing Script command lines
    sed -i '/^\s*$/d' ${_ERROR_LOG_FILE}
  fi

  if [ ${_d_warn} -ne 0 ]; then
    echo -ne "${cyan}-->${nc} dmesg ${yellow}WARNING${nc} : (${bold}${_d_warn}${nc}) msg \n"
    script ${_WARN_LOG_FILE} bash -c 'dmesg --level=warn -x -T' > /dev/null
    sed -i '1d' ${_WARN_LOG_FILE}; sed -i -e '$ d' ${_WARN_LOG_FILE} # removing Script command lines
    sed -i '/^\s*$/d' ${_WARN_LOG_FILE}
  fi

  if [ ${_d_notice} -ne 0 ]; then
    echo -ne "${cyan}-->${nc} dmesg ${yellow}NOTICE${nc}  : (${bold}${_d_notice}${nc}) msg \n"
    script ${_NOTICE_LOG_FILE} bash -c 'dmesg --level=notice -x -T' > /dev/null
    sed -i '1d' ${_NOTICE_LOG_FILE}; sed -i -e '$ d' ${_NOTICE_LOG_FILE} # removing Script command lines
    sed -i '/^\s*$/d' ${_NOTICE_LOG_FILE}
  fi

  if [ ${_d_info} -ne 0 ]; then
    echo -ne "${cyan}-->${nc} dmesg ${yellow}INFO${nc}    : (${bold}${_d_info}${nc}) msg \n"
    script ${_INFO_LOG_FILE} bash -c 'dmesg --level=info -x -T' > /dev/null
    sed -i '1d' ${_INFO_LOG_FILE}; sed -i -e '$ d' ${_INFO_LOG_FILE} # removing Script command lines
    sed -i '/^\s*$/d' ${_INFO_LOG_FILE}
  fi

  if [ ${_d_debug} -ne 0 ]; then
    echo -ne "${cyan}-->${nc} dmesg ${blue}DEBUG${nc}   : (${bold}${_d_debug}${nc}) msg \n"
    script ${_DEBUG_LOG_FILE} bash -c 'dmesg --level=debug -x -T' > /dev/null
    sed -i '1d' ${_DEBUG_LOG_FILE}; sed -i -e '$ d' ${_DEBUG_LOG_FILE} # removing Script command lines
    sed -i '/^\s*$/d' ${_DEBUG_LOG_FILE}
  fi

  #echo -ne " Supported log levels (priorities) : \n\n"
  #echo -ne " emerg     - system is unusable \n"
  #echo -ne " alert     - action must be taken immediately \n"
  #echo -ne " crit      - critical conditions \n"
  #echo -ne " err       - error conditions \n"
  #echo -ne " warn      - warning conditions \n"
  #echo -ne " notice    - normal but significant condition \n"
  #echo -ne " info      - informational \n"
  #echo -ne " debug     - debug-level messages \n\n\n"
}

CheckDmesgInfo "$1"
