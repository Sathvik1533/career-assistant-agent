"""
Career Assistant Agent - Direct Tool Invocation Approach
Calls each tool individually and returns structured results
"""

import os
from typing import Dict, Any
from tools import (
    job_search_advisor,
    skill_gap_analyzer,
    project_idea_generator,
    github_profile_analyzer
)


def analyze_career(
    resume_text: str,
    target_role: str, 
    github_username: str
) -> Dict[str, Any]:
    """
    Run comprehensive career analysis by directly invoking all 4 tools
    
    Args:
        resume_text: Candidate's resume content
        target_role: Desired job position
        github_username: GitHub username for profile analysis
        
    Returns:
        Dictionary with individual tool results under exact frontend keys
    """
    try:
        print("🤖 Invoking career analysis tools...")
        
        # Call each tool individually
        print("📞 Calling job_search_advisor...")
        job_result = job_search_advisor.invoke({
            "resume_text": resume_text,
            "target_role": target_role
        })
        
        print("📞 Calling skill_gap_analyzer...")
        skill_result = skill_gap_analyzer.invoke({
            "resume_text": resume_text,
            "target_role": target_role
        })
        
        print("📞 Calling project_idea_generator...")
        project_result = project_idea_generator.invoke({
            "resume_text": resume_text,
            "target_role": target_role
        })
        
        print("📞 Calling github_profile_analyzer...")
        github_result = github_profile_analyzer.invoke({
            "github_username": github_username
        })
        
        print("✅ All tools executed successfully!")
        
        # Stitch all results together into a full report for backward compatibility
        full_report = f"""# Career Analysis Report

## 1. Job Search Strategy
{job_result}

## 2. Skill Gap Analysis
{skill_result}

## 3. Project Ideas
{project_result}

## 4. GitHub Profile Review
{github_result}"""
        
        # Return with both 'analysis' key (for compatibility) and individual keys
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
        
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "target_role": target_role,
            "github_username": github_username
        }


def parse_analysis_sections(analysis_text: str) -> Dict[str, str]:
    """
    Legacy function - no longer needed since we return individual tool results
    Kept for backward compatibility
    """
    return {
        "job_search": analysis_text,
        "skill_gaps": "See full analysis",
        "project_ideas": "See full analysis",
        "github_summary": "See full analysis"
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
