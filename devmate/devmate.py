"""
DevMate - AI Development Assistant using Strands Agents
======================================================

A comprehensive development assistant that helps with:
1. Code analysis and review
2. Project management and task tracking
3. Documentation generation
4. Git workflow assistance
5. Debug help and error analysis
6. Technology research and recommendations
7. Code refactoring suggestions
8. Testing assistance

Features:
- Analyzes local codebases and provides insights
- Integrates with Git for workflow management
- Generates documentation and README files  
- Provides code review and security analysis
- Tracks development tasks and progress
- Searches Stack Overflow and documentation
- Manages development environment setup
"""

import os
import json
import subprocess
import ast
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import fnmatch

from strands import Agent, tool
from strands.models import BedrockModel
# Alternative imports:
# from strands.models.anthropic import AnthropicModel
# from strands.models.ollama import OllamaModel


class ProjectContext:
    """Manages development project context and memory"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.context_file = self.project_root / ".devmate_context.json"
        self.context = self._load_context()
    
    def _load_context(self) -> Dict[str, Any]:
        """Load project context from file"""
        if self.context_file.exists():
            with open(self.context_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "project_name": self.project_root.name,
                "language": "unknown",
                "framework": "unknown",
                "last_analysis": None,
                "issues_found": [],
                "tasks": [],
                "code_metrics": {},
                "dependencies": [],
                "git_info": {},
                "team_notes": []
            }
    
    def save_context(self):
        """Save current context to file"""
        with open(self.context_file, 'w') as f:
            json.dump(self.context, f, indent=2, default=str)
    
    def update_project_info(self, **kwargs):
        """Update project information"""
        self.context.update(kwargs)
        self.save_context()


# Global project context
project_ctx = ProjectContext()


@tool
def analyze_codebase(directory: str = ".", include_patterns: str = "*.py,*.js,*.ts,*.java,*.cpp,*.c,*.go,*.rs") -> str:
    """
    Analyze the codebase structure, complexity, and potential issues.
    
    Args:
        directory: Directory to analyze (default: current directory)
        include_patterns: Comma-separated file patterns to include
    """
    directory = Path(directory).resolve()
    patterns = [p.strip() for p in include_patterns.split(",")]
    
    files_analyzed = []
    total_lines = 0
    total_functions = 0
    issues = []
    languages = {}
    
    # Walk through directory
    for root, dirs, files in os.walk(directory):
        # Skip common non-code directories
        dirs[:] = [d for d in dirs if d not in {'.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache'}]
        
        for file in files:
            file_path = Path(root) / file
            
            # Check if file matches patterns
            if any(fnmatch.fnmatch(file, pattern) for pattern in patterns):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = len(content.splitlines())
                        total_lines += lines
                        
                        # Detect language
                        ext = file_path.suffix.lower()
                        languages[ext] = languages.get(ext, 0) + 1
                        
                        # Count functions (simple heuristic)
                        if ext == '.py':
                            functions = len(re.findall(r'^\s*def\s+\w+', content, re.MULTILINE))
                        elif ext in ['.js', '.ts']:
                            functions = len(re.findall(r'function\s+\w+|const\s+\w+\s*=\s*\([^)]*\)\s*=>', content))
                        elif ext == '.java':
                            functions = len(re.findall(r'public\s+\w+\s+\w+\s*\(|private\s+\w+\s+\w+\s*\(', content))
                        else:
                            functions = 0
                        
                        total_functions += functions
                        
                        # Check for potential issues
                        if lines > 500:
                            issues.append(f"Large file: {file_path.relative_to(directory)} ({lines} lines)")
                        
                        if ext == '.py' and 'TODO' in content:
                            todos = len(re.findall(r'#\s*TODO', content, re.IGNORECASE))
                            if todos > 0:
                                issues.append(f"TODOs found in {file_path.relative_to(directory)}: {todos}")
                        
                        files_analyzed.append({
                            "file": str(file_path.relative_to(directory)),
                            "lines": lines,
                            "functions": functions
                        })
                        
                except Exception as e:
                    issues.append(f"Error reading {file_path}: {str(e)}")
    
    # Update project context
    project_ctx.context["last_analysis"] = datetime.now().isoformat()
    project_ctx.context["code_metrics"] = {
        "total_files": len(files_analyzed),
        "total_lines": total_lines,
        "total_functions": total_functions,
        "languages": languages
    }
    project_ctx.context["issues_found"] = issues
    project_ctx.save_context()
    
    # Generate report
    main_language = max(languages.items(), key=lambda x: x[1])[0] if languages else "unknown"
    
    report = f"""
