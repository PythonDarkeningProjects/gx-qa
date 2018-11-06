#!/bin/bash
# https://packages.debian.org/wheezy/i386/libgcrypt11/download

	clear
	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>
	export _USER=$(whoami)
	export _PASSWORD=linux
	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>
	# Setting the path
	export _THISPATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd ) # <- current script path, even if i call from tux ;)

	source ${_THISPATH}/functions.sh


function dependencies {

		clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
		start_time
		echo ${_PASSWORD} | sudo -S ls -l &> /dev/null; sleep 2
		# Adding i386 architecture
		# echo ${_PASSWORD} | sudo -S dpkg --add-architecture i386 &> /dev/null  # <<-- not good because libc cannot be installed with foreing architecture
		# Updating the system
		#start_spinner "--> Upgrading the system ..."
			#echo ${_PASSWORD} | sudo -S apt-key update -q=2 &> /tmp/log
			#echo ${_PASSWORD} | sudo -S apt-get update --allow-unauthenticated -q=2 &> /tmp/log
			#echo ${_PASSWORD} | sudo -S apt-get upgrade --allow-unauthenticated -q=2 &> /tmp/log
		#stop_spinner $?

		#if [ ${_STATUS} = 1 ]; then
			#echo -ne "\n\n"; echo -ne "--> ${red}Something was wrong${nc} ..."; echo -ne "\n\n"
			#cat /tmp/log; echo -ne "\n\n"
			#exit 1
		#fi


	#########################################
	# Checking for dependencies             #
	#########################################

	_XORG_LIST="xserver-xorg-dev libxcb-keysyms1-dev xutils-dev intltool spice-protocol* x11proto-xf86dga-dev gtk2.0 libxcb* libxmuu-dev libxcb* libwacom*"  # intltool is for ubuntu 17.04
	_XSERVER_LIST="libgcrypt11-dev xorg-dev libxcb-keysyms1-dev libgl1-mesa-dev x11proto-xcmisc-dev x11proto-bigreqs-dev xfonts-utils"
	#_MESA_LIST="git mesa-utils bison flex libudev-dev libx11-xcb-dev libxcb-glx0-dev libxcb-dri2-0-dev libxcb-dri3-dev libxcb-present-dev libxcb-sync-dev libxshmfence-dev libdrm-intel1 libxext-dev libxdamage-dev libxfixes-dev x11proto-dri2-dev x11proto-xf86dri-dev libexpat1-dev llvm python-mako x11proto-gl-dev libdrm-dev libglapi-mesa libgles* libglu1-mesa-dev freeglut3-dev libgles2-mesa x11proto-gl-dev x11proto-dri3-dev x11proto-present-dev libomxil-bellagio-dev" # libgles1-mesa deprecated for ubuntu 17.04
	_MESA_LIST="git mesa-utils bison flex libudev-dev libx11-xcb-dev libxcb-glx0-dev libxcb-dri2-0-dev libxcb-dri3-dev libxcb-present-dev libxcb-sync-dev libxshmfence-dev libdrm-intel1 libxext-dev libxdamage-dev libxfixes-dev x11proto-dri2-dev x11proto-xf86dri-dev libexpat1-dev llvm python-mako x11proto-gl-dev libdrm-dev libglapi-mesa libglu1-mesa-dev freeglut3-dev libgles2-mesa x11proto-gl-dev x11proto-dri3-dev x11proto-present-dev libomxil-bellagio-dev" # libgles1-mesa deprecated for ubuntu 17.04
	_VAAPI_LIST="libva-dev libdrm-dev libpciaccess-dev vainfo"
	_DRM_LIST="valgrind xsltproc gawk"
	_ALL_DRIVERS_LIST_="dh-autoreconf python-mako"
	_IGT_LIST="libprocps-dev libkmod-dev autoconf libtool libcairo2-dev swig libpython3-dev libunwind8 libunwind8-dev python-pip libyaml-dev gtk-doc-tools libxmlrpc-core-c3-dev libcunit1 libcunit1-doc libcunit1-dev" # swig2.0 is only available in ubuntu 15X but no in ubuntu 16, instead swig
	_PIGLIT_LIST="libxrender-dev python-numpy mesa-common-dev g++ cmake docbook-xsl libtiff5-dev python-six" # libtiff5-dev:i386 # <<-- not good because libc cannot be installed with foreing architecture
	_RENDERCHECK_LIST="libxrender1 csh libgles2-mesa-dev" # libgles1-mesa-dev deprecated for ubuntu 17.04
	_OTHERS_LIST="csvtool sendmail libncurses5-dev libncursesw5-dev dpkg-dev libssl-dev libqt4-dev pkg-config w3m ssh dos2unix zenity libcheese-dev python-pymongo python3-pymongo python3-numpy python-numpy pv python-yaml python3-yaml python-astropy python-tabulate v86d ipython python-requests"
	_XF86="libevdev* mtdev-tools libmtdev-dev"

	for dependence in ${_XORG_LIST} ${_XSERVER_LIST} ${_MESA_LIST} ${_VAAPI_LIST} ${_DRM_LIST} ${_ALL_DRIVERS_LIST_} ${_IGT_LIST} ${_PIGLIT_LIST} ${_RENDERCHECK_LIST} ${_OTHERS_LIST} ${_XF86}; do
		_CHECK_DEPENDENCE=`dpkg -l | grep -w "${dependence}"`
		if [ -z "${_CHECK_DEPENDENCE}" ]; then
			start_spinner "--> Installing ${dependence} ..."
				echo ${_PASSWORD} | sudo -S apt-get install ${dependence} --allow-unauthenticated -q=2 &> /tmp/log
			stop_spinner $?
			if [ ${_STATUS} = 1 ]; then
				echo -ne "\n\n"; echo -ne "--> ${red}Something was wrong${nc} ..."; echo -ne "\n\n"
				cat /tmp/log; echo -ne "\n\n"; exit 1
			fi
		fi
	done

	# For Steam
	#libgl1-mesa-dri:i386 -q=2
	#libgl1-mesa-glx:i386 -q=2
	#libc6:i386 -q=2

	typearchitecture=$(uname -p) # x86_64 = 64 bits    i386 = 32 bits i686= 32 Bits
	if [ ${typearchitecture} = "x86" ] || [ ${typearchitecture} = "i686" ]; then export architecture=32-bit; elif [ $typearchitecture = "x86_64" ]; then export architecture="64-bit"; fi
		if [ "${architecture}" =  "32-bit" ]; then
			# This dependence is needed for Mesa and DRM 32 bits
			start_spinner "--> Installing libgcrypt_11_1.5.0 (32bit) ..."
				echo ${_PASSWORD} | sudo -S dpkg -i ${_THISPATH}/libgcrypt11_1.5.0-5+deb7u4_i386.deb &> /dev/null
			stop_spinner $?
		elif [ "${architecture}" =  "64-bit" ]; then
			# This dependence is needed for Mesa and DRM 64 bits
			start_spinner "--> Installing libgcrypt_11_1.5.0 (64bit) ..."
				echo ${_PASSWORD} | sudo -S dpkg -i ${_THISPATH}/libgcrypt11_1.5.0-5+deb7u4_amd64.deb &> /dev/null
			stop_spinner $?
		fi

	stop_time "elapsed time"
	echo -ne "\n\n"; exit 2

}

dependencies