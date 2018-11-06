#!/bin/bash
benchmarks_list=`ls /opt/benchmarks/ | grep .tar.gz`; len=`echo "${benchmarks_list}" | wc -w`; count=1
for benchmark in ${benchmarks_list}; do 
	echo -ne ">>> gzip : decompressing (${benchmark}) (${count}/${len}) ... "
	cmd=`gzip -d /opt/benchmarks/${benchmark}`; output=$?
	if [ ${output} -eq 0 ]; then 
		echo "done"; tar_name=`echo ${benchmark} | sed 's/.gz//g'`
		echo -ne ">>> tar  : decompressing (${tar_name}) ... "; cmd=`cd /opt/benchmarks/ && tar -xf ${tar_name}`
		output=$?
		if [ ${output} -eq 0 ]; then echo "done"; else echo "fail"; fi
	else
		echo "fail"; continue
	fi
	((count++))
done
rm /opt/benchmarks/*.tar
