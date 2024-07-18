@echo off

cd /d %~dp0

start cmd /k "streamlit run main.py"