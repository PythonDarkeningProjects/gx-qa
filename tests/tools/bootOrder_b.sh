#!/bin/bash


#=========================================
# Source config                          =
#=========================================
source /home/custom/config.cfg

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


if (lsmod | grep smi &> /dev/null); then
    echo -e "--> smi module is already in the kernel"
else
    echo -n "--> Starting smidrv ... "
        SMIPath="/home/${dut_user}/BIOSConf_Release_6.1/SMIDriver/Linux64/Release"
        cd ${SMIPath} && chmod +x smidrv && sudo ./smidrv start
        checkOutput $? "kill"
fi


echo -n "--> Getting bios boot order ..."
    BIOSexecutablePath="/home/${dut_user}/BIOSConf_Release_6.1/Linux64/Release"
    cd ${BIOSexecutablePath} && chmod +x BIOSConf && sudo ./BIOSConf bootorder get 2> /dev/null | grep ^[0:9] > bootOrder
    checkOutput $? "kill"

cd /home/${dut_user}/BIOSConf_Release_6.1/Linux64/Release

BootFile="/home/${dut_user}/BIOSConf_Release_6.1/Linux64/Release/bootOrder"
UsbNumber=`grep "EFI USB Device" ${BootFile} | awk '{print $1}'`

if [ -z "${UsbNumber}" ]; then
    echo "--> the USB is not connected to the DUT"
    echo " FAIL"; status="1"; echo "${status}" > /home/${dut_user}/.status
    echo -e "--> leaving the script secondary ..."
    exit 0

else

    List=`cat ${BootFile} | awk '{print $1}'`

    for element in ${List}; do
        if [ "${element}" = "${UsbNumber}" ]; then
            continue
        else
            list="$list-$element"
        fi
    done

    echo "${UsbNumber}${list}"

    echo -n "--> Setting boot order ..."
        sudo ./BIOSConf bootorder set ${UsbNumber}${list} &> /dev/null
        checkOutput $? "kill"
fi