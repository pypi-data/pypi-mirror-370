@echo off
setlocal enabledelayedexpansion

:: Check for silent mode parameter
set "SILENT_MODE=0"
if /i "%1"=="/silent" set "SILENT_MODE=1"

echo source_folder=%source_folder%
echo target_folder=%target_folder%
echo local_storage_path=%local_storage_path%
echo python_script=%python_script%
echo config_file=%config_file%
echo.

:: Expects these to be set by caller (MediBot.bat):
:: %source_folder% %target_folder% %python_script% %config_file% %local_storage_path%

:: Validate JSON update script path or prompt for alternate
if not exist "%python_script%" (
  echo.
  echo Warning: Python script for JSON updates not found at: %python_script%
  echo.
  set /p provide_alt_json="Enter 'Y' to provide alternate path, or any other key to continue: "
  if /i "!provide_alt_json!"=="Y" (
    echo.
    echo Please enter the full path to your update_json.py file.
    echo Example: C:\MediBot\scripts\update_json.py
    echo Example with spaces: "G:\My Drive\MediBot\scripts\update_json.py"
    echo.
    set /p alt_json_path="Enter JSON update script path: "
    set "alt_json_path=!alt_json_path:"=!"
    if exist "!alt_json_path!" (
      echo JSON update script found at: !alt_json_path!
      set "python_script=!alt_json_path!"
    ) else (
      echo JSON update script not found at: !alt_json_path!
      echo Continuing without JSON update script...
    )
  ) else (
    echo Continuing without JSON update script...
  )
)

:: Move any CSVs from local storage to source folder
if defined local_storage_path if exist "%local_storage_path%\*.csv" (
  echo Checking for new CSV files in local storage...
  for %%f in ("%local_storage_path%\*.csv") do (
    echo Moving %%f to %source_folder%...
    move "%%f" "%source_folder%"
  )
)

:: Timestamp for new filename
for /f "tokens=1-5 delims=/: " %%a in ('echo %time%') do (
  set "hour=%%a"
  set "minute=%%b"
  set "second=%%c"
)
for /f "tokens=2-4 delims=/ " %%a in ('echo %date%') do (
  set "day=%%a"
  set "month=%%b"
  set "year=%%c"
)
set "timestamp=!year!!month!!day!_!hour!!minute!"

:: Find most recent CSV in source folder
set "latest_csv="
for /f "delims=" %%a in ('dir /b /a-d /o-d "%source_folder%\*.csv"') do (
  set "latest_csv=%%a"
  goto :have_csv
)
echo No CSV files found in %source_folder%.
if "%SILENT_MODE%"=="0" set /p _="Press Enter to continue..."
exit /b 0

:have_csv
echo Validating latest CSV with config file...
if exist "%python_script%" if exist "%config_file%" (
  for /f "delims=" %%a in ('python "%python_script%" "%config_file%"') do set "current_csv=%%a"
  for %%f in ("!current_csv!") do set "current_csv_name=%%~nxf"
  for %%f in ("%target_folder%\!latest_csv!") do set "latest_csv_name=%%~nxf"
  if not "!current_csv_name!"=="!latest_csv_name!" (
    echo Current CSV: !current_csv_name!
    echo Latest CSV: !latest_csv_name!
    set /p update_choice="Update config to latest CSV? (Y/N): "
    if /i "!update_choice!"=="Y" (
      python "%python_script%" "%config_file%" "%target_folder%\!latest_csv!"
    )
  )
)

move "%source_folder%\!latest_csv!" "%target_folder%\SX_CSV_!timestamp!.csv"
set "new_csv_path=%target_folder%\SX_CSV_!timestamp!.csv"
echo Processing CSV...
if exist "%python_script%" if exist "%config_file%" (
  python "%python_script%" "%config_file%" "!new_csv_path!"
)
echo CSV Processor Complete.
if "%SILENT_MODE%"=="0" set /p _="Press Enter to continue..."
exit /b 0


