#!/bin/bash

#==============================================================================#
#        GLOBAL COLORS                                                         #
#==============================================================================#
export nc="\e[0m"
export underline="\e[4m"
export bold="\e[1m"
export green="\e[1;32m"
export red="\e[1;31m"
export yellow="\e[1;33m"
export blue="\e[1;34m"
export cyan="\e[1;36m"

#==============================================================================#
#        GLOBAL VARIABLES                                                      #
#==============================================================================#

# The local work directory
WORKDIR="/root/custom"

# Config filepaths
CONFIG_FILE="${WORKDIR}/config.cfg"
ENV_FILE="${WORKDIR}/env.vars"

#==============================================================================#
#        INITIALIZATION                                                        #
#==============================================================================#

# Source config files for default values
source ${CONFIG_FILE}
source ${ENV_FILE}

# Check if system setup is ready
if [ "$SYSTEM_READY" != "1" ]
then
	echo -e " ${red}System not ready to run default package!${nc}"
	exit 1
fi

#==============================================================================#
#        RUN PACKAGE                                                           #
#==============================================================================#

if [ ! -z "$default_package" ]
then
	if [ -d "${PACKAGES_DIR}" ] && [ -f "${PACKAGES_DIR}/${default_package}/run.sh" ]
	then
		bash "${PACKAGES_DIR}/${default_package}/run.sh"
		exit $?
	else
		echo -e " Package ${cyan}'${default_package}'${nc} ${red}cannot be run!${nc}"
		exit 1
	fi
fi

exit 0
