"""
TechScout - AI Tool Research & Evaluation Assistant
==================================================

A comprehensive research assistant that helps software developers evaluate new AI tools,
frameworks, and technologies by gathering information from multiple sources, analyzing
pros/cons, identifying risks, and maintaining a searchable knowledge base for team decisions.

Features:
- Multi-source research (Reddit, YouTube, industry sites, GitHub)
- Structured evaluation with scoring matrices
- Risk assessment and security analysis
- Team knowledge base with searchable evaluations
- Integration recommendations and migration paths
- Executive summaries for leadership decisions
"""

import os
import json
import requests
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from urllib.parse import urlencode, urlparse
import hashlib

from strands import Agent, tool
from strands.models import BedrockModel
# Alternative imports:
# from strands.models.anthropic import AnthropicModel
# from strands.models.ollama import OllamaModel


@dataclass
class TechEvaluation:
    """Structure for technology evaluations"""
    name: str
    category: str
    version: str
    evaluated_date: str
    evaluator: str
    
    # Research sources
    sources_researched: List[str]
    github_repo: Optional[str]
    official_website: Optional[str]
    
    # Evaluation scores (1-10 scale)
    ease_of_use: int
    documentation_quality: int
    community_support: int
    performance: int
    security: int
    maintenance_burden: int
    integration_complexity: int
    
    # Analysis
    pros: List[str]
    cons: List[str]
    risks: List[str]
    alternatives: List[str]
    
    # Business considerations
    licensing: str
    cost_analysis: str
    team_skill_requirements: List[str]
    migration_effort: str
    
    # Decision
    recommendation: str  # "adopt", "trial", "assess", "hold"
    reasoning: str
    next_steps: List[str]
    
    # Metadata
    tags: List[str]
    related_evaluations: List[str]
    last_updated: str


