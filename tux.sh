#!/bin/bash

	# ==================================================================================================================
	# Save credentials fot github : https://git-scm.com/docs/git-credential-store
	# ==================================================================================================================
	# git config credential.helper store
	# git push http://github.com/IntelGraphics/dev
	# and then enter username and password
	#
	# Configuration for git
	# git config --global user.name "John Doe"
	# git config --global user.email johndoe@example.com
	#
	# See git configuration
	# git config --list
	# ==================================================================================================================

	clear
	# setting the permission for all the scripts
	# echo $PASSWORD | sudo -S ls -l &> /dev/null
	# Exporting this directory to path in order to run menu.sh in any place
	# checkpath=$(cat /home/$CUSER/.bashrc | grep -w "PATH=$PWD:$PATH")
	# if [ -z "$checkpath" ]; then echo "PATH=$PWD:$PATH" >> /home/$CUSER/.bashrc; echo "export PATH" >> /home/$CUSER/.bashrc; fi
	#export typearchitecture=$(uname -p) # x86_64 = 64 bits    i386 = 32 bits
	#if [ $typearchitecture = "x86" ]; then export architecture=32-bit; elif [ $typearchitecture = "x86_64" ]; then export architecture="64-bit"; else export architecture="$typearchitecture"; fi

	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>
	export CUSER=$(whoami)
	export PASSWORD=linux
	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>

	export thispath=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
	export GIT_SSL_NO_VERIFY=1

	##########################################
	# Loading tux functions                  #
	##########################################
	source ${thispath}/.functions/tux_functions.sh

	##########################################
	# Checking connection                    #
	##########################################
	#export ip=$(ifconfig | awk '/inet addr/{print substr($2,6)}' | grep -v "^127")
	export ip=`/sbin/ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'`

 	if [[ $ip =~ ^19 ]]; then
 		connection=SEDLINE
 		unset ALL_PROXY all_proxy http_proxy https_proxy ftp_proxy socks_proxy no_proxy
 	elif [ -z "$ip" ]; then
 		connection="${red}OFFLINE${nc}"
 	else
 		connection=INTRANET
 	fi


	##########################################
	# Check for updates on github            #
	##########################################
	if [[ ! -z $1 && $1 = "-nu" || ! -z $2 && $2 = "-nu" ]]; then
		export message=$(echo -e "${yellow}skipping updates${nc}")
		centered_message "${message}"
		sleep .75; clear
	else
		# git symbolic-ref --short HEAD # Current branch
		if [ "${connection}" = "SEDLINE" ] || [ "${connection}" = "INTRANET" ]; then
			clear; echo -ne "\n\n\n"
			start_spinner ">>> Checking updates from github.com ..."
				LOCAL_COMMIT=$(cd ${thispath} && git rev-parse origin/master) # Current commit
				REMOTE_COMMIT=$(cd ${thispath} && timeout 2 git ls-remote origin master | awk '{print $1}') # Latest commit
			stop_spinner $?
			if [ "${LOCAL_COMMIT}" != "${REMOTE_COMMIT}" ]; then
				export message=$(echo -e "dev folder is ${red}out-to-date${nc} please do a ${yellow}git pull${nc}")
				centered_message "${message}" "pull"
			elif [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
				export message=$(echo -e "dev folder is ${green}up-to-date${nc}")
				centered_message "${message}" "up-to-date"
			fi
		fi
	fi


	##########################################
	# Check for dependencies                 #
	##########################################

	# you can use the [[ ]] form rather than [ ], which allows && and || internally:

	if [[ ! -z $1 && $1 = "-nd" || ! -z $2 && $2 = "-nd" ]]; then
		clear
		export message=$(echo -e "${yellow}skipping dependencies${nc}")
		centered_message "${message}"
		sleep .75; clear
	else
		_DEPENDENCIES_LIST="sshpass dos2unix ssh vim git w3m zenity vim-gnome tmux mate-terminal synaptic"

		if [ "${connection}" = "SEDLINE" ] || [ "${connection}" = "INTRANET" ]; then
			for dependence in ${_DEPENDENCIES_LIST}; do
				_CHECK_DEPENDENCE=`dpkg -l | grep -w "${dependence}"`
				if [ -z "${_CHECK_DEPENDENCE}" ]; then
					start_spinner "--> Installing ${dependence} ..."
						echo ${PASSWORD} | sudo -S apt-get install ${dependence} -q=2 &> /tmp/error.log
					stop_spinner $?
					if [ "${_STATUS}" = "1" ]; then
						echo -ne "\n\n"; echo -ne "--> ${red}Something was wrong${nc} ..."; echo -ne "\n\n"; cat /tmp/error.log; echo -ne "\n\n"; exit 1
					fi
				fi
			done
		fi
	fi

	checkarchey=$(dpkg -l archey 2> /dev/null)
	if [ -z "$checkarchey" ]; then start_spinner "--> Installing archey ..."; echo ${PASSWORD} | sudo -S ls -l /tmp/ &> /dev/null && sleep 2; echo $PASSWORD | sudo -S apt-get install lsb-release scrot -q=2 &> /dev/null; wget http://github.com/downloads/djmelik/archey/archey-0.2.8.deb &> /dev/null; echo $PASSWORD | sudo -S dpkg -i archey-0.2.8.deb &> /dev/null; stop_spinner $? ;fi

	# Setting PS1
	checkps1=$(cat /home/$CUSER/.bashrc| grep -e ^PS1= -e "W]$ : '"$)
	if [ -z "$checkps1" ]; then echo "PS1='(\@) [\u@\h] [\W]$ : '" >> /home/$CUSER/.bashrc; fi
	##########################################
	# Setting alias                          #
	##########################################
	check_alias1=$(cat /home/$CUSER/.bashrc| grep -e "^alias clonedev")
	if [ -z "$check_alias1" ]; then echo "alias clonedev='git clone https://github.intel.com/linuxgraphics/gfx-qa-tools.git dev'" >> /home/$CUSER/.bashrc; fi
	check_alias2=$(cat /home/$CUSER/.bashrc| grep -e "^alias cdmesg")
	if [ -z "$check_alias2" ]; then echo "alias cdmesg='$thispath/tests/tools/check_dmesg_issues.sh'" >> /home/$CUSER/.bashrc; fi
	check_alias3=$(cat /home/$CUSER/.bashrc| grep -e "^alias tmux")
	if [ -z "$check_alias3" ]; then echo "alias tmuxs='exec /home/${CUSER}/.tmux.split'" >> /home/${CUSER}/.bashrc; fi
	check_alias4=$(cat /home/$CUSER/.bashrc| grep -e "^alias vim")
	if [ -z "$check_alias4" ]; then echo "alias vim='vim -c 'startinsert''" >> /home/${CUSER}/.bashrc; fi
	check_alias5=$(cat /home/$CUSER/.bashrc| grep -e "^alias hosts")
	if [ -z "$check_alias5" ]; then echo "alias hosts='$thispath/tests/tools/hosts.sh'" >> /home/${CUSER}/.bashrc; fi

	# Setting vim on the environment
	CheckEditor=$(cat /home/$CUSER/.bashrc| grep -e "^EDITOR=vim")
	if [ -z "${CheckEditor}" ]; then echo "EDITOR=vim" >> /home/$CUSER/.bashrc; fi
	# Erasing nano
	#_nano_editor=`dpkg -l | grep -w "nano"`
	# if [ ! -z "${_nano_editor}" ]; then echo ${PASSWORD} | sudo -S ls -l /tmp/ &> /dev/null && sleep 2; echo ${PASSWORD} | sudo -S apt-get remove nano -y &> /dev/null; fi


	##########################################
	# Check for configuration files          #
	##########################################

	if [ ! -f "/home/${CUSER}/.tmux.conf" ]; then cp ${thispath}/tests/tools/tmux.conf /home/${CUSER}/.tmux.conf &> /dev/null; fi
	if [ ! -f "/home/${CUSER}/.tmux.split" ]; then cp ${thispath}/tests/tools/tmux.split /home/${CUSER}/.tmux.split &> /dev/null; fi
	cp ${thispath}/tests/tools/vimrc /home/${CUSER}/.vimrc &> /dev/null

	##########################################
	# Check for ssh banner                   #
	##########################################

	_IP_BLACKLIST="10.219.106.111 10.219.106.16 10.219.128.200"
	_CHECK_IP_BLACKLIST=`echo ${_IP_BLACKLIST} | grep -w ${ip} 2> /dev/null`

	if [ -z "${_CHECK_IP_BLACKLIST}" ] && [ ! -f "/etc/motd" ]; then
		echo ${PASSWORD} | sudo -S ls &> /dev/null; sleep .75; echo ${PASSWORD} | sudo -S cp ${thispath}/tests/tools/ssh_tools/motd /etc/motd &> /dev/null
	fi


	if [ ! -f "/home/${CUSER}/.myssh.conf" ]; then
		clear; echo -ne "\n\n"
		start_spinner "--> Setting ssh environment ..."
			sleep .75

			UbuntuVersion=`cat /etc/*-release | grep -w "PRETTY_NAME" | awk -F"PRETTY_NAME=" '{print $2}' | sed 's/"//g'`
			MemoryRam=`echo ${PASSWORD} | sudo -S dmidecode –t 17 | grep "Range Size" | head -n 1 | awk -F": " '{print $2}'`
			Cpu=`cat /proc/cpuinfo | grep "model name" | head -n 1 | awk -F": " '{print $2}'`
			CPuCores=`cat /proc/cpuinfo | grep processor | wc -l`
			GpuCard=`echo ${PASSWORD} | sudo -S lspci -v -s $(lspci |grep "VGA compatible controller" |cut -d" " -f 1) | grep "VGA compatible controller" | awk -F": " '{print $2}'`
			DiskCapacity=`sudo lshw | grep -A 20 "*-scsi" | grep -A 10 "*-disk" | grep "size:" | sed 's/ *size: //g'`
			HostName=`echo ${HOSTNAME}`
			if [ `getconf LONG_BIT` = "64" ]; then arch="64-bit"; else arch="32-bit"; fi

			sed -i '3s|^.*$|Distro        : '"${UbuntuVersion}"'|g' ${thispath}/tests/tools/ssh_tools/issue.net
			sed -i '4s|^.*$|Memory        : '"${MemoryRam}"'|g' ${thispath}/tests/tools/ssh_tools/issue.net
			sed -i '5s|^.*$|Processor     : '"${Cpu}"'|g' ${thispath}/tests/tools/ssh_tools/issue.net
			sed -i '6s|^.*$|Graphic card  : '"${GpuCard}"'|g' ${thispath}/tests/tools/ssh_tools/issue.net
			sed -i '7s|^.*$|OS-Type       : '"${arch}"'|g' ${thispath}/tests/tools/ssh_tools/issue.net
			sed -i '8s|^.*$|Disk          : '"${DiskCapacity}"'|g' ${thispath}/tests/tools/ssh_tools/issue.net
			sed -i '9s|^.*$|Hostname      : '"${HostName}"'|g' ${thispath}/tests/tools/ssh_tools/issue.net
		stop_spinner $?

		export _SSH_TOOLS_PATH="${thispath}/tests/tools/ssh_tools"
		export _SSH_TOOLS_LIST=`ls ${thispath}/tests/tools/ssh_tools/`

			for file in ${_SSH_TOOLS_LIST}; do
				start_spinner "--> Copying [${file}] file in ssh system folder ..."
					sleep .5; echo ${PASSWORD} | sudo -S cp ${_SSH_TOOLS_PATH}/${file} /etc/ssh/ &> /dev/null
				stop_spinner $?
			done


		start_spinner "--> Restarting ssh in order to apply changes ..."
			sleep .75; echo ${PASSWORD} | sudo -S /etc/init.d/ssh restart &> /dev/null
		stop_spinner $?

		touch /home/${CUSER}/.myssh.conf
	fi # see man ssh_conf


:<<COMMENT
	if [ ! -z "$checkmatrix" ] && [ ! -z "$checkzenity" ] && [ ! -z "$checkarchey" ]; then
		cmatrix &
		pid=$(pidof cmatrix | awk '{print $1}')
		sleep 2
		kill -SIGTERM $pid
	fi
COMMENT


function mainMenu {

	pause(){
		local m="$@"
		echo "$m"
	}

	while :
	do

		clear
		archey
		echo -ne " ${bold}${blue}IP${nc} : [${bold}$ip${nc}] / CONNECTION : [${cyan}$connection${nc}] \n\n"
		echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
		#echo -ne " ${bold}`tput setf 4`User                :${nc} $(whoami) \n"
		#echo -ne " ${bold}`tput setf 4`OS                  :${nc} $(cat /etc/*-release | grep -w "PRETTY_NAME" | awk -F"PRETTY_NAME=" '{print $2}' | sed 's/"//g') $architecture \n"
		#echo -ne " ${bold}`tput setf 4`Ram                 :${nc} $(sudo dmidecode –t 17 | grep "Range Size" | head -n 1 | awk -F": " '{print $2}') \n"
		#echo -ne " ${bold}`tput setf 4`Cpu                 :${nc} $(cat /proc/cpuinfo | grep "model name" | head -n 1 | awk -F": " '{print $2}') \n"
		#echo -ne " ${bold}`tput setf 4`Cpu cores           :${nc} $(cat /proc/cpuinfo | grep processor | wc -l) \n"
		#echo -ne " ${bold}`tput setf 4`Desktop environment :${nc} $GDMSESSION \n"
		#echo -ne " ${bold}`tput setf 4`Shell               :${nc} $SHELL \n"
		#echo -ne " ${bold}`tput setf 4`Disk                :${nc} $(df -hT /home | awk '{print $4}' | tail -n 1) / $(dmesg | grep blocks | tail -n 1 | awk -F"(" '{print $2}' | awk -F"/" '{print $1}') \n\n"
		echo -ne " Select one option \n\n"
		echo -ne " ${bold}1)${nc} Tests Scripts \n"
		echo -ne " ${bold}2)${nc} Utilities \n\n"
		read -e -p " Your choice: " choose

		case ${choose} in

			1)

				pause(){
					local m="$@"
					echo "$m"
				}

					while :
					do
						clear #; echo -ne "\n\n"
						archey
						#ip=$(ifconfig | awk '/inet addr/{print substr($2,6)}' | grep -v "^127")
						export ip=`/sbin/ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'`
						if [[ $ip =~ ^19 ]]; then connection=SEDLINE; elif [ -z "$ip" ]; then connection="${red}OFFLINE${nc}"; else connection=INTRANET; fi
						echo -ne " `tput setaf 4`IP${nc} : [${bold}$ip${nc}] / CONNECTION : [`tput setaf 6`$connection${nc}] \n\n"
						echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
						echo -ne " Select one option \n\n"
						echo -ne " ${bold}1)${nc} Cairo menu \n"
						echo -ne " ${bold}2)${nc} Run glxgears tests \n"
						echo -ne " ${bold}3)${nc} Piglit menu \n"
						echo -ne " ${bold}4)${nc} Rendercheck menu \n"
						echo -ne " ${bold}5)${nc} Webglc (analyze results from a given file) \n"
						echo -ne " ${bold}6)${nc} Get debug logs \n"
						echo -ne " ${bold}7)${nc} Get drivers information \n"
						echo -ne " ${bold}8)${nc} Run ogles 1 / 2 / 3 tests \n"
						echo -ne " ${bold}9)${nc} Run stress tests (for s3/s4/freeze) \n"
						echo -ne " ${bold}10)${nc} Run SFT tests \n"
						echo -ne " ${bold}11)${nc} ${bold}${yellow}Return to Main Menu${nc} \n\n"
						read -e -p " Your choice : " choose

						case $choose in
							1)
								pause(){
									local m="$@"
								echo "$m"
								}

								while :
								do
									clear ; echo -ne "\n\n"
									echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
									echo -ne " What do you want yo do with Cairo ? \n\n"
									echo -ne " ${bold}1)${nc} Build Cairo from scratch \n"
									echo -ne " ${bold}2)${nc} Run cairo tests \n"
									echo -ne " ${bold}3)${nc} Select a folder for run cairo \n"
									echo -ne "    - select this option if you wish \n"
									echo -ne "    - specify a different folder than \n"
									echo -ne "    - [$PWD/tests/cairo] \n"
									echo -ne " ${bold}4)${nc} Create a report from a given file \n"
									echo -ne " ${bold}5)${nc} ${bold}${yellow}Return to Main Menu${nc} \n\n"
									read -e -p "Your choice : " choose

									case $choose in
										1) exec tests/Cairo.sh "scratch" "menu" ;;
										2) exec tests/Cairo.sh "runCairo" "menu" ;;
										3)
											pause(){
												local m="$@"
												echo "$m"
											}

											zenity --info --text="Please select cairo folder" 2> /dev/null
											folder=$(zenity --file-selection --directory --filename=/home/$CUSER/ 2> /dev/null)
											if [ $? != 0 ]; then pause; else exec tests/Cairo.sh "runCairo" "menu" "$folder"; fi
										;;

										4)
											pause(){
												local m="$@"
												echo "$m"
											}

											zenity --info --text="Please select the file" 2> /dev/null
											file=$(zenity --file-selection --filename=/home/$CUSER/ 2> /dev/null)
											if [ $? != 0 ]; then pause; else exec tests/Cairo.sh "report" "menu" "$file"; fi

										;;

										5) mainMenu ;;
									esac

								done

							;;


							2) exec tests/GlxGears.sh ;;
							3)

								pause(){
									local m="$@"
								echo "$m"
								}

								while :
								do
									clear ; echo -ne "\n\n"
									echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
									echo -ne " What do you want to do with Piglit ? \n\n"
									echo -ne " ${bold}1)${nc} Build pligit from scratch \n"
									echo -ne " ${bold}2)${nc} Run all piglit tests \n"
									echo -ne " ${bold}3)${nc} Resume interrupted piglit tests \n"
									echo -ne " ${bold}4)${nc} Analize results from piglit blacklist \n"
									echo -ne "    - Platforms availables are : ${bold}BDW/BYT/HSW/IVB/SKL/SNB/BSW${nc} \n"
									echo -ne " ${bold}5)${nc} Create a TRC report from a file.json \n"
									echo -ne " ${bold}6)${nc} ${bold}${yellow}Return to Main Menu${nc} \n\n"
									read -e -p " Your choice : " choose

									case $choose in


										1) echo $PASSWORD | sudo -S ls -l &> /dev/null; sleep 5; export countdep=1; exec tests/Piglit.sh waffle_flag ;;

										2)
											piglitfolder=tests/piglit ; wafflefolder=tests/waffle

											if [ ! -d "$piglitfolder" ] && [ ! -d "$wafflefolder" ]; then echo -ne " In order to run Piglit yoo must have piglit and waflle \n"; echo -ne " Please select the option 1 to build piglit \n"; echo -ne "     Press any key to continue   "; read -n 1 line; pause; else echo $PASSWORD | sudo -S ls -l &> /dev/null; sleep 5; exec tests/Piglit.sh piglitRun "all" "menu"; fi

										;;

										3)
											piglitfolder=tests/piglit ; wafflefolder=tests/waffle

											if [ ! -d "$piglitfolder" ] && [ ! -d "$wafflefolder" ]; then echo -ne "\n\n";echo -ne " In order to run Piglit yoo must have piglit and waflle \n"; echo -ne " Please select the option 1 to build piglit \n"; echo -ne "\n\n"; echo -ne "     Press any key to continue   "; read -n 1 line; pause; else exec tests/Piglit.sh "-r" "menu"; fi

										 ;;

										4)

										checkTTY=$(tty | awk -F"/dev/" '{print $2}')
										if [ ! -z "$SSH_CLIENT" ] || [ ! -z "$SSH_TTY" ] || [[ "$checkTTY" = "tty1"  || "$checkTTY" = "tty2" || "$checkTTY" = "tty3" || "$checkTTY" = "tty4" || "$checkTTY" = "tty5" || "$checkTTY" = "tty6" ]]; then
										# Under SSH

											pause(){
												local m="$@"
												echo "$m"
											}

											while :
											do
												clear ; echo -ne "\n\n"
												echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
												read -e -p " Full path to csv file : " filecsv

											if [ -z "$filecsv" ]; then
												pause

											else

												pause(){
													local m="$@"
													echo "$m"
												}

												while :
												do
													clear ; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"; echo -ne " CSV file is : $filecsv \n\n"; echo -ne " Platforms availables are : ${bold}BDW/BYT/HSW/IVB/SKL/SNB/BSW${nc} \n"
													read -e -p " Platform : " platform
													if [ -z "$platform" ]; then pause; else exec tests/Piglit.sh "-a" "$filecsv" "$platform" "menu"; fi
												done

											fi

											done

										else
												# Under X window
												pause(){
													local m="$@"
													echo "$m"
												}

												filecsv=$(zenity --file-selection --filename=/home/$CUSER/ 2> /dev/null)

												if [ -z "$filecsv" ]; then
													pause
												else

													pause(){
														local m="$@"
														echo "$m"
													}

													platform=$(zenity --list --text "Select a platform" --title "Intel® Graphics for Linux* | 01.org" --radiolist --column "Pick" --column "List" FALSE BDW FALSE BYT FALSE HSW FALSE IVB FALSE SKL FALSE SNB FALSE BSW --separator=":" 2> /dev/null)
													if [ -z "$platform" ]; then pause; else exec tests/Piglit.sh "-a" "$filecsv" "$platform" "menu"; fi

												fi

										fi

										 ;;

										5)

											pause(){
												local m="$@"
												echo "$m"
											}

											while :
											do
												clear ; echo -ne "\n\n"
												echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
												echo -ne " Do you want type or select your file : \n\n"
												echo -ne " ${bold}1)${nc} Type manually \n"
												echo -ne " ${bold}2)${nc} Select from box \n\n"
												read -e -p " Your choice : " choice

												if [ -z "$choice" ]; then pause; elif [ "$choice" = 1 ]; then read -e -p " Full path to the file : " path; elif [ "$choice" = 2 ]; then path=$(zenity --file-selection --filename=/home/$CUSER/ 2> /dev/null); fi

												if [ -z "$path" ]; then
													pause
												elif [ ! -z "$path" ] && [ -f "$path" ]; then

													export file="$path"
													extension=$(echo "${file#*.}")

													if [[ "$extension" == "json.bz2" ]] || [[ "$extension" == "json" ]]; then exec tests/Piglit.sh report "$path" "create" "menu"; else echo -ne "\n\n"; echo -ne " -- Your file has extension : [$extension] -- \n";echo -ne " > The files accepted by this script are \n"; echo -ne " > json.bz2 / json \n\n"; echo -ne "Please type down a valid file \n\n"; echo -ne "   Press any key to continue  "; read -n 1 line; pause; fi

												elif [ ! -z "$path" ] && [ ! -f "$path" ]; then
														echo -ne "\n\n"; echo -ne " The file [$path] ${bold}`tput setf 4`Not exists${nc} \n"
														echo -ne " Please enter a valid file \n" ; echo -ne "\n\n"; echo -ne "   Push any key to continue   " ; read -n 1 line; pause

												fi

											done

										 ;;

										 6) mainMenu ;;

										*) pause ;;

									esac

								done

								;;

							4)
								pause(){
									local m="$@"
								echo "$m"
								}

								while :
								do
									clear ; echo -ne "\n\n"
									echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
									echo -ne " What do you want yo do with Rendercheck ? \n\n"
									echo -ne " ${bold}1)${nc} Run rendercheck tests \n"
									echo -ne " ${bold}2)${nc} Merge 2 CSVs files \n"
									echo -ne " ${bold}3)${nc} Create a CSV report from a given file \n"
									echo -ne " ${bold}4)${nc} ${bold}${yellow}Return to Main Menu${nc} \n\n"
									read -e -p " Your choice : " choose


										case $choose in

											1) exec tests/Rendercheck.sh select_run "menu" ;;
											2)
												checkTTY=$(tty | awk -F"/dev/" '{print $2}')
												if [ ! -z "$SSH_CLIENT" ] || [ ! -z "$SSH_TTY" ] || [[ "$checkTTY" = "tty1"  || "$checkTTY" = "tty2" || "$checkTTY" = "tty3" || "$checkTTY" = "tty4" || "$checkTTY" = "tty5" || "$checkTTY" = "tty6" ]]; then
												# Under SSH

														pause1(){
															local m="$@"
															echo "$m"
														}
														while :
														do

															clear ; echo -ne "\n\n"
															echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
															echo -ne " Type down the path to CSVs files \n\n"
															read -e -p " CSV file 1 : " path1
															read -e -p " CSV file 2 : " path2
															if [ -z "$path1" ] || [ -z "$path2" ]; then pause; else exec tests/Rendercheck.sh "-m" "$path1" "$path2"; fi
														done
												else

															pause1(){
																local m="$@"
																echo "$m"
															}

															while :
															do
																zenity --info --text="Please select the first csv file" 2> /dev/null
																file1=$(zenity --file-selection --filename=/home/$CUSER/ 2> /dev/null 2> /dev/null)
																if [ -z "$file1" ]; then
																	zenity --question --title="Intel® Graphics for Linux | 01.org" --text="Do you want to exit ?" --width=250 2> /dev/null
																	if [ $? = 0 ]; then echo -ne "\n\n"; exit 2; elif [ $? = 1 ]; then pause; fi
																else
																	break
																fi
															done

															pause2(){
																local m="$@"
																echo "$m"
															}

															while :
															do

																zenity --info --text="Please select the second csv file" 2> /dev/null
																file2=$(zenity --file-selection --filename=/home/$CUSER/ 2> /dev/null)
																if [ -z "$file2" ]; then
																	zenity --question --title="Intel® Graphics for Linux | 01.org" --text="Do you want to exit ?" --width=250 2> /dev/null
																	if [ $? = 0 ]; then echo -ne "\n\n"; exit 2; elif [ $? = 1 ]; then pause; fi
																else
																	break
																fi
															done

															if [ ! -z "$file1" ] && [ ! -z "$file2" ]; then exec tests/Rendercheck.sh "-m" "$file1" "$file2"; fi

														# checkpaths=$(zenity --file-selection --multiple --filename=/home/$CUSER/)
														# path1=$(echo $checkpaths | awk -F"|" '{print $1}')
														# path2=$(echo $checkpaths | awk -F"|" '{print $2}')
												fi

													# if [ -z "$checkpaths" ]; then pause; else exec tests/Rendercheck.sh "-m" "$path1" "$path2"; fi
											;;

											3)

												checkTTY=$(tty | awk -F"/dev/" '{print $2}')
												if [ ! -z "$SSH_CLIENT" ] || [ ! -z "$SSH_TTY" ] || [[ "$checkTTY" = "tty1"  || "$checkTTY" = "tty2" || "$checkTTY" = "tty3" || "$checkTTY" = "tty4" || "$checkTTY" = "tty5" || "$checkTTY" = "tty6" ]]; then
												# Under SSH

													pause(){
														local m="$@"
														echo "$m"
													}

													while :
													do
														clear ; echo -ne "\n\n"
														echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
														read -e -p " Full path to the file : " path

														if [ -z "$path" ]; then
															pause
														else
															python tests/render.py "--report" "${path}"; exit 1
														fi

													done

												else
														# Under X window
														pause(){
															local m="$@"
															echo "$m"
														}

														path=$(zenity --file-selection --filename=/home/$CUSER/ 2> /dev/null)

														if [ -z "$path" ]; then
															pause
														else
															python tests/render.py "--report" "${path}"; exit 1
														fi
												fi

											;;

											4) mainMenu ;;

											*) pause ;;
										esac

								done

								;;
							5)

								checkTTY=$(tty | awk -F"/dev/" '{print $2}')
								if [ ! -z "$SSH_CLIENT" ] || [ ! -z "$SSH_TTY" ] || [[ "$checkTTY" = "tty1"  || "$checkTTY" = "tty2" || "$checkTTY" = "tty3" || "$checkTTY" = "tty4" || "$checkTTY" = "tty5" || "$checkTTY" = "tty6" ]]; then

									pause(){
										local m="$@"
									echo "$m"
									}

									while :
									do
										clear ; echo -ne "\n\n"
										echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
										read -e -p " Full path to file : " choose
										if [ -z "$choose" ]; then pause; else exec tests/Webglc.sh "-a" "$choose" "menu"; fi
									done

								else
									path=$(zenity --file-selection --filename=/home/$CUSER/ 2> /dev/null)
									if [ -z "$path" ]; then pause; else exec tests/Webglc.sh "-a" "$path" "menu"; fi
								fi

								;;

							6) exec tests/DebugLogs.sh "menu" ;;
							7) exec tests/DriversInformation.sh "menu";;

							8)
								pause(){
									local m="$@"
								echo "$m"
								}

								while :
								do
									clear ; echo -ne "\n\n"
									echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
									echo -ne " 1) ogles1conform \n"
									echo -ne " 2) ogles2conform / ogles3conform \n"
									echo -ne " 3) ${bold}${yellow}Return to Main Menu${nc} \n\n"
									read -e -p " Your choice : " choose


									case $choose in

										1)
											pause(){
												local m="$@"
												echo "$m"
											}


											while :
											do
												clear ; echo -ne "\n\n"
												echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
												echo -ne " 1) Analyze the results from a givin file to convert in TRC format \n"
												echo -ne " 2) Run ogles1conform tests \n"
												echo -ne " 3) Build ogles1conform from scratch \n"
												echo -ne " 4) ${bold}${yellow}Return to Main Menu${nc} \n\n"
												read -e -p " Your choice : " choose

												case $choose in

													1)
														checkTTY=$(tty | awk -F"/dev/" '{print $2}')
														if [ ! -z "$SSH_CLIENT" ] || [ ! -z "$SSH_TTY" ] || [[ "$checkTTY" = "tty1"  || "$checkTTY" = "tty2" || "$checkTTY" = "tty3" || "$checkTTY" = "tty4" || "$checkTTY" = "tty5" || "$checkTTY" = "tty6" ]]; then echo -ne "\n\n";	echo -ne "${bold}`tput setf 4` ******************************************${nc} \n"; echo -ne " ${bold}`tput setf 6`This option only run under [X Window System]${nc} \n"; echo -ne "${bold}`tput setf 4` ******************************************${nc} \n"; sleep 5; pause; else exec tests/ogles1conform.sh "-a" "menu"; fi
													 ;;

													2)
														checkTTY=$(tty | awk -F"/dev/" '{print $2}')
														if [ ! -z "$SSH_CLIENT" ] || [ ! -z "$SSH_TTY" ] || [[ "$checkTTY" = "tty1"  || "$checkTTY" = "tty2" || "$checkTTY" = "tty3" || "$checkTTY" = "tty4" || "$checkTTY" = "tty5" || "$checkTTY" = "tty6" ]]; then echo -ne "\n\n";	echo -ne "${bold}`tput setf 4` ******************************************${nc} \n"; echo -ne " ${bold}`tput setf 6`This option only run under [X Window System]${nc} \n"; echo -ne "${bold}`tput setf 4` ******************************************${nc} \n"; sleep 5; pause; else exec tests/ogles1conform.sh "-r" "menu"; fi
													;;

													3)

														checkTTY=$(tty | awk -F"/dev/" '{print $2}')
														if [ ! -z "$SSH_CLIENT" ] || [ ! -z "$SSH_TTY" ] || [[ "$checkTTY" = "tty1"  || "$checkTTY" = "tty2" || "$checkTTY" = "tty3" || "$checkTTY" = "tty4" || "$checkTTY" = "tty5" || "$checkTTY" = "tty6" ]]; then echo -ne "\n\n";	echo -ne "${bold}`tput setf 4` ******************************************${nc} \n"; echo -ne " ${bold}`tput setf 6`This option only run under [X Window System]${nc} \n"; echo -ne "${bold}`tput setf 4` ******************************************${nc} \n"; sleep 5; pause; else export countdep=1; exec tests/ogles1conform.sh "dependencies" "random" "menu"; fi
													;;

													4) mainMenu ;;

												esac

											done



										;;

										2)

											pause(){
												local m="$@"
												echo "$m"
											}

											while :
											do
												clear ; echo -ne "\n\n"
												echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
												echo -ne " 1) Build ogles2 / ogles3 from scratch \n"
												echo -ne " 2) Run ogles2 / ogles3 tests \n"
												echo -ne " ${bold}`tput setf 6`3)${nc} Return to Main Menu \n\n"
												read -e -p " Your choice : " choose


												case $choose in

													1) export countdep=1; exec tests/ogles23conform.sh "checkgitproxy" "random" "menu" ;;

													2) exec tests/ogles23conform.sh runOgles ;;

													3) mainMenu ;;

													*) pause ;;

												esac

											done

										;;

										3) mainMenu ;;

										*) pause ;;


									esac


								done

							;;

							9)

							# i need to set this commands in order to work with any platform
							# hwclock -systohc / hwclock -hctosys
								pause(){
									local m="$@"
									echo "$m"
								}

								while :
								do
									clear ; echo -ne "\n\n"
									echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
									echo -ne " 1) stress tests for s3 \n"
									echo -ne " 2) stress tests for s4 \n"
									echo -ne " 3) stress tests for freeze \n"
									echo -ne " 4) ${bold}${yellow}Return to Main Menu${nc} \n\n"
									read -p " Your choice : " choose

									case $choose in

										1)
											# S3 tests

											pause(){
												local m="$@"
												echo "$m"
											}

											while :
											do
												clear ; echo -ne "\n\n"
												echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
												read -p " How many iterations for s3 : " iterations

												if [ -z "$iterations" ]; then
													pause
												else

													pause(){
														local m="$@"
														echo "$m"
													}

													while :
													do
														clear ; echo -ne "\n\n"
														echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
														echo -ne " |== ${cyan}SUSPEND TIME${nc} ==| \n\n"
														echo -ne " ${yellow}Suspend time will be used for keeps the DUT${nc} \n"
														echo -ne " ${yellow}in S3 state, e.g : 44-48 = minimum_seconds-maximum_seconds${nc} \n"
														echo -ne " ${yellow}please specify the time in intervals of 4 seconds${nc} \n\n\n"
														read -p " Please specify the time for suspend : " suspendtime

														if [ -z "$suspendtime"]; then
															pause
														else

															pause(){
																local m="$@"
																echo "$m"
															}

															while :
															do
																clear ; echo -ne "\n\n"
																echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
																echo -ne " |== ${cyan}WAKE TIME${nc} ==| \n\n"
																echo -ne " ${yellow}wake time will be used for stay the DUT awake after an iteration${nc} \n"
																echo -ne " ${yellow}e.g : 44-48 = minimum_seconds-maximum_seconds${nc} \n"
																echo -ne " ${yellow}please specify the time in intervals of 4 seconds${nc} \n\n\n"
																read -p " Please specify the time for wake : " waketime

																if [ -z "$waketime" ]; then
																	pause
																else
																	clear ; echo -ne "\n\n"
																	echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
																	echo -ne " This is your configuration for S3 \n\n"
																	echo -ne " iterations    : ${yellow}${iterations}${nc} \n"
																	echo -ne " suspend-time  : ${cyan}${suspendtime}${nc} \n"
																	echo -ne " wake-time     : ${waketime} \n\n"
																	echo -ne " Do you want to continue ? \n\n"
																	echo -ne " 1) Yes \n"
																	echo -ne " 2) No \n\n"
																	read -p " Your choice : " choose

																	case $choose in

																	1)
																		export iterations=$iterations; export suspendtime=$suspendtime ; export waketime=$waketime # this is because i run stress tests under a subshell with script command
																		clear; echo -ne "\n\n"
																		echo -ne " ${yellow}#################################################${nc} \n"
																		echo -ne " --> Starting stress tests for s3 state <-- \n"
																		echo -ne " ++ Please do not touch your keyboard or mouse \n"
																		echo -ne " ++ while this script is running \n"
																		echo -ne " ++ ${cyan}This script will generate a log in [/home/$CUSER/Desktop/results/stress_tests/s3/s3_stress.log]${nc} \n"
																		echo -ne " ${yellow}#################################################${nc} \n\n"
																		echo -ne "Press any key to continue " ; read -n 1; echo -ne "\n\n"
																		echo -ne " --> suspend_stress_test.shell --mode=mem --iterations=${iterations} --suspend=${suspendtime} --wake=${waketime} --abort=none --display=error \n\n"

																		mkdir -p /home/$CUSER/Desktop/results/stress_tests/s3/
																		start_time
																		script /home/$CUSER/Desktop/results/stress_tests/s3/s3_stress.log bash -c 'echo $PASSWORD | sudo -S sh tests/suspend_stress_test.shell.sh --mode=mem --iterations=${iterations} --suspend=${suspendtime} --wake=${waketime} --abort=none --display=error'
																		wait

																		if [ $? = 0 ]; then
																			echo -ne "\n\n"
																			echo -ne " ${green}#################################################${nc} \n"
																			echo -ne " --> ${green}suspend stress tests has finished successfully${nc} <-- \n"
																			echo -ne " ${green}#################################################${nc} \n\n"

																			stop_time " Total time"
																			if [ -f "/home/$CUSER/s3_stress.log" ]; then
																				echo -ne " ++ s3_stress.log was create successfully in [mkdir -p /home/$CUSER/Desktop/results/stress_tests/s3/s3_stress.log] \n\n"; exit 2
																			fi

																		else
																			echo -ne "\n\n"
																			echo -ne " ${yellow}#################################################${nc} \n"
																			echo -ne " --> ${red}an error has occurred during the execution${nc} <-- \n"
																			echo -ne " ${yellow}#################################################${nc} \n\n"

																			stop_time " Total time"
																			if [ -f "/home/$CUSER/s3_stress.log" ]; then
																				echo -ne " ++ Please refer to s3_stress.log located in [mkdir -p /home/$CUSER/Desktop/results/stress_tests/s3/s3_stress.log] \n"
																				echo -ne " ++ for more information \n\n"; exit 2
																			fi


																		fi

																	;;

																	2) mainMenu ;;

																	*) pause ;;

																	esac

																fi

															done

														fi

													done

												fi

											done

										;;

										2)

											# S4 stress tests

											pause(){
												local m="$@"
												echo "$m"
											}

											while :
											do
												clear ; echo -ne "\n\n"
												echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
												read -p " How many iterations for s4 : " iterations

												if [ -z "$iterations" ]; then
													pause
												else

													pause(){
														local m="$@"
														echo "$m"
													}

													while :
													do
														clear ; echo -ne "\n\n"
														echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
														echo -ne " |== ${cyan}SUSPEND TIME${nc} ==| \n\n"
														echo -ne " ${yellow}Suspend time will be used for keeps the DUT${nc} \n"
														echo -ne " ${yellow}in S4 state, e.g : 44-48 = minimum_seconds-maximum_seconds${nc} \n"
														echo -ne " ${yellow}please specify the time in intervals of 4 seconds${nc} \n\n\n"
														read -p " Please specify the time for suspend : " suspendtime

														if [ -z "$suspendtime"]; then
															pause
														else

															pause(){
																local m="$@"
																echo "$m"
															}

															while :
															do
																clear ; echo -ne "\n\n"
																echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
																echo -ne " |== ${cyan}WAKE TIME${nc} ==| \n\n"
																echo -ne " ${yellow}wake time will be used for stay the DUT awake after an iteration${nc} \n"
																echo -ne " ${yellow}e.g : 44-48 = minimum_seconds-maximum_seconds${nc} \n"
																echo -ne " ${yellow}please specify the time in intervals of 4 seconds${nc} \n\n\n"
																read -p " Please specify the time for wake : " waketime

																if [ -z "$waketime" ]; then
																	pause
																else
																	clear ; echo -ne "\n\n"
																	echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
																	echo -ne " This is your configuration for S4 \n\n"
																	echo -ne " iterations    : ${yellow}${iterations}${nc} \n"
																	echo -ne " suspend-time  : ${cyan}${suspendtime}${nc} \n"
																	echo -ne " wake-time     : ${waketime} \n\n"
																	echo -ne " Do you want to continue ? \n\n"
																	echo -ne " 1) Yes \n"
																	echo -ne " 2) No \n\n"
																	read -p " Your choice : " choose

																	case $choose in

																	1)
																		export iterations=$iterations; export suspendtime=$suspendtime ; export waketime=$waketime # this is because i run stress tests under a subshell with script command
																		clear; echo -ne "\n\n"
																		echo -ne " ${yellow}#################################################${nc} \n"
																		echo -ne " --> Starting stress tests for s4 state <-- \n"
																		echo -ne " ++ Please do not touch your keyboard or mouse \n"
																		echo -ne " ++ while this script is running \n"
																		echo -ne " ++ ${cyan}This script will generate a log in [/home/$CUSER/Desktop/results/stress_tests/s4/s4_stress.log]${nc} \n"
																		echo -ne " ${yellow}#################################################${nc} \n\n"
																		echo -ne "Press any key to continue " ; read -n 1; echo -ne "\n\n"
																		echo -ne " --> suspend_stress_test.shell --mode=disk --iterations=${iterations} --suspend=${suspendtime} --wake=${waketime} --abort=none --display=error \n\n"

																		mkdir -p mkdir -p /home/$CUSER/Desktop/results/stress_tests/s4/
																		start_time
																		script /home/$CUSER/Desktop/results/stress_tests/s4/s4_stress.log bash -c 'echo $PASSWORD | sudo -S sh tests/suspend_stress_test.shell.sh --mode=disk --iterations=${iterations} --suspend=${suspendtime} --wake=${waketime} --abort=none --display=error'
																		wait

																		if [ $? = 0 ]; then
																			echo -ne "\n\n"
																			echo -ne " ${green}#################################################${nc} \n"
																			echo -ne " --> ${green}suspend stress tests has finished successfully${nc} <-- \n"
																			echo -ne " ${green}#################################################${nc} \n\n"

																			stop_time " Total time"
																			if [ -f "/home/$CUSER/s4_stress.log" ]; then
																				echo -ne " ++ s4_stress.log was create successfully in [/home/$CUSER/Desktop/results/stress_tests/s4/s4_stress.log] \n\n"; exit 2
																			fi

																		else
																			echo -ne "\n\n"
																			echo -ne " ${yellow}#################################################${nc} \n"
																			echo -ne " --> ${red}an error has occurred during the execution${nc} <-- \n"
																			echo -ne " ${yellow}#################################################${nc} \n\n"

																			stop_time " Total time"
																			if [ -f "/home/$CUSER/s4_stress.log" ]; then
																				echo -ne " ++ Please refer to s4_stress.log located in [/home/$CUSER/Desktop/results/stress_tests/s4/s4_stress.log] \n"
																				echo -ne " ++ for more information \n\n"; exit 2
																			fi


																		fi

																	;;

																	2) mainMenu ;;

																	*) pause ;;

																	esac

																fi

															done

														fi

													done

												fi

											done

										;;


										3)

											# freeze stress tests

											pause(){
												local m="$@"
												echo "$m"
											}

											while :
											do
												clear ; echo -ne "\n\n"
												echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
												read -p " How many iterations for freeze : " iterations

												if [ -z "$iterations" ]; then
													pause
												else

													pause(){
														local m="$@"
														echo "$m"
													}

													while :
													do
														clear ; echo -ne "\n\n"
														echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
														echo -ne " |== ${cyan}SUSPEND TIME${nc} ==| \n\n"
														echo -ne " ${yellow}Suspend time will be used for keeps the DUT${nc} \n"
														echo -ne " ${yellow}in freeze state, e.g : 44-48 = minimum_seconds-maximum_seconds${nc} \n"
														echo -ne " ${yellow}please specify the time in intervals of 4 seconds${nc} \n\n\n"
														read -p " Please specify the time for suspend : " suspendtime

														if [ -z "$suspendtime"]; then
															pause
														else

															pause(){
																local m="$@"
																echo "$m"
															}

															while :
															do
																clear ; echo -ne "\n\n"
																echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
																echo -ne " |== ${cyan}WAKE TIME${nc} ==| \n\n"
																echo -ne " ${yellow}wake time will be used for stay the DUT awake after an iteration${nc} \n"
																echo -ne " ${yellow}e.g : 44-48 = minimum_seconds-maximum_seconds${nc} \n"
																echo -ne " ${yellow}please specify the time in intervals of 4 seconds${nc} \n\n\n"
																read -p " Please specify the time for wake : " waketime

																if [ -z "$waketime" ]; then
																	pause
																else
																	clear ; echo -ne "\n\n"
																	echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
																	echo -ne " This is your configuration for freeze \n\n"
																	echo -ne " iterations    : ${yellow}${iterations}${nc} \n"
																	echo -ne " suspend-time  : ${cyan}${suspendtime}${nc} \n"
																	echo -ne " wake-time     : ${waketime} \n\n"
																	echo -ne " Do you want to continue ? \n\n"
																	echo -ne " 1) Yes \n"
																	echo -ne " 2) No \n\n"
																	read -p " Your choice : " choose

																	case $choose in

																	1)
																		export iterations=$iterations; export suspendtime=$suspendtime ; export waketime=$waketime # this is because i run stress tests under a subshell with script command
																		clear; echo -ne "\n\n"
																		echo -ne " ${yellow}#################################################${nc} \n"
																		echo -ne " --> Starting stress tests for freeze state <-- \n"
																		echo -ne " ++ Please do not touch your keyboard or mouse \n"
																		echo -ne " ++ while this script is running \n"
																		echo -ne " ++ ${cyan}This script will generate a log in [/home/$CUSER/freeze_stress.log]${nc} \n"
																		echo -ne " ${yellow}#################################################${nc} \n\n"
																		echo -ne "Press any key to continue " ; read -n 1; echo -ne "\n\n"
																		echo -ne " --> suspend_stress_test.shell --mode=idle --iterations=${iterations} --suspend=${suspendtime} --wake=${waketime} --abort=none --display=error \n\n"

																		start_time
																		script /home/$CUSER/freeze_stress.log bash -c 'echo $PASSWORD | sudo -S sh tests/suspend_stress_test.shell.sh --mode=idle --iterations=${iterations} --suspend=${suspendtime} --wake=${waketime} --abort=none --display=error'
																		wait

																		if [ $? = 0 ]; then
																			echo -ne "\n\n"
																			echo -ne " ${green}#################################################${nc} \n"
																			echo -ne " --> ${green}suspend stress tests has finished successfully${nc} <-- \n"
																			echo -ne " ${green}#################################################${nc} \n\n"

																			stop_time " Total time"
																			if [ -f "/home/$CUSER/freeze_stress.log" ]; then
																				echo -ne " ++ freeze_stress.log was create successfully in [/home/$CUSER/freeze_stress.log] \n\n"; exit 2
																			fi

																		else
																			echo -ne "\n\n"
																			echo -ne " ${yellow}#################################################${nc} \n"
																			echo -ne " --> ${red}an error has occurred during the execution${nc} <-- \n"
																			echo -ne " ${yellow}#################################################${nc} \n\n"

																			stop_time " Total time"
																			if [ -f "/home/$CUSER/freeze_stress.log" ]; then
																				echo -ne " ++ Please refer to freeze_stress.log located in [/home/$CUSER/freeze_stress.log] \n"
																				echo -ne " ++ for more information \n\n"; exit 2
																			fi


																		fi

																	;;

																	2) mainMenu ;;

																	*) pause ;;

																	esac

																fi

															done

														fi

													done

												fi

											done

										;;

										4) mainMenu ;;

									esac


								done

							;;

							10) source tests/SFT/SFT_menu.sh ; SFT_main_menu ;;

							11) mainMenu ;;

							*) pause ;;
						esac

					done
			;;

			2)

				pause(){
					local m="$@"
					echo "$m"
				}


				while :
				do
					clear
					archey
					export ip=`/sbin/ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'`
					if [[ $ip =~ ^19 ]]; then connection=SEDLINE; elif [ -z "$ip" ]; then connection="${red}OFFLINE${nc}"; else connection=INTRANET; fi
					echo -ne " ${blue}IP${nc} : [${bold}$ip${nc}] / CONNECTION : [${cyan}$connection${nc}] \n\n"
					echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
					echo -ne " 1) Select a kernel in your system \n"
					echo -ne " 2) Select a kernel in your system to boot with BXT \n"
					echo -ne " 3) ${yellow}Remove${nc} a kernel in your system \n"
					echo -ne " 4) Download a kernel from ${blue}${bold}linuxgraphics.intel.com${nc} (MX) \n"
					echo -ne " 5) Download a linux iso and make a ${blue}USB${nc} bootable \n"
					echo -ne " 6) Download editors for Ubuntu \n"
					echo -ne " 7) Upload your folder that contains your deb package to ${bold}${underline}${blue}https://linuxgraphics.intel.com${nc} \n"
					echo -ne " 8) Install all the dependencies needed for gfx stack \n"
					echo -ne " 9) Enable or disable graphical interface \n"
					echo -ne " 10) ${bold}${yellow}Return to mainMenu${nc} \n\n"
					read -e -p " Your choice : " choose


					case $choose in

						1)
							# under SSH
							checkTTY=$(tty | awk -F"/dev/" '{print $2}')
							if [ ! -z "$SSH_CLIENT" ] || [ ! -z "$SSH_TTY" ] || [[ "$checkTTY" = "tty1"  || "$checkTTY" = "tty2" || "$checkTTY" = "tty3" || "$checkTTY" = "tty4" || "$checkTTY" = "tty5" || "$checkTTY" = "tty6" ]]; then

								pause(){
									local m="$@"
									echo "$m"
								}


								while :
								do
									clear ; echo -ne "\n\n"
									echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
									ls /boot/ | grep initrd | sed 's/initrd.img-//g' | sort -r > /tmp/kernels

										number=""
										while [[ ! $number =~ ^[0-9]+$ ]]; do
												count=1
												kernel_line=`cat -n /etc/default/grub | grep "GRUB_CMDLINE_LINUX_DEFAULT=" | awk '{print $1}'`
												clear ; echo -ne "\n\n"
												echo -ne " Intel® Graphics for Linux* | 01.org [under SSH] \n\n\n"
												echo -ne " Select a kernel to boot in the next reboot \n"
												#echo -ne " Kernel parameters : $(sed -n 11p /etc/default/grub | awk -F"GRUB_CMDLINE_LINUX_DEFAULT=" '{print $2}' | sed 's/"//g') \n"
												echo -ne " Kernel parameters : $(sed -n '${kernel_line}'p /etc/default/grub | awk -F"GRUB_CMDLINE_LINUX_DEFAULT=" '{print $2}' | sed 's/"//g') \n"
												echo -ne " Your current kernel is : ${bold}`tput setf 6`$(uname -r)${nc} \n\n"
												while read line
												do
													echo -ne " $line \n" | sed 's/'"$line"'/'"$count"') '"$line"'/g'
													let count+=1
												done < /tmp/kernels
											echo
    										echo -ne " Your choice : "
    										read number
										done
									export number

									# read -e -p " Your choice : " kchoose
									# export kchoose

										check=$(cat -n /tmp/kernels | awk '{print $1}' | grep -w "$number")

										if [ -z "$check" ]; then
											echo -ne "\n\n"
											echo -ne " Please enter a valid option \n\n"
											echo -ne "\t Press any key to continue \t "; read -n 1; pause

										else
											export kernelname=$(sed -n "$number"p /tmp/kernels)
											echo -ne "\n\n"
											echo -ne " You've selected : [$kernelname] \n"
											echo -ne " Do you want to continue ? \n\n"
											echo -ne " 1) Yes \n"
											echo -ne " 2) No \n\n"
											read -e -p " Your choice : " choose


											case $choose in

												1)
												clear ; echo -ne "\n\n"
												echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
												start_spinner "++ Adding [$kernelname] to grub  ... "
													echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 5
													echo $PASSWORD | sudo -S sed -i '6s/^.*$/GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux '"$kernelname"'"/g' /etc/default/grub
													sleep 2
												stop_spinner $?

												start_spinner "++ Updating the grub  ... "
													echo $PASSWORD | sudo -S update-grub &> /dev/null
												stop_spinner $?

												echo -ne "\n\n"
												echo -ne "++ ${bold}${yellow}Do you want to reboot in order to use the kernel${nc} : ${bold}${underline}[$kernelname]${nc} \n\n"
												echo -ne " 1) Yes \n"
												echo -ne " 2) No \n\n"
												read -e -p "Your choice : " choose

												case $choose in

													1) echo $PASSWORD | sudo -S reboot; exit 1 ;;

													2) echo	-ne "\n\n"; exit 1 ;;

													*) echo	-ne "\n\n"; exit 1 ;;

												esac

												;;


												2) pause ;;

											esac
										fi

								done



							elif [ -z "$SSH_CLIENT" ] && [ -z "$SSH_TTY" ]; then

									# under X widows

								pause(){
									local m="$@"
									echo "$m"
								}

								while :
								do
									# zenity --info --text="Please select a kernel"

									ls /boot/ | grep initrd | sed 's/initrd.img-//g' | sort -r > /tmp/kernels
									unset list

									while read line
									do
    									list+=("FALSE")
    									list+=("$line")
									done < /tmp/kernels

									# display the dialog
									xkernelname=$(zenity --list --text "Select a kernel" --title "Intel® Graphics for Linux* | 01.org" --radiolist --column "Pick" --column "List" "${list[@]}" --separator=":" 2> /dev/null)
									if [ -z "$xkernelname" ]; then
										exit 1


									else
										(
										echo $PASSWORD | sudo -S ls &> /dev/null
										echo $PASSWORD | sudo -S sed -i '6s/^.*$/GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux '"$xkernelname"'"/g' /etc/default/grub
										echo $PASSWORD | sudo -S update-grub >& /dev/null
										) | zenity --progress --title="Intel® Graphics for Linux* | 01.org" --text="Updating grub ... " --pulsate 2> /dev/null


										zenity --question --title="Intel® Graphics for Linux | 01.org" --text="Do you want to reboot now \n in order to use the kernel \n $xkernelname"	--width=250 2> /dev/null

											if [ $? = 0 ]; then
												echo $PASSWORD | sudo -S reboot
											else
												echo -ne "\n\n"
												exit 1
											fi

									fi

								done

							fi

						;;

						2) exec tests/tools/select-kernel-for-bxt.sh

						;;

						3)

								pause(){
									local m="$@"
									echo "$m"
								}


								while :
								do
									clear ; echo -ne "\n\n"
									echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
									ls /boot/ | grep initrd | sed 's/initrd.img-//g' | sort -r > /tmp/kernels

										number=""
										while [[ ! $number =~ ^[0-9]+$ ]]; do
												count=1
												clear ; echo -ne "\n\n"
												echo -ne " Intel® Graphics for Linux* | 01.org [under SSH] \n\n\n"
												echo -ne " ${bold}Select a kernel to remove from your system${nc} \n"
												echo -ne " ${yellow}Kernel parameters${nc} : $(sed -n 11p /etc/default/grub | awk -F"GRUB_CMDLINE_LINUX_DEFAULT=" '{print $2}' | sed 's/"//g') \n"
												echo -ne " Your current kernel is : ${bold}$(uname -r)${nc} \n\n"
												while read line
												do
													echo -ne " $line \n" | sed 's/'"$line"'/'"$count"') '"$line"'/g'
													let count+=1
												done < /tmp/kernels
											echo
    										echo -ne " Your choice : "
    										read number
										done
									export number

									# read -e -p " Your choice : " kchoose
									# export kchoose

										check=$(cat -n /tmp/kernels | awk '{print $1}' | grep -w "$number")

										if [ -z "$check" ]; then
											echo -ne "\n\n"
											echo -ne " Please enter a valid option \n\n"
											echo -ne "\t Press any key to continue \t "; read -n 1; pause

										else
											export kernelname=$(sed -n "$number"p /tmp/kernels)
											echo -ne "\n\n"
											echo -ne " You've selected : [$kernelname] \n"
											echo -ne " Are you sure ? \n\n"
											echo -ne " 1) Yes \n"
											echo -ne " 2) No \n\n"
											read -e -p " Your choice : " choose


											case $choose in

												1)
													# dpkg --list | grep linux-image-
													clear ; echo -ne "\n\n"
													echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
													start_spinner "++ apt-get purge linux-image-$kernelname ... "
														echo $PASSWORD | sudo -S apt-get purge linux-image-$kernelname -y &> /dev/null
													stop_spinner $?
													start_spinner "++ apt-get purge linux-headers-$kernelname ... "
														echo $PASSWORD | sudo -S apt-get purge linux-headers-$kernelname -y &> /dev/null
													stop_spinner $?
													start_spinner "++ Updating grub ... "
														echo $PASSWORD | sudo -S update-grub &> /dev/null
													stop_spinner $?

													pause(){
														local m="$@"
														echo "$m"
													}

													while :
													do
														clear ; echo -ne "\n\n"
														echo -ne " Intel® Graphics for Linux* | 01.org \n\n\n"
														echo -ne " ${bold}${yellow}the kernel${nc} : ${underline}${bold}$kernelname${nc} \n"
														echo -ne " has been removed from your system \n"
														echo -ne " Do you want to reboot now ? \n\n"
														echo -ne " 1) Yes \n"
														echo -ne " 2) No \n\n"
														read -e -p " Your choice : " choose

														case $choose in

															1) echo $PASSWORD | sudo -S reboot &> /dev/null; exit 2 ;;

															2) echo -ne "\n\n"; exit 2 ;;

														esac

													done


												;;


												2) pause ;;

											esac


										fi


							done



						;;


						4)
							ip=$(ifconfig | awk '/inet addr/{print substr($2,6)}' | grep -v "^127")
							if [[ $ip =~ ^19 ]]; then
								# connection=SEDLINE
								echo -ne "\n\n"
								echo -ne " ${bold}${yellow}This option only works on INTRANET connection${nc} \n"
								echo -ne "\n\n"; exit 2
							else
								# Testing conection to linuxgraphics.intel.com
									echo -ne "\n\n"
									start_spinner "++ Testing connection to linuxgraphics.intel.com ... "
										ping -c1 linuxgraphics.intel.com &> /dev/null
										sleep 2
									stop_spinner $? | tee .log

									check=$(cat .log | grep "FAIL")

									if [ ! -z "$check" ]; then
										echo -ne "\n\n"
										echo -ne "++ The server ${underline}linuxgraphics.intel.com${nc} is ${red}unavailable${nc} \n"
										echo -ne "++ please try download the kernel from ${blue}vanaheimr.tl.intel.com${nc} \n"
										echo -ne "++ running this script (option 4 Utilities > option 4) \n\n"; exit 2
									else
										# connection=INTRANET
										source tests/tools/download-kernel_mx.sh "download_kernel"
									fi

							fi

						;;


						5)
							# Checing for type of conection
							ip=$(ifconfig | awk '/inet addr/{print substr($2,6)}' | grep -v "^127")
							if [[ $ip =~ ^19 ]]; then
								# connection=SEDLINE
								echo -ne "\n\n"
								echo -ne " ${bold}${yellow}${underline}You are connected to ${red}SEDLINE${nc} \n"
								echo -ne " ${bold}${yellow}${underline}This option only works on INTRANET connection${nc} \n"
								echo -ne "\n\n"; exit 2
							fi

							checkTTY=$(tty | awk -F"/dev/" '{print $2}')
							if [ ! -z "$SSH_CLIENT" ] || [ ! -z "$SSH_TTY" ] || [[ "$checkTTY" = "tty1"  || "$checkTTY" = "tty2" || "$checkTTY" = "tty3" || "$checkTTY" = "tty4" || "$checkTTY" = "tty5" || "$checkTTY" = "tty6" ]]; then
								# Under SSH
								echo -ne "\n\n"
								echo -ne "${red}+++++++++++++++++++++++++++++++++++++++++++++++${nc} \n"
								echo -ne " --> ${bold}${underline}${yellow}This option only run in Graphical mode${nc} <-- \n"
								echo -ne "${red}+++++++++++++++++++++++++++++++++++++++++++++++${nc} \n\n"
								exit 1

							else

								check=$(dpkg -l usb-creator-gtk)
								if [ -z "$check" ]; then echo $PASSWORD | sudo -S ls -l &> /dev/null; sleep 5; echo $PASSWORD | sudo -S apt-get install usb-creator-gtk &> /dev/null; fi

									# Checking if is connect at least one USB and there is no more than one USB
									mountpoint=$(df -T | grep /media/$CUSER/ | awk '{print $1}')
									check=$(df -T | grep /media/$CUSER/ | awk '{print $1}'| wc -l)
									usbid=$(echo $PASSWORD | sudo -S blkid $mountpoint | awk -F"UUID=" '{print $2}' | awk '{print $1}' | sed 's/"//g')

									if [ -z "$mountpoint" ]; then zenity --error --title "Intel® Graphics for Linux* | 01.org" --text="Please connect at least one USB" 2> /dev/null; wait; exit 1; fi
									if [ "$check" -gt 1 ]; then zenity --error --title "Intel® Graphics for Linux* | 01.org" --text="You have "$check" USB connected, please disconnect one" 2> /dev/null; wait; exit 1; fi

									# This is an add for Fedora's ISOS
									zenity --title="Notice" --question --text="This option only works with Ubuntu's ISOS \n For Fedora's ISOS you might to download the right tools from : \n linuxgraphics.intel.com \n\n the recommended tools are : rufus (for windows) and fedora Live USB creator (windows and linux) \n\n Do you want to continue ?" 2> /dev/null
									if [ $? = 1 ]; then echo -ne "\n\n"; exit 2; fi

									zenity --question --title="Intel® Graphics for Linux | 01.org" --text="Do you want to format the USB as Fat32" --width=250 2> /dev/null
									if [ $? = 0 ]; then
										( # unmounting
											echo $PASSWORD | sudo -S umount -f $mountpoint &> /dev/null
											sleep 2
										) | zenity --progress --auto-close --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Unmounting USB in [$mountpoint]" --pulsate 2> /dev/null

										( # Formating as Fat32
											echo $PASSWORD | sudo -S mkfs.vfat $mountpoint &> /dev/null
											sleep 2
										) | zenity --progress --auto-close --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Formating USB as Fat32" --pulsate 2> /dev/null

										( # mounting again
											echo $PASSWORD | sudo -S mount -t vfat $mountpoint /mnt/ &> /dev/null
											sleep 2
										) | zenity --progress --auto-close --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Mounting USB in [/mnt]" --pulsate 2> /dev/null
									fi

								# Under Graphical mode

									isos=$(zenity --list --text "Select an iso" --title "Intel® Graphics for Linux* | 01.org" --radiolist --column "Pick" --column "OS" FALSE "Ubuntu" FALSE "Fedora" --separator=":" 2> /dev/null)

									if [ ! -z "$isos" ] && [ "$isos" = "Ubuntu" ]; then
										sshpass -p guest ssh -o "StrictHostKeyChecking no" guest@10.219.106.67 ls /home/guest/isos/ubuntu > /tmp/ubuntuisos

										unset list

										while read line
										do
    										list+=("FALSE")
    										list+=("$line")
										done < /tmp/ubuntuisos

										version=$(zenity --list --text "Select a version" --title "Intel® Graphics for Linux* | 01.org" --radiolist --column "Pick" --column "Version" "${list[@]}" --separator=":" 2> /dev/null)

										if [ $? = 1 ]; then
											exit 1

										elif [ ! -z "$version" ]; then

											architecture_ubuntu=$(zenity --list --text "Select the architecture" --title "Intel® Graphics for Linux* | 01.org" --radiolist --column "Pick" --column "architecture" FALSE "32-bit" FALSE "64-bit" --separator=":" 2> /dev/null)

											case $architecture_ubuntu in

												32-bit)
														iso_image=$(sshpass -p guest ssh -o "StrictHostKeyChecking no" guest@10.219.106.67 ls /home/guest/isos/ubuntu/$version/ | grep -w "i386")

														if [ ! -f "/home/$CUSER/Downloads/Isos/Ubuntu/$version/$iso_image" ]; then

															mkdir -p /home/$CUSER/Downloads/Isos/Ubuntu/$version

															(
															sshpass -p guest scp -o "StrictHostKeyChecking no" guest@10.219.106.67:/home/guest/isos/ubuntu/$version/$iso_image /home/$CUSER/Downloads/Isos/Ubuntu/$version/ &> /dev/null
															wait
															) | zenity --progress --auto-close --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Downloading ubuntu iso \n $iso_image" --pulsate 2> /dev/null

															echo $PASSWORD | sudo -S ls -l &> /dev/null; sleep 5
															echo $PASSWORD | sudo -S usb-creator-gtk -i /home/$CUSER/Downloads/Isos/Ubuntu/$version/$iso_image
															wait
															exit 1

														else
															zenity --info --text="The iso image \n ($iso_image) \n already exits" 2> /dev/null
															echo $PASSWORD | sudo -S ls -l &> /dev/null; sleep 5
															echo $PASSWORD | sudo -S usb-creator-gtk -i /home/$CUSER/Downloads/Isos/Ubuntu/$version/$iso_image
															wait
															exit 1

														fi

													;;


												64-bit)

														iso_image=$(sshpass -p guest ssh -o "StrictHostKeyChecking no" guest@10.219.106.67 ls /home/guest/isos/ubuntu/$version/ | grep -w "amd64")

														if [ ! -f "/home/$CUSER/Downloads/Isos/Ubuntu/$version/$iso_image" ]; then

															mkdir -p /home/$CUSER/Downloads/Isos/Ubuntu/$version

															(
															sshpass -p guest scp -o "StrictHostKeyChecking no" guest@10.219.106.67:/home/guest/isos/ubuntu/$version/$iso_image /home/$CUSER/Downloads/Isos/Ubuntu/$version/ &> /dev/null
															wait
															) | zenity --progress --auto-close --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Downloading Ubuntu iso \n $iso_image" --pulsate 2> /dev/null

															echo $PASSWORD | sudo -S ls -l &> /dev/null; sleep 5
															echo $PASSWORD | sudo -S usb-creator-gtk -i /home/$CUSER/Downloads/Isos/Ubuntu/$version/$iso_image
															wait
															exit 1

														else
															zenity --info --text="The iso image \n ($iso_image) \n already exits" 2> /dev/null
															echo $PASSWORD | sudo -S ls -l &> /dev/null; sleep 5
															echo $PASSWORD | sudo -S usb-creator-gtk -i /home/$CUSER/Downloads/Isos/Ubuntu/$version/$iso_image
															wait
															exit 1

														fi

													;;

												*) exit 1 ;;

											esac

										fi


									elif [ ! -z "$isos" ] && [ "$isos" = "Fedora" ]; then

										sshpass -p guest ssh -o "StrictHostKeyChecking no" guest@10.219.106.67 ls /home/guest/isos/fedora > /tmp/fedoraisos

										unset list

										while read line
										do
    										list+=("FALSE")
    										list+=("$line")
										done < /tmp/fedoraisos

										version=$(zenity --list --text "Select a version" --title "Intel® Graphics for Linux* | 01.org" --radiolist --column "Pick" --column "Version" "${list[@]}" --separator=":" 2> /dev/null)

										if [ ! -z "$version" ]; then

											architecture_fedora=$(zenity --list --text "Select the architecture" --title "Intel® Graphics for Linux* | 01.org" --radiolist --column "Pick" --column "architecture" FALSE "32-bit" FALSE "64-bit" --separator=":" 2> /dev/null)

											case $architecture_fedora in

												32-bit)
														iso_image=$(sshpass -p guest ssh -o "StrictHostKeyChecking no" guest@10.219.106.67 ls /home/guest/isos/fedora/$version/ | grep -w "i686")

														if [ ! -f "/home/$CUSER/Downloads/Isos/Fedora/$version/$iso_image" ]; then

															mkdir -p /home/$CUSER/Downloads/Isos/Fedora/$version

															(
															sshpass -p guest scp -o "StrictHostKeyChecking no" guest@10.219.106.67:/home/guest/isos/fedora/$version/$iso_image /home/$CUSER/Downloads/Isos/Fedora/$version/ &> /dev/null
															wait
															) | zenity --progress --auto-close --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Downloading Fedora iso \n $iso_image" --pulsate 2> /dev/null

															echo $PASSWORD | sudo -S ls -l &> /dev/null; sleep 5
															echo $PASSWORD | sudo -S usb-creator-gtk -i /home/$CUSER/Downloads/Isos/Fedora/$version/$iso_image
															wait
															exit 1

														else
															zenity --info --text="The iso image \n ($iso_image) \n already exits" 2> /dev/null
															echo $PASSWORD | sudo -S ls -l &> /dev/null; sleep 5
															echo $PASSWORD | sudo -S usb-creator-gtk -i /home/$CUSER/Downloads/Isos/Fedora/$version/$iso_image
															wait
															exit 1

														fi

													;;


												64-bit)

														iso_image=$(sshpass -p guest ssh -o "StrictHostKeyChecking no" guest@10.219.106.67 ls /home/guest/isos/fedora/$version/ | grep -w "x86_64")

														if [ ! -f "/home/$CUSER/Downloads/Isos/Fedora/$version/$iso_image" ]; then

															mkdir -p /home/$CUSER/Downloads/Isos/Fedora/$version

															(
															sshpass -p guest scp -o "StrictHostKeyChecking no" guest@10.219.106.67:/home/guest/isos/fedora/$version/$iso_image /home/$CUSER/Downloads/Isos/Fedora/$version/ &> /dev/null
															wait
															) | zenity --progress --auto-close --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Downloading ubuntu iso \n $iso_image" --pulsate 2> /dev/null

															echo $PASSWORD | sudo -S ls -l &> /dev/null; sleep 5
															echo $PASSWORD | sudo -S usb-creator-gtk -i /home/$CUSER/Downloads/Isos/Fedora/$version/$iso_image
															wait
															exit 1

														else
															zenity --info --text="The iso image \n ($iso_image) \n already exits" 2> /dev/null
															echo $PASSWORD | sudo -S ls -l &> /dev/null; sleep 5
															echo $PASSWORD | sudo -S usb-creator-gtk -i /home/$CUSER/Downloads/Isos/Fedora/$version/$iso_image
															wait
															exit 1

														fi

													;;

												*) exit 1 ;;

											esac

										fi

									fi

							fi

						;;

						6) exec tests/tools/editors/download_editors.sh ;;

						7)

							# Checing for type of conection
							ip=$(ifconfig | awk '/inet addr/{print substr($2,6)}' | grep -v "^127")
							if [[ $ip =~ ^19 ]]; then
								# connection=SEDLINE
								echo -ne "\n\n"
								echo -ne " ${bold}${yellow}${underline}You are connected to ${red}SEDLINE${nc} \n"
								echo -ne " ${bold}${yellow}${underline}This option only works on INTRANET connection${nc} \n"
								echo -ne "\n\n"; exit 2
							fi

							# solo falta checar antes de subir el folder que no exista en el servidor
							# Creating the file that contains all folders from deb_packages

							ls /home/$CUSER/intel-graphics/deb_packages > /tmp/deb_folders

							unset list

							while read line
							do
								list+=("FALSE")
								list+=("$line")
							done < /tmp/deb_folders

							deb_folders=$(zenity --list --text "Select the deb package folder" --title "Intel® Graphics for Linux* | 01.org" --radiolist --column "Pick" --column "Folder" "${list[@]}" --separator=":" 2> /dev/null)

							if [ ! -z "$deb_folders" ]; then

								zenity --question --width=250 --title="Intel® Graphics for Linux | 01.org" --text="Are you sure to upload \n $deb_folders "	2> /dev/null

								if [ $? = 0 ]; then

									(
										sshpass -p linuxgfx scp -o "StrictHostKeyChecking no" -r /home/gfx/intel-graphics/deb_packages/"$deb_folders"/ gfxserver@10.219.106.67:/home/gfxserver/automation/gfx_stack_deb_packages/
									) | zenity --progress --no-cancel --title="Intel® Graphics for Linux* | 01.org" --text="Uploading $deb_folders to linuxgraphics.intel.com ... " --pulsate 2> /dev/null

									echo -ne "\n\n"; exit

								else
									echo -ne "\n\n"; exit 2
								fi

							else

								echo -ne "\n\n"; exit

							fi

						;;

						8) exec tests/tools/full_dep.sh ;;

						9)

							pause(){
								local m="$@"
								echo "$m"
							}

							while :
							do
								clear; echo -ne "\n\n"; echo -ne " Intel® Graphics for Linux* | 01.org \n\n"
								echo -ne " 1) Enable graphical interface \n"
								echo -ne " 2) Disable graphical interface \n\n"
								read -p " Your choice : " choose


								case $choose in

									1)  echo -ne "\n\n"
										start_spinner "++ Enabling graphical interface ... "
										echo $PASSWORD | sudo -S ls &> /dev/null; sleep 3
										echo $PASSWORD | sudo -S systemctl set-default graphical.target &> /dev/null
										echo $PASSWORD | sudo -S systemctl start lightdm &> /dev/null
										stop_spinner $?

										echo -ne "\n\n"; exit 2

										;;


									2)  echo -ne "\n\n"
										start_spinner "++ Disabling graphical interface ... "
										echo $PASSWORD | sudo -S ls &> /dev/null; sleep 3
										echo $PASSWORD | sudo -S systemctl enable multi-user.target --force &> /dev/null
										echo $PASSWORD | sudo -S systemctl set-default multi-user.target &> /dev/null
										stop_spinner $? | tee .log

										check=$(cat .log | grep "FAIL")

										if [ -z "$check" ]; then
											echo -ne "\n\n"
											echo -ne "++ Do you want to reboot in order to start in tty mode ? \n\n"
											echo -ne " 1) Yes \n"
											echo -ne " 2) No \n\n"
											read -p " Your choice : " choose

											case $choose in

												1) echo $PASSWORD | sudo -S reboot; exit 2 ;;

												2) echo -ne "\n\n"; exit 2 ;;

											esac

										else
											echo -ne "\n\n"
											echo -ne "++ ${yellow}Something was wrong disabling the graphical interface${nc} \n"
											echo -ne "++ Please disable graphical interface manually following this steps \n"
											echo -ne " 1) sudo systemctl enable multi-user.target --force \n"
											echo -ne " 2) systemctl set-default multi-user.target \n"
											echo -ne " 3) sudo reboot \n\n"; exit 2

										fi

									;;

									*) pause ;;

								esac

							done


						;;

						10) mainMenu ;;

						*) pause ;;

					esac
				done
			;;


			*) pause ;;
		esac
	done

}


