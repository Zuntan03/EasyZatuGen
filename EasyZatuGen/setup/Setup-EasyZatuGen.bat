@echo off
chcp 65001 > NUL
set CURL_CMD=C:\Windows\System32\curl.exe
@REM set PS_CMD=PowerShell -Version 5.1 -ExecutionPolicy Bypass

if not exist %~dp0..\lib\ ( mkdir %~dp0..\lib )

call %~dp0Setup-Python.bat

pushd %~dp0..\..
if not exist EasyZatuGen/src/lpw_stable_diffusion.py (
	echo %CURL_CMD% -Lo EasyZatuGen/src/lpw_stable_diffusion.py https://github.com/huggingface/diffusers/raw/6b04d61cf6c105de9f2530b5bfca2d65fc9e29d7/examples/community/lpw_stable_diffusion.py
	%CURL_CMD% -Lo EasyZatuGen/src/lpw_stable_diffusion.py https://github.com/huggingface/diffusers/raw/6b04d61cf6c105de9f2530b5bfca2d65fc9e29d7/examples/community/lpw_stable_diffusion.py
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )
)

if not exist model\ ( mkdir model )
if not exist model\real_model_N.safetensors (
	echo %CURL_CMD% -Lo model\real_model_N.safetensors https://huggingface.co/fcski/real_model_L/resolve/main/real_model_N.safetensors
	%CURL_CMD% -Lo model\real_model_N.safetensors https://huggingface.co/fcski/real_model_L/resolve/main/real_model_N.safetensors
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )
)

if not exist embedding\ ( mkdir embedding )
if not exist embedding\EasyNegative.safetensors (
	echo %CURL_CMD% -Lo embedding\EasyNegative.safetensors https://huggingface.co/datasets/gsdf/EasyNegative/resolve/main/EasyNegative.safetensors
	%CURL_CMD% -Lo embedding\EasyNegative.safetensors https://huggingface.co/datasets/gsdf/EasyNegative/resolve/main/EasyNegative.safetensors
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )
)

if not exist lora\ ( mkdir lora )
if not exist lora\flat1.safetensors (
	echo %CURL_CMD% -Lo lora\flat1.safetensors https://huggingface.co/2vXpSwA7/iroiro-lora/resolve/main/release/flat1.safetensors
	%CURL_CMD% -Lo lora\flat1.safetensors https://huggingface.co/2vXpSwA7/iroiro-lora/resolve/main/release/flat1.safetensors
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )
)
if not exist lora\flat2.safetensors (
	echo %CURL_CMD% -Lo lora\flat2.safetensors https://huggingface.co/2vXpSwA7/iroiro-lora/resolve/main/release/flat2.safetensors
	%CURL_CMD% -Lo lora\flat2.safetensors https://huggingface.co/2vXpSwA7/iroiro-lora/resolve/main/release/flat2.safetensors
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )
)
if not exist lora\flatBG.safetensors (
	echo %CURL_CMD% -Lo lora\flatBG.safetensors https://huggingface.co/2vXpSwA7/iroiro-lora/resolve/main/release/flatBG.safetensors
	%CURL_CMD% -Lo lora\flatBG.safetensors https://huggingface.co/2vXpSwA7/iroiro-lora/resolve/main/release/flatBG.safetensors
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )
)

if not exist output\ ( mkdir output )

call %~dp0Setup-Venv.bat

python -c "import tkinter" > NUL 2>&1
if %errorlevel% neq 0 (
	echo %PS_CMD% Expand-Archive -Path %~dp0tkinter-PythonSoftwareFoundationLicense.zip -DestinationPath venv -Force
	%PS_CMD% Expand-Archive -Path %~dp0tkinter-PythonSoftwareFoundationLicense.zip -DestinationPath venv -Force
)

set FFMPEG_DIR=%~dp0..\lib\ffmpeg-master-latest-win64-gpl
if not exist %FFMPEG_DIR%\ (
	echo curl -Lo %~dp0..\lib\ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
	curl -Lo %~dp0..\lib\ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

	%PS_CMD% Expand-Archive -Path %~dp0..\lib\ffmpeg.zip -DestinationPath %~dp0..\lib -Force
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

	echo del %~dp0..\lib\ffmpeg.zip
	del %~dp0..\lib\ffmpeg.zip
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )
)

if not exist venv\Scripts\ffplay.exe (
	xcopy /QY %FFMPEG_DIR%\bin\*.exe venv\Scripts\
	if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )
)

echo pip install torch==2.1.2+cu121 torchvision==0.16.2+cu121 torchaudio==2.1.2+cu121 xformers==0.0.23.post1 --index-url https://download.pytorch.org/whl/cu121
pip install torch==2.1.2+cu121 torchvision==0.16.2+cu121 torchaudio==2.1.2+cu121 xformers==0.0.23.post1 --index-url https://download.pytorch.org/whl/cu121
if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

echo pip install -r %~dp0requirements.txt
pip install -r %~dp0requirements.txt
if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

popd rem %~dp0..\..

call %~dp0Setup-StreamDiffusion.bat

call %~dp0Setup-StyleBertVITS2.bat
@REM call %~dp0Setup-BertVITS2.bat
