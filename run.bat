@echo off
echo Starting Job Search App...
echo Backend  -> http://localhost:8000
echo Frontend -> http://localhost:5173
echo.

start "Backend" cmd /k "cd backend && python manage.py runserver"
timeout /t 2 /nobreak >nul
start "Frontend" cmd /k "cd frontend && npm run dev"

echo Both services started in separate windows.
