@echo off
where python
cls
if errorlevel 1 (
	echo Python is not installed on your system.
	echo Make sure Python 3.5.x is installed and PATH is configured.
	pause
) else (
	where pip
	cls 
	if errorlevel 1 (
		echo Missing pip.
		echo Make sure your Python installation is complete.
	) else (
		start /wait python setup.py install
		echo Installing required modules
		REM pip install PyQt5==5.6
		REM pip install requests, tinydb, json, deepcopy
		pip install -r requirements.txt
		pause
	)
)