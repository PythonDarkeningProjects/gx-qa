##rsyslog configuration file

###parameter - hourly
######description
Log files are rotated every hour. Note that usually logrotate is configured to be run by cron daily. You have to change this configuration and run logrotate hourly to be able to really rotatelogs hourly.

###parameter - maxage count
######description
Remove rotated logs older than <count> days. The age is only checked if the logfile is to be rotated. The files are mailed to the configured address if maillast and mail are configured.

###parameter - maxsize size
######description
Log files are rotated when they grow bigger than size bytes even before the additionally specified time interval (daily, weekly, monthly, or yearly). The  related  size  option  is  similar except  that it is mutually exclusive with the time interval options, and it causes log files to be rotated without regard for the last rotation time.  When maxsize is used, both the size and timestamp of a log file are considered.
```
This parameter depends of two factors
1 - time interval options
2 - maxsize of the log
```

###parameter - rotate count
######description
Log files are rotated count times before being removed or mailed to the address specified in a mail directive. If count is 0, old versions are removed rather than rotated.

###parameter - size size
######description
Log  files  are  rotated  only  if they grow bigger then size bytes. If size is followed by k, the size is assumed to be in kilobytes.  If the M is used, the size is in megabytes, and if G is used, the size is in gigabytes. So size 100, size 100k, size 100M and size 100G are all valid.

#### Configuration files
######/etc/logrotate.d/rsyslog
######/var/lib/logrotate/status     "Default state file"
######/etc/logrotate.conf           "Configuration options"

#### manual
man logrotate

###Rules for rsyslog file (for intel-gpu-tools)
```
1 - limit the maximum rotatory logs to 4.
2 - limit the maximum size for the rotatory logs to 15M
3 - generate a new rotatory log when one of the following conditions are met:
    whether the log exceeds of 15M or has one day elapsed.

Note : with these preventive measures we can make sure of the IGT execution
will be fine in most of the DUTs in the automated system since the disk
will no longer fill with with unnecessary system logs.
```

####References:
[how-do-i-limit-the-size-of-my-syslog](https://askubuntu.com/questions/184949/how-do-i-limit-the-size-of-my-syslog)