📊 Codebase Analysis Results:
============================
Project: {directory.name}
Files analyzed: {len(files_analyzed)}
Total lines of code: {total_lines:,}
Total functions: {total_functions}
Primary language: {main_language}

Languages detected: {dict(languages)}

⚠️  Issues found: {len(issues)}
{chr(10).join('• ' + issue for issue in issues[:10])}
{f'... and {len(issues) - 10} more issues' if len(issues) > 10 else ''}

📈 Top files by size:
{chr(10).join('• ' + f['file'] + f" ({f['lines']} lines)" for f in sorted(files_analyzed, key=lambda x: x['lines'], reverse=True)[:5])}
"""
    
    return report


@tool
def review_code_file(file_path: str, focus_areas: str = "security,performance,maintainability") -> str:
    """
    Perform detailed code review of a specific file.
    
    Args:
        file_path: Path to the file to review
        focus_areas: Comma-separated areas to focus on (security, performance, maintainability, style)
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return f"File not found: {file_path}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return f"Error reading file: {e}"
    
    focus_list = [area.strip().lower() for area in focus_areas.split(",")]
    issues = []
    suggestions = []
    
    # Security checks
    if "security" in focus_list:
        security_patterns = [
            (r'eval\s*\(', "Avoid using eval() - security risk"),
            (r'exec\s*\(', "Avoid using exec() - security risk"),
            (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', "Avoid shell=True in subprocess - security risk"),
            (r'password\s*=\s*["\'][^"\']*["\']', "Hardcoded password detected"),
            (r'api_key\s*=\s*["\'][^"\']*["\']', "Hardcoded API key detected")
        ]
        
        for pattern, message in security_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"🔒 Security: {message}")
    
    # Performance checks
    if "performance" in focus_list:
        perf_patterns = [
            (r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\([^)]+\)\s*\)', "Consider using enumerate() instead of range(len())"),
            (r'\.append\s*\([^)]+\)\s*$', "Consider list comprehension for better performance"),
            (r'time\.sleep\s*\(\s*\d+\s*\)', "Long sleep detected - consider async alternatives")
        ]
        
        for pattern, message in perf_patterns:
            if re.search(pattern, content, re.MULTILINE):
                suggestions.append(f"⚡ Performance: {message}")
    
    # Maintainability checks
    if "maintainability" in focus_list:
        lines = content.splitlines()
        
        # Check function length
        current_function = None
        function_start = 0
        
        for i, line in enumerate(lines):
            if re.match(r'^\s*def\s+\w+', line):
                if current_function:
                    length = i - function_start
                    if length > 50:
                        issues.append(f"🔧 Maintainability: Function '{current_function}' is too long ({length} lines)")
                
                current_function = re.search(r'def\s+(\w+)', line).group(1)
                function_start = i
        
        # Check for magic numbers
        magic_numbers = re.findall(r'\b\d{2,}\b', content)
        if len(magic_numbers) > 5:
            suggestions.append("🔧 Maintainability: Consider using named constants for magic numbers")
        
        # Check documentation
        if file_path.suffix == '.py':
            if '"""' not in content and "'''" not in content:
                suggestions.append("📝 Documentation: Add docstrings to functions and classes")
    
    # Style checks
    if "style" in focus_list and file_path.suffix == '.py':
        if len([l for l in content.splitlines() if len(l) > 100]) > 5:
            suggestions.append("✨ Style: Consider breaking long lines (>100 chars)")
        
        if content.count('\n\n\n') > 0:
            suggestions.append("✨ Style: Remove excessive blank lines")
    
    # Generate report
    report = f"""
📋 Code Review: {file_path.name}
{'=' * (15 + len(file_path.name))}
File size: {len(content.splitlines())} lines
Focus areas: {', '.join(focus_list)}

"""
    
    if issues:
        report += "🚨 Issues Found:\n"
        report += '\n'.join(f"  {issue}" for issue in issues)
        report += "\n\n"
    
    if suggestions:
        report += "💡 Suggestions:\n"
        report += '\n'.join(f"  {suggestion}" for suggestion in suggestions)
        report += "\n\n"
    
    if not issues and not suggestions:
        report += "✅ No major issues found! Code looks good.\n"
    
    return report