class TechEvaluationManager:
    """Manages technology evaluations and knowledge base"""
    
    def __init__(self, data_dir: str = "tech_evaluations"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.evaluations_file = self.data_dir / "evaluations.json"
        self.evaluations = self._load_evaluations()
    
    def _load_evaluations(self) -> Dict[str, Dict]:
        """Load existing evaluations"""
        if self.evaluations_file.exists():
            with open(self.evaluations_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_evaluations(self):
        """Save evaluations to file"""
        with open(self.evaluations_file, 'w') as f:
            json.dump(self.evaluations, f, indent=2, default=str)
    
    def add_evaluation(self, evaluation: TechEvaluation):
        """Add or update a technology evaluation"""
        eval_id = self._generate_eval_id(evaluation.name)
        self.evaluations[eval_id] = asdict(evaluation)
        self.save_evaluations()
        return eval_id
    
    def get_evaluation(self, name: str) -> Optional[Dict]:
        """Get evaluation by technology name"""
        eval_id = self._generate_eval_id(name)
        return self.evaluations.get(eval_id)
    
    def search_evaluations(self, query: str) -> List[Dict]:
        """Search evaluations by name, tags, or category"""
        results = []
        query_lower = query.lower()
        
        for eval_data in self.evaluations.values():
            if (query_lower in eval_data['name'].lower() or
                query_lower in eval_data['category'].lower() or
                any(query_lower in tag.lower() for tag in eval_data['tags'])):
                results.append(eval_data)
        
        return results
    
    def _generate_eval_id(self, name: str) -> str:
        """Generate consistent ID for technology"""
        return hashlib.md5(name.lower().strip().encode()).hexdigest()[:12]


# Global evaluation manager
eval_manager = TechEvaluationManager()


@tool
def research_tech_tool(
    tool_name: str,
    category: str = "ai-development",
    sources: str = "github,reddit,hackernews,official",
    depth: str = "standard"
) -> str:
    """
    Research a new technology tool from multiple sources.
    
    Args:
        tool_name: Name of the technology/tool to research
        category: Category (ai-development, frontend, backend, devops, etc.)
        sources: Comma-separated sources (github, reddit, hackernews, official, youtube)
        depth: Research depth (quick, standard, comprehensive)
    """
    print(f"🔍 Starting research on {tool_name}...")
    
    sources_list = [s.strip() for s in sources.split(',')]
    research_data = {
        'tool_name': tool_name,
        'category': category,
        'research_date': datetime.now().isoformat(),
        'sources_researched': sources_list,
        'findings': {}
    }
    
    # Research from each source
    for source in sources_list:
        print(f"📊 Researching from {source}...")
        
        if source == 'github':
            research_data['findings']['github'] = _research_github(tool_name)
        elif source == 'reddit':
            research_data['findings']['reddit'] = _research_reddit(tool_name)
        elif source == 'hackernews':
            research_data['findings']['hackernews'] = _research_hackernews(tool_name)
        elif source == 'official':
            research_data['findings']['official'] = _research_official_sources(tool_name)
        elif source == 'youtube':
            research_data['findings']['youtube'] = _research_youtube(tool_name)
    
    # Save research data
    research_file = eval_manager.data_dir / f"research_{tool_name.replace(' ', '_').lower()}.json"
    with open(research_file, 'w') as f:
        json.dump(research_data, f, indent=2, default=str)
    
    # Generate research summary
    summary = _generate_research_summary(research_data)
    
    return f"""
🔍 Research Complete: {tool_name}
================================

{summary}

📁 Detailed research saved to: {research_file}

💡 Next steps:
1. Run: evaluate_tech_tool "{tool_name}" to create structured evaluation
2. Review findings and add team-specific considerations
3. Make adoption recommendation based on research
"""


def _research_github(tool_name: str) -> Dict[str, Any]:
    """Research tool on GitHub (mock implementation - replace with GitHub API)"""
    # Mock GitHub research - replace with actual GitHub API calls
    return {
        'repository_found': True,
        'stars': 1250,
        'forks': 89,
        'issues_open': 23,
        'last_commit': '2 days ago',
        'license': 'MIT',
        'primary_language': 'Python',
        'contributors': 15,
        'release_frequency': 'Monthly',
        'documentation_quality': 'Good - comprehensive README and docs/',
        'community_activity': 'Active - regular commits and issue responses'
    }


def _research_reddit(tool_name: str) -> Dict[str, Any]:
    """Research tool mentions on Reddit (mock implementation)"""
    # Mock Reddit research - replace with Reddit API
    return {
        'mentions_found': 8,
        'sentiment': 'Mostly positive',
        'common_topics': [
            'Easy to integrate',
            'Good performance',
            'Some learning curve',
            'Documentation could be better'
        ],
        'subreddits': ['r/MachineLearning', 'r/programming', 'r/Python'],
        'recent_discussions': [
            'User reports 3x speed improvement over alternative',
            'Integration guide shared by community',
            'Minor bugs reported but actively fixed'
        ]
    }


def _research_hackernews(tool_name: str) -> Dict[str, Any]:
    """Research tool on Hacker News (mock implementation)"""
    return {
        'posts_found': 3,
        'average_score': 45,
        'discussion_quality': 'High - technical depth',
        'key_points': [
            'Praised for innovative approach',
            'Some concerns about vendor lock-in',
            'Comparison with established alternatives',
            'Real-world usage examples shared'
        ]
    }


def _research_official_sources(tool_name: str) -> Dict[str, Any]:
    """Research official documentation and website"""
    return {
        'official_website': f"https://{tool_name.lower().replace(' ', '')}.com",
        'documentation_quality': 'Comprehensive',
        'getting_started_guide': True,
        'api_documentation': True,
        'examples_provided': True,
        'support_channels': ['Discord', 'GitHub Issues', 'Email'],
        'pricing_model': 'Open source with enterprise support',
        'company_backing': 'Well-funded startup',
        'compliance_certifications': ['SOC2', 'GDPR compliant']
    }


def _research_youtube(tool_name: str) -> Dict[str, Any]:
    """Research tool tutorials and reviews on YouTube"""
    return {
        'tutorial_videos': 12,
        'review_videos': 5,
        'view_counts': 'High engagement (10k+ avg views)',
        'creator_sentiment': 'Positive',
        'common_use_cases': [
            'API development automation',
            'Code generation workflows',
            'Integration with existing tools'
        ],
        'learning_resources': 'Good - multiple quality tutorials available'
    }


def _generate_research_summary(research_data: Dict[str, Any]) -> str:
    """Generate a summary of research findings"""
    findings = research_data['findings']
    
    summary = f"📊 Research Summary for {research_data['tool_name']}:\n\n"
    
    # GitHub insights
    if 'github' in findings:
        gh = findings['github']
        summary += f"🐙 GitHub: {gh['stars']} stars, {gh['contributors']} contributors, {gh['license']} license\n"
        summary += f"   Activity: {gh['community_activity']}\n\n"
    
    # Community sentiment
    if 'reddit' in findings:
        reddit = findings['reddit']
        summary += f"💬 Community Sentiment: {reddit['sentiment']}\n"
        summary += f"   Key feedback: {', '.join(reddit['common_topics'][:3])}\n\n"
    
    # Technical assessment
    if 'official' in findings:
        official = findings['official']
        summary += f"📚 Documentation: {official['documentation_quality']}\n"
        summary += f"💰 Pricing: {official['pricing_model']}\n\n"
    
    return summary


@tool
def evaluate_tech_tool(
    tool_name: str,
    research_notes: str = "",
    team_context: str = "general development team",
    evaluation_criteria: str = "standard"
) -> str:
    """
    Create a structured evaluation of a technology tool.
    
    Args:
        tool_name: Name of the technology to evaluate
        research_notes: Additional research notes or findings
        team_context: Team context (frontend, backend, devops, etc.)
        evaluation_criteria: Evaluation criteria (standard, security-focused, performance-focused)
    """
    print(f"📋 Creating structured evaluation for {tool_name}...")
    
    # Check if research data exists
    research_file = eval_manager.data_dir / f"research_{tool_name.replace(' ', '_').lower()}.json"
    research_data = {}
    if research_file.exists():
        with open(research_file, 'r') as f:
            research_data = json.load(f)
    
    # Create evaluation framework
    evaluation = TechEvaluation(
        name=tool_name,
        category=research_data.get('category', 'unknown'),
        version="latest",
        evaluated_date=datetime.now().isoformat(),
        evaluator=os.getenv('USER', 'developer'),
        
        # Sources (from research data)
        sources_researched=research_data.get('sources_researched', []),
        github_repo=_extract_github_repo(research_data),
        official_website=_extract_official_website(research_data),
        
        # Initial scoring (would be refined based on research)
        ease_of_use=_score_ease_of_use(research_data),
        documentation_quality=_score_documentation(research_data),
        community_support=_score_community(research_data),
        performance=_score_performance(research_data),
        security=_score_security(research_data),
        maintenance_burden=_score_maintenance(research_data),
        integration_complexity=_score_integration(research_data),
        
        # Analysis (generated from research)
        pros=_extract_pros(research_data),
        cons=_extract_cons(research_data),
        risks=_identify_risks(research_data, evaluation_criteria),
        alternatives=_suggest_alternatives(tool_name, research_data),
        
        # Business considerations
        licensing=_extract_licensing(research_data),
        cost_analysis=_analyze_costs(research_data),
        team_skill_requirements=_assess_skill_requirements(research_data, team_context),
        migration_effort=_assess_migration_effort(research_data, team_context),
        
        # Decision framework
        recommendation=_generate_recommendation(research_data, evaluation_criteria),
        reasoning=_generate_reasoning(research_data, evaluation_criteria),
        next_steps=_suggest_next_steps(tool_name, research_data),
        
        # Metadata
        tags=_generate_tags(tool_name, research_data),
        related_evaluations=[],
        last_updated=datetime.now().isoformat()
    )
    
    # Save evaluation
    eval_id = eval_manager.add_evaluation(evaluation)
    
    # Generate evaluation report
    report = _generate_evaluation_report(evaluation)
    
    # Save detailed report
    report_file = eval_manager.data_dir / f"evaluation_report_{tool_name.replace(' ', '_').lower()}.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    return f"""
📋 Evaluation Complete: {tool_name}
===================================

{report}

💾 Evaluation saved with ID: {eval_id}
📄 Detailed report: {report_file}

🎯 Recommendation: {evaluation.recommendation.upper()}
💡 Reasoning: {evaluation.reasoning}

📋 Next Steps:
{chr(10).join('• ' + step for step in evaluation.next_steps)}
"""


def _score_ease_of_use(research_data: Dict) -> int:
    """Score ease of use based on research data (1-10)"""
    # Example scoring logic based on research findings
    base_score = 5
    
    if 'github' in research_data.get('findings', {}):
        gh = research_data['findings']['github']
        if 'Good' in gh.get('documentation_quality', ''):
            base_score += 2
    
    if 'reddit' in research_data.get('findings', {}):
        reddit = research_data['findings']['reddit']
        if 'Easy to integrate' in reddit.get('common_topics', []):
            base_score += 1
        if 'learning curve' in str(reddit.get('common_topics', [])).lower():
            base_score -= 1
    
    return min(max(base_score, 1), 10)


def _score_documentation(research_data: Dict) -> int:
    """Score documentation quality (1-10)"""
    base_score = 5
    
    if 'official' in research_data.get('findings', {}):
        official = research_data['findings']['official']
        quality = official.get('documentation_quality', '').lower()
        if 'comprehensive' in quality:
            base_score = 8
        elif 'good' in quality:
            base_score = 7
        elif 'basic' in quality:
            base_score = 4
    
    return min(max(base_score, 1), 10)


def _score_community(research_data: Dict) -> int:
    """Score community support (1-10)"""
    base_score = 5
    
    if 'github' in research_data.get('findings', {}):
        gh = research_data['findings']['github']
        stars = gh.get('stars', 0)
        if stars > 1000:
            base_score += 2
        elif stars > 100:
            base_score += 1
        
        if 'Active' in gh.get('community_activity', ''):
            base_score += 1
    
    return min(max(base_score, 1), 10)


def _score_performance(research_data: Dict) -> int:
    """Score performance based on available data"""
    base_score = 6  # Neutral assumption
    
    if 'reddit' in research_data.get('findings', {}):
        reddit = research_data['findings']['reddit']
        topics = reddit.get('common_topics', [])
        if any('performance' in topic.lower() or 'speed' in topic.lower() for topic in topics):
            if any('improvement' in topic.lower() for topic in topics):
                base_score += 2
    
    return min(max(base_score, 1), 10)


def _score_security(research_data: Dict) -> int:
    """Score security considerations"""
    base_score = 6
    
    if 'official' in research_data.get('findings', {}):
        official = research_data['findings']['official']
        if official.get('compliance_certifications'):
            base_score += 2
    
    return min(max(base_score, 1), 10)


def _score_maintenance(research_data: Dict) -> int:
    """Score maintenance burden"""
    base_score = 5
    
    if 'github' in research_data.get('findings', {}):
        gh = research_data['findings']['github']
        if gh.get('release_frequency') == 'Monthly':
            base_score += 1
        elif gh.get('release_frequency') == 'Weekly':
            base_score -= 1  # Too frequent might be unstable
    
    return min(max(base_score, 1), 10)


def _score_integration(research_data: Dict) -> int:
    """Score integration complexity"""
    base_score = 5
    
    if 'reddit' in research_data.get('findings', {}):
        reddit = research_data['findings']['reddit']
        if 'Easy to integrate' in reddit.get('common_topics', []):
            base_score += 2
    
    return min(max(base_score, 1), 10)


def _extract_pros(research_data: Dict) -> List[str]:
    """Extract pros from research data"""
    pros = []
    
    if 'reddit' in research_data.get('findings', {}):
        reddit = research_data['findings']['reddit']
        for topic in reddit.get('common_topics', []):
            if any(positive in topic.lower() for positive in ['easy', 'good', 'fast', 'simple']):
                pros.append(topic)
    
    if 'github' in research_data.get('findings', {}):
        gh = research_data['findings']['github']
        if gh.get('stars', 0) > 500:
            pros.append(f"Strong community adoption ({gh['stars']} stars)")
        if 'Active' in gh.get('community_activity', ''):
            pros.append("Active development and maintenance")
    
    return pros or ["Requires detailed analysis to identify specific benefits"]


def _extract_cons(research_data: Dict) -> List[str]:
    """Extract cons from research data"""
    cons = []
    
    if 'reddit' in research_data.get('findings', {}):
        reddit = research_data['findings']['reddit']
        for topic in reddit.get('common_topics', []):
            if any(negative in topic.lower() for negative in ['difficult', 'complex', 'slow', 'bug']):
                cons.append(topic)
    
    if 'hackernews' in research_data.get('findings', {}):
        hn = research_data['findings']['hackernews']
        for point in hn.get('key_points', []):
            if any(concern in point.lower() for concern in ['concern', 'issue', 'problem']):
                cons.append(point)
    
    return cons or ["Requires detailed analysis to identify potential drawbacks"]


def _identify_risks(research_data: Dict, evaluation_criteria: str) -> List[str]:
    """Identify potential risks"""
    risks = []
    
    # Vendor lock-in risk
    if 'hackernews' in research_data.get('findings', {}):
        hn = research_data['findings']['hackernews']
        if any('lock-in' in point.lower() for point in hn.get('key_points', [])):
            risks.append("Potential vendor lock-in concerns raised by community")
    
    # Maturity risk
    if 'github' in research_data.get('findings', {}):
        gh = research_data['findings']['github']
        if gh.get('contributors', 0) < 5:
            risks.append("Small contributor base - bus factor risk")
        if 'beta' in gh.get('version', '').lower():
            risks.append("Tool still in beta - stability concerns")
    
    # Security risks (if security-focused evaluation)
    if 'security' in evaluation_criteria.lower():
        if 'official' in research_data.get('findings', {}):
            official = research_data['findings']['official']
            if not official.get('compliance_certifications'):
                risks.append("No compliance certifications - may not meet enterprise security requirements")
    
    return risks or ["Standard technology adoption risks apply"]


def _suggest_alternatives(tool_name: str, research_data: Dict) -> List[str]:
    """Suggest alternative tools"""
    # This would typically be based on a knowledge base of similar tools
    category = research_data.get('category', '').lower()
    
    alternatives_map = {
        'ai-development': ['GitHub Copilot', 'Cursor', 'Replit AI', 'Codeium'],
        'frontend': ['React', 'Vue.js', 'Angular', 'Svelte'],
        'backend': ['Node.js', 'Python Flask/Django', 'Go', 'Rust'],
        'devops': ['Docker', 'Kubernetes', 'Terraform', 'Ansible']
    }
    
    return alternatives_map.get(category, ['Research category-specific alternatives'])


def _extract_github_repo(research_data: Dict) -> Optional[str]:
    """Extract GitHub repository URL from research data"""
    if 'github' in research_data.get('findings', {}):
        return f"https://github.com/example/{research_data['tool_name'].lower()}"
    return None


def _extract_official_website(research_data: Dict) -> Optional[str]:
    """Extract official website from research data"""
    if 'official' in research_data.get('findings', {}):
        return research_data['findings']['official'].get('official_website')
    return None


def _extract_licensing(research_data: Dict) -> str:
    """Extract licensing information"""
    if 'github' in research_data.get('findings', {}):
        return research_data['findings']['github'].get('license', 'Unknown')
    return 'Unknown - requires investigation'


def _analyze_costs(research_data: Dict) -> str:
    """Analyze cost implications"""
    if 'official' in research_data.get('findings', {}):
        pricing = research_data['findings']['official'].get('pricing_model', '')
        if 'open source' in pricing.lower():
            return 'Open source - no licensing costs, consider support costs'
        else:
            return 'Commercial - evaluate pricing tiers and ROI'
    return 'Cost structure requires investigation'


def _assess_skill_requirements(research_data: Dict, team_context: str) -> List[str]:
    """Assess required skills for adoption"""
    skills = []
    
    if 'github' in research_data.get('findings', {}):
        language = research_data['findings']['github'].get('primary_language')
        if language:
            skills.append(f"{language} programming knowledge")
    
    # Add context-specific skills
    if 'ai' in team_context.lower():
        skills.append('Machine learning fundamentals')
        skills.append('API integration experience')
    
    return skills or ['General software development skills']


def _assess_migration_effort(research_data: Dict, team_context: str) -> str:
    """Assess effort required for adoption/migration"""
    if 'reddit' in research_data.get('findings', {}):
        reddit = research_data['findings']['reddit']
        if 'Easy to integrate' in reddit.get('common_topics', []):
            return 'Low - tool appears to integrate easily with existing workflows'
    
    return 'Medium - requires planning and gradual rollout'


def _generate_recommendation(research_data: Dict, evaluation_criteria: str) -> str:
    """Generate adoption recommendation"""
    # Simple scoring logic - in reality this would be more sophisticated
    positive_indicators = 0
    negative_indicators = 0
    
    # Check various indicators
    if 'github' in research_data.get('findings', {}):
        gh = research_data['findings']['github']
        if gh.get('stars', 0) > 500:
            positive_indicators += 1
        if 'Active' in gh.get('community_activity', ''):
            positive_indicators += 1
        if gh.get('contributors', 0) < 3:
            negative_indicators += 1
    
    if 'reddit' in research_data.get('findings', {}):
        reddit = research_data['findings']['reddit']
        if reddit.get('sentiment') == 'Mostly positive':
            positive_indicators += 1
    
    # Make recommendation
    if positive_indicators >= 3 and negative_indicators == 0:
        return 'adopt'
    elif positive_indicators >= 2:
        return 'trial'
    elif positive_indicators >= 1:
        return 'assess'
    else:
        return 'hold'


def _generate_reasoning(research_data: Dict, evaluation_criteria: str) -> str:
    """Generate reasoning for recommendation"""
    reasoning_parts = []
    
    if 'github' in research_data.get('findings', {}):
        gh = research_data['findings']['github']
        reasoning_parts.append(f"GitHub metrics show {gh.get('stars', 0)} stars with {gh.get('community_activity', 'unknown')} community")
    
    if 'reddit' in research_data.get('findings', {}):
        reddit = research_data['findings']['reddit']
        reasoning_parts.append(f"Community sentiment is {reddit.get('sentiment', 'mixed')}")
    
    return '. '.join(reasoning_parts) if reasoning_parts else 'Based on available research data and evaluation criteria'


def _suggest_next_steps(tool_name: str, research_data: Dict) -> List[str]:
    """Suggest concrete next steps"""
    steps = [
        f"Set up proof-of-concept with {tool_name}",
        "Evaluate against current toolchain",
        "Assess team training requirements",
        "Create migration plan if adopting"
    ]
    
    if 'github' in research_data.get('findings', {}):
        steps.insert(0, "Review GitHub repository and documentation")
    
    return steps


def _generate_tags(tool_name: str, research_data: Dict) -> List[str]:
    """Generate tags for categorization"""
    tags = [research_data.get('category', 'uncategorized')]
    
    if 'github' in research_data.get('findings', {}):
        gh = research_data['findings']['github']
        if gh.get('primary_language'):
            tags.append(gh['primary_language'].lower())
    
    tags.extend(['ai-tool', 'development', '2025'])
    return tags


def _generate_evaluation_report(evaluation: TechEvaluation) -> str:
    """Generate comprehensive evaluation report"""
    
    report = f"""# Technology Evaluation Report: {evaluation.name}

**Evaluation Date:** {evaluation.evaluated_date[:10]}  
**Evaluator:** {evaluation.evaluator}  
**Category:** {evaluation.category}  
**Recommendation:** {evaluation.recommendation.upper()}

## Executive Summary

**Bottom Line:** {evaluation.reasoning}

**Key Metrics:**
- Ease of Use: {evaluation.ease_of_use}/10
- Documentation: {evaluation.documentation_quality}/10  
- Community Support: {evaluation.community_support}/10
- Security: {evaluation.security}/10

## Detailed Analysis

### Strengths
{chr(10).join('• ' + pro for pro in evaluation.pros)}

### Concerns
{chr(10).join('• ' + con for con in evaluation.cons)}

### Risk Assessment
{chr(10).join('• ' + risk for risk in evaluation.risks)}

## Business Considerations

**Licensing:** {evaluation.licensing}  
**Cost Analysis:** {evaluation.cost_analysis}  
**Migration Effort:** {evaluation.migration_effort}

**Required Skills:**
{chr(10).join('• ' + skill for skill in evaluation.team_skill_requirements)}

## Alternatives Considered
{chr(10).join('• ' + alt for alt in evaluation.alternatives)}

## Implementation Plan

**Next Steps:**
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(evaluation.next_steps))}

