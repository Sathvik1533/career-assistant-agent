"""
LangChain Career Assistant Agent (No LangGraph)

Single agent with 4 tools that:
1. Searches for jobs
2. Analyzes skill gaps
3. Suggests portfolio projects
4. Checks GitHub profile

Uses LangChain 0.3.x with tool-calling via ChatGoogleGenerativeAI
"""

import os
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from tools import (
    job_search_tool,
    skill_gap_analysis_tool,
    project_idea_generator_tool,
    github_checker_tool
)

from utils import extract_text_from_pdf, validate_inputs, synthesize_report


def create_career_agent():
    """
    Create a LangChain career assistant agent using tool calling.
    Compatible with LangChain 0.3.x and LangServe.
    """
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment")
    
    # Initialize LLM with tool binding
    llm = ChatGoogleGenerativeAI(
        model="models/gemma-4-31b-it",
        google_api_key=api_key,
        temperature=0.1,
    )
    
    # Bind tools to LLM
    tools = [
        job_search_tool,
        skill_gap_analysis_tool,
        project_idea_generator_tool,
        github_checker_tool
    ]
    
    llm_with_tools = llm.bind_tools(tools)
    
    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Career Assistant Agent helping candidates improve their job prospects.

You have access to 4 tools:
1. job_search_tool - Find relevant job openings
2. skill_gap_analysis_tool - Analyze skill gaps
3. project_idea_generator_tool - Suggest portfolio projects
4. github_checker_tool - Check GitHub profile

Given a user's resume, target role, and GitHub username:
1. Use ALL 4 tools to gather information
2. Synthesize the results into a comprehensive career report
3. Provide actionable recommendations

Be thorough and use all available tools."""),
        ("human", "{input}")
    ])
    
    # Build chain
    chain = prompt | llm_with_tools | StrOutputParser()
    
    return chain


def run_career_analysis(resume_text: str, target_role: str, github_username: str) -> Dict[str, Any]:
    """
    Run complete career analysis with resume, target role, and GitHub profile.
    
    Returns comprehensive JSON report with:
    - Job opportunities
    - Skill gap analysis
    - Project recommendations
    - GitHub portfolio summary
    """
    # Validate inputs
    validate_inputs(resume_text, target_role, github_username)
    
    # Create agent
    agent = create_career_agent()
    
    # Prepare input
    user_input = f"""
Please analyze this candidate's career prospects:

Target Role: {target_role}
GitHub Username: {github_username}

Resume:
{resume_text[:2000]}...

Please:
1. Search for {target_role} job openings
2. Analyze skill gaps between resume and role
3. Suggest portfolio projects to close gaps
4. Review GitHub profile @{github_username}

Provide a comprehensive career report.
"""
    
    # Run analysis
    try:
        result = agent.invoke({"input": user_input})
        
        # Synthesize into structured report
        report = synthesize_report(
            result=result,
            target_role=target_role,
            github_username=github_username
        )
        
        return report
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Analysis failed: {str(e)}",
            "target_role": target_role,
            "github_username": github_username
        }


if __name__ == "__main__":
    print("✅ Career Agent module loaded (LangChain 0.3.x compatible)")
