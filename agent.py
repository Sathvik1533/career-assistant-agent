"""
LangGraph Career Assistant Agent

Single agent with 4 tools that:
1. Searches for jobs
2. Analyzes skill gaps
3. Suggests portfolio projects
4. Checks GitHub profile

Then validates outputs and synthesizes a final report.
"""

import os
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

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

# Bind tools to LLM
tools = [
    job_search_tool,
    skill_gap_analysis_tool,
    project_idea_generator_tool,
    github_checker_tool
]

llm_with_tools = llm.bind_tools(tools)
tool_executor = ToolExecutor(tools)


# Define agent state
class AgentState(Dict):
    """State for the Career Assistant Agent"""
    resume_text: str
    target_role: str
    github_username: str
    messages: List
    tool_outputs: Dict[str, Any]
    validation_result: Dict[str, Any]
    final_report: Dict[str, Any]
    next_step: str


def create_agent_graph():
    """Create the LangGraph agent with all nodes and edges"""
    
    workflow = StateGraph(AgentState)
    
    # Node 1: Initial planning
    def plan_node(state: AgentState) -> AgentState:
        """Agent decides which tools to call"""
        print("\n🤖 Agent: Planning analysis strategy...")
        
        system_msg = """You are a career assistant agent with 4 tools:
1. job_search_tool - Find job openings
2. skill_gap_analysis_tool - Analyze resume vs role
3. project_idea_generator_tool - Suggest portfolio projects
4. github_checker_tool - Check GitHub profile

Your task: Use ALL 4 tools to help the user. 
Call them in order, passing appropriate arguments."""
        
        user_msg = f"""Analyze this candidate:
- Target Role: {state['target_role']}
- GitHub: {state['github_username']}
- Resume available: Yes

Execute all 4 tools to provide complete career guidance."""
        
        messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=user_msg)
        ]
        
        response = llm_with_tools.invoke(messages)
        
        state['messages'] = messages + [response]
        state['next_step'] = "execute_tools"
        
        return state
    
    # Node 2: Execute tools
    def execute_tools_node(state: AgentState) -> AgentState:
        """Execute all 4 tools"""
        print("\n🔧 Executing tools...")
        
        tool_outputs = {}
        
        # Tool 1: Job Search
        try:
            print("  1/4 Job Search...")
            result = job_search_tool.invoke(state['target_role'])
            tool_outputs['job_search'] = result
        except Exception as e:
            tool_outputs['job_search'] = f"Error: {str(e)}"
        
        # Tool 2: Skill Gap Analysis
        try:
            print("  2/4 Skill Gap Analysis...")
            result = skill_gap_analysis_tool.invoke({
                "resume_text": state['resume_text'],
                "target_role": state['target_role']
            })
            tool_outputs['skill_gap_analysis'] = result
        except Exception as e:
            tool_outputs['skill_gap_analysis'] = f"Error: {str(e)}"
        
        # Tool 3: Project Ideas (using skill gaps)
        try:
            print("  3/4 Project Idea Generation...")
            missing_skills = "Based on resume analysis"  # Could parse from tool 2
            result = project_idea_generator_tool.invoke({
                "missing_skills": missing_skills,
                "target_role": state['target_role']
            })
            tool_outputs['project_ideas'] = result
        except Exception as e:
            tool_outputs['project_ideas'] = f"Error: {str(e)}"
        
        # Tool 4: GitHub Check
        try:
            print("  4/4 GitHub Analysis...")
            result = github_checker_tool.invoke(state['github_username'])
            tool_outputs['github_check'] = result
        except Exception as e:
            tool_outputs['github_check'] = f"Error: {str(e)}"
        
        state['tool_outputs'] = tool_outputs
        state['next_step'] = "validate"
        
        return state
    
    # Node 3: Validate outputs
    def validate_node(state: AgentState) -> AgentState:
        """Validate all tool outputs"""
        print("\n✅ Validating outputs...")
        
        validation = validate_tool_outputs(state['tool_outputs'])
        state['validation_result'] = validation
        
        if validation['valid']:
            print("  All tools executed successfully!")
            state['next_step'] = "synthesize"
        else:
            print(f"  Validation issues: {validation['errors']}")
            state['next_step'] = "synthesize"  # Continue anyway
        
        return state
    
    # Node 4: Synthesize report
    def synthesize_node(state: AgentState) -> AgentState:
        """Combine all outputs into final report"""
        print("\n📄 Synthesizing final report...")
        
        report = synthesize_report(
            outputs=state['tool_outputs'],
            resume_text=state['resume_text'],
            target_role=state['target_role'],
            github_username=state['github_username']
        )
        
        state['final_report'] = report
        state['next_step'] = "end"
        
        print("  Report complete!")
        
        return state
    
    # Add nodes
    workflow.add_node("plan", plan_node)
    workflow.add_node("execute_tools", execute_tools_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("synthesize", synthesize_node)
    
    # Add edges
    workflow.set_entry_point("plan")
    workflow.add_edge("plan", "execute_tools")
    workflow.add_edge("execute_tools", "validate")
    workflow.add_edge("validate", "synthesize")
    workflow.add_edge("synthesize", END)
    
    return workflow.compile()


def run_career_analysis(resume_text: str, target_role: str, github_username: str) -> Dict[str, Any]:
    """
    Run the complete career analysis.
    
    Args:
        resume_text: Text extracted from resume PDF
        target_role: Target job role (e.g., "Software Engineer")
        github_username: GitHub username to analyze
    
    Returns:
        Complete analysis report as dictionary
    """
    print("\n" + "="*80)
    print("🚀 STARTING CAREER ANALYSIS")
    print("="*80)
    
    # Initialize state
    initial_state = {
        "resume_text": resume_text,
        "target_role": target_role,
        "github_username": github_username,
        "messages": [],
        "tool_outputs": {},
        "validation_result": {},
        "final_report": {},
        "next_step": "plan"
    }
    
    # Create and run agent
    agent = create_agent_graph()
    
    try:
        final_state = agent.invoke(initial_state)
        return final_state['final_report']
    
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }


# Export main function
__all__ = ["run_career_analysis", "create_agent_graph"]
