#!/bin/bash
if [ "$1" = "" ]; then
	port=8000
else
	port="$1"
fi
chmod +x cgi-bin/ -R
python3 -m http.server --cgi $port
