"""
Career Assistant Agent - FastAPI Application
Powered by Groq Llama 3.3 70B + LangChain

Features:
- Custom minimal frontend (HTML/CSS/JS)
- PDF resume upload and text extraction
- LangServe playground for testing
- RESTful API endpoints
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
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langserve import add_routes
import PyPDF2

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Career Assistant Agent",
    version="5.2.0",
    description="AI-powered career guidance using Groq Llama 3.3 70B"
)

# Enable CORS for cross-origin requests
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
    """JSON request model for legacy API"""
    resume_text: str
    target_role: str
    github_username: str


class PlaygroundInput(BaseModel):
    """Input schema for LangServe playground"""
    query: str = Field(
        description="Career analysis query with resume, role, and GitHub username"
    )


# ============================================================================
# LANGCHAIN AGENT
# ============================================================================

def create_agent():
    """
    Create Groq-powered LangChain agent for career analysis
    
    Returns:
        Runnable chain that takes query and returns analysis
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    # Initialize Groq LLM
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=api_key,
        temperature=0.7,  # Balanced creativity and consistency
    )
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert Career Assistant helping professionals advance their careers.

Provide comprehensive, actionable advice covering:
1. Job Search Strategy - Specific companies, platforms, and keywords
2. Skill Gap Analysis - Technical and soft skills to develop
3. Project Ideas - Portfolio projects that demonstrate relevant skills
4. GitHub Profile Review - Improvements to showcase work effectively

Be specific, realistic, and encouraging."""),
        ("human", "{query}")
    ])
    
    # Build the chain: prompt -> LLM -> string output
    chain = prompt | llm | StrOutputParser()
    
    # Add input schema for LangServe compatibility
    chain = chain.with_types(input_type=PlaygroundInput)
    
    return chain


# ============================================================================
# LANGSERVE PLAYGROUND (Optional Testing Interface)
# ============================================================================

try:
    career_chain = create_agent()
    
    add_routes(
        app,
        career_chain,
        path="/agent",
        enabled_endpoints=["invoke", "stream", "playground"],
    )
    print("✅ LangServe playground available at /agent/playground")
except Exception as e:
    print(f"⚠️  Warning: LangServe routes not added: {e}")


# ============================================================================
# STATIC FILES (Custom Frontend)
# ============================================================================

# Serve HTML/CSS/JS from static/ directory
app.mount("/static", StaticFiles(directory="static"), name="static")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def home():
    """Serve the custom minimal frontend"""
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    """Health check endpoint"""
    api_key = os.getenv("GROQ_API_KEY")
    return {
        "status": "healthy",
        "version": "5.2.0",
        "api_key_configured": bool(api_key),
        "model": "llama-3.3-70b-versatile",
        "provider": "Groq"
    }


def extract_text_from_pdf(pdf_file: bytes) -> str:
    """
    Extract text content from PDF file
    
    Args:
        pdf_file: PDF file as bytes
        
    Returns:
        Extracted text as string
        
    Raises:
        HTTPException: If PDF extraction fails
    """
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
async def analyze_career(
    resume: UploadFile = File(..., description="Resume in PDF format"),
    target_role: str = Form(..., description="Desired job role"),
    github_username: str = Form(..., description="GitHub username")
):
    """
    Main endpoint for career analysis
    
    Accepts:
        - resume: PDF file upload
        - target_role: Target job position
        - github_username: GitHub username for profile review
    
    Returns:
        JSON with 4 sections: job_search, skill_gaps, project_ideas, github_summary
    """
    try:
        # Validate file type
        if not resume.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF files are supported"
            )
        
        # Read and extract text from PDF
        pdf_bytes = await resume.read()
        resume_text = extract_text_from_pdf(pdf_bytes)
        
        if not resume_text:
            raise HTTPException(
                status_code=400, 
                detail="Could not extract text from PDF. Please check the file."
            )
        
        # Create agent and generate analysis
        agent = create_agent()
        
        # Construct detailed query
        query = f"""
Analyze this career profile:

**Target Role:** {target_role}
**GitHub Username:** {github_username}
**Resume Summary:** {resume_text[:1000]}...

Provide detailed advice in these 4 sections:
1. Job Search Strategy
2. Skill Gap Analysis
3. Project Ideas
4. GitHub Profile Review

Be specific and actionable.
"""
        
        # Get LLM response
        result = agent.invoke({"query": query})
        
        # Parse response into sections
        sections = parse_response_sections(result)
        
        return {
            "status": "success",
            "target_role": target_role,
            "github_username": github_username,
            "job_search": sections["job_search"],
            "skill_gaps": sections["skill_gaps"],
            "project_ideas": sections["project_ideas"],
            "github_summary": sections["github_summary"],
            "full_analysis": result
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


def parse_response_sections(result: str) -> dict:
    """
    Parse LLM response into 4 sections
    
    Looks for numbered sections (1., 2., 3., 4.) and splits accordingly.
    If parsing fails, returns full text in job_search section.
    """
    sections = {
        "job_search": "",
        "skill_gaps": "",
        "project_ideas": "",
        "github_summary": ""
    }
    
    # Try to split by numbered sections
    if "1." in result and "2." in result:
        parts = result.split("1.")
        if len(parts) > 1:
            rest = parts[1]
            sections_parts = rest.split("2.")
            if len(sections_parts) > 1:
                sections["job_search"] = "1." + sections_parts[0].strip()
                rest2 = sections_parts[1]
                sections_parts2 = rest2.split("3.")
                if len(sections_parts2) > 1:
                    sections["skill_gaps"] = "2." + sections_parts2[0].strip()
                    rest3 = sections_parts2[1]
                    sections_parts3 = rest3.split("4.")
                    if len(sections_parts3) > 1:
                        sections["project_ideas"] = "3." + sections_parts3[0].strip()
                        sections["github_summary"] = "4." + sections_parts3[1].strip()
    
    # Fallback: if parsing failed, put everything in job_search
    if not sections["job_search"]:
        sections["job_search"] = result
        sections["skill_gaps"] = "See full analysis above"
        sections["project_ideas"] = "See full analysis above"
        sections["github_summary"] = "See full analysis above"
    
    return sections


@app.post("/analyze-json")
async def analyze_json(request: CareerRequest):
    """
    Legacy JSON endpoint for career analysis
    
    Accepts JSON payload instead of file upload.
    Maintained for backward compatibility.
    """
    try:
        agent = create_agent()
        
        query = f"""
Analyze this career profile:

**Target Role:** {request.target_role}
**GitHub Username:** {request.github_username}
**Resume:** {request.resume_text[:500]}...

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
        print(f"❌ Error in /analyze-json: {error_detail}")
        print(traceback.format_exc())
        
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {error_detail}"
        )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
