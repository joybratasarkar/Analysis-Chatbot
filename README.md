# 🤖 AI Data Analysis Chatbot

A secure, production-ready AI chatbot built with **LangGraph** and **FastAPI** that analyzes CSV data, generates interactive visualizations, and provides intelligent insights using **Google's Gemini AI**.

## 🎯 What This Application Does

### **Core Functionality**
This AI chatbot transforms raw CSV data into actionable insights through natural language conversations. Simply upload your data and ask questions in plain English - the AI will analyze your data, generate Python code, execute it securely, and provide both textual insights and interactive visualizations.

### **Key Capabilities**
- **🔍 Intelligent Data Analysis**: Upload CSV files and get AI-powered statistical insights
- **📊 Interactive Visualizations**: Auto-generates Plotly charts and Matplotlib graphs based on your questions
- **👤 Specific Record Queries**: Ask about individual people or records (e.g., "Tell me about John Smith")
- **📈 Comparative Analysis**: Compare departments, analyze trends, identify patterns
- **🧠 Context-Aware Conversations**: Remembers previous interactions and maintains conversation flow
- **🔒 Secure Code Execution**: AI-generated Python code runs in a secure, isolated environment

## 🚀 Quick Start Guide

### **Prerequisites**
- **Python 3.12+**
- **Redis** (for session management)
- **Google Cloud Account** with Vertex AI API enabled
- **Git** (for cloning the repository)

### **Step 1: Environment Setup**
```bash
# Clone the repository
git clone <your-repository-url>
cd Batlabs

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### **Step 2: Configure Environment**
Create a `.env` file in the project root:
```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=securepassword123

# Google Cloud Authentication
GOOGLE_APPLICATION_CREDENTIALS=./xooper.json
```

### **Step 3: Setup Google Cloud**
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Vertex AI API**
4. Create a **Service Account** with Vertex AI permissions
5. Download the service account key as `xooper.json`
6. Place `xooper.json` in the project root directory

### **Step 4: Setup Redis**
Choose one option:

**Option A: Docker (Recommended)**
```bash
docker run -d -p 6379:6379 --name redis-server redis:7-alpine redis-server --requirepass securepassword123
```

**Option B: Local Installation**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
redis-server --requirepass securepassword123

# macOS with Homebrew
brew install redis
redis-server --requirepass securepassword123
```

**Option C: Docker Compose**
```bash
docker-compose up redis -d
```

### **Step 5: Start the Application**
```bash
# Recommended: Use the auto-setup script
python start.py

# Alternative: Start manually
python simple_main.py
```

### **Step 6: Access the Application**
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📊 How to Use the Application

### **1. Upload Your Data**
1. Open http://localhost:8000 in your browser
2. Click "📁 Upload CSV File"
3. Select your CSV file (or use the included `sample_data.csv`)
4. Wait for the upload confirmation

### **2. Start Asking Questions**
Once your data is uploaded, you can ask questions in natural language:

#### **Person-Specific Queries**
```
"Tell me about Mia Rodriguez"
"Show me John Smith's information"
"What can you tell me about employee Alice Johnson?"
```
**Result**: Returns specific person's details AND an interactive visualization highlighting their position relative to others.

#### **Department Analysis**
```
"Show me all Engineering employees"
"Compare the Marketing department with Sales"
"Which department has the highest average salary?"
```
**Result**: Detailed department breakdown with comparative visualizations.

#### **Statistical Analysis**
```
"What's the average salary by department?"
"Who has the highest performance score?"
"Show me the salary distribution"
"Compare experience levels across departments"
```
**Result**: Statistical insights with supporting charts and graphs.

#### **Visualization Requests**
```
"Create a scatter plot of age vs salary"
"Show me a histogram of performance scores"
"Plot salary trends by experience"
"Visualize department distribution"
```
**Result**: Interactive Plotly charts or static Matplotlib graphs based on your request.

#### **Trend Analysis**
```
"Show me patterns in the data"
"What correlations exist between age and performance?"
"Identify salary outliers"
"Compare junior vs senior employees"
```
**Result**: Pattern recognition with visual representations of trends and correlations.

### **3. Understanding the Responses**
Each response typically includes:
- **Text Analysis**: Written insights and explanations
- **Interactive Visualizations**: Plotly charts you can zoom, pan, and hover over
- **Data Context**: Specific numbers and statistics from your actual data

