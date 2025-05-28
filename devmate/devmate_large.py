"""
Complete Enhanced DevMate - AI Development Assistant
===================================================

Enhanced version with large codebase support, smart file prioritization,
and batch processing capabilities.
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
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from strands import Agent, tool
from strands.models import BedrockModel
# Alternative imports:
# from strands.models.anthropic import AnthropicModel
# from strands.models.ollama import OllamaModel


# Configuration for large codebase handling
class LargeCodebaseConfig:
    MAX_FILE_SIZE_MB = 10  # Skip files larger than this
    MAX_TOTAL_FILES = 1000  # Default limit for total files analyzed
    BATCH_SIZE = 50  # Process files in batches
    CONCURRENT_WORKERS = 4  # Parallel processing threads
    PRIORITY_EXTENSIONS = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']
    
    # High priority directories (analyze first)
    PRIORITY_DIRS = ['src', 'lib', 'app', 'core', 'main', 'server', 'client', 'api']
    
    # Skip these directories entirely for large projects
    SKIP_DIRS = {
        '.git', '.svn', '.hg',
        'node_modules', 'venv', 'env', '.venv', 'virtualenv',
        '__pycache__', '.pytest_cache', '.mypy_cache', '.tox',
        'dist', 'build', 'target', 'out', 'bin', 'obj',
        '.idea', '.vscode', '.vs', '.eclipse',
        'coverage', 'htmlcov', '.coverage',
        'logs', 'log', 'tmp', 'temp', 'cache',
        'vendor', 'third_party', 'external', 'deps',
        'test_data', 'fixtures', 'mock_data', 'data'
    }


class ProjectContext:
    """Enhanced project context management"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.context_file = self.project_root / ".devmate_context.json"
        self.context = self._load_context()
        self.config = LargeCodebaseConfig()
    
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
                "last_full_analysis": None,
                "total_files": 0,
                "analyzed_files": 0,
                "issues_found": [],
                "tasks": [],
                "code_metrics": {},
                "dependencies": [],
                "git_info": {},
                "team_notes": [],
                "analysis_cache": {}
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


def _calculate_file_priority(path: Path, config: LargeCodebaseConfig) -> int:
    """Calculate priority score for a file (0-20 scale)"""
    priority = 1
    
    # Directory-based priority
    for part in path.parts:
        if part.lower() in config.PRIORITY_DIRS:
            priority += 3
    
    # Extension-based priority
    ext = path.suffix.lower()
    if ext in config.PRIORITY_EXTENSIONS:
        priority += 5
    elif ext in ['.json', '.yaml', '.yml', '.toml', '.ini']:
        priority += 2
    elif ext in ['.md', '.txt', '.rst']:
        priority += 1
    
    # File name based priority
    name = path.name.lower()
    if any(keyword in name for keyword in ['main', 'index', 'app', 'server', 'client', 'core']):
        priority += 3
    elif any(keyword in name for keyword in ['config', 'setting', 'constant']):
        priority += 2
    
    # Security-sensitive files get highest priority
    if any(keyword in name for keyword in ['auth', 'login', 'password', 'token', 'security', 'crypto']):
        priority += 10
    
    # Lower priority for deeper nesting
    depth = len(path.parts)
    if depth > 6:
        priority -= (depth - 6)
    
    return max(priority, 0)


def _is_test_file(path: Path) -> bool:
    """Check if file is likely a test file"""
    name = path.name.lower()
    parent = path.parent.name.lower()
    
    test_indicators = [
        'test_', '_test', 'tests', 'spec_', '_spec', 
        'mock_', '_mock', 'fixture', 'e2e_', 'integration_'
    ]
    
    return (
        any(indicator in name for indicator in test_indicators) or
        any(indicator in parent for indicator in test_indicators) or
        parent in {'test', 'tests', 'spec', 'specs', '__tests__', 'e2e', 'integration'}
    )