@tool
def git_status_summary() -> str:
    """Get a comprehensive Git status summary including recent commits and branch info."""
    try:
        # Get current branch
        branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                     capture_output=True, text=True, cwd=project_ctx.project_root)
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
        
        # Get status
        status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                     capture_output=True, text=True, cwd=project_ctx.project_root)
        
        # Get recent commits
        log_result = subprocess.run(['git', 'log', '--oneline', '-10'], 
                                  capture_output=True, text=True, cwd=project_ctx.project_root)
        
        # Get remote info
        remote_result = subprocess.run(['git', 'remote', '-v'], 
                                     capture_output=True, text=True, cwd=project_ctx.project_root)
        
        # Parse status
        status_lines = status_result.stdout.strip().split('\n') if status_result.stdout.strip() else []
        modified = [line[3:] for line in status_lines if line.startswith(' M')]
        added = [line[3:] for line in status_lines if line.startswith('A ')]
        deleted = [line[3:] for line in status_lines if line.startswith(' D')]
        untracked = [line[3:] for line in status_lines if line.startswith('??')]
        
        # Update project context
        project_ctx.context["git_info"] = {
            "current_branch": current_branch,
            "modified_files": len(modified),
            "added_files": len(added),
            "deleted_files": len(deleted),
            "untracked_files": len(untracked),
            "last_check": datetime.now().isoformat()
        }
        project_ctx.save_context()
        
        report = f"""
🌿 Git Status Summary
====================
Current branch: {current_branch}
Repository: {project_ctx.project_root.name}

📊 Working Directory Status:
• Modified files: {len(modified)}
• Added files: {len(added)} 
• Deleted files: {len(deleted)}
• Untracked files: {len(untracked)}

"""
        
        if modified:
            report += f"📝 Modified files:\n"
            report += '\n'.join(f"  • {file}" for file in modified[:10])
            if len(modified) > 10:
                report += f"\n  ... and {len(modified) - 10} more"
            report += "\n\n"
        
        if untracked:
            report += f"❓ Untracked files:\n"
            report += '\n'.join(f"  • {file}" for file in untracked[:5])
            if len(untracked) > 5:
                report += f"\n  ... and {len(untracked) - 5} more"
            report += "\n\n"
        
        if log_result.returncode == 0:
            report += "📈 Recent commits:\n"
            commits = log_result.stdout.strip().split('\n')[:5]
            report += '\n'.join(f"  • {commit}" for commit in commits)
            report += "\n\n"
        
        if remote_result.returncode == 0 and remote_result.stdout.strip():
            report += "🔗 Remotes:\n"
            remotes = remote_result.stdout.strip().split('\n')
            report += '\n'.join(f"  • {remote}" for remote in remotes)
        
        return report
        
    except Exception as e:
        return f"Error getting Git status: {e}"


@tool
def create_git_commit_message(files: str = "", description: str = "") -> str:
    """
    Generate a conventional commit message based on changed files and description.
    
    Args:
        files: Comma-separated list of files (optional, will detect from git status)
        description: Brief description of changes
    """
    try:
        if not files:
            # Get modified files from git status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=project_ctx.project_root)
            if result.returncode == 0:
                status_lines = result.stdout.strip().split('\n')
                modified_files = [line[3:] for line in status_lines if line.strip()]
                files = ', '.join(modified_files[:5])
        
        # Analyze file types to determine commit type
        file_list = [f.strip() for f in files.split(',') if f.strip()]
        
        commit_type = "feat"  # default
        
        # Determine commit type based on files
        if any('test' in f.lower() for f in file_list):
            commit_type = "test"
        elif any(f.endswith(('.md', '.txt', '.rst')) for f in file_list):
            commit_type = "docs"
        elif any('config' in f.lower() or f.endswith(('.json', '.yaml', '.yml', '.toml')) for f in file_list):
            commit_type = "chore"
        elif any('style' in f.lower() or f.endswith('.css') for f in file_list):
            commit_type = "style"
        elif description and any(word in description.lower() for word in ['fix', 'bug', 'error', 'issue']):
            commit_type = "fix"
        elif description and any(word in description.lower() for word in ['refactor', 'cleanup', 'reorganize']):
            commit_type = "refactor"
        
        # Generate scope from file paths
        scope = ""
        if file_list:
            common_dirs = set()
            for f in file_list:
                parts = Path(f).parts
                if len(parts) > 1:
                    common_dirs.add(parts[0])
            
            if len(common_dirs) == 1:
                scope = f"({list(common_dirs)[0]})"
        
        # Generate commit message
        if description:
            message = f"{commit_type}{scope}: {description}"
        else:
            message = f"{commit_type}{scope}: update {', '.join(file_list[:2])}"
            if len(file_list) > 2:
                message += f" and {len(file_list) - 2} other files"
        
        # Add body with file list if many files
        body = ""
        if len(file_list) > 3:
            body = f"\n\nModified files:\n" + '\n'.join(f"- {f}" for f in file_list)
        
        return f"""
🎯 Suggested commit message:
===========================
{message}{body}

💡 Conventional commit types:
• feat: new feature
• fix: bug fix  
• docs: documentation
• style: formatting changes
• refactor: code restructuring
• test: adding tests
• chore: maintenance

To commit: git commit -m "{message}"
"""
        
    except Exception as e:
        return f"Error generating commit message: {e}"


