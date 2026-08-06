"""
Career Assistant Tools - LangChain Tool Implementations
Each tool provides specialized career guidance functionality
"""

import os
import requests
from typing import Optional
from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


# Initialize Groq LLM for tools
def get_llm():
    """Get configured Groq LLM instance"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")
    
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=api_key,
        temperature=0.7
    )


@tool
def job_search_advisor(resume_text: str, target_role: str) -> str:
    """
    Provide personalized job search strategies based on resume and target role.
    
    Args:
        resume_text: Candidate's resume content
        target_role: Desired job position
        
    Returns:
        Job search strategies and recommendations
    """
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Job Search Expert specializing in tech careers.

Provide specific, actionable job search strategies including:
- Companies to target (by name)
- Job boards and platforms to use
- Keywords to include in applications
- Networking strategies
- Timeline and action steps"""),
        ("human", """Target Role: {target_role}

Resume Summary: {resume_text}

Provide detailed job search strategies.""")
    ])
    
    chain = prompt | llm
    result = chain.invoke({
        "target_role": target_role,
        "resume_text": resume_text[:800]
    })
    
    return result.content


@tool
def skill_gap_analyzer(resume_text: str, target_role: str) -> str:
    """
    Analyze skill gaps between current resume and target role requirements.
    
    Args:
        resume_text: Candidate's resume content
        target_role: Desired job position
        
    Returns:
        Detailed skill gap analysis with learning recommendations
    """
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Skill Development Expert for tech professionals.

Analyze the candidate's current skills vs. target role requirements and provide:
- Technical skills needed (specific technologies/frameworks)
- Soft skills to develop
- Recommended learning resources (courses, books, tutorials)
- Time estimates for skill development
- Practice opportunities"""),
        ("human", """Target Role: {target_role}

Current Skills from Resume: {resume_text}

Analyze skill gaps and provide learning roadmap.""")
    ])
    
    chain = prompt | llm
    result = chain.invoke({
        "target_role": target_role,
        "resume_text": resume_text[:800]
    })
    
    return result.content


@tool
def project_idea_generator(resume_text: str, target_role: str) -> str:
    """
    Generate portfolio project ideas tailored to target role and current skills.
    
    Args:
        resume_text: Candidate's resume content
        target_role: Desired job position
        
    Returns:
        2-3 specific project ideas with implementation details
    """
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Portfolio Development Expert for tech professionals.

Generate 2-3 impressive portfolio project ideas that:
- Demonstrate skills needed for the target role
- Build on candidate's existing knowledge
- Are realistic to complete in 2-4 weeks each
- Include specific technologies to use
- Have clear showcase value

For each project provide:
- Project name and description
- Technologies/frameworks to use
- Key features to implement
- Learning outcomes
- How to present it effectively"""),
        ("human", """Target Role: {target_role}

Current Experience: {resume_text}

Generate tailored project ideas.""")
    ])
    
    chain = prompt | llm
    result = chain.invoke({
        "target_role": target_role,
        "resume_text": resume_text[:800]
    })
    
    return result.content