@tool
def analyze_codebase_smart(
    directory: str = ".", 
    max_files: int = 500,
    include_patterns: str = "*.py,*.js,*.ts,*.java,*.cpp,*.c,*.go,*.rs",
    skip_tests: bool = True,
    focus_areas: str = "security,performance,maintainability"
) -> str:
    """
    Smart codebase analysis optimized for large projects with intelligent file prioritization.
    
    Args:
        directory: Directory to analyze (default: current directory)
        max_files: Maximum number of files to analyze (default: 500)
        include_patterns: Comma-separated file patterns to include
        skip_tests: Whether to skip test files to focus on main codebase
        focus_areas: Comma-separated focus areas (security, performance, maintainability, complexity)
    """
    directory = Path(directory).resolve()
    config = project_ctx.config
    patterns = [p.strip() for p in include_patterns.split(",")]
    focus_list = [area.strip().lower() for area in focus_areas.split(",")]
    
    print(f"🔍 Starting smart analysis of {directory.name}...")
    print(f"📊 Limits: {max_files} files max, Skip tests: {skip_tests}")
    
    # Phase 1: Discover and prioritize files
    files_to_analyze = []
    total_files_found = 0
    
    print("📁 Discovering files...")
    
    for root, dirs, files in os.walk(directory):
        # Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in config.SKIP_DIRS]
        
        root_path = Path(root)
        
        for file in files:
            total_files_found += 1
            file_path = root_path / file
            
            # Check if file matches patterns
            if not any(fnmatch.fnmatch(file, pattern) for pattern in patterns):
                continue
            
            # Skip large files
            try:
                if file_path.stat().st_size > config.MAX_FILE_SIZE_MB * 1024 * 1024:
                    continue
            except (OSError, FileNotFoundError):
                continue
            
            # Skip test files if requested
            if skip_tests and _is_test_file(file_path):
                continue
            
            # Calculate priority
            priority = _calculate_file_priority(file_path, config)
            
            if priority > 0:
                files_to_analyze.append({
                    'path': file_path,
                    'priority': priority,
                    'size': file_path.stat().st_size,
                    'extension': file_path.suffix.lower()
                })
    
    # Sort by priority and take top files
    files_to_analyze.sort(key=lambda x: x['priority'], reverse=True)
    selected_files = files_to_analyze[:max_files]
    
    print(f"📈 Found {total_files_found} total files, analyzing top {len(selected_files)} by priority")
    
    # Phase 2: Analyze files in batches
    analysis_results = {
        'files_analyzed': 0,
        'total_lines': 0,
        'issues_found': [],
        'security_issues': [],
        'performance_issues': [],
        'complexity_issues': [],
        'languages': {},
        'file_summaries': []
    }
    
    batch_size = config.BATCH_SIZE
    for i in range(0, len(selected_files), batch_size):
        batch = selected_files[i:i + batch_size]
        
        # Process batch
        for file_info in batch:
            try:
                file_path = file_info['path']
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                lines = len(content.splitlines())
                analysis_results['files_analyzed'] += 1
                analysis_results['total_lines'] += lines
                
                # Track languages
                ext = file_info['extension']
                analysis_results['languages'][ext] = analysis_results['languages'].get(ext, 0) + 1
                
                # Quick analysis based on focus areas
                file_issues = _analyze_file_content(file_path, content, focus_list)
                
                # Aggregate issues
                analysis_results['issues_found'].extend(file_issues.get('general', []))
                analysis_results['security_issues'].extend(file_issues.get('security', []))
                analysis_results['performance_issues'].extend(file_issues.get('performance', []))
                analysis_results['complexity_issues'].extend(file_issues.get('complexity', []))
                
                # Track high-priority files
                if file_info['priority'] > 8:
                    analysis_results['file_summaries'].append({
                        'file': str(file_path.relative_to(directory)),
                        'lines': lines,
                        'priority': file_info['priority'],
                        'issues_count': sum(len(issues) for issues in file_issues.values())
                    })
                
            except Exception as e:
                print(f"⚠️ Error analyzing {file_path}: {e}")
                analysis_results['issues_found'].append(f"Error reading {file_path.name}: {str(e)}")
        
        # Progress update
        progress = min((i + batch_size) / len(selected_files) * 100, 100)
        print(f"📊 Progress: {progress:.1f}% ({analysis_results['files_analyzed']} files analyzed)")
    
    # Phase 3: Generate comprehensive report
    report = _generate_smart_analysis_report(analysis_results, directory, total_files_found, len(selected_files))
    
    # Update project context
    project_ctx.context["last_analysis"] = datetime.now().isoformat()
    project_ctx.context["total_files"] = total_files_found
    project_ctx.context["analyzed_files"] = len(selected_files)
    project_ctx.context["code_metrics"] = {
        "files_analyzed": analysis_results['files_analyzed'],
        "total_lines": analysis_results['total_lines'],
        "languages": analysis_results['languages'],
        "issues_count": len(analysis_results['issues_found']) + len(analysis_results['security_issues']) + 
                       len(analysis_results['performance_issues']) + len(analysis_results['complexity_issues'])
    }
    project_ctx.save_context()
    
    return report


