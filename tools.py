"""
Four tools for the Career Assistant Agent:
1. Job Search Tool - Find job openings
2. Skill Gap Analysis Tool - Compare resume vs role
3. Project Idea Generator Tool - Suggest portfolio projects
4. GitHub Checker Tool - Analyze GitHub repos
"""

import os
import requests
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, List

# Initialize LLM for tools that need it
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(
    model="models/gemma-4-31b-it",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7
)


@tool
def job_search_tool(target_role: str) -> str:
    """
    Search for job openings matching the target role.
    
    Args:
        target_role: The job title to search for (e.g., "Software Engineer")
    
    Returns:
        JSON string with job listings including titles, companies, and requirements
    """
    print(f"🔍 Searching for jobs: {target_role}")
    
    # Simple web search simulation
    # In production, use Google Custom Search API or SERP API
    prompt = f"""Generate a realistic list of 3-5 current job openings for the role: {target_role}

Return in this JSON format:
{{
    "jobs": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "location": "City, State/Remote",
            "requirements": ["skill1", "skill2", "skill3"],
            "link": "https://example.com/job"
        }}
    ]
}}

Be realistic and include actual tech companies and common requirements for this role."""
    
    result = llm.invoke(prompt)
    return result.content


@tool
def skill_gap_analysis_tool(resume_text: str, target_role: str) -> str:
    """
    Analyze skill gaps between resume and target role requirements.
    
    Args:
        resume_text: Extracted text from resume PDF
        target_role: Target job role
    
    Returns:
        JSON string with missing skills, existing strengths, and recommendations
    """
    print(f"📊 Analyzing skill gaps for: {target_role}")
    
    prompt = f"""Analyze the following resume against the target role: {target_role}

Resume:
{resume_text}

Provide a detailed skill gap analysis in this JSON format:
{{
    "existing_skills": ["skill1", "skill2", ...],
    "missing_skills": ["skill1", "skill2", ...],
    "strength_areas": ["area1", "area2", ...],
    "recommendations": ["rec1", "rec2", ...],
    "match_percentage": 75
}}

Be thorough and honest about gaps."""
    
    result = llm.invoke(prompt)
    return result.content


@tool
def project_idea_generator_tool(missing_skills: str, target_role: str) -> str:
    """
    Generate portfolio project ideas to close skill gaps.
    
    Args:
        missing_skills: List or description of missing skills
        target_role: Target job role
    
    Returns:
        JSON string with project ideas, tech stacks, and difficulty levels
    """
    print(f"�� Generating project ideas to close skill gaps")
    
    prompt = f"""Given these missing skills: {missing_skills}
For target role: {target_role}

Generate 3-5 portfolio project ideas that would help close these gaps.

Return in this JSON format:
{{
    "projects": [
        {{
            "title": "Project Name",
            "description": "What it does",
            "tech_stack": ["tech1", "tech2", "tech3"],
            "difficulty": "Beginner/Intermediate/Advanced",
            "time_estimate": "X weeks",
            "skills_practiced": ["skill1", "skill2"],
            "github_repo_structure": "Brief outline of repo structure"
        }}
    ]
}}

Make projects realistic, practical, and impressive for the role."""
    
    result = llm.invoke(prompt)
    return result.content


@tool
def github_checker_tool(github_username: str) -> str:
    """
    Check GitHub profile and analyze public repositories.
    
    Args:
        github_username: GitHub username to analyze
    
    Returns:
        JSON string with repo summary, languages, and activity
    """
    print(f"🐙 Checking GitHub profile: {github_username}")
    
    try:
        # Get user info
        github_token = os.getenv("GITHUB_TOKEN")
        headers = {}
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        
        user_response = requests.get(
            f"https://api.github.com/users/{github_username}",
            headers=headers
        )
        user_data = user_response.json()
        
        # Get repos
        repos_response = requests.get(
            f"https://api.github.com/users/{github_username}/repos?per_page=100&sort=updated",
            headers=headers
        )
        repos = repos_response.json()
        
        # Analyze repos
        languages = {}
        repo_list = []
        
        for repo in repos[:10]:  # Top 10 most recent
            if not repo.get("fork", False):  # Skip forks
                repo_list.append({
                    "name": repo["name"],
                    "description": repo.get("description", "No description"),
                    "language": repo.get("language", "Unknown"),
                    "stars": repo.get("stargazers_count", 0),
                    "url": repo["html_url"]
                })
                
                # Count languages
                lang = repo.get("language")
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1
        
        result = {
            "username": github_username,
            "name": user_data.get("name", "N/A"),
            "bio": user_data.get("bio", "N/A"),
            "public_repos": user_data.get("public_repos", 0),
            "followers": user_data.get("followers", 0),
            "top_languages": dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]),
            "recent_repos": repo_list,
            "profile_url": user_data.get("html_url", "")
        }
        
        return str(result)
        
    except Exception as e:
        return f'{{"error": "Failed to fetch GitHub data: {str(e)}"}}'


# Export all tools
__all__ = [
    "job_search_tool",
    "skill_gap_analysis_tool", 
    "project_idea_generator_tool",
    "github_checker_tool"
]
