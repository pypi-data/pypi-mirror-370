::MediBot.bat - Streamlined version with coordinated debug system
@echo off
setlocal enabledelayedexpansion

:: Clear screen before launcher header
cls

:: Launcher header
echo ========================================
echo           MediCafe Launcher
echo ========================================
echo.

:: Hidden debug access: 1-second Enter-to-open gate; otherwise start normal mode
echo Press Enter within 1 second to open Debug Options... (otherwise starting Normal Mode)
rem Prefer timeout for key-break; fall back to ping if unavailable
where timeout >nul 2>&1
if errorlevel 1 (
    rem Fallback: simple 1-second delay (no key detection on XP fallback)
    ping -n 2 127.0.0.1 >nul
    goto start_normal_mode
) else (
    timeout /t 1 >nul 2>nul
    if errorlevel 1 goto show_debug_menu
    goto start_normal_mode
)

:show_debug_menu
echo.
echo Choose your mode:
echo 1. Normal Mode - Production
echo 2. Debug Mode - Full diagnostics (Interactive)
echo 3. Debug Mode - Full diagnostics (Non-Interactive)
echo.
set /p debug_choice="Enter your choice (1-3): "

if "!debug_choice!"=="1" goto start_normal_mode
if "!debug_choice!"=="2" goto start_debug_interactive
if "!debug_choice!"=="3" goto start_debug_noninteractive
goto start_normal_mode

:start_debug_interactive
echo.
echo ========================================
echo        DEBUG MODE (INTERACTIVE)
echo ========================================
echo Running full diagnostic suite...
set "MEDICAFE_IMPORT_DEBUG=1"
set "MEDICAFE_IMPORT_STRICT=0"
echo.
set "SKIP_CLS_AFTER_DEBUG=1"
call "%~dp0full_debug_suite.bat" /interactive
echo.
goto normal_mode

:start_debug_noninteractive
echo.
echo ========================================
echo     DEBUG MODE (NON-INTERACTIVE)
echo ========================================
echo Running full diagnostic suite...
set "MEDICAFE_IMPORT_DEBUG=1"
set "MEDICAFE_IMPORT_STRICT=0"
echo.
set "SKIP_CLS_AFTER_DEBUG=1"
call "%~dp0full_debug_suite.bat"
echo.
goto normal_mode

:start_normal_mode
echo Starting Normal Mode...
set "MEDICAFE_IMPORT_DEBUG=0"
set "MEDICAFE_IMPORT_STRICT=1"
goto normal_mode

:normal_mode
:: Normal production mode - streamlined without excessive debug output
if not defined SKIP_CLS_AFTER_DEBUG cls
set "SKIP_CLS_AFTER_DEBUG="
echo ========================================
echo           MediBot Starting
echo ========================================
echo.

:: Define paths with local fallbacks for F: drive dependencies
set "source_folder=C:\MEDIANSI\MediCare"
set "target_folder=C:\MEDIANSI\MediCare\CSV"
set "python_script=C:\Python34\Lib\site-packages\MediBot\update_json.py"
set "python_script2=C:\Python34\Lib\site-packages\MediBot\Medibot.py"
set "medicafe_package=medicafe"

:: Absolute paths for updater scripts
set "script_dir=%~dp0"
set "upgrade_medicafe_local=%script_dir%update_medicafe.py"
set "upgrade_medicafe_legacy=F:\Medibot\update_medicafe.py"

:: Storage and config paths with local fallbacks
set "local_storage_legacy=F:\Medibot\DOWNLOADS"
set "local_storage_local=MediBot\DOWNLOADS"
set "config_file_legacy=F:\Medibot\json\config.json"
set "config_file_local=MediBot\json\config.json"
set "temp_file_legacy=F:\Medibot\last_update_timestamp.txt"
set "temp_file_local=MediBot\last_update_timestamp.txt"

