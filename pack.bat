@echo off
setlocal
pushd "%~dp0" || exit /b 1

if defined BENA_PYTHON goto python_ready
if exist "%~dp0.venv-build\Scripts\python.exe" (
    set "BENA_PYTHON=%~dp0.venv-build\Scripts\python.exe"
) else (
    set "BENA_PYTHON=python"
)

:python_ready
set "PYINSTALLER_CONFIG_DIR=%~dp0build\.pyinstaller-cache"
"%BENA_PYTHON%" -X utf8 -c "import PyInstaller" >nul 2>nul
if errorlevel 1 (
    echo Python or PyInstaller is unavailable in the selected environment.
    echo Install the build dependencies with:
    echo "%BENA_PYTHON%" -m pip install -r requirements-build.txt
    goto failed
)

"%BENA_PYTHON%" -X utf8 -m PyInstaller --noconfirm --onefile --name main --icon "icon\icon.ico" main.py
if errorlevel 1 goto failed

"%BENA_PYTHON%" -X utf8 packer.py
if errorlevel 1 goto failed

popd
if /i not "%~1"=="--no-pause" pause
endlocal
exit /b 0

:failed
echo Packaging failed. Build files and previous packages have been kept.
popd
if /i not "%~1"=="--no-pause" pause
endlocal
exit /b 1