## 🏗️ Architecture & Technology Stack

### **Application Architecture**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │────│   FastAPI Server │────│   Google Gemini │
│   (Your Input)  │    │   (Processing)   │    │   AI (Analysis) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │              ┌──────────────────┐               │
         └──────────────│   Redis Cache    │───────────────┘
                        │   (Sessions)     │
                        └──────────────────┘
                                 │
                    ┌──────────────────────────┐
                    │   Secure Sandbox        │
                    │   (Code Execution)      │
                    └──────────────────────────┘
```

### **Technology Components**
- **Frontend**: HTML5, CSS3, JavaScript with real-time updates
- **Backend**: FastAPI (Python) with async request handling
- **AI Engine**: Google Gemini 2.0 Flash via Vertex AI
- **Workflow**: LangGraph for structured AI processing
- **Visualization**: Plotly (interactive) and Matplotlib (static)
- **Data Processing**: Pandas and NumPy for data manipulation
- **Session Management**: Redis for conversation persistence
- **Security**: Sandboxed Python execution environment

## 🔒 Security Features

### **Data Protection**
- **Temporary Storage**: Uploaded CSV files are processed in memory only
- **Session Expiry**: All data automatically deleted after 1 hour
- **No Persistent Storage**: No user data is permanently stored
- **UUID Sessions**: Anonymous session identification

### **Code Execution Security**
- **Sandboxed Environment**: AI-generated code runs in restricted Python environment
- **Limited Builtins**: Only safe Python functions are available
- **No File I/O**: Code cannot read from or write to the filesystem
- **No Network Access**: Code cannot make external network requests
- **Memory Limits**: Execution is constrained to prevent resource abuse
- **Timeout Protection**: Code execution automatically stops after 30 seconds

### **Input Validation**
- **File Size Limits**: Maximum 10MB CSV uploads
- **Content Validation**: CSV structure and data type verification
- **Message Length**: Maximum 10,000 characters per query
- **CORS Protection**: Restricted to specific origins

## 🛠️ Configuration & Customization

### **Application Settings**
```python
# File Upload Limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = ['.csv']

# Processing Timeouts
CODE_GENERATION_TIMEOUT = 30  # seconds
CODE_EXECUTION_TIMEOUT = 30   # seconds

# Session Management
SESSION_EXPIRY = 3600  # 1 hour
```

### **Environment Variables**
```bash
# Required Configuration
REDIS_HOST=localhost                           # Redis server host
REDIS_PORT=6379                               # Redis server port  
REDIS_PASSWORD=your_secure_password           # Redis authentication
GOOGLE_APPLICATION_CREDENTIALS=./xooper.json  # Google Cloud key file

# Optional Configuration
LOG_LEVEL=INFO                                # Logging verbosity
REDIS_URL=redis://user:pass@host:port/db      # Alternative Redis URL
```

### **CORS Origins**
For production deployment, update the allowed origins in `main.py` and `simple_main.py`:
```python
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

## 🐳 Docker Deployment

### **Using Docker Compose (Recommended)**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f chatbot

# Stop services
docker-compose down
```

### **Manual Docker Deployment**
```bash
# Build the image
docker build -t ai-chatbot .

# Run the container
docker run -d \
  --name ai-chatbot \
  -p 8000:8000 \
  -v $(pwd)/xooper.json:/app/xooper.json:ro \
  -e REDIS_URL=redis://your-redis-server:6379/0 \
  ai-chatbot
```

## 📋 API Reference

### **Core Endpoints**

#### **Upload CSV Data**
```http
POST /upload-csv
Content-Type: multipart/form-data

file: [CSV file]
```
**Response**:
```json
{
  "session_id": "uuid-string",
  "message": "Uploaded 100 rows and 5 columns",
  "columns": ["name", "age", "salary", "department"],
  "shape": [100, 5]
}
```

#### **Chat with AI**
```http
POST /chat
Content-Type: application/json

