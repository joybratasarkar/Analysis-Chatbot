#!/usr/bin/env python3
"""
Startup script for the AI Data Analysis Chatbot
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check if virtual environment exists
    if not Path("venv").exists():
        print("❌ Virtual environment not found. Creating one...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
        print("✅ Virtual environment created")
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
        import langchain
        print("✅ Core dependencies found")
    except ImportError:
        print("❌ Dependencies missing. Installing...")
        if os.name == 'nt':  # Windows
            subprocess.run(["venv\\Scripts\\pip", "install", "-r", "requirements.txt"])
        else:  # Unix/Linux
            subprocess.run(["venv/bin/pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed")
    
    # Check environment file
    if not Path(".env").exists():
        print("❌ .env file not found")
        return False
    
    # Check Google credentials
    if not Path("xooper.json").exists():
        print("❌ Google Cloud credentials not found")
        return False
    
    print("✅ All requirements met")
    return True

def start_redis():
    """Check Redis connection (local or remote)"""
    try:
        import redis
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        redis_url = os.getenv("REDIS_URL")
        
        if redis_url:
            # Use Redis URL from environment
            r = redis.from_url(redis_url)
            r.ping()
            print("✅ Redis is running (using external Redis URL)")
            return True
        else:
            # Try local Redis
            r = redis.Redis(host='localhost', port=6379, password='securepassword123')
            r.ping()
            print("✅ Redis is running (local)")
            return True
    except Exception as e:
        print(f"❌ Redis not available: {e}")
        print("   Please check your Redis configuration in .env file")
        return False

def start_application():
    """Start the FastAPI application"""
    print("🚀 Starting AI Data Analysis Chatbot...")
    print("📊 The application will be available at: http://localhost:8000")
    print("🔗 API documentation at: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")

def main():
    """Main startup function"""
    print("🤖 AI Data Analysis Chatbot - Startup")
    print("=====================================")
    
    if not check_requirements():
        print("❌ Requirements check failed. Please fix the issues above.")
        return
    
    if not start_redis():
        print("⚠️  Redis not available. Some features may not work properly.")
        print("   You can start Redis with: redis-server")
        print("   Or use Docker Compose: docker-compose up redis")
        
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return
    
    start_application()

if __name__ == "__main__":
    main()