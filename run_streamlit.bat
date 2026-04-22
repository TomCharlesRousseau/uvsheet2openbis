@echo off
REM Streamlit startup script for UV Sheet Parser
REM Run this to start the Streamlit UI

echo Starting UV Sheet Parser Streamlit UI...
echo.
echo The app will open in your default browser at http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

streamlit run streamlit_app.py --logger.level=info

pause
