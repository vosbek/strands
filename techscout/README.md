# Strands Agents Examples

A collection of production-ready AI agent applications built with AWS Strands Agents SDK, demonstrating memory capabilities, development assistance, technology evaluation, and practical AI integration.

## 🚀 Projects

### 1. Personal Assistant with Memory
An intelligent personal assistant that remembers user preferences, manages tasks, and maintains conversation context across sessions.

**Features:**
- Persistent memory across conversations
- Task and reminder management
- Note-taking with searchable tags
- User preference learning
- Multi-model support (Bedrock, Anthropic, Ollama)

**What it does:** Creates an AI assistant that builds a relationship with you over time by remembering your conversations, preferences, and ongoing projects. Unlike ChatGPT that forgets everything, this assistant becomes more helpful the more you use it.

**Why use it:** You get genuine personalization that improves over time, complete control over your data, and it works with any AI provider. Most commercial alternatives cost $20-50/month and lock you into their ecosystem.

**Workflow integration:** Use as your daily AI companion - check in each morning to review tasks, capture meeting notes, ask questions where past context adds value. It becomes your personalized knowledge base.

[📂 View Project](./personal-assistant/) | [🚀 Quick Start](./personal-assistant/README.md)

### 2. DevMate - AI Development Assistant
A comprehensive development assistant that helps with code analysis, project management, and development workflow optimization.

**Features:**
- Intelligent codebase analysis with smart file prioritization
- Git workflow integration and commit message generation
- Security and performance scanning
- Automated documentation generation
- Development task tracking with priorities
- Stack Overflow integration for quick solutions

**What it does:** Analyzes your actual codebase (not generic advice) and provides intelligent insights about security vulnerabilities, performance issues, and technical debt. Combines multiple development tools with AI reasoning to understand your specific project context.

**Why use it:** GitHub Copilot only does code completion. SonarQube analyzes but lacks AI reasoning. ChatGPT gives generic advice but can't see your codebase. DevMate combines deep analysis with AI understanding of your specific project and learns your patterns over time.

**Workflow integration:** Run analysis at start of coding sessions to prioritize work. Use for code reviews before committing. Generate commit messages and track technical debt. It becomes your AI pair programmer that understands your specific codebase.

[📂 View Project](./devmate/) | [🚀 Quick Start](./devmate/README.md)

### 3. TechScout - AI Technology Research & Evaluation Assistant
A systematic research assistant that helps teams evaluate new AI tools and technologies through multi-source research and structured analysis.

**Features:**
- Multi-source research (GitHub, Reddit, Hacker News, official sites)
- Structured evaluation with scoring matrices and risk assessment
- Team knowledge base with searchable evaluations
- Executive reporting for leadership decisions
- Tool comparison and alternative analysis
- Integration recommendations and migration planning

**What it does:** Systematically researches new tools across multiple sources, creates structured evaluations with scoring matrices, identifies risks and alternatives, and maintains a searchable knowledge base that your team and leadership can reference for technology decisions.

**Why use it:** Manual research takes hours and results get lost. ChatGPT can't maintain knowledge base or remember past evaluations. TechScout provides consistent methodology, builds institutional knowledge, and generates leadership-ready reports with structured decision frameworks.

**Workflow integration:** Research any new tool you hear about in 5 minutes. Get structured evaluations instead of gut-feel decisions. Generate executive summaries for technology strategy meetings. Build institutional memory of what your team has evaluated and decided.

[📂 View Project](./techscout/) | [🚀 Quick Start](./techscout/README.md)

## 🛠 Getting Started (Windows)

### Prerequisites
- Python 3.10+
- Git for Windows (recommended)
- AWS CLI (for Bedrock) OR API keys for other providers

### Quick Installation
```batch
# Clone the repository
git clone https://github.com/yourusername/strands-agents-examples.git
cd strands-agents-examples

# Run automated setup for all projects
setup.bat
```

### Manual Setup
```batch
# Personal Assistant
cd personal-assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your API keys
python main.py

# DevMate
cd devmate
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your API keys
python devmate.py

# TechScout
cd techscout
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your API keys
python techscout.py
```

## 🧠 About Strands Agents

Strands Agents is AWS's open-source SDK that takes a model-driven approach to building AI agents. Unlike traditional frameworks requiring complex orchestration logic, Strands lets the LLM handle planning and execution, reducing development time from months to days.

### Why Strands?
- **Simple**: Build agents with just a model, tools, and prompt
- **Flexible**: Works with any LLM provider (Bedrock, Anthropic, OpenAI, local models)
- **Production-Ready**: Used by Amazon Q Developer, AWS Glue, and other AWS services
- **Fast Development**: Reduce time from months to days

**Key Advantage:** Strands eliminates complex orchestration workflows that plague traditional agent frameworks. Instead of manually coding decision trees, you delegate planning entirely to the LLM. This approach reduced Amazon Q Developer teams' time-to-market from months to days while providing flexibility to work with any model provider.

## 📚 Documentation

- [Strands Agents Official Docs](https://strandsagents.com/)
- [Windows Setup Guide](./docs/windows-setup.md)
- [Model Configuration Guide](./docs/model-setup.md)
- [Custom Tools Development](./docs/custom-tools.md)
- [Deployment Guide](./docs/deployment.md)

## 🎯 Example Use Cases

### Daily Developer Workflow
```bash
# Morning routine with Personal Assistant
"Review my tasks for today and remind me about the client meeting"

# Code analysis with DevMate
cd my-project && devmate analyze
"What security issues should I prioritize?"

# Technology research with TechScout
"research v0.dev" 
"compare v0.dev vs Cursor AI"
```

### Team Integration
- **Personal Assistant**: Individual productivity and task management
- **DevMate**: Code quality and development workflow optimization
- **TechScout**: Technology evaluation and strategic decision making

### Leadership Value
- **Personal Assistant**: Improved individual productivity and context retention
- **DevMate**: Consistent code quality standards and technical debt management
- **TechScout**: Data-driven technology decisions and strategic planning

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:
- Reporting bugs and requesting features
- Development setup and guidelines
- Pull request process
- Code of conduct

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- AWS Strands Agents team for the excellent SDK
- The open-source community for tool integrations
- Contributors and testers who helped improve these examples

---

⭐ If you find these examples helpful, please star the repository and share with your team!

**These projects demonstrate the full potential of Strands Agents for practical AI integration in software development workflows.**