@tool
def add_dev_task(title: str, description: str = "", priority: str = "medium", category: str = "general") -> str:
    """
    Add a development task to the project.
    
    Args:
        title: Task title
        description: Detailed description
        priority: Priority level (low, medium, high, urgent)
        category: Task category (feature, bug, refactor, docs, test, chore)
    """
    task = {
        "id": len(project_ctx.context["tasks"]) + 1,
        "title": title,
        "description": description,
        "priority": priority,
        "category": category,
        "status": "todo",
        "created": datetime.now().isoformat(),
        "assigned_to": None,
        "estimated_hours": None
    }
    
    project_ctx.context["tasks"].append(task)
    project_ctx.save_context()
    
    return f"✅ Added task #{task['id']}: {title} ({priority} priority, {category} category)"


@tool
def list_dev_tasks(status: str = "all", category: str = "all") -> str:
    """
    List development tasks with filtering options.
    
    Args:
        status: Filter by status (all, todo, in_progress, done, blocked)
        category: Filter by category (all, feature, bug, refactor, docs, test, chore)
    """
    tasks = project_ctx.context["tasks"]
    
    # Apply filters
    if status != "all":
        tasks = [t for t in tasks if t["status"] == status]
    
    if category != "all":
        tasks = [t for t in tasks if t["category"] == category]
    
    if not tasks:
        return f"No tasks found with status='{status}' and category='{category}'"
    
    # Sort by priority and creation date
    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    tasks.sort(key=lambda t: (priority_order.get(t["priority"], 4), t["created"]))
    
    report = f"📋 Development Tasks ({len(tasks)} found)\n"
    report += "=" * 50 + "\n\n"
    
    for task in tasks:
        status_emoji = {"todo": "⏳", "in_progress": "🔄", "done": "✅", "blocked": "🚫"}.get(task["status"], "❓")
        priority_emoji = {"urgent": "🔥", "high": "⚡", "medium": "⚪", "low": "🔽"}.get(task["priority"], "⚪")
        
        report += f"{status_emoji} #{task['id']} [{task['category'].upper()}] {priority_emoji}\n"
        report += f"   {task['title']}\n"
        if task['description']:
            report += f"   💬 {task['description']}\n"
        report += f"   📅 Created: {task['created'][:10]}\n\n"
    
    return report


@tool
def update_task_status(task_id: int, status: str, notes: str = "") -> str:
    """
    Update the status of a development task.
    
    Args:
        task_id: ID of the task to update
        status: New status (todo, in_progress, done, blocked)
        notes: Optional notes about the status change
    """
    tasks = project_ctx.context["tasks"]
    
    for task in tasks:
        if task["id"] == task_id:
            old_status = task["status"]
            task["status"] = status
            task["last_updated"] = datetime.now().isoformat()
            
            if notes:
                if "notes" not in task:
                    task["notes"] = []
                task["notes"].append({
                    "timestamp": datetime.now().isoformat(),
                    "note": notes
                })
            
            project_ctx.save_context()
            return f"✅ Updated task #{task_id} status: {old_status} → {status}"
    
    return f"❌ Task #{task_id} not found"


