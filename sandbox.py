import docker
import tempfile
import os
import json
import time
from typing import Dict, Any, Optional
import subprocess
import sys

class SecureSandbox:
    """Secure sandbox for executing AI-generated code"""
    
    def __init__(self):
        self.client = None
        self.use_docker = self._check_docker_available()
    
    def _check_docker_available(self) -> bool:
        """Check if Docker is available"""
        try:
            self.client = docker.from_env()
            self.client.ping()
            return True
        except Exception:
            print("Docker not available, using restricted Python execution")
            return False
    
    def execute_code_safe(self, code: str, data_csv: str) -> Dict[str, Any]:
        """Execute code in a secure environment"""
        if self.use_docker:
            return self._execute_in_docker(code, data_csv)
        else:
            return self._execute_restricted_python(code, data_csv)
    
    def _execute_in_docker(self, code: str, data_csv: str) -> Dict[str, Any]:
        """Execute code in Docker container"""
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write data file
                data_path = os.path.join(temp_dir, "data.csv")
                with open(data_path, "w") as f:
                    f.write(data_csv)
                
                # Write code file
                code_path = os.path.join(temp_dir, "execute.py")
                safe_code = self._wrap_code_for_docker(code)
                with open(code_path, "w") as f:
                    f.write(safe_code)
                
                # Create Dockerfile for execution
                dockerfile_content = """
FROM python:3.12-slim
RUN pip install pandas numpy matplotlib plotly
WORKDIR /app
COPY . .
RUN useradd -m sandboxuser
USER sandboxuser
CMD ["python", "execute.py"]
"""
                dockerfile_path = os.path.join(temp_dir, "Dockerfile")
                with open(dockerfile_path, "w") as f:
                    f.write(dockerfile_content)
                
                # Build and run container
                image = self.client.images.build(
                    path=temp_dir,
                    tag="sandbox-execution",
                    rm=True
                )[0]
                
                container = self.client.containers.run(
                    image.id,
                    detach=True,
                    mem_limit="512m",
                    cpu_period=100000,
                    cpu_quota=50000,  # 50% CPU
                    network_disabled=True,
                    read_only=True,
                    tmpfs={'/tmp': 'noexec,nosuid,size=100m'}
                )
                
                # Wait for completion with timeout
                try:
                    result = container.wait(timeout=30)
                    logs = container.logs().decode('utf-8')
                    
                    return {
                        "success": result["StatusCode"] == 0,
                        "output": logs,
                        "error": None if result["StatusCode"] == 0 else logs
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "output": "",
                        "error": f"Execution timeout or error: {str(e)}"
                    }
                finally:
                    container.remove(force=True)
                    
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Docker execution error: {str(e)}"
            }
    
    def _execute_restricted_python(self, code: str, data_csv: str) -> Dict[str, Any]:
        """Execute code in restricted Python environment"""
        try:
            import io
            import sys
            import pandas as pd
            import numpy as np
            import matplotlib.pyplot as plt
            import plotly.express as px
            import plotly.graph_objects as go
            from io import StringIO, BytesIO
            import base64
            
            # Capture output
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            try:
                sys.stdout = stdout_capture
                sys.stderr = stderr_capture
                
                # Load data
                df = pd.read_csv(StringIO(data_csv))
                
                # Define safe globals
                safe_globals = {
                    'pd': pd,
                    'np': np,
                    'plt': plt,
                    'px': px,
                    'go': go,
                    'df': df,
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
                
                # Execute code
                exec(code, safe_globals)
                
                output = stdout_capture.getvalue()
                error = stderr_capture.getvalue()
                
                # Check for plot output
                plot_data = None
                if 'plot_base64' in safe_globals:
                    plot_data = safe_globals['plot_base64']
                
                return {
                    "success": not error,
                    "output": output,
                    "error": error if error else None,
                    "plot_data": plot_data
                }
                
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                plt.close('all')  # Clean up matplotlib
                
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Execution error: {str(e)}"
            }
    
    def _wrap_code_for_docker(self, code: str) -> str:
        """Wrap user code for safe Docker execution"""
        wrapper = f"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO, BytesIO
import base64
import sys
import warnings
warnings.filterwarnings('ignore')

try:
    # Load data
    df = pd.read_csv('data.csv')
    
    # User code
{code}
    
    print("Execution completed successfully")
    
except Exception as e:
    print(f"Error: {{e}}", file=sys.stderr)
    sys.exit(1)
"""
        return wrapper

# Global sandbox instance
sandbox = SecureSandbox()