def _analyze_file_content(file_path: Path, content: str, focus_areas: List[str]) -> Dict[str, List[str]]:
    """Analyze file content based on focus areas"""
    issues = {
        'general': [],
        'security': [],
        'performance': [],
        'complexity': []
    }
    
    relative_path = str(file_path.relative_to(Path.cwd()))
    
    # Security analysis
    if 'security' in focus_areas:
        security_patterns = [
            (r'password\s*=\s*["\'][^"\']*["\']', "Hardcoded password detected"),
            (r'api_key\s*=\s*["\'][^"\']*["\']', "Hardcoded API key detected"),
            (r'secret\s*=\s*["\'][^"\']*["\']', "Hardcoded secret detected"),
            (r'eval\s*\(', "Dangerous eval() usage"),
            (r'exec\s*\(', "Dangerous exec() usage"),
            (r'subprocess\.call\([^)]*shell\s*=\s*True', "Shell injection risk"),
            (r'sql.*["\'].*\+.*["\']', "Potential SQL injection"),
        ]
        
        for pattern, message in security_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues['security'].append(f"{relative_path}: {message}")
    
    # Performance analysis
    if 'performance' in focus_areas:
        perf_patterns = [
            (r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\([^)]+\)\s*\)', "Use enumerate() instead of range(len())"),
            (r'time\.sleep\s*\(\s*[1-9]\d*\s*\)', "Long sleep detected (consider async)"),
            (r'requests\.get\s*\([^)]*timeout\s*=\s*None', "Missing request timeout"),
            (r'\.append\s*\([^)]+\)\s*$', "Consider list comprehension for better performance"),
        ]
        
        for pattern, message in perf_patterns:
            if re.search(pattern, content, re.MULTILINE):
                issues['performance'].append(f"{relative_path}: {message}")
    
    # Complexity and maintainability
    if 'complexity' in focus_areas or 'maintainability' in focus_areas:
        lines = content.splitlines()
        
        # Large file check
        if len(lines) > 500:
            issues['complexity'].append(f"{relative_path}: Large file ({len(lines)} lines)")
        
        # Function complexity (simple heuristic)
        if file_path.suffix == '.py':
            functions = re.findall(r'^\s*def\s+(\w+)', content, re.MULTILINE)
            if len(functions) > 20:
                issues['complexity'].append(f"{relative_path}: Many functions ({len(functions)})")
        
        # Nesting level check
        max_nesting = 0
        current_nesting = 0
        for line in lines:
            stripped = line.strip()
            if any(keyword in stripped for keyword in ['if ', 'for ', 'while ', 'try:', 'with ']):
                current_nesting += line.count('{') + (1 if line.count('{') == 0 and stripped.endswith(':') else 0)
                max_nesting = max(max_nesting, current_nesting)
            current_nesting -= line.count('}')
            current_nesting = max(0, current_nesting)
        
        if max_nesting > 6:
            issues['complexity'].append(f"{relative_path}: High nesting level ({max_nesting})")
        
        # TODO/FIXME count
        todos = len(re.findall(r'#\s*(TODO|FIXME|HACK|XXX)', content, re.IGNORECASE))
        if todos > 5:
            issues['general'].append(f"{relative_path}: Many TODOs/FIXMEs ({todos})")
    
    return issues


