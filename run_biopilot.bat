@echo off
if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment not found. Run: py -3.13 -m venv .venv
  exit /b 1
)
call .venv\Scripts\activate.bat
streamlit run ui\app.py

