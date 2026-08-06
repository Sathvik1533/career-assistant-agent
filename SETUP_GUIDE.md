# 🚀 Setup Guide - Career Assistant Agent

**Repository**: https://github.com/Sathvik1533/career-assistant-agent

This guide walks you through setting up and running the Career Assistant Agent locally, then deploying to Render.

---

## ✅ What You Just Created

A complete LangGraph agent project with:
- ✅ 11 files pushed to GitHub
- ✅ Single agent using Groq Llama 3.3 70B model
- ✅ 4 specialized tools (job search, skill gap, projects, GitHub)
- ✅ Validation and synthesis pipeline
- ✅ FastAPI web server
- ✅ Local testing script
- ✅ Render deployment config

---

## 📋 Phase 1: Local Setup

### Step 1: Clone the Repository

```bash
cd ~/Desktop  # or your preferred location
git clone https://github.com/Sathvik1533/career-assistant-agent.git
cd career-assistant-agent
```

### Step 2: Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate  # On Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- LangGraph & LangChain
- langchain-groq (for Groq model)
- FastAPI & Uvicorn
- PDF processing libraries
- All utilities

### Step 4: Set Up Environment Variables

```bash
# Copy the example
cp .env.example .env

# Edit .env file
nano .env  # or use VS Code: code .env
```

Add your API key:
```
GROQ_API_KEY=your_actual_groq_api_key_here
GITHUB_TOKEN=your_github_token_here  # optional
```

**Get Groq API Key**: https://makersuite.google.com/app/apikey

---

## 🧪 Phase 2: Local Testing

### Test 1: Check Tools Import

```bash
python -c "from tools import job_search_tool; print('✅ Tools working')"
```

### Test 2: Test Individual Tool

```bash
python -c "from tools import github_checker_tool; print(github_checker_tool.invoke('Sathvik1533'))"
```

### Test 3: Add Sample Resume

Add a PDF resume to `sample_data/`:
```bash
# Copy your resume
cp ~/path/to/your/resume.pdf sample_data/my_resume.pdf
```

### Test 4: Run Full Agent

```bash
python test_local.py \
  --resume sample_data/my_resume.pdf \
  --role "Software Engineer" \
  --github "Sathvik1533"
```

**Expected output**:
```
================================================================================
🚀 STARTING CAREER ANALYSIS
================================================================================

🤖 Agent: Planning analysis strategy...

🔧 Executing tools...
  1/4 Job Search...
  2/4 Skill Gap Analysis...
  3/4 Project Idea Generation...
  4/4 GitHub Analysis...

✅ Validating outputs...
  All tools executed successfully!

📄 Synthesizing final report...
  Report complete!

💾 Report saved to: report.json
```

### Test 5: Check Report

```bash
cat report.json | python -m json.tool | head -50
```

---

## 🌐 Phase 3: Web API Testing

### Start Local Server

```bash
uvicorn app:app --reload
```

Visit:
- **API Docs**: http://localhost:8000/docs
- **Home**: http://localhost:8000
- **Health**: http://localhost:8000/health

### Test API with cURL

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "resume=@sample_data/my_resume.pdf" \
  -F "target_role=Software Engineer" \
  -F "github_username=Sathvik1533"
```

---

## 🚀 Phase 4: Deploy to Render

### Step 1: Verify GitHub Push

Check: https://github.com/Sathvik1533/career-assistant-agent

You should see all 11 files.

### Step 2: Connect to Render

1. Go to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Select **"Build and deploy from a Git repository"**
4. Click **"Connect account"** if needed
5. Find and select: **career-assistant-agent**

### Step 3: Configure Service

Render will auto-detect `render.yaml` settings:
- **Name**: career-assistant-agent
- **Runtime**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app`

### Step 4: Add Environment Variables

In Render dashboard, add:

```
GROQ_API_KEY = your_actual_groq_api_key_here
GITHUB_TOKEN = your_github_token_here (optional)
```

### Step 5: Deploy!

Click **"Create Web Service"**

Render will:
1. Clone your repo
2. Install dependencies (~2-3 minutes)
3. Start the server
4. Give you a live URL

### Step 6: Test Live API

