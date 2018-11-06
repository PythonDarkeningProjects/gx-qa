#!/bin/bash

source /home/custom/config.cfg

if [ ! -f "/home/${dut_user}/.grubUpdate" ]; then
	echo ${dut_password} | sudo -S ls &> /dev/null; sleep .5
	echo -e "--> updating grub ..."
	echo ${dut_password} | sudo -S update-grub
	touch /home/${dut_user}/.grubUpdate
	echo -e "--> Rebooting DUT ..."
	sleep 2; echo ${dut_password} | sudo -S reboot
	exit 0
fi