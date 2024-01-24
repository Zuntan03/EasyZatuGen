@echo off
chcp 65001 > NUL
pushd %~dp0
set PS_CMD=PowerShell -Version 5.1 -ExecutionPolicy Bypass

set CURL_CMD=C:\Windows\System32\curl.exe
if not exist %CURL_CMD% (
	echo [ERROR] %CURL_CMD% が見つかりません。
	pause & popd & exit /b 1
)

echo 以下の配布元から関連ファイルをダウンロードして使用します（URL を Ctrl + クリックで開けます）。
echo.
echo https://www.python.org/
echo https://github.com/pypa/get-pip/
echo https://github.com/BtbN/FFmpeg-Builds/
echo.
echo https://github.com/casper-hansen/AutoAWQ/
echo https://huggingface.co/TheBloke/calm2-7B-chat-AWQ/
echo.
echo https://github.com/litagin02/Style-Bert-VITS2/
echo https://huggingface.co/litagin/style_bert_vits2_jvnv/
@REM echo https://huggingface.co/litagin/style_bert_vits2_okiba/
@REM echo https://huggingface.co/litagin/style_bert_vits2_nsfw/
echo.
echo https://github.com/cumulo-autumn/StreamDiffusion/
echo https://huggingface.co/fcski/real_model_L/
echo https://huggingface.co/datasets/gsdf/EasyNegative/
echo echo https://huggingface.co/2vXpSwA7/iroiro-lora/
echo.
echo よろしいですか？ [y/n]
set /p YES_OR_NO=
if /i not "%YES_OR_NO%" == "y" ( popd & exit /b 1 )

set EASY_ZATU_GEN_DIR=EasyZatuGen-main

if not exist EasyZatuGen\lib\ ( mkdir EasyZatuGen\lib )

%CURL_CMD% -Lo EasyZatuGen\lib\EasyZatuGen.zip^
	https://github.com/Zuntan03/EasyZatuGen/archive/refs/heads/main.zip
if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

%PS_CMD% Expand-Archive -Path EasyZatuGen\lib\EasyZatuGen.zip -DestinationPath EasyZatuGen\lib -Force
if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

del EasyZatuGen\lib\EasyZatuGen.zip
if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

xcopy /QSY .\EasyZatuGen\lib\%EASY_ZATU_GEN_DIR%\ .

copy /Y .\EasyZatuGen\setup\Install-EasyZatuGen.bat .\Update.bat

call EasyZatuGen\setup\Setup-EasyZatuGen.bat

start EasyZatuGen.bat

popd rem %~dp0..
