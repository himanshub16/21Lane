#!/bin/bash

# Linux distinguishes Python3 and Python2
var="$(which python3)"
if [ "$var" = "" ]; then
	echo "Python3 is not installed."
	echo "Make sure Python 3.5.x is installed on your system and configured."
	read -n1 -p "Press any key to exit... "
	exit 1
else
	var="$(which pip3)"
	if [ "$var" = "" ]; then
		echo "pip3 is missing."
		echo "Make sure your Python installation is complete."
		read -n1 -p "Press any key to exit... "
		exit 1
	else
		python3 setup.py install 
		# install required modules
		pip3 install PyQt5==5.6
		pip3 install requests, tinydb, json, deepcopy
	fi
fi
read -n1 -p "Press any key to exit... "
