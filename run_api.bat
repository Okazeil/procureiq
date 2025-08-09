@echo off
REM run from anywhere
cd /d %~dp0
uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000