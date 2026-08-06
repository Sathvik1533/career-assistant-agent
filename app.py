"""
FastAPI Career Assistant with detailed error logging
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
    version="3.1.0",
    description="Simple Career Assistant using Gemini"
)


class CareerRequest(BaseModel):
    resume_text: str
    target_role: str
    github_username: str


def create_agent():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    
    print(f"🔑 API Key configured: {api_key[:10]}...")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",
        google_api_key=api_key,
        temperature=0.7,
    )
    
    print("✅ LLM initialized")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Career Assistant. Provide job search tips, skill analysis, project ideas, and GitHub advice."),
        ("human", "{query}")
    ])
    
    return prompt | llm | StrOutputParser()


@app.get("/")
def home():
    return {
        "message": "Career Assistant API",
        "version": "3.1.0",
        "model": "gemini-1.5-flash-latest",
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
        "api_key_set": bool(api_key),
        "api_key_length": len(api_key) if api_key else 0
    }


@app.post("/analyze")
async def analyze(request: CareerRequest):
    print(f"📨 Received request for role: {request.target_role}")
    
    try:
        print("🤖 Creating agent...")
        agent = create_agent()
        
        query = f"""
Target Role: {request.target_role}
GitHub: {request.github_username}
Resume: {request.resume_text[:1000]}

Provide: job tips, skill gaps, project ideas, GitHub advice.
"""
        
        print("🔄 Invoking agent...")
        result = agent.invoke({"query": query})
        
        print("✅ Analysis complete")
        
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
