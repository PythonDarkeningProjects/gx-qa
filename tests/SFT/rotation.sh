#!/bin/bash

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

	echo -ne "\n\n"

	export thispath=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd ) # <- current script path, even if i call from tux ;)
	source $thispath/common.sh

	OUTPUT=$(xrandr -q |grep -w connected | head -1 |awk '{print $1}')
	
	echo -ne " --> ${yellow}xrandr --output $OUTPUT --rotate left${nc} \n"
	sleep 2
	xrandr --output $OUTPUT --rotate left
	check_rc "xrandr/left" $?
	echo -ne " --> ${yellow}xrandr --output $OUTPUT --rotate right${nc} \n"
	sleep 3
	xrandr --output $OUTPUT --rotate right
	check_rc "xrandr/right" $?
	echo -ne " --> ${yellow}xrandr --output $OUTPUT --rotate normal${nc} \n"
	sleep 10s
	xrandr --output $OUTPUT --rotate normal
	check_rc "xrandr/normal" $?
	echo -ne " --> ${yellow}xrandr --output $OUTPUT --rotate inverted${nc} \n"
	sleep 7
	xrandr --output $OUTPUT --rotate inverted
	check_rc "xrandr/inverted" $?
	echo -ne " --> ${yellow}xrandr --output $OUTPUT --rotate normal${nc} \n"
	sleep 7
	xrandr --output $OUTPUT --rotate normal
	check_rc "xrandr/normal" $?
	echo -ne "\n\n"
	echo -ne " ${bold}${blue}Rotation tests has finished${nc} \n\n\n"; exit 2

