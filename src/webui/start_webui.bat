@echo off
echo Starting LLM News Thread Web UI...
echo.

cd /d "%~dp0..\.."
call virtualenv\Scripts\python.exe src\webui\run.py

pause
