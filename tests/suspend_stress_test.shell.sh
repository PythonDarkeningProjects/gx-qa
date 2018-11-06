#!/bin/sh

# Copyright (c) 2012 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

FLAGS_TRUE=1
FLAGS_FALSE=0
#DEFAULT configuration 
#DEFINE_integer count 10 "number of iterations"
FLAGS_count=10
#DEFINE_integer suspend_max 10 "Max seconds to suspend"
FLAGS_suspend_max=x
#DEFINE_integer suspend_min 5 "Min seconds to suspend"
FLAGS_suspend_min=x
#DEFINE_integer wake_max 10 "Max seconds to stay awake for"
FLAGS_wake_max=x
#DEFINE_integer wake_min 5 "Min seconds to stay awake for"
FLAGS_wake_min=x
#DEFINE_boolean backup_rtc ${FLAGS_FALSE} "Use second rtc if present for backup"
FLAGS_backup_rtc=${FLAGS_FALSE}
#DEFINE_boolean bug_fatal ${FLAGS_TRUE} "Abort on BUG dmesg lines"
FLAGS_bug_fatal=${FLAGS_TRUE}
#DEFINE_boolean crc_fatal ${FLAGS_TRUE} "Abort on CRC error dmesg lines"
FLAGS_crc_fatal=${FLAGS_TRUE}
#DEFINE_boolean warn_fatal ${FLAGS_FALSE} "Abort on WARNING dmesg lines"
FLAGS_warn_fatal=${FLAGS_FALSE}
#DEFINE_boolean errors_fatal ${FLAGS_TRUE} "Abort on errors"
FLAGS_errors_fatal=${FLAGS_TRUE}
#DEFINE_boolean memory_check ${FLAGS_FALSE} "Use memory_suspend_test to suspend"
FLAGS_memory_check=${FLAGS_FALSE}
#DEFINE_boolean lev_err_fatal ${FLAGS_TRUE} "Abort on message of level error or less"
FLAGS_lev_err_fatal=${FLAGS_TRUE}
#DEFINE_boolean lev_warn_fatal ${FLAGS_FALSE} "Abort on message of level warning or less"
FLAGS_lev_warn_fatal=${FLAGS_FALSE}
#DEFINE_boolean suspend_to_disk ${FLAGS_FALSE} "Suspend to disk"
FLAGS_suspend_to_disk=${FLAGS_FALSE}
#DEFINE_boolean suspend_to_mem ${FLAGS_TRUE} "Suspend to mem"
FLAGS_suspend_to_mem=${FLAGS_TRUE}
#DEFINE_boolean standby ${FLAGS_FALSE} "standby"
FLAGS_standby=${FLAGS_FALSE}
#DEFINE_boolean suspend_to_idle ${FLAGS_FALSE} "Suspend to Idle"
FLAGS_suspend_to_idle=${FLAGS_FALSE}
#DEFINE_boolean powerd_dbus_suspend ${FLAGS_FALSE} "Power dbus suspend"
FLAGS_powerd_dbus_suspend=${FLAGS_FALSE}

