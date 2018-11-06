#!/bin/bash

source common.sh

cat /sys/power/state | grep mem
if [ $? -eq 0 ]; then
	date
	sleep 10
	# Clear old alarm
	echo '[CMD]echo 0 > /sys/class/rtc/rtc0/wakealarm'
	echo 0 > /sys/class/rtc/rtc0/wakealarm
	RC=$?
	if [ ${RC} -ne 0 ]; then
		check_rc "[CMD]echo 0 > /sys/class/rtc/rtc0/wakealarm" ${RC}
		return 1
	fi
	echo '[CMD]echo +15 > /sys/class/rtc/rtc0/wakealarm'
	echo +15 > /sys/class/rtc/rtc0/wakealarm
	RC=$?
        if [ ${RC} -ne 0 ]; then
                check_rc "[CMD]echo 15 > /sys/class/rtc/rtc0/wakealarm" ${RC}
                return 1
        fi
#	to change to /sys/class/rtc/rtcN/wakeup in future kernel

	# Save dmesg before S3
	dmesg -c >> dmesg
	echo '[CMD]echo mem > /sys/power/state	#S3'
	echo mem > /sys/power/state	#S3
	dmesg -c >> dmesg

#	date
else
	echo '[NOTE][CMD] S3 is not supported'
fi

cat /sys/power/state | grep disk
if [ $? -eq 0 ]; then
	date
	sleep 10
	# Clear old alarm
	echo '[CMD]echo 0 > /sys/class/rtc/rtc0/wakealarm'
	echo 0 > /sys/class/rtc/rtc0/wakealarm
        RC=$?
        if [ ${RC} -ne 0 ]; then
                check_rc "[CMD]echo 0 > /sys/class/rtc/rtc0/wakealarm" ${RC}
                return 1
        fi

	echo '[CMD]echo +40 > /sys/class/rtc/rtc0/wakealarm'
	echo +40 > /sys/class/rtc/rtc0/wakealarm
        RC=$?
        if [ ${RC} -ne 0 ]; then
                check_rc "[CMD]echo 40 > /sys/class/rtc/rtc0/wakealarm" ${RC}
                return 1
        fi

#	to change to /sys/class/rtc/rtcN/wakeup in future kernel
	dmesg -c >> dmesg
	echo '[CMD]echo disk > /sys/power/state	#S3'
	echo disk > /sys/power/state	#S4
	dmesg -c >> dmesg
else
	echo '[NOTE][CMD] S4 is not supported'
fi

echo "[CMD]suspend_resume end"
