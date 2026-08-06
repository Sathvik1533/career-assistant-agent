"""
FastAPI Career Assistant with Groq + Custom Frontend
"""

import os
import traceback
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
from io import BytesIO

load_dotenv()

app = FastAPI(
    title="Career Assistant Agent",
    version="5.0.0",
    description="Career Assistant using Groq with Custom Frontend"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
# STATIC FILES - Custom Frontend
# =============================================================================

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# =============================================================================
# REST API ENDPOINTS
# =============================================================================

@app.get("/")
def home():
    """Serve the custom frontend"""
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    api_key = os.getenv("GROQ_API_KEY")
    return {
        "status": "healthy",
        "api_key_set": bool(api_key),
        "model": "llama-3.3-70b-versatile"
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
        raise HTTPException(status_code=400, detail=f"Failed to extract PDF text: {str(e)}")


@app.post("/analyze")
async def analyze_career(
    resume: UploadFile = File(...),
    target_role: str = Form(...),
    github_username: str = Form(...)
):
    """
    REST API endpoint for career analysis with file upload
    Accepts multipart/form-data with PDF resume
    """
    try:
        # Validate file type
        if not resume.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read and extract text from PDF
        pdf_bytes = await resume.read()
        resume_text = extract_text_from_pdf(pdf_bytes)
        
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Create agent and analyze
        agent = create_agent()
        
        query = f"""
Analyze this career profile and provide:
1. Job Search Strategy
2. Skill Gap Analysis  
3. Project Ideas
4. GitHub Profile Review

Target Role: {target_role}
GitHub Username: {github_username}
Resume Summary: {resume_text[:1000]}

Provide detailed, actionable advice for each section.
"""
        
        result = agent.invoke({"query": query})
        
        # Parse the result into sections (basic parsing)
        sections = {
            "job_search": "",
            "skill_gaps": "",
            "project_ideas": "",
            "github_summary": ""
        }
        
        # Try to split by numbered sections or return full result
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
        
        # If parsing failed, put everything in job_search
        if not sections["job_search"]:
            sections["job_search"] = result
            sections["skill_gaps"] = "See job search section above"
            sections["project_ideas"] = "See job search section above"
            sections["github_summary"] = "See job search section above"
        
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
        print(f"❌ Error: {error_detail}")
        print(traceback.format_exc())
        
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {error_detail}"
        )


@app.post("/analyze-json")
async def analyze_json(request: CareerRequest):
    """REST API endpoint for career analysis with JSON input (legacy)"""
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
