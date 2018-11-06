#!/bin/bash
  # How to set PyDash v1.4.6 (24 April 2016)
  # user for PyDash : gfx / Password for PyDash : linux

  # <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>
	export CUSER=`whoami`
	export PASSWORD=linux
	# <<-- SET HERE YOUR CURRENT USER AND PASSWORD FOR LINUX -->>

  # <<-- Setting the global colors -->
  # http://misc.flogisoft.com/bash/tip_colors_and_formatting
  # The right colors that works under TTys are : https://wiki.archlinux.org/index.php/Color_Bash_Prompt_(Espa%C3%B1ol)#Indicadores_Basicos
  export nc="\e[0m"
  export underline="\e[4m"
  export bold="\e[1m"
  export green="\e[1;32m"
  export red="\e[1;31m"
  export yellow="\e[1;33m"
  export blue="\e[1;34m"
  export cyan="\e[1;36m"
  # <<-- Setting the global colors -->

  export thispath=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

  function _spinner() {
      # $1 start/stop
      #
      # on start: $2 display message
      # on stop : $2 process exit status
      #           $3 spinner function pid (supplied from stop_spinner)

      local on_success="DONE"
      local on_fail="FAIL"
      local white="\e[1;37m"
      local green="\e[1;32m"
      local red="\e[1;31m"
      local nc="\e[0m"

      case $1 in
          start)
              # calculate the column where spinner and status msg will be displayed
              let column=$(tput cols)-${#2}-8
              # display message and position the cursor in $column column
              echo -ne ${2}
              printf "%${column}s"

              # start spinner
              i=1
              sp='\|/-'
              delay=${SPINNER_DELAY:-0.15}

              while :
              do
                  printf "\b${sp:i++%${#sp}:1}"
                  sleep $delay
              done
              ;;
          stop)
              if [[ -z ${3} ]]; then
                  echo "spinner is not running.."
                  exit 1
              fi

              kill $3 > /dev/null 2>&1

              # inform the user uppon success or failure
              echo -en "\b["
              if [[ $2 -eq 0 ]]; then
                  echo -en "${green}${on_success}${nc}"
              else
                  echo -en "${red}${on_fail}${nc}"
              fi
              echo -e "]"
              ;;
          *)
              echo "invalid argument, try {start/stop}"
              exit 1
              ;;
      esac

  }

  function start_spinner {
      # $1 : msg to display
      _spinner "start" "${1}" &
      # set global spinner pid
      _sp_pid=$!
      disown

  }

  function stop_spinner {
      # $1 : command exit status
      _spinner "stop" $1 $_sp_pid
      unset _sp_pid

  }

  # << Cheking for dependencies in the system >>
  _check_git=`dpkg -l | grep -w "git"`
  _check_django=`dpkg -l | grep -w "python-django"`
  _check_apache2=`dpkg -l | grep -w "apache2"`
  _check_pip=`dpkg -l | grep -w "python-pip"`
  _check_lib_apache=`dpkg -l | grep -w "libapache2-mod-wsgi"`

  if [ -z "$_check_git" ]; then start_spinner "++ Installing git ..."; echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 2; echo $PASSWORD | sudo -S apt-get install git -q=2 &> /dev/null; stop_spinner $? ;fi
  if [ -z "$_check_django" ]; then start_spinner "++ Installing python-django ..."; echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 2; echo $PASSWORD | sudo -S apt-get install python-django -q=2 &> /dev/null; stop_spinner $? ;fi
  if [ -z "$_check_apache2" ]; then start_spinner "++ Installing apache2 ..."; echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 2; echo $PASSWORD | sudo -S apt-get install apache2 -q=2 &> /dev/null; stop_spinner $? ;fi
  if [ -z "$_check_pip" ]; then start_spinner "++ Installing python-pip ..."; echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 2; echo $PASSWORD | sudo -S apt-get install python-pip -q=2 &> /dev/null; stop_spinner $? ;fi
  if [ -z "$_check_lib_apache" ]; then start_spinner "++ Installing libapache2-mod-wsgi ..."; echo $PASSWORD | sudo -S ls -l &> /dev/null && sleep 2; echo $PASSWORD | sudo -S apt-get install libapache2-mod-wsgi -q=2 &> /dev/null; stop_spinner $? ;fi
  # << Cheking for dependencies in the system >>

  if [ ! -f "/home/$CUSER/._pydash" ]; then

      start_spinner "++ Copying PyDash folder ..."
        echo $PASSWORD | sudo -S ls &> /dev/null; sleep 2
        echo $PASSWORD | sudo -S cp -r $thispath/pydash /var/www/ &> /dev/null
        # Setting the permissions for pydash folder
        echo $PASSWORD | sudo -S chown -R www-data.www-data /var/www/pydash
      stop_spinner $?

      start_spinner "++ Copying pydash.conf ..."
        echo $PASSWORD | sudo -S ls &> /dev/null; sleep 2
        echo $PASSWORD | sudo -S cp $thispath/pydash.conf /etc/apache2/sites-available/ &> /dev/null
        echo $PASSWORD | sudo -S cp $thispath/pydash.conf /etc/apache2/sites-enabled/ &> /dev/null
      stop_spinner $?


      start_spinner "++ Copying apache2.conf ..."
        echo $PASSWORD | sudo -S ls &> /dev/null; sleep 2
        echo $PASSWORD | sudo -S mv /etc/apache2/apache2.conf /etc/apache2/apache2.conf.old
        echo $PASSWORD | sudo -S cp $thispath/apache2.conf /etc/apache2/ &> /dev/null
      stop_spinner $?

      start_spinner "++ Renaming apache2 default files for localhost ..."
        echo $PASSWORD | sudo -S ls &> /dev/null; sleep 2
        echo $PASSWORD | sudo -S mv /etc/apache2/sites-enabled/000-default.conf /etc/apache2/sites-enabled/000-default.conf.old &> /dev/null
        echo $PASSWORD | sudo -S mv /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-available/000-default.conf.old &> /dev/null
      stop_spinner $?

      start_spinner "++ Restarting apache2 service ..."
        echo $PASSWORD | sudo -S ls &> /dev/null; sleep 2
        echo $PASSWORD | sudo -S chown -R www-data.www-data /var/www/pydash # Setting again the permission as workaround
        echo $PASSWORD | sudo -S service apache2 restart &> /dev/null
      stop_spinner $?

      touch /home/$CUSER/._pydash

  else
    echo -ne "\n\n"; echo -ne "++ ${blue}PyDash${nc} is already installed in the system \n\n"
  fi