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

## What it does: 
This analyzes your actual codebase (not just generic coding advice) and provides intelligent insights about security vulnerabilities, performance issues, code quality, and technical debt. It combines multiple development tools with AI reasoning to understand your specific project context and suggest improvements, manage development tasks, and help with Git workflows.

## Why use it over alternatives: 

GitHub Copilot only does code completion. SonarQube analyzes code but lacks AI reasoning. ChatGPT gives generic coding advice but can't see your actual codebase. DevMate combines deep code analysis with AI understanding of your specific project, learns your coding patterns over time, and integrates directly into your development workflow.

## Workflow integration: 
Run analysis at the start of each coding session to prioritize what needs attention. Use it for code reviews before committing to catch issues early. Let it generate commit messages, track technical debt, and maintain project documentation automatically. It becomes your AI pair programmer that understands your specific codebase and helps maintain quality standards.
These descriptions make it immediately clear why someone would choose these tools over existing alternatives and how they fit into real development workflows. They emphasize the unique value proposition of having AI that understands YOUR specific context rather than providing generic responses.