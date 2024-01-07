@echo off
chcp 65001 > NUL

call %~dp0SingleLaunch-StyleBertVITS2.bat

start "EasyZatuGen ログ" %~dp0SingleLaunch-EasyZatuGen.bat
