# Multi-Agent Bot Framework

A modular AI-powered assistant framework featuring multiple specialized agents for market research, sales analysis, and web search capabilities.

## Features

- **Multi-Agent System**: Multiple specialized agents working together
  - Market Study Agent (Experto Estudios)
  - Sales Agent (Analista Ventas)
  - Web Search Agent (Agente Web)
  - Research Team coordination
  - Response Synthesizer

- **FastAPI Backend**: RESTful API with automatic documentation
- **Vector Search**: Integration with vector databases for document retrieval
- **Web Search**: Integration with Tavily for real-time web search
- **Session Management**: User session tracking and context management
- **MLflow Integration**: Experiment tracking and cleanup utilities

## Architecture

The project follows a modular architecture with:
- `agents/`: Individual agent implementations
- `api/`: FastAPI application and engines
- `core/`: Base classes and abstractions
- `nodes/`: LangGraph node implementations
- `tools/`: External tool integrations
- `utils/`: Utility functions and helpers

## Requirements

- **Python 3.11+** (required for modern type annotation syntax like `Literal[*options]`)
- **direnv** (recommended for environment management)
- **pyenv** (recommended for Python version management)

## Installation

### 1. Set up Python Environment

**Option A: Using pyenv (recommended)**
```bash
# Install Python 3.11+ if not available
pyenv install 3.12.3  # or any Python 3.11+
pyenv local 3.12.3

# Verify version
python --version  # Should show 3.11+
```

**Option B: System Python**
```bash
# Ensure you have Python 3.11+
python --version  # Should show 3.11+
```

### 2. Install the Package

```bash
# Clone the repository
git clone https://github.com/jpalvarezb/multi-agent-bot.git
cd multi-agent-bot

# Install as editable package (enables clean imports)
pip install -e .
```

### 3. Configure Environment

**Option A: Using direnv (recommended)**
```bash
# Copy environment file
cp .env.example .env

# Edit .env with your API keys and configuration
# The .envrc file is already configured
direnv allow
```

**Option B: Manual environment setup**
```bash
# Copy and edit environment file
cp .env.example .env
# Edit .env with your API keys

# Load environment variables manually or use python-dotenv
export $(cat .env | xargs)
```

### 4. Run the Application

```bash
# Start the API server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Or run individual bots
python main/sales_bot.py "Show me sales data for 2024"
python main/market_study_bot.py "Analyze market trends"
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Usage

Send POST requests to `/api/query` with your questions about market research, competitors, and business intelligence.

## Configuration

The system uses environment variables for configuration. See `.env.example` for required variables.
