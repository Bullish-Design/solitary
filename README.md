# Solitary

A sandboxed environment for your python code to play in.

## Overview

Solitary provides a simple, secure way to execute Python code in isolated Docker containers. It uses Pydantic models for configuration and connects to existing Docker containers via stdin/stdout/stderr for code execution.

Perfect for:
- Code evaluation and testing
- Untrusted code execution
- Educational platforms
- CI/CD pipeline testing
- Code analysis tools

## Installation

```bash
uv add solitary
```

## Requirements

- Docker installed and running
- Python 3.8+
- docker-py

## Quick Start

```python
from solitary import SandboxConfig, Sandbox

# Create configuration
config = SandboxConfig(container="my-python-container")

# Create sandbox with config
sandbox = Sandbox(config=config)

# Execute code string
result = sandbox.execute("print('Hello from sandbox!')")
print(result.stdout)  # "Hello from sandbox!"

# Execute file
result = sandbox.execute_file("script.py")
print(result.exit_code)  # 0
```

## Configuration

### SandboxConfig Class

```python
from solitary import SandboxConfig

# Basic configuration
config = SandboxConfig(
    container="python-sandbox",
    timeout=30,
    workdir="/workspace",
    max_output_size=1024*1024,
    env={"PYTHONPATH": "/app"}
)

# Connect by container ID
config = SandboxConfig(container="abc123def456")

# Minimal config
config = SandboxConfig(container="my-container")
```

### Configuration Options

```python
config = SandboxConfig(
    container="python-sandbox",        # Container name or ID (required)
    timeout=60,                        # Execution timeout in seconds
    workdir="/app",                    # Working directory in container
    max_output_size=512*1024,          # Max stdout/stderr size in bytes
    env={"DEBUG": "true"},             # Environment variables
    user="sandbox",                    # User to run commands as
    shell="/bin/bash"                  # Shell to use for execution
)
```

## Basic Usage

### Creating and Using Sandbox

```python
from solitary import SandboxConfig, Sandbox

# Create config
config = SandboxConfig(
    container="python-sandbox",
    timeout=30,
    workdir="/workspace"
)

# Create sandbox
sandbox = Sandbox(config=config)

# Execute code
result = sandbox.execute("x = 5\nprint(x * 2)")
print(result.stdout)  # "10"
```

### Executing Code Strings

```python
# Simple execution
result = sandbox.execute("import sys; print(sys.version)")

# Handle errors
result = sandbox.execute("1/0")
if result.exit_code != 0:
    print(f"Error: {result.stderr}")

# Check execution details
print(f"Exit code: {result.exit_code}")
print(f"Execution time: {result.execution_time}s")
print(f"Timed out: {result.timeout_occurred}")
```

### Executing Files

```python
# Execute local file in container
result = sandbox.execute_file("my_script.py")

# Execute with arguments
result = sandbox.execute_file("script.py", args=["arg1", "arg2"])

# Execute file content directly
with open("script.py", "r") as f:
    content = f.read()
result = sandbox.execute(content)
```

## Advanced Usage

### Runtime Configuration Override

```python
# Override config settings per execution
result = sandbox.execute(
    "import os; print(os.getcwd())", 
    workdir="/tmp",
    timeout=10,
    env={"CUSTOM_VAR": "value"}
)
```

### Input/Output Handling

```python
# Provide stdin input
result = sandbox.execute(
    "name = input('Name: '); print(f'Hi {name}')", 
    stdin="Alice"
)
print(result.stdout)  # "Name: Hi Alice"

# Capture all output streams
result = sandbox.execute("""
import sys
print("stdout message")
print("stderr message", file=sys.stderr)
""")
print("OUT:", result.stdout)
print("ERR:", result.stderr)
```

### Context Manager

```python
# Automatic cleanup
config = SandboxConfig(container="python-container")
with Sandbox(config=config) as sandbox:
    result = sandbox.execute("print('Hello World')")
    print(result.stdout)
# Container connection cleaned up automatically
```

## Container Management

### Listing Available Containers

```python
from solitary import list_containers

# List all running containers
containers = list_containers()
for container in containers:
    print(f"{container.name}: {container.image}")

# List containers with Python
python_containers = list_containers(image_filter="python")
```

### Container Health Checks

```python
# Check if container is responsive
if sandbox.is_healthy():
    result = sandbox.execute("print('Ready!')")
else:
    print("Container not responding")

# Get container info
info = sandbox.get_container_info()
print(f"Image: {info.image}")
print(f"Status: {info.status}")
```

## Error Handling

