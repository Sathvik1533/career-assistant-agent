"""
FastAPI Career Assistant with Groq + LangServe Playground
"""

import os
import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langserve import add_routes

load_dotenv()

app = FastAPI(
    title="Career Assistant Agent",
    version="4.1.0",
    description="Career Assistant using Groq with LangServe Playground"
)


# Pydantic models
class CareerRequest(BaseModel):
    resume_text: str
    target_role: str
    github_username: str


class PlaygroundInput(BaseModel):
    """Input for LangServe playground"""
    query: str = Field(description="Career analysis query with resume, role, and GitHub username")


def create_agent():
    """Create Groq-powered agent chain"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=api_key,
        temperature=0.7,
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Career Assistant. Provide job search tips, skill analysis, project ideas, and GitHub advice."),
        ("human", "{query}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    # Add input schema for LangServe
    chain = chain.with_types(input_type=PlaygroundInput)
    
    return chain


# =============================================================================
# LANGSERVE PLAYGROUND
# =============================================================================

try:
    career_chain = create_agent()
    
    add_routes(
        app,
        career_chain,
        path="/agent",
        enabled_endpoints=["invoke", "stream", "playground"],
    )
    print("✅ LangServe playground added at /agent/playground")
except Exception as e:
    print(f"⚠️  Warning: Could not add LangServe routes: {e}")


# =============================================================================
# REST API ENDPOINTS
# =============================================================================

@app.get("/")
def home():
    return {
        "message": "Career Assistant API with Groq",
        "version": "4.1.0",
        "model": "Groq Llama 3.3 70B",
        "endpoints": {
            "home": "/",
            "health": "/health",
            "analyze": "/analyze (POST - JSON)",
            "playground": "/agent/playground (Interactive UI)",
            "invoke": "/agent/invoke (POST - LangServe)",
            "stream": "/agent/stream (POST - LangServe)",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health():
    api_key = os.getenv("GROQ_API_KEY")
    return {
        "status": "healthy",
        "api_key_set": bool(api_key),
        "model": "llama-3.3-70b-versatile"
    }


@app.post("/analyze")
async def analyze(request: CareerRequest):
    """REST API endpoint for career analysis"""
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