# count suspend stats
success_count_stub=0
get_success_count() {
  if [ ${FLAGS_suspend_to_mem} -eq ${FLAGS_TRUE} ]; then
	awk '$1 == "success:" { print $2 }' /sys/kernel/debug/suspend_stats
  else
	echo $(( success_count_stub + 1 ))
  fi
}
# random number
random() {
  hexdump -n 2 -e '/2 "%u"' /dev/urandom
}
# boolean string
boolean_value() {
  if [ $1 -eq ${FLAGS_TRUE} ]; then
    echo "true"
  else
    echo "false"
  fi
}
# last report
dump_stats_and_exit() {
  echo $preserved_pm_print_times > /sys/power/pm_print_times
  eval echo "" $ALOGFILENAME
  eval echo "Finished ${cur} iterations." $ALOGFILENAME
  eval echo "Suspend_failures: $(( ${cur} -
                              (${success_count_stub} - ${initial_successes}) ))" $ALOGFILENAME
  eval echo "Firmware log errors: ${firmware_errors}" $ALOGFILENAME
  exit 0
}
# displaying configuration information
show_config() {
  eval echo "configuration" $ALOGFILENAME
  eval printf "\ \ " $ALOGFILENAME;eval dmidecode -s bios-version 2> /dev/zero $ALOGFILENAME
  eval printf "\ \ " $ALOGFILENAME;eval dmidecode -s processor-version 2> /dev/zero $ALOGFILENAME
  eval printf "\ \ " $ALOGFILENAME;eval uname -s -r -i $ALOGFILENAME
  eval printf "\ \ " $ALOGFILENAME;eval lsb_release -d 2> /dev/zero $ALOGFILENAME
}
# usage information
usage() {
  echo "usage : run as root"
  echo "    --iterations=nb"
  echo "    --mode=<idle|standby|mem|disk>"
  echo "    --supend=min-max"
  echo "    --wake=min-max"
  echo "    --abort=<none|error|warning>"
  echo "    --display=<none|error|warning>"
  echo "    --file=file name"
  echo "    --nodisplay=<error|warning:prefix;perfix>"
  echo "    --help"
}
# displaying messages
display() {
  if [ $DISPLAY = "none" ]; then
	return
  fi
  if [ `dmesg --level=emerg | wc -l` -ne 0 ]; then
  eval echo "EMERGENCY : " `dmesg --level=emerg | wc -l` $ALOGFILENAME
	eval dmesg --level=emerg $cmd_noerr $ALOGFILENAME
  fi
  if [ `dmesg --level=alert | wc -l` -ne 0 ]; then
  eval echo "ALERT     : " `dmesg --level=alert | wc -l` $ALOGFILENAME
	eval dmesg --level=alert $cmd_noerr $ALOGFILENAME
  fi
  if [ `dmesg --level=crit | wc -l` -ne 0 ]; then
  eval echo "CRITICAL  : " `dmesg --level=crit | wc -l` $ALOGFILENAME
	eval dmesg --level=crit $cmd_noerr $ALOGFILENAME
  fi
  if [ `dmesg --level=err | wc -l` -ne 0 ]; then
  eval echo "ERROR     : " `dmesg --level=err | wc -l` $ALOGFILENAME
	eval dmesg --level=err $cmd_noerr $ALOGFILENAME
  fi
  if [ $DISPLAY = "warning" ]; then
  if [ `dmesg --level=warn | wc -l` -ne 0 ]; then
  eval echo "WARNING   : " `dmesg --level=warn | wc -l` $ALOGFILENAME
	eval dmesg --level=warn $cmd_nowarn $ALOGFILENAME
  fi
  fi
}
# build a command to avoid displaying some warning messages
build_cmd_nowarn() {
  cmd_nowarn=""
  nowarn=`echo $NODISPLAY | sed s/^.*warning://g | sed s/error.*$//g`
  IFS=';'
  for i in $nowarn; do
      cmd_nowarn+=" | sed /^\\\[.*\\\]\\ \""$i"\"/d"
  done
  echo "$cmd_nowarn"
}
# build a command to avoid displaying some error messages
build_cmd_noerr() {
  cmd_noerr=""
  noerr=`echo $NODISPLAY | sed s/^.*error://g | sed s/warning.*$//g`
  IFS=';'
  for i in $noerr; do
      cmd_noerr+=" | sed /^\\\[.*\\\]\\ \""$i"\"/d"
  done
  echo $cmd_noerr
}
# initialisation
MODE="mem"
ABORT="error"
SUSPEND=5-10
WAKE=5-10
DISPLAY="none"
NODISPLAY=""
ALOGFILENAME=""
LOGFILENAME=""
cmd_noerr=""
cmd_nowarn=""
# parse command line
for WORD in "$@" ; do
 case $WORD in
  --*) true ;
    case $WORD in
      --iterations=*)
          FLAGS_count=${WORD#--iterations=}
          shift ;;	
      --mode=*)
          MODE=${WORD#--mode=}
          shift ;;	  
      --suspend=*)
          SUSPEND=${WORD#--suspend=}
          shift ;;
      --wake=*)
          WAKE=${WORD#--wake=}
          shift ;;
      --abort=*)
          ABORT=${WORD#--abort=}
          shift ;;
      --display=*)
	  DISPLAY=${WORD#--display=}
	  shift ;;
      --nodisplay=*)
	  NODISPLAY=${WORD#--nodisplay=}
	  cmd_noerr=$(build_cmd_noerr)
	  cmd_nowarn=$(build_cmd_nowarn)
	  shift ;;
      --file=*)
	  LOGFILENAME=${WORD#--file=}
	  ALOGFILENAME=">> ${WORD#--file=}"
	  shift ;;
      --help)
          usage
          exit 0
	  ;;
      *) echo "Unrecognized argument $WORD"
	  usage
	  exit 1
          ;;
    esac ;;
  *) echo "Option $WORD not starting with double dash."
     exit 1
     ;;
 esac
done
# only root
if [ "$USER" != root ]; then
  echo "This script must be run as root." 1>&2
  exit 1
fi
# select mode S0 S1 S3 or S4
case $MODE in
     disk) 
	FLAGS_suspend_to_disk=${FLAGS_TRUE}
	FLAGS_suspend_to_mem=${FLAGS_FALSE}
	;;
     mem)
	;;
     standby)
	FLAGS_standby=${FLAGS_TRUE}
	FLAGS_suspend_to_mem=${FLAGS_FALSE}
	;;
     idle)
	FLAGS_suspend_to_idle=${FLAGS_TRUE}
	FLAGS_suspend_to_mem=${FLAGS_FALSE}
	;;
     *) echo "supported modes are idle - standby - mem - disk"
	exit 1
        ;;
