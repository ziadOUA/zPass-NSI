@echo off
pyinstaller main.py --windowed -i "zpass.ico" --hidden-import settings_utils
echo Finished building the program
Xcopy themes dist\main\themes /E /I
echo Finished copying the necessary files
pause