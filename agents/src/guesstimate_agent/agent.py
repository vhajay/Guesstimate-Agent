"""LangGraph agent for solving guesstimate problems"""

import os
import asyncio
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json
from datetime import datetime
import httpx

class GuesstimateSolver:
    def __init__(self, openai_api_key: str = None, server_url: str = "http://localhost:8000"):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.server_url = server_url
        self.llm = ChatOpenAI(api_key=self.openai_api_key, model="gpt-3.5-turbo")
        self.graph = self._build_graph()
    
    def _log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def _log_node(self, node_name: str, status: str = "STARTED"):
        """Log node activation"""
        self._log(f"[NODE] LangGraph Node '{node_name}' {status}", "NODE")
    
    def _log_llm(self, action: str):
        """Log LLM calls"""
        self._log(f"[LLM] {action}", "LLM")
    
    def _log_mcp(self, tool_name: str, action: str):
        """Log MCP tool usage"""
        self._log(f"[MCP] {tool_name}: {action}", "MCP")
    
    async def _call_http_tool(self, endpoint: str, data: dict) -> str:
        """Call HTTP tool endpoint"""
        self._log(f"[HTTP] Calling endpoint: {endpoint}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.server_url}/tools/{endpoint}",
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("success", True):
                    self._log(f"[HTTP] Tool {endpoint} SUCCESS")
                    return result.get("result", "")
                else:
                    self._log(f"[HTTP] Tool {endpoint} FAILED - {result.get('error', 'Unknown error')}")
                    return f"Error: {result.get('error', 'Unknown error')}"
                    
        except Exception as e:
            self._log(f"[HTTP] Tool {endpoint} FAILED - {str(e)}")
            return f"Error calling {endpoint}: {str(e)}"
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(dict)
        
        # Add nodes
        workflow.add_node("analyze_problem", self._analyze_problem)
        workflow.add_node("research", self._research)
        workflow.add_node("calculate", self._calculate)
        workflow.add_node("validate", self._validate)
        workflow.add_node("finalize", self._finalize)
        
        # Add edges
        workflow.set_entry_point("analyze_problem")
        workflow.add_edge("analyze_problem", "research")
        workflow.add_edge("research", "calculate")
        workflow.add_edge("calculate", "validate")
        workflow.add_edge("validate", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    async def _analyze_problem(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the guesstimate problem and break it down"""
        self._log_node("analyze_problem")
        problem = state["problem"]
        
        prompt = f"""
        Analyze this guesstimate problem and break it down into components:
        
        Problem: {problem}
        
        Identify:
        1. What needs to be estimated
        2. Key factors and assumptions needed
        3. What research might be helpful
        4. Calculation approach
        
        Respond in JSON format with keys: target, factors, research_needs, approach
        """
        
        self._log_llm("Analyzing problem structure and components")
        response = await self.llm.ainvoke([SystemMessage(content=prompt)])
        
        try:
            analysis = json.loads(response.content)
        except:
            analysis = {
                "target": "Unknown estimation target",
                "factors": ["Population", "Market size", "Usage patterns"],
                "research_needs": ["Current market data", "Demographics"],
                "approach": "Top-down estimation"
            }
        
        state["analysis"] = analysis
        self._log_node("analyze_problem", "COMPLETED")
        return state
    
    async def _research(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Research relevant information using web search"""
        self._log_node("research")
        research_needs = state["analysis"].get("research_needs", [])
        research_results = {}
        
        for need in research_needs[:3]:  # Limit to 3 searches
            try:
                self._log(f"[SEARCH] Web Search: {need}")
                result = await self._web_search(need)
                research_results[need] = result
            except Exception as e:
                research_results[need] = f"Research failed: {str(e)}"
        
        state["research"] = research_results
        self._log_node("research", "COMPLETED")
        return state
    
    async def _calculate(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Perform calculations using the MCP calculator"""
        self._log_node("calculate")
        analysis = state["analysis"]
        research = state["research"]
        
        # Generate calculation steps based on analysis and research
        calc_prompt = f"""
        Based on this analysis and research, create calculation steps:
        
        Analysis: {analysis}
        Research: {research}
        
        Provide specific mathematical expressions to calculate the estimate.
        Use realistic numbers based on the research.
        """
        
        self._log_llm("Generating calculation steps from analysis and research")
        response = await self.llm.ainvoke([SystemMessage(content=calc_prompt)])
        
        # Extract and perform calculations
        calculations = []
        calc_steps = response.content.split('\n')
        
        for step in calc_steps:
            if any(op in step for op in ['+', '-', '*', '/', 'sqrt']):
                try:
                    # Extract mathematical expression
                    expr = self._extract_expression(step)
                    if expr:
                        result = await self._calculate_expression(expr)
                        calculations.append({"expression": expr, "result": result})
                except Exception as e:
                    calculations.append({"expression": step, "error": str(e)})
        
        state["calculations"] = calculations
        self._log_node("calculate", "COMPLETED")
        return state
    
    async def _validate(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the results and check reasonableness"""
        self._log_node("validate")
        calculations = state["calculations"]
        
        if calculations:
            final_result = calculations[-1].get("result", "No result")
        else:
            final_result = "No calculations performed"
        
        validation_prompt = f"""
        Validate this guesstimate result:
        
        Problem: {state["problem"]}
        Final Result: {final_result}
        Calculations: {calculations}
        
        Is this result reasonable? Provide validation and any adjustments needed.
        """
        
        self._log_llm("Validating results and checking reasonableness")
        response = await self.llm.ainvoke([SystemMessage(content=validation_prompt)])
        
        state["validation"] = response.content
        state["final_estimate"] = final_result
        self._log_node("validate", "COMPLETED")
        return state
    
    async def _finalize(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create final answer with explanation"""
        self._log_node("finalize")
        final_answer = f"""
        GUESSTIMATE SOLUTION
        
        Problem: {state["problem"]}
        
        Final Estimate: {state["final_estimate"]}
        
        Analysis: {state["analysis"]["target"]}
        
        Key Calculations:
        {chr(10).join([f"- {calc['expression']} = {calc.get('result', 'Error')}" for calc in state.get("calculations", [])])}
        
        Validation: {state["validation"]}
        """
        
        state["final_answer"] = final_answer
        self._log_node("finalize", "COMPLETED")
        return state
    
    async def _web_search(self, query: str) -> str:
        """Search using HTTP web-search tool"""
        self._log_mcp("web-search", f"Searching for: {query}")
        return await self._call_http_tool("web-search", {"query": query})
    
    async def _calculate_expression(self, expression: str) -> float:
        """Calculate using HTTP calculator tool"""
        self._log_mcp("calculator", f"Calculating: {expression}")
        
        try:
            content = await self._call_http_tool("calculator", {"expression": expression})
            
            # Extract numeric result from the response
            import re
            numbers = re.findall(r'[-+]?\d*\.?\d+', content)
            if numbers:
                numeric_result = float(numbers[-1])  # Get the last number (usually the result)
                self._log_mcp("calculator", f"SUCCESS - Result: {numeric_result}")
                return numeric_result
            else:
                self._log_mcp("calculator", "FAILED - No numeric result found")
                raise ValueError(f"No numeric result in: {content}")
                
        except Exception as e:
            self._log_mcp("calculator", f"FAILED - {str(e)}")
            raise e
    
    def _extract_expression(self, text: str) -> str:
        """Extract mathematical expression from text"""
        import re
        
        # Look for expressions with = sign first
        equals_pattern = r'([\d\+\-\*/\(\)\.\s%sqrt]+)\s*='
        equals_matches = re.findall(equals_pattern, text)
        for match in equals_matches:
            clean_match = match.strip()
            if len(clean_match) > 1 and any(op in clean_match for op in ['+', '*', '/', 'sqrt']):
                return clean_match
        
        # Look for standalone numbers and operations
        number_pattern = r'\d+(?:\.\d+)?\s*[\+\-\*/]\s*\d+(?:\.\d+)?'
        number_matches = re.findall(number_pattern, text)
        if number_matches:
            return number_matches[0].strip()
        
        # Look for sqrt expressions
        sqrt_pattern = r'sqrt\(\d+(?:\.\d+)?\)'
        sqrt_matches = re.findall(sqrt_pattern, text)
        if sqrt_matches:
            return sqrt_matches[0]
        
        return None
    
    async def solve(self, problem: str) -> str:
        """Solve a guesstimate problem"""
        self._log(f"[START] Starting LangGraph workflow for: {problem}")
        
        initial_state = {"problem": problem}
        result = await self.graph.ainvoke(initial_state)
        self._log("[COMPLETE] LangGraph workflow completed successfully")
        return result["final_answer"]