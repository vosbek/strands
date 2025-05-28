# DevMate - AI Development Assistant

Comprehensive development assistant for Windows developers.

## Features

* **Code Analysis**: Security, performance, and maintainability scanning
* **Git Integration**: Status summaries, commit message generation, branch analysis
* **Task Management**: Development task tracking with priorities
* **Documentation**: Automated README and changelog generation
* **Research**: Stack Overflow integration and best practices

## Quick Start (Windows)

```batch
REM Create virtual environment
python -m venv venv
venv\Scripts\activate

REM Install dependencies (includes dev tools)
pip install -r requirements.txt

REM Setup configuration
copy .env.example .env
notepad .env

REM Run from your project root
python devmate.py
```

## Commands

* `analyze` - Analyze current codebase
* `tasks` - View development tasks
* `git` - Git status summary
* `readme` - Generate project README
* `search <query>` - Search Stack Overflow
* `review <file>` - Code review for specific file

## Windows-Specific Features

* PowerShell integration
* Windows path handling
* Visual Studio Code integration
* Windows Terminal optimization

## Example Session

```
🤖 DevMate> analyze
📊 Analyzing codebase... Found 3 security issues and 5 performance optimizations

🤖 DevMate> add task "fix SQL injection in auth.py" security urgent
✅ Added high-priority security task

🤖 DevMate> git
🌿 Git Status: 3 modified files, 2 untracked files
💡 Suggested commit: "fix^(auth^): resolve SQL injection vulnerability"
```
