"""
FastAPI Web Server for Career Assistant Agent

Endpoints:
- GET  /           - Home
- GET  /health     - Health check  
- POST /analyze    - Upload resume and get analysis
- GET  /docs       - API documentation
"""

import os
import tempfile
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from langchain.agents import AgentExecutor

from agent import run_career_analysis
from utils import extract_text_from_pdf

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Career Assistant Agent API",
    version="1.0.0",
    description="LangGraph agent with 4 tools for career assistance using Gemma 4 31B"
)


@app.get("/")
def home():
    """Home endpoint with API information"""
    return {
        "message": "Career Assistant Agent API",
        "version": "1.0.0",
        "model": "Gemma 4 31B (models/gemma-4-31b-it)",
        "tools": [
            "Job Search",
            "Skill Gap Analysis",
            "Project Idea Generator",
            "GitHub Checker"
        ],
        "endpoints": {
            "analyze": "/analyze (POST)",
            "health": "/health (GET)",
            "docs": "/docs (GET)"
        },
        "github": "https://github.com/Sathvik1533/career-assistant-agent"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    api_key_set = bool(os.getenv("GOOGLE_API_KEY"))
    return {
        "status": "healthy",
        "api_key_configured": api_key_set
    }


@app.post("/analyze")
async def analyze_career(
    resume: UploadFile = File(..., description="Resume PDF file"),
    target_role: str = Form(..., description="Target job role (e.g., 'Software Engineer')"),
    github_username: str = Form(..., description="GitHub username to analyze")
):
    """
    Analyze career prospects with resume, target role, and GitHub profile.
    
    Returns comprehensive report with:
    - Job opportunities
    - Skill gap analysis
    - Project recommendations
    - GitHub portfolio summary
    """
    
    # Validate API key
    if not os.getenv("GOOGLE_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_API_KEY not configured on server"
        )
    
    # Validate file type
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    # Save uploaded file temporarily
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await resume.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Extract text from PDF
        resume_text = extract_text_from_pdf(tmp_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"PDF extraction failed: {str(e)}"
        )
    
    # Run analysis
    try:
        report = run_career_analysis(
            resume_text=resume_text,
            target_role=target_role,
            github_username=github_username
        )
        
        return JSONResponse(content=report)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/tools")
def list_tools():
    """List available tools and their descriptions"""
    return {
        "tools": [
            {
                "name": "Job Search",
                "description": "Finds relevant job openings matching the target role",
                "input": "target_role",
                "output": "List of jobs with requirements"
            },
            {
                "name": "Skill Gap Analysis",
                "description": "Compares resume skills against role requirements",
                "input": "resume_text, target_role",
                "output": "Missing skills, strengths, match percentage"
            },
            {
                "name": "Project Idea Generator",
                "description": "Suggests portfolio projects to close skill gaps",
                "input": "missing_skills, target_role",
                "output": "Project ideas with tech stacks"
            },
            {
                "name": "GitHub Checker",
                "description": "Analyzes GitHub profile and repositories",
                "input": "github_username",
                "output": "Repo summary, languages, activity"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
