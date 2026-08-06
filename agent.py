"""
Career Assistant Agent with Real Tool-Calling Architecture
Uses LangChain AgentExecutor with 4 specialized tools
"""

import os
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

# Import our custom tools
from tools import career_tools


class CareerAnalysisInput(BaseModel):
    """Input schema for career analysis"""
    resume_text: str = Field(description="Resume content as text")
    target_role: str = Field(description="Desired job role")
    github_username: str = Field(description="GitHub username")


def create_career_agent():
    """
    Create a tool-calling agent
    
    The agent has access to 4 specialized tools:
    1. job_search_advisor - Job search strategies
    2. skill_gap_analyzer - Skill gap analysis
    3. project_idea_generator - Portfolio project ideas
    4. github_profile_analyzer - GitHub profile review with API
    
    Returns:
        Configured LLM with tool binding
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    
    # Initialize Groq LLM with tool-calling support
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=api_key,
        temperature=0.7,
    )
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(career_tools)
    
    return llm_with_tools


def analyze_career(
    resume_text: str,
    target_role: str, 
    github_username: str
) -> Dict[str, Any]:
    """
    Run comprehensive career analysis using tools
    
    Args:
        resume_text: Candidate's resume content
        target_role: Desired job position
        github_username: GitHub username for profile analysis
        
    Returns:
        Dictionary with analysis results and tool outputs
    """
    try:
        # Call each tool directly for now
        print("🔧 Calling tools...")
        
        # Call job search tool
        print("  1. Job Search Advisor...")
        from tools import job_search_advisor
        job_result = job_search_advisor.invoke({
            "resume_text": resume_text[:800],
            "target_role": target_role
        })
        
        # Call skill gap tool
        print("  2. Skill Gap Analyzer...")
        from tools import skill_gap_analyzer
        skill_result = skill_gap_analyzer.invoke({
            "resume_text": resume_text[:800],
            "target_role": target_role
        })
        
        # Call project ideas tool
        print("  3. Project Idea Generator...")
        from tools import project_idea_generator
        project_result = project_idea_generator.invoke({
            "resume_text": resume_text[:800],
            "target_role": target_role
        })
        
        # Call GitHub tool
        print("  4. GitHub Profile Analyzer...")
        from tools import github_profile_analyzer
        github_result = github_profile_analyzer.invoke({
            "github_username": github_username
        })
        
        # Combine results
        full_analysis = f"""# Career Analysis Report

## 1. Job Search Strategy
{job_result}

## 2. Skill Gap Analysis
{skill_result}

## 3. Project Ideas
{project_result}

## 4. GitHub Profile Review
{github_result}
"""
        
        return {
            "status": "success",
            "target_role": target_role,
            "github_username": github_username,
            "analysis": full_analysis,
            "tool_based": True
        }
        
    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        print(traceback.format_exc())
        return {
            "status": "error",
            "error": str(e),
            "target_role": target_role,
            "github_username": github_username
        }


def parse_analysis_sections(analysis_text: str) -> Dict[str, str]:
    """
    Parse agent output into 4 sections
    
    Args:
        analysis_text: Complete analysis from agent
        
    Returns:
        Dictionary with 4 sections: job_search, skill_gaps, project_ideas, github_summary
    """
    sections = {
        "job_search": "",
        "skill_gaps": "",
        "project_ideas": "",
        "github_summary": ""
    }
    
    # Split by markdown headers
    if "## 1. Job Search" in analysis_text:
        parts = analysis_text.split("## 1. Job Search")
        if len(parts) > 1:
            rest = parts[1]
            if "## 2. Skill Gap" in rest:
                skill_parts = rest.split("## 2. Skill Gap")
                sections["job_search"] = skill_parts[0].strip()
                
                if len(skill_parts) > 1:
                    rest2 = skill_parts[1]
                    if "## 3. Project" in rest2:
                        project_parts = rest2.split("## 3. Project")
                        sections["skill_gaps"] = project_parts[0].strip()
                        
                        if len(project_parts) > 1:
                            rest3 = project_parts[1]
                            if "## 4. GitHub" in rest3:
                                github_parts = rest3.split("## 4. GitHub")
                                sections["project_ideas"] = github_parts[0].strip()
                                if len(github_parts) > 1:
                                    sections["github_summary"] = github_parts[1].strip()
    
    # Fallback
    if not sections["job_search"]:
        sections["job_search"] = analysis_text
        sections["skill_gaps"] = "See full analysis above"
        sections["project_ideas"] = "See full analysis above"
        sections["github_summary"] = "See full analysis above"
    
    return sections


# ============================================================================
# CLI TESTING
# ============================================================================

def test_agent():
    """Test the agent with sample data"""
    print("🧪 Testing Career Assistant with Tools...\n")
    
    resume_text = """
    Software Engineer with 2 years of experience in Python and JavaScript.
    Built web applications using React and FastAPI.
    Familiar with SQL databases and REST APIs.
    Experience with Git and Docker.
    """
    
    target_role = "Senior Full-Stack Engineer"
    github_username = "Sathvik1533"
    
    print(f"📄 Resume: {resume_text[:100]}...")
    print(f"🎯 Target Role: {target_role}")
    print(f"🐙 GitHub: {github_username}\n")
    
    try:
        result = analyze_career(resume_text, target_role, github_username)
        
        if result["status"] == "success":
            print("\n✅ Analysis Complete!\n")
            print("="*60)
            print(result["analysis"][:500])
            print("="*60)
        else:
            print(f"❌ Error: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_agent()
