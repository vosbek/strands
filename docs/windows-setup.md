# Windows Setup Guide

## Quick Start

1. **Run the setup script**
   ```batch
   setup.bat
   ```

2. **Add your code files**
   - Copy Personal Assistant code to: `personal-assistant\main.py`
   - Copy DevMate code to: `devmate\devmate.py`

3. **Configure API keys**
   - Edit `personal-assistant\.env`
   - Edit `devmate\.env`

4. **Test the assistants**
   ```batch
   cd personal-assistant
   venv\Scripts\activate
   python main.py
   ```

## Troubleshooting

**Python not found**
- Install Python 3.10+ from python.org
- Ensure "Add Python to PATH" is checked

**Virtual environment issues**
- Delete `venv` folder and rerun setup
- Run Command Prompt as Administrator

**Import errors**
- Activate virtual environment: `venv\Scripts\activate`
- Reinstall requirements: `pip install -r requirements.txt`

## API Configuration

### AWS Bedrock
1. Install AWS CLI: `pip install awscli`
2. Configure: `aws configure`
3. Enable model access in AWS Bedrock console

### Anthropic
- Get API key from console.anthropic.com
- Add to .env: `ANTHROPIC_API_KEY=your_key_here`

### OpenAI
- Get API key from platform.openai.com
- Add to .env: `OPENAI_API_KEY=your_key_here`

### Ollama (Local Models)
1. Install Ollama from ollama.ai
2. Pull models: `ollama pull llama3`
3. Start server: `ollama serve`
