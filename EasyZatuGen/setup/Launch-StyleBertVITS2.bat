@echo off
chcp 65001 > NUL
pushd %~dp0..\lib\Style-Bert-VITS2

call venv\Scripts\activate.bat
if %errorlevel% neq 0 ( pause & exit /b %errorlevel% )

echo python server_fastapi.py
python server_fastapi.py
if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

popd rem %~dp0..\lib\Style-Bert-VITS2
