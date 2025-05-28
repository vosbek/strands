"""
Personal Assistant with Memory using Strands Agents
==================================================

This example demonstrates how to build a personal assistant that:
1. Remembers user preferences and context across conversations
2. Maintains conversation history
3. Uses multiple tools for enhanced functionality
4. Implements persistent memory using JSON storage

Features:
- Memory management for user preferences and conversation history
- Task management with reminders
- Weather information retrieval
- Note-taking capabilities
- Web search functionality
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from strands import Agent, tool
from strands.models import BedrockModel
# Alternative model imports (uncomment as needed):
# from strands.models.anthropic import AnthropicModel
# from strands.models.ollama import OllamaModel


class MemoryManager:
    """Handles persistent memory for the assistant"""
    
    def __init__(self, memory_file: str = "assistant_memory.json"):
        self.memory_file = Path(memory_file)
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from file or create new memory structure"""
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "user_profile": {
                    "name": None,
                    "preferences": {},
                    "timezone": "UTC",
                    "interests": []
                },
                "conversation_history": [],
                "tasks": [],
                "notes": [],
                "facts_learned": {}
            }
    
    def save_memory(self):
        """Save current memory state to file"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2, default=str)
    
    def add_conversation(self, user_input: str, assistant_response: str):
        """Add conversation to history"""
        self.memory["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": assistant_response
        })
        # Keep only last 50 conversations to manage size
        if len(self.memory["conversation_history"]) > 50:
            self.memory["conversation_history"] = self.memory["conversation_history"][-50:]
        self.save_memory()
    
    def update_user_profile(self, **kwargs):
        """Update user profile information"""
        self.memory["user_profile"].update(kwargs)
        self.save_memory()
    
    def add_preference(self, key: str, value: Any):
        """Add or update user preference"""
        self.memory["user_profile"]["preferences"][key] = value
        self.save_memory()
    
    def get_context_summary(self) -> str:
        """Generate a context summary for the assistant"""
        profile = self.memory["user_profile"]
        recent_conversations = self.memory["conversation_history"][-5:]
        
        context = f"""
User Profile:
- Name: {profile.get('name', 'Unknown')}
- Preferences: {json.dumps(profile.get('preferences', {}), indent=2)}
- Interests: {', '.join(profile.get('interests', []))}

