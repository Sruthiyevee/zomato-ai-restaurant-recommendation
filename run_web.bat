@echo off
echo Starting Zomato AI Web Interface...
echo Please wait while the server starts...
echo.
echo Once started, open http://127.0.0.1:8000 in your browser.
echo.
python -m uvicorn phase_6_web.src.main:app --host 127.0.0.1 --port 8000 --reload
pause