:: Ensure F: has the latest updater when available; prefer F: when present
if exist "F:\" (
    if not exist "F:\Medibot" mkdir "F:\Medibot" 2>nul
    if exist "%upgrade_medicafe_local%" (
        copy /Y "%upgrade_medicafe_local%" "%upgrade_medicafe_legacy%" >nul 2>&1
    )
)

:: Preference order: 1) F: drive updater, 2) Local updater
if exist "%upgrade_medicafe_legacy%" (
    set "upgrade_medicafe=%upgrade_medicafe_legacy%"
    set "use_local_update=0"
) else if exist "%upgrade_medicafe_local%" (
    set "upgrade_medicafe=%upgrade_medicafe_local%"
    set "use_local_update=1"
) else (
    set "upgrade_medicafe="
)

:: Determine which paths to use based on availability
if exist "F:\Medibot" (
    set "local_storage_path=%local_storage_legacy%"
    set "config_file=%config_file_legacy%"
    set "temp_file=%temp_file_legacy%"
    
    :: Only use F: drive update script if local doesn't exist
    if "!use_local_update!"=="0" (
        if exist "%upgrade_medicafe_legacy%" (
            set "upgrade_medicafe=%upgrade_medicafe_legacy%"
        )
    )
) else (
    set "local_storage_path=%local_storage_local%"
    set "config_file=%config_file_local%"
    set "temp_file=%temp_file_local%"
    :: Ensure local directories exist
    if not exist "MediBot\json" mkdir "MediBot\json" 2>nul
    if not exist "MediBot\DOWNLOADS" mkdir "MediBot\DOWNLOADS" 2>nul
)

set "firefox_path=C:\Program Files\Mozilla Firefox\firefox.exe"
set "claims_status_script=..\MediLink\MediLink_ClaimStatus.py"
set "deductible_script=..\MediLink\MediLink_Deductible.py"
set "package_version="
set PYTHONWARNINGS=ignore
set "PRES_WARN_UPDATE_SCRIPT=0"
set "PRES_WARN_NO_INTERNET=0"

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please run in Debug Mode to diagnose Python issues.
    pause
    exit /b 1
)

:: Check if critical directories exist
if not exist "%source_folder%" (
    echo [WARNING] Source folder not found at: %source_folder%
    set /p provide_alt_source="Enter 'Y' to provide alternate path, or any other key to continue: "
    if /i "!provide_alt_source!"=="Y" (
        set /p alt_source_folder="Enter the alternate source folder path: "
        if not "!alt_source_folder!"=="" set "source_folder=!alt_source_folder!"
    )
)

if not exist "%target_folder%" (
    mkdir "%target_folder%" 2>nul
)

:: Check if the MediCafe package is installed
python -c "import pkg_resources; print('MediCafe=='+pkg_resources.get_distribution('medicafe').version)" 2>nul
if errorlevel 1 (
    echo [WARNING] MediCafe package not found. Attempting to install...
    python -m pip install medicafe --upgrade
    if errorlevel 1 (
        echo [ERROR] Failed to install MediCafe package.
        echo Please run in Debug Mode to diagnose package issues.
        pause
        exit /b 1
    )
)

:: Determine installed MediCafe version
set "package_version="
set "medicafe_version="
python -c "import pkg_resources; print('MediCafe=='+pkg_resources.get_distribution('medicafe').version)" > temp.txt 2>nul
set /p package_version=<temp.txt
if exist temp.txt del temp.txt
if not defined package_version (
    rem Fallback: try importing MediCafe and reading __version__
    python -c "import sys;\ntry:\n import MediCafe;\n print('MediCafe=='+getattr(MediCafe, '__version__','unknown'))\nexcept Exception as e:\n print('')" > temp.txt 2>nul
    set /p package_version=<temp.txt
    if exist temp.txt del temp.txt
)
if defined package_version (
    for /f "tokens=2 delims==" %%a in ("%package_version%") do set "medicafe_version=%%a"
) else (
    set "medicafe_version=unknown"
)

