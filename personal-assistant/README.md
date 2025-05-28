# Personal Assistant with Memory

An intelligent AI assistant that remembers user preferences and manages tasks.

## Features

* **Persistent Memory**: Remembers user information across conversations
* **Task Management**: Add, track, and complete tasks with priorities
* **Note Taking**: Save and search notes with tags
* **Context Awareness**: References past conversations naturally
* **Multi-Model Support**: Works with Bedrock, Anthropic, OpenAI, or local models

## Quick Start (Windows)

```batch
REM Create virtual environment
python -m venv venv
venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Configure environment
copy .env.example .env
notepad .env

REM Run the assistant
python main.py
```

## Example Usage

```
You: My name is Sarah and I prefer morning meetings
Assistant: I'll remember that your name is Sarah and your preference for morning meetings.

You: Add a task to review quarterly report by Friday with high priority
Assistant: Added task: 'review quarterly report' with priority 'high' due Friday

You: What did we discuss about meetings?
Assistant: You mentioned preferring morning meetings. This helps me schedule appropriately.
```

## Configuration

Edit `.env` file with your settings:
* Choose model provider (bedrock, anthropic, openai, ollama)
* Add your API keys
* Configure memory settings

## Memory Storage

The assistant stores memory in `assistant_memory.json` including:
* User profile and preferences
* Conversation history (last 50 interactions)
* Tasks and reminders
* Notes with tags
* Learned facts about the user
