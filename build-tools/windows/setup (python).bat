@echo off
where python
cls
if errorlevel 1 (
	echo Python is not installed on your system.
	echo Installing Python...
	START /WAIT python-3.5.2.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
	resetvars.bat
) else (
	where pip
	cls 
	if errorlevel 1 (
		echo Missing pip.
		echo Make sure your Python installation is complete.
	) else (
		start /wait python validator.py install
		echo Installing required modules
		pip install -r requirements.txt --user
		REM Script from : https://github.com/npocmaka/batch.scripts/blob/master/hybrids/jscript/shortcutJS.bat
		create_shortcut.bat -linkfile "%userprofile%\Desktop\21Lane.lnk" -target "%userprofile%\21Lane\21lane.bat" -description "21Lane (FTP based file sharing)" -iconlocation "%userprofile%\21Lane\icons\favicon.ico" -workingdirectory "%userprofile%\21Lane\""
		create_shortcut.bat -linkfile "%appdata%\Microsoft\Windows\Start Menu\21Lane.lnk" -target "%userprofile%\21Lane\21lane.bat" -description "21Lane (FTP based file sharing)" -iconlocation "%userprofile%\21Lane\icons\favicon.ico" -workingdirectory "%userprofile%\21Lane\"
		echo "Setup complete. Shortcuts have been created on Desktop and Start Menu"
		pause
	)
)
