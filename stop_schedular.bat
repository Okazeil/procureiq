@echo off
echo Stopping ProcureIQ scheduler...
for /f "tokens=2" %%P in ('tasklist /FI "IMAGENAME eq python.exe" /V ^| find /I "scripts\\scheduler.py"') do (
  echo Killing PID %%P
  taskkill /PID %%P /F >nul 2>&1
)
echo Done. (If you still see it in Task Manager, stop the python.exe tied to scheduler.py)
exit /b