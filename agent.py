"""
Career Assistant Agent with Real Tool-Calling Architecture
Uses LangChain AgentExecutor with 4 specialized tools
"""

import os
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from pydantic import BaseModel, Field

# Import our custom tools
from tools import career_tools


class CareerAnalysisInput(BaseModel):
    """Input schema for career analysis"""
    resume_text: str = Field(description="Resume content as text")
    target_role: str = Field(description="Desired job role")
    github_username: str = Field(description="GitHub username")


def create_career_agent() -> AgentExecutor:
    """
    Create a tool-calling agent with AgentExecutor
    
    The agent has access to 4 specialized tools:
    1. job_search_advisor - Job search strategies
    2. skill_gap_analyzer - Skill gap analysis
    3. project_idea_generator - Portfolio project ideas
    4. github_profile_analyzer - GitHub profile review with API
    
    Returns:
        AgentExecutor configured with career guidance tools
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
    
    # Create agent prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert Career Assistant Agent with access to specialized tools.

Your role is to provide comprehensive career guidance by:
1. Using the job_search_advisor tool for job search strategies
2. Using the skill_gap_analyzer tool for skill analysis
3. Using the project_idea_generator tool for portfolio projects
4. Using the github_profile_analyzer tool for GitHub profile review

IMPORTANT: You MUST use ALL 4 tools to provide a complete analysis. Call each tool with appropriate inputs.

After gathering information from all tools, synthesize the results into a comprehensive career report with these 4 sections:

**1. Job Search Strategy**
[Results from job_search_advisor tool]

**2. Skill Gap Analysis**
[Results from skill_gap_analyzer tool]

**3. Project Ideas**
[Results from project_idea_generator tool]

**4. GitHub Profile Review**
[Results from github_profile_analyzer tool]

Be thorough, specific, and actionable in your guidance."""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])
    
    # Create the agent
    agent = create_tool_calling_agent(llm, career_tools, prompt)
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=career_tools,
        verbose=True,  # Show tool calls for debugging
        handle_parsing_errors=True,
        max_iterations=10,  # Allow multiple tool calls
        return_intermediate_steps=False
    )
    
    return agent_executor


def analyze_career(
    resume_text: str,
    target_role: str, 
    github_username: str
) -> Dict[str, Any]:
    """
    Run comprehensive career analysis using agent with tools
    
    Args:
        resume_text: Candidate's resume content
        target_role: Desired job position
        github_username: GitHub username for profile analysis
        
    Returns:
        Dictionary with analysis results and tool outputs
    """
    agent_executor = create_career_agent()
    
    # Construct input for agent
    input_text = f"""Please analyze this candidate's career profile:

**Resume Summary:**
{resume_text[:1000]}

**Target Role:** {target_role}

**GitHub Username:** {github_username}

Use ALL 4 tools (job_search_advisor, skill_gap_analyzer, project_idea_generator, and github_profile_analyzer) to provide a complete analysis. Then synthesize the results into a comprehensive report."""

    try:
        # Execute agent with tools
        result = agent_executor.invoke({"input": input_text})
        
        return {
            "status": "success",
            "target_role": target_role,
            "github_username": github_username,
            "analysis": result["output"],
            "tool_based": True
        }
        
    except Exception as e:
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
    
    # Try to split by section headers
    markers = {
        "job_search": ["**1. Job Search", "Job Search Strategy", "**Job Search"],
        "skill_gaps": ["**2. Skill Gap", "Skill Gap Analysis", "**Skill"],
        "project_ideas": ["**3. Project", "Project Ideas", "**Project"],
        "github_summary": ["**4. GitHub", "GitHub Profile Review", "**GitHub"]
    }
    
    # Simple parsing - split by markers
    for section_key, possible_markers in markers.items():
        for marker in possible_markers:
            if marker in analysis_text:
                # Find start of this section
                start_idx = analysis_text.find(marker)
                
                # Find start of next section (or end of text)
                end_idx = len(analysis_text)
                for other_markers in markers.values():
                    for other_marker in other_markers:
                        idx = analysis_text.find(other_marker, start_idx + len(marker))
                        if idx != -1 and idx < end_idx:
                            end_idx = idx
                
                sections[section_key] = analysis_text[start_idx:end_idx].strip()
                break
    
    # Fallback: if parsing failed, return full text in job_search
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
    print("🧪 Testing Career Assistant Agent with Tools...\n")
    
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
    print("🔧 Running agent with 4 tools...\n")
    
    try:
        result = analyze_career(resume_text, target_role, github_username)
        
        if result["status"] == "success":
            print("✅ Analysis Complete!\n")
            print("="*60)
            print(result["analysis"][:500])
            print("="*60)
        else:
            print(f"❌ Error: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_agent()
