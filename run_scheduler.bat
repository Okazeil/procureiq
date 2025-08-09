@echo off
REM === Run the ProcureIQ scheduler in the background (minimized) ===
REM This script works no matter where you launch it from.

cd /d %~dp0

REM Optional: create a logs folder
if not exist logs mkdir logs

REM Tidy log name like logs\scheduler_2025-08-09_14-03.log
for /f "tokens=1-4 delims=/:. " %%a in ("%date% %time%") do (
  set _Y=%%d& set _M=%%b& set _D=%%c& set _H=%%e& set _Min=%%f
)
set LOG=logs\scheduler_%_Y%-%_M%-%_D%_%_H%-%_Min%.log

REM Ensure deps (first run only; harmless later)
python -m pip install -q requests schedule python-dotenv

REM Start minimized; keep running after you close the window
start "" /min cmd /c "python scripts\scheduler.py >> %LOG% 2>&1"
echo Scheduler started in background. Logging to %LOG%
exit /b