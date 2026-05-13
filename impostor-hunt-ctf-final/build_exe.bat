@echo off
echo Cleaning old builds...
rmdir /s /q build
rmdir /s /q dist

echo.
echo Building ImpostorHunt EXE...
python -m PyInstaller ImpostorHunt.spec

echo.
echo Done! Your built files are in the "dist\ImpostorHunt" folder.
pause