@echo off
echo Building knitout-interpreter documentation...
echo.

REM Change to docs directory
cd /d "%~dp0"

REM Generate API documentation
echo Generating API documentation...
sphinx-apidoc -o source ..\src\knitout_interpreter --force --module-first

REM Build HTML documentation
echo Building HTML...
sphinx-build -M html source build

echo.
echo Documentation built successfully!
echo Open: %~dp0build\html\index.html
echo.
pause