:: Check for internet connectivity
ping -n 1 google.com >nul 2>&1
if errorlevel 1 (
    set "internet_available=0"
    set "PRES_WARN_NO_INTERNET=1"
) else (
    set "internet_available=1"
    echo Internet connection detected.
)

:: Common pre-menu setup
echo Setting up the environment...
if not exist "%config_file%" (
    echo Configuration file missing.
    echo.
    echo Expected configuration file path: %config_file%
    echo.
    echo Would you like to provide an alternate path for the configuration file?
    set /p provide_alt="Enter 'Y' to provide alternate path, or any other key to exit: "
    if /i "!provide_alt!"=="Y" (
        echo.
        echo Please enter the full path to your configuration file.
        echo Example: C:\MediBot\config\config.json
        echo Example with spaces: "G:\My Drive\MediBot\config\config.json"
        echo.
        echo Note: If your path contains spaces, please include quotes around the entire path.
        echo.
        set /p alt_config_path="Enter configuration file path: "
        :: Remove any surrounding quotes from user input and re-add them for consistency
        set "alt_config_path=!alt_config_path:"=!"
        if exist "!alt_config_path!" (
            echo Configuration file found at: !alt_config_path!
            set "config_file=!alt_config_path!"
            goto config_check_complete
        ) else (
            echo Configuration file not found at: !alt_config_path!
            echo.
            set /p retry="Would you like to try another path? (Y/N): "
            if /i "!retry!"=="Y" (
                goto retry_config_path
            ) else (
                goto end_script
            )
        )
    ) else (
        goto end_script
    )
) else (
    goto config_check_complete
)

:retry_config_path
echo.
echo Please enter the full path to your configuration file.
echo Example: C:\MediBot\config\config.json
echo Example with spaces: "G:\My Drive\MediBot\config\config.json"
echo.
echo Note: If your path contains spaces, please include quotes around the entire path.
echo.
set /p alt_config_path="Enter configuration file path: "
:: Remove any surrounding quotes from user input and re-add them for consistency
set "alt_config_path=!alt_config_path:"=!"
if exist "!alt_config_path!" (
    echo Configuration file found at: !alt_config_path!
    set "config_file=!alt_config_path!"
) else (
    echo Configuration file not found at: !alt_config_path!
    echo.
    set /p retry="Would you like to try another path? (Y/N): "
    if /i "!retry!"=="Y" (
        goto retry_config_path
    ) else (
        goto end_script
    )
)

:config_check_complete

:: Check if the file exists and attempt to copy it to the local directory
echo Checking for the update script...
ping -n 2 127.0.0.1 >nul