Once deployed, visit:
```
https://career-assistant-agent.onrender.com/docs
```

Test the `/analyze` endpoint with your resume!

---

## 📊 Understanding the Flow

```
1. Upload Resume PDF
        ↓
2. Agent Plans (LangGraph)
        ↓
3. Execute 4 Tools in Sequence:
   - Job Search (web/LLM)
   - Skill Gap Analysis (LLM compares resume vs role)
   - Project Ideas (LLM suggests projects)
   - GitHub Check (GitHub API + analysis)
        ↓
4. Validate All Outputs
        ↓
5. Synthesize Final Report
        ↓
6. Return JSON Response
```

---

## 🔧 Customization

### Change the Model

Edit `agent.py` and `tools.py`:

```python
# Current: Groq Llama 3.3 70B
model="models/groq-4-31b-it"

# Alternatives:
model="groq-2.0-flash-exp"  # Faster
model="groq-1.5-pro"         # Most capable
model="models/groq-2-27b-it"  # Smaller Groq
```

### Add More Tools

1. Edit `tools.py`:
```python
@tool
def my_new_tool(input: str) -> str:
    """Description"""
    # Your logic
    return result
```

2. Update `agent.py`:
```python
tools = [
    job_search_tool,
    skill_gap_analysis_tool,
    project_idea_generator_tool,
    github_checker_tool,
    my_new_tool  # Add here
]
```

3. Update execution in `execute_tools_node()`

### Change Job Search Method

By default, uses LLM to simulate search. For real search:

1. Get SERP API key: https://serpapi.com
2. Add to `.env`: `SERP_API_KEY=...`
3. Update `job_search_tool` in `tools.py`

---

## 🐛 Troubleshooting

### "GROQ_API_KEY not found"

Solution:
```bash
# Check .env file exists
ls -la .env

# Check content
cat .env

# Make sure it's loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GROQ_API_KEY'))"
```

### "PDF extraction failed"

Solutions:
- Ensure PDF is text-based (not scanned image)
- Try: `pip install --upgrade pdfplumber`
- Test with different PDF

### "Model not found: groq-4-31b-it"

Solutions:
- Verify API key has access to Groq models
- Try alternative: `groq-2.0-flash-exp`
- Check Groq Console for available models

### "Tool execution timeout"

Solutions:
- Check internet connection
- GitHub API: Add GITHUB_TOKEN for higher limits
- Increase timeout in code if needed

### "Render deployment fails"

Solutions:
- Check build logs in Render dashboard
- Verify `requirements.txt` is correct
- Ensure GROQ_API_KEY is set in Render
- Check Python version (should be 3.11+)

---

## 📚 File Guide

| File | Purpose |
|------|---------|
| `agent.py` | LangGraph agent definition |
| `tools.py` | 4 tool implementations |
| `utils.py` | PDF parsing, validation, synthesis |
| `app.py` | FastAPI web server |
| `test_local.py` | Local CLI testing |
| `requirements.txt` | Python dependencies |
| `render.yaml` | Render deployment config |
| `.env.example` | Environment variable template |
| `.gitignore` | Git ignore rules |

---

## ✅ Success Checklist

Local Setup:
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file configured with GROQ_API_KEY
- [ ] Sample resume added to `sample_data/`

Local Testing:
- [ ] Tools import successfully
- [ ] Individual tool test works
- [ ] Full agent run completes
- [ ] `report.json` generated
- [ ] FastAPI server starts
- [ ] API docs accessible

Deployment:
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Repository connected to Render
- [ ] Environment variables added
- [ ] Service deployed successfully
- [ ] Live API working

---

## 🎯 Next Steps

1. **Test with Your Resume**: Run locally with your actual resume
2. **Customize Tools**: Adjust prompts or add new tools
3. **Deploy to Production**: Push to Render
4. **Share with Friends**: Help others land jobs!

---

## 📞 Support

- **GitHub Issues**: https://github.com/Sathvik1533/career-assistant-agent/issues
- **Documentation**: This file + README.md
- **Model Info**: https://ai.google.dev/

---

**Built with ❤️ using LangGraph, LangChain, and Groq Llama 3.3 70B**

*Good luck with your job search!* 🚀