## Resources

**GitHub:** {evaluation.github_repo or 'Not available'}  
**Official Site:** {evaluation.official_website or 'Not available'}  
**Research Sources:** {', '.join(evaluation.sources_researched)}

---
*This evaluation can be referenced for future technology decisions and shared with leadership.*
"""
    
    return report


@tool
def search_evaluations(query: str) -> str:
    """
    Search existing technology evaluations.
    
    Args:
        query: Search query (tool name, category, or tag)
    """
    results = eval_manager.search_evaluations(query)
    
    if not results:
        return f"No evaluations found for '{query}'. Use research_tech_tool to start a new evaluation."
    
    response = f"🔍 Found {len(results)} evaluation(s) for '{query}':\n\n"
    
    for eval_data in results:
        response += f"**{eval_data['name']}** ({eval_data['category']})\n"
        response += f"  📅 Evaluated: {eval_data['evaluated_date'][:10]}\n"
        response += f"  🎯 Recommendation: {eval_data['recommendation'].upper()}\n"
        response += f"  📊 Scores: Ease {eval_data['ease_of_use']}/10, Docs {eval_data['documentation_quality']}/10\n"
        response += f"  💭 Reasoning: {eval_data['reasoning'][:100]}...\n"
        response += f"  🏷️ Tags: {', '.join(eval_data['tags'][:3])}\n\n"
    
    return response


@tool
def generate_team_report(category: str = "all", time_period: str = "last_6_months") -> str:
    """
    Generate a comprehensive report of all evaluations for team/leadership review.
    
    Args:
        category: Filter by category (all, ai-development, frontend, backend, devops)
        time_period: Time period (last_month, last_3_months, last_6_months, all_time)
    """
    print("📊 Generating team evaluation report...")
    
    # Filter evaluations by category and time
    all_evaluations = list(eval_manager.evaluations.values())
    
    if category != "all":
        all_evaluations = [e for e in all_evaluations if e['category'] == category]
    
    # Time filtering
    if time_period != "all_time":
        cutoff_date = datetime.now()
        if time_period == "last_month":
            cutoff_date -= timedelta(days=30)
        elif time_period == "last_3_months":
            cutoff_date -= timedelta(days=90)
        elif time_period == "last_6_months":
            cutoff_date -= timedelta(days=180)
        
        all_evaluations = [
            e for e in all_evaluations 
            if datetime.fromisoformat(e['evaluated_date']) > cutoff_date
        ]
    
    if not all_evaluations:
        return f"No evaluations found for category '{category}' in {time_period}"
    
    # Generate comprehensive report
    report = f"""
