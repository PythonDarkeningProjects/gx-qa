#!/bin/bash

	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>
	export CUSER=$(whoami)
	export PASSWORD=linux
	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>

function download_kernel {

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
			echo -ne " 2) drm-intel-testing \n\n"
			read -p " Your choice : " choose
			echo -ne "\n\n"

			case $choose in

				1)
					# drm-intel-nightly

					start_spinner "++ Generating WW kernel list"
						w3m linuxgraphics.intel.com/kernels/drm-intel-nightly/ > /tmp/wwlist
						# Cleaning the list
						sed -i '/^\s*$/d' /tmp/wwlist # empty lines
						cat /tmp/wwlist | grep -w "DIR" | awk '{print $2}' | sed 's|/||g' > /tmp/ww1
						rm /tmp/wwlist &> /dev/null; mv /tmp/ww1 /tmp/wwlist
						cat -n /tmp/wwlist > /tmp/ww1; rm /tmp/wwlist; mv /tmp/ww1 /tmp/wwlist
						sleep 2
					stop_spinner $?
						
					unset list
					while read line
					do
	    				numbers=$(echo $line | awk '{print $1}')
    					list+=("$numbers")
					done < /tmp/wwlist


					pause(){
						local m="$@"
						echo "$m"
					}	

					while :
					do
						clear; echo -ne "\n\n"
						echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
						echo -ne " Select a WW \n\n"
						cat /tmp/wwlist
						echo -ne "\n\n"
						read -p " Your choice : " ww
						echo -ne "\n\n"

						check=$(echo ${list[@]} | grep -w "$ww")

						if [ -z "$check" ]; then
							pause

						else

							# Getting WW name
							export ww=$(sed -n "$ww"p /tmp/wwlist | awk '{print $2}')

							start_spinner "++ Generating kernel list"
								# Downloading the list of kernels
								w3m linuxgraphics.intel.com/kernels/drm-intel-nightly/$ww > /tmp/drm-intel-nightly_list; wait
								# Cleaning the list
								sed -i '/^\s*$/d' /tmp/drm-intel-nightly_list # empty lines
								cat /tmp/drm-intel-nightly_list | grep -w "DIR" | grep -ve "debug" -ve "latest" | awk '{print $2}' | sed 's|/||g' > /tmp/1
								rm /tmp/drm-intel-nightly_list &> /dev/null; mv /tmp/1 /tmp/drm-intel-nightly_list
								cat -n /tmp/drm-intel-nightly_list > /tmp/1; rm /tmp/drm-intel-nightly_list; mv /tmp/1 /tmp/drm-intel-nightly_list

								unset list
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

									mkdir -p /home/$CUSER/Downloads/kernels/drm-intel-nightly/$ww/$pickakernel/ && cd /home/$CUSER/Downloads/kernels/drm-intel-nightly/$ww/$pickakernel/
									start_spinner "++ Downloading the kernel $pickakernel"			
										wget linuxgraphics.intel.com/kernels/drm-intel-nightly/$ww/$pickakernel/commit_info &> /dev/null; wait
										wget linuxgraphics.intel.com/kernels/drm-intel-nightly/$ww/$pickakernel/package_list &> /dev/null; wait
										wget -A '.deb' -np -nd -m -E -k -K -e robots=off -l 1 linuxgraphics.intel.com/kernels/drm-intel-nightly/$ww/$pickakernel/deb_packages/ &> /dev/null; wait
									stop_spinner $? | tee /tmp/.log

									check=$(cat /tmp/.log | grep "FAIL")

									if [ -z "$check" ]; then

										start_spinner "++ Installing the kernel $pickakernel"
											cd /home/$CUSER/Downloads/kernels/drm-intel-nightly/$ww/$pickakernel/
											echo $PASSWORD | sudo -S ls -l &> /dev/null; sleep 5
											echo $PASSWORD | sudo -S dpkg -i *.deb &> /dev/null
											wait
										stop_spinner $?

										check_kernel=$(cat /etc/default/grub |grep -w "Advanced options for Ubuntu>Ubuntu, with Linux")

										if [ ! -z "$check_kernel" ]; then

											start_spinner "++ Adding [$pickakernel] to grub  ... "
												kerneln=$(ls /home/$CUSER/Downloads/kernels/drm-intel-nightly/$ww/$pickakernel | grep -w "firmware-image" | awk -F"firmware-image-" '{print $2}' | awk -F"_" '{print $1}')
												echo $PASSWORD | sudo -S sed -i '6s/^.*$/GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux '"$kerneln"'"/g' /etc/default/grub 
												sleep 4
											stop_spinner $?
										fi 	

										
										# Showing the outstanding information
										echo -ne "\n\n"
										echo -ne " ++ Commit information \n\n"
										cat /home/$CUSER/Downloads/kernels/drm-intel-nightly/$ww/$pickakernel/commit_info
										echo -ne "\n\n"
										echo -ne " ++ Do you want to reboot now in order to use the kernel \n"
										echo -ne " ++ $pickakernel \n\n"
										echo -ne " 1) Restart now \n"
										echo -ne " 2) Restart later \n\n"
										read -p " Your choice : " choose

											case $choose in

												1) echo $PASSWORD | sudo -S ls -l &> /dev/null; sleep 5; echo $PASSWORD | sudo -S reboot ; exit 1 ;;

												2) echo -ne "\n\n"; exit 1 ;;

												*) echo -ne "\n\n"; exit 1 ;;

											esac

									else
										echo -ne "\n\n"
										echo -ne " ++ `tput bold``tput setf 4`an error has occurred when downloading the kernel`tput sgr0` \n"
										echo -ne " ++ `tput bold``tput setf 4`check is the server : linuxgraphics.intel.com`tput sgr0` \n"
										echo -ne " ++ `tput bold``tput setf 4`is online`tput sgr0` \n\n\n"
										exit 1

									fi

								fi

							done

						fi

					done

				;;


				2)
					# drm-intel-testing

					start_spinner "++ Generating WW kernel list"
						w3m linuxgraphics.intel.com/kernels/drm-intel-testing/ > /tmp/wwlist
						# Cleaning the list
						sed -i '/^\s*$/d' /tmp/wwlist # empty lines
						cat /tmp/wwlist | grep -w "DIR" | awk '{print $2}' | sed 's|/||g' > /tmp/ww1
						rm /tmp/wwlist &> /dev/null; mv /tmp/ww1 /tmp/wwlist
						cat -n /tmp/wwlist > /tmp/ww1; rm /tmp/wwlist; mv /tmp/ww1 /tmp/wwlist
						sleep 2
					stop_spinner $?
						
					unset list
					while read line
					do
	    				numbers=$(echo $line | awk '{print $1}')
    					list+=("$numbers")
					done < /tmp/wwlist


					pause(){
						local m="$@"
						echo "$m"
					}	

					while :
					do
						clear; echo -ne "\n\n"
						echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
						echo -ne " Select a WW \n\n"
						cat /tmp/wwlist
						echo -ne "\n\n"
						read -p " Your choice : " ww
						echo -ne "\n\n"

						check=$(echo ${list[@]} | grep -w "$ww")

						if [ -z "$check" ]; then
							pause

						else

							# Getting WW name
							export ww=$(sed -n "$ww"p /tmp/wwlist | awk '{print $2}')

							start_spinner "++ Generating kernel list"
								# Downloading the list of kernels
								w3m linuxgraphics.intel.com/kernels/drm-intel-testing/$ww > /tmp/drm-intel-testing_list; wait
								# Cleaning the list
								sed -i '/^\s*$/d' /tmp/drm-intel-testing_list # empty lines
								cat /tmp/drm-intel-testing_list | grep -w "DIR" | grep -ve "debug" -ve "latest" | awk '{print $2}' | sed 's|/||g' > /tmp/1
								rm /tmp/drm-intel-testing_list &> /dev/null; mv /tmp/1 /tmp/drm-intel-testing_list
								cat -n /tmp/drm-intel-testing_list > /tmp/1; rm /tmp/drm-intel-testing_list; mv /tmp/1 /tmp/drm-intel-testing_list

								unset list
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

									mkdir -p /home/$CUSER/Downloads/kernels/drm-intel-testing/$ww/$pickakernel/ && cd /home/$CUSER/Downloads/kernels/drm-intel-testing/$ww/$pickakernel/
									start_spinner "++ Downloading the kernel $pickakernel"			
										wget linuxgraphics.intel.com/kernels/drm-intel-testing/$ww/$pickakernel/commit_info &> /dev/null; wait
										wget linuxgraphics.intel.com/kernels/drm-intel-testing/$ww/$pickakernel/package_list &> /dev/null; wait
										wget -A '.deb' -np -nd -m -E -k -K -e robots=off -l 1 linuxgraphics.intel.com/kernels/drm-intel-testing/$ww/$pickakernel/deb_packages/ &> /dev/null; wait
									stop_spinner $? | tee /tmp/.log

									check=$(cat /tmp/.log | grep "FAIL")

									if [ -z "$check" ]; then

										start_spinner "++ Installing the kernel $pickakernel"
											cd /home/$CUSER/Downloads/kernels/drm-intel-testing/$ww/$pickakernel/
											echo $PASSWORD | sudo -S ls -l &> /dev/null; sleep 5
											echo $PASSWORD | sudo -S dpkg -i *.deb &> /dev/null
											wait
										stop_spinner $?

										check_kernel=$(cat /etc/default/grub |grep -w "Advanced options for Ubuntu>Ubuntu, with Linux")

										if [ ! -z "$check_kernel" ]; then

											start_spinner "++ Adding [$pickakernel] to grub  ... "
												kerneln=$(ls /home/$CUSER/Downloads/kernels/drm-intel-testing/$ww/$pickakernel | grep -w "firmware-image" | awk -F"firmware-image-" '{print $2}' | awk -F"_" '{print $1}')
												echo $PASSWORD | sudo -S sed -i '6s/^.*$/GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux '"$kerneln"'"/g' /etc/default/grub 
												sleep 4
											stop_spinner $?
										fi 	

										
										# Showing the outstanding information
										echo -ne "\n\n"
										echo -ne " ++ Commit information \n\n"
										cat /home/$CUSER/Downloads/kernels/drm-intel-testing/$ww/$pickakernel/commit_info
										echo -ne "\n\n"
										echo -ne " ++ Do you want to reboot now in order to use the kernel \n"
										echo -ne " ++ $pickakernel \n\n"
										echo -ne " 1) Restart now \n"
										echo -ne " 2) Restart later \n\n"
										read -p " Your choice : " choose

											case $choose in

												1) echo $PASSWORD | sudo -S ls -l &> /dev/null; sleep 5; echo $PASSWORD | sudo -S reboot ; exit 1 ;;

												2) echo -ne "\n\n"; exit 1 ;;

												*) echo -ne "\n\n"; exit 1 ;;

											esac

									else
										echo -ne "\n\n"
										echo -ne " ++ `tput bold``tput setf 4`an error has occurred when downloading the kernel`tput sgr0` \n"
										echo -ne " ++ `tput bold``tput setf 4`check is the server : linuxgraphics.intel.com`tput sgr0` \n"
										echo -ne " ++ `tput bold``tput setf 4`is online`tput sgr0` \n\n\n"
										exit 1

									fi

								fi

							done

						fi

					done

				;;


				*) pause ;;

			esac	
		
		done

}


$@