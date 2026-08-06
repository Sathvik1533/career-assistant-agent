"""
Career Assistant Agent - LangChain Implementation
Powered by Groq Llama 3.3 70B

This module provides the core agent logic for career guidance.
Can be used standalone or imported by the FastAPI app.
"""

import os
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field


class CareerInput(BaseModel):
    """Input schema for career assistant agent"""
    query: str = Field(
        description="Career analysis query including resume info, target role, and GitHub username"
    )


def create_career_agent():
    """
    Create a LangChain agent for career guidance using Groq
    
    The agent provides:
    - Job search strategies
    - Skill gap analysis
    - Project ideas for portfolio
    - GitHub profile optimization tips
    
    Returns:
        Runnable chain that processes career queries
        
    Raises:
        ValueError: If GROQ_API_KEY is not set
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    
    # Initialize Groq LLM
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=api_key,
        temperature=0.7,  # Balance between creativity and consistency
    )
    
    # Create system prompt
    system_prompt = """You are an expert Career Assistant helping professionals advance their careers.

Your role is to provide comprehensive, actionable career guidance tailored to each individual's:
- Current skills and experience (from resume)
- Target job role and industry
- Online presence (GitHub profile)

When analyzing, provide specific advice in these 4 areas:

1. **Job Search Strategy**
   - Specific companies and job boards to target
   - Keywords and skills to highlight
   - Networking strategies
   - Timeline and action steps

2. **Skill Gap Analysis**
   - Technical skills needed for target role
   - Soft skills to develop
   - Learning resources (courses, books, tutorials)
   - Practice opportunities

3. **Project Ideas**
   - 2-3 portfolio projects that demonstrate target role skills
   - Technologies to use
   - Complexity and time estimates
   - How to showcase them effectively

4. **GitHub Profile Review**
   - README improvements
   - Repository organization
   - Documentation best practices
   - Profile presentation tips

Be specific, realistic, and encouraging. Provide actionable steps, not generic advice."""

    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{query}")
    ])
    
    # Build the chain: prompt -> LLM -> string output
    chain = prompt | llm | StrOutputParser()
    
    # Add input schema for validation
    chain = chain.with_types(input_type=CareerInput)
    
    return chain


def run_career_analysis(
    resume_text: str, 
    target_role: str, 
    github_username: str
) -> Dict[str, Any]:
    """
    Run career analysis with given inputs
    
    This is a convenience function for direct usage without FastAPI.
    
    Args:
        resume_text: Text extracted from resume
        target_role: Desired job position
        github_username: GitHub username for profile review
        
    Returns:
        Dictionary with status and analysis results
    """
    agent = create_career_agent()
    
    # Construct query
    user_query = f"""
Analyze this career profile:

**Target Role:** {target_role}
**GitHub Username:** {github_username}
**Resume Summary:** {resume_text[:1000]}...

Please provide detailed analysis covering:
1. Job Search Strategy
2. Skill Gap Analysis
3. Project Ideas
4. GitHub Profile Tips
"""
    
    # Get analysis from agent
    result = agent.invoke({"query": user_query})
    
    return {
        "status": "success",
        "target_role": target_role,
        "github_username": github_username,
        "analysis": result
    }


# ============================================================================
# CLI TESTING
# ============================================================================

def test_agent():
    """Test function for development"""
    print("🧪 Testing Career Assistant Agent...\n")
    
    # Sample inputs
    resume_text = """
    Software Engineer with 2 years of experience in Python and JavaScript.
    Built web applications using React and Django. Familiar with SQL databases.
    """
    
    target_role = "Senior Software Engineer"
    github_username = "example-user"
    
    try:
        result = run_career_analysis(resume_text, target_role, github_username)
        print(f"✅ Status: {result['status']}")
        print(f"📊 Analysis length: {len(result['analysis'])} characters")
        print(f"\n{result['analysis'][:500]}...\n")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Test the agent when run directly
    test_agent()