Recent Conversation Context:
"""
        for conv in recent_conversations:
            context += f"- User: {conv['user'][:100]}...\n"
        
        return context


# Initialize memory manager
memory_manager = MemoryManager()


@tool
def remember_user_info(name: str = None, preference_key: str = None, preference_value: str = None, interest: str = None) -> str:
    """
    Remember information about the user including name, preferences, and interests.
    
    Args:
        name: User's name to remember
        preference_key: Key for a preference (e.g., 'coffee_type', 'work_schedule')
        preference_value: Value for the preference
        interest: An interest or hobby to remember about the user
    """
    if name:
        memory_manager.update_user_profile(name=name)
        return f"I'll remember that your name is {name}."
    
    if preference_key and preference_value:
        memory_manager.add_preference(preference_key, preference_value)
        return f"I've noted your preference: {preference_key} = {preference_value}"
    
    if interest:
        current_interests = memory_manager.memory["user_profile"]["interests"]
        if interest not in current_interests:
            current_interests.append(interest)
            memory_manager.save_memory()
        return f"I've added '{interest}' to your interests."
    
    return "Please specify what you'd like me to remember about you."


@tool
def add_task_reminder(task: str, due_date: str = None, priority: str = "medium") -> str:
    """
    Add a task or reminder to the user's task list.
    
    Args:
        task: Description of the task
        due_date: Due date in YYYY-MM-DD format (optional)
        priority: Priority level (low, medium, high)
    """
    task_item = {
        "id": len(memory_manager.memory["tasks"]) + 1,
        "task": task,
        "due_date": due_date,
        "priority": priority,
        "created": datetime.now().isoformat(),
        "completed": False
    }
    
    memory_manager.memory["tasks"].append(task_item)
    memory_manager.save_memory()
    
    return f"Added task: '{task}' with priority '{priority}'" + (f" due {due_date}" if due_date else "")


@tool
def get_my_tasks(show_completed: bool = False) -> str:
    """
    Retrieve the user's current tasks and reminders.
    
    Args:
        show_completed: Whether to include completed tasks
    """
    tasks = memory_manager.memory["tasks"]
    if not show_completed:
        tasks = [t for t in tasks if not t["completed"]]
    
    if not tasks:
        return "You have no pending tasks."
    
    task_list = "Your tasks:\n"
    for task in tasks:
        status = "✓" if task["completed"] else "○"
        due_info = f" (due: {task['due_date']})" if task.get('due_date') else ""
        task_list += f"{status} [{task['priority'].upper()}] {task['task']}{due_info}\n"
    
    return task_list


@tool
def complete_task(task_id: int) -> str:
    """
    Mark a task as completed.
    
    Args:
        task_id: ID of the task to complete
    """
    tasks = memory_manager.memory["tasks"]
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            task["completed_date"] = datetime.now().isoformat()
            memory_manager.save_memory()
            return f"Marked task '{task['task']}' as completed!"
    
    return f"Could not find task with ID {task_id}"


@tool
def save_note(title: str, content: str, tags: str = "") -> str:
    """
    Save a note for future reference.
    
    Args:
        title: Title of the note
        content: Content of the note
        tags: Comma-separated tags for organizing notes
    """
    note = {
        "id": len(memory_manager.memory["notes"]) + 1,
        "title": title,
        "content": content,
        "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
        "created": datetime.now().isoformat()
    }
    
    memory_manager.memory["notes"].append(note)
    memory_manager.save_memory()
    
    return f"Saved note: '{title}'"


@tool
def search_notes(query: str) -> str:
    """
    Search through saved notes by title, content, or tags.
    
    Args:
        query: Search query
    """
    notes = memory_manager.memory["notes"]
    matching_notes = []
    
    query_lower = query.lower()
    for note in notes:
        if (query_lower in note["title"].lower() or 
            query_lower in note["content"].lower() or 
            any(query_lower in tag.lower() for tag in note["tags"])):
            matching_notes.append(note)
    
    if not matching_notes:
        return f"No notes found matching '{query}'"
    
    result = f"Found {len(matching_notes)} note(s) matching '{query}':\n"
    for note in matching_notes[:5]:  # Limit to 5 results
        result += f"• {note['title']}: {note['content'][:100]}...\n"
    
    return result


@tool
def get_weather_info(location: str) -> str:
    """
    Get weather information for a location.
    Note: This is a mock implementation. In production, integrate with a real weather API.
    
    Args:
        location: City or location name
    """
    # Mock weather data - replace with actual weather API call
    import random
    temperatures = [65, 72, 68, 75, 71, 69, 74]
    conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Light Rain", "Clear"]
    
    temp = random.choice(temperatures)
    condition = random.choice(conditions)
    
    return f"Weather in {location}: {temp}°F, {condition}"


@tool
def recall_conversation_context(topic: str = None, days_back: int = 7) -> str:
    """
    Recall previous conversation context about a specific topic.
    
    Args:
        topic: Specific topic to search for (optional)
        days_back: How many days back to search
    """
    conversations = memory_manager.memory["conversation_history"]
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    recent_conversations = [
        conv for conv in conversations 
        if datetime.fromisoformat(conv["timestamp"]) > cutoff_date
    ]
    
    if topic:
        topic_lower = topic.lower()
        relevant_conversations = [
            conv for conv in recent_conversations
            if topic_lower in conv["user"].lower() or topic_lower in conv["assistant"].lower()
        ]
    else:
        relevant_conversations = recent_conversations[-10:]  # Last 10 conversations
    
    if not relevant_conversations:
        return f"No recent conversations found" + (f" about '{topic}'" if topic else "")
    
    context = f"Recent conversation context" + (f" about '{topic}'" if topic else "") + ":\n"
    for conv in relevant_conversations[-5:]:  # Show last 5 relevant
        context += f"You: {conv['user'][:80]}...\nMe: {conv['assistant'][:80]}...\n\n"
    
    return context


class PersonalAssistant:
    """Main assistant class that integrates memory with Strands Agent"""
    
    def __init__(self, model_provider="bedrock"):
        # Configure model based on preference
        if model_provider == "bedrock":
            # Default to Bedrock - requires AWS credentials
            self.model = BedrockModel(
                model_id="us.amazon.nova-pro-v1:0",
                temperature=0.7
            )
        elif model_provider == "anthropic":
            # Uncomment and configure if using Anthropic API
            # self.model = AnthropicModel(
            #     model_id="claude-3-sonnet-20240229",
            #     temperature=0.7
            # )
            pass
        elif model_provider == "ollama":
            # Uncomment and configure if using Ollama
            # self.model = OllamaModel(
            #     host="http://localhost:11434",
            #     model_id="llama3"
            # )
            pass
        
        # Initialize agent with tools
        self.agent = Agent(
            model=self.model if model_provider == "bedrock" else None,  # Use default if not bedrock
            tools=[
                remember_user_info,
                add_task_reminder,
                get_my_tasks,
                complete_task,
                save_note,
                search_notes,
                get_weather_info,
                recall_conversation_context
            ]
        )
        
        # System prompt that incorporates memory
        self.system_prompt = """
You are a helpful personal assistant with memory capabilities. You can remember user preferences, 
maintain conversation context, manage tasks, and take notes. Always use the available tools to 
store and retrieve information about the user.

Key behaviors:
1. Remember important information the user shares
2. Reference past conversations when relevant
3. Proactively suggest tasks or reminders based on context
4. Be personable and build rapport over time
5. Use the user's name when you know it

Always check your memory tools before responding to provide personalized assistance.
"""
    
    def chat(self, user_input: str) -> str:
        """Process user input and return response"""
        # Get current context for the agent
        context = memory_manager.get_context_summary()
        
        # Combine system prompt with current context
        full_prompt = f"{self.system_prompt}\n\nCurrent Context:\n{context}\n\nUser: {user_input}"
        
        # Get response from agent
        response = self.agent(full_prompt)
        
        # Store conversation in memory
        memory_manager.add_conversation(user_input, response)
        
        return response


def main():
    """Example usage of the Personal Assistant"""
    print("🤖 Personal Assistant with Memory")
    print("=" * 40)
    print("Commands: 'quit' to exit, 'memory' to see current memory")
    print()
    
    # Initialize assistant
    assistant = PersonalAssistant()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'memory':
                print("\n📝 Current Memory:")
                print(json.dumps(memory_manager.memory, indent=2, default=str))
                print()
                continue
            
            if not user_input:
                continue
            
            # Get response from assistant
            response = assistant.chat(user_input)
            print(f"\n🤖 Assistant: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Example interactions to demonstrate memory capabilities
    print("📚 Example Usage:")
    print("""
    Try these commands to see memory in action:
    
    1. "My name is John and I love coffee"
    2. "Add a task to buy groceries tomorrow with high priority"
    3. "What are my current tasks?"
    4. "Save a note titled 'Meeting Notes' with content 'Discuss project timeline'"
    5. "What did we talk about earlier?"
    6. "What's the weather like in New York?"
    
    The assistant will remember your preferences and conversation history!
    """)
    
    main()