# Technology Evaluation Summary Report

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Period:** {time_period.replace('_', ' ').title()}
**Category Filter:** {category.title()}
**Total Evaluations:** {len(all_evaluations)}

## Executive Dashboard

### Adoption Recommendations
"""
    
    # Categorize by recommendation
    adopt_count = len([e for e in all_evaluations if e['recommendation'] == 'adopt'])
    trial_count = len([e for e in all_evaluations if e['recommendation'] == 'trial'])
    assess_count = len([e for e in all_evaluations if e['recommendation'] == 'assess'])
    hold_count = len([e for e in all_evaluations if e['recommendation'] == 'hold'])
    
    report += f"""
- 🟢 **ADOPT:** {adopt_count} tools ready for production use
- 🟡 **TRIAL:** {trial_count} tools recommended for pilot projects
- 🔵 **ASSESS:** {assess_count} tools requiring further evaluation
- 🔴 **HOLD:** {hold_count} tools not recommended at this time

### Top Recommended Tools
"""
    
    # Sort by recommendation priority and scores
    priority_order = {'adopt': 4, 'trial': 3, 'assess': 2, 'hold': 1}
    top_tools = sorted(
        all_evaluations, 
        key=lambda x: (priority_order.get(x['recommendation'], 0), x['ease_of_use'] + x['documentation_quality']), 
        reverse=True
    )[:5]
    
    for i, tool in enumerate(top_tools, 1):
        report += f"{i}. **{tool['name']}** - {tool['recommendation'].upper()}\n"
        report += f"   Category: {tool['category']} | Overall Score: {(tool['ease_of_use'] + tool['documentation_quality'] + tool['community_support'])//3}/10\n"
    
    report += f"""

