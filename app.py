"""
FastAPI Career Assistant with CORRECT Gemini model
"""

import os
import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

app = FastAPI(
    title="Career Assistant Agent",
    version="3.2.0",
    description="Career Assistant using Gemini Pro"
)


class CareerRequest(BaseModel):
    resume_text: str
    target_role: str
    github_username: str


def create_agent():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    
    # Use gemini-pro - this DEFINITELY exists!
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=api_key,
        temperature=0.7,
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Career Assistant. Provide job search tips, skill analysis, project ideas, and GitHub advice."),
        ("human", "{query}")
    ])
    
    return prompt | llm | StrOutputParser()


@app.get("/")
def home():
    return {
        "message": "Career Assistant API",
        "version": "3.2.0",
        "model": "gemini-pro",
        "endpoints": {
            "home": "/",
            "health": "/health",
            "analyze": "/analyze (POST)",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health():
    api_key = os.getenv("GOOGLE_API_KEY")
    return {
        "status": "healthy",
        "api_key_set": bool(api_key)
    }


@app.post("/analyze")
async def analyze(request: CareerRequest):
    try:
        agent = create_agent()
        
        query = f"""
Target Role: {request.target_role}
GitHub: {request.github_username}
Resume: {request.resume_text[:500]}

Provide job search tips, skill gap analysis, project ideas, and GitHub profile advice.
"""
        
        result = agent.invoke({"query": query})
        
        return {
            "status": "success",
            "target_role": request.target_role,
            "github_username": request.github_username,
            "analysis": result
        }
        
    except Exception as e:
        error_detail = f"{type(e).__name__}: {str(e)}"
        print(f"❌ Error: {error_detail}")
        print(traceback.format_exc())
        
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {error_detail}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
