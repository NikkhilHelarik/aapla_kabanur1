@echo off
echo Installing requirements...
pip install -r requirements.txt
echo.
echo Starting Aapla Kabanur (database and tables are created automatically)...
python app.py
pause
