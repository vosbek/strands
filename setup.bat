@echo off
echo 🚀 Setting up Strands Agents Examples...
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.10+ from python.org
    pause
    exit /b 1
)
echo ✅ Python found

REM Check Git
git --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Git not found - some features will be limited
) else (
    echo ✅ Git found
)

echo.
echo 📦 Setting up Personal Assistant...
cd personal-assistant
if exist setup.bat (
    call setup.bat
) else (
    echo Creating basic setup for Personal Assistant...
    python -m venv venv
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if not exist .env copy .env.example .env
)
cd ..

echo.
echo 🔧 Setting up DevMate...
cd devmate
if exist setup.bat (
    call setup.bat
) else (
    echo Creating basic setup for DevMate...
    python -m venv venv
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if not exist .env copy .env.example .env
)
cd ..

echo.
echo 🔍 Setting up TechScout...
cd techscout
if exist setup.bat (
    call setup.bat
) else (
    echo Creating basic setup for TechScout...
    python -m venv venv
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if not exist .env copy .env.example .env
    if not exist tech_evaluations mkdir tech_evaluations
)
cd ..

echo.
echo ✅ All projects setup complete!
echo.
echo 🎯 Your Strands Agents Examples are ready:
echo.
echo 📋 Available Projects:
echo   1. Personal Assistant - Memory & task management
echo      cd personal-assistant ^&^& python main.py
echo.
echo   2. DevMate - Code analysis ^& development workflow
echo      cd devmate ^&^& python devmate.py
echo.
echo   3. TechScout - Technology research ^& evaluation
echo      cd techscout ^&^& python techscout.py
echo.
echo 📝 Next steps:
echo 1. Edit .env files in each project with your API keys:
echo    - personal-assistant\.env
echo    - devmate\.env  
echo    - techscout\.env
echo.
echo 2. Test each assistant:
echo    - Personal Assistant: "My name is John, add task buy groceries"
echo    - DevMate: "analyze" or "git" or "tasks"
echo    - TechScout: "research Cursor AI" or "evaluate GitHub Copilot"
echo.
echo 💡 See individual README.md files for detailed instructions
echo.
pause