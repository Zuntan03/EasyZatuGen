@echo off
chcp 65001 > NUL
set PS_CMD=PowerShell -Version 5.1 -ExecutionPolicy Bypass
set CURL_CMD=C:\Windows\System32\curl.exe
set PYTHON_DIR=%~dp0..\lib\python
set PYTHON_CMD=%PYTHON_DIR%\python.exe

if not exist %CURL_CMD% (
	echo [ERROR] %CURL_CMD% が見つかりません。
	pause & exit /b 1
)


if not exist %PYTHON_DIR%\ (
	echo https://www.python.org/
	echo https://github.com/pypa/get-pip
	mkdir %PYTHON_DIR%

	echo %CURL_CMD% -o %~dp0python.zip https://www.python.org/ftp/python/3.10.6/python-3.10.6-embed-amd64.zip
	%CURL_CMD% -o %~dp0python.zip https://www.python.org/ftp/python/3.10.6/python-3.10.6-embed-amd64.zip
	if %errorlevel% neq 0 ( pause & exit /b %errorlevel% )

	echo %PS_CMD% Expand-Archive -Path %~dp0python.zip -DestinationPath %PYTHON_DIR%
	%PS_CMD% Expand-Archive -Path %~dp0python.zip -DestinationPath %PYTHON_DIR%
	if %errorlevel% neq 0 ( pause & exit /b %errorlevel% )

	echo del %~dp0python.zip
	del %~dp0python.zip
	if %errorlevel% neq 0 ( pause & exit /b %errorlevel% )

	echo %PS_CMD% "&{(Get-Content '%PYTHON_DIR%/python310._pth') -creplace '#import site', 'import site' | Set-Content '%PYTHON_DIR%/python310._pth' }"
	%PS_CMD% "&{(Get-Content '%PYTHON_DIR%/python310._pth') -creplace '#import site', 'import site' | Set-Content '%PYTHON_DIR%/python310._pth' }"
	if %errorlevel% neq 0 ( pause & exit /b %errorlevel% )

	echo %CURL_CMD% -o %PYTHON_DIR%\get-pip.py https://bootstrap.pypa.io/get-pip.py
	@REM プロキシ環境用コマンド。動作未確認。
	@REM %CURL_CMD% -o %PYTHON_DIR%\get-pip.py https://bootstrap.pypa.io/get-pip.py --proxy="PROXY_SERVER:PROXY_PORT"
	%CURL_CMD% -o %PYTHON_DIR%\get-pip.py https://bootstrap.pypa.io/get-pip.py
	if %errorlevel% neq 0 (
		echo プロキシ環境によりインストールに失敗した可能性があります。
		echo パスの通った Python を用意して、Setup-Venv.bat を書き換えてインストールを再実行してください。
		pause & exit /b %errorlevel%
	)

	echo %PYTHON_CMD% %PYTHON_DIR%\get-pip.py --no-warn-script-location
	%PYTHON_CMD% %PYTHON_DIR%\get-pip.py --no-warn-script-location
	if %errorlevel% neq 0 ( pause & exit /b %errorlevel% )

	echo %PYTHON_CMD% -m pip install virtualenv --no-warn-script-location
	%PYTHON_CMD% -m pip install virtualenv --no-warn-script-location
	if %errorlevel% neq 0 ( pause & exit /b %errorlevel% )
)
