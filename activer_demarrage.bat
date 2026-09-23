@echo off
cd /d "%~dp0"
where pythonw >nul 2>nul || (echo Python introuvable dans le PATH. & pause & exit /b 1)
python "%~dp0h13ris_pets.py" --autostart on
start "" pythonw "%~dp0h13ris_pets.py"
