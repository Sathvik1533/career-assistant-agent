"""
Simple LangChain Career Assistant - LangServe Compatible
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def create_career_agent():
    """
    Create a simple career assistant chain compatible with LangServe.
    """
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment")
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-1.5-flash",  # Using a model that definitely exists
        google_api_key=api_key,
        temperature=0.7,
    )
    
    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Career Assistant helping candidates with their job search.

Based on the user's input about their resume, target role, and GitHub username, provide:

1. **Job Search Tips**: Suggest where to find relevant jobs and what keywords to use
2. **Skill Gap Analysis**: Based on their experience, identify likely skill gaps for their target role
3. **Project Ideas**: Suggest 2-3 portfolio projects they could build
4. **GitHub Profile Review**: Give tips on how to improve their GitHub presence

Be specific, actionable, and encouraging."""),
        ("human", "{input}")
    ])
    
    # Build chain
    chain = (
        {"input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain


def run_career_analysis(resume_text: str, target_role: str, github_username: str):
    """Run career analysis - for REST API endpoint"""
    agent = create_career_agent()
    
    user_input = f"""
Please analyze my career prospects:

Target Role: {target_role}
GitHub Username: {github_username}

My Background:
{resume_text[:1000]}

Please provide:
1. Job search strategy
2. Skill gap analysis
3. Portfolio project ideas
4. GitHub profile tips
"""
    
    result = agent.invoke(user_input)
    
    return {
        "status": "success",
        "target_role": target_role,
        "github_username": github_username,
        "analysis": result
    }


if __name__ == "__main__":
    print("✅ Simple Career Agent loaded (LangServe compatible)")
