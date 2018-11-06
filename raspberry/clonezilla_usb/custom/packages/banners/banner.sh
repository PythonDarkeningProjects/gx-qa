#!/usr/bin/env bash

# Reference : http://patorjk.com/software/taag/#p=display&f=Digital&t=Restoring%20image
# http://www.network-science.de/ascii/ (digital letter)

source /root/custom/packages/all/functions.sh

function initialization () {
	clear; echo -ne "\n\n\n"
	echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
	echo "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
	echo "|i|n|i|t|i|a|l|i|z|a|t|i|o|n|"
	echo "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
	echo -ne "\n\n"; sleep .5
}

function suite_igt () {
	clear; echo -ne "\n\n\n"
	echo "+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
	echo "|S|U|I|T|E| |[|i|n|t|e|l|-|g|p|u|-|t|o|o|l|s|]|"
	echo "+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
	echo -ne "\n\n"; sleep 3
}

function suite_ezbench () {
	clear; echo -ne "\n\n\n"
	echo "+-+-+-+-+-+ +-+-+-+-+-+-+-+"
	echo "|S|U|I|T|E| |e|z|b|e|n|c|h|"
	echo "+-+-+-+-+-+ +-+-+-+-+-+-+-+"
	echo -ne "\n\n"; sleep 3
}


function suite_ezbench_rendercheck () {
    clear; echo -ne "\n\n\n"
    echo"+-+-+-+-+-+ +-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+"
    echo"|S|U|I|T|E| |e|z|b|e|n|c|h| |r|e|n|d|e|r|c|h|e|c|k|"
    echo"+-+-+-+-+-+ +-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+"
	echo -ne "\n\n"; sleep 3
}

function suite_ezbench_igt () {
    clear; echo -ne "\n\n\n"
    echo"+-+-+-+-+-+ +-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
    echo"|S|U|I|T|E| |e|z|b|e|n|c|h| |i|n|t|e|l|-|g|p|u|-|t|o|o|l|s|"
    echo"+-+-+-+-+-+ +-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
	echo -ne "\n\n"; sleep 3
}

function suite_ezbench_benchmarks () {
    clear; echo -ne "\n\n\n"
    echo"+-+-+-+-+-+ +-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+"
    echo"|S|U|I|T|E| |e|z|b|e|n|c|h| |b|e|n|c|h|m|a|r|k|s|"
    echo"+-+-+-+-+-+ +-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+"
	echo -ne "\n\n"; sleep 3
}


function set_environment () {
	clear; echo -ne "\n\n\n"
 	echo -e "${cyan}+-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+${nc}"
 	echo -e "${cyan}|S|e|t|t|i|n|g| |e|n|v|i|r|o|n|m|e|n|t|${nc}"
 	echo -e "${cyan}+-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+${nc}"
	echo -ne "\n\n"; sleep .5
}


function resize_disk () {
	clear; echo -ne "\n\n\n"
 	echo "+-+-+-+-+-+-+-+-+ +-+-+-+-+"
 	echo "|R|e|s|i|z|i|n|g| |d|i|s|k|"
 	echo "+-+-+-+-+-+-+-+-+ +-+-+-+-+"
	echo -ne "\n\n"; sleep .5
}

function set_image () {
	clear; echo -ne "\n\n\n"
	echo "+-+-+-+-+-+-+-+-+-+ +-+-+-+-+-+"
	echo "|R|e|s|t|o|r|i|n|g| |i|m|a|g|e|"
	echo "+-+-+-+-+-+-+-+-+-+ +-+-+-+-+-+"
	echo -ne "\n\n"; sleep 3
}

function skip_updates () {
	echo -ne "\n\n"
	echo -e "${yellow}+-++-++-++-++-++-++-++-+ +-++-++-++-++-++-++-+${nc}"
	echo -e "${yellow}|s||k||i||p||p||i||n||g| |u||p||d||a||t||e||s|${nc}"
	echo -e "${yellow}+-++-++-++-++-++-++-++-+ +-++-++-++-++-++-++-+${nc}"
	echo -ne "\n\n"; sleep 3
}

function up_to_date () {

	echo -ne "\n\n"
	echo -e "${green}+-++-++-++-++-++-+ +-++-++-++-++-++-+ +-++-+ +-++-++-++-++-++-++-++-++-++-+${nc}"
	echo -e "${green}|c||u||s||t||o||m| |f||o||l||d||e||r| |i||s| |u||p||-||t||o||-||d||a||t||e|${nc}"
	echo -e "${green}+-++-++-++-++-++-+ +-++-++-++-++-++-+ +-++-+ +-++-++-++-++-++-++-++-++-++-+${nc}"
	echo -ne "\n\n"; sleep 3
}

function applying_updates () {
	echo -ne "\n\n"
	echo -e "${cyan}+-++-++-++-++-++-++-++-+ +-++-++-+ +-++-++-++-++-++-++-+${nc}"
	echo -e "${cyan}|A||p||p||l||y||i||n||g| |U||S||B| |u||p||d||a||t||e||s|${nc}"
	echo -e "${cyan}+-++-++-++-++-++-++-++-+ +-++-++-+ +-++-++-++-++-++-++-+${nc}"
	echo -ne "\n\n"; sleep 2
}

function reboot_for_updates () {

	echo -ne "\n\n\n"
	echo "+-++-++-++-++-++-++-++-++-+ +-++-+ +-++-++-++-++-+ +-++-++-+ +-++-++-++-++-++-++-+"
	echo "|R||e||b||o||o||t||i||n||g| |t||o| |a||p||p||l||y| |U||S||B| |u||p||d||a||t||e||s|"
	echo "+-++-++-++-++-++-++-++-++-+ +-++-+ +-++-++-++-++-+ +-++-++-+ +-++-++-++-++-++-++-+"
	echo -ne "\n\n"; sleep 3
}


function skip_installation () {

	case "$1" in

		kernel)
			echo -e "${yellow}+-+-+-+-+-+-+-+ +-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+${nc}"
			echo -e "${yellow}|S|k|i|p|i|n|g| |k|e|r|n|e|l| |i|n|s|t|a|l|l|a|t|i|o|n|${nc}"
			echo -e "${yellow}+-+-+-+-+-+-+-+ +-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+${nc}"
			echo; sleep 2
		;;

		gfx_stack)
			echo -e "${yellow}+-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+ +-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+${nc}"
			echo -e "${yellow}|S|k|i|p|i|n|g| |g|r|a|p|h|i|c| |s|t|a|c|k| |i|n|s|t|a|l|l|a|t|i|o|n|${nc}"
			echo -e "${yellow}+-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+ +-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+${nc}"
			echo; sleep 2
		;;
	esac

}

$@