```python
from solitary import SandboxConfig, Sandbox
from solitary.exceptions import SandboxError, ContainerNotFoundError

try:
    config = SandboxConfig(container="nonexistent-container")
    sandbox = Sandbox(config=config)
except ContainerNotFoundError:
    print("Container not found")

try:
    result = sandbox.execute("invalid python code")
    if result.exit_code != 0:
        print(f"Execution failed: {result.stderr}")
except SandboxError as e:
    print(f"Sandbox error: {e}")
```

## API Reference

### SandboxConfig Class

```python
class SandboxConfig(BaseModel):
    container: str                    # Container name or ID
    timeout: int = 30                 # Execution timeout
    workdir: str = "/workspace"       # Working directory
    max_output_size: int = 1024*1024  # Max output size
    env: Dict[str, str] = {}          # Environment variables
    user: Optional[str] = None        # User to run as
    shell: str = "/bin/bash"          # Shell to use
```

### Sandbox Class

```python
class Sandbox(BaseModel):
    config: SandboxConfig
    
    def execute(self, code: str, **kwargs) -> ExecutionResult
    def execute_file(self, filepath: str, **kwargs) -> ExecutionResult
    def is_healthy(self) -> bool
    def get_container_info(self) -> ContainerInfo
    def close(self)
```

### ExecutionResult Class

```python
class ExecutionResult(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    timeout_occurred: bool
    container_id: str
    command: str
```

## Examples

### Code Evaluation Service

```python
from solitary import SandboxConfig, Sandbox

def create_evaluator() -> Sandbox:
    config = SandboxConfig(
        container="python-evaluator",
        timeout=10,
        max_output_size=64*1024,
        env={"PYTHONUNBUFFERED": "1"}
    )
    return Sandbox(config=config)

def evaluate_code(user_code: str) -> dict:
    sandbox = create_evaluator()
    
    with sandbox:
        result = sandbox.execute(user_code)
        
        return {
            "success": result.exit_code == 0,
            "output": result.stdout,
            "error": result.stderr,
            "execution_time": result.execution_time
        }

# Usage
response = evaluate_code("print(sum([1, 2, 3, 4, 5]))")
print(response)  # {"success": True, "output": "15", ...}
```

### Batch Testing

```python
test_cases = [
    "assert 2 + 2 == 4",
    "assert 'hello'.upper() == 'HELLO'",
    "assert len([1, 2, 3]) == 3"
]

config = SandboxConfig(container="test-runner", timeout=5)
with Sandbox(config=config) as sandbox:
    for i, test in enumerate(test_cases):
        result = sandbox.execute(test)
        status = "PASS" if result.exit_code == 0 else "FAIL"
        print(f"Test {i+1}: {status}")
```

### Educational Platform Integration

```python
def create_student_sandbox() -> Sandbox:
    config = SandboxConfig(
        container="student-env",
        timeout=5,
        workdir="/student",
        max_output_size=32*1024,
        user="student"
    )
    return Sandbox(config=config)

def run_student_code(code: str, test_inputs: list) -> dict:
    results = []
    
    with create_student_sandbox() as sandbox:
        for test_input in test_inputs:
            result = sandbox.execute(code, stdin=test_input)
            results.append({
                "input": test_input,
                "output": result.stdout.strip(),
                "passed": result.exit_code == 0,
                "time": result.execution_time
            })
    
    return {"results": results}
```

### Multiple Container Types

```python
# Different configurations for different use cases
configs = {
    "basic": SandboxConfig(
        container="python-basic",
        timeout=10
    ),
    "ml": SandboxConfig(
        container="python-ml",
        timeout=60,
        max_output_size=10*1024*1024,
        env={"CUDA_VISIBLE_DEVICES": "0"}
    ),
    "web": SandboxConfig(
        container="python-web",
        timeout=30,
        env={"PORT": "8000"}
    )
}

# Use appropriate config based on code type
def execute_by_type(code: str, code_type: str):
    config = configs[code_type]
    with Sandbox(config=config) as sandbox:
        return sandbox.execute(code)
```

## Docker Setup Examples

### Basic Python Container

```dockerfile
FROM python:3.11-slim
WORKDIR /workspace
RUN useradd -m sandbox
USER sandbox
CMD ["tail", "-f", "/dev/null"]
```

```bash
docker build -t python-sandbox .
docker run -d --name my-sandbox python-sandbox
```

### Container with Additional Packages

```dockerfile
FROM python:3.11-slim
RUN pip install numpy pandas requests
WORKDIR /workspace
RUN useradd -m sandbox
USER sandbox
CMD ["tail", "-f", "/dev/null"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
