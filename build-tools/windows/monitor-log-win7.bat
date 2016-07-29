@ECHO OFF
PowerShell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-Content log.txt -Wait"
PAUSE
