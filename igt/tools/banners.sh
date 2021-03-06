#!/bin/bash

function banner() {

case $1 in

	"igt_all")
		echo "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
		echo "|i|n|t|e|l|-|g|p|u|-|t|o|o|l|s|-|a|l|l|"
		echo "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
	;;

	"igt_fast_feedback")
		echo "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
		echo "|i|n|t|e|l|-|g|p|u|-|t|o|o|l|s|-|f|a|s|t|f|e|e|d|b|a|c|k|"
		echo "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
	;;


	"igt_extended_list")
		echo "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
		echo "|i|n|t|e|l|-|g|p|u|-|t|o|o|l|s|-|e|x|t|e|n|d|e|d|"
		echo "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
	;;

	"igt_clone_testing")
		echo "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
		echo "|i|n|t|e|l|-|g|p|u|-|t|o|o|l|s|-|c|l|o|n|e|s|"
		echo "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
	;;

	"start")
		echo "+-+-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
		echo "|s|t|a|r|t|i|n|g| |i|n|t|e|l|-|g|p|u|-|t|o|o|l|s|"
		echo "+-+-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"
	;;


	"error")
		echo "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+"
		echo "|i|n|t|e|l|-|g|p|u|-|t|o|o|l|s| |[|E|R|R|O|R|]|"
		echo "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ +-+-+-+-+-+-+-+"
	;;

	"merge")
		echo "+-+-+-+-+-+ +-+-+-+-+-+-+"
		echo "|m|e|r|g|e| |r|e|p|o|r|t|"
		echo "+-+-+-+-+-+ +-+-+-+-+-+-+"
	;;


	"slave")
		echo "+-+-+-+-+-+"
		echo "|s|l|a|v|e|"
		echo "+-+-+-+-+-+"
	;;


	"master")
		echo "+-+-+-+-+-+-+"
		echo "|m|a|s|t|e|r|"
		echo "+-+-+-+-+-+-+"
	;;

esac


}

banner $1