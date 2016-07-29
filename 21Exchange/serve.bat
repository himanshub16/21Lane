@echo off
if [%1] == [] (
	set port=8000
) else (
	set port=%1
)

start /wait python http.server --cgi %port%
exit
