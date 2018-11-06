#/bin/bash

# About GuC
# GuC is a feature that is designed to perform graphics workload scheduling on the various graphics
# parallels engines. In this scheduling model, host software submits work through one of the 256
# graphics doorbells and this invokes the scheduling operation on the appropriate graphics engine.
# Scheduling operations include determining which workload to run next, submitting a workload to a
# a command streamer, pre-empting existing workloads running on an engine, monitoring progress and
# notifying host SW when work is done.

# this script apply for bxt_guc / bxt_dmc / bxt_huc / kbl_dmc / kbl_guc / skl_guc / skl_huc / skl-dmc

##############################################################
# Loading scripts                                            #
##############################################################
source /root/custom/packages/all/functions.sh
source /root/custom/config.cfg
export _DATA=`cat /root/custom/DATA`

export KERNEL=`ls /boot/ | grep "initrd.img" | grep "${kernel_commit}.$" | sed 's/initrd.img-//g'`

#FIRMWARE=guc
FIRMWARE=`ls | grep .bin | awk -F"_" '{print $2}'`

# The $KERNEL_FIRMWARE_DIR varies on different distribution. On Linux it is typically /lib/firmware. While on Android, it could be /etc/firmware.
KERNEL_FIRMWARE_DIR="/lib/firmware"

#PRODUCT_CODE=bxt
PRODUCT_CODE=`ls | grep .bin | awk -F"_" '{print $1}'`
#API_VER=ver5
API_VER=`ls | grep .bin | awk -F"_" '{print $3}'`
#RELEASE_VER=1
RELEASE_VER=`ls | grep .bin | awk -F"_" '{print $4}' | sed 's/.bin//g'`
# BUILD_VER=1398
BUILD_VER=`ls | grep .bin | awk -F"_" '{print $5}' | sed 's/.bin//g'`

mkdir -p ${KERNEL_FIRMWARE_DIR}/i915
if [ -z "${BUILD_VER}" ]; then
	cp  ${PRODUCT_CODE}_${FIRMWARE}_${API_VER}_${RELEASE_VER}.bin $KERNEL_FIRMWARE_DIR/i915
else
	cp  ${PRODUCT_CODE}_${FIRMWARE}_${API_VER}_${RELEASE_VER}_${BUILD_VER}.bin $KERNEL_FIRMWARE_DIR/i915
fi

if [ -z "${BUILD_VER}" ]; then
	if [ ! -f "$KERNEL_FIRMWARE_DIR/i915/${PRODUCT_CODE}_${FIRMWARE}_${API_VER}_${RELEASE_VER}.bin" ]; then
		timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo "--> ERROR : Could not install ['${FIRMWARE}'] file" >> '${_DATA}'/clonezilla'
	    echo -e "--> ${red}ERROR${nc}: Couldn't install new firmwares file"
	    exit -1
	fi
else
	if [ ! -f "$KERNEL_FIRMWARE_DIR/i915/${PRODUCT_CODE}_${FIRMWARE}_${API_VER}_${RELEASE_VER}_${BUILD_VER}.bin" ]; then
		timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo "--> ERROR : Could not install ['${FIRMWARE}'] file" >> '${_DATA}'/clonezilla'
	    echo -e "--> ${red}ERROR${nc}: Couldn't install new firmwares file"
	    exit -1
	else
		timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo "--> SUCCESS : new firmware installed ['${FIRMWARE}']" >> '${_DATA}'/clonezilla'
	    echo -e "--> ${green}Success${nc}: [${KERNEL_FIRMWARE_DIR}/i915/${PRODUCT_CODE}_${FIRMWARE}_${API_VER}_${RELEASE_VER}_${BUILD_VER}.bin] installed!"
	fi
fi

if [ -z "${BUILD_VER}" ]; then
	ln -sf ${KERNEL_FIRMWARE_DIR}/i915/${PRODUCT_CODE}_${FIRMWARE}_${API_VER}_${RELEASE_VER}.bin $KERNEL_FIRMWARE_DIR/i915/${PRODUCT_CODE}_${FIRMWARE}_${API_VER}.bin

	if [ ! -f $KERNEL_FIRMWARE_DIR/i915/${PRODUCT_CODE}_${FIRMWARE}_${API_VER}.bin ]; then
		timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo "--> ERROR : Link creation failed for ['${FIRMWARE}']" >> '${_DATA}'/clonezilla'
	    echo -e "--> ${red}ERROR${nc}: Link creation failed"
	    exit -1
	else
		timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo "--> Link successfully created for ['${FIRMWARE}']" >> '${_DATA}'/clonezilla'
	    echo -e "--> ${green}Success${nc}: [${KERNEL_FIRMWARE_DIR}/i915/${PRODUCT_CODE}_${FIRMWARE}_${API_VER}_${RELEASE_VER}.bin] installed!"
	fi
fi

timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo "--> Forcing initrd/initramfs update ..." >> '${_DATA}'/clonezilla'
echo "--> Forcing initrd/initramfs update..."

# Update initrd/initramfs
# For distros with Dracut: (Fedora)
DRACUT=`which dracut 2> /dev/null`

# Update initrd/initramfs
# For distros with Initramfs: (Ubuntu)
UPDATEINITRAMFS=`which update-initramfs 2> /dev/null`

if [ $DRACUT ]; then
    INITRD=/boot/"initramfs-$(uname -r).img"
elif [ $UPDATEINITRAMFS ]; then
    #INITRD=/boot/"initrd.img-$(uname -r)"
    INITRD=`ls /boot/ | grep "initrd.img" | grep ${kernel_commit}.$`
else
	timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo "--> FAIL : This script depends on Dracut or Update-iniramfs" >> '${_DATA}'/clonezilla'
    echo -e "--> ${red}FAIL${nc}: No such file: This script depends on Dracut or Update-iniramfs."
    exit -1
fi

timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo "--> Trying to backup ['${KERNEL}']" >> '${_DATA}'/clonezilla'
echo "--> Trying to backup [${KERNEL}]"
cd /boot/
rm -rf $INITRD.i915-fw.backup
cp $INITRD $INITRD.i915-fw.backup
if [ $? -eq 0 ]; then
	timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo "DONE" >> '${_DATA}'/clonezilla'
    echo "--> Created a backup of your current initramfs [${INITRD}.i915-fw.backup]"
else
	timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo "WARNING : Could not create a backup of your current initramfs" >> '${_DATA}'/clonezilla'
    echo -e "--> ${yellow}WARNING${nc}: Could not create a backup of your current initramfs"
fi

timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo "--> Trying to update ['${KERNEL}']" >> '${_DATA}'/clonezilla'
echo "--> Trying to update [${KERNEL}]"
if [ $DRACUT ]; then
    dracut $INITRD $(uname -r) --force
else
    update-initramfs -k ${KERNEL} -u 2> /dev/null
    result=$?
fi

if [ "${result}" = "0" ]; then
	timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo "DONE" >> '${_DATA}'/clonezilla'
	echo -e "--> ${green}Success${nc}: the kernel [$KERNEL] was updated!"
else
	timeout 2 ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=1 -q ${server_user}@${server_hostname} 'echo "FAIL : the kernel was not updated" >> '${_DATA}'/clonezilla'
	echo -e "--> ${red}FAIL${nc}: the kernel [$KERNEL] was not updated!"
fi