@tool
def generate_project_readme(include_sections: str = "description,installation,usage,contributing") -> str:
    """
    Generate a comprehensive README.md for the project.
    
    Args:
        include_sections: Comma-separated sections to include
    """
    sections = [s.strip() for s in include_sections.split(",")]
    
    # Analyze project to gather information
    project_name = project_ctx.context["project_name"]
    language = project_ctx.context.get("language", "unknown")
    framework = project_ctx.context.get("framework", "unknown")
    
    readme_content = f"# {project_name}\n\n"
    
    if "description" in sections:
        readme_content += f"""## Description

{project_name} is a {language} project{"" if framework == "unknown" else f" built with {framework}"}. 

<!-- Add your project description here -->

## Features

- Feature 1
- Feature 2  
- Feature 3

"""
    
    if "installation" in sections:
        if language == "python":
            readme_content += """## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd """ + project_name + """

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

"""
        elif language in ["javascript", "typescript"]:
            readme_content += """## Installation

### Prerequisites
- Node.js 16 or higher
- npm or yarn

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd """ + project_name + """

# Install dependencies
npm install
# or
yarn install
```

"""
        else:
            readme_content += """## Installation

```bash
# Clone the repository
git clone <repository-url>
cd """ + project_name + """

# Follow installation steps specific to your environment
```

"""
    
    if "usage" in sections:
        readme_content += """## Usage

```bash
# Basic usage example
# Add your usage instructions here
```

### Examples

```python
# Add code examples here
```

"""
    
    if "contributing" in sections:
        readme_content += """## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Additional setup for contributors
```

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions and classes
- Write tests for new features

"""
    
    if "license" in sections:
        readme_content += """## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

"""
    
    # Save README to project root
    readme_path = project_ctx.project_root / "README.md"
    try:
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        return f"""✅ Generated README.md successfully!

📁 File saved to: {readme_path}

📝 Generated sections: {', '.join(sections)}

💡 Next steps:
1. Review and customize the generated content
2. Add specific project details and examples
3. Update installation instructions if needed
4. Add screenshots or documentation links

Preview:
{'-' * 50}
{readme_content[:500]}...
"""
    except Exception as e:
        return f"❌ Error saving README.md: {e}\n\nGenerated content:\n{readme_content}"


@tool
def search_stack_overflow(query: str, tags: str = "") -> str:
    """
    Search Stack Overflow for programming questions and answers.
    Note: This is a mock implementation. In production, integrate with Stack Overflow API.
    
    Args:
        query: Search query
        tags: Comma-separated tags to filter by (python, javascript, etc.)
    """
    # Mock implementation - replace with actual Stack Overflow API
    mock_results = [
        {
            "title": f"How to {query.lower()} efficiently",
            "url": "https://stackoverflow.com/questions/12345",
            "score": 156,
            "answers": 8,
            "tags": tags.split(",") if tags else ["programming"]
        },
        {
            "title": f"Best practices for {query.lower()}",
            "url": "https://stackoverflow.com/questions/67890",
            "score": 89,
            "answers": 3,
            "tags": tags.split(",") if tags else ["best-practices"]
        }
    ]
    
    result = f"🔍 Stack Overflow Search: '{query}'\n"
    result += "=" * 50 + "\n\n"
    
    for i, item in enumerate(mock_results, 1):
        result += f"{i}. {item['title']}\n"
        result += f"   👍 {item['score']} | 💬 {item['answers']} answers\n"
        result += f"   🏷️  {', '.join(item['tags'])}\n"
        result += f"   🔗 {item['url']}\n\n"
    
    result += "💡 Tip: Always verify solutions and adapt them to your specific use case!"
    
    return result


class DevMate:
    """Main Development Assistant class"""
    
    def __init__(self, model_provider="bedrock"):
        # Configure model
        if model_provider == "bedrock":
            self.model = BedrockModel(
                model_id="us.amazon.nova-pro-v1:0",
                temperature=0.3  # Lower temperature for more consistent code analysis
            )
        else:
            self.model = None  # Use default
        
        # Initialize agent with development tools
        self.agent = Agent(
            model=self.model if model_provider == "bedrock" else None,
            tools=[
                analyze_codebase,
                review_code_file,
                git_status_summary,
                create_git_commit_message,
                add_dev_task,
                list_dev_tasks,
                update_task_status,
                generate_project_readme,
                search_stack_overflow
            ]
        )
        
        # System prompt optimized for development assistance
        self.system_prompt = """
You are DevMate, an expert AI development assistant. You help software developers with:

1. Code analysis and review
2. Project management and task tracking  
3. Git workflow assistance
4. Documentation generation
5. Debugging and problem-solving
6. Best practices and recommendations

Key behaviors:
- Provide actionable, specific advice
- Focus on code quality, security, and maintainability
- Suggest industry best practices
- Help with project organization and workflow
- Be concise but thorough in explanations
- Always consider the broader project context

When analyzing code, prioritize:
1. Security vulnerabilities
2. Performance issues
3. Maintainability concerns
4. Code style and consistency
5. Documentation completeness

Use the available tools to provide comprehensive assistance with development tasks.
"""
    
    def chat(self, user_input: str) -> str:
        """Process developer query and return response"""
        # Add project context to prompt
        context_info = f"""
Current Project Context:
- Project: {project_ctx.context['project_name']}
- Language: {project_ctx.context.get('language', 'unknown')}
- Framework: {project_ctx.context.get('framework', 'unknown')}
- Active tasks: {len([t for t in project_ctx.context['tasks'] if t['status'] != 'done'])}
- Last analysis: {project_ctx.context.get('last_analysis', 'never')}
"""
        
        full_prompt = f"{self.system_prompt}\n\n{context_info}\n\nDeveloper: {user_input}"
        
        return self.agent(full_prompt)


