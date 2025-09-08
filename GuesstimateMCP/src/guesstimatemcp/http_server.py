"""HTTP server for GuesstimateMCP tools"""

import asyncio
import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Tool request/response models
class CalculatorRequest(BaseModel):
    expression: str

class WebSearchRequest(BaseModel):
    query: str

class ToolResponse(BaseModel):
    result: str
    success: bool = True
    error: str = None

app = FastAPI(title="GuesstimateMCP HTTP Server", version="1.0.0")

def calculate(expression: str) -> float:
    """Safely evaluate arithmetic expressions"""
    import math
    allowed_chars = set('0123456789+-*/.()% sqrt')
    if not all(c in allowed_chars for c in expression):
        raise ValueError("Invalid characters in expression")
    
    # Replace sqrt with math.sqrt
    expression = expression.replace('sqrt', 'math.sqrt')
    
    # Create safe namespace
    safe_dict = {"__builtins__": {}, "math": math}
    return eval(expression, safe_dict)

async def tavily_search(query: str) -> str:
    """Search the web using Tavily API"""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY environment variable not set"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "basic",
                    "include_answer": True,
                    "max_results": 5
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            if "answer" in data and data["answer"]:
                return f"Answer: {data['answer']}\n\nSources: {', '.join([r['url'] for r in data.get('results', [])])}"
            else:
                results = data.get("results", [])
                if results:
                    return "\n\n".join([f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content'][:200]}..." for r in results[:3]])
                else:
                    return "No results found"
        except Exception as e:
            return f"Search error: {str(e)}"

@app.get("/")
async def root():
    return {"message": "GuesstimateMCP HTTP Server", "tools": ["calculator", "web-search"]}

@app.post("/tools/calculator", response_model=ToolResponse)
async def calculator_tool(request: CalculatorRequest):
    try:
        result = calculate(request.expression)
        return ToolResponse(result=f"{request.expression} = {result}")
    except Exception as e:
        return ToolResponse(result="", success=False, error=str(e))

@app.post("/tools/web-search", response_model=ToolResponse)
async def web_search_tool(request: WebSearchRequest):
    try:
        result = await tavily_search(request.query)
        return ToolResponse(result=result)
    except Exception as e:
        return ToolResponse(result="", success=False, error=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def main():
    """Run the HTTP server"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()