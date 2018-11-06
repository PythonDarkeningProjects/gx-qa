#!/bin/bash

function run_test()
{
	local -a pid
	counter=0

	while [ $counter -ne $loops ]; do
		echo "[CMD] round $counter"
		pcounter=0
		for test in $tests; do
			if [ -f ${test}.sh ]; then
				echo start ${test}
				/bin/bash ${test}.sh &
				pid[$pcounter]=$!
			else
				echo not exist
			fi
			((pcounter=$pcounter+1))
		done

		pcounter=0
		for test in $tests; do
			if [ -f ${test}.sh ]; then
				echo waiting $test ${pid[$pcounter]}
				wait ${pid[$pcounter]}
				echo $test finished
			fi
			((pcounter=$pcounter+1))
		done
		echo "[CMD] round $counter done"
		((counter=$counter+1))
	done
}

function help()
{
    cat << EOF
  Tool for running lengthy testing.

  Usage:
  $0 [ -t "test list" ] [ -i loop ]

    -t "test list"        : list of tests to be executed
    -i "loop"             : how many loops we run the tests
    -h or --help          : This manual.

EOF
}


if [ $# -lt 4 -o "$1" = "-h" -o "$1" = "--help" ]; then
    help
    exit 0
fi

tests=

dmesg -c > dmesg

while [ $# -gt 0 ]; do
        case $1 in
        "-t")
            [ -z "$2" ] && help && exit 1
            tests=$2; shift 2
            ;;
        "-i")
            [ -z "$2" ] && help && exit 1
            loops=$2; shift 2
            ;;
        *)
            help
            exit 0
            ;;
        esac
done

run_test

dmesg -c >> dmesg
