@echo off
chcp 65001 >nul
echo ==========================================================
echo   🛑 Stopping Local AI Email Security Agent...
echo ==========================================================
echo.

where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Docker command not found.
    pause
    exit /b 1
)

docker compose down

echo.
echo ==========================================================
echo   [✓] Agent stopped and Docker container cleaned up!
echo ==========================================================
echo.
pause
