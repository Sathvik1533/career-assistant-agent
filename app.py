"""
FastAPI Web Server with LangServe for Career Assistant Agent

Endpoints:
- GET  /                    - Home
- GET  /health              - Health check  
- POST /analyze             - Upload resume and get analysis (REST API)
- POST /agent/invoke        - LangServe invoke endpoint
- POST /agent/stream        - LangServe streaming endpoint
- GET  /agent/playground    - LangServe interactive playground
- GET  /docs                - API documentation
"""

import os
import tempfile
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from langserve import add_routes

from agent import run_career_analysis, create_career_agent
from utils import extract_text_from_pdf

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Career Assistant Agent API",
    version="2.0.0",
    description="LangChain agent with 4 tools for career assistance using Gemma 4 31B"
)


# =============================================================================
# LANGSERVE ROUTES - Interactive Playground
# =============================================================================

# Create the agent for LangServe
try:
    career_agent = create_career_agent()
    
    # Add LangServe routes - this gives us /agent/playground
    add_routes(
        app,
        career_agent,
        path="/agent",
        enabled_endpoints=["invoke", "stream", "playground"],
    )
    print("✅ LangServe routes added at /agent")
except Exception as e:
    print(f"⚠️  Warning: Could not initialize agent for LangServe: {e}")
    print("   (Make sure GOOGLE_API_KEY is set)")


# =============================================================================
# REST API ENDPOINTS
# =============================================================================

@app.get("/")
def home():
    """Home endpoint with API information"""
    return {
        "message": "Career Assistant Agent API",
        "version": "2.0.0",
        "model": "Gemma 4 31B (models/gemma-4-31b-it)",
        "framework": "LangChain (NO LangGraph)",
        "tools": [
            "Job Search",
            "Skill Gap Analysis",
            "Project Idea Generator",
            "GitHub Checker"
        ],
        "endpoints": {
            "langserve_playground": "/agent/playground (Interactive UI)",
            "langserve_invoke": "/agent/invoke (POST)",
            "langserve_stream": "/agent/stream (POST)",
            "rest_analyze": "/analyze (POST - Upload resume)",
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
        "api_key_configured": api_key_set,
        "langserve_enabled": True
    }


@app.post("/analyze")
async def analyze_career(
    resume: UploadFile = File(..., description="Resume PDF file"),
    target_role: str = Form(..., description="Target job role (e.g., 'Software Engineer')"),
    github_username: str = Form(..., description="GitHub username to analyze")
):
    """
    REST API: Analyze career prospects with resume, target role, and GitHub profile.
    
    This endpoint accepts file upload and returns comprehensive report with:
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