:: Continue with existing logic but with enhanced error reporting
:: First check if we already have it locally
if exist "%upgrade_medicafe_local%" (
    echo Found update_medicafe.py in local directory. No action needed.
    ping -n 2 127.0.0.1 >nul
) else (
    if exist "C:\Python34\Lib\site-packages\MediBot\update_medicafe.py" (
        echo Found update_medicafe.py in site-packages. Copying to local directory...
        ping -n 2 127.0.0.1 >nul
        :: Ensure MediBot directory exists
        if not exist "MediBot" mkdir "MediBot"
        copy "C:\Python34\Lib\site-packages\MediBot\update_medicafe.py" "%upgrade_medicafe_local%" >nul 2>&1
        if %errorlevel% neq 0 (
            echo Copy to local directory failed. Error code: %errorlevel%
            echo [DIAGNOSTIC] Attempting copy to F: drive - detailed error reporting
            ping -n 2 127.0.0.1 >nul
            :: Ensure F:\Medibot directory exists (only if F: drive is accessible)
            if exist "F:\" (
                if not exist "F:\Medibot" (
                    echo [DIAGNOSTIC] Creating F:\Medibot directory...
                    mkdir "F:\Medibot" 2>nul
                    if not exist "F:\Medibot" (
                        echo [ERROR] Failed to create F:\Medibot - Permission denied or read-only drive
                    )
                )
                if exist "F:\Medibot" (
                    echo [DIAGNOSTIC] Attempting file copy to F:\Medibot...
                    copy "C:\Python34\Lib\site-packages\MediBot\update_medicafe.py" "%upgrade_medicafe_legacy%" 2>nul
                    if %errorlevel% neq 0 (
                        echo [ERROR] Copy to F:\Medibot failed with error code: %errorlevel%
                        echo [ERROR] Possible causes:
                        echo    - Permission denied [insufficient write access]
                        echo    - Disk full
                        echo    - File locked by another process
                        echo    - Antivirus blocking the operation
                    ) else (
                        echo [SUCCESS] File copied to F:\Medibot successfully
                    )
                )
            ) else (
                echo [ERROR] F: drive not accessible - skipping F: drive copy attempt
            )
        ) else (
            echo File copied to local directory successfully.
            ping -n 2 127.0.0.1 >nul
        )
    ) else (
        if exist "%upgrade_medicafe_legacy%" (
            echo Found update_medicafe.py in legacy F: drive location.
            echo [DIAGNOSTIC] Verifying F: drive file accessibility...
            type "%upgrade_medicafe_legacy%" | find "#update_medicafe.py" >nul 2>&1
            if %errorlevel% equ 0 (
                echo [OK] F: drive file is accessible and readable
            ) else (
                echo [ERROR] F: drive file exists but cannot be read [permission/lock issue]
            )
            ping -n 2 127.0.0.1 >nul
        ) else (
            echo update_medicafe.py not detected in any known location.
            set "PRES_WARN_UPDATE_SCRIPT=1"
            echo.
            echo Checked locations:
            echo   - Site-packages: C:\Python34\Lib\site-packages\MediBot\update_medicafe.py
            echo   - Local: %upgrade_medicafe_local%
            echo   - Legacy: %upgrade_medicafe_legacy%
            echo.
            echo [DIAGNOSTIC] Current working directory:
            cd
            echo [DIAGNOSTIC] Current directory contents:
            dir /b
            echo.
            echo [DIAGNOSTIC] MediBot directory contents:
            dir /b MediBot\ 2>nul || echo MediBot directory not found
            echo.
            echo Continuing without update script...
            ping -n 2 127.0.0.1 >nul
        )
    )
)

:: Main menu
:main_menu
cls
echo Version: %medicafe_version%
echo --------------------------------------------------------------
echo              .//*  Welcome to MediCafe  *\\. 
echo --------------------------------------------------------------
echo. 

:: Preserve important warnings/errors from boot sequence
if "%PRES_WARN_UPDATE_SCRIPT%"=="1" (
  echo [WARNING] Update helper script not detected during startup. Update features may be limited.
  echo.
)
if "%PRES_WARN_NO_INTERNET%"=="1" (
  echo [WARNING] No internet connectivity detected during startup.
  echo.
)

if "!internet_available!"=="0" (
echo NOTE: No internet detected. Options 1-5 require internet.
    echo.
)
echo Please select an option:
echo.
echo 1. Update MediCafe
echo.
echo 2. Download Email de Carol
echo.
echo 3. MediLink Claims
echo.
echo 4. ^[United^] Claims Status
echo.
echo 5. ^[United^] Deductible
echo.
echo 6. Run MediBot
echo.
echo 7. Troubleshooting
echo.
echo 8. Exit
echo.
set /p choice=Enter your choice:  

:: Update option numbers
if "!choice!"=="8" goto end_script
if "!choice!"=="7" goto troubleshooting_menu
if "!choice!"=="6" goto medibot_flow
if "!choice!"=="5" goto united_deductible
if "!choice!"=="4" goto united_claims_status
if "!choice!"=="3" goto medilink_flow
if "!choice!"=="2" goto download_emails
if "!choice!"=="1" goto check_updates
if "!choice!"=="0" goto end_script

echo Invalid choice. Please try again.
pause
goto main_menu

