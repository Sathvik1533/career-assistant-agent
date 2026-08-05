# 🤖 Career Assistant Agent

**LangChain agent with 4 tools** for career assistance using **Gemma 4 31B**

> Single intelligent agent that analyzes resumes, finds jobs, suggests projects, and reviews GitHub portfolios

---

## 🏗️ Architecture

```
Input: Resume PDF + Target Role + GitHub ID
                    ↓
         ┌──────────────────────┐
         │  LangChain Agent     │
         │  (Gemma 4 31B)       │
         │  AgentExecutor       │
         └──────────┬───────────┘
                    │
      ┌─────────────┼─────────────┬──────────────┐
      │             │             │              │
   Tool 1       Tool 2        Tool 3         Tool 4
 Job Search   Skill Gap    Project Ideas  GitHub Check
      │             │             │              │
      └─────────────┴─────────────┴──────────────┘
                    │
              Validation Step
                    │
              Synthesis Step
                    │
            📄 Final Report
```

---

## ✨ Features

✅ **Single LangChain agent** (not LangGraph - simpler!)  
✅ **4 specialized tools** for comprehensive career analysis  
✅ **Gemma 4 31B model** for intelligent reasoning  
✅ **Resume PDF parsing**  
✅ **Real-time job search**  
✅ **AI-powered skill gap analysis**  
✅ **Portfolio project recommendations**  
✅ **GitHub repository analysis**  
✅ **FastAPI web interface**  
✅ **One-click Render deployment**  
✅ **Local CLI testing**  

---

## 🚀 Quick Start

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

### Usage

**Local CLI:**
```bash
python test_local.py \
  --resume sample_data/resume.pdf \
  --role "Software Engineer" \
  --github "yourusername"
```

**Web API:**
```bash
uvicorn app:app --reload
# Visit: http://localhost:8000/docs
```

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
3. New Web Service → Connect repository
4. Add environment variable: `GOOGLE_API_KEY`
5. Deploy!

---

## 📚 Documentation

- **SETUP_GUIDE.md** - Detailed setup instructions
- **Code comments** - Well-documented code

---

## �� Technology Stack

- **LangChain** - Agent orchestration (NO LangGraph)
- **Gemma 4 31B** - LLM for reasoning
- **FastAPI** - Web framework
- **pdfplumber** - PDF parsing
- **GitHub API** - Repository analysis

---

## 📝 License

MIT License - Free to use!

---

**Repository**: https://github.com/Sathvik1533/career-assistant-agent

**Built with ❤️ using LangChain and Gemma 4 31B**
