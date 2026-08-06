"""
Career Assistant Agent with Real AgentExecutor
Uses LangChain's create_tool_calling_agent and AgentExecutor for proper runtime loop
"""

import os
import re
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Import our custom tools
try:
    from tools import career_tools
except ImportError:
    print("⚠️  Warning: tools module not found. Make sure tools.py is in the same directory.")
    career_tools = []


def create_career_agent() -> AgentExecutor:
    """
    Create a real AgentExecutor with tool-calling runtime loop
    
    The agent has access to 4 specialized tools:
    1. job_search_advisor - Job search strategies
    2. skill_gap_analyzer - Skill gap analysis
    3. project_idea_generator - Portfolio project ideas
    4. github_profile_analyzer - GitHub profile review with API
    
    Returns:
        AgentExecutor with tools and runtime loop
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
    
    # Create prompt template for agent
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Career Assistant Agent with access to 4 specialized tools.

Your role is to provide comprehensive career guidance by:
1. Analyzing job search strategies for the target role
2. Identifying skill gaps and learning recommendations
3. Generating portfolio project ideas
4. Reviewing GitHub profile and suggesting improvements

**Available Tools:**
- job_search_advisor: Get personalized job search strategies
- skill_gap_analyzer: Analyze skill gaps and learning path
- project_idea_generator: Generate portfolio project ideas
- github_profile_analyzer: Analyze GitHub profile using REST API

**Instructions:**
1. Use ALL 4 tools to gather comprehensive information
2. Call each tool with appropriate parameters (resume_text, target_role, github_username)
3. After gathering all tool outputs, synthesize them into a well-structured report
4. Organize the final response with clear sections:
   - Job Search Strategy
   - Skill Gap Analysis
   - Project Ideas
   - GitHub Profile Review

Be specific, actionable, and professional in your recommendations."""),
        ("human", """Please analyze my career profile and provide comprehensive guidance.

**Target Role:** {target_role}

**Resume Summary:**
{resume_text}

**GitHub Username:** {github_username}

Use all 4 tools to gather insights, then provide a complete career analysis report."""),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create tool-calling agent
    agent = create_tool_calling_agent(llm, career_tools, prompt)
    
    # Create AgentExecutor with runtime loop
    agent_executor = AgentExecutor(
        agent=agent,
        tools=career_tools,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True,
        return_intermediate_steps=False
    )
    
    return agent_executor


