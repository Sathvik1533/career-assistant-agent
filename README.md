# 🤖 Career Assistant Agent

> **AI-powered career guidance using Groq's lightning-fast Llama 3.3 70B**

[![Live Demo](https://img.shields.io/badge/Live-Demo-success?style=for-the-badge)](https://career-assistant-agent-bet6.onrender.com/docs
[![Powered by Groq](https://img.shields.io/badge/Powered%20by-Groq-FF6B00?style=for-the-badge)](https://groq.com)

## ✨ What It Does

🔍 **Job Search** - Personalized strategies  
📊 **Skill Gaps** - Know what to learn  
💡 **Projects** - Build your portfolio  
🐙 **GitHub** - Optimize your profile  

## 🚀 Try It Now

**Live Playground**: https://career-assistant-agent-bet6.onrender.com/agent/playground

## 📍 Endpoints

| URL | What It Does |
|-----|--------------|
| `/agent/playground` | 🎮 Interactive UI |
| `/docs` | 📚 API Documentation |
| `/analyze` | 🔍 Career Analysis API |

## 💻 Quick Example

```bash
curl -X POST https://career-assistant-agent-bet6.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "Python, React, 2 years", "target_role": "Engineer", "github_username": "you"}'
```

## 🛠️ Stack

- Groq Llama 3.3 70B
- LangChain + FastAPI
- LangServe Playground
- Deployed on Render

## 🏃 Run Locally

```bash
git clone https://github.com/Sathvik1533/career-assistant-agent.git
cd career-assistant-agent
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key" > .env
python app.py
```

Get API key: https://console.groq.com/keys

## ⚡ Why Groq?

- 🚀 10x faster than GPUs
- �� Free tier available
- 🔧 Simple to use
- 🧠 Powerful AI models

## 👨‍💻 Author

Sathvik - [@Sathvik1533](https://github.com/Sathvik1533)

**Built with ❤️ using LangChain & Groq**