:: Medicafe Update
:check_updates
if "!internet_available!"=="0" (
    echo ========================================
    echo           UPDATE ERROR
    echo ========================================
    echo.
    echo [ERROR] No internet connection available.
    echo.
    echo MediCafe updates require an internet connection.
    echo Please check your network connection and try again.
    echo.
    echo Press Enter to return to main menu...
    pause >nul
    goto main_menu
)

echo ========================================
echo        MediCafe Update Process
echo ========================================
echo.
echo Checking system requirements...
echo.

:: Step 1: Verify Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.4 or later and try again.
    echo.
    echo Press Enter to return to main menu...
    pause >nul
    goto main_menu
)
echo [OK] Python found
echo.

:: Step 2: Check if update script exists
echo [2/5] Locating update script...
if exist "%upgrade_medicafe_local%" (
    set "upgrade_medicafe=%upgrade_medicafe_local%"
    echo [OK] Found local update script
) else (
    if exist "%upgrade_medicafe_legacy%" (
        set "upgrade_medicafe=%upgrade_medicafe_legacy%"
        echo [OK] Found legacy update script
    ) else (
        echo [ERROR] Update script not found
        echo.
        echo Expected locations:
        echo   - Local: %upgrade_medicafe_local%
        echo   - Legacy: %upgrade_medicafe_legacy%
        echo.
        echo Please ensure the update script is available.
        echo.
        echo Press Enter to return to main menu...
        pause >nul
        goto main_menu
    )
)
echo.

:: Step 3: Check MediCafe package
echo [3/5] Checking MediCafe installation...
python -c "import pkg_resources; print('MediCafe=='+pkg_resources.get_distribution('medicafe').version)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] MediCafe package not found
    echo Will attempt to install during update process
) else (
    echo [OK] MediCafe package found
)
echo.

:: Step 4: Verify internet connectivity
echo [4/5] Testing internet connection...
ping -n 1 google.com >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Internet connection test failed
    echo Please check your network connection and try again.
    echo.
    echo Press Enter to return to main menu...
    pause >nul
    goto main_menu
)
echo [OK] Internet connection available
echo.

:: Step 5: Start update process (self-update orchestrator)
echo [5/5] Preparing self-update...
echo.
echo ========================================
echo           UPDATE PREPARATION
echo ========================================
echo The application will close to allow safe replacement of files.
echo A separate updater will run and reopen MediBot when finished.
echo.
echo Update script: %upgrade_medicafe%
echo.

:: Build a temporary updater to run after this window exits
set "_MEDIBOT_PATH=%~f0"

:: Choose a writable temp directory with XP-safe fallback
if not defined TEMP set "TEMP=%~dp0"
if not exist "%TEMP%" mkdir "%TEMP%" 2>nul
set "_UPD_RUNNER=%TEMP%\medicafe_update_runner_%RANDOM%.cmd"

:: Create updater script line-by-line to avoid XP parsing issues with grouped redirection
echo @echo off> "%_UPD_RUNNER%"
echo setlocal enabledelayedexpansion>> "%_UPD_RUNNER%"
echo set "MEDIBOT_PATH=%_MEDIBOT_PATH%" >> "%_UPD_RUNNER%"
echo rem Wait briefly to ensure the main window has exited and released file locks>> "%_UPD_RUNNER%"
echo ping 127.0.0.1 -n 3 ^>nul>> "%_UPD_RUNNER%"
echo echo Starting MediCafe updater...>> "%_UPD_RUNNER%"
:: XP-compatible Python presence check
echo python --version ^>nul 2^>nul>> "%_UPD_RUNNER%"
echo if errorlevel 1 (>> "%_UPD_RUNNER%"
echo   echo [ERROR] Python not found in PATH. Aborting update.>> "%_UPD_RUNNER%"
echo   goto :eof>> "%_UPD_RUNNER%"
echo )>> "%_UPD_RUNNER%"
:: Run the updater directly with fully-resolved path to avoid nested %% var expansion issues
echo python "%upgrade_medicafe%" >> "%_UPD_RUNNER%"
echo set "RET=%%ERRORLEVEL%%" >> "%_UPD_RUNNER%"
echo echo Update process exited with code %%RET%%>> "%_UPD_RUNNER%"
echo if %%RET%% neq 0 (>> "%_UPD_RUNNER%"
echo   echo Update failed. Press any key to close...>> "%_UPD_RUNNER%"
echo   pause ^>nul>> "%_UPD_RUNNER%"
echo   exit %%RET%%>> "%_UPD_RUNNER%"
echo ) else (>> "%_UPD_RUNNER%"
echo   rem Relaunch MediBot on success>> "%_UPD_RUNNER%"
echo   if exist "%%MEDIBOT_PATH%%" start "MediBot" "%%MEDIBOT_PATH%%" >> "%_UPD_RUNNER%"
echo   exit>> "%_UPD_RUNNER%"
echo )>> "%_UPD_RUNNER%"

