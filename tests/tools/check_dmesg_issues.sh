#!/bin/bash

  # displaying dmesg messages
  # ==========================================
  # Supported log levels (priorities):
  # emerg - system is unusable
  # alert - action must be taken immediately
  # crit - critical conditions
  # err - error conditions
  # warn - warning conditions
  # notice - normal but significant condition
  # info - informational
  # debug - debug-level messages
  # ==========================================

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

  mkdir -p /home/gfx/dmesg_issues &> /dev/null
  export thispath=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

  # Setting the alias for this script
  check_al2=$(cat /home/$CUSER/.bashrc| grep -e "^alias cdmesg")
  if [ -z "$check_al2" ]; then echo "alias cdmesg='$thispath/check_dmesg_issues.sh'" >> /home/$CUSER/.bashrc; fi

  # Setting dmesg level logs
  _d_emerg=$(dmesg --level=emerg | wc -l)
  _d_alert=$(dmesg --level=alert | wc -l)
  _d_crit=$(dmesg --level=crit | wc -l)
  _d_err=$(dmesg --level=err | wc -l)
  _d_warn=$(dmesg --level=warn | wc -l)
  _d_debug=$(dmesg --level=debug | wc -l)

  # Setting logs files
 _EMERGENCY_LOG_FILE=/home/$CUSER/dmesg_issues/dmesg_emergency.log
 _ALERT_LOG_FILE=/home/$CUSER/dmesg_issues/dmesg_alert.log
 _CRITICAL_LOG_FILE=/home/$CUSER/dmesg_issues/dmesg_critical.log
 _ERROR_LOG_FILE=/home/$CUSER/dmesg_issues/dmesg_error.log
 _WARN_LOG_FILE=/home/$CUSER/dmesg_issues/dmesg_warning.log
 _DEBUG_LOG_FILE=/home/$CUSER/dmesg_issues/dmesg_debug.log

 rm /home/$CUSER/dmesg_issues/* 2> /dev/null

 clear; echo; echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"

  if [ ${_d_emerg} -ne 0 ]; then
    echo -ne " --> dmesg ${cyan}EMERGENCY${nc}  : ${bold}${_d_emerg}${nc} msg \n"
    script ${_EMERGENCY_LOG_FILE} bash -c 'dmesg --level=emerg -x -T' > /dev/null
    sed -i '1d' ${_EMERGENCY_LOG_FILE}; sed -i -e '$ d' ${_EMERGENCY_LOG_FILE} # removing Script command lines
  fi

  if [ ${_d_alert} -ne 0 ]; then
    echo -ne " --> dmesg ${blue}ALERT${nc}      : ${bold}${_d_alert}${nc} msg \n"
    script ${_ALERT_LOG_FILE} bash -c 'dmesg --level=alert -x -T' > /dev/null
    sed -i '1d' ${_ALERT_LOG_FILE}; sed -i -e '$ d' ${_ALERT_LOG_FILE} # removing Script command lines
  fi

  if [ ${_d_crit} -ne 0 ]; then
    echo -ne " --> dmesg ${red}CRIT1CAL${nc}   : ${bold}${_d_crit}${nc} msg \n"
    script ${_CRITICAL_LOG_FILE} bash -c 'dmesg --level=crit -x -T' > /dev/null
    sed -i '1d' ${_CRITICAL_LOG_FILE}; sed -i -e '$ d' ${_CRITICAL_LOG_FILE} # removing Script command lines
  fi

  if [ ${_d_err} -ne 0 ]; then
    echo -ne " --> dmesg ${red}ERROR${nc}      : ${bold}${_d_err}${nc} msg \n"
    script ${_ERROR_LOG_FILE} bash -c 'dmesg --level=err -x -T' > /dev/null
    sed -i '1d' ${_ERROR_LOG_FILE}; sed -i -e '$ d' ${_ERROR_LOG_FILE} # removing Script command lines
  fi

  if [ ${_d_warn} -ne 0 ]; then
    echo -ne " --> dmesg ${yellow}WARNING${nc}    : ${bold}${_d_warn}${nc} msg \n"
    script ${_WARN_LOG_FILE} bash -c 'dmesg --level=warn -x -T' > /dev/null
    sed -i '1d' ${_WARN_LOG_FILE}; sed -i -e '$ d' ${_WARN_LOG_FILE} # removing Script command lines
  fi

  if [ ${_d_debug} -ne 0 ]; then
    echo -ne " --> dmesg ${blue}DEBUG${nc}      : ${bold}${_d_debug}${nc} msg \n"
    script ${_DEBUG_LOG_FILE} bash -c 'dmesg --level=debug -x -T' > /dev/null
    sed -i '1d' ${_DEBUG_LOG_FILE}; sed -i -e '$ d' ${_DEBUG_LOG_FILE} # removing Script command lines
  fi

  echo -ne "\n\n"
  echo -ne " Supported log levels (priorities) : \n\n"
  echo -ne " emerg     - system is unusable \n"
  echo -ne " alert     - action must be taken immediately \n"
  echo -ne " crit      - critical conditions \n"
  echo -ne " err       - error conditions \n"
  echo -ne " warn      - warning conditions \n"
  echo -ne " notice    - normal but significant condition \n"
  echo -ne " info      - informational \n"
  echo -ne " debug     - debug-level messages \n\n\n"
  
  echo -ne " to run this script againg please type : (${yellow}cdmesg${nc}) in any path / terminal \n\n"
  echo -ne " ${cyan}===============================================================${nc} \n"
  echo -ne " --> Please check the logs into [/home/$CUSER/dmesg_issues] folder \n"
  echo -ne " ${cyan}===============================================================${nc} \n\n\n"

:<<COMMENT

dmesg --level=warn -T # -T means show time

    if [ -f /sys/firmware/log ] && grep ERROR /sys/firmware/log | \
    grep -v "attempting to recover by searching for header"; then
    eval echo "Firmware error found." $ALOGFILENAME
    : $(( firmware_errors += 1 ))
  fi

COMMENT