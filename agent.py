"""
Career Assistant Agent - Bulletproof Direct Tool Invocation
Calls each tool individually and returns comprehensive structured results
"""

import os
from typing import Dict, Any


def parse_analysis_sections(analysis_text: str) -> Dict[str, str]:
    """
    Safely extracts blocks from the full analysis string using robust keyword fallback.
    
    Args:
        analysis_text: Raw analysis output text
        
    Returns:
        Dictionary with 4 section keys
    """
    sections = {
        "job_search": "No job search data available.",
        "skill_gaps": "No skill gap data available.",
        "project_ideas": "No project ideas available.",
        "github_summary": "No GitHub analysis available."
    }
    
    lines = analysis_text.split('\n')
    current_section = None
    section_content = {k: [] for k in sections.keys()}
    
    for line in lines:
        line_lower = line.lower()
        if "1. job search" in line_lower or "## 1" in line_lower:
            current_section = "job_search"
            continue
        elif "2. skill gap" in line_lower or "## 2" in line_lower:
            current_section = "skill_gaps"
            continue
        elif "3. project" in line_lower or "## 3" in line_lower:
            current_section = "project_ideas"
            continue
        elif "4. github" in line_lower or "## 4" in line_lower:
            current_section = "github_summary"
            continue
        
        if current_section:
            section_content[current_section].append(line)
    
    for key in sections.keys():
        if section_content[key]:
            sections[key] = "\n".join(section_content[key]).strip()
    
    if not any(section_content.values()):
        sections["job_search"] = analysis_text
    
    return sections


def analyze_career(
    resume_text: str,
    target_role: str, 
    github_username: str
) -> Dict[str, Any]:
    """
    Runs career tool pipelines and compiles a multi-key dictionary to fulfill all API contracts.
    
    Args:
        resume_text: Candidate's resume content
        target_role: Desired job position
        github_username: GitHub username for profile analysis
        
    Returns:
        Dictionary with ALL required keys for both app.py and frontend
    """
    try:
        print("🤖 Invoking career analysis tools...")
        
        # Import tools
        from tools import (
            job_search_advisor,
            skill_gap_analyzer,
            project_idea_generator,
            github_profile_analyzer
        )
        
        # Call each tool individually with truncated resume for efficiency
        print("📞 Calling job_search_advisor...")
        job_result = job_search_advisor.invoke({
            "resume_text": resume_text[:800],
            "target_role": target_role
        })
        
        print("📞 Calling skill_gap_analyzer...")
        skill_result = skill_gap_analyzer.invoke({
            "resume_text": resume_text[:800],
            "target_role": target_role
        })
        
        print("📞 Calling project_idea_generator...")
        project_result = project_idea_generator.invoke({
            "resume_text": resume_text[:800],
            "target_role": target_role
        })
        
        print("📞 Calling github_profile_analyzer...")
        github_result = github_profile_analyzer.invoke({
            "github_username": github_username
        })
        
        print("✅ All tools executed successfully!")
        
        # Stitch all results together into a full markdown report
        full_report = f"""# Career Analysis Report

## 1. Job Search Strategy
{job_result}

## 2. Skill Gap Analysis
{skill_result}

## 3. Project Ideas
{project_result}

## 4. GitHub Profile Review
{github_result}"""
        
        # Enforce all contract keys natively so neither app.py nor script.js can throw a KeyError
        return {
            "status": "success",
            "target_role": target_role,
            "github_username": github_username,
            "analysis": full_report,
            "job_search": str(job_result),
            "skill_gaps": str(skill_result),
            "project_ideas": str(project_result),
            "github_summary": str(github_result),
            "tool_based": True
        }
        
    except Exception as e:
        import traceback
        print(f"❌ Agent Error: {e}")
        print(traceback.format_exc())
        
        # Return error structure with all required keys to prevent KeyErrors
        error_msg = str(e)
        return {
            "status": "error",
            "error": error_msg,
            "traceback": traceback.format_exc(),
            "target_role": target_role,
            "github_username": github_username,
            "analysis": f"An error occurred: {error_msg}",
            "job_search": "Error running tool.",
            "skill_gaps": "Error running tool.",
            "project_ideas": "Error running tool.",
            "github_summary": "Error running tool."
        }


# ============================================================
# CLI TESTING
# ============================================================

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
            print("Job Search:")
            print(result.get("job_search", "N/A")[:400])
            print("\n" + "="*60)
            print("Skill Gaps:")
            print(result.get("skill_gaps", "N/A")[:400])
            print("="*60)
        else:
            print(f"❌ Error: {result.get('error')}")
            
    except Exception as e:
        import traceback
        print(f"❌ Test failed: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    test_agent()
