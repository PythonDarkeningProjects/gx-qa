#!/bin/bash
  # How to set PyDash v1.4.6 (24 April 2016)
  # user for PyDash : gfx / _PASSWORD for PyDash : linux

  source ../functions.sh
  _USER='gfx'
  _PASSWORD="linux"
  export _THISPATH=`cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd`
  export _PYDASH_PATH="${_THISPATH}"

  _DEPENDENCIES_LIST="git python-django apache2 python-pip libapache2-mod-wsgi"

  for dependence in ${_DEPENDENCIES_LIST}; do
    _CHECK_DEPENDENCE=`dpkg -l | grep -w "${dependence}"`
    if [ -z "${_CHECK_DEPENDENCE}" ]; then
      start_spinner "--> Installing ${dependence} ..."
        echo ${_PASSWORD} | sudo -S ls -l &> /dev/null && sleep 2; echo ${_PASSWORD} | sudo -S apt-get install ${dependence} -q=2 &> /dev/null
      stop_spinner $?
    fi
  done

  if [ ! -f "/home/$_USER/._pydash" ]; then

      start_spinner "--> Copying PyDash folder ..."
        echo ${_PASSWORD} | sudo -S ls &> /dev/null; sleep 2
        echo ${_PASSWORD} | sudo -S cp -r ${_PYDASH_PATH}/pydash /var/www/ #&> /dev/null
        # Setting the permissions for pydash folder
        echo ${_PASSWORD} | sudo -S chown -R www-data.www-data /var/www/pydash
      stop_spinner $?

      start_spinner "--> Copying pydash.conf ..."
        sleep 2
        echo ${_PASSWORD} | sudo -S cp ${_PYDASH_PATH}/pydash.conf /etc/apache2/sites-available/ &> /dev/null
        echo ${_PASSWORD} | sudo -S cp ${_PYDASH_PATH}/pydash.conf /etc/apache2/sites-enabled/ &> /dev/null
      stop_spinner $?


      start_spinner "--> Copying apache2.conf ..."
        sleep 2
        echo ${_PASSWORD} | sudo -S mv /etc/apache2/apache2.conf /etc/apache2/apache2.conf.old &> /dev/null
        echo ${_PASSWORD} | sudo -S cp ${_PYDASH_PATH}/apache2.conf /etc/apache2/ &> /dev/null
      stop_spinner $?

      start_spinner "--> Renaming apache2 default files for localhost ..."
        sleep 2
        echo ${_PASSWORD} | sudo -S mv /etc/apache2/sites-enabled/000-default.conf /etc/apache2/sites-enabled/000-default.conf.old &> /dev/null
        echo ${_PASSWORD} | sudo -S mv /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-available/000-default.conf.old &> /dev/null
      stop_spinner $?

      start_spinner "--> Restarting apache2 service ..."
        sleep 2
        echo ${_PASSWORD} | sudo -S chown -R www-data.www-data /var/www/pydash &> /dev/null # Setting again the permission as workaround
        echo ${_PASSWORD} | sudo -S service apache2 restart &> /dev/null
      stop_spinner $?

      touch /home/$_USER/._pydash

  else
    echo -ne "\n\n"; echo -ne "--> ${blue}PyDash${nc} is already installed in the system \n\n"
  fi