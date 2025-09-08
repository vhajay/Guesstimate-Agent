# Guesstimate Agent

A Model Context Protocol (MCP) server for estimation and analysis tools.

## Installation

```bash
cd GuesstimateMCP
uv sync
```

## Usage

### Development
```bash
cd GuesstimateMCP
uv run guesstimatemcp
```

### With MCP Inspector (for debugging)
```bash
npx @modelcontextprotocol/inspector uv --directory GuesstimateMCP run guesstimatemcp
```

## Project Structure

```
├── README.md
├── requirements.txt
├── test_agent.py
├── GuesstimateMCP/                    # MCP Server
│   ├── src/guesstimatemcp/
│   │   ├── __init__.py
│   │   └── server.py
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── .python-version
│   ├── .gitignore
│   └── README.md
└── agents/                           # LangGraph Agents
    ├── src/guesstimate_agent/
    │   ├── __init__.py
    │   ├── agent.py
    │   └── main.py
    ├── pyproject.toml
    └── .env.example
```

## Features

### MCP Server
- **Calculator Tool**: Arithmetic operations including square root and modulo
- **Web Search Tool**: Real-time information via Tavily API
- **Note Management**: Add and manage estimation notes
- **Claude Desktop Integration**: Ready for Claude Desktop configuration

### LangGraph Agent
- **Problem Analysis**: Breaks down guesstimate problems into components
- **Research**: Uses web search for relevant data
- **Calculation**: Performs mathematical estimations
- **Validation**: Checks results for reasonableness
- **End-to-End Solving**: Complete guesstimate problem solver

## Usage

### Run LangGraph Agent
```bash
cd agents
uv sync
uv run python -m guesstimate_agent.main
```

### Test Agent
```bash
python test_agent.py
```