# Career Assistant Agent 🚀

A LangChain-powered career assistant using **Groq AI** (Llama 3.3 70B).

## Features ✨
- Job Search Tips
- Skill Gap Analysis  
- Project Ideas
- GitHub Profile Review

## Live URL 🌐
https://career-assistant-agent-bet6.onrender.com

## Endpoints
- `/` - Home
- `/docs` - Swagger docs
- `/analyze` - REST API
- `/agent/playground` - LangServe UI

## Tech Stack
- LangChain + FastAPI
- Groq (Llama 3.3 70B)
- Deployed on Render

## Setup
```bash
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key" > .env
python app.py
```

Get Groq API key: https://console.groq.com/keys
