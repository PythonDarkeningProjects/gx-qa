#!/bin/bash
	
	loadkeys us
	export _SCRIPTS_PARTITION=`blkid | grep "scripts" | awk -F":" '{print $1}' | sed 's|/dev/||g'` # sdX
	mount /dev/${_SCRIPTS_PARTITION} /root/

