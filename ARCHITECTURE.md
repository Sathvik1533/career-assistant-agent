# Architecture Overview

## System Design

```
User → Frontend (HTML/CSS/JS) → FastAPI Backend → AgentExecutor → 4 LangChain Tools → Groq LLM + GitHub API
```

## Components

### 1. Agent System (`agent.py`)
- **AgentExecutor** with tool-calling runtime loop
- **4 LangChain Tools** orchestrated dynamically
- **Groq Llama 3.3 70B** (temperature: 0.7)
- **MessagesPlaceholder** for agent scratchpad

### 2. Tools (`tools.py`)
- `job_search_advisor` - Job search strategies
- `skill_gap_analyzer` - Skill gap analysis  
- `project_idea_generator` - Portfolio project ideas
- `github_profile_analyzer` - GitHub profile analysis (REST API)

### 3. API Server (`app.py`)
- **FastAPI** with 7 endpoints
- PDF upload and text extraction
- Agent integration
- Static file serving

### 4. Frontend (`static/`)
- Minimal HTML/CSS/JS interface
- Resume upload, role and GitHub username inputs
- 4-section results display

## Data Flow

1. User submits resume PDF + target role + GitHub username
2. FastAPI extracts PDF text
3. AgentExecutor dynamically orchestrates tool calls
4. Each tool uses Groq LLM or GitHub API
5. Agent synthesizes results into report
6. Frontend displays 4 sections

## Tech Stack

- **LLM:** Groq Llama 3.3 70B
- **Framework:** LangChain (AgentExecutor)
- **Backend:** FastAPI
- **Frontend:** Vanilla HTML/CSS/JS
- **Deployment:** Render
- **APIs:** GitHub REST API

## Environment Variables

- `GROQ_API_KEY` (required) - Groq LLM access
- `GITHUB_TOKEN` (optional) - Higher GitHub API rate limits (5,000/hour vs 60/hour)
