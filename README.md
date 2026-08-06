# Career Assistant Agent

> AI-powered career guidance using LangChain AgentExecutor and Groq Llama 3.3 70B

[![Live Demo](https://img.shields.io/badge/Live-Demo-green)](https://career-assistant-agent-bet6.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://www.python.org)
[![LangChain](https://img.shields.io/badge/LangChain-Agent-orange)](https://www.langchain.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## Overview

An intelligent career assistant that analyzes resumes, identifies skill gaps, suggests portfolio projects, and reviews GitHub profiles using LangChain's AgentExecutor with 4 specialized tools.

## Features

- **Job Search Strategies** - Personalized recommendations for target roles
- **Skill Gap Analysis** - Identify missing skills and learning paths
- **Project Idea Generation** - Tailored portfolio project suggestions
- **GitHub Profile Review** - Profile optimization with REST API integration
- **AgentExecutor Runtime** - Dynamic tool orchestration by Groq LLM
- **Custom Frontend** - Clean, minimal web interface

## Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Groq Llama 3.3 70B (temperature: 0.7) |
| Framework | LangChain AgentExecutor |
| Backend | FastAPI |
| Frontend | HTML/CSS/JavaScript |
| APIs | GitHub REST API |
| Deployment | Render |

## Quick Start

### Prerequisites

- Python 3.9+
- Groq API key ([Get free key](https://console.groq.com/keys))

### Installation

```bash
# Clone repository
git clone https://github.com/Sathvik1533/career-assistant-agent.git
cd career-assistant-agent

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export GROQ_API_KEY="your_groq_api_key"

# Optional: Add GitHub token for higher rate limits (60/hour → 5,000/hour)
export GITHUB_TOKEN="your_github_token"

# Run server
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000` to access the application.

## API Usage

### Analyze Career Profile

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "resume=@resume.pdf" \
  -F "target_role=Software Engineer" \
  -F "github_username=yourusername"
```

### Response Format

```json
{
  "status": "success",
  "job_search": "Personalized job search strategies...",
  "skill_gaps": "Skills to develop and resources...",
  "project_ideas": "2-3 portfolio project ideas...",
  "github_summary": "GitHub profile analysis and recommendations..."
}
```

## Architecture

```
User Input → FastAPI → AgentExecutor → 4 LangChain Tools → Groq LLM + GitHub API → Structured Output
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## Project Structure

```
career-assistant-agent/
├── app.py              # FastAPI server
├── agent.py            # AgentExecutor and tool orchestration
├── tools.py            # 4 LangChain tools (@tool decorator)
├── utils.py            # PDF parsing utilities
├── requirements.txt    # Python dependencies
├── static/             # Frontend files
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── ARCHITECTURE.md     # System design documentation
├── SETUP_GUIDE.md      # Detailed setup instructions
└── README.md           # This file
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key for LLM access |
| `GITHUB_TOKEN` | No | GitHub PAT for higher API rate limits |

## Deployment

### Deploy to Render

1. Push code to GitHub
2. Create Web Service on [Render](https://render.com)
3. Connect GitHub repository
4. Set environment variables:
   - `GROQ_API_KEY`: Your Groq API key
   - `GITHUB_TOKEN`: (Optional) GitHub Personal Access Token
5. Deploy

Build and start commands are configured in `render.yaml`.

## Development

### Run Tests

```bash
# CLI test with interactive input
python agent.py
```

### API Documentation

Visit `/docs` for interactive Swagger UI documentation.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [Groq](https://groq.com) - Lightning-fast LLM inference
- [LangChain](https://langchain.com) - Agent framework
- [FastAPI](https://fastapi.tiangolo.com) - Web framework

## Links

- **Live Demo**: https://career-assistant-agent-bet6.onrender.com
- **API Docs**: https://career-assistant-agent-bet6.onrender.com/docs
- **GitHub**: https://github.com/Sathvik1533/career-assistant-agent

---

**Built with LangChain AgentExecutor and Groq Llama 3.3 70B**
