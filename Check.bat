@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo ==========================================================
echo   🩺 Local AI Email Security Agent — System Health Check
echo ==========================================================
echo.

set ERR_COUNT=0

:: 1. Check .env
echo [*] Checking .env file...
if not exist .env (
    echo   [X] Error: .env file is missing!
    set /a ERR_COUNT+=1
) else (
    echo   [✓] .env file is present.
    
    :: Check if credentials are filled in (not default placeholders)
    findstr /C:"your_email@gmail.com" .env >nul
    if %errorlevel% equ 0 (
        echo   [!] Warning: IMAP_USERNAME is still set to placeholder 'your_email@gmail.com'.
        set /a ERR_COUNT+=1
    )
    findstr /C:"your_app_password_here" .env >nul
    if %errorlevel% equ 0 (
        echo   [!] Warning: IMAP_PASSWORD is still set to placeholder 'your_app_password_here'.
        set /a ERR_COUNT+=1
    )
)

:: 2. Check Docker
echo [*] Checking Docker installation...
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo   [X] Error: Docker is not installed or not in PATH.
    set /a ERR_COUNT+=1
) else (
    echo   [✓] Docker CLI is available.
    
    docker info >nul 2>&1
    if %errorlevel% neq 0 (
        echo   [X] Error: Docker Desktop is not running.
        set /a ERR_COUNT+=1
    ) else (
        echo   [✓] Docker Daemon is running.
    )
)

:: 3. Check Ollama
echo [*] Checking Ollama service...
powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 3 > $null; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel% neq 0 (
    echo   [X] Error: Ollama is not running on http://localhost:11434.
    set /a ERR_COUNT+=1
) else (
    echo   [✓] Ollama service is running.
    
    :: Check model availability
    powershell -Command ^
        "$model = (Get-Content .env | Select-String '^OLLAMA_MODEL=' | ForEach-Object { $_.Line.Split('=')[1].Trim() });" ^
        "if (-not $model) { $model = 'qwen2.5:1.5b' };" ^
        "$tags = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags';" ^
        "$exists = $false;" ^
        "foreach ($m in $tags.models) {" ^
        "  if ($m.name -eq $model -or $m.name.StartsWith(($model.Split(':')[0] + ':'))) {" ^
        "    $exists = $true; break;" ^
        "  }" ^
        "};" ^
        "if ($exists) {" ^
        "  Write-Host '  [✓] Model' $model 'is downloaded and ready.' -ForegroundColor Green;" ^
        "  exit 0;" ^
        "} else {" ^
        "  Write-Host '  [X] Model' $model 'is NOT downloaded!' -ForegroundColor Red;" ^
        "  exit 1;" ^
        "}"
    if %errorlevel% neq 0 (
        set /a ERR_COUNT+=1
    )
)

:: 4. Run python health checks (using python or docker run)
echo [*] Running application-level health check...
if exist .env (
    docker info >nul 2>&1
    if %errorlevel% equ 0 (
        echo   [Running check inside Docker container...]
        docker compose run --rm email-agent python main.py --check
        if %errorlevel% neq 0 (
            echo   [X] Application health check inside container failed.
            set /a ERR_COUNT+=1
        )
    ) else (
        if exist .venv\Scripts\python.exe (
            echo   [Running check using local virtual environment...]
            .venv\Scripts\python.exe main.py --check
            if %errorlevel% neq 0 (
                echo   [X] Application health check failed.
                set /a ERR_COUNT+=1
            )
        ) else (
            echo   [!] Skipping app-level check (Docker is stopped and Python virtual environment is not setup).
        )
    )
)

echo.
echo ==========================================================
if %ERR_COUNT% equ 0 (
    echo   [✓] ALL HEALTH CHECKS PASSED - READY TO RUN!
) else (
    echo   [X] FOUND %ERR_COUNT% ISSUES - SEE DETAILS ABOVE.
)
echo ==========================================================
echo.
pause