esac
# parse suspend and wake option
#TBD check SUSPEND and WAKE syntax and order
FLAGS_suspend_min=$(echo $SUSPEND | sed s/-.*$//)
FLAGS_suspend_max=$(echo $SUSPEND | sed s/^.*-//)
FLAGS_wake_min=$(echo $WAKE | sed s/-.*$//)
FLAGS_wake_max=$(echo $WAKE | sed s/^.*-//)
# choose abort level
case $ABORT in
     none)
	FLAGS_bug_fatal=${FLAGS_FALSE}
	FLAGS_crc_fatal=${FLAGS_FALSE}
	FLAGS_errors_fatal=${FLAGS_FALSE}
	FLAGS_lev_err_fatal=${FLAGS_FALSE}
	;;
     error)
	;;
     warning)
	FLAGS_warn_fatal=${FLAGS_TRUE}
	FLAGS_lev_warn_fatal=${FLAGS_TRUE}
	;;
     *) echo "supported abort are none - error - warning"
	exit 1
        ;;
esac

if [ ${FLAGS_backup_rtc} -eq ${FLAGS_TRUE} ] &&
  [ ! -e /sys/class/rtc/rtc1/wakealarm ]; then
  eval echo "rtc1 not present, not setting second wakealarm"  $ALOGFILENAME
  FLAGS_backup_rtc=${FLAGS_FALSE}
fi

if [ ${FLAGS_memory_check} -eq ${FLAGS_TRUE} ]; then
  free_kb=$(grep MemFree: /proc/meminfo | awk '{ print $2}')
  inactive_kb=$(grep Inactive: /proc/meminfo | awk '{ print $2}')
  slack_kb=100000
  bytes=$(((free_kb + inactive_kb - slack_kb) * 1024))
  suspend_cmd="memory_suspend_test --size=${bytes}"

  # Writing to memory can take a while. Make it less likely that the
  # wake alarm will fire before the system has suspended.
  if [ $FLAGS_suspend_min -lt $MEMORY_TEST_SUSPEND_MIN_DELAY ]; then
    local orig_diff=$(($FLAGS_suspend_max - $FLAGS_suspend_min))
    FLAGS_suspend_min=$MEMORY_TEST_SUSPEND_MIN_DELAY
    FLAGS_suspend_max=$(($FLAGS_suspend_min + $orig_diff))
  fi
elif [ ${FLAGS_suspend_to_disk} -eq ${FLAGS_TRUE} ]; then
  suspend_cmd="echo disk > /sys/power/state"
elif [ ${FLAGS_suspend_to_mem} -eq ${FLAGS_TRUE} ]; then
  suspend_cmd="echo mem > /sys/power/state"
elif [ ${FLAGS_standby} -eq ${FLAGS_TRUE} ]; then
  suspend_cmd="echo standby > /sys/power/state"
elif [ ${FLAGS_suspend_to_idle} -eq ${FLAGS_TRUE} ]; then
  suspend_cmd="echo freeze > /sys/power/state"
#TBD
#elif [ ${FLAGS_powerd_dbus_suspend} -eq ${FLAGS_TRUE} ]; then
#suspend_cmd="powerd_dbus_suspend --delay=0"
fi

echo "Running ${FLAGS_count} iterations with:" | tee -a $LOGFILENAME
eval echo "\  suspend: ${FLAGS_suspend_min}-${FLAGS_suspend_max} seconds" $ALOGFILENAME
eval echo "\  wake: ${FLAGS_wake_min}-${FLAGS_wake_max} seconds" $ALOGFILENAME
eval echo "\  backup_rtc: $(boolean_value ${FLAGS_backup_rtc})" $ALOGFILENAME
eval echo "\  errors_fatal: $(boolean_value ${FLAGS_errors_fatal})" $ALOGFILENAME
eval echo "\  bugs fatal:  $(boolean_value ${FLAGS_bug_fatal})" $ALOGFILENAME
eval echo "\  warnings fatal:  $(boolean_value ${FLAGS_warn_fatal})" $ALOGFILENAME
eval echo "\  crcs fatal:  $(boolean_value ${FLAGS_crc_fatal})" $ALOGFILENAME
eval echo "\  level warning fatal:  $(boolean_value ${FLAGS_lev_warn_fatal})" $ALOGFILENAME
eval echo "\  level error fatal:  $(boolean_value ${FLAGS_lev_err_fatal})" $ALOGFILENAME
echo "  suspend command: ${suspend_cmd}" | tee -a $LOGFILENAME

