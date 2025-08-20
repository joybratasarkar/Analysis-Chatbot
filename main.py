from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import uuid
import json
from typing import Optional, List
import asyncio
from io import StringIO
import time
import logging

from chatbot import chatbot
from logging_config import (
    log_api_request, log_chat_interaction, log_file_upload, 
    log_performance_metric, log_error
)
from guardrails_manager import get_guardrails_manager

app = FastAPI(title="Secure AI Data Analysis Chatbot", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"],  # Specific origins for security
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Serve static files (commented out since we don't have a static directory)
# app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    plot_data: Optional[str] = None
    generated_code: Optional[str] = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def get_homepage():
    """Serve the main chat interface"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Data Analysis Chatbot</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background-color: #f5f5f5;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                background: white; 
                border-radius: 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header { 
                background: #2c3e50; 
                color: white; 
                padding: 20px; 
                text-align: center;
            }
            .chat-container { 
                display: flex; 
                height: 600px;
            }
            .chat-messages { 
                flex: 1; 
                padding: 20px; 
                overflow-y: auto; 
                border-right: 1px solid #eee;
            }
            .visualization-area { 
                flex: 1; 
                padding: 20px; 
                background: #f8f9fa;
            }
            .message { 
                margin: 10px 0; 
                padding: 10px; 
                border-radius: 5px;
            }
            .user-message { 
                background: #e3f2fd; 
                margin-left: 20px;
            }
            .bot-message { 
                background: #f1f8e9; 
                margin-right: 20px;
            }
            .input-area { 
                padding: 20px; 
                border-top: 1px solid #eee;
                display: flex;
                gap: 10px;
            }
            input[type="text"] { 
                flex: 1; 
                padding: 10px; 
                border: 1px solid #ddd; 
                border-radius: 5px;
            }
            button { 
                padding: 10px 20px; 
                background: #2c3e50; 
                color: white; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer;
            }
            button:hover { 
                background: #34495e;
            }
            .upload-area {
                margin: 20px;
                padding: 20px;
                border: 2px dashed #ddd;
                border-radius: 10px;
                text-align: center;
                background: #fafafa;
            }
            .plot-area {
                text-align: center;
                padding: 20px;
            }
            .plot-area img {
                max-width: 100%;
                border-radius: 5px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .status {
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                background: #fff3cd;
                border: 1px solid #ffeaa7;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AI Data Analysis Chatbot</h1>
                <p>Upload your CSV data and let AI analyze it for you!</p>
            </div>
            
            <div class="upload-area">
                <input type="file" id="fileInput" accept=".csv" style="display: none;">
                <button onclick="document.getElementById('fileInput').click()">
                    📁 Upload CSV File
                </button>
                <p id="fileStatus">No file selected</p>
            </div>
            
            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <div class="bot-message message">
                        Hello! I'm your AI data analysis assistant. Upload a CSV file and ask me to analyze it!
                    </div>
                </div>
                <div class="visualization-area">
                    <div class="plot-area" id="plotArea">
                        <p>📊 Visualizations will appear here</p>
                    </div>
                </div>
            </div>
            
            <div class="input-area">
                <input type="text" id="messageInput" placeholder="Ask me about your data..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>
            let sessionId = null;
            let currentData = null;

            document.getElementById('fileInput').addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    document.getElementById('fileStatus').textContent = `Selected: ${file.name}`;
                    uploadFile(file);
                }
            });

            async function uploadFile(file) {
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    const response = await fetch('/upload-csv', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        sessionId = result.session_id;
                        addMessage('File uploaded successfully! ' + result.message, 'bot-message');
                    } else {
                        addMessage('Error uploading file. Please try again.', 'bot-message');
                    }
                } catch (error) {
                    addMessage('Network error. Please try again.', 'bot-message');
                }
            }

            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                addMessage(message, 'user-message');
                input.value = '';
                
                // Show thinking status
                const statusDiv = document.createElement('div');
                statusDiv.className = 'status';
                statusDiv.textContent = '🤔 Analyzing your request...';
                document.getElementById('chatMessages').appendChild(statusDiv);
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            message: message,
                            session_id: sessionId
                        })
                    });
                    
                    statusDiv.remove();
                    
                    if (response.ok) {
                        const result = await response.json();
                        sessionId = result.session_id;
                        addMessage(result.response, 'bot-message');
                        
                        console.log('Response received:', {
                            has_plot_data: !!result.plot_data,
                            plot_data_length: result.plot_data ? result.plot_data.length : 0,
                            plot_data_start: result.plot_data ? result.plot_data.substring(0, 50) : 'none'
                        });
                        
                        if (result.plot_data) {
                            console.log('Displaying plot...');
                            displayPlot(result.plot_data);
                        } else {
                            console.log('No plot data to display');
                        }
                    } else {
                        addMessage('Sorry, I encountered an error. Please try again.', 'bot-message');
                    }
                } catch (error) {
                    statusDiv.remove();
                    addMessage('Network error. Please try again.', 'bot-message');
                }
            }

            function addMessage(message, className) {
                const messagesDiv = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${className}`;
                messageDiv.textContent = message;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }

            function displayPlot(plotData) {
                console.log('displayPlot called with data length:', plotData.length);
                console.log('Plot data type:', plotData.startsWith('<') ? 'HTML/Plotly' : 'Base64/Matplotlib');
                
                const plotArea = document.getElementById('plotArea');
                if (plotData.startsWith('<')) {
                    // HTML plot (Plotly)
                    console.log('Creating Plotly iframe...');
                    plotArea.innerHTML = `<iframe srcdoc="${plotData.replace(/"/g, '&quot;')}" width="100%" height="400" frameborder="0"></iframe>`;
                } else {
                    // Base64 image (Matplotlib)
                    console.log('Creating Matplotlib image...');
                    plotArea.innerHTML = `<img src="data:image/png;base64,${plotData}" alt="Data Visualization" style="max-width: 100%;">`;
                }
                console.log('Plot display completed');
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
        </script>
    </body>
    </html>
    """)

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), request: Request = None):
    """Upload and process CSV file"""
    start_time = time.time()
    session_id = str(uuid.uuid4())
    
    # Log API request
    client_ip = request.client.host if request else None
    log_api_request(session_id, "/upload-csv", "POST", client_ip)
    
    if not file.filename.endswith('.csv'):
        log_error(ValueError("Invalid file type"), "file_upload", session_id, {"filename": file.filename})
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        # Validate file size (10MB limit)
        if file.size and file.size > 10 * 1024 * 1024:
            log_error(ValueError("File too large"), "file_upload", session_id, {"size": file.size})
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB")
            
        # Read CSV content
        content = await file.read()
        if len(content) == 0:
            log_error(ValueError("Empty file"), "file_upload", session_id, {"filename": file.filename})
            raise HTTPException(status_code=400, detail="Empty file uploaded")
            
        csv_content = content.decode('utf-8')
        df = pd.read_csv(StringIO(csv_content))
        
        # Validate DataFrame
        if df.empty:
            log_error(ValueError("Empty DataFrame"), "file_upload", session_id, {"filename": file.filename})
            raise HTTPException(status_code=400, detail="CSV file contains no data")
        if len(df.columns) == 0:
            log_error(ValueError("No columns"), "file_upload", session_id, {"filename": file.filename})
            raise HTTPException(status_code=400, detail="CSV file contains no columns")
        
        # Process with chatbot to store data
        result = await chatbot.process_message(
            session_id=session_id,
            message="Data uploaded successfully",
            data=df
        )
        
        # Log successful upload
        execution_time = time.time() - start_time
        log_file_upload(session_id, file.filename, len(content), df.shape[0], df.shape[1], True)
        log_performance_metric("file_upload", execution_time, session_id)
        
        return {
            "session_id": session_id,
            "message": f"Uploaded {df.shape[0]} rows and {df.shape[1]} columns. Ready for analysis!",
            "columns": list(df.columns),
            "shape": df.shape
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        log_file_upload(session_id, file.filename, 0, 0, 0, False, str(e))
        log_error(e, "file_upload", session_id, {"filename": file.filename})
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage, request: Request = None):
    """Chat endpoint for processing messages"""
    start_time = time.time()
    session_id = message.session_id or str(uuid.uuid4())
    
    # Log API request
    client_ip = request.client.host if request else None
    log_api_request(session_id, "/chat", "POST", client_ip)
    
    try:
        # Validate message
        if not message.message or not message.message.strip():
            log_error(ValueError("Empty message"), "chat", session_id)
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        if len(message.message) > 10000:
            log_error(ValueError("Message too long"), "chat", session_id, {"length": len(message.message)})
            raise HTTPException(status_code=400, detail="Message too long. Maximum 10,000 characters")
        
        result = await chatbot.process_message(
            session_id=session_id,
            message=message.message.strip()
        )
        
        # Log chat interaction
        execution_time = time.time() - start_time
        has_data = result.get("plot_data") is not None
        log_chat_interaction(session_id, len(message.message), has_data, execution_time)
        log_performance_metric("chat_processing", execution_time, session_id)
        
        return ChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            plot_data=result.get("plot_data"),
            generated_code=result.get("generated_code")
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        log_error(e, "chat", session_id, {"message_length": len(message.message) if message.message else 0})
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message
            result = await chatbot.process_message(
                session_id=session_id,
                message=message_data["message"]
            )
            
            # Send response
            response = {
                "type": "chat_response",
                "response": result["response"],
                "plot_data": result.get("plot_data"),
                "generated_code": result.get("generated_code")
            }
            
            await manager.send_personal_message(json.dumps(response), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    guardrails = get_guardrails_manager()
    return {
        "status": "healthy", 
        "service": "AI Data Analysis Chatbot",
        "guardrails": guardrails.get_status()
    }

@app.get("/guardrails/status")
async def guardrails_status():
    """Get detailed guardrails status"""
    guardrails = get_guardrails_manager()
    return guardrails.get_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)