def _generate_smart_analysis_report(results: Dict[str, Any], directory: Path, total_files: int, analyzed_files: int) -> str:
    """Generate a comprehensive analysis report"""
    
    # Calculate coverage
    coverage_percent = (analyzed_files / total_files * 100) if total_files > 0 else 0
    
    # Determine primary language
    languages = results['languages']
    primary_language = max(languages.items(), key=lambda x: x[1])[0] if languages else "unknown"
    
    # Count total issues
    total_issues = (len(results['security_issues']) + len(results['performance_issues']) + 
                   len(results['complexity_issues']) + len(results['issues_found']))
    
    report = f"""
🧠 Smart Codebase Analysis Report
=================================
Project: {directory.name}
Analysis date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 Coverage Summary:
• Total files in project: {total_files:,}
• Files analyzed: {analyzed_files:,} ({coverage_percent:.1f}% coverage)
• Lines of code analyzed: {results['total_lines']:,}
• Primary language: {primary_language}

🔍 Issue Summary:
• 🔒 Security issues: {len(results['security_issues'])}
• ⚡ Performance issues: {len(results['performance_issues'])}
• 🧩 Complexity issues: {len(results['complexity_issues'])}
• 📝 General issues: {len(results['issues_found'])}
• 📈 Total issues: {total_issues}

🌐 Languages Detected:
"""
    
    for ext, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
        report += f"  {ext}: {count} files\n"
    
    # Critical issues (top priority)
    critical_issues = results['security_issues'][:5]  # Top 5 security issues
    if critical_issues:
        report += f"\n🚨 Critical Security Issues (Top 5):\n"
        for i, issue in enumerate(critical_issues, 1):
            report += f"  {i}. {issue}\n"
    
    # High-impact performance issues
    perf_issues = results['performance_issues'][:3]
    if perf_issues:
        report += f"\n⚡ Performance Issues (Top 3):\n"
        for i, issue in enumerate(perf_issues, 1):
            report += f"  {i}. {issue}\n"
    
    # Complex files that need attention
    complex_files = [f for f in results['file_summaries'] if f['issues_count'] > 3]
    if complex_files:
        report += f"\n🎯 Files Needing Attention:\n"
        for file_info in sorted(complex_files, key=lambda x: x['issues_count'], reverse=True)[:5]:
            report += f"  • {file_info['file']} - {file_info['issues_count']} issues ({file_info['lines']} lines)\n"
    
    # Recommendations based on findings
    report += f"\n💡 Smart Recommendations:\n"
    
    if len(results['security_issues']) > 0:
        report += f"  🔒 ADDRESS SECURITY: {len(results['security_issues'])} security issues found - review immediately\n"
    
    if len(results['performance_issues']) > 5:
        report += f"  ⚡ OPTIMIZE PERFORMANCE: {len(results['performance_issues'])} performance issues detected\n"
    
    if any(f['lines'] > 500 for f in results['file_summaries']):
        report += f"  🔧 REFACTOR LARGE FILES: Consider breaking down files >500 lines\n"
    
    if coverage_percent < 50:
        report += f"  📈 EXPAND ANALYSIS: Only analyzed {coverage_percent:.1f}% of codebase - consider full scan\n"
    
    # Next steps
    report += f"""
📋 Suggested Next Steps:
1. Review security issues with: devmate review-security
2. Focus on high-priority files: devmate analyze {' '.join(f['file'] for f in complex_files[:3])}
3. Run full analysis if needed: devmate analyze --max-files 1000
4. Set up automated checks in CI/CD pipeline

⏱️  Analysis completed in smart mode - focused on {analyzed_files} most important files
💾 Results cached in .devmate_context.json for future reference
"""
    
    return report


# Keep all the original DevMate tools (git_status_summary, create_git_commit_message, etc.)
# [Previous tools from original DevMate would go here - truncated for space]

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
        
        # Parse status
        status_lines = status_result.stdout.strip().split('\n') if status_result.stdout.strip() else []
        modified = [line[3:] for line in status_lines if line.startswith(' M')]
        added = [line[3:] for line in status_lines if line.startswith('A ')]
        untracked = [line[3:] for line in status_lines if line.startswith('??')]
        
        report = f"""
🌿 Git Status Summary
====================
Current branch: {current_branch}
Repository: {project_ctx.project_root.name}

📊 Working Directory Status:
• Modified files: {len(modified)}
• Added files: {len(added)} 
• Untracked files: {len(untracked)}
"""
        
        if modified:
            report += f"\n📝 Modified files:\n"
            report += '\n'.join(f"  • {file}" for file in modified[:10])
        
        if untracked:
            report += f"\n❓ Untracked files:\n"
            report += '\n'.join(f"  • {file}" for file in untracked[:5])
        
        if log_result.returncode == 0:
            report += f"\n📈 Recent commits:\n"
            commits = log_result.stdout.strip().split('\n')[:5]
            report += '\n'.join(f"  • {commit}" for commit in commits)
        
        return report
        
    except Exception as e:
        return f"Error getting Git status: {e}"


@tool
def add_dev_task(title: str, description: str = "", priority: str = "medium", category: str = "general") -> str:
    """Add a development task to the project."""
    task = {
        "id": len(project_ctx.context["tasks"]) + 1,
        "title": title,
        "description": description,
        "priority": priority,
        "category": category,
        "status": "todo",
        "created": datetime.now().isoformat()
    }
    
    project_ctx.context["tasks"].append(task)
    project_ctx.save_context()
    
    return f"✅ Added task #{task['id']}: {title} ({priority} priority, {category} category)"


@tool
def quick_security_scan(directory: str = ".") -> str:
    """Quick security-focused scan of the codebase."""
    return analyze_codebase_smart(
        directory=directory,
        max_files=200,
        skip_tests=True,
        focus_areas="security"
    )


