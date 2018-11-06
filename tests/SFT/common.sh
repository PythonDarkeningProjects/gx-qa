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

function check_rc()
{
	MSG=$1
	RC=$2
	
	if [ ${RC} -ne 0 ]; then
		echo -ne "${red}FAIL${nc}: ${MSG} rc=${RC} \n"
	fi
}