{
  "message": "Tell me about the salary distribution",
  "session_id": "uuid-from-upload"
}
```
**Response**:
```json
{
  "response": "The salary distribution shows...",
  "session_id": "uuid-string",
  "plot_data": "base64-encoded-image-or-html",
  "generated_code": "python code that was executed"
}
```

#### **Health Check**
```http
GET /health
```
**Response**:
```json
{
  "status": "healthy",
  "service": "AI Data Analysis Chatbot"
}
```

### **WebSocket Support**
Real-time communication available at:
```
ws://localhost:8000/ws/{session_id}
```

## 🔍 Troubleshooting

### **Common Issues & Solutions**

#### **"Redis not available"**
```bash
# Check if Redis is running
redis-cli ping

# Start Redis manually
redis-server --requirepass your_password

# Using Docker
docker run -d -p 6379:6379 redis:7-alpine redis-server --requirepass your_password
```

#### **"Google Cloud credentials not found"**
```bash
# Verify the file exists
ls -la xooper.json

# Check environment variable
echo $GOOGLE_APPLICATION_CREDENTIALS

# Ensure proper file permissions
chmod 600 xooper.json
```

#### **"Visualization not showing"**
- Ensure your browser supports JavaScript and iframes
- Check that the file upload was successful
- Try refreshing the page and re-uploading the data
- Check browser console for any JavaScript errors

#### **"Port already in use"**
```bash
# Find the process using port 8000
lsof -i :8000

# Kill the process
kill -9 <process_id>

# Or use a different port
uvicorn main:app --port 8001
```

### **Debug Mode**
Enable detailed logging for troubleshooting:
```bash
export LOG_LEVEL=DEBUG
python simple_main.py
```

Check log files in the `logs/` directory:
- `logs.logs` - Main application log
- `logs/errors.log` - Error-specific logs
- `logs/api.log` - HTTP request logs
- `logs/chatbot.log` - AI interaction logs

## 📈 Performance & Scaling

### **Performance Characteristics**
- **File Processing**: Handles CSV files up to 10MB (typically 100k+ rows)
- **Response Time**: 2-5 seconds for typical analysis queries
- **Concurrent Users**: Supports multiple simultaneous sessions
- **Memory Usage**: ~200-500MB per active session
- **Visualization Generation**: 1-3 seconds for interactive charts

### **Scaling Recommendations**
- **Redis Clustering**: Use Redis Cluster for high availability
- **Load Balancing**: Deploy multiple application instances behind a load balancer
- **Caching**: Implement response caching for frequently asked questions
- **Resource Monitoring**: Monitor CPU, memory, and Redis usage
- **Rate Limiting**: Implement per-user request rate limiting

## 💡 Use Cases & Applications

### **Business Intelligence**
- Employee performance analysis
- Salary benchmarking and equity analysis
- Department productivity comparison
- Workforce demographics analysis

### **Data Exploration**
- Quick data profiling and statistics
- Pattern identification and trend analysis
- Outlier detection and data quality assessment
- Correlation analysis between variables

### **Reporting & Insights**
- Executive dashboard creation
- Automated report generation
- Data storytelling with visualizations
- Ad-hoc analysis requests

### **Educational & Research**
- Data science learning and experimentation
- Research data analysis
- Statistical concept demonstration
- Interactive data exploration

## 🛡️ Production Deployment Checklist

### **Security**
- [ ] Update CORS origins to production domains
- [ ] Use HTTPS with proper SSL certificates
- [ ] Secure Redis with authentication and network isolation
- [ ] Implement request rate limiting
- [ ] Set up proper firewall rules
- [ ] Use secrets management for credentials
- [ ] Enable security headers

### **Monitoring**
- [ ] Set up application performance monitoring
- [ ] Configure log aggregation and analysis
- [ ] Implement health check endpoints
- [ ] Set up alerting for errors and performance issues
- [ ] Monitor resource usage (CPU, memory, disk)

### **Reliability**
- [ ] Configure automatic service restart
- [ ] Set up database backups (if using persistent Redis)
- [ ] Implement graceful shutdown handling
- [ ] Configure load balancing
- [ ] Set up container orchestration (Kubernetes/Docker Swarm)

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🤝 Support

For questions, issues, or feature requests:
- Check the application logs in the `logs/` directory
- Verify the health check endpoint: `/health`
- Review this documentation for common solutions
- Create GitHub issues for bugs or enhancements

---

**Version**: 1.2.0  
**Last Updated**: August 2025  
**Status**: Production Ready