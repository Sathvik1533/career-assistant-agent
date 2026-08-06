"""
Career Assistant Agent - Simple Tool-Binding Approach
Uses direct tool binding with ChatGroq for maximum compatibility
"""

import os
import re
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Import our custom tools
try:
    from tools import career_tools
except ImportError:
    print("⚠️  Warning: tools module not found. Make sure tools.py is in the same directory.")
    career_tools = []


def create_career_agent():
    """
    Create a simple agent using tool binding
    
    Returns:
        Configured LLM with tools bound
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    
    # Initialize Groq LLM
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
    Run comprehensive career analysis using LLM with tools
    
    Args:
        resume_text: Candidate's resume content
        target_role: Desired job position
        github_username: GitHub username for profile analysis
        
    Returns:
        Dictionary with analysis results
    """
    try:
        print("🤖 Initializing Groq LLM with tools...")
        
        # Create LLM with tools
        llm_with_tools = create_career_agent()
        
        # Create comprehensive prompt
        prompt = f"""You are a Career Assistant with access to 4 specialized tools. Analyze the candidate's profile comprehensively.

**Available Tools:**
1. job_search_advisor - Get job search strategies
2. skill_gap_analyzer - Analyze skill gaps
3. project_idea_generator - Generate project ideas  
4. github_profile_analyzer - Analyze GitHub profile

**Instructions:**
- Use ALL 4 tools to gather information
- Call each tool with appropriate parameters
- Synthesize results into a comprehensive report with 4 sections

**Target Role:** {target_role}

**Resume Summary:**
{resume_text[:800]}

**GitHub Username:** {github_username}

Please provide a complete analysis with these sections:
## 1. Job Search Strategy
## 2. Skill Gap Analysis
## 3. Project Ideas
## 4. GitHub Profile Review

Be specific, actionable, and professional."""

        print("🔧 Running LLM with tool-calling...")
        
        # Invoke LLM
        response = llm_with_tools.invoke(prompt)
        
        # Extract content
        analysis = response.content if hasattr(response, 'content') else str(response)
        
        print("✅ Analysis complete!")
        
        return {
            "status": "success",
            "target_role": target_role,
            "github_username": github_username,
            "analysis": analysis
        }
        
    except Exception as e:
        import traceback
        print(f"❌ Agent Error: {e}")
        print(traceback.format_exc())
        
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "target_role": target_role,
            "github_username": github_username
        }


def parse_analysis_sections(analysis_text: str) -> Dict[str, str]:
    """
    Parse agent output into 4 sections using robust parsing
    
    Args:
        analysis_text: Complete analysis from agent
        
    Returns:
        Dictionary with 4 sections
    """
    import re
    
    sections = {
        "job_search": "",
        "skill_gaps": "",
        "project_ideas": "",
        "github_summary": ""
    }
    
    # Try multiple header patterns
    patterns = [
        (r"##?\s*1\.?\s*Job Search.*?\n(.*?)(?=##?\s*2|$)", "job_search"),
        (r"##?\s*2\.?\s*Skill Gap.*?\n(.*?)(?=##?\s*3|$)", "skill_gaps"),
        (r"##?\s*3\.?\s*Project.*?\n(.*?)(?=##?\s*4|$)", "project_ideas"),
        (r"##?\s*4\.?\s*GitHub.*?\n(.*?)$", "github_summary"),
    ]
    
    # Try to extract each section
    for pattern, key in patterns:
        if not sections[key]:
            match = re.search(pattern, analysis_text, re.IGNORECASE | re.DOTALL)
            if match:
                sections[key] = match.group(1).strip()
    
    # Fallback: split by double newlines
    if not any(sections.values()):
        chunks = [chunk.strip() for chunk in analysis_text.split('\n\n') if chunk.strip()]
        if len(chunks) >= 4:
            sections["job_search"] = chunks[0]
            sections["skill_gaps"] = chunks[1] if len(chunks) > 1 else ""
            sections["project_ideas"] = chunks[2] if len(chunks) > 2 else ""
            sections["github_summary"] = chunks[3] if len(chunks) > 3 else ""
        else:
            sections["job_search"] = analysis_text
            sections["skill_gaps"] = "See comprehensive analysis above"
            sections["project_ideas"] = "See comprehensive analysis above"
            sections["github_summary"] = "See comprehensive analysis above"
    
    return sections


# ============================================================================
# CLI TESTING
# ============================================================================

def test_agent():
    """Test the agent with dynamic terminal input"""
    print("🧪 Testing Career Assistant\n")
    print("="*60)
    print("Please provide the following information:")
    print("="*60)
    
    # Get resume text
    print("\n📄 Enter resume summary (press Enter twice when done):")
    resume_lines = []
    while True:
        line = input()
        if line == "":
            if resume_lines and resume_lines[-1] == "":
                break
            resume_lines.append(line)
        else:
            resume_lines.append(line)
    
    resume_text = "\n".join(resume_lines).strip()
    
    if not resume_text:
        print("⚠️  No resume provided, using sample data...")
        resume_text = "Software Engineer with 2 years experience in Python and JavaScript."
    
    # Get target role
    print("\n🎯 Enter target role:")
    target_role = input().strip()
    if not target_role:
        target_role = "Senior Full-Stack Engineer"
    
    # Get GitHub username
    print("\n🐙 Enter GitHub username:")
    github_username = input().strip()
    if not github_username:
        github_username = "Sathvik1533"
    
    print("\n" + "="*60)
    print("Input Summary:")
    print("="*60)
    print(f"📄 Resume: {resume_text[:100]}...")
    print(f"🎯 Target Role: {target_role}")
    print(f"🐙 GitHub: {github_username}")
    print("="*60 + "\n")
    
    try:
        result = analyze_career(resume_text, target_role, github_username)
        
        if result["status"] == "success":
            print("\n✅ Analysis Complete!\n")
            print("="*60)
            print(result["analysis"][:800])
            print("="*60)
        else:
            print(f"❌ Error: {result.get('error')}")
            
    except Exception as e:
        import traceback
        print(f"❌ Test failed: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    test_agent()