if not exist "%_UPD_RUNNER%" (
  echo [ERROR] Failed to create updater script at %_UPD_RUNNER%
  echo Press Enter to return to main menu...
  pause >nul
  goto main_menu
)

echo.
echo Launching updater and closing this window...
start "MediCafe Update" "%_UPD_RUNNER%"
exit 0

:: Download Carol's Emails
:download_emails
if "!internet_available!"=="0" (
    echo [WARNING] No internet connection available.
    goto main_menu
)

call "%~dp0process_csvs.bat"
cls
echo Starting email download via MediCafe...
cd /d "%~dp0.."
python -m MediCafe download_emails
if errorlevel 1 (
    echo [ERROR] Failed to download emails.
    pause
)

pause
goto main_menu

:: MediBot Flow
:medibot_flow
cls
echo Starting MediBot flow...
cd /d "%~dp0.."
python -m MediCafe medibot
if errorlevel 1 (
    echo [ERROR] Failed to start MediBot flow.
    pause
)

goto main_menu

:: MediLink Flow
:medilink_flow
cls
echo Starting MediLink flow...
cd /d "%~dp0.."
python -m MediCafe medilink
if errorlevel 1 (
    echo [ERROR] Failed to start MediLink flow.
    pause
)

goto main_menu

:toggle_perf_logging
cls
echo ========================================
echo Performance Logging (session toggle)
echo ========================================
echo.
if /I "%MEDICAFE_PERFORMANCE_LOGGING%"=="1" (
  set "MEDICAFE_PERFORMANCE_LOGGING=0"
  echo Turned OFF performance logging for this session.
) else (
  set "MEDICAFE_PERFORMANCE_LOGGING=1"
  echo Turned ON performance logging for this session.
)
echo.
echo Note: This affects current session only. To persist, set in config.json.
pause
goto troubleshooting_menu

:: United Claims Status
:united_claims_status
cls
echo Starting United Claims Status...
cd /d "%~dp0.."
python -m MediCafe claims_status
if errorlevel 1 (
    echo [ERROR] Failed to start United Claims Status.
    pause
)

pause
goto main_menu

:: United Deductible
:united_deductible
cls
echo Starting United Deductible...
cd /d "%~dp0.."
python -m MediCafe deductible
if errorlevel 1 (
    echo [ERROR] Failed to start United Deductible.
    pause
)

pause
goto main_menu

:: Process CSV Files moved to external script
:process_csvs
call "%~dp0process_csvs.bat"
goto :eof

REM [removed legacy :clear_cache block in favor of :clear_cache_menu]

REM [removed duplicate :clear_cache quick block; use :clear_cache_menu instead]

:: Clear Cache submenu (Quick vs Deep)
:clear_cache_menu
cls
echo ========================================
echo Clear Python Cache
echo ========================================
echo.
echo 1. Quick clear - compileall + delete __pycache__
echo 2. Deep clear via update_medicafe.py
echo 3. Back
echo.
set /p cc_choice=Enter your choice: 
if "%cc_choice%"=="1" goto clear_cache_quick
if "%cc_choice%"=="2" goto clear_cache_deep
if "%cc_choice%"=="3" goto troubleshooting_menu
echo Invalid choice. Press any key to continue...
pause >nul
goto clear_cache_menu