# initialisation
success_count_stub=$(get_success_count)
initial_successes=$success_count_stub
suspend_interval=$(( FLAGS_suspend_max - FLAGS_suspend_min + 1 ))
wake_interval=$(( FLAGS_wake_max - FLAGS_wake_min + 1 ))
preserved_pm_print_times=$(cat /sys/power/pm_print_times)

echo 1 > /sys/power/pm_print_times

trap dump_stats_and_exit INT

cur=0
firmware_errors=0
last_successes=${initial_successes}
exit_loop=0

#configuration information
show_config
# iterate suspend and resume
while true; do
  : $(( cur += 1 ))
  printf "Suspend %5d of ${FLAGS_count}: " ${cur} | tee -a $LOGFILENAME

  sus_time=$(( ( $(random) % suspend_interval ) + FLAGS_suspend_min ))
  printf "sleep for %2d seconds..." ${sus_time} | tee -a $LOGFILENAME
  wakeup_count=$(cat /sys/power/wakeup_count)
  echo 0 > /sys/class/rtc/rtc0/wakealarm
  echo "+${sus_time}" > /sys/class/rtc/rtc0/wakealarm
  if [ ${FLAGS_backup_rtc} -eq ${FLAGS_TRUE} ]; then
    echo 0 > /sys/class/rtc/rtc1/wakealarm
    echo "+$(( sus_time + 5 ))" > /sys/class/rtc/rtc1/wakealarm
  fi

  #eval "$suspend_cmd --wakeup_count=${wakeup_count}"
  eval "$suspend_cmd"

  # Look for errors in firmware log.
  # Exempt a specific error string in Coreboot that is not a real error.
  # TODO(shawnn): Remove this exemption once all devices have firmware with
  # this error string changed.
  if [ -f /sys/firmware/log ] && grep ERROR /sys/firmware/log | \
    grep -v "attempting to recover by searching for header"; then
    eval echo "Firmware error found." $ALOGFILENAME
    : $(( firmware_errors += 1 ))
    if [ ${FLAGS_errors_fatal} -eq ${FLAGS_TRUE} ]; then
      exit_loop=1
    fi
  fi
  # Make sure suspend succeeded
  success_count_stub=$(get_success_count)
  cur_successes=$success_count_stub
  if [ ${cur_successes} -eq ${last_successes} ]; then
    if [ ${FLAGS_errors_fatal} -eq ${FLAGS_TRUE} ]; then
      eval echo "Suspend failed." $ALOGFILENAME
      exit_loop=1
    else
      eval printf "(suspend failed, ignoring)" $ALOGFILENAME
    fi
  fi
  last_successes=${cur_successes}
  # For BUG and CRC errors counting existing occurrences in dmesg
  # is not that useful as dmesg will wrap so we would need to account
  # for the count shrinking over time.
  # Exit on BUG
  if [ ${FLAGS_bug_fatal} -eq ${FLAGS_TRUE} ] &&
        dmesg | grep -w BUG; then
    eval echo "BUG found." $ALOGFILENAME
    exit_loop=1
  fi
  # Exit on WARNING
  if [ ${FLAGS_warn_fatal} -eq ${FLAGS_TRUE} ] &&
        dmesg | grep -w WARNING; then
    eval echo "WARNING found." $ALOGFILENAME
    exit_loop=1
  fi
  # Exit on CRC error
  if [ ${FLAGS_crc_fatal} -eq ${FLAGS_TRUE} ] && dmesg | grep "CRC.*error"; then
    eval echo "CRC error found." $ALOGFILENAME
    exit_loop=1
  fi
  # Display message
  display

  # Exit on Log Level message ERR
  if [ ${FLAGS_lev_err_fatal} -eq ${FLAGS_TRUE} ] && [ `dmesg --level=emerg,alert,crit,err | wc -l` -ne 0 ]; then
    eval echo "Error level found." $ALOGFILENAME
    exit_loop=1
  fi
  # Exit on Log Level message WARN
  if [ ${FLAGS_lev_warn_fatal} -eq ${FLAGS_TRUE} ] && [ `dmesg --level=emerg,alert,crit,err,warn | wc -l` -ne 0 ]; then
    eval echo "Warning level found." $ALOGFILENAME
    exit_loop=1
  fi 
 
  # Exit the loop if requested from errors or done with iterations
  if [ ${cur} -eq ${FLAGS_count} ] || [ ${exit_loop} -eq 1 ]; then
    eval echo "" $ALOGFILENAME
    break
  fi
  wake_time=$(( ( $(random) % wake_interval ) + FLAGS_wake_min ))
  printf " wake for %2d seconds..." ${wake_time} | tee -a $LOGFILENAME
  sleep ${wake_time}
  eval echo "" $ALOGFILENAME
done

dump_stats_and_exit