def main():
    """Interactive development assistant"""
    print("🚀 DevMate - AI Development Assistant")
    print("=" * 50)
    print("Your intelligent coding companion powered by Strands Agents")
    print()
    print("Available commands:")
    print("  📊 'analyze' - Analyze current codebase")
    print("  📋 'tasks' - View development tasks")
    print("  🌿 'git' - Git status summary")
    print("  📝 'readme' - Generate project README")
    print("  🔍 'search <query>' - Search Stack Overflow")
    print("  💾 'context' - Show project context")
    print("  ❌ 'quit' - Exit DevMate")
    print()
    
    # Initialize assistant
    assistant = DevMate()
    
    # Quick project setup
    try:
        if not project_ctx.context_file.exists():
            print("🔧 Setting up project context...")
            # Try to detect project type
            if (project_ctx.project_root / "requirements.txt").exists() or \
               (project_ctx.project_root / "setup.py").exists() or \
               any(project_ctx.project_root.glob("*.py")):
                project_ctx.context["language"] = "python"
            elif (project_ctx.project_root / "package.json").exists():
                project_ctx.context["language"] = "javascript"
            elif (project_ctx.project_root / "Cargo.toml").exists():
                project_ctx.context["language"] = "rust"
            elif (project_ctx.project_root / "go.mod").exists():
                project_ctx.context["language"] = "go"
            
            project_ctx.save_context()
            print(f"✅ Initialized project context for {project_ctx.context['project_name']}")
            print()
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize project context: {e}")
    
    while True:
        try:
            user_input = input("🤖 DevMate> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Happy coding! See you next time!")
                break
            
            # Handle quick commands
            if user_input.lower() == 'analyze':
                user_input = "Please analyze the current codebase"
            elif user_input.lower() == 'tasks':
                user_input = "Show me the current development tasks"
            elif user_input.lower() == 'git':
                user_input = "Give me a git status summary"
            elif user_input.lower() == 'readme':
                user_input = "Generate a README.md for this project"
            elif user_input.lower().startswith('search '):
                query = user_input[7:]
                user_input = f"Search Stack Overflow for: {query}"
            elif user_input.lower() == 'context':
                print("\n📋 Current Project Context:")
                print(json.dumps(project_ctx.context, indent=2, default=str))
                print()
                continue
            
            if not user_input:
                continue
            
            # Get response from assistant
            print("\n🤔 Thinking...")
            response = assistant.chat(user_input)
            print(f"\n🤖 DevMate: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Happy coding! See you next time!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or type 'quit' to exit.\n")


if __name__ == "__main__":
    # Example usage and demonstrations
    print("🔧 DevMate Setup Examples:")
    print("""
    
📚 Quick Start Commands:
- "analyze" - Get codebase overview
- "review src/main.py" - Review specific file  
- "add task 'implement user authentication' feature high" - Add development task
- "git" - Check git status
- "create commit message for login feature" - Generate commit message
- "search python async best practices" - Find Stack Overflow help
- "generate readme" - Create project documentation

🎯 Advanced Usage:
- "analyze codebase focusing on security issues"
- "review authentication.py for performance problems"  
- "list tasks that are blocked or high priority"
- "help me refactor the database connection code"
- "what are the current technical debt issues?"

💡 Integration Tips:
1. Run DevMate from your project root directory
2. Ensure git is initialized for full functionality
3. Use .devmate_context.json to persist project knowledge
4. Integrate with your IDE for seamless workflow

    """)
    
    main()