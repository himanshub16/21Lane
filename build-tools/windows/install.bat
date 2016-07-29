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
		pip install -r requirements.txt
		REM Don't create desktop shortcut .. execution issues
		REM cscript create_shortcut.vbs
		REM del create_shortcut.vbs
		pause
	)
)