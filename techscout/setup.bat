@echo off
echo 🔍 Setting up TechScout...
echo.

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

if not exist tech_evaluations (
    mkdir tech_evaluations
    echo ✅ Created tech_evaluations directory
)

echo.
echo ✅ TechScout setup complete!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your API keys
echo 2. Run: python techscout.py
echo 3. Try: research "Cursor AI" or evaluate "GitHub Copilot"
echo.
pause