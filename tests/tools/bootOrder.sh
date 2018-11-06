#!/bin/bash


#=========================================
# Source config                          =
#=========================================
source /home/custom/config.cfg

if [ ! -f "/home/${dut_user}/.bo_compiled" ]; then

    #=========================================
    # Local variables                        =
    #=========================================
    export ModuleFolder="/home/shared/tools/BIOSConf_Release_6.1"

    if [ -d "${ModuleFolder}" ]; then rm -rf ${ModuleFolder} &> /dev/null; fi

    function checkOutput () {
        unset status
        output="$1"
        action="$2"
        
        if [ "${output}" != "0" ]; then
            echo " FAIL"; status="1"; echo "${status}" > /home/${dut_user}/.status
        elif [ "${output}" = "0" ]; then
            echo " DONE"; status="0"; echo "${status}" > /home/${dut_user}/.status
        fi

        if [ "${status}" = "1" -a "${action}" = "kill" ]; then
            echo -e "--> leaving the script secondary ..."
            exit 0
        fi

        unset action
    }

    echo -n "--> Copying kernel module to DUT : [${dut_hostname}] ..." 
        scp -q -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -r "${server_user}"@"${server_hostname}":"${ModuleFolder}" /home/${dut_user} 2> /dev/null; sshOutput=$?; wait # scp does not allow (/) in the variables
        checkOutput "${sshOutput}" "kill"

    # We have to compile the smi module in each platform, otherwise the SMI would not be recognize the current kernel
    echo -n "--> Compiling smi module ..."
        cd /home/${dut_user}/BIOSConf_Release_6.1/SMIDriver/Linux64/Release && make; wait

    touch /home/${dut_user}/.bo_compiled

fi