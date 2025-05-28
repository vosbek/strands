@echo off
echo 🔧 Setting up DevMate...

python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

if not exist .env (
    copy .env.example .env
    echo ✅ Created .env file - please edit with your API keys
) else (
    echo ✅ .env file already exists
)

echo.
echo ✅ DevMate setup complete
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your API keys
echo 2. Add your devmate.py file with the DevMate code
echo 3. Run: python devmate.py
echo.
pause
