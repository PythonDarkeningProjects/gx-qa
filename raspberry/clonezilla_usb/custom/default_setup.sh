#!/bin/bash

export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`


##############################################################
# Load functions                                             #
##############################################################
source ${_THISPATH}/packages/all/functions.sh
# source /root/custom/config.cfg

#==============================================================================#
#        GLOBAL VARIABLES                                                      #
#==============================================================================#

# The local work directory
WORKDIR="/root/custom"

# Various dirpaths and filepaths
PACKAGES_DIR="${WORKDIR}/packages"
TOOLS_DIR="${WORKDIR}/tools"
CONFIG_FILE="${WORKDIR}/config.cfg"
ENV_FILE="${WORKDIR}/env.vars"
NETMASK="255.255.255.0"

# The local mount directories
PARTIMAG="/home/partimag"
SHARED="/home/shared"

# The default params to use with SSH
SSH_PARAMS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=quiet"

#==============================================================================#
#        CHANGING language SETTINS TO US                                       #
#==============================================================================#
export _INIT_BANNER="/root/custom/packages/banners/banner.sh initialization"
${_INIT_BANNER}

start_spinner "${blue}>>> (info)${nc} ${yellow}Changing language settings to US${nc} ..."
    sleep .5; loadkeys us
stop_spinner $?

#==============================================================================#
#        INITIALIZATION                                                        #
#==============================================================================#
# Source config file for default values
sed -i '1i\#!/bin/bash' ${CONFIG_FILE} # this as workaround to avoid  : cannot execute binary file due to several updates from bifrost
source ${CONFIG_FILE}


# Create an env file to store values
echo "WORKDIR=${WORKDIR}" > ${ENV_FILE}
echo "PACKAGES_DIR=${PACKAGES_DIR}" >> ${ENV_FILE}
echo "TOOLS_DIR=${TOOLS_DIR}" >> ${ENV_FILE}

#==============================================================================#
#        SSH CONFIGURATION                                                     #
#==============================================================================#

start_spinner "${blue}>>> (info)${nc} ${yellow}Copying SSH files${nc} ..."
    sleep .5
    cp -R ${WORKDIR}/ssh /root/.ssh
    chmod -R 600 /root/.ssh
    chmod 644 /root/.ssh/*
    chmod 600 /root/.ssh/id_rsa
stop_spinner $?

#==============================================================================#
#        LOCAL HOSTNAME                                                        #
#==============================================================================#

if [ ! -z "$custom_hostname" ]
then
    start_spinner "${blue}>>> (info)${nc} ${yellow}Updating usb stick hostname${nc} ..."
        sleep .75
        echo "$custom_hostname" > "/etc/hostname"
        sed -i "s/debian/$custom_hostname/g" "/etc/hosts"
    stop_spinner $?

    start_spinner "${blue}>>> (info)${nc} ${yellow}Reloading the network${nc} ..."
        sleep .75
        /etc/init.d/networking reload &> /dev/null
    stop_spinner $?

fi

#==============================================================================#
#        NETWORK INTERFACE                                                     #
#==============================================================================#

start_spinner "${blue}>>> (info)${nc} ${yellow}Mounting network interface${nc} ..."
if [ -z "$network_interface" ]
then
    interfaces=$(ip link show | grep -E "^[0-9]: " | awk -F ": " '{print $2}' | grep -v "lo")
    dhclient -v $interfaces &> /dev/null
    stop_spinner $?
else
    dhclient -v $network_interface &> /dev/null
    stop_spinner $?
fi

echo -ne "${blue}>>> (info)${nc} ${yellow}Trying to setup a IP address by DHCP${nc} \n"
ip=`hostname -I | sed 's/ //g'`

if [ ! -z "$ip" ]
then
    isSedline=`echo "$ip" | awk -F"." '{print $1}'`
    if [[ "${isSedline}" -eq "192" ]]; then
        _VLAN=`echo ${ip} | awk -F"." '{print $3}'`
        _BROADCAST="10.219.${_VLAN}.255"
        start_spinner "${blue}>>> (info)${nc} ${yellow}Setting a static ip instead of DHCP${nc} ..."
            sleep .75
            ifconfig ${interfaces} ${dut_static_ip} netmask ${NETMASK} broadcast ${_BROADCAST} up
            # after configure manually the network with the previous command, the hostname needs to be configurated again
            echo "$custom_hostname" > "/etc/hostname"
            sed -i "s/debian/$custom_hostname/g" "/etc/hosts"
            /etc/init.d/networking reload &> /dev/null
        stop_spinner $?

        start_spinner "${blue}>>> (info)${nc} ${yellow}Reloading the network${nc} ..."
            sleep .75
            /etc/init.d/networking reload &> /dev/null
        stop_spinner $?

        sleep 2
        ip=`hostname -I | sed 's/ //g'`
        echo -e "${blue}>>> (info)${nc} (Target now available on ${blue}${ip}${nc})"
        echo "IP_ADDRESS=${ip}" >> ${ENV_FILE}
    elif [[ "${isSedline}" -eq "10" ]]; then
        echo -e "${blue}>>> (info)${nc} the IP was taken by DHCP"
        echo -e "${blue}>>> (info)${nc} (Target now available on ${blue}${ip}${nc})"
        echo "IP_ADDRESS=${ip}" >> ${ENV_FILE}
    else
        echo -e ">>> ${red}(err) ${nc} the ip (${blue}${ip}${nc}) is out of range"
        echo -e ">>> ${blue}(info) ${nc} please report this issue to : "
        echo -e ">>> ${blue}(info) ${nc} humberto.i.perez.rodriguez@intel.com"
        exit 1
    fi

else
    echo -e "(${red}Unable to initialize network interface!${nc})"
    echo -e ">>> ${blue}(info) ${nc} please report this issue to : "
    echo -e ">>> ${blue}(info) ${nc} humberto.i.perez.rodriguez@intel.com"
    echo "IP_ADDRESS=False" >> ${ENV_FILE}
    exit 1
fi

#==============================================================================#
#        PARTIMAG DIR                                                          #
#==============================================================================#

if [ ! -z "$server_partimag" ] && [ ! -z "$server_hostname" ] && [ ! -z "$server_user" ]
then
    start_spinner "${blue}>>> (info)${nc} ${yellow}Mounting /home/partimag from (asgard.intel.com)${nc} ..."
        mkdir -p ${PARTIMAG}
        sshfs ${SSH_PARAMS} -o noatime "${server_user}@10.219.106.16:${server_partimag}" ${PARTIMAG}
    stop_spinner $?
    echo "PARTIMAG=${PARTIMAG}" >> ${ENV_FILE}
fi

#==============================================================================#
#        SHARED DIR                                                            #
#==============================================================================#

if [ ! -z "$server_shared" ] && [ ! -z "$server_hostname" ] && [ ! -z "$server_user" ]
then
    start_spinner "${blue}>>> (info)${nc} ${yellow}Mounting /home/shared from (${server_hostname})${nc} ..."
        mkdir -p ${SHARED}
        sshfs ${SSH_PARAMS} -o noatime "${server_user}@${server_hostname}:${server_shared}" ${SHARED}
    stop_spinner $?
    echo "SHARED=${SHARED}" >> ${ENV_FILE}
fi

start_spinner "${blue}>>> (info)${nc} ${yellow}Enabling ssh${nc} ..."
    sleep .5
    #mount devpts /dev/pts -t devpts # to get access trhought ssh (this is neccesary sometimes)
    service ssh start
stop_spinner $?
#==============================================================================#
#        FINALIZATION                                                          #
#==============================================================================#

echo "SYSTEM_READY=1" >> ${ENV_FILE}
echo -e " ============================"
echo -e " ========== ${cyan}FINISH${nc} =========="
echo -ne " ============================ \n\n"

#==============================================================================#
#        SHOWING USEFUL INFORMATION                                            #
#==============================================================================#

# looking for the usb
whereisUSB=`lsblk -S | grep usb | awk '{print $1}'`
# getting the disk/eMMC attached to the DUT
lsblk -d | grep -ve ${whereisUSB} -ve "filesystem.squashfs" -ve M > attachedDisk
# selecting mayor disk capacity to clone
howManyDisk=`cat attachedDisk | wc -l`

# here i guess that the maximum disk in the DUT will be 2 in the worst case
if [ ${howManyDisk} -eq 1 ];then
    echo -e "${blue}>>> (info)${nc} 1 disk was found in the DUT"
    export disk_label=`cat attachedDisk | head -1 | awk '{print $1}'`

elif [ ${howManyDisk} -eq 2 ];then
    echo -e "${blue}>>> (info)${nc} 2 disk was found in the DUT"
    echo -e "${blue}>>> (info)${nc} Selecting the highest capacity disk ..."
    disk_A=`cat attachedDisk | head -1 | awk '{print $1}'`
    disk_B=`cat attachedDisk | tail -1 | awk '{print $1}'`
    disk_A_capacity=`lsblk -b --output SIZE -n -d /dev/${disk_A}`
    disk_B_capacity=`lsblk -b --output SIZE -n -d /dev/${disk_B}`

    if [ ${disk_A_capacity} -gt ${disk_B_capacity} ]; then
        echo -e "${blue}>>> (info)${nc} dev/${disk_A} was selected"
        export disk_label=${disk_A}
    elif [ ${disk_B_capacity} -gt ${disk_A_capacity} ]; then
        echo -e "${blue}>>> (info)${nc} dev/${disk_B} was selected"
        export disk_label=${disk_B}
    fi

elif [ ${howManyDisk} -eq 0 ];then
    echo -ne "\n\n"
    cat ${thispath}/asciiImages/homero
    echo -ne "${red}>>> (err)${nc} no disks were found in the DUT \n\n\n"
    exit 1
fi


#disk_label=`lsblk | grep sda | head -1 | awk '{print $1}'`
disk_size=`lsblk | grep -w ${disk_label} | head -1 | awk '{print $4}'`


echo -e "${blue}>>> (info)${nc} ${bold}Disk was mounted on${nc} : (${cyan}${disk_label}${nc})"
echo -e "${blue}>>> (info)${nc} ${bold}Disk size${nc}           : (${cyan}${disk_size}${nc})"

sleep 7
exit 0
