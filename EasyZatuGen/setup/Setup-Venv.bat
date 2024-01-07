@echo off
chcp 65001 > NUL

set VENV_CMD=%~dp0..\lib\python\python.exe -m virtualenv --copies

@REM パスを通してあるインストール済みの Python を使う場合は、次の行の先頭 @REM を削除します。
@REM set VENV_CMD=python -m venv

if not exist venv\ (
	echo %VENV_CMD% venv
	%VENV_CMD% venv
	if %errorlevel% neq 0 ( pause & exit /b %errorlevel% )
)

call venv\Scripts\activate.bat
if %errorlevel% neq 0 ( pause & exit /b %errorlevel% )

python -m pip install -q --upgrade pip
if %errorlevel% neq 0 ( pause & exit /b %errorlevel% )
