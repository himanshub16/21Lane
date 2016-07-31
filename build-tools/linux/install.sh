#!/bin/bash

# Linux distinguishes Python3 and Python2
var="$(which python3)"
if [ "$var" = "" ]; then
	echo "Python3 is not installed."
	read -pr "Do you want to install Python3 ? (y/n) " pythonresp
	if [ "$pythonresp" = "y"] || [ "$pythonresp" = "Y" ]; then
		sudo apt-get install python3.5
	else
		echo "Make sure Python 3.5.x is installed on your system and configured."
		read -n1 -p "Press any key to exit... "
		exit 1
	fi
else
	var="$(which pip3)"
	if [ "$var" = "" ]; then
		echo "pip3 is missing."
		read -pr "Do you want to install pip ? (y/n) " pipresp
		if [ "$pipresp" = "y"] || [ "$pipresp" = "Y" ]; then
			sudo apt-get install pip3
		else
			echo "Make sure your Python installation is complete."
			read -n1 -p "Press any key to exit... "
			exit 1
		fi
	else
		python3 setup.py install && pip3 install -r requirements.txt
		# install required modules
		# pip3 install PyQt5==5.6
		# pip3 install requests, tinydb, json, deepcopy
		# pip3 install -r requirements.txt
	fi
fi
echo "Setup complete. An entry has been made to the applications menu."
read -n1 -p "Press any key to exit... "