## Detailed Evaluations

"""
    
    # Group by category
    by_category = {}
    for eval_data in all_evaluations:
        cat = eval_data['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(eval_data)
    
    for category_name, tools in by_category.items():
        report += f"### {category_name.title()} Tools\n\n"
        
        for tool in sorted(tools, key=lambda x: priority_order.get(x['recommendation'], 0), reverse=True):
            status_emoji = {'adopt': '🟢', 'trial': '🟡', 'assess': '🔵', 'hold': '🔴'}
            
            report += f"{status_emoji.get(tool['recommendation'], '⚪')} **{tool['name']}**\n"
            report += f"- **Decision:** {tool['recommendation'].upper()}\n"
            report += f"- **Evaluated:** {tool['evaluated_date'][:10]}\n"
            report += f"- **Key Strength:** {tool['pros'][0] if tool['pros'] else 'See detailed analysis'}\n"
            report += f"- **Main Concern:** {tool['cons'][0] if tool['cons'] else 'None identified'}\n"
            report += f"- **Business Impact:** {tool['cost_analysis']}\n\n"
    
    report += f"""
## Risk Assessment Summary

### High-Risk Areas
"""
    
    # Identify common risks across evaluations
    all_risks = []
    for eval_data in all_evaluations:
        all_risks.extend(eval_data['risks'])
    
    # Count risk frequencies
    risk_counts = {}
    for risk in all_risks:
        key = risk.lower()
        if 'security' in key:
            risk_counts['Security Concerns'] = risk_counts.get('Security Concerns', 0) + 1
        elif 'vendor' in key or 'lock-in' in key:
            risk_counts['Vendor Lock-in'] = risk_counts.get('Vendor Lock-in', 0) + 1
        elif 'maturity' in key or 'beta' in key:
            risk_counts['Maturity Issues'] = risk_counts.get('Maturity Issues', 0) + 1
        else:
            risk_counts['Other Risks'] = risk_counts.get('Other Risks', 0) + 1
    
    for risk_type, count in sorted(risk_counts.items(), key=lambda x: x[1], reverse=True):
        report += f"- **{risk_type}:** {count} tools affected\n"
    
    report += f"""

