#!/bin/bash

	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>
	export CUSER=$(whoami)
	export PASSWORD=linux
	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>s

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

function SFT_main_menu {

	pause(){
		local m="$@"
		echo "$m"
	}

	while :
	do
		clear; echo -ne "\n\n"
		echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
		echo -ne " (${yellow}SFT tests${nc}) Please select a test : \n\n"
		echo -ne " 1) Render tests \n"
		echo -ne " 2) Rotation tests \n"
		echo -ne " 3) S3 test \n"
		echo -ne " 4) S4 test \n"
		echo -ne " 5) Video test \n"
		echo -ne " 6) TTys (${underline}virtual terminals${nc}) tests \n"
		echo -ne " 7) ${yellow}Return to main menu${nc} \n\n"
		read -p " Your choice : " choose

		case $choose in 

			1) exec tests/SFT/render.sh ;;
			2) exec tests/SFT/rotation.sh ;;
			3) exec tests/SFT/s3.sh ;;
			4) exec tests/SFT/s4.sh ;;
			5) exec tests/SFT/video.sh ;;
			6) exec tests/SFT/vt.sh ;;
			7) mainMenu ;;
			*) SFT_menu ;;


		esac

	done


}