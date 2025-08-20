"""
Logging configuration for the AI Data Analysis Chatbot
"""

import logging
import logging.handlers
import os
from datetime import datetime
import json
from typing import Any, Dict

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

class JSONFormatter(logging.Formatter):
    """Custom formatter to output logs in JSON format"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        if hasattr(record, 'user_action'):
            log_entry['user_action'] = record.user_action
        if hasattr(record, 'execution_time'):
            log_entry['execution_time'] = record.execution_time
        if hasattr(record, 'error_type'):
            log_entry['error_type'] = record.error_type
            
        return json.dumps(log_entry)

def setup_logging():
    """Set up logging configuration"""
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for general logs (logs.logs file)
    file_handler = logging.FileHandler('logs.logs', mode='a')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Structured logs in separate directory
    structured_handler = logging.handlers.RotatingFileHandler(
        'logs/application.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    structured_handler.setLevel(logging.INFO)
    structured_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(structured_handler)
    
    # Chatbot specific logger
    chatbot_logger = logging.getLogger('chatbot')
    chatbot_handler = logging.handlers.RotatingFileHandler(
        'logs/chatbot.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    chatbot_handler.setLevel(logging.INFO)
    chatbot_handler.setFormatter(JSONFormatter())
    chatbot_logger.addHandler(chatbot_handler)
    chatbot_logger.propagate = True
    
    # API specific logger
    api_logger = logging.getLogger('api')
    api_handler = logging.handlers.RotatingFileHandler(
        'logs/api.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(JSONFormatter())
    api_logger.addHandler(api_handler)
    api_logger.propagate = True
    
    # Error specific logger
    error_logger = logging.getLogger('errors')
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    error_logger.addHandler(error_handler)
    error_logger.propagate = True
    
    # Performance logger
    perf_logger = logging.getLogger('performance')
    perf_handler = logging.handlers.RotatingFileHandler(
        'logs/performance.log',
        maxBytes=3*1024*1024,  # 3MB
        backupCount=2
    )
    perf_handler.setLevel(logging.INFO)
    perf_handler.setFormatter(JSONFormatter())
    perf_logger.addHandler(perf_handler)
    perf_logger.propagate = False  # Don't propagate to root
    
    return {
        'root': root_logger,
        'chatbot': chatbot_logger,
        'api': api_logger,
        'errors': error_logger,
        'performance': perf_logger
    }

# Utility functions for structured logging
def log_api_request(session_id: str, endpoint: str, method: str, ip: str = None):
    """Log API request"""
    logger = logging.getLogger('api')
    logger.info(
        f"API Request - {method} {endpoint}",
        extra={
            'session_id': session_id,
            'user_action': 'api_request',
            'endpoint': endpoint,
            'method': method,
            'ip_address': ip
        }
    )

def log_chat_interaction(session_id: str, message_length: int, has_data: bool, response_time: float):
    """Log chat interaction"""
    logger = logging.getLogger('chatbot')
    logger.info(
        f"Chat interaction - message_length: {message_length}, has_data: {has_data}",
        extra={
            'session_id': session_id,
            'user_action': 'chat_message',
            'message_length': message_length,
            'has_data': has_data,
            'execution_time': response_time
        }
    )

def log_code_execution(session_id: str, code_type: str, success: bool, execution_time: float, error: str = None):
    """Log code execution"""
    logger = logging.getLogger('chatbot')
    level = logging.INFO if success else logging.ERROR
    logger.log(
        level,
        f"Code execution - type: {code_type}, success: {success}",
        extra={
            'session_id': session_id,
            'user_action': 'code_execution',
            'code_type': code_type,
            'success': success,
            'execution_time': execution_time,
            'error_type': 'execution_error' if error else None
        }
    )
    
    if error:
        error_logger = logging.getLogger('errors')
        error_logger.error(
            f"Code execution failed: {error}",
            extra={
                'session_id': session_id,
                'error_type': 'code_execution_error',
                'code_type': code_type
            }
        )

def log_file_upload(session_id: str, filename: str, size: int, rows: int, columns: int, success: bool, error: str = None):
    """Log file upload"""
    logger = logging.getLogger('api')
    level = logging.INFO if success else logging.ERROR
    logger.log(
        level,
        f"File upload - {filename}, size: {size}, shape: ({rows}, {columns})",
        extra={
            'session_id': session_id,
            'user_action': 'file_upload',
            'uploaded_filename': filename,  # Changed from 'filename' to avoid conflict
            'file_size': size,
            'rows': rows,
            'columns': columns,
            'success': success,
            'error_type': 'upload_error' if error else None
        }
    )

def log_performance_metric(operation: str, duration: float, session_id: str = None, additional_data: Dict[str, Any] = None):
    """Log performance metrics"""
    logger = logging.getLogger('performance')
    extra = {
        'operation': operation,
        'execution_time': duration
    }
    
    if session_id:
        extra['session_id'] = session_id
    
    if additional_data:
        extra.update(additional_data)
    
    logger.info(f"Performance - {operation}: {duration:.3f}s", extra=extra)

def log_error(error: Exception, context: str, session_id: str = None, additional_data: Dict[str, Any] = None):
    """Log errors with context"""
    error_logger = logging.getLogger('errors')
    extra = {
        'error_type': type(error).__name__,
        'context': context
    }
    
    if session_id:
        extra['session_id'] = session_id
    
    if additional_data:
        extra.update(additional_data)
    
    error_logger.error(f"Error in {context}: {str(error)}", extra=extra)

# Initialize logging when module is imported
loggers = setup_logging()

# Log startup
startup_logger = logging.getLogger('api')
startup_logger.info("Logging system initialized")