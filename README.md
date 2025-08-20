# 🤖 AI Data Analysis Chatbot

A secure, production-ready AI chatbot built with **LangGraph** and **FastAPI** that analyzes CSV data, generates visualizations, and provides intelligent insights using **Google's Gemini AI**.

## 🎯 Features

### ✨ **Core Capabilities**
- **🔍 Smart Data Analysis**: Upload CSV files and get AI-powered insights
- **📊 Interactive Visualizations**: Auto-generates Plotly and Matplotlib charts
- **🧠 Context-Aware Responses**: Remembers conversation history and uploaded data
- **👤 Specific Queries**: Ask about individual records (e.g., "Show me John Doe's information")
- **🔒 Secure Code Execution**: Runs AI-generated code in isolated sandboxes
- **⚡ Real-time Processing**: WebSocket support for instant responses

### 🛡️ **Security Features**
- **Containerized Execution**: Docker-based code sandboxing
- **Input Validation**: File size limits, content validation, message filtering
- **Restricted Environment**: Limited Python execution with safe builtins only
- **CORS Protection**: Configurable origin restrictions
- **Session Management**: Redis-based session persistence

### 📈 **Advanced Analytics**
- **Person-Specific Lookups**: "Tell me about Mia Rodriguez" → Returns her exact data
- **Department Analysis**: "Show me Engineering employees" → Lists all matches  
- **Statistical Insights**: Real data statistics, not AI hallucinations
- **Custom Visualizations**: Generates appropriate charts based on data type and query

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI Web  │────│   LangGraph      │────│   Gemini AI     │
│   Interface     │    │   Workflow       │    │   (Vertex AI)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │              ┌──────────────────┐               │
         └──────────────│   Redis Cache    │───────────────┘
                        │   (Sessions)     │
                        └──────────────────┘
                                 │
                    ┌──────────────────────────┐
                    │    Docker Sandbox       │
                    │   (Code Execution)      │
                    └──────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker (optional, for enhanced security)
- Redis (local or cloud)
- Google Cloud Account with Vertex AI enabled

### 1. **Clone & Setup**
```bash
git clone <repository-url>
cd Batlabs
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. **Configure Environment**
```bash
# Create .env file
cat > .env << EOF
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=securepassword123
EOF
```

### 3. **Setup Google Cloud Credentials**
- Download your service account key as `xooper.json`
- Place it in the project root directory

### 4. **Start Redis** (if using local Redis)
```bash
# Option 1: Docker Compose (recommended)
docker-compose up redis

# Option 2: Local Redis
redis-server --requirepass securepassword123

# Option 3: Use cloud Redis (update REDIS_URL in .env)
```

### 5. **Run the Application**

#### **Simple Version** (recommended for development)
```bash
python simple_main.py
```

#### **Full Version** (with LangGraph workflow)
```bash
python main.py
```

#### **Auto-Setup Script**
```bash
python start.py  # Checks requirements and starts automatically
```

### 6. **Access the Application**
- **Web Interface**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📊 Usage Examples

### **Upload Data**
1. Click "📁 Upload CSV File"
2. Select your CSV file (e.g., `sample_data.csv`)
3. Wait for "File uploaded successfully" message

### **Query Examples**

#### **👤 Person-Specific Queries**
```
"Tell me about Mia Rodriguez"
→ Returns: Age: 24, Salary: $52,000, Department: HR, Experience: 1 year
```

#### **📈 Department Analysis**
```
"Show me all Engineering employees"
→ Lists all employees in Engineering department with their details
```

#### **📊 Data Visualization**
```
"Create a salary vs experience scatter plot"
"Show me department distribution"
"Plot performance scores by age"
```

#### **🔍 Statistical Analysis**
```
"What's the average salary by department?"
"Who has the highest performance score?"
"Show me salary trends"
```

## 🛠️ Development

### **Project Structure**
```
Batlabs/
├── main.py                 # Full FastAPI app with LangGraph
├── simple_main.py          # Simplified FastAPI app
├── chatbot.py              # LangGraph-based chatbot
├── simple_chatbot.py       # Basic chatbot implementation
├── llm.py                  # LLM and Redis factories
├── sandbox.py              # Secure code execution
├── logging_config.py       # Comprehensive logging setup
├── start.py                # Auto-setup script
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Multi-service setup
├── sample_data.csv         # Example dataset
└── logs/                   # Application logs
    ├── application.log     # Structured JSON logs
    ├── chatbot.log        # Chatbot-specific logs
    ├── api.log            # API request logs
    └── errors.log         # Error logs
```

### **Available Endpoints**

#### **Core API**
- `GET /` - Web interface
- `POST /upload-csv` - Upload CSV files
- `POST /chat` - Send chat messages
- `GET /health` - Health check
- `WS /ws/{session_id}` - WebSocket connection

#### **Response Format**
```json
{
  "response": "Analysis text",
  "session_id": "uuid",
  "plot_data": "base64_image_or_html",
  "generated_code": "python_code"
}
```

### **Environment Variables**
```bash
# Redis Configuration
REDIS_URL=redis://user:pass@host:port/db
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=./xooper.json
```

## 🐳 Docker Deployment

### **Single Container**
```bash
docker build -t ai-chatbot .
docker run -p 8000:8000 \
  -v ./xooper.json:/app/xooper.json:ro \
  -e REDIS_URL=your_redis_url \
  ai-chatbot
