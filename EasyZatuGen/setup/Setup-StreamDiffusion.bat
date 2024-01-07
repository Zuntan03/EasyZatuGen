@echo off
chcp 65001 > NUL
pushd %~dp0..\lib
set PS_CMD=PowerShell -Version 5.1 -ExecutionPolicy Bypass
set CURL_CMD=C:\Windows\System32\curl.exe

@REM 2023-12-28
set STREAM_DIFFUSION_REV=59de06fb41eea17785d9d5aa653118cb441f5727

if not exist StreamDiffusion-%STREAM_DIFFUSION_REV%\ (
	echo %CURL_CMD% -Lo StreamDiffusion.zip https://github.com/cumulo-autumn/StreamDiffusion/archive/%STREAM_DIFFUSION_REV%.zip
	%CURL_CMD% -Lo StreamDiffusion.zip https://github.com/cumulo-autumn/StreamDiffusion/archive/%STREAM_DIFFUSION_REV%.zip
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

	%PS_CMD% Expand-Archive -Path StreamDiffusion.zip -DestinationPath . -Force
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

	del StreamDiffusion.zip
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

	xcopy /QSY StreamDiffusion-%STREAM_DIFFUSION_REV%\*.* StreamDiffusion\
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )
)

popd rem %~dp0..\lib
