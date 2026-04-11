# Alpha-Logic

Alpha-Logic is a Flask-based resume analysis web app that compares a candidate resume against a job description. It uses CrewAI agents to parse, normalize, match, and question the resume vs. JD content, then returns a score, matched skills, insights, and follow-up questions.

## Features

- Upload resume as PDF, DOCX, or plain text
- Submit job description text
- Extracts resume text robustly from PDF/DOCX files
- Performs AI-powered matching and scoring using crew agents
- Returns structured JSON results for frontend display

## Structure

- `app.py` - Flask web server and file/route handling
- `orchestrator.py` - CrewAI orchestration for resume/JD analysis
- `agents/` - custom agent modules for parser, normalizer, matcher, and inquisitor logic
- `templates/index.html` - frontend user interface

## Requirements

- Python 3.10+ (recommended)
- `flask`
- `flask-cors`
- `pdfplumber`
- `python-docx`
- `crewai`

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate it:

```bash
# Windows PowerShell
venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install flask flask-cors pdfplumber python-docx crewai
```

4. Set your Groq API key:

```bash
# Windows PowerShell
$env:GROQ_API_KEY="your_groq_api_key"
```

5. Run the app:

```bash
python app.py
```

## Push to GitHub

If you have `git` installed, run these commands from the project root:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/zalamanthan101/Alpha-Logic.git
git push -u origin main
```

If you already have the repository initialized, just add the remote and push:

```bash
git remote add origin https://github.com/zalamanthan101/Alpha-Logic.git
git branch -M main
git push -u origin main
```

## Note

`GROQ_API_KEY` must be provided through your environment before starting the app.
