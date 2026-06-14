@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo ==========================================================
echo   📬 Local AI Email Security Agent — Windows Startup
echo ==========================================================
echo.

:: 1. Check if .env exists
echo [*] Checking configuration (.env file)...
if not exist .env (
    echo [X] Error: .env file is missing!
    echo.
    echo Creating .env from template (.env.example)...
    copy .env.example .env >nul
    echo.
    echo [!] Created .env. Please open .env, enter your email credentials,
    echo     and run Run.bat again.
    echo.
    echo Opening .env in Notepad for you now...
    notepad.exe .env
    pause
    exit /b 1
)
echo [✓] Configuration file (.env) exists.

:: 2. Check if Docker is installed
echo [*] Checking if Docker is installed...
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Error: Docker is not installed or not in your system PATH.
    echo     Please download and install Docker Desktop:
    echo     https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)
echo [✓] Docker is installed.

:: 3. Check if Docker Desktop is running
echo [*] Checking if Docker Desktop is running...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Error: Docker Desktop is not running!
    echo     Please start Docker Desktop and wait for it to be ready,
    echo     then run Run.bat again.
    echo.
    pause
    exit /b 1
)
echo [✓] Docker Desktop is running.

:: 4. Check if Ollama is running
echo [*] Checking if Ollama is running...
powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 3 > $null; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Error: Ollama is not running on http://localhost:11434!
    echo     Please open the Ollama application in your system tray,
    echo     then run Run.bat again.
    echo.
    pause
    exit /b 1
)
echo [✓] Ollama is running.

:: 5. Check and Pull Model
echo [*] Checking model availability...
powershell -Command ^
    "$model = (Get-Content .env | Select-String '^OLLAMA_MODEL=' | ForEach-Object { $_.Line.Split('=')[1].Trim() });" ^
    "if (-not $model) { $model = 'qwen2.5:1.5b' };" ^
    "Write-Host '   Configured Model: ' -NoNewline; Write-Host $model -ForegroundColor Cyan;" ^
    "$tags = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags';" ^
    "$exists = $false;" ^
    "foreach ($m in $tags.models) {" ^
    "  if ($m.name -eq $model -or $m.name.StartsWith(($model.Split(':')[0] + ':'))) {" ^
    "    $exists = $true; break;" ^
    "  }" ^
    "};" ^
    "if (-not $exists) {" ^
    "  Write-Host '   [!] Model not found locally. Pulling now (this may take a few minutes)...' -ForegroundColor Yellow;" ^
    "  ollama pull $model;" ^
    "  exit 0;" ^
    "} else {" ^
    "  Write-Host '   [✓] Model is downloaded and ready.' -ForegroundColor Green;" ^
    "  exit 0;" ^
    "}"
if %errorlevel% neq 0 (
    echo [X] Failed to verify or pull Ollama model.
    pause
    exit /b 1
)

:: 6. Launch Docker Compose
echo.
echo ==========================================================
echo   🚀 All checks passed! Starting the Email Security Agent...
echo ==========================================================
echo   * Press Ctrl+C in this window to stop the agent.
echo   * To clean up containers completely, run Stop.bat.
echo ==========================================================
echo.

docker compose up

pause
