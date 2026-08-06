"""
LangChain Career Assistant - LangServe Compatible with Input Schema
"""

import os
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field


class CareerInput(BaseModel):
    """Input schema for career assistant"""
    query: str = Field(description="Career analysis query with resume info, target role, and GitHub username")


def create_career_agent():
    """
    Create a career assistant chain with proper input schema for LangServe.
    """
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment")
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0.7,
    )
    
    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Career Assistant helping candidates with their job search.

Based on the user's input, provide:
1. **Job Search Tips**: Relevant jobs and keywords
2. **Skill Gap Analysis**: Skills they need to develop
3. **Project Ideas**: 2-3 portfolio projects to build
4. **GitHub Profile Tips**: How to improve their presence

Be specific and actionable."""),
        ("human", "{query}")
    ])
    
    # Build chain
    chain = prompt | llm | StrOutputParser()
    
    # Add input schema
    chain = chain.with_types(input_type=CareerInput)
    
    return chain


def run_career_analysis(resume_text: str, target_role: str, github_username: str) -> Dict[str, Any]:
    """Run career analysis - for REST API endpoint"""
    agent = create_career_agent()
    
    user_query = f"""
Target Role: {target_role}
GitHub: {github_username}

Resume: {resume_text[:1000]}

Please analyze and provide job search tips, skill gaps, project ideas, and GitHub tips.
"""
    
    result = agent.invoke({"query": user_query})
    
    return {
        "status": "success",
        "target_role": target_role,
        "github_username": github_username,
        "analysis": result
    }


if __name__ == "__main__":
    print("✅ Career Agent with input schema loaded")
