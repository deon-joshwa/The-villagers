:: run_app.bat -- launches OST.io at http://127.0.0.1:7860
@echo off
cd /d %~dp0
set HF_HOME=%~dp0hf_cache
set PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
call .venv\Scripts\activate
python app.py