@tool
def performance_check(directory: str = ".") -> str:
    """Quick performance-focused analysis of the codebase."""
    return analyze_codebase_smart(
        directory=directory,
        max_files=300,
        skip_tests=True,
        focus_areas="performance"
    )


class EnhancedDevMate:
    """Enhanced DevMate with large codebase support"""
    
    def __init__(self, model_provider="bedrock"):
        # Configure model
        if model_provider == "bedrock":
            self.model = BedrockModel(
                model_id="us.amazon.nova-pro-v1:0",
                temperature=0.3
            )
        else:
            self.model = None
        
        # Initialize agent with enhanced tools
        self.agent = Agent(
            model=self.model if model_provider == "bedrock" else None,
            tools=[
                analyze_codebase_smart,
                git_status_summary,
                add_dev_task,
                quick_security_scan,
                performance_check
            ]
        )
        
        self.system_prompt = """
You are Enhanced DevMate, an expert AI development assistant optimized for large codebases. You help with:

1. Smart code analysis with intelligent file prioritization
2. Security vulnerability detection
3. Performance optimization suggestions
4. Project management and task tracking
5. Git workflow assistance

Key behaviors:
- Prioritize security issues above all else
- Focus on high-impact files rather than analyzing everything
- Provide actionable, specific recommendations
- Consider project size and complexity in analysis approach
- Help developers work efficiently on large codebases

When analyzing large projects, use smart analysis to focus on the most important files first.
Always explain your reasoning and provide clear next steps.
"""
    
    def chat(self, user_input: str) -> str:
        """Process developer query with enhanced context"""
        context_info = f"""
Current Project Context:
- Project: {project_ctx.context['project_name']}
- Total files: {project_ctx.context.get('total_files', 'unknown')}
- Last analyzed: {project_ctx.context.get('analyzed_files', 'unknown')} files
- Last analysis: {project_ctx.context.get('last_analysis', 'never')}
- Active tasks: {len([t for t in project_ctx.context['tasks'] if t['status'] != 'done'])}
"""
        
        full_prompt = f"{self.system_prompt}\n\n{context_info}\n\nDeveloper: {user_input}"
        return self.agent(full_prompt)


def main():
    """Interactive enhanced development assistant"""
    print("🚀 Enhanced DevMate - AI Development Assistant")
    print("=" * 55)
    print("Optimized for large codebases with smart analysis")
    print()
    print("Available commands:")
    print("  📊 'analyze' - Smart codebase analysis")
    print("  🔒 'security' - Quick security scan")  
    print("  ⚡'performance' - Performance check")
    print("  📋 'tasks' - View development tasks")
    print("  🌿 'git' - Git status summary")
    print("  💾 'context' - Show project context")
    print("  ❌ 'quit' - Exit Enhanced DevMate")
    print()
    
    # Initialize assistant
    assistant = EnhancedDevMate()
    
    # Project detection
    try:
        total_files = sum(1 for _ in Path('.').rglob('*') if _.is_file())
        print(f"🔍 Detected project with ~{total_files:,} files")
        
        if total_files > 10000:
            print("📈 Large codebase detected - will use smart analysis")
        elif total_files > 1000:
            print("📊 Medium codebase detected - optimized analysis available")
        else:
            print("📁 Small-medium codebase - full analysis available")
        print()
        
        project_ctx.context['total_files'] = total_files
        project_ctx.save_context()
        
    except Exception as e:
        print(f"⚠️ Could not detect project size: {e}")
    
    while True:
        try:
            user_input = input("🤖 Enhanced DevMate> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Happy coding! Enhanced analysis saved to .devmate_context.json")
                break
            
            # Handle quick commands
            if user_input.lower() == 'analyze':
                user_input = "Run smart codebase analysis focusing on the most important files"
            elif user_input.lower() == 'security':
                user_input = "Run a quick security scan of the codebase"
            elif user_input.lower() == 'performance':
                user_input = "Check for performance issues in the codebase"
            elif user_input.lower() == 'tasks':
                user_input = "Show me the current development tasks"
            elif user_input.lower() == 'git':
                user_input = "Give me a git status summary"
            elif user_input.lower() == 'context':
                print("\n📋 Current Project Context:")
                print(json.dumps(project_ctx.context, indent=2, default=str))
                print()
                continue
            
            if not user_input:
                continue
            
            # Get response from assistant
            print("\n🧠 Analyzing...")
            response = assistant.chat(user_input)
            print(f"\n🤖 Enhanced DevMate: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Happy coding!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or type 'quit' to exit.\n")


if __name__ == "__main__":
    main()