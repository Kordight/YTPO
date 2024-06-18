@echo on
echo Starting YTPO for the first time, please wait...
echo We have to install a few required Python libraries
pip install -r requirements.txt
echo Installation completed, launching YTPO...
win_launch.bat
pause