```

### **Docker Compose** (recommended)
```bash
docker-compose up
```

This starts:
- AI Chatbot on port 8000
- Redis on port 6379
- Automatic health checks
- Volume mounts for credentials

## 🔧 Configuration

### **Chatbot Behavior**
- **File Size Limit**: 10MB per CSV
- **Message Length**: Max 10,000 characters
- **Code Timeout**: 30 seconds for generation, 30 seconds for execution
- **Session Expiry**: 1 hour in Redis

### **Security Settings**
```python
# CORS Origins (main.py, simple_main.py)
allow_origins=[
    "http://localhost:3000",
    "http://localhost:8000", 
    "http://127.0.0.1:8000"
]

# Sandbox Restrictions (sandbox.py)
- Network disabled
- Read-only filesystem
- Memory limit: 512MB
- CPU limit: 50%
- Execution timeout: 30s
```

### **Logging Configuration**
```python
# Log Levels
- Console: INFO
- File: INFO  
- Errors: ERROR only

# Log Rotation
- Max size: 10MB
- Backup count: 5
- JSON format for structured logs
```

## 🔍 Troubleshooting

### **Common Issues**

#### **"Redis not available"**
```bash
# Check Redis connection
redis-cli ping

# Start Redis with Docker
docker run -d -p 6379:6379 redis:7-alpine

# Update .env with correct Redis URL
```

#### **"Google Cloud credentials not found"**
```bash
# Verify file exists
ls -la xooper.json

# Check environment variable
echo $GOOGLE_APPLICATION_CREDENTIALS

# Test authentication
gcloud auth application-default login
```

#### **"Import errors"**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.12+
```

#### **"Docker not available"**
```bash
# Check Docker status
docker --version
docker ps

# The app works without Docker (uses restricted Python)
# But Docker provides better security
```

### **Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with auto-reload
uvicorn main:app --reload --log-level debug

# Check logs
tail -f logs.logs
```

## 🧪 Testing

### **Manual Testing**
1. Upload `sample_data.csv`
2. Try these queries:
   - "Mia Rodriguez"
   - "Engineering department" 
   - "Create a salary chart"
   - "Average performance by department"

### **API Testing**
```bash
# Health check
curl http://localhost:8000/health

# Upload file
curl -X POST "http://localhost:8000/upload-csv" \
  -F "file=@sample_data.csv"

# Send chat message
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me salary statistics"}'
```

## 📝 Logging

The application provides comprehensive logging:

### **Log Files**
- **`logs.logs`**: Main application log (human-readable)
- **`logs/application.log`**: Structured JSON logs
- **`logs/chatbot.log`**: AI interaction logs
- **`logs/api.log`**: HTTP request logs
- **`logs/errors.log`**: Error-only logs
- **`logs/performance.log`**: Timing metrics

### **Log Entry Example**
```
2025-08-20 15:17:18,823 - INFO - api - File upload - employee_data.csv, size: 2048, shape: (26, 6)
2025-08-20 15:17:18,824 - INFO - chatbot - Code execution - type: plotly, success: True
2025-08-20 15:17:18,825 - INFO - performance - Performance - chat_processing: 2.150s
```

## ⚠️ **IMPORTANT: Fixed Data Analysis Issue**

### **Problem Identified**
Previously, when querying specific individuals (e.g., "Mia Rodriguez"), the system would return **generic, made-up statistics** instead of actual person data.

### **Solution Implemented** ✅
- **Person-Specific Queries**: Now correctly identifies and returns individual records
- **Real Data Analysis**: Uses actual CSV data instead of generating fake statistics
- **Prevents AI Hallucination**: Forces analysis based only on uploaded data

### **Before vs After**
```bash
# BEFORE (incorrect):
Query: "Mia Rodriguez"
Response: "The dataset represents 26 individuals with average salary $76,692..."

# AFTER (correct):
Query: "Mia Rodriguez"  
Response: "**Mia Rodriguez**
Age: 24
Salary: 52000
Department: HR
Experience Years: 1
Performance Score: 7.1"
```

## 🔒 Security Considerations

### **Production Checklist**
- [ ] Update CORS origins to specific domains
- [ ] Use HTTPS in production
- [ ] Secure Redis with authentication
- [ ] Monitor file upload sizes
- [ ] Set up proper logging rotation
- [ ] Use secrets management for credentials
- [ ] Enable Docker for code execution
- [ ] Set up rate limiting
- [ ] Monitor resource usage

### **Data Privacy**
- User data is stored temporarily in Redis
- Sessions expire after 1 hour
- No persistent data storage
- Code execution is sandboxed
- File uploads are validated

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Vertex AI** for the Gemini LLM
- **LangChain & LangGraph** for workflow orchestration
- **FastAPI** for the web framework
- **Plotly & Matplotlib** for visualizations
- **Redis** for session management
- **Docker** for secure sandboxing

---

## 🆘 Support

For issues and questions:
1. Check the [troubleshooting section](#-troubleshooting)
2. Review application logs in `logs.logs`
3. Test with the provided `sample_data.csv`
4. Ensure all prerequisites are installed

**Happy Data Analysis! 🎉📊**# Analysis-Chatbot
