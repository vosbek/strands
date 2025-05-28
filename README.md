# Strands Agents Examples

A collection of production-ready AI agent applications built with AWS Strands Agents SDK.

## 🚀 Projects

### 1. Personal Assistant with Memory
An intelligent personal assistant that remembers user preferences and manages tasks.

**Features:**
* Persistent memory across conversations
* Task and reminder management
* Note-taking with searchable tags
* User preference learning
* Multi-model support (Bedrock, Anthropic, Ollama)

[View Personal Assistant](./personal-assistant/)

### 2. DevMate - AI Development Assistant
Comprehensive development assistant for code analysis and project management.

**Features:**
* Intelligent codebase analysis
* Git workflow integration
* Security and performance scanning
* Automated documentation generation
* Development task tracking

[View DevMate](./devmate/)

## 🛠 Getting Started (Windows)

### Prerequisites
- Python 3.10+
- Git for Windows (recommended)
- AWS CLI (for Bedrock) OR API keys for other providers

### Quick Installation
```batch
git clone https://github.com/vosbek/strands-agents-examples.git
cd strands-agents-examples
setup.bat
```

### Manual Setup
```batch
REM Personal Assistant
cd personal-assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
REM Edit .env with your API keys
python main.py
```

## 🧠 About Strands Agents

Strands Agents is AWS's open-source SDK that simplifies AI agent development using a model-driven approach instead of complex orchestration logic.

### Why Strands?
* **Simple**: Build agents with just model + tools + prompt
* **Flexible**: Works with any LLM provider
* **Production-Ready**: Used by Amazon Q Developer and AWS services
* **Fast Development**: Reduce time from months to days

## 📚 Documentation

- [Official Strands Docs](https://strandsagents.com/)
- [Windows Setup Guide](./docs/windows-setup.md)
- [Model Configuration](./docs/model-setup.md)

## 🤝 Contributing

We welcome contributions See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

⭐ Star this repo if you find it helpful
