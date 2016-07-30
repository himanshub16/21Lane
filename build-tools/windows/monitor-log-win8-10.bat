@ECHO OFF
PowerShell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-Content log.txt -Wait -Tail 5"
PAUSE
