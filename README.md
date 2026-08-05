# 🤖 Career Assistant Agent

**LangChain agent with 4 tools deployed via LangServe** using **Gemma 4 31B**

> Single intelligent agent that analyzes resumes, finds jobs, suggests projects, and reviews GitHub portfolios

---

## �� Interactive Playground

Once deployed or running locally, visit:
```
http://localhost:8000/agent/playground
```

**Try the agent interactively** in your browser with LangServe's playground UI!

---

## 🏗️ Architecture

```
Input: Resume PDF + Target Role + GitHub ID
                    ↓
         ┌──────────────────────┐
         │  LangChain Agent     │
         │  (Gemma 4 31B)       │
         │  + LangServe         │
         └──────────┬───────────┘
                    │
      ┌─────────────┼─────────────┬──────────────┐
      │             │             │              │
   Tool 1       Tool 2        Tool 3         Tool 4
 Job Search   Skill Gap    Project Ideas  GitHub Check
      │             │             │              │
      └─────────────┴─────────────┴──────────────┘
                    │
            📄 Final Report
```

---

## ✨ Features

✅ **LangServe playground** - Interactive web UI at `/agent/playground`  
✅ **LangChain agent** (NO LangGraph - simpler!)  
✅ **4 specialized tools** for comprehensive career analysis  
✅ **Gemma 4 31B model** for intelligent reasoning  
✅ **Streaming responses** via `/agent/stream`  
✅ **Resume PDF parsing**  
✅ **Real-time job search**  
✅ **AI-powered skill gap analysis**  
✅ **Portfolio project recommendations**  
✅ **GitHub repository analysis**  
✅ **FastAPI + LangServe**  
✅ **One-click Render deployment**  

---

## �� Quick Start

### Prerequisites

- Python 3.11 or 3.12
- Google API Key ([Get it here](https://makersuite.google.com/app/apikey))

### Installation

```bash
# Clone repository
git clone https://github.com/Sathvik1533/career-assistant-agent.git
cd career-assistant-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Run Locally

```bash
# Start the server
uvicorn app:app --reload

# Visit the playground
open http://localhost:8000/agent/playground
```

---

## 🎮 Available Endpoints

### LangServe Endpoints (Playground!)

| Endpoint | Type | Description |
|----------|------|-------------|
| `/agent/playground` | GET | **Interactive UI** - Test agent in browser 🎮 |
| `/agent/invoke` | POST | Invoke agent (single response) |
| `/agent/stream` | POST | Streaming responses |

### REST API Endpoints

| Endpoint | Type | Description |
|----------|------|-------------|
| `/` | GET | Home/info |
| `/health` | GET | Health check |
| `/analyze` | POST | Upload resume PDF + analyze |
| `/docs` | GET | OpenAPI documentation |

---

## 🛠️ The Four Tools

1. **Job Search Tool** - Finds relevant job openings
2. **Skill Gap Analysis Tool** - Compares resume vs role requirements
3. **Project Idea Generator Tool** - Suggests portfolio projects
4. **GitHub Checker Tool** - Analyzes GitHub profile and repos

---

## 🌐 Deploy to Render

1. Push to GitHub ✅ (already done!)
2. Go to [render.com](https://render.com)
3. New Web Service → Connect repository: `career-assistant-agent`
4. Add environment variable: `GOOGLE_API_KEY`
5. Deploy!

**After deployment, visit:**
```
https://your-app.onrender.com/agent/playground
```

---

## 🧪 Test the Agent

### Via Playground (Recommended)
1. Start server: `uvicorn app:app --reload`
2. Visit: http://localhost:8000/agent/playground
3. Enter your query: "Analyze career for Software Engineer with GitHub: yourusername"
4. Watch the agent use all 4 tools!

### Via CLI
```bash
python test_local.py \
  --resume sample_data/resume.pdf \
  --role "Software Engineer" \
  --github "yourusername"
```

### Via REST API
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "resume=@resume.pdf" \
  -F "target_role=Software Engineer" \
  -F "github_username=yourusername"
```

---

## 📚 Documentation

- **SETUP_GUIDE.md** - Detailed setup instructions
- **Code comments** - Well-documented code
- **OpenAPI docs** - http://localhost:8000/docs

---

## 🔧 Technology Stack

- **LangChain** - Agent orchestration (NO LangGraph)
- **LangServe** - Web deployment with playground UI
- **Gemma 4 31B** - LLM for reasoning
- **FastAPI** - Web framework
- **pdfplumber** - PDF parsing
- **GitHub API** - Repository analysis

---

## 📝 License

MIT License - Free to use!

---

**Repository**: https://github.com/Sathvik1533/career-assistant-agent

**Try the playground**: http://localhost:8000/agent/playground 🎮

**Built with ❤️ using LangChain, LangServe, and Gemma 4 31B**
