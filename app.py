"""
Simple FastAPI Career Assistant - NO LangServe complexity
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

app = FastAPI(
    title="Career Assistant Agent",
    version="3.0.0",
    description="Simple Career Assistant using Gemini"
)


class CareerRequest(BaseModel):
    resume_text: str
    target_role: str
    github_username: str


def create_agent():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",
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
        "version": "3.0.0",
        "endpoints": {
            "home": "/",
            "health": "/health",
            "analyze": "/analyze (POST)",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "api_key_set": bool(os.getenv("GOOGLE_API_KEY"))
    }


@app.post("/analyze")
async def analyze(request: CareerRequest):
    try:
        agent = create_agent()
        
        query = f"""
Target Role: {request.target_role}
GitHub: {request.github_username}
Resume: {request.resume_text[:1000]}

Provide: job tips, skill gaps, project ideas, GitHub advice.
"""
        
        result = agent.invoke({"query": query})
        
        return {
            "status": "success",
            "target_role": request.target_role,
            "github_username": request.github_username,
            "analysis": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