## Team Readiness Assessment

### Skills Gap Analysis
"""
    
    # Analyze skill requirements across tools
    all_skills = []
    for eval_data in all_evaluations:
        if eval_data['recommendation'] in ['adopt', 'trial']:
            all_skills.extend(eval_data['team_skill_requirements'])
    
    skill_counts = {}
    for skill in all_skills:
        skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    for skill, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        report += f"- **{skill}:** Required for {count} recommended tools\n"
    
    report += f"""

## Budget Impact Analysis

### Cost Categories
"""
    
    # Analyze cost implications
    open_source_count = len([e for e in all_evaluations if 'open source' in e['cost_analysis'].lower()])
    commercial_count = len([e for e in all_evaluations if 'commercial' in e['cost_analysis'].lower()])
    unknown_count = len(all_evaluations) - open_source_count - commercial_count
    
    report += f"- **Open Source Tools:** {open_source_count} (consider support/training costs)\n"
    report += f"- **Commercial Tools:** {commercial_count} (evaluate ROI and licensing)\n"
    report += f"- **Cost TBD:** {unknown_count} (require detailed pricing analysis)\n"
    
    report += f"""

## Implementation Roadmap

### Quarter 1 Priorities (High-Confidence Adoptions)
"""
    
    q1_tools = [e for e in all_evaluations if e['recommendation'] == 'adopt'][:3]
    for i, tool in enumerate(q1_tools, 1):
        report += f"{i}. **{tool['name']}** - {tool['migration_effort']}\n"
    
    report += f"""

### Quarter 2-3 Trials (Pilot Projects)
"""
    
    trial_tools = [e for e in all_evaluations if e['recommendation'] == 'trial'][:3]
    for i, tool in enumerate(trial_tools, 1):
        report += f"{i}. **{tool['name']}** - {tool['next_steps'][0] if tool['next_steps'] else 'Plan pilot project'}\n"
    
    report += f"""

## Decision Log

For detailed analysis of any tool, reference the individual evaluation reports:
"""
    
    for eval_data in sorted(all_evaluations, key=lambda x: x['evaluated_date'], reverse=True):
        report += f"- **{eval_data['name']}** ({eval_data['evaluated_date'][:10]}) - {eval_data['recommendation'].upper()}\n"
    
    report += f"""

---

**Next Actions:**
1. Review and approve Q1 adoption priorities
2. Allocate budget for commercial tools requiring licenses
3. Plan training for required skill development
4. Set up pilot projects for trial-phase tools
5. Schedule quarterly review of technology landscape

*This report summarizes all technology evaluations and provides data-driven recommendations for strategic technology decisions.*
"""
    
    # Save report
    report_file = eval_manager.data_dir / f"team_report_{category}_{time_period}_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    return f"""
📊 Team Report Generated Successfully!

{report}

💾 Full report saved to: {report_file}

