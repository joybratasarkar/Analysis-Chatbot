# AI Data Analysis Chatbot

A production-ready AI-powered data analysis platform that transforms CSV data into actionable insights through natural language conversations. Built with FastAPI, LangGraph, and Google Gemini AI.

## Features

- **🔍 Natural Language Data Analysis** - Ask questions about your data in plain English
- **📊 Interactive Visualizations** - Auto-generated Plotly charts and Matplotlib graphs
- **🤖 AI-Powered Insights** - Powered by Google Gemini 2.0 Flash via Vertex AI
- **🔒 Secure Code Execution** - Sandboxed Python environment for safe AI-generated code
- **🛡️ Enterprise Security** - NVIDIA NeMo Guardrails for comprehensive AI safety
- **⚡ Real-time Processing** - WebSocket support for instant responses
- **📈 Comprehensive Analytics** - Statistical analysis, trend detection, and pattern recognition

## Quick Start

### Prerequisites

- Python 3.12+
- Redis server
- Google Cloud account with Vertex AI API enabled

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/joybratasarkar/Analysis-Chatbot.git
cd Analysis-Chatbot
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment**
```bash
# Create .env file
cat > .env << EOF
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_password
GOOGLE_APPLICATION_CREDENTIALS=./credVertex.json
EOF
```

4. **Set up Google Cloud credentials**
   - Create a service account in Google Cloud Console
   - Enable Vertex AI API
   - Download credentials as `credVertex.json`
   - Place in project root

5. **Start Redis**
```bash
# Using Docker (recommended)
docker run -d -p 6379:6379 --name redis-server redis:7-alpine redis-server --requirepass your_secure_password

# Or using docker-compose
docker-compose up redis -d
```

6. **Run the application**
```bash
python start.py
```

Access the application at http://localhost:8000

## Usage

### Basic Workflow

1. **Upload CSV data** via the web interface
2. **Ask questions** in natural language:
   - "Tell me about Mia Rodriguez"
   - "Show salary distribution by department"
   - "Create a scatter plot of age vs performance"
   - "Which department has the highest average salary?"

### Example Queries

```bash
# Person-specific analysis
"Tell me about John Smith"

# Department comparisons
"Compare Engineering and Marketing departments"

# Statistical insights
"What's the correlation between age and salary?"

# Visualization requests
"Create a histogram of performance scores"
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │────│   FastAPI Server │────│   Google Gemini │
│   (Frontend)    │    │   (Backend)      │    │   AI (Analysis) │
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

## Technology Stack

- **Backend**: FastAPI with async request handling
- **AI Engine**: Google Gemini 2.0 Flash via Vertex AI
- **Workflow**: LangGraph for structured AI processing
- **Visualization**: Plotly (interactive) and Matplotlib (static)
- **Data Processing**: Pandas and NumPy
- **Session Management**: Redis
- **Security**: Sandboxed Python execution environment

## API Reference

### Upload CSV
```http
POST /upload-csv
Content-Type: multipart/form-data

file: [CSV file]
```

### Chat with AI
```http
POST /chat
Content-Type: application/json

{
  "message": "Show me salary trends",
  "session_id": "uuid-from-upload"
}
```

### Health Check
```http
GET /health
```

### Guardrails Status
```http
GET /guardrails/status
```

## Docker Deployment

### Using Docker Compose
```bash
docker-compose up -d
```

### Manual Docker
```bash
docker build -t ai-chatbot .
docker run -d -p 8000:8000 \
  -v $(pwd)/credVertex.json:/app/credVertex.json:ro \
  -e REDIS_URL=redis://your-redis:6379/0 \
  ai-chatbot
```

## Security Features

- **🛡️ Enterprise Security Rails** - Custom AI safety and security controls inspired by NVIDIA NeMo Guardrails
- **Real-time Input Validation** - Blocks malicious prompts, code injection, and harmful requests
- **Output Filtering** - Prevents data leakage, harmful content generation, and unsafe code
- **Code Safety Validation** - Automatic detection and sanitization of dangerous operations
- **Privacy Protection** - Filters sensitive information (SSNs, credit cards, passwords)
- **Sandboxed Code Execution** - AI-generated code runs in restricted environment
- **Session Management** - UUID-based anonymous sessions
- **Input Validation** - File size limits and content validation
- **Temporary Storage** - Data processed in memory, auto-deleted after 1 hour
- **CORS Protection** - Configurable origin restrictions

### Security Capabilities
- **Malicious Intent Detection**: Blocks requests containing "hack", "exploit", "steal", etc.
- **Code Injection Prevention**: Prevents `os.system()`, `exec()`, `eval()`, and similar unsafe operations
- **Sensitive Data Protection**: Automatically detects and blocks sharing of personal information
- **Safe Code Generation**: Sanitizes AI-generated code to remove dangerous system calls
- **Graceful Degradation**: Continues secure operation even if security systems encounter issues

## Configuration

### Environment Variables
```bash
REDIS_HOST=localhost                           # Redis server host
REDIS_PORT=6379                               # Redis server port
REDIS_PASSWORD=your_secure_password           # Redis authentication
GOOGLE_APPLICATION_CREDENTIALS=./credVertex.json  # Google Cloud credentials
LOG_LEVEL=INFO                                # Logging verbosity
```

### Application Settings
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB file limit
SESSION_EXPIRY = 3600             # 1 hour session timeout
CODE_EXECUTION_TIMEOUT = 30       # 30 second execution limit
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
black .
flake8 .
mypy .
```

### Debug Mode
```bash
export LOG_LEVEL=DEBUG
python simple_main.py
```

## Troubleshooting

### Common Issues

**Redis Connection Failed**
```bash
# Check Redis status
redis-cli ping

# Restart Redis
docker restart redis-server
```

**Google Cloud Authentication Error**
```bash
# Verify credentials file
ls -la credVertex.json

# Check environment variable
echo $GOOGLE_APPLICATION_CREDENTIALS
```

**Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000

# Use different port
uvicorn main:app --port 8001
```

### Log Files
- `logs/api.log` - HTTP request logs
- `logs/chatbot.log` - AI interaction logs
- `logs/errors.log` - Error tracking
- `logs/performance.log` - Performance metrics

## Performance

- **File Processing**: Handles CSV files up to 10MB
- **Response Time**: 2-5 seconds for typical queries
- **Concurrent Users**: Supports multiple simultaneous sessions
- **Memory Usage**: ~200-500MB per active session

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/joybratasarkar/Analysis-Chatbot/issues)
- **Documentation**: Check `/docs` endpoint for API documentation
- **Health Check**: `/health` endpoint for service status

---

**Built with ❤️ by [Joybrata Sarkar](https://github.com/joybratasarkar)**