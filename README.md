# AI-Powered Recruitment Assistant

An end-to-end AI-powered recruitment assistant that automates the hiring process using agentic AI.

## Features

- **ResumeBot**: Collects and parses resumes through conversational interface
- **FilterAI**: Analyzes and ranks candidates based on job requirements
- **StoreKeeper**: Manages data storage and retrieval
- **HRBridge**: Provides HR interface for candidate review
- **TimeBot**: Handles interview scheduling
- **NotifyBot**: Manages candidate communications

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Add your GOOGLE_API_KEY
```

3. Run the application:
```bash
streamlit run app.py
```

## Architecture

The system uses LangGraph for agent orchestration and Gemini as the LLM. Each agent specializes in specific recruitment tasks while maintaining seamless integration.

## File Structure

```
├── app.py
├── requirements.txt
├── .env
├── README.md
└── src/
    ├── agents/
    │   ├── __init__.py
    │   ├── resume_bot.py
    │   ├── filter_ai.py
    │   ├── store_keeper.py
    │   ├── hr_bridge.py
    │   ├── time_bot.py
    │   └── notify_bot.py
    ├── agentic_prompts/
    │   ├── __init__.py
    │   └── prompts.py
    ├── tools/
    │   ├── __init__.py
    │   ├── resume_parser.py
    │   ├── file_handler.py
    │   └── scheduler.py
    ├── utils/
    │   ├── __init__.py
    │   ├── config.py
    │   └── helpers.py
    ├── models/
    │   ├── __init__.py
    │   └── llm_config.py
    └── schema/
        ├── __init__.py
        └── data_models.py
```