📋 Quick Actions:
• Share report with leadership for technology strategy discussions
• Use evaluation IDs to reference detailed analysis
• Schedule follow-up evaluations for 'assess' category tools
• Begin planning pilot projects for 'trial' recommendations
"""


@tool
def compare_tools(tool1: str, tool2: str, focus_areas: str = "all") -> str:
    """
    Compare two evaluated tools side-by-side.
    
    Args:
        tool1: First tool name
        tool2: Second tool name  
        focus_areas: Comma-separated areas to focus on (cost, performance, security, ease_of_use, all)
    """
    eval1 = eval_manager.get_evaluation(tool1)
    eval2 = eval_manager.get_evaluation(tool2)
    
    if not eval1:
        return f"No evaluation found for '{tool1}'. Run evaluate_tech_tool first."
    if not eval2:
        return f"No evaluation found for '{tool2}'. Run evaluate_tech_tool first."
    
    focus_list = [area.strip() for area in focus_areas.split(',')] if focus_areas != "all" else ["all"]
    
    comparison = f"""
🔄 Tool Comparison: {tool1} vs {tool2}
{'=' * (25 + len(tool1) + len(tool2))}

## Overall Recommendations
- **{tool1}:** {eval1['recommendation'].upper()} - {eval1['reasoning']}
- **{tool2}:** {eval2['recommendation'].upper()} - {eval2['reasoning']}

## Score Comparison
| Metric | {tool1} | {tool2} | Winner |
|--------|---------|---------|---------|
| Ease of Use | {eval1['ease_of_use']}/10 | {eval2['ease_of_use']}/10 | {tool1 if eval1['ease_of_use'] > eval2['ease_of_use'] else tool2 if eval2['ease_of_use'] > eval1['ease_of_use'] else 'Tie'} |
| Documentation | {eval1['documentation_quality']}/10 | {eval2['documentation_quality']}/10 | {tool1 if eval1['documentation_quality'] > eval2['documentation_quality'] else tool2 if eval2['documentation_quality'] > eval1['documentation_quality'] else 'Tie'} |
| Community Support | {eval1['community_support']}/10 | {eval2['community_support']}/10 | {tool1 if eval1['community_support'] > eval2['community_support'] else tool2 if eval2['community_support'] > eval1['community_support'] else 'Tie'} |
| Performance | {eval1['performance']}/10 | {eval2['performance']}/10 | {tool1 if eval1['performance'] > eval2['performance'] else tool2 if eval2['performance'] > eval1['performance'] else 'Tie'} |
| Security | {eval1['security']}/10 | {eval2['security']}/10 | {tool1 if eval1['security'] > eval2['security'] else tool2 if eval2['security'] > eval1['security'] else 'Tie'} |

## Business Considerations

### Licensing & Cost
- **{tool1}:** {eval1['licensing']} - {eval1['cost_analysis']}  
- **{tool2}:** {eval2['licensing']} - {eval2['cost_analysis']}

### Team Impact
- **{tool1} Skills Needed:** {', '.join(eval1['team_skill_requirements'])}
- **{tool2} Skills Needed:** {', '.join(eval2['team_skill_requirements'])}

### Migration Effort
- **{tool1}:** {eval1['migration_effort']}
- **{tool2}:** {eval2['migration_effort']}

## Risk Analysis
**{tool1} Risks:**
{chr(10).join('• ' + risk for risk in eval1['risks'])}

**{tool2} Risks:**
{chr(10).join('• ' + risk for risk in eval2['risks'])}

## Decision Framework

**Choose {tool1} if:**
{chr(10).join('• ' + pro for pro in eval1['pros'][:3])}

**Choose {tool2} if:**
{chr(10).join('• ' + pro for pro in eval2['pros'][:3])}

## Bottom Line Recommendation

"""
    
    # Calculate overall scores
    score1 = sum([eval1['ease_of_use'], eval1['documentation_quality'], eval1['community_support'], 
                  eval1['performance'], eval1['security']]) / 5
    score2 = sum([eval2['ease_of_use'], eval2['documentation_quality'], eval2['community_support'], 
                  eval2['performance'], eval2['security']]) / 5
    
    if score1 > score2:
        winner = tool1
        comparison += f"**{tool1}** has the edge with an average score of {score1:.1f}/10 vs {score2:.1f}/10 for {tool2}."
    elif score2 > score1:
        winner = tool2
        comparison += f"**{tool2}** has the edge with an average score of {score2:.1f}/10 vs {score1:.1f}/10 for {tool1}."
    else:
        winner = "Tie"
        comparison += f"Both tools are closely matched with average scores of {score1:.1f}/10."
    
    comparison += f"""

**Recommendation Priority:**
1. {eval1['name'] if eval1['recommendation'] == 'adopt' else eval2['name'] if eval2['recommendation'] == 'adopt' else 'Neither ready for adoption'}
2. Consider business context and team preferences for final decision

*Use this comparison to inform technology selection discussions with stakeholders.*
"""
    
    return comparison


class TechScout:
    """Main TechScout assistant for technology evaluation"""
    
    def __init__(self, model_provider="bedrock"):
        # Configure model
        if model_provider == "bedrock":
            self.model = BedrockModel(
                model_id="us.amazon.nova-pro-v1:0",
                temperature=0.4  # Slightly higher for creative research analysis
            )
        else:
            self.model = None
        
        # Initialize agent with research and evaluation tools
        self.agent = Agent(
            model=self.model if model_provider == "bedrock" else None,
            tools=[
                research_tech_tool,
                evaluate_tech_tool, 
                search_evaluations,
                generate_team_report,
                compare_tools
            ]
        )
        
        self.system_prompt = """
You are TechScout, an expert AI assistant for technology research and evaluation. You help software development teams make informed decisions about adopting new tools, frameworks, and technologies.

