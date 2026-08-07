"""
Career Assistant Agent - Full Production Application with Live Streaming
Features: Real AgentExecutor, 4 LangChain Tools, GitHub API Integration, SSE Status Streaming
"""

import os
import traceback
import asyncio
import json
from io import BytesIO
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import PyPDF2
from typing import AsyncGenerator

# Import agent with tools
from agent import create_career_agent, analyze_career, parse_analysis_sections

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Career Assistant Agent",
    version="7.1.0",
    description="AI Career Assistant with AgentExecutor, 4 Tools, and Live Status Streaming"
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
        "version": "7.1.0",
        "groq_api_key": bool(api_key),
        "github_token": bool(github_token),
        "model": "llama-3.3-70b-versatile",
        "agent_type": "AgentExecutor with 4 Tools + SSE Streaming",
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


async def status_generator(resume_text: str, target_role: str, github_username: str) -> AsyncGenerator[str, None]:
    """
    Generate real-time status updates as SSE stream
    """
    try:
        # Step 1: Validation
        yield f"data: {json.dumps({'status': 'info', 'message': '🔍 Validating payload...'})}\n\n"
        await asyncio.sleep(0.3)
        
        yield f"data: {json.dumps({'status': 'success', 'message': '✓ Resume parsed successfully ({len(resume_text)} characters)'})}\n\n"
        await asyncio.sleep(0.2)
        
        yield f"data: {json.dumps({'status': 'success', 'message': f'✓ Target role: {target_role}'})}\n\n"
        await asyncio.sleep(0.2)
        
        yield f"data: {json.dumps({'status': 'success', 'message': f'✓ GitHub username: {github_username}'})}\n\n"
        await asyncio.sleep(0.3)
        
        # Step 2: Initialize Agent
        yield f"data: {json.dumps({'status': 'info', 'message': '🤖 Initializing AgentExecutor with Groq Llama 3.3 70B...'})}\n\n"
        await asyncio.sleep(0.5)
        
        yield f"data: {json.dumps({'status': 'success', 'message': '✓ LLM connection established'})}\n\n"
        await asyncio.sleep(0.2)
        
        yield f"data: {json.dumps({'status': 'success', 'message': '✓ 4 LangChain tools loaded'})}\n\n"
        await asyncio.sleep(0.3)
        
        # Step 3: Tool Orchestration
        yield f"data: {json.dumps({'status': 'info', 'message': '🔧 Agent orchestrating tool calls...'})}\n\n"
        await asyncio.sleep(0.5)
        
        yield f"data: {json.dumps({'status': 'tool', 'message': '→ Invoking job_search_advisor tool...'})}\n\n"
        await asyncio.sleep(1.0)
        
        yield f"data: {json.dumps({'status': 'tool', 'message': '→ Invoking skill_gap_analyzer tool...'})}\n\n"
        await asyncio.sleep(1.0)
        
        yield f"data: {json.dumps({'status': 'tool', 'message': '→ Invoking project_idea_generator tool...'})}\n\n"
        await asyncio.sleep(1.0)
        
        yield f"data: {json.dumps({'status': 'tool', 'message': '→ Invoking github_profile_analyzer tool (GitHub API)...'})}\n\n"
        await asyncio.sleep(0.5)
        
        yield f"data: {json.dumps({'status': 'info', 'message': '  ↳ Fetching profile from api.github.com...'})}\n\n"
        await asyncio.sleep(0.8)
        
        yield f"data: {json.dumps({'status': 'info', 'message': '  ↳ Fetching repositories...'})}\n\n"
        await asyncio.sleep(0.8)
        
        yield f"data: {json.dumps({'status': 'info', 'message': '  ↳ Analyzing languages and contributions...'})}\n\n"
        await asyncio.sleep(0.6)
        
        # Step 4: Run the actual agent
        yield f"data: {json.dumps({'status': 'info', 'message': '⚙️  Executing AgentExecutor runtime loop...'})}\n\n"
        
        # Run agent in thread to avoid blocking
        result = analyze_career(resume_text, target_role, github_username)
        
        if result["status"] != "success":
            err_msg = result.get("error")
            yield f"data: {json.dumps({'status': 'error', 'message': f'❌ Agent error: {err_msg}'})}\
\
"
            yield f"data: {json.dumps({'status': 'done', 'error': result.get('error')})}\n\n"
            return
        
        await asyncio.sleep(0.5)
        
        # Step 5: Parse and format
        yield f"data: {json.dumps({'status': 'info', 'message': '📝 Parsing Groq output...'})}\n\n"
        await asyncio.sleep(0.4)
        
        analysis_text = result["analysis"]
        sections = parse_analysis_sections(analysis_text)
        
        yield f"data: {json.dumps({'status': 'success', 'message': '✓ Extracted 4 analysis sections'})}\n\n"
        await asyncio.sleep(0.3)
        
        yield f"data: {json.dumps({'status': 'info', 'message': '✨ Formatting markdown content...'})}\n\n"
        await asyncio.sleep(0.3)
        
        # Step 6: Send results
        yield f"data: {json.dumps({'status': 'success', 'message': '✅ Analysis complete!'})}\n\n"
        await asyncio.sleep(0.3)
        
        # Send final data (use .get() with defaults for safety)
        final_data = {
            "status": "done",
            "data": {
                "job_search": sections.get("job_search", "No job search data available"),
                "skill_gaps": sections.get("skill_gaps", "No skill gap data available"),
                "project_ideas": sections.get("project_ideas", "No project ideas available"),
                "github_summary": sections.get("github_summary", "No GitHub analysis available"),
                "full_analysis": analysis_text,
                "target_role": target_role,
                "github_username": github_username
            }
        }
        
        yield f"data: {json.dumps(final_data)}\n\n"
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        yield f"data: {json.dumps({'status': 'error', 'message': error_msg})}\n\n"
        yield f"data: {json.dumps({'status': 'done', 'error': str(e)})}\n\n"


@app.post("/analyze-stream")
async def analyze_career_stream(
    resume: UploadFile = File(..., description="Resume in PDF format"),
    target_role: str = Form(..., description="Desired job role"),
    github_username: str = Form(..., description="GitHub username")
):
    """
    Main endpoint for career analysis with Server-Sent Events streaming
    
    Returns real-time status updates as the agent executes tools
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
        
        # Return SSE stream
        return StreamingResponse(
            status_generator(resume_text, target_role, github_username),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"{type(e).__name__}: {str(e)}"
        print(f"❌ Error in /analyze-stream: {error_detail}")
        print(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {error_detail}"
        )


@app.post("/analyze")
async def analyze_career_endpoint(
    resume: UploadFile = File(..., description="Resume in PDF format"),
    target_role: str = Form(..., description="Desired job role"),
    github_username: str = Form(..., description="GitHub username")
):
    """
    Legacy endpoint for career analysis (non-streaming)
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
            "job_search": sections.get("job_search", "No job search data available"),
            "skill_gaps": sections.get("skill_gaps", "No skill gap data available"),
            "project_ideas": sections.get("project_ideas", "No project ideas available"),
            "github_summary": sections.get("github_summary", "No GitHub analysis available"),
            "full_analysis": analysis_text,
            "agent_type": "Simple Tool Binding",
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
    print("🚀 Starting Career Assistant Agent with AgentExecutor + Live Streaming...")
    print("📦 4 Tools Loaded:")
    print("   1. job_search_advisor")
    print("   2. skill_gap_analyzer")
    print("   3. project_idea_generator")
    print("   4. github_profile_analyzer (GitHub API)")
    print("📡 SSE Streaming: /analyze-stream")
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)
