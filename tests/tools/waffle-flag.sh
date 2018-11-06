#!/bin/bash


function waffleflag {

	echo -ne "\n\n"
	check=$(cat /home/$cuser/.bashrc | grep -w 'export LD_LIBRARY_PATH='$thispath'/waffle/lib:$LD_LIBRARY_PATH')

	if [ -z "$check" ]; then 

		start_spinner '++ Adding waffle flag to bashrc ... '
			sleep 5; echo 'export LD_LIBRARY_PATH='$thispath'/waffle/lib:$LD_LIBRARY_PATH' >> /home/$cuser/.bashrc
		stop_spinner $?
		start_spinner '++ Recharging bashrc ... '
			source /home/$cuser/.bashrc &> /dev/null; sleep 3
		stop_spinner $?
		echo -ne "\n\n"
		echo "library path : $LD_LIBRARY_PATH"
		#piglit
		exit 1

	else 
		#piglit
		exit 1
	fi
	
}
