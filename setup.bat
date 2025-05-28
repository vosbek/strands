@echo off
echo 🚀 Setting up Strands Agents Examples...
echo.

echo 📦 Setting up Personal Assistant...
cd personal-assistant
call setup.bat
cd ..

echo 🔧 Setting up DevMate...
cd devmate
call setup.bat
cd ..

echo ✅ All projects setup complete
echo.
echo 📋 Next steps:
echo 1. Add your Python code files:
echo    - Copy Personal Assistant code to: personal-assistant\main.py
echo    - Copy DevMate code to: devmate\devmate.py
echo.
echo 2. Edit .env files in both projects with your API keys
echo.
echo 3. Test the assistants:
echo    - Personal Assistant: cd personal-assistant && python main.py
echo    - DevMate: cd devmate && python devmate.py
echo.
echo 💡 See README.md files for detailed instructions
pause
