"""
Career Assistant Agent - Full Production Application
Features: Real AgentExecutor, 4 LangChain Tools, GitHub API Integration
"""

import os
import traceback
from io import BytesIO
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import PyPDF2

# Import agent with tools
from agent import create_career_agent, analyze_career, parse_analysis_sections

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Career Assistant Agent",
    version="6.0.0",
    description="AI Career Assistant with AgentExecutor and 4 Specialized Tools"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CareerRequest(BaseModel):
    """JSON request model"""
    resume_text: str
    target_role: str
    github_username: str


# ============================================================================
# STATIC FILES
# ============================================================================

app.mount("/static", StaticFiles(directory="static"), name="static")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def home():
    """Serve the custom frontend"""
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    """Health check endpoint"""
    api_key = os.getenv("GROQ_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    
    return {
        "status": "healthy",
        "version": "6.0.0",
        "groq_api_key": bool(api_key),
        "github_token": bool(github_token),
        "model": "llama-3.3-70b-versatile",
        "agent_type": "AgentExecutor with 4 Tools",
        "tools": [
            "job_search_advisor",
            "skill_gap_analyzer", 
            "project_idea_generator",
            "github_profile_analyzer"
        ]
    }


def extract_text_from_pdf(pdf_file: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text.strip()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract PDF text: {str(e)}"
        )


@app.post("/analyze")
async def analyze_career_endpoint(
    resume: UploadFile = File(..., description="Resume in PDF format"),
    target_role: str = Form(..., description="Desired job role"),
    github_username: str = Form(..., description="GitHub username")
):
    """
    Main endpoint for career analysis using AgentExecutor with 4 tools
    
    The agent will:
    1. Call job_search_advisor tool
    2. Call skill_gap_analyzer tool
    3. Call project_idea_generator tool
    4. Call github_profile_analyzer tool (with GitHub API)
    5. Synthesize results into comprehensive report
    
    Returns:
        JSON with 4 sections and metadata
    """
    try:
        # Validate file type
        if not resume.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Extract text from PDF
        pdf_bytes = await resume.read()
        resume_text = extract_text_from_pdf(pdf_bytes)
        
        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF"
            )
        
        # Run agent with tools
        print(f"🤖 Running AgentExecutor for {target_role}...")
        result = analyze_career(resume_text, target_role, github_username)
        
        if result["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Agent execution failed: {result.get('error')}"
            )
        
        # Parse analysis into sections
        analysis_text = result["analysis"]
        sections = parse_analysis_sections(analysis_text)
        
        return {
            "status": "success",
            "target_role": target_role,
            "github_username": github_username,
            "job_search": sections["job_search"],
            "skill_gaps": sections["skill_gaps"],
            "project_ideas": sections["project_ideas"],
            "github_summary": sections["github_summary"],
            "full_analysis": analysis_text,
            "agent_type": "AgentExecutor",
            "tools_used": 4
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"{type(e).__name__}: {str(e)}"
        print(f"❌ Error in /analyze: {error_detail}")
        print(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {error_detail}"
        )


@app.post("/analyze-json")
async def analyze_json(request: CareerRequest):
    """
    Legacy JSON endpoint
    """
    try:
        result = analyze_career(
            request.resume_text,
            request.target_role,
            request.github_username
        )
        
        if result["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Agent execution failed: {result.get('error')}"
            )
        
        return {
            "status": "success",
            "target_role": request.target_role,
            "github_username": request.github_username,
            "analysis": result["analysis"],
            "agent_type": "AgentExecutor"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"{type(e).__name__}: {str(e)}"
        print(f"❌ Error in /analyze-json: {error_detail}")
        print(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {error_detail}"
        )


@app.get("/tools")
def list_tools():
    """List all available tools"""
    return {
        "tools": [
            {
                "name": "job_search_advisor",
                "description": "Provides personalized job search strategies"
            },
            {
                "name": "skill_gap_analyzer",
                "description": "Analyzes skill gaps and recommends learning path"
            },
            {
                "name": "project_idea_generator",
                "description": "Generates portfolio project ideas"
            },
            {
                "name": "github_profile_analyzer",
                "description": "Analyzes GitHub profile using REST API"
            }
        ],
        "agent_type": "AgentExecutor with tool-calling"
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Career Assistant Agent with AgentExecutor...")
    print("📦 4 Tools Loaded:")
    print("   1. job_search_advisor")
    print("   2. skill_gap_analyzer")
    print("   3. project_idea_generator")
    print("   4. github_profile_analyzer (GitHub API)")
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)