function terminalSettings {

	checkTTY=$(tty | awk -F"/dev/" '{print $2}')
	if [ ! -z "$SSH_CLIENT" ] || [ ! -z "$SSH_TTY" ] || [[ "$checkTTY" = "tty1"  || "$checkTTY" = "tty2" || "$checkTTY" = "tty3" || "$checkTTY" = "tty4" || "$checkTTY" = "tty5" || "$checkTTY" = "tty6" ]]; then mainMenu; fi

		# ONLY WORKS ON UBUNTU 14
		# file = /home/gfx/.gconf/apps/gnome-terminal/profiles/Default
		# Setting the color
		gconftool-2 --set /apps/gnome-terminal/profiles/Default/background_color --type string "#031F29"
		# Seting the cursor
		gconftool-2 --set /apps/gnome-terminal/profiles/Default/cursor_shape --type string "underline"
		# Setting terminal's name
		gconftool-2 --set /apps/gnome-terminal/profiles/Default/title --type string "linux-graphics"
		# Setting terminal size (funciona pero no inmediatamente para la ventana actual, hasta la proxima ventana abierta)
		gconftool-2 --set /apps/gnome-terminal/profiles/Default/use_custom_default_size --type bool "true"
		gconftool-2 --set /apps/gnome-terminal/profiles/Default/default_size_rows --type int "40"
		gconftool-2 --set /apps/gnome-terminal/profiles/Default/default_size_columns --type int "150"
		# Setting terminal's font and foreground color
		gconftool-2 --set /apps/gnome-terminal/profiles/Default/font --type string "Nimbus Mono L 13"
		gconftool-2 --set /apps/gnome-terminal/profiles/Default/foreground_color --type string "#FFFFFFFFFFFF"
		# Setting buffer
		gconftool-2 --set /apps/gnome-terminal/profiles/Default/scrollback_unlimited --type bool "true"
		# Setting transparent window
		gconftool-2 --set /apps/gnome-terminal/profiles/Default/background_type --type string "transparent"
		gconftool-2 --set /apps/gnome-terminal/profiles/Default/background_darkness --type float "0.9206010103225708"
		# unchecking use theme color button
		gconftool-2 --set /apps/gnome-terminal/profiles/Default/use_theme_colors --type bool "false"

		# Setting keybindings
		gconftool-2 --set /apps/gnome-terminal/keybindings/new_tab --type string "<Primary>t"
		gconftool-2 --set /apps/gnome-terminal/keybindings/new_window --type string "<Primary>n"
		gconftool-2 --set /apps/gnome-terminal/keybindings/close_tab --type string "<Primary>w"
		gconftool-2 --set /apps/gnome-terminal/keybindings/close_window --type string "<Primary>q"
		gconftool-2 --set /apps/gnome-terminal/keybindings/next_tab --type string "<Primary>Right"
		gconftool-2 --set /apps/gnome-terminal/keybindings/prev_tab --type string "<Primary>Left"
		gconftool-2 --set /apps/gnome-terminal/keybindings/paste --type string "<Primary>v"
		gconftool-2 --set /apps/gnome-terminal/keybindings/copy --type string "<Primary>c"

		mainMenu

}

# function help() {

# 	PS3='Please enter your choice: '
# 	options=("Option 1" "Option 2" "Option 3" "Quit")
# 	select opt in "${options[@]}"
# 	do
# 	    case $opt in
# 	        "Option 1")
# 	            echo "you chose choice 1"
# 	            ;;
# 	        "Option 2")
# 	            echo "you chose choice 2"
# 	            ;;
# 	        "Option 3")
# 	            echo "you chose choice 3"
# 	            ;;
# 	        "Quit")
# 	            break
# 	            ;;
# 	        *) echo invalid option;;
# 	    esac
# 	done
# }


# terminalSettings
mainMenu