@tool
def github_profile_analyzer(github_username: str) -> str:
    """
    Analyze GitHub profile using GitHub REST API and provide optimization tips.
    
    Args:
        github_username: GitHub username to analyze
        
    Returns:
        GitHub profile analysis with improvement recommendations
    """
    try:
        # Fetch user data from GitHub API
        user_url = f"https://api.github.com/users/{github_username}"
        repos_url = f"https://api.github.com/users/{github_username}/repos?sort=updated&per_page=10"
        
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Add GitHub token if available for higher rate limits
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        
        # Get user profile
        user_response = requests.get(user_url, headers=headers, timeout=10)
        
        # Handle rate limiting specifically (403 = rate limit exceeded)
        if user_response.status_code == 403:
            rate_limit_remaining = user_response.headers.get('X-RateLimit-Remaining', '0')
            rate_limit_reset = user_response.headers.get('X-RateLimit-Reset', 'unknown')
            
            if github_token:
                return f"⚠️ GitHub API rate limit exceeded even with authentication (5,000/hour limit).\n\nRate limit remaining: {rate_limit_remaining}\nResets at timestamp: {rate_limit_reset}\n\nPlease try again in a few minutes."
            else:
                return f"⚠️ GitHub API rate limit exceeded (60 requests/hour without token).\n\n💡 **Solution:** Add a GITHUB_TOKEN environment variable with a Personal Access Token to unlock 5,000 requests/hour.\n\nGet token at: https://github.com/settings/tokens\nRequired scopes: public_repo (read-only)\n\nFor now, please try again in an hour or contact support."
        
        # Handle user not found (404)
        if user_response.status_code == 404:
            return f"❌ GitHub user '{github_username}' not found. Please check the username is correct and try again."
        
        # Handle other errors
        if user_response.status_code != 200:
            return f"⚠️ Could not fetch GitHub profile for '{github_username}'.\n\nHTTP Status: {user_response.status_code}\nError: {user_response.text[:200]}\n\nPlease try again later."
        
        user_data = user_response.json()
        
        # Get repositories
        repos_response = requests.get(repos_url, headers=headers, timeout=10)
        
        # Handle rate limit for repos endpoint too
        if repos_response.status_code == 403:
            rate_limit_remaining = repos_response.headers.get('X-RateLimit-Remaining', '0')
            if github_token:
                return f"⚠️ GitHub API rate limit exceeded while fetching repositories (authenticated).\n\nRemaining: {rate_limit_remaining}\n\nProfile data was fetched successfully, but repository analysis is unavailable. Please try again later."
            else:
                return f"⚠️ GitHub API rate limit exceeded while fetching repositories.\n\n💡 Add GITHUB_TOKEN environment variable for 5,000 requests/hour.\n\nProfile data was fetched, but repository analysis is unavailable."
        
        repos_data = repos_response.json() if repos_response.status_code == 200 else []
        
        # Extract key information
        profile_info = {
            "username": user_data.get("login"),
            "name": user_data.get("name"),
            "bio": user_data.get("bio"),
            "public_repos": user_data.get("public_repos", 0),
            "followers": user_data.get("followers", 0),
            "following": user_data.get("following", 0),
            "company": user_data.get("company"),
            "location": user_data.get("location"),
            "blog": user_data.get("blog"),
            "twitter": user_data.get("twitter_username")
        }
        
        # Analyze repositories
        repo_info = []
        languages_used = set()
        
        for repo in repos_data[:10]:  # Top 10 repos
            repo_info.append({
                "name": repo.get("name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "updated": repo.get("updated_at")
            })
            if repo.get("language"):
                languages_used.add(repo.get("language"))
        
        # Use LLM to analyze and provide recommendations
        llm = get_llm()
        
        analysis_prompt = f"""Analyze this GitHub profile and provide specific improvement recommendations:

**Profile Summary:**
- Username: {profile_info['username']}
- Name: {profile_info['name'] or 'Not set'}
- Bio: {profile_info['bio'] or 'Not set'}
- Public Repos: {profile_info['public_repos']}
- Followers: {profile_info['followers']}
- Following: {profile_info['following']}
- Company: {profile_info['company'] or 'Not set'}
- Location: {profile_info['location'] or 'Not set'}
- Website: {profile_info['blog'] or 'Not set'}

**Recent Repositories:**
{chr(10).join(f"- {r['name']}: {r['description'] or 'No description'} ({r['language'] or 'N/A'}) - ⭐ {r['stars']}" for r in repo_info[:5])}

**Languages Used:** {', '.join(languages_used) if languages_used else 'None detected'}

Provide specific, actionable recommendations for:
1. Profile completeness (bio, pinned repos, README)
2. Repository organization and documentation
3. Project showcase improvements
4. Contribution strategies
5. Professional presentation"""

        result = llm.invoke(analysis_prompt)
        
        return result.content
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching GitHub data: {str(e)}. Please check the username and try again."
    except Exception as e:
        return f"Error analyzing GitHub profile: {str(e)}"


# List of all tools for agent
career_tools = [
    job_search_advisor,
    skill_gap_analyzer,
    project_idea_generator,
    github_profile_analyzer
]


def get_tool_descriptions() -> str:
    """Get formatted descriptions of all available tools"""
    descriptions = []
    for tool in career_tools:
        descriptions.append(f"- {tool.name}: {tool.description}")
    return "\n".join(descriptions)


if __name__ == "__main__":
    print("Career Assistant Tools")
    print("=" * 60)
    print("\nAvailable Tools:")
    print(get_tool_descriptions())
    print("\n✅ Tools module loaded successfully")
