#!/bin/bash

	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>
	export CUSER=$(whoami)
	export PASSWORD=linux
	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>


function download_kernel {


	checkTTY=$(tty | awk -F"/dev/" '{print $2}')
	if [ ! -z "$SSH_CLIENT" ] || [ ! -z "$SSH_TTY" ] || [[ "$checkTTY" = "tty1"  || "$checkTTY" = "tty2" || "$checkTTY" = "tty3" || "$checkTTY" = "tty4" || "$checkTTY" = "tty5" || "$checkTTY" = "tty6" ]]; then
		# SSH mode
		pause(){
			local m="$@"
			echo "$m"
		}	


		while :
		do
			clear; echo -ne "\n\n"
			echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
			echo -ne " Select a kernel \n\n"
			echo -ne " 1) drm-intel-nightly \n"
			echo -ne " 2) drm-intel-testing \n"
			echo -ne " 3) mainline \n\n"
			read -p " Your choice : " choose
			echo -ne "\n\n"

			case $choose in

				1)
					start_spinner "++ Generating kernel list"
						# Downloading the list of kernels
						w3m vanaheimr.tl.intel.com/shared/out/kernels/drm-intel-nightly/ > /tmp/drm-intel-nightly_list; wait
						# Cleaning the list
						sed -i '/^\s*$/d' /tmp/drm-intel-nightly_list # empty lines
						cat /tmp/drm-intel-nightly_list | grep -w "DIR" | grep -ve "debug" -ve "latest" | awk '{print $2}' | sed 's|/||g' > /tmp/1
						rm /tmp/drm-intel-nightly_list &> /dev/null; mv /tmp/1 /tmp/drm-intel-nightly_list
						cat -n /tmp/drm-intel-nightly_list > /tmp/1; rm /tmp/drm-intel-nightly_list; mv /tmp/1 /tmp/drm-intel-nightly_list

						while read line
						do
	    					numbers=$(echo $line | awk '{print $1}')
    						list+=("$numbers")
						done < /tmp/drm-intel-nightly_list

					stop_spinner $?

					pause(){
						local m="$@"
						echo "$m"
					}	

					while :
					do
						clear; echo -ne "\n\n"
						echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
						echo -ne " Select a kernel \n\n"
						cat /tmp/drm-intel-nightly_list
						echo -ne "\n\n"
						read -p " Your choice : " choose
						echo -ne "\n\n"

						check=$(echo ${list[@]} | grep -w "$choose")

						if [ -z "$check" ]; then
							pause

						else
							pickakernel=$(cat /tmp/drm-intel-nightly_list | grep -w "$choose" | awk '{print $2}')

							mkdir -p /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/ && cd /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/
							start_spinner "++ Downloading the kernel $pickakernel"			
								wget vanaheimr.tl.intel.com/shared/out/kernels/drm-intel-nightly/$pickakernel/commit.txt &> /dev/null; wait
								wget vanaheimr.tl.intel.com/shared/out/kernels/drm-intel-nightly/$pickakernel/info.txt &> /dev/null; wait
								wget -A '.deb' -np -nd -m -E -k -K -e robots=off -l 1 vanaheimr.tl.intel.com/shared/out/kernels/drm-intel-nightly/$pickakernel/deb/ &> /dev/null; wait
							stop_spinner $? | tee /tmp/.log

							check=$(cat /tmp/.log | grep "FAIL")

							if [ -z "$check" ]; then

								start_spinner "++ Installing the kernel $pickakernel"
									cd /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/
									echo $PASSWORD | sudo -S ls -l /tmp &> /dev/null; sleep 5
									echo $PASSWORD | sudo -S dpkg -i *.deb &> /dev/null
									wait
								stop_spinner $?

								check_kernel=$(cat /etc/default/grub |grep -w "Advanced options for Ubuntu>Ubuntu, with Linux")

								if [ ! -z "$check_kernel" ]; then

									start_spinner "++ Adding [$pickakernel] to grub  ... "
										kerneln=$(ls /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel | grep -w "firmware-image" | awk -F"firmware-image-" '{print $2}' | awk -F"_" '{print $1}')
										echo $PASSWORD | sudo -S sed -i '6s/^.*$/GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux '"$kerneln"'"/g' /etc/default/grub 
										sleep 4
									stop_spinner $?
								fi 	

								# Adding info to commit.txt
								kernel_version=$(cat /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/info.txt | grep -w "kernel_version" | awk -F"kernel_version=" '{print $2}')
								git_url=$(cat /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/info.txt | grep -w "git_url" | awk -F"git_url=" '{print $2}')
								git_branch=$(cat /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/info.txt | grep -w "git_branch" | awk -F"git_branch=" '{print $2}')
								git_describe=$(cat /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/info.txt | grep -w "git_describe" | awk -F"git_describe=" '{print $2}')
								echo -ne "\n\n" >> /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/commit.txt
								echo "kernel version : $kernel_version" >> /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/commit.txt
								echo "git url        : $git_url" >> /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/commit.txt
								echo "git branch     : $git_branch" >> /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/commit.txt
								echo "git describe   : $git_describe" >> /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/commit.txt
								mv /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/commit.txt /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/commit &> /dev/null
								rm /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/info.txt &> /dev/null
											
								# Showing the outstanding information
								echo -ne "\n\n"
								echo -ne " ++ Commit information \n\n"
								cat /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/commit
								echo -ne "\n\n"
								echo -ne " ++ Do you want to reboot now in order to use the kernel \n"
								echo -ne " ++ $pickakernel \n\n"
								echo -ne " 1) Restart now \n"
								echo -ne " 2) Restart later \n\n"
								read -p " Your choice : " choose

									case $choose in

										1) echo $PASSWORD | sudo -S ls -l /tmp &> /dev/null; sleep 5; echo $PASSWORD | sudo -S reboot ; exit 1 ;;

										2) echo -ne "\n\n"; exit 1 ;;

										*) echo -ne "\n\n"; exit 1 ;;

									esac

							else
								echo -ne "\n\n"
								echo -ne " ++ `tput bold``tput setf 4`an error has occurred when downloading the kernel`tput sgr0` \n"
								echo -ne " ++ `tput bold``tput setf 4`check is the server : vanaheimr.tl.intel.com`tput sgr0` \n"
								echo -ne " ++ `tput bold``tput setf 4`is online`tput sgr0` \n\n\n"
								exit 1


							fi


						fi


					done

				;;



				2)
					start_spinner "++ Generating kernel list"
						# Downloading the list of kernels
						w3m vanaheimr.tl.intel.com/shared/out/kernels/drm-intel-testing/ > /tmp/drm-intel-testing_list; wait
						# Cleaning the list
						sed -i '/^\s*$/d' /tmp/drm-intel-testing_list # empty lines
						cat /tmp/drm-intel-testing_list | grep -w "DIR" | grep -ve "debug" -ve "latest" -ve "platforms" | awk '{print $2}' | sed 's|/||g' > /tmp/1
						rm /tmp/drm-intel-testing_list &> /dev/null; mv /tmp/1 /tmp/drm-intel-testing_list
						cat -n /tmp/drm-intel-testing_list > /tmp/1; rm /tmp/drm-intel-testing_list; mv /tmp/1 /tmp/drm-intel-testing_list

						while read line
						do
    						numbers=$(echo $line | awk '{print $1}')
    						list+=("$numbers")
						done < /tmp/drm-intel-testing_list

					stop_spinner $?

					pause(){
						local m="$@"
						echo "$m"
					}	

					while :
					do
						clear; echo -ne "\n\n"
						echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
						echo -ne " Select a kernel \n\n"
						cat /tmp/drm-intel-testing_list
						echo -ne "\n\n"
						read -p " Your choice : " choose
						echo -ne "\n\n"

						check=$(echo ${list[@]} | grep -w "$choose")

						if [ -z "$check" ]; then
							pause

						else
							pickakernel=$(cat /tmp/drm-intel-testing_list | grep -w "$choose" | awk '{print $2}')

							mkdir -p /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/ && cd /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/
							start_spinner "++ Downloading the kernel $pickakernel"			
								wget vanaheimr.tl.intel.com/shared/out/kernels/drm-intel-testing/$pickakernel/commit.txt &> /dev/null; wait
								wget vanaheimr.tl.intel.com/shared/out/kernels/drm-intel-testing/$pickakernel/info.txt &> /dev/null; wait
								wget -A '.deb' -np -nd -m -E -k -K -e robots=off -l 1 vanaheimr.tl.intel.com/shared/out/kernels/drm-intel-testing/$pickakernel/deb/ &> /dev/null; wait
							stop_spinner $? | tee /tmp/.log

							check=$(cat /tmp/.log | grep "FAIL")

							if [ -z "$check" ]; then

								start_spinner "++ Installing the kernel $pickakernel"
									cd /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/
									echo $PASSWORD | sudo -S ls -l /tmp &> /dev/null; sleep 5
									echo $PASSWORD | sudo -S dpkg -i *.deb &> /dev/null
									wait
								stop_spinner $?

								check_kernel=$(cat /etc/default/grub |grep -w "Advanced options for Ubuntu>Ubuntu, with Linux")

								if [ ! -z "$check_kernel" ]; then

									start_spinner "++ Adding [$pickakernel] to grub  ... "
										kerneln=$(ls /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel | grep -w "firmware-image" | awk -F"firmware-image-" '{print $2}' | awk -F"_" '{print $1}')
										echo $PASSWORD | sudo -S sed -i '6s/^.*$/GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux '"$kerneln"'"/g' /etc/default/grub 
										sleep 4
									stop_spinner $?
								fi 	

								# Adding info to commit.txt
								kernel_version=$(cat /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/info.txt | grep -w "kernel_version" | awk -F"kernel_version=" '{print $2}')
								git_url=$(cat /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/info.txt | grep -w "git_url" | awk -F"git_url=" '{print $2}')
								git_branch=$(cat /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/info.txt | grep -w "git_branch" | awk -F"git_branch=" '{print $2}')
								git_describe=$(cat /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/info.txt | grep -w "git_describe" | awk -F"git_describe=" '{print $2}')
								echo -ne "\n\n" >> /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/commit.txt
								echo "kernel version : $kernel_version" >> /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/commit.txt
								echo "git url        : $git_url" >> /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/commit.txt
								echo "git branch     : $git_branch" >> /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/commit.txt
								echo "git describe   : $git_describe" >> /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/commit.txt
								mv /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/commit.txt /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/commit &> /dev/null
								rm /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/info.txt &> /dev/null
											
								# Showing the outstanding information
								echo -ne "\n\n"
								echo -ne " ++ Commit information \n\n"
								cat /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/commit
								echo -ne "\n\n"
								echo -ne " ++ Do you want to reboot now in order to use the kernel \n"
								echo -ne " ++ $pickakernel \n\n"
								echo -ne " 1) Restart now \n"
								echo -ne " 2) Restart later \n\n"
								read -p " Your choice : " choose

									case $choose in

										1) echo $PASSWORD | sudo -S ls -l /tmp &> /dev/null; sleep 5; echo $PASSWORD | sudo -S reboot ; exit 1 ;;

										2) echo -ne "\n\n"; exit 1 ;;

										*) echo -ne "\n\n"; exit 1 ;;

									esac

							else
								echo -ne "\n\n"
								echo -ne " ++ `tput bold``tput setf 4`an error has occurred when downloading the kernel`tput sgr0` \n"
								echo -ne " ++ `tput bold``tput setf 4`check is the server : vanaheimr.tl.intel.com`tput sgr0` \n"
								echo -ne " ++ `tput bold``tput setf 4`is online`tput sgr0` \n\n\n"
								exit 1


							fi


						fi


					done


				;;



				3)
					start_spinner "++ Generating kernel list"
						# Downloading the list of kernels
						w3m vanaheimr.tl.intel.com/shared/out/kernels/mainline/ > /tmp/mainline_list; wait
						# Cleaning the list
						sed -i '/^\s*$/d' /tmp/mainline_list # empty lines
						cat /tmp/mainline_list | grep -w "DIR" | grep -ve "BAT" -ve "debug" -ve "latest" -ve "platforms" | awk '{print $2}' | sed 's|/||g' > /tmp/1
						rm /tmp/mainline_list &> /dev/null; mv /tmp/1 /tmp/mainline_list
						cat -n /tmp/mainline_list > /tmp/1; rm /tmp/mainline_list; mv /tmp/1 /tmp/mainline_list

						while read line
						do
    						numbers=$(echo $line | awk '{print $1}')
    						list+=("$numbers")
						done < /tmp/mainline_list

					stop_spinner $?

					pause(){
						local m="$@"
						echo "$m"
					}	

					while :
					do
						clear; echo -ne "\n\n"
						echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
						echo -ne " Select a kernel \n\n"
						cat /tmp/mainline_list
						echo -ne "\n\n"
						read -p " Your choice : " choose
						echo -ne "\n\n"
						check=$(echo ${list[@]} | grep -w "$choose")

						if [ -z "$check" ]; then
							pause

						else
							pickakernel=$(cat /tmp/mainline_list | grep -w "$choose" | awk '{print $2}')

							mkdir -p /home/$CUSER/Downloads/kernels/mainline/$pickakernel/ && cd /home/$CUSER/Downloads/kernels/mainline/$pickakernel/
							start_spinner "++ Downloading the kernel $pickakernel"			
								wget vanaheimr.tl.intel.com/shared/out/kernels/mainline/$pickakernel/commit.txt &> /dev/null; wait
								wget vanaheimr.tl.intel.com/shared/out/kernels/mainline/$pickakernel/info.txt &> /dev/null; wait
								wget -A '.deb' -np -nd -m -E -k -K -e robots=off -l 1 vanaheimr.tl.intel.com/shared/out/kernels/mainline/$pickakernel/deb/ &> /dev/null; wait
							stop_spinner $? | tee /tmp/.log

							check=$(cat /tmp/.log | grep "FAIL")

							if [ -z "$check" ]; then

								start_spinner "++ Installing the kernel $pickakernel"
									cd /home/$CUSER/Downloads/kernels/mainline/$pickakernel/
									echo $PASSWORD | sudo -S ls -l /tmp &> /dev/null; sleep 5
									echo $PASSWORD | sudo -S dpkg -i *.deb &> /dev/null
									wait
								stop_spinner $?

								check_kernel=$(cat /etc/default/grub |grep -w "Advanced options for Ubuntu>Ubuntu, with Linux")

								if [ ! -z "$check_kernel" ]; then

									start_spinner "++ Adding [$pickakernel] to grub  ... "
										kerneln=$(ls /home/$CUSER/Downloads/kernels/mainline/$pickakernel | grep -w "firmware-image" | awk -F"firmware-image-" '{print $2}' | awk -F"_" '{print $1}')
										echo $PASSWORD | sudo -S sed -i '6s/^.*$/GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux '"$kerneln"'"/g' /etc/default/grub 
										sleep 4
									stop_spinner $?
								fi 	

								# Adding info to commit.txt
								kernel_version=$(cat /home/$CUSER/Downloads/kernels/mainline/$pickakernel/info.txt | grep -w "kernel_version" | awk -F"kernel_version=" '{print $2}')
								git_url=$(cat /home/$CUSER/Downloads/kernels/mainline/$pickakernel/info.txt | grep -w "git_url" | awk -F"git_url=" '{print $2}')
								git_branch=$(cat /home/$CUSER/Downloads/kernels/mainline/$pickakernel/info.txt | grep -w "git_branch" | awk -F"git_branch=" '{print $2}')
								git_describe=$(cat /home/$CUSER/Downloads/kernels/mainline/$pickakernel/info.txt | grep -w "git_describe" | awk -F"git_describe=" '{print $2}')
								echo -ne "\n\n" >> /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit.txt
								echo "kernel version : $kernel_version" >> /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit.txt
								echo "git url        : $git_url" >> /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit.txt
								echo "git branch     : $git_branch" >> /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit.txt
								echo "git describe   : $git_describe" >> /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit.txt
								mv /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit.txt /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit &> /dev/null
								rm /home/$CUSER/Downloads/kernels/mainline/$pickakernel/info.txt &> /dev/null
											
								# Showing the outstanding information
								echo -ne "\n\n"
								echo -ne " ++ Commit information \n\n"
								cat /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit
								echo -ne "\n\n"
								echo -ne " ++ Do you want to reboot now in order to use the kernel \n"
								echo -ne " ++ $pickakernel \n\n"
								echo -ne " 1) Restart now \n"
								echo -ne " 2) Restart later \n\n"
								read -p " Your choice : " choose

									case $choose in

										1) echo $PASSWORD | sudo -S ls -l /tmp &> /dev/null; sleep 5; echo $PASSWORD | sudo -S reboot ; exit 1 ;;

										2) echo -ne "\n\n"; exit 1 ;;

										*) echo -ne "\n\n"; exit 1 ;;

									esac

							else
								echo -ne "\n\n"
								echo -ne " ++ `tput bold``tput setf 4`an error has occurred when downloading the kernel`tput sgr0` \n"
								echo -ne " ++ `tput bold``tput setf 4`check is the server : vanaheimr.tl.intel.com`tput sgr0` \n"
								echo -ne " ++ `tput bold``tput setf 4`is online`tput sgr0` \n\n\n"
								exit 1


							fi


						fi


					done



				;;


				*) pause ;;


			esac	


		done

	else

		# Graphical mode
		pause(){
			local m="$@"
			echo "$m"
		}	

		while :
		do
			xkernelname=$(zenity --list --text "Select a kernel" --title "Intel® Graphics for Linux* | 01.org" --radiolist --column "Pick" --column "List" FALSE "drm-intel-nightly" FALSE "drm-intel-testing" FALSE "mainline" --separator=":" 2> /dev/null)

			if [ -z "$xkernelname" ]; then  
				zenity --question --text "Are you sure ?" --title "Intel® Graphics for Linux* | 01.org" --width=240 2> /dev/null
				if [ $? = 0 ]; then echo -ne "\n\n"; exit 1; else pause; fi

			else

				case $xkernelname in

					drm-intel-nightly) 
	
							pause(){
								local m="$@"
								echo "$m"
							}	

							while :
							do
								(
								# Downloading the list of kernels
								w3m vanaheimr.tl.intel.com/shared/out/kernels/drm-intel-nightly/ > /tmp/drm-intel-nightly_list
								# Cleaning the list
								sed -i '/^\s*$/d' /tmp/drm-intel-nightly_list # empty lines
								cat /tmp/drm-intel-nightly_list | grep -w "DIR" | grep -ve "debug" -ve "latest" | awk '{print $2}' | sed 's|/||g' > /tmp/1
								rm /tmp/drm-intel-nightly_list &> /dev/null; mv /tmp/1 /tmp/drm-intel-nightly_list
								) | zenity --progress --auto-close --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Generating kernel list" --pulsate 2> /dev/null

								unset list
							
								while read line
								do
    								list+=("FALSE")
    								list+=("$line")
								done < /tmp/drm-intel-nightly_list

								pickakernel=$(zenity --list --text "Select a kernel" --title "Intel® Graphics for Linux* | 01.org" --radiolist --column "Pick" --column "List" "${list[@]}" --separator=":" 2> /dev/null)
						
									if [ -z "$pickakernel" ]; then  
										zenity --question --text "Are you sure ?" --title "Intel® Graphics for Linux* | 01.org" --width=240 2> /dev/null
										if [ $? = 0 ]; then echo -ne "\n\n"; exit 1; else pause; fi
									else
										mkdir -p /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/ && cd /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/
										
										(
										wget vanaheimr.tl.intel.com/shared/out/kernels/drm-intel-nightly/$pickakernel/commit.txt &> /dev/null
										wait
										wget vanaheimr.tl.intel.com/shared/out/kernels/drm-intel-nightly/$pickakernel/info.txt &> /dev/null
										wait
										wget -A '.deb' -np -nd -m -E -k -K -e robots=off -l 1 vanaheimr.tl.intel.com/shared/out/kernels/drm-intel-nightly/$pickakernel/deb/ &> /dev/null
										wait
										) | zenity --progress --auto-close --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Downloading the kernel \n $pickakernel" --pulsate 2> /dev/null

										# 0 mean that the kernel was download
										if [ $? = 0 ]; then 
											
											(
											cd /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/
											echo $PASSWORD | sudo -S ls -l /tmp &> /dev/null; sleep 5
											echo $PASSWORD | sudo -S dpkg -i *.deb &> /dev/null
											wait
											) | zenity --progress --auto-close --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Installing the kernel \n $pickakernel" --pulsate 2> /dev/null

											# Adding info to commit.txt
											kernel_version=$(cat /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/info.txt | grep -w "kernel_version" | awk -F"kernel_version=" '{print $2}')
											git_url=$(cat /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/info.txt | grep -w "git_url" | awk -F"git_url=" '{print $2}')
											git_branch=$(cat /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/info.txt | grep -w "git_branch" | awk -F"git_branch=" '{print $2}')
											git_describe=$(cat /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/info.txt | grep -w "git_describe" | awk -F"git_describe=" '{print $2}')
											echo -ne "\n\n" >> /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/commit.txt
											echo "kernel version : $kernel_version" >> /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/commit.txt
											echo "git url        : $git_url" >> /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/commit.txt
											echo "git branch     : $git_branch" >> /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/commit.txt
											echo "git describe   : $git_describe" >> /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/commit.txt
											mv /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/commit.txt /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/commit &> /dev/null
											rm /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/info.txt &> /dev/null
											
											# Showing the outstanding information
											cat /home/$CUSER/Downloads/kernels/drm-intel-nightly/$pickakernel/commit | zenity --text-info --title="Intel® Graphics for Linux* | 01.org" --width=450 --height=300

											zenity --question --title="Intel® Graphics for Linux | 01.org" --text="Do you want to reboot now \n in order to use the kernel \n $pickakernel"	--width=250 2> /dev/null

											if [ $? = 0 ]; then
												echo $PASSWORD | sudo -S reboot
											else
												echo -ne "\n\n"
												exit 1
											fi
										fi
									fi
							done
					;;


					drm-intel-testing) 

							pause(){
								local m="$@"
								echo "$m"
							}	

							while :
							do
								(
								# Downloading the list of kernels
								w3m vanaheimr.tl.intel.com/shared/out/kernels/drm-intel-testing/ > /tmp/drm-intel-testing_list
								# Cleaning the list
								sed -i '/^\s*$/d' /tmp/drm-intel-testing_list # empty lines
								cat /tmp/drm-intel-testing_list | grep -w "DIR" | grep -ve "debug" -ve "latest" -ve "platforms" | awk '{print $2}' | sed 's|/||g' > /tmp/1
								rm /tmp/drm-intel-testing_list &> /dev/null; mv /tmp/1 /tmp/drm-intel-testing_list
								) | zenity --progress --auto-close --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Generating kernel list" --pulsate 2> /dev/null

								unset list
							
								while read line
								do
    								list+=("FALSE")
    								list+=("$line")
								done < /tmp/drm-intel-testing_list

								pickakernel=$(zenity --list --text "Select a kernel" --title "Intel® Graphics for Linux* | 01.org" --radiolist --column "Pick" --column "List" "${list[@]}" --separator=":" 2> /dev/null)
						
									if [ -z "$pickakernel" ]; then  
										zenity --question --text "Are you sure ?" --title "Intel® Graphics for Linux* | 01.org" --width=240 2> /dev/null
										if [ $? = 0 ]; then echo -ne "\n\n"; exit 1; else pause; fi
									else
										mkdir -p /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/ && cd /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/
										
										(
										wget vanaheimr.tl.intel.com/shared/out/kernels/drm-intel-testing/$pickakernel/commit.txt &> /dev/null
										wait
										wget vanaheimr.tl.intel.com/shared/out/kernels/drm-intel-testing/$pickakernel/info.txt &> /dev/null
										wait
										wget -A '.deb' -np -nd -m -E -k -K -e robots=off -l 1 vanaheimr.tl.intel.com/shared/out/kernels/drm-intel-testing/$pickakernel/deb/ &> /dev/null
										wait
										) | zenity --progress --auto-close --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Downloading the kernel \n $pickakernel" --pulsate 2> /dev/null

										# 0 mean that the kernel was download
										if [ $? = 0 ]; then 
											
											(
											cd /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/
											echo $PASSWORD | sudo -S ls -l /tmp &> /dev/null; sleep 5
											echo $PASSWORD | sudo -S dpkg -i *.deb &> /dev/null
											wait
											) | zenity --progress --auto-close --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Installing the kernel \n $pickakernel" --pulsate 2> /dev/null

											# Adding info to commit.txt
											kernel_version=$(cat /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/info.txt | grep -w "kernel_version" | awk -F"kernel_version=" '{print $2}')
											git_url=$(cat /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/info.txt | grep -w "git_url" | awk -F"git_url=" '{print $2}')
											git_branch=$(cat /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/info.txt | grep -w "git_branch" | awk -F"git_branch=" '{print $2}')
											git_describe=$(cat /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/info.txt | grep -w "git_describe" | awk -F"git_describe=" '{print $2}')
											echo -ne "\n\n" >> /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/commit.txt
											echo "kernel version : $kernel_version" >> /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/commit.txt
											echo "git url        : $git_url" >> /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/commit.txt
											echo "git branch     : $git_branch" >> /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/commit.txt
											echo "git describe   : $git_describe" >> /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/commit.txt
											mv /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/commit.txt /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/commit &> /dev/null
											rm /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/info.txt &> /dev/null
											
											# Showing the outstanding information
											cat /home/$CUSER/Downloads/kernels/drm-intel-testing/$pickakernel/commit | zenity --text-info --title="Intel® Graphics for Linux* | 01.org" --width=450 --height=300 2> /dev/null

											zenity --question --title="Intel® Graphics for Linux | 01.org" --text="Do you want to reboot now \n in order to use the kernel \n $pickakernel"	--width=250 2> /dev/null

											if [ $? = 0 ]; then
												echo $PASSWORD | sudo -S reboot
											else
												echo -ne "\n\n"
												exit 1
											fi
										fi
									fi
							done
					;;

				
					mainline) 

							pause(){
								local m="$@"
								echo "$m"
							}	

							while :
							do
								(
								# Downloading the list of kernels
								w3m vanaheimr.tl.intel.com/shared/out/kernels/mainline/ > /tmp/mainline_list
								# Cleaning the list
								sed -i '/^\s*$/d' /tmp/mainline_list # empty lines
								cat /tmp/mainline_list | grep -w "DIR" | grep -ve "BAT" -ve "debug" -ve "latest" -ve "platforms" | awk '{print $2}' | sed 's|/||g' > /tmp/1
								rm /tmp/mainline_list &> /dev/null; mv /tmp/1 /tmp/mainline_list
								) | zenity --progress --auto-close --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Generating kernel list" --pulsate 2> /dev/null

								unset list
							
								while read line
								do
    								list+=("FALSE")
    								list+=("$line")
								done < /tmp/mainline_list

								pickakernel=$(zenity --list --text "Select a kernel" --title "Intel® Graphics for Linux* | 01.org" --radiolist --column "Pick" --column "List" "${list[@]}" --separator=":" 2> /dev/null)
						
									if [ -z "$pickakernel" ]; then  
										zenity --question --text "Are you sure ?" --title "Intel® Graphics for Linux* | 01.org" --width=240 2> /dev/null
										if [ $? = 0 ]; then echo -ne "\n\n"; exit 1; else pause; fi
									else
										mkdir -p /home/$CUSER/Downloads/kernels/mainline/$pickakernel/ && cd /home/$CUSER/Downloads/kernels/mainline/$pickakernel/
										
										(
										wget vanaheimr.tl.intel.com/shared/out/kernels/mainline/$pickakernel/commit.txt &> /dev/null
										wait
										wget vanaheimr.tl.intel.com/shared/out/kernels/mainline/$pickakernel/info.txt &> /dev/null
										wait
										wget -A '.deb' -np -nd -m -E -k -K -e robots=off -l 1 vanaheimr.tl.intel.com/shared/out/kernels/mainline/$pickakernel/deb/ &> /dev/null
										wait
										) | zenity --progress --auto-close --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Downloading the kernel \n $pickakernel" --pulsate 2> /dev/null

										# 0 mean that the kernel was download
										if [ $? = 0 ]; then 
											
											(
											cd /home/$CUSER/Downloads/kernels/mainline/$pickakernel/
											echo $PASSWORD | sudo -S ls -l /tmp &> /dev/null; sleep 5
											echo $PASSWORD | sudo -S dpkg -i *.deb &> /dev/null
											wait
											) | zenity --progress --auto-close --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Installing the kernel \n $pickakernel" --pulsate 2> /dev/null

											# Adding info to commit.txt
											kernel_version=$(cat /home/$CUSER/Downloads/kernels/mainline/$pickakernel/info.txt | grep -w "kernel_version" | awk -F"kernel_version=" '{print $2}')
											git_url=$(cat /home/$CUSER/Downloads/kernels/mainline/$pickakernel/info.txt | grep -w "git_url" | awk -F"git_url=" '{print $2}')
											git_branch=$(cat /home/$CUSER/Downloads/kernels/mainline/$pickakernel/info.txt | grep -w "git_branch" | awk -F"git_branch=" '{print $2}')
											git_tag=$(cat /home/$CUSER/Downloads/kernels/mainline/$pickakernel/info.txt | grep -w "git_tag" | awk -F"git_tag=" '{print $2}')
											git_describe=$(cat /home/$CUSER/Downloads/kernels/mainline/$pickakernel/info.txt | grep -w "git_describe" | awk -F"git_describe=" '{print $2}')
											echo -ne "\n\n" >> /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit.txt
											echo "kernel version : $kernel_version" >> /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit.txt
											echo "git url        : $git_url" 		>> /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit.txt
											echo "git branch     : $git_branch" 	>> /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit.txt
											echo "git tag        : $git_tag" 		>> /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit.txt
											echo "git describe   : $git_describe" 	>> /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit.txt
											mv /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit.txt /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit &> /dev/null
											rm /home/$CUSER/Downloads/kernels/mainline/$pickakernel/info.txt &> /dev/null
											
											# Showing the outstanding information
											cat /home/$CUSER/Downloads/kernels/mainline/$pickakernel/commit | zenity --text-info --title="Intel® Graphics for Linux* | 01.org" --width=450 --height=300 2> /dev/null

											zenity --question --title="Intel® Graphics for Linux | 01.org" --text="Do you want to reboot now \n in order to use the kernel \n $pickakernel"	--width=250 2> /dev/null

											if [ $? = 0 ]; then
												echo $PASSWORD | sudo -S reboot
											else
												echo -ne "\n\n"
												exit 1
											fi
										fi
									fi
							done
					;;

				esac
			fi
		done		
	fi

}


$@