Your core capabilities:
1. **Research**: Gather information from multiple sources (GitHub, Reddit, industry sites, documentation)
2. **Analysis**: Evaluate tools using structured frameworks considering technical and business factors
3. **Risk Assessment**: Identify potential risks, security concerns, and adoption challenges
4. **Recommendations**: Provide clear adoption recommendations (adopt/trial/assess/hold) with reasoning
5. **Knowledge Management**: Maintain searchable evaluation database for team reference

Key behaviors:
- Always research thoroughly before making recommendations
- Consider both technical merit and business context
- Identify risks and mitigation strategies
- Provide concrete next steps and implementation guidance
- Create documentation that leadership can reference for decisions
- Compare similar tools objectively when requested

When evaluating tools:
- Security and stability are paramount considerations
- Consider team skill requirements and learning curves
- Assess long-term maintenance and support implications
- Factor in integration complexity with existing systems
- Evaluate vendor lock-in risks and exit strategies

Always provide structured, actionable insights that help teams make confident technology decisions.
"""
    
    def chat(self, user_input: str) -> str:
        """Process technology evaluation queries"""
        
        # Add context about existing evaluations
        eval_count = len(eval_manager.evaluations)
        context_info = f"""
Current Knowledge Base:
- Total evaluations completed: {eval_count}
- Evaluation data stored in: {eval_manager.data_dir}
- Available for team reference and leadership decisions

Recent evaluation categories: {list(set(e.get('category', 'unknown') for e in eval_manager.evaluations.values()))}
"""
        
        full_prompt = f"{self.system_prompt}\n\n{context_info}\n\nUser: {user_input}"
        return self.agent(full_prompt)


def main():
    """Interactive TechScout assistant"""
    print("🔍 TechScout - AI Technology Research & Evaluation Assistant")
    print("=" * 65)
    print("Your intelligent companion for evaluating new development tools and technologies.")
    print()
    print("Available commands:")
    print("  🔍 'research <tool_name>' - Research a new technology")
    print("  📋 'evaluate <tool_name>' - Create structured evaluation")
    print("  🔎 'search <query>' - Search existing evaluations")
    print("  📊 'report' - Generate team summary report")
    print("  ⚖️  'compare <tool1> <tool2>' - Compare two tools")
    print("  💾 'status' - Show evaluation database status")
    print("  ❌ 'quit' - Exit TechScout")
    print()
    
    # Initialize assistant
    scout = TechScout()
    
    # Show current status
    eval_count = len(eval_manager.evaluations)
    if eval_count > 0:
        print(f"📚 Knowledge base: {eval_count} evaluations available")
        recent_tools = list(eval_manager.evaluations.values())[-3:]
        print(f"🕒 Recent evaluations: {', '.join(e['name'] for e in recent_tools)}")
    else:
        print("📋 Knowledge base empty - start by researching a tool!")
    print()
    
    while True:
        try:
            user_input = input("🔍 TechScout> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Happy tool hunting! Evaluations saved for team reference.")
                break
            
            # Handle quick commands
            if user_input.lower().startswith('research '):
                tool_name = user_input[9:].strip()
                user_input = f"Research the technology '{tool_name}' from multiple sources including GitHub, Reddit, and official documentation"
            
            elif user_input.lower().startswith('evaluate '):
                tool_name = user_input[9:].strip()
                user_input = f"Create a comprehensive evaluation of '{tool_name}' with scoring, risk assessment, and adoption recommendation"
            
            elif user_input.lower().startswith('search '):
                query = user_input[7:].strip()
                user_input = f"Search existing evaluations for '{query}'"
            
            elif user_input.lower().startswith('compare '):
                tools = user_input[8:].strip().split(' vs ')
                if len(tools) == 2:
                    user_input = f"Compare {tools[0].strip()} and {tools[1].strip()} side by side"
                else:
                    print("💡 Usage: compare <tool1> vs <tool2>")
                    continue
            
            elif user_input.lower() == 'report':
                user_input = "Generate a comprehensive team report showing all evaluations with recommendations for leadership review"
            
            elif user_input.lower() == 'status':
                print(f"\n📊 TechScout Database Status:")
                print(f"📚 Total evaluations: {len(eval_manager.evaluations)}")
                print(f"💾 Storage location: {eval_manager.data_dir}")
                
                if eval_manager.evaluations:
                    categories = {}
                    recommendations = {}
                    for eval_data in eval_manager.evaluations.values():
                        cat = eval_data.get('category', 'unknown')
                        rec = eval_data.get('recommendation', 'unknown')
                        categories[cat] = categories.get(cat, 0) + 1
                        recommendations[rec] = recommendations.get(rec, 0) + 1
                    
                    print(f"📂 Categories: {dict(categories)}")
                    print(f"🎯 Recommendations: {dict(recommendations)}")
                print()
                continue
            
            if not user_input:
                continue
            
            # Get response from assistant
            print("\n🧠 Analyzing...")
            response = scout.chat(user_input)
            print(f"\n🔍 TechScout: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Happy tool hunting!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or type 'quit' to exit.\n")


if __name__ == "__main__":
    # Example usage
    print("🚀 TechScout Example Usage:")
    print("""
    
📚 Getting Started:
- "research Cursor AI" - Research the Cursor AI coding tool
- "evaluate GitHub Copilot" - Create structured evaluation
- "compare Cursor AI vs GitHub Copilot" - Side-by-side comparison
- "report" - Generate team summary for leadership
- "search ai-development" - Find all AI development tool evaluations

🎯 Workflow Example:
1. Hear about new tool → "research [tool name]"
2. Get structured analysis → "evaluate [tool name]" 
3. Compare options → "compare [tool1] vs [tool2]"
4. Share with team → "report" 
5. Reference later → "search [query]"

💼 Perfect for:
- Staying current with development tools
- Making evidence-based technology decisions  
- Avoiding redundant research across team members
- Providing leadership with clear recommendations
- Building institutional knowledge about tool evaluations

    """)
    
    main()