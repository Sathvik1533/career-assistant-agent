# 🤖 Career Assistant Agent

<div align="center">

**AI-powered career guidance using Groq's lightning-fast Llama 3.3 70B**

[![Live Demo](https://img.shields.io/badge/🚀_LIVE_DEMO-4CAF50?style=for-the-badge)](https://career-assistant-agent-bet6.onrender.com/docs)
[![Powered By](https://img.shields.io/badge/POWERED_BY-GROQ-FF6F00?style=for-the-badge&logo=ai)](https://groq.com/)
[![LangChain](https://img.shields.io/badge/LangChain-🦜-1C3C3C?style=for-the-badge)](https://www.langchain.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

</div>

---

## 🎯 What It Does

🔍 **Job Search** - Personalized strategies for your target role  
📊 **Skill Gaps** - Know what to learn next  
💡 **Projects** - Build your portfolio with tailored ideas  
🐙 **GitHub** - Optimize your developer profile  

---

## ✨ Key Features

- **Single Agent Architecture** - Clean, maintainable LangChain implementation
- **4 Specialized Tools** - Job search, skill analysis, project ideas, GitHub review
- **Multi-Input Processing** - Upload resume (PDF), specify target role, provide GitHub username
- **JSON Output** - Structured, comprehensive career report
- **Production Ready** - Deployed on Render with FastAPI + Swagger UI
- **Fast Inference** - Powered by Groq's Llama 3.3 70B (temperature: 0.7)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Groq API key → [Get one here](https://console.groq.com/keys) (Free tier available!)

### Installation

```bash
# Clone the repository
git clone https://github.com/Sathvik1533/career-assistant-agent.git
cd career-assistant-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# Run the application
python app.py
```

### 🎮 Try It Now

**Live API**: https://career-assistant-agent-bet6.onrender.com

**Swagger UI**: https://career-assistant-agent-bet6.onrender.com/docs

---

## 📡 API Usage

### Endpoint: `/analyze`

**Method**: `POST`  
**Content-Type**: `multipart/form-data`

**Parameters**:
- `resume` (file): PDF file of your resume
- `target_role` (string): Desired job role (e.g., "Software Engineer")
- `github_username` (string): Your GitHub username

### Example with cURL

```bash
curl -X POST "https://career-assistant-agent-bet6.onrender.com/analyze" \
  -H "accept: application/json" \
  -F "resume=@resume.pdf" \
  -F "target_role=Software Engineer" \
  -F "github_username=Sathvik1533"
```

### Example with Python

```python
import requests

url = "https://career-assistant-agent-bet6.onrender.com/analyze"

files = {'resume': open('resume.pdf', 'rb')}
data = {
    'target_role': 'Software Engineer',
    'github_username': 'Sathvik1533'
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

### Sample Response

```json
{
  "job_search": "Focus on applying to companies that value LangChain expertise...",
  "skill_gaps": "Consider learning Docker, Kubernetes, and system design...",
  "project_ideas": "Build a multi-agent RAG system with tool-calling capabilities...",
  "github_summary": "Your profile shows strong Python skills with 15 repositories..."
}
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│  User Input     │
│  - Resume PDF   │
│  - Target Role  │
│  - GitHub ID    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│   (Pydantic)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LangChain      │
│  AgentExecutor  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Groq LLM       │
│  Llama 3.3 70B  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│         4 Tools                 │
│  1. Job Search Advisor          │
│  2. Skill Gap Analyzer          │
│  3. Project Idea Generator      │
│  4. GitHub Profile Checker      │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────┐
│  JSON Response  │
│  (Structured)   │
└─────────────────┘
```

---

## 📂 Project Structure

```
career-assistant-agent/
├── app.py                  # FastAPI application & routes
├── agent.py                # LangChain agent setup
├── tools.py                # 4 tool implementations
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI |
| **Agent** | LangChain (NO LangGraph) |
| **LLM** | Groq - Llama 3.3 70B Versatile |
| **PDF Processing** | PyPDF2, pdfplumber |
| **API Integration** | GitHub REST API |
| **Deployment** | Render |
| **Temperature** | 0.7 (balanced creativity) |

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### Temperature Setting

The agent uses `temperature=0.7` for balanced responses:
- **Lower (0.0-0.3)**: More consistent, deterministic
- **Medium (0.4-0.7)**: Balanced creativity and accuracy ✅
- **Higher (0.8-1.0)**: More creative, varied responses

---

## 🚀 Deployment

### Deploy to Render

1. **Push to GitHub**
```bash
git add .
git commit -m "Deploy career assistant agent"
git push origin main
```

2. **Create Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click **New +** → **Web Service**
   - Connect your GitHub repository
   - Select `career-assistant-agent`

3. **Configure Environment**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `GROQ_API_KEY`: Your Groq API key

4. **Deploy!** 🎉

---

## 📊 How It Works

### 1. **Resume Processing**
- Extracts text from uploaded PDF
- Parses skills, experience, and education
- Prepares context for agent

### 2. **Agent Reasoning**
- LangChain AgentExecutor orchestrates tool calls
- Llama 3.3 70B decides which tools to use
- Tools execute in sequence or parallel

### 3. **Tool Execution**

#### 🔍 Job Search Tool
- Analyzes target role requirements
- Provides personalized job search strategies
- Suggests companies and platforms

#### 📊 Skill Gap Tool
- Compares resume skills with role requirements
- Identifies learning priorities
- Recommends resources

#### 💡 Project Idea Tool
- Generates portfolio project ideas
- Aligned with target role
- Practical and impressive

#### 🐙 GitHub Tool
- Fetches profile via GitHub API
- Reviews repositories and contributions
- Suggests improvements

### 4. **Response Generation**
- Combines all tool outputs
- Formats as structured JSON
- Returns comprehensive career report

---

## 🎓 Learning Outcomes

Building this project taught me:

✅ **Agent Architecture** - Understanding how agents orchestrate tool calls  
✅ **LangChain Imports** - Correct modern import paths for `AgentExecutor`  
✅ **API Integration** - Working with GitHub REST API and authentication  
✅ **FastAPI + Pydantic** - Building production-ready REST APIs  
✅ **Debugging** - Fixing model compatibility issues (Gemini → Groq migration)  
✅ **JSON Parsing** - Using `StrOutputParser()` for structured outputs  
✅ **Deployment** - Deploying LangChain apps to Render with environment variables  

---

## 🐛 Troubleshooting

### Issue: API Key Errors

**Solution**: Ensure `GROQ_API_KEY` is set in environment
```bash
# Local
echo "GROQ_API_KEY=your_key" > .env

# Render
Add in Environment Variables section
```

### Issue: Import Errors

**Solution**: Use correct LangChain imports
```python
from langchain.agents import AgentExecutor
from langchain.agents.tool_calling_agent.base import create_tool_calling_agent
```

### Issue: GitHub API Rate Limits

**Solution**: Add GitHub personal access token to tool for higher limits

---

## 🔮 Future Enhancements

- [ ] Add custom frontend (HTML/CSS/JS) for better UX
- [ ] Implement streaming responses for real-time feedback
- [ ] Add caching for GitHub API calls
- [ ] Support multiple file formats (DOCX, TXT)
- [ ] Add LinkedIn profile analysis tool
- [ ] Implement conversation memory for follow-up questions
- [ ] Add unit tests and integration tests

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Groq** - For lightning-fast LLM inference
- **LangChain** - For the agent framework
- **FastAPI** - For the web framework
- **Render** - For easy deployment

---

<div align="center">

**Built with ❤️ using LangChain & Groq**

[🚀 Live Demo](https://career-assistant-agent-bet6.onrender.com/docs) • [📖 API Docs](https://career-assistant-agent-bet6.onrender.com/docs) • [🐛 Report Bug](https://github.com/Sathvik1533/career-assistant-agent/issues) • [✨ Request Feature](https://github.com/Sathvik1533/career-assistant-agent/issues)

---

### 📬 Contact

**Sathvik** - [@Sathvik1533](https://github.com/Sathvik1533)

**Project Link**: https://github.com/Sathvik1533/career-assistant-agent

</div>
