# How to make a USB stick for the automated system

Creating 2 USB partitions for clonezilla USB stick

- IMPORTANT : as EFI SHELL only recognize the fist partition in FAT 16/32 , CLONEZILLA partition must be /dev/sdX1, otherwise HSW/BXT will not boot to clonezilla
- Purpose : create a isolated partition in the usb to keep custom folder always up-to-date from bifrost.intel.com

I Recommend that the first partition will be for clonezilla files and the second partition will be for custom folder files, thus the first partition needs to be at least of 1GB

1 - Clean all USB partitions
	Caution : this commmand will delete all USB information

	First to all you must know where your usb is mounted, the lsblk command will help you.

	## Please notice that /dev/sdX is you USB, take this in mind for the next commands

	Do the following commands as root
	-> umount /dev/sdX
	-> dd if=/dev/zero of=/dev/sdX bs=512 count=1


2 - Install Gparted (is needed)

	-> sudo apt-get install gparted -y

3 - Open Gparted as sudo

	-> sudo gparted /dev/sdX &

	Note : be sure that Gparted is in /dev/sdX in the Gparted's right top

4 - In Gparted select the following options to create a new partition table

	Device > Create partition table

	4.1 - In the box select new partition table type : msdos and apply

5 - Select the following option to create the first partition

	Partition > New

	In "Free space preceding (MiB)" type the space in MB that you'll let for the second partition

	In "New size (MiB)" type the space in MB for the first partition

	Create as : Primary Partition
	File system : fat32 (windows compartible)
	Label : CLONEZILLA (case sensitive)

	and when you're ready click on "Add" buttom

6 - Select the "unallocated" gray bar and > Partition > New

	Create as : Primary Partition
	File system : ext4
	Label : scripts (case sensitive)

	and when you're ready click on "Add" buttom

7 - When all is done > Edit > Apply all operations

8 - Edit flags for the primary partition

	Select the partition which contains the fat 32 file system created in step 5 (this partition must be CLONEZILLA)

	Partition > Manage Flags

	and select the following flags : boot, lba


9 - Download clonezilla zip files from either of the following repositories :

	-> http://clonezilla.org/downloads.php

	select stable 2.4.7-8

		or

	-> wget http://linuxgraphics.intel.com/isos/clonezilla/clonezilla.tar.gz (preferred option)

	and extract the files

	9.1 - Copy the files from clonezilla to the partition in step 5 (CLONEZILLA partition)

		a recomendation here, after copying the files please wait for at less 1 minute before to proceed to the next step.


10 - Please select the most convenient step

	10.1 - if the USB will be destined to the automated system :

		run the following command : ./syncronize.sh -j

	10.2 - if the USB will be destined only for download/upload images from the server :

		run the following command : ./syncronize.sh -n


## Optional step

The following step only is required by the automated system (if any)

11 - To generate ramdom UUID to each USB use :

		11.1 - sudo tune2fs /dev/{device} -U random (in fat partitions does not works)
		11.2 - or you can do it trought gparted



## That's it

## Questions :
- humberto.i.perez.rodriguez@intel.com
