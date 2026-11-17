:: run_app.bat -- launches YuE-Studio at http://127.0.0.1:7860
@echo off
cd /d %~dp0
set HF_HOME=%~dp0hf_cache
call .venv\Scripts\activate
python app.py