def analyze_career(
    resume_text: str,
    target_role: str, 
    github_username: str
) -> Dict[str, Any]:
    """
    Run comprehensive career analysis using AgentExecutor
    
    Args:
        resume_text: Candidate's resume content
        target_role: Desired job position
        github_username: GitHub username for profile analysis
        
    Returns:
        Dictionary with analysis results from agent
    """
    try:
        print("🤖 Initializing AgentExecutor...")
        
        # Create agent executor
        agent_executor = create_career_agent()
        
        print("🔧 Running agent with tool-calling runtime loop...")
        
        # Execute agent with inputs
        result = agent_executor.invoke({
            "resume_text": resume_text[:800],  # Limit resume length
            "target_role": target_role,
            "github_username": github_username
        })
        
        # Extract output from agent result
        analysis = result.get("output", "")
        
        print("✅ Agent execution complete!")
        
        return {
            "status": "success",
            "target_role": target_role,
            "github_username": github_username,
            "analysis": analysis,
            "agent_type": "AgentExecutor",
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
    Parse agent output into 4 sections using more robust parsing
    
    Args:
        analysis_text: Complete analysis from agent
        
    Returns:
        Dictionary with 4 sections: job_search, skill_gaps, project_ideas, github_summary
    """
    import re
    
    sections = {
        "job_search": "",
        "skill_gaps": "",
        "project_ideas": "",
        "github_summary": ""
    }
    
    # Try multiple header patterns (agent might format differently)
    patterns = [
        # Pattern 1: Numbered headers
        (r"##?\s*1\.?\s*Job Search.*?\n(.*?)(?=##?\s*2|$)", "job_search"),
        (r"##?\s*2\.?\s*Skill Gap.*?\n(.*?)(?=##?\s*3|$)", "skill_gaps"),
        (r"##?\s*3\.?\s*Project.*?\n(.*?)(?=##?\s*4|$)", "project_ideas"),
        (r"##?\s*4\.?\s*GitHub.*?\n(.*?)$", "github_summary"),
        
        # Pattern 2: Non-numbered headers
        (r"##?\s*Job Search.*?\n(.*?)(?=##|$)", "job_search"),
        (r"##?\s*Skill Gap.*?\n(.*?)(?=##|$)", "skill_gaps"),
        (r"##?\s*Project.*?\n(.*?)(?=##|$)", "project_ideas"),
        (r"##?\s*GitHub.*?\n(.*?)$", "github_summary"),
    ]
    
    # Try to extract each section
    for pattern, key in patterns:
        if not sections[key]:  # Only if not already found
            match = re.search(pattern, analysis_text, re.IGNORECASE | re.DOTALL)
            if match:
                sections[key] = match.group(1).strip()
    
    # Fallback: if sections are still empty, try to split the analysis
    if not any(sections.values()):
        # Split by double newlines and take chunks
        chunks = [chunk.strip() for chunk in analysis_text.split('\n\n') if chunk.strip()]
        if len(chunks) >= 4:
            sections["job_search"] = chunks[0]
            sections["skill_gaps"] = chunks[1] if len(chunks) > 1 else ""
            sections["project_ideas"] = chunks[2] if len(chunks) > 2 else ""
            sections["github_summary"] = chunks[3] if len(chunks) > 3 else ""
        else:
            # Last resort: put everything in job_search
            sections["job_search"] = analysis_text
            sections["skill_gaps"] = "See comprehensive analysis above"
            sections["project_ideas"] = "See comprehensive analysis above"
            sections["github_summary"] = "See comprehensive analysis above"
    
    return sections


# ============================================================================
# CLI TESTING
# ============================================================================

def test_agent():
    """Test the AgentExecutor with dynamic terminal input"""
    print("🧪 Testing Career Assistant AgentExecutor\n")
    print("="*60)
    print("Please provide the following information:")
    print("="*60)
    
    # Get resume text from user
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
    
    # If no resume provided, use sample
    if not resume_text:
        print("⚠️  No resume provided, using sample data...")
        resume_text = """Software Engineer with 2 years of experience in Python and JavaScript.
Built web applications using React and FastAPI.
Familiar with SQL databases and REST APIs.
Experience with Git and Docker."""
    
    # Get target role
    print("\n🎯 Enter target role (e.g., 'Senior Full-Stack Engineer'):")
    target_role = input().strip()
    if not target_role:
        print("⚠️  No role provided, using default: 'Senior Full-Stack Engineer'")
        target_role = "Senior Full-Stack Engineer"
    
    # Get GitHub username
    print("\n🐙 Enter GitHub username (e.g., 'Sathvik1533'):")
    github_username = input().strip()
    if not github_username:
        print("⚠️  No username provided, using default: 'Sathvik1533'")
        github_username = "Sathvik1533"
    
    print("\n" + "="*60)
    print("Input Summary:")
    print("="*60)
    print(f"📄 Resume: {resume_text[:100]}{'...' if len(resume_text) > 100 else ''}")
    print(f"🎯 Target Role: {target_role}")
    print(f"🐙 GitHub: {github_username}")
    print("="*60 + "\n")
    
    try:
        result = analyze_career(resume_text, target_role, github_username)
        
        if result["status"] == "success":
            print("\n✅ Agent Analysis Complete!\n")
            print("="*60)
            print(f"Agent Type: {result.get('agent_type', 'Unknown')}")
            print("="*60)
            print(result["analysis"][:800])
            print("="*60)
            
            # Test section parsing
            print("\n📊 Testing Section Parsing...")
            sections = parse_analysis_sections(result["analysis"])
            for key, value in sections.items():
                print(f"\n{key.upper()}: {len(value)} chars")
        else:
            print(f"❌ Error: {result.get('error')}")
            print(f"Traceback: {result.get('traceback')}")
            
    except Exception as e:
        import traceback
        print(f"❌ Test failed: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    test_agent()
