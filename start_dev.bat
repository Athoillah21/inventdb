@echo off
echo Starting Dashboard Environment...

:: Start Django Backend (Port 8000)
start "Django Backend" cmd /k "call venv\Scripts\activate && python manage.py runserver"

:: Start Svelte Frontend (Port 5173)
start "Svelte Frontend" cmd /k "cd svelte-poc && npm run dev"

echo Backend and Frontend are starting in separate windows...
