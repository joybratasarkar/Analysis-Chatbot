import asyncio
import json
import os
import tempfile
import uuid
from typing import Dict, List, Any, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from io import StringIO, BytesIO
import base64
import time
import logging

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict

from llm import get_vertex_ai_llm, get_redis_client
from logging_config import log_code_execution, log_performance_metric, log_error

# Initialize LLM and Redis
llm = get_vertex_ai_llm()
redis_client = get_redis_client(decode_responses=True)

class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
    data: Optional[pd.DataFrame]
    generated_code: Optional[str]
    plot_result: Optional[str]
    analysis_summary: Optional[str]
    session_id: str

class SecureAIChatbot:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.graph = self._create_graph()
    
    def _create_graph(self):
        """Create LangGraph workflow"""
        workflow = StateGraph(ChatState)
        
        # Define nodes
        workflow.add_node("process_input", self._process_input)
        workflow.add_node("generate_code", self._generate_code)
        workflow.add_node("execute_code", self._execute_code)
        workflow.add_node("analyze_results", self._analyze_results)
        workflow.add_node("respond", self._respond)
        
        # Define edges
        workflow.set_entry_point("process_input")
        workflow.add_edge("process_input", "generate_code")
        workflow.add_edge("generate_code", "execute_code")
        workflow.add_edge("execute_code", "analyze_results")
        workflow.add_edge("analyze_results", "respond")
        workflow.add_edge("respond", END)
        
        return workflow.compile()
    
    async def _process_input(self, state: ChatState) -> ChatState:
        """Process user input and determine if data processing is needed"""
        last_message = state["messages"][-1].content
        
        # Check if this is a data-related query
        data_keywords = ["plot", "analyze", "visualize", "chart", "graph", "data", "csv"]
        needs_data_processing = any(keyword in last_message.lower() for keyword in data_keywords)
        
        if needs_data_processing and state["data"] is None:
            state["messages"].append(AIMessage(content="I'd be happy to help you analyze your data! Please upload a CSV file first."))
            return state
            
        return state
    
    async def _generate_code(self, state: ChatState) -> ChatState:
        """Generate Python code using Gemini for data analysis"""
        if state["data"] is None:
            return state
            
        user_request = state["messages"][-1].content
        data_info = self._get_data_info(state["data"])
        
        prompt = f"""
        You are a data analysis expert. Generate secure Python code to analyze the following dataset based on the user's request.
        
        Dataset information:
        {data_info}
        
        User request: {user_request}
        
        Requirements:
        1. Use only pandas, numpy, matplotlib, and plotly (px, go)
        2. The DataFrame is already loaded as 'df'
        3. Generate appropriate plots based on the data and request
        4. Include error handling
        5. For matplotlib: save to BytesIO buffer and convert to base64, store in 'plot_base64'
        6. For plotly: use fig.to_html() and store in 'plot_base64'
        7. Do not use any file I/O operations
        8. Do not import any modules not in the allowed list
        
        Example for matplotlib:
        ```python
        plt.figure(figsize=(10,6))
        plt.scatter(df['x'], df['y'])
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.getvalue()).decode()
        plt.close()
        ```
        
        Example for plotly:
        ```python
        fig = px.scatter(df, x='x', y='y')
        plot_base64 = fig.to_html()
        ```
        
        Generate clean, secure Python code only. No explanations.
        """
        
        try:
            response = await asyncio.wait_for(llm.ainvoke([HumanMessage(content=prompt)]), timeout=30.0)
            state["generated_code"] = response.content.strip()
        except asyncio.TimeoutError:
            state["generated_code"] = None
            state["plot_result"] = "Error: Code generation timed out"
        
        return state
    
    async def _execute_code(self, state: ChatState) -> ChatState:
        """Execute generated code in a secure environment"""
        if not state["generated_code"] or state["data"] is None:
            return state
        
        start_time = time.time()
        session_id = state.get("session_id", "unknown")
        
        try:
            # Create secure execution environment
            import numpy as np
            safe_globals = {
                'pd': pd,
                'np': np,
                'plt': plt,
                'px': px,
                'go': go,
                'df': state["data"],
                'StringIO': StringIO,
                'BytesIO': BytesIO,
                'base64': base64,
                '__builtins__': {
                    'len': len, 'str': str, 'int': int, 'float': float, 'bool': bool,
                    'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
                    'range': range, 'enumerate': enumerate, 'zip': zip,
                    'max': max, 'min': min, 'sum': sum, 'abs': abs,
                    'round': round, 'sorted': sorted, 'print': print,
                    'isinstance': isinstance, 'hasattr': hasattr, 'getattr': getattr,
                    'TypeError': TypeError, 'ValueError': ValueError, 'IndexError': IndexError
                }
            }
            
            # Execute code in restricted environment
            exec(state["generated_code"], safe_globals)
            
            # Capture plot if created
            plot_type = None
            if 'plot_base64' in safe_globals:
                state["plot_result"] = safe_globals['plot_base64']
                plot_type = "plotly" if safe_globals['plot_base64'].startswith('<') else "matplotlib"
            else:
                # Check if there are any matplotlib figures
                if plt.get_fignums():
                    # Try to capture matplotlib plot
                    buf = BytesIO()
                    plt.savefig(buf, format='png', bbox_inches='tight')
                    buf.seek(0)
                    plot_base64 = base64.b64encode(buf.getvalue()).decode()
                    state["plot_result"] = plot_base64
                    plot_type = "matplotlib"
                    plt.close('all')
                else:
                    state["plot_result"] = None
            
            # Log successful execution
            execution_time = time.time() - start_time
            log_code_execution(session_id, plot_type or "no_plot", True, execution_time)
            log_performance_metric("code_execution", execution_time, session_id)
                
        except Exception as e:
            execution_time = time.time() - start_time
            state["plot_result"] = f"Error executing code: {str(e)}"
            log_code_execution(session_id, "error", False, execution_time, str(e))
            log_error(e, "code_execution", session_id)
        finally:
            # Always clean up matplotlib figures
            plt.close('all')
            
        return state
    
    async def _analyze_results(self, state: ChatState) -> ChatState:
        """Analyze the results and generate insights"""
        if state["data"] is None:
            return state
            
        user_request = state["messages"][-1].content
        df = state["data"]
        
        # Check if user is asking about a specific person
        analysis_result = self._check_for_specific_query(df, user_request)
        
        if analysis_result:
            state["analysis_summary"] = analysis_result
            return state
        
        # General data analysis
        data_summary = df.describe().to_string()
        actual_stats = self._get_actual_statistics(df)
        
        prompt = f"""
        Analyze the following ACTUAL dataset and provide insights based on the user's request.
        
        ACTUAL Data Summary:
        {data_summary}
        
        ACTUAL Statistics:
        {actual_stats}
        
        First few rows of ACTUAL data:
        {df.head().to_string()}
        
        User Request: {user_request}
        
        IMPORTANT: Use ONLY the actual data provided above. Do NOT make up statistics.
        Provide a concise analysis with key insights, patterns, and recommendations based on the REAL data.
        Keep it under 200 words and focus on actionable insights from the actual dataset.
        """
        
        try:
            response = await asyncio.wait_for(llm.ainvoke([HumanMessage(content=prompt)]), timeout=20.0)
            state["analysis_summary"] = response.content.strip()
        except asyncio.TimeoutError:
            state["analysis_summary"] = "Analysis timed out. The data has been processed successfully."
        
        return state
    
    def _check_for_specific_query(self, df: pd.DataFrame, user_request: str) -> Optional[str]:
        """Check if user is asking about specific people or records"""
        user_request_lower = user_request.lower()
        
        # Check if asking about a specific person (if 'name' column exists)
        if 'name' in df.columns:
            for _, row in df.iterrows():
                name = str(row['name']).lower()
                # Check if any part of the name is mentioned in the request
                name_parts = name.split()
                if any(part in user_request_lower for part in name_parts if len(part) > 2):
                    return self._format_person_info(row)
        
        # Check for specific values in other columns
        for col in df.columns:
            if df[col].dtype == 'object':  # String columns
                for value in df[col].unique():
                    if str(value).lower() in user_request_lower and len(str(value)) > 3:
                        matching_rows = df[df[col] == value]
                        if len(matching_rows) <= 5:  # If few matches, show specific info
                            return self._format_specific_records(matching_rows, col, value)
        
        return None
    
    def _format_person_info(self, person_row) -> str:
        """Format information for a specific person"""
        info_parts = []
        for col, value in person_row.items():
            if col.lower() == 'name':
                info_parts.append(f"**{value}**")
            else:
                # Format column names nicely
                col_formatted = col.replace('_', ' ').title()
                info_parts.append(f"{col_formatted}: {value}")
        
        return "Here's the information for " + "\n".join(info_parts)
    
    def _format_specific_records(self, records_df, column, value) -> str:
        """Format information for specific records matching a criteria"""
        count = len(records_df)
        result = f"Found {count} record{'s' if count != 1 else ''} where {column} is '{value}':\n\n"
        
        for _, row in records_df.iterrows():
            result += "• " + ", ".join([f"{col}: {val}" for col, val in row.items()]) + "\n"
        
        return result
    
    def _get_actual_statistics(self, df: pd.DataFrame) -> str:
        """Get actual statistics from the dataset"""
        stats = []
        stats.append(f"Dataset size: {len(df)} rows, {len(df.columns)} columns")
        
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                stats.append(f"{col}: mean={df[col].mean():.2f}, min={df[col].min()}, max={df[col].max()}")
            elif df[col].dtype == 'object':
                unique_count = df[col].nunique()
                stats.append(f"{col}: {unique_count} unique values")
        
        return "\n".join(stats)
    
    async def _respond(self, state: ChatState) -> ChatState:
        """Generate final response to user"""
        if state["analysis_summary"] and state["plot_result"]:
            response = f"{state['analysis_summary']}\n\n[Plot generated and ready for display]"
        elif state["data"] is None:
            response = "Hello! I'm your AI data analysis assistant. I can help you analyze CSV data, create visualizations, and provide insights. Please upload a CSV file to get started!"
        else:
            response = "I'm ready to help analyze your data. What would you like to explore?"
            
        state["messages"].append(AIMessage(content=response))
        return state
    
    def _get_data_info(self, df: pd.DataFrame) -> str:
        """Get basic information about the dataset"""
        info = f"""
        Shape: {df.shape}
        Columns: {list(df.columns)}
        Data types: {df.dtypes.to_dict()}
        Missing values: {df.isnull().sum().to_dict()}
        First 3 rows:
        {df.head(3).to_string()}
        """
        return info
    
    async def process_message(self, session_id: str, message: str, data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Process a message and return response"""
        # Initialize or get session
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "messages": [AIMessage(content="Hello! I'm your AI data analysis assistant. How can I help you today?")],
                "data": None,
                "session_id": session_id
            }
        
        session = self.sessions[session_id]
        
        # Update data if provided
        if data is not None:
            session["data"] = data
        
        # Create state
        state = ChatState(
            messages=session["messages"] + [HumanMessage(content=message)],
            data=session["data"],
            generated_code=None,
            plot_result=None,
            analysis_summary=None,
            session_id=session_id
        )
        
        # Run through graph
        result = await self.graph.ainvoke(state)
        
        # Update session
        self.sessions[session_id]["messages"] = result["messages"]
        if result["data"] is not None:
            self.sessions[session_id]["data"] = result["data"]
        
        # Store in Redis for persistence
        try:
            redis_client.setex(
                f"session:{session_id}",
                3600,  # 1 hour expiry
                json.dumps({
                    "messages": [{"type": type(m).__name__, "content": m.content} for m in result["messages"]],
                    "has_data": result["data"] is not None
                })
            )
        except Exception as e:
            print(f"Redis error: {e}")
        
        return {
            "response": result["messages"][-1].content,
            "plot_data": result.get("plot_result"),
            "generated_code": result.get("generated_code"),
            "session_id": session_id
        }

# Global chatbot instance
chatbot = SecureAIChatbot()