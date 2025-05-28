@echo off
echo 🚀 Setting up Personal Assistant...

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
echo ✅ Personal Assistant setup complete
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your API keys
echo 2. Add your main.py file with the Personal Assistant code
echo 3. Run: python main.py
echo.
pause