:clear_cache_quick
echo Running quick cache clear...
call "%~dp0clear_cache.bat" --quick
pause
goto troubleshooting_menu

:clear_cache_deep
cls
echo Deep cache clear using update_medicafe.py...
echo.
call "%~dp0clear_cache.bat" --deep
pause
goto troubleshooting_menu

:: Troubleshooting Submenu
:troubleshooting_menu
cls
echo Troubleshooting Options:
echo.
echo 1. Open Latest Log File
echo 2. Clear Python Cache
echo 3. Toggle Performance Logging ^(session^)
echo 4. Forced MediCafe version rollback
echo 5. Back to Main Menu
echo.
set /p tchoice=Enter your choice: 
if "%tchoice%"=="1" goto open_latest_log
if "%tchoice%"=="2" goto clear_cache_menu
if "%tchoice%"=="3" goto toggle_perf_logging
if "%tchoice%"=="4" goto forced_version_rollback
if "%tchoice%"=="5" goto main_menu
echo Invalid choice. Please try again.
pause
goto troubleshooting_menu

:: Open Latest Log (streamlined)
:open_latest_log
echo Opening the latest log file...
set "latest_log="
for /f "delims=" %%a in ('dir /b /a-d /o-d "%local_storage_path%\*.log" 2^>nul') do (
    set "latest_log=%%a"
    goto open_log_found
)

echo No log files found in %local_storage_path%.
pause
goto troubleshooting_menu

:: End Script
:end_script
echo Exiting MediBot
exit 0

:: Full Debug Mode moved to external script full_debug_suite.bat

:: Opened log file handling and helpers
:open_log_found
echo Found log file: %latest_log%
start notepad "%local_storage_path%\%latest_log%" >nul 2>&1
if %errorlevel% neq 0 (
    start write "%local_storage_path%\%latest_log%" >nul 2>&1
)
if %errorlevel% neq 0 (
    call :tail "%local_storage_path%\%latest_log%" 50
)
pause
goto troubleshooting_menu

:: Forced version rollback for MediCafe (hardcoded version placeholder)
:forced_version_rollback
cls
echo ========================================
echo Forced MediCafe Version Rollback
echo ========================================
echo.
if "!internet_available!"=="0" (
    echo No internet connection available.
    echo Cannot proceed with rollback without internet.
    pause >nul
    goto troubleshooting_menu
)
set "rollback_version=0.250813.1"
echo Forcing reinstall of %medicafe_package%==%rollback_version% with no dependencies...
python -m pip install --no-deps --force-reinstall %medicafe_package%==%rollback_version%
if errorlevel 1 (
    echo.
    echo [ERROR] Forced rollback failed.
    pause >nul
    goto troubleshooting_menu
)

:: Refresh displayed MediCafe version
set "package_version="
python -c "import pkg_resources; print('MediCafe=='+pkg_resources.get_distribution('medicafe').version)" > temp.txt 2>nul
set /p package_version=<temp.txt
if exist temp.txt del temp.txt
if defined package_version (
    for /f "tokens=2 delims==" %%a in ("%package_version%") do (
        set "medicafe_version=%%a"
    )
)
echo.
echo Rollback complete. Current MediCafe version: %medicafe_version%
pause >nul
goto troubleshooting_menu

:: Subroutine to display the last N lines of a file
:tail
:: Usage: call :tail filename number_of_lines
setlocal
set "file=%~1"
set /a lines=%~2

:: Get total line count robustly (avoid prefixed output)
set "count=0"
for /f %%a in ('type "%file%" ^| find /v /c ""') do set count=%%a

:: Compute starting line; clamp to 1
set /a start=count-lines+1
if !start! lss 1 set start=1

for /f "tokens=1* delims=:" %%a in ('findstr /n .* "%file%"') do (
    if %%a geq !start! echo %%b
)
endlocal & goto :eof