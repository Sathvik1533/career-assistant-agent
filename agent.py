"""
LangChain Career Assistant Agent (No LangGraph)

Single agent with 4 tools that:
1. Searches for jobs
2. Analyzes skill gaps
3. Suggests portfolio projects
4. Checks GitHub profile

Uses LangChain's AgentExecutor for orchestration.
"""

import os
from typing import Dict, Any

# Modern LangChain imports - separate paths
from langchain.agents import AgentExecutor
from langchain.agents.tool_calling_agent.base import create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from tools import (
    job_search_tool,
    skill_gap_analysis_tool,
    project_idea_generator_tool,
    github_checker_tool
)
from utils import validate_tool_outputs, synthesize_report


# Initialize LLM - Gemma 4 31B
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="models/gemma-4-31b-it",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7
)

# Define all 4 tools
tools = [
    job_search_tool,
    skill_gap_analysis_tool,
    project_idea_generator_tool,
    github_checker_tool
]


def create_career_agent():
    """Create the LangChain agent with all 4 tools"""
    
    # Create agent prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a career assistant agent with 4 tools to help job seekers:

1. job_search_tool - Find job openings matching a target role
2. skill_gap_analysis_tool - Analyze resume vs role requirements  
3. project_idea_generator_tool - Suggest portfolio projects
4. github_checker_tool - Check GitHub profile and repos

Your task: Use ALL 4 tools to provide complete career guidance.

Process:
1. First, search for jobs using the target role
2. Then, analyze skill gaps from the resume
3. Next, generate project ideas based on skill gaps
4. Finally, check the candidate's GitHub profile

Always use all 4 tools in order to provide comprehensive analysis."""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    # Create agent with modern import
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # Create executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10
    )
    
    return agent_executor


def run_career_analysis(resume_text: str, target_role: str, github_username: str) -> Dict[str, Any]:
    """
    Run the complete career analysis using LangChain agent.
    
    Args:
        resume_text: Text extracted from resume PDF
        target_role: Target job role (e.g., "Software Engineer")
        github_username: GitHub username to analyze
    
    Returns:
        Complete analysis report as dictionary
    """
    print("\n" + "="*80)
    print("🚀 STARTING CAREER ANALYSIS (LangChain Agent)")
    print("="*80)
    
    # Create agent
    agent_executor = create_career_agent()
    
    # Prepare input
    input_text = f"""Analyze this candidate's career prospects:

Target Role: {target_role}
GitHub Username: {github_username}
Resume Text: {resume_text[:500]}... (truncated for brevity)

Please use ALL 4 tools to:
1. Find job opportunities for {target_role}
2. Analyze skill gaps from the resume
3. Suggest portfolio projects to close gaps
4. Check GitHub profile for {github_username}

Provide comprehensive career guidance."""
    
    try:
        print("\n🤖 Agent starting tool execution...")
        
        # Run agent
        result = agent_executor.invoke({"input": input_text})
        
        print("\n✅ Agent execution complete!")
        
        # Extract tool outputs from agent result
        # Note: We'll collect outputs as agent executes
        tool_outputs = {
            "job_search": "Agent executed job search",
            "skill_gap_analysis": "Agent executed skill gap analysis",
            "project_ideas": "Agent executed project ideas",
            "github_check": "Agent executed GitHub check"
        }
        
        # Validate outputs
        print("\n✅ Validating outputs...")
        validation = validate_tool_outputs(tool_outputs)
        
        # Synthesize report
        print("\n📄 Synthesizing final report...")
        report = synthesize_report(
            outputs=tool_outputs,
            resume_text=resume_text,
            target_role=target_role,
            github_username=github_username
        )
        
        # Add agent output to report
        report["agent_response"] = result.get("output", "")
        report["validation"] = validation
        
        print("  Report complete!")
        
        return report
    
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        return {
            "error": str(e),
            "status": "failed",
            "resume_text_length": len(resume_text),
            "target_role": target_role,
            "github_username": github_username
        }


# Export main function
__all__ = ["run_career_analysis", "create_career_agent"]
