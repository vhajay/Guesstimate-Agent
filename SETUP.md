# Setup Instructions

## Prerequisites
- Python 3.11+
- UV package manager
- OpenAI API key
- Tavily API key

## Installation

1. **Clone the repository**
2. **Set up environment variables:**
   ```bash
   cd agents
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Install dependencies:**
   ```bash
   # MCP Server
   cd GuesstimateMCP
   uv sync
   
   # LangGraph Agent
   cd ../agents
   uv sync
   ```

## Running the System

### 1. Start HTTP Server:
```bash
cd GuesstimateMCP
uv run python src/guesstimatemcp/http_server.py
```

### 2. Run Interactive Agent:
```bash
cd agents
uv run python -m guesstimate_agent.main
```

## API Testing
Test endpoints with Postman:
- GET `http://localhost:8000/`
- POST `http://localhost:8000/tools/calculator`
- POST `http://localhost:8000/tools/web-search`

## Environment Variables Required
- `OPENAI_API_KEY`: Your OpenAI API key
- `TAVILY_API_KEY`: Your Tavily search API key