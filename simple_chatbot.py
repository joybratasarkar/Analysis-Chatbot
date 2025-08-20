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

from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage, AIMessage

from llm import get_vertex_ai_llm, get_redis_client

# Initialize LLM and Redis
llm = get_vertex_ai_llm()
redis_client = get_redis_client(decode_responses=True)

class SimpleAIChatbot:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
    
    async def process_message(self, session_id: str, message: str, data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Process a message and return response"""
        # Initialize or get session
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "messages": [AIMessage(content="Hello! I'm your AI data analysis assistant. How can I help you today?")],
                "data": None
            }
        
        session = self.sessions[session_id]
        
        # Update data if provided
        if data is not None:
            session["data"] = data
        
        # Add user message
        session["messages"].append(HumanMessage(content=message))
        
        # Process based on content
        if session["data"] is None and any(word in message.lower() for word in ["plot", "chart", "analyze", "visualize"]):
            response = "I'd be happy to help you analyze your data! Please upload a CSV file first."
            plot_data = None
            generated_code = None
        elif session["data"] is not None:
            # Generate code and visualization
            response, plot_data, generated_code = await self._analyze_data(message, session["data"])
        else:
            # General conversation
            response = await self._general_response(message)
            plot_data = None
            generated_code = None
        
        # Add AI response
        session["messages"].append(AIMessage(content=response))
        
        # Store in Redis for persistence
        try:
            redis_client.setex(
                f"session:{session_id}",
                3600,  # 1 hour expiry
                json.dumps({
                    "messages": [{"type": type(m).__name__, "content": m.content} for m in session["messages"]],
                    "has_data": session["data"] is not None
                })
            )
        except Exception as e:
            print(f"Redis error: {e}")
        
        return {
            "response": response,
            "plot_data": plot_data,
            "generated_code": generated_code,
            "session_id": session_id
        }
    
    async def _analyze_data(self, user_request: str, df: pd.DataFrame) -> tuple:
        """Analyze data and generate visualization"""
        data_info = self._get_data_info(df)
        
        # Generate code using Gemini
        prompt = f"""
        You are a data analysis expert. Generate Python code to analyze the following dataset based on the user's request.
        
        Dataset information:
        {data_info}
        
        User request: {user_request}
        
        Requirements:
        1. Use only pandas (as 'df'), plotly.express (as 'px'), and plotly.graph_objects (as 'go')
        2. Create appropriate visualizations based on the data and request
        3. Convert plot to HTML string and store in variable 'plot_html_base64'
        4. Use: plot_html_base64 = fig.to_html()
        5. Do not use file I/O operations
        6. Include brief analysis insights
        
        Example code structure:
        ```python
        # Analysis code here
        fig = px.scatter(df, x='column1', y='column2', title='My Plot')
        plot_html_base64 = fig.to_html()
        ```
        
        Generate only the Python code, no explanations.
        """
        
        try:
            response = await asyncio.wait_for(llm.ainvoke([HumanMessage(content=prompt)]), timeout=30.0)
            generated_code = response.content.strip()
        except asyncio.TimeoutError:
            return "Error: Code generation timed out", None, "# Timeout error occurred"
        
        # Execute code safely
        plot_data = None
        try:
            # Create safe execution environment
            import numpy as np
            safe_globals = {
                'pd': pd,
                'np': np,
                'px': px,
                'go': go,
                'df': df,
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
            
            # Execute generated code
            exec(generated_code, safe_globals)
            
            # Get plot data
            if 'plot_html_base64' in safe_globals:
                plot_data = safe_globals['plot_html_base64']
            
        except Exception as e:
            generated_code = f"# Error in code execution: {str(e)}\n{generated_code}"
        
        # Check for specific queries first
        specific_result = self._check_for_specific_query(df, user_request)
        if specific_result:
            return specific_result, plot_data, generated_code
        
        # Generate analysis summary for general queries
        actual_stats = self._get_actual_statistics(df)
        analysis_prompt = f"""
        Analyze this ACTUAL dataset and provide insights based on the user's request: "{user_request}"
        
        ACTUAL Data Summary:
        {df.describe().to_string()}
        
        ACTUAL Statistics:
        {actual_stats}
        
        First few rows of ACTUAL data:
        {df.head().to_string()}
        
        IMPORTANT: Use ONLY the actual data provided above. Do NOT make up statistics.
        Provide a concise analysis with key insights based on the REAL data. Keep it under 150 words.
        """
        
        try:
            analysis_response = await asyncio.wait_for(llm.ainvoke([HumanMessage(content=analysis_prompt)]), timeout=20.0)
            return analysis_response.content.strip(), plot_data, generated_code
        except asyncio.TimeoutError:
            return "Analysis completed successfully. The data has been processed and visualized.", plot_data, generated_code
    
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
    
    async def _general_response(self, message: str) -> str:
        """Generate general conversational response"""
        prompt = f"""
        You are a helpful AI data analysis assistant. Respond to this message in a friendly, professional way.
        If the user asks about data analysis capabilities, mention that you can help with CSV data analysis, 
        visualization, and insights once they upload data.
        
        User message: {message}
        
        Keep response concise and helpful.
        """
        
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        return response.content.strip()
    
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

# Global chatbot instance
chatbot = SimpleAIChatbot()