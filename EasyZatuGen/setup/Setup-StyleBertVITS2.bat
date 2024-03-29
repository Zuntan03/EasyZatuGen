@echo off
chcp 65001 > NUL
pushd %~dp0..\lib
set PS_CMD=PowerShell -Version 5.1 -ExecutionPolicy Bypass
set CURL_CMD=C:\Windows\System32\curl.exe

@REM 2024-01-15
set STYLE_BERT_VITS2_REV=972ec0e627976e928428e1902334a2dd591477ea

if not exist Style-Bert-VITS2-%STYLE_BERT_VITS2_REV%\ (
	%CURL_CMD% -Lo Style-Bert-VITS2.zip https://github.com/litagin02/Style-Bert-VITS2/archive/%STYLE_BERT_VITS2_REV%.zip
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

	%PS_CMD% Expand-Archive -Path Style-Bert-VITS2.zip -DestinationPath . -Force
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

	del Style-Bert-VITS2.zip
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

	xcopy /QSY Style-Bert-VITS2-%STYLE_BERT_VITS2_REV%\*.* Style-Bert-VITS2\
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )
)
popd rem %~dp0..\lib

pushd %~dp0..\lib\Style-Bert-VITS2
call %~dp0Setup-Venv.bat

echo pip install -r requirements.txt
pip install -r requirements.txt
if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

python initialize.py
if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

echo copy /Y %~dp0StyleBertVITS2-config.yml config.yml
copy /Y %~dp0StyleBertVITS2-config.yml config.yml
if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

set DOWNLOAD_DST=model_assets

@REM 2024-01-15 2024-01-24 公開停止
@REM call :DOWNLOAD Hilja Hilja_e300_s26480.safetensors^
@REM 	https://huggingface.co/litagin/style_bert_vits2_okiba/resolve/main/model_assets/Hilja/
@REM if %errorlevel% neq 0 ( popd & exit /b %errorlevel% )

@REM call :DOWNLOAD Ilona Ilona_e233_s18000.safetensors^
@REM 	https://huggingface.co/litagin/style_bert_vits2_okiba/resolve/main/model_assets/Ilona-fixed/
@REM if %errorlevel% neq 0 ( popd & exit /b %errorlevel% )

@REM call :DOWNLOAD Kaisa Kaisa_e265_s27000.safetensors^
@REM 	https://huggingface.co/litagin/style_bert_vits2_okiba/resolve/main/model_assets/Kaisa-fixed/
@REM if %errorlevel% neq 0 ( popd & exit /b %errorlevel% )

@REM call :DOWNLOAD Leena Leena_e181_s13000.safetensors^
@REM 	https://huggingface.co/litagin/style_bert_vits2_okiba/resolve/main/model_assets/Leena/
@REM if %errorlevel% neq 0 ( popd & exit /b %errorlevel% )

@REM call :DOWNLOAD Liisa Liisa2-g2p_e221_s19000.safetensors^
@REM 	https://huggingface.co/litagin/style_bert_vits2_okiba/resolve/main/model_assets/Liisa-fixed/
@REM if %errorlevel% neq 0 ( popd & exit /b %errorlevel% )

@REM call :DOWNLOAD Hilja-nsfw Hilja-nsfw_e300_s3900.safetensors^
@REM 	https://huggingface.co/litagin/style_bert_vits2_nsfw/resolve/main/model_assets/Hilja-nsfw/
@REM if %errorlevel% neq 0 ( popd & exit /b %errorlevel% )

@REM call :DOWNLOAD Ilona-nsfw Ilona-nsfw_e400_s7200.safetensors^
@REM 	https://huggingface.co/litagin/style_bert_vits2_nsfw/resolve/main/model_assets/Ilona-nsfw/
@REM if %errorlevel% neq 0 ( popd & exit /b %errorlevel% )

@REM call :DOWNLOAD Kaisa-nsfw Kaisa-nsfw_e189_s13000.safetensors^
@REM 	https://huggingface.co/litagin/style_bert_vits2_nsfw/resolve/main/model_assets/Kaisa-nsfw/
@REM if %errorlevel% neq 0 ( popd & exit /b %errorlevel% )

@REM call :DOWNLOAD Liisa-nsfw Liisa-nsfw_e219_s14000.safetensors^
@REM 	https://huggingface.co/litagin/style_bert_vits2_nsfw/resolve/main/model_assets/Liisa-nsfw/
@REM if %errorlevel% neq 0 ( popd & exit /b %errorlevel% )

popd rem %~dp0..\lib\Style-Bert-VITS2
exit /b 0

:DOWNLOAD
set NAME=%1
set FILE_NAME=%2
set BASE_URL=%3

if not exist %DOWNLOAD_DST%\%NAME%\ (
	mkdir %DOWNLOAD_DST%\%NAME%\
	pushd %DOWNLOAD_DST%\%NAME%\

	echo %CURL_CMD% -Lo %FILE_NAME% %BASE_URL%%FILE_NAME%
	%CURL_CMD% -Lo %FILE_NAME% %BASE_URL%%FILE_NAME%
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )
	timeout /t 1 /nobreak > NUL

	echo %CURL_CMD% -Lo config.json %BASE_URL%config.json
	%CURL_CMD% -Lo config.json %BASE_URL%config.json
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )
	timeout /t 1 /nobreak > NUL

	echo %CURL_CMD% -Lo style_vectors.npy %BASE_URL%style_vectors.npy
	%CURL_CMD% -Lo style_vectors.npy %BASE_URL%style_vectors.npy
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )
	timeout /t 1 /nobreak > NUL

	popd rem %DOWNLOAD_DST%\%NAME%\
)

exit /b 0
