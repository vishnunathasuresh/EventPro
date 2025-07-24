@echo off
cd /d %~dp0

REM Start a new Command Prompt that activates the venv and runs Streamlit
start cmd /k ".\.venv\Scripts\activate.bat && streamlit run main.py"
