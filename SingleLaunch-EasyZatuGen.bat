@echo off
chcp 65001 > NUL
set CURL_CMD=C:\Windows\System32\curl.exe
pushd %~dp0
call venv\Scripts\activate.bat

set PYTHONPATH=%~dp0EasyZatuGen/lib/StreamDiffusion/src;%PYTHONPATH%

set DEF_CFG_DIR=EasyZatuGen\res\default_config
set CONFIG_URL=https://yyy.wpx.jp/EasyZatuGen/config

%CURL_CMD% -sLo %DEF_CFG_DIR%\lora_download.json %CONFIG_URL%/lora_download.json
%CURL_CMD% -sLo %DEF_CFG_DIR%\model_download.json %CONFIG_URL%/model_download.json
%CURL_CMD% -sLo %DEF_CFG_DIR%\sample.json %CONFIG_URL%/sample.json

set SAMPLE_NSFW=config\sample_nsfw.json
if exist %SAMPLE_NSFW% (
	%CURL_CMD% -sLo %SAMPLE_NSFW% %CONFIG_URL%/sample_nsfw.json
)

python EasyZatuGen\src\easy_zatu_gen.py

@REM popd rem %~dp0
