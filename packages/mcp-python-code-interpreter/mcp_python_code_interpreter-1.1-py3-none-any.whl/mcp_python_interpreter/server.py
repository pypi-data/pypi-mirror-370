"""
MCP Python Interpreter

A Model Context Protocol server for interacting with Python environments 
and executing Python code. All operations are confined to a specified working directory
or allowed system-wide if explicitly enabled.
"""

import os
import sys
import json
import glob
import subprocess
import tempfile
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import asyncio
import inspect

# Import FastMCP for building our server
from fastmcp import FastMCP, Context, Image

# Parse command line arguments to get the working directory
# Use a default value that works when run via uvx
parser = argparse.ArgumentParser(description='MCP Python Interpreter')
parser.add_argument('--dir', type=str, default=os.getcwd(),
                    help='Working directory for code execution and file operations')
parser.add_argument('--python-path', type=str, default=None,
                    help='Custom Python interpreter path to use as default')
args, unknown = parser.parse_known_args()

# Check if system-wide access is enabled via environment variable
ALLOW_SYSTEM_ACCESS = os.environ.get('MCP_ALLOW_SYSTEM_ACCESS', 'false').lower() in ('true', '1', 'yes')

# Set and create working directory
WORKING_DIR = Path(args.dir).absolute()
WORKING_DIR.mkdir(parents=True, exist_ok=True)

# Set default Python path
DEFAULT_PYTHON_PATH = args.python_path if args.python_path else sys.executable

# Print startup message to stderr (doesn't interfere with MCP protocol)
print(f"MCP Python Interpreter starting in directory: {WORKING_DIR}", file=sys.stderr)
print(f"Using default Python interpreter: {DEFAULT_PYTHON_PATH}", file=sys.stderr)
print(f"System-wide file access: {'ENABLED' if ALLOW_SYSTEM_ACCESS else 'DISABLED'}", file=sys.stderr)

# Create our MCP server
mcp = FastMCP("Python Interpreter")

# ============================================================================
# Helper functions
# ============================================================================

def is_path_allowed(path: Path) -> bool:
    """
    Check if a path is allowed based on security settings.
    
    Args:
        path: Path to check
        
    Returns:
        bool: True if path is allowed, False otherwise
    """
    if ALLOW_SYSTEM_ACCESS:
        return True
    
    return str(path).startswith(str(WORKING_DIR))

def get_python_environments() -> List[Dict[str, str]]:
    """Get all available Python environments (system and conda)."""
    environments = []
    
    # Add default Python if a custom path was specified
    if DEFAULT_PYTHON_PATH != sys.executable:
        try:
            # Get Python version
            version_result = subprocess.run(
                [DEFAULT_PYTHON_PATH, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"],
                capture_output=True, text=True, check=True
            )
            version = version_result.stdout.strip()
            
            environments.append({
                "name": "default",
                "path": DEFAULT_PYTHON_PATH,
                "version": version
            })
        except Exception as e:
            print(f"Error getting version for custom Python path: {e}")
    
    # Add system Python
    environments.append({
        "name": "system",
        "path": sys.executable,
        "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    })
    
    # Try to find conda environments
    try:
        # Check if conda is available
        result = subprocess.run(
            ["conda", "info", "--envs", "--json"],
            capture_output=True, text=True, check=False
        )
        
        if result.returncode == 0:
            conda_info = json.loads(result.stdout)
            for env in conda_info.get("envs", []):
                env_name = os.path.basename(env)
                if env_name == "base":
                    env_name = "conda-base"
                
                # Get Python executable path and version
                python_path = os.path.join(env, "bin", "python")
                if not os.path.exists(python_path):
                    python_path = os.path.join(env, "python.exe")  # Windows
                
                if os.path.exists(python_path):
                    # Get Python version
                    try:
                        version_result = subprocess.run(
                            [python_path, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"],
                            capture_output=True, text=True, check=True
                        )
                        version = version_result.stdout.strip()
                        
                        environments.append({
                            "name": env_name,
                            "path": python_path,
                            "version": version
                        })
                    except Exception:
                        # Skip environments where we can't get the version
                        pass
    except Exception as e:
        print(f"Error getting conda environments: {e}")
    
    return environments

def get_installed_packages(python_path: str) -> List[Dict[str, str]]:
    """Get installed packages for a specific Python environment."""
    try:
        result = subprocess.run(
            [python_path, "-m", "pip", "list", "--format=json"],
            capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error getting installed packages: {e}")
        return []

def execute_python_code(
    code: str, 
    python_path: Optional[str] = None,
    working_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute Python code and return the result.
    
    Args:
        code: Python code to execute
        python_path: Path to Python executable (default: custom or system Python)
        working_dir: Working directory for execution
        
    Returns:
        Dict with stdout, stderr, and status
    """
    if python_path is None:
        python_path = DEFAULT_PYTHON_PATH
    
    # Create a temporary file for the code
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as temp:
        temp.write(code)
        temp_path = temp.name
    
    try:
        result = subprocess.run(
            [python_path, temp_path],
            capture_output=True, text=True,
            cwd=working_dir
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "status": result.returncode
        }
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except Exception:
            pass

def find_python_files(directory: str or Path) -> List[Dict[str, str]]:
    """Find all Python files in a directory and its subdirectories."""
    files = []
    
    directory_path = Path(directory)
    if not directory_path.exists():
        return files  # Return empty list instead of throwing error
    
    for path in directory_path.rglob("*.py"):
        if path.is_file():
            files.append({
                "path": str(path),
                "name": path.name,
                "size": path.stat().st_size,
                "modified": path.stat().st_mtime
            })
    
    return files

# ============================================================================
# Resources
# ============================================================================

@mcp.resource("python://environments")
def get_environments_resource() -> str:
    """List all available Python environments as a resource."""
    environments = get_python_environments()
    return json.dumps(environments, indent=2)

@mcp.resource("python://packages/{env_name}")
def get_packages_resource(env_name: str) -> str:
    """List installed packages for a specific environment as a resource."""
    environments = get_python_environments()
    
    # Find the requested environment
    env = next((e for e in environments if e["name"] == env_name), None)
    if not env:
        return json.dumps({"error": f"Environment '{env_name}' not found"})
    
    packages = get_installed_packages(env["path"])
    return json.dumps(packages, indent=2)

@mcp.resource("python://file")
def get_file_in_current_dir() -> str:
    """List Python files in the current working directory."""
    files = find_python_files(WORKING_DIR)
    return json.dumps(files, indent=2)

@mcp.tool()
def read_file(file_path: str, max_size_kb: int = 1024) -> str:
    """
    Read the content of any file, with size limits for safety.
    
    Args:
        file_path: Path to the file (relative to working directory or absolute)
        max_size_kb: Maximum file size to read in KB (default: 1024)
    
    Returns:
        str: File content or an error message
    """
    # Handle path based on security settings
    path = Path(file_path)
    if path.is_absolute():
        if not is_path_allowed(path):
            return f"Access denied: System-wide file access is {'DISABLED' if not ALLOW_SYSTEM_ACCESS else 'ENABLED, but this path is not allowed'}"
    else:
        # Make path relative to working directory if it's not already absolute
        path = WORKING_DIR / path
    
    try:
        if not path.exists():
            return f"Error: File '{file_path}' not found"
        
        # Check file size
        file_size_kb = path.stat().st_size / 1024
        if file_size_kb > max_size_kb:
            return f"Error: File size ({file_size_kb:.2f} KB) exceeds maximum allowed size ({max_size_kb} KB)"
        
        # Determine file type and read accordingly
        try:
            # Try to read as text first
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # If it's a known source code type, use code block formatting
            source_code_extensions = ['.py', '.js', '.html', '.css', '.json', '.xml', '.md', '.txt', '.sh', '.c', '.cpp', '.java', '.rb']
            if path.suffix.lower() in source_code_extensions:
                file_type = path.suffix[1:] if path.suffix else 'plain'
                return f"File: {file_path}\n\n```{file_type}\n{content}\n```"
            
            # For other text files, return as-is
            return f"File: {file_path}\n\n{content}"
        
        except UnicodeDecodeError:
            # If text decoding fails, read as binary and show hex representation
            with open(path, 'rb') as f:
                content = f.read()
                hex_content = content.hex()
                return f"Binary file: {file_path}\nFile size: {len(content)} bytes\nHex representation (first 1024 chars):\n{hex_content[:1024]}"
    
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"

@mcp.tool()
def write_file(
    file_path: str,
    content: str,
    overwrite: bool = False,
    encoding: str = 'utf-8'
) -> str:
    """
    Write content to a file in the working directory or system-wide if allowed.
    
    Args:
        file_path: Path to the file to write (relative to working directory or absolute if system access is enabled)
        content: Content to write to the file
        overwrite: Whether to overwrite the file if it exists (default: False)
        encoding: File encoding (default: utf-8)
    
    Returns:
        str: Status message about the file writing operation
    """
    # Handle path based on security settings
    path = Path(file_path)
    if path.is_absolute():
        if not is_path_allowed(path):
            return f"For security reasons, you can only write files inside the working directory: {WORKING_DIR} (System-wide access is disabled)"
    else:
        # Make path relative to working directory if it's not already
        path = WORKING_DIR / path
    
    try:
        # Check if the file exists
        if path.exists() and not overwrite:
            return f"File '{path}' already exists. Use overwrite=True to replace it."
        
        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine write mode based on content type
        if isinstance(content, str):
            # Text content
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
        elif isinstance(content, bytes):
            # Binary content
            with open(path, 'wb') as f:
                f.write(content)
        else:
            return f"Unsupported content type: {type(content)}"
        
        # Get file information
        file_size_kb = path.stat().st_size / 1024
        return f"Successfully wrote to {path}. File size: {file_size_kb:.2f} KB"
    
    except Exception as e:
        return f"Error writing to file: {str(e)}"

@mcp.resource("python://directory")
def get_working_directory_listing() -> str:
    """List all Python files in the working directory as a resource."""
    try:
        files = find_python_files(WORKING_DIR)
        return json.dumps({
            "working_directory": str(WORKING_DIR),
            "files": files
        }, indent=2)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@mcp.tool()
def list_directory(directory_path: str = "") -> str:
    """
    List all Python files in a directory or subdirectory.
    
    Args:
        directory_path: Path to directory (relative to working directory or absolute, empty for working directory)
    """
    try:
        # Handle empty path (use working directory)
        if not directory_path:
            path = WORKING_DIR
        else:
            # Handle absolute paths
            path = Path(directory_path)
            if path.is_absolute():
                if not is_path_allowed(path):
                    return f"Access denied: System-wide file access is {'DISABLED' if not ALLOW_SYSTEM_ACCESS else 'ENABLED, but this path is not allowed'}"
            else:
                # Make path relative to working directory if it's not already absolute
                path = WORKING_DIR / directory_path
                
        # Check if directory exists
        if not path.exists():
            return f"Error: Directory '{directory_path}' not found"
            
        if not path.is_dir():
            return f"Error: '{directory_path}' is not a directory"
            
        files = find_python_files(path)
        
        if not files:
            return f"No Python files found in {directory_path or 'working directory'}"
            
        result = f"Python files in directory: {directory_path or str(WORKING_DIR)}\n\n"
        
        # Group files by subdirectory for better organization
        files_by_dir = {}
        base_dir = path if ALLOW_SYSTEM_ACCESS else WORKING_DIR
        
        for file in files:
            file_path = Path(file["path"])
            try:
                relative_path = file_path.relative_to(base_dir)
                parent = str(relative_path.parent)
                
                if parent == ".":
                    parent = "(root)"
            except ValueError:
                # This can happen with system-wide access enabled
                parent = str(file_path.parent)
                
            if parent not in files_by_dir:
                files_by_dir[parent] = []
                
            files_by_dir[parent].append({
                "name": file["name"],
                "size": file["size"],
                "modified": file["modified"]
            })
            
        # Format the output
        for dir_name, dir_files in sorted(files_by_dir.items()):
            result += f"📁 {dir_name}:\n"
            for file in sorted(dir_files, key=lambda x: x["name"]):
                size_kb = round(file["size"] / 1024, 1)
                result += f"  📄 {file['name']} ({size_kb} KB)\n"
            result += "\n"
            
        return result
    except Exception as e:
        return f"Error listing directory: {str(e)}"

# ============================================================================
# Tools
# ============================================================================

@mcp.tool()
def list_python_environments() -> str:
    """List all available Python environments (system Python and conda environments)."""
    environments = get_python_environments()
    
    if not environments:
        return "No Python environments found."
    
    result = "Available Python Environments:\n\n"
    for env in environments:
        result += f"- Name: {env['name']}\n"
        result += f"  Path: {env['path']}\n"
        result += f"  Version: Python {env['version']}\n\n"
    
    return result

@mcp.tool()
def list_installed_packages(environment: str = "default") -> str:
    """
    List installed packages for a specific Python environment.
    
    Args:
        environment: Name of the Python environment (default: default if custom path provided, otherwise system)
    """
    environments = get_python_environments()
    
    # Use default environment if a custom path was provided, otherwise use system
    default_env = "default" if any(e["name"] == "default" for e in environments) else "system"
    
    # If environment parameter is default but there's no default environment, use system
    if environment == "default" and not any(e["name"] == "default" for e in environments):
        environment = "system"
    
    # Find the requested environment
    env = next((e for e in environments if e["name"] == environment), None)
    if not env:
        return f"Environment '{environment}' not found. Available environments: {', '.join(e['name'] for e in environments)}"
    
    packages = get_installed_packages(env["path"])
    
    if not packages:
        return f"No packages found in environment '{environment}'."
    
    result = f"Installed Packages in '{environment}':\n\n"
    for pkg in packages:
        result += f"- {pkg['name']} {pkg['version']}\n"
    
    return result

@mcp.tool()
def run_python_code(
    code: str, 
    environment: str = "default",
    save_as: Optional[str] = None
) -> str:
    """
    Execute Python code and return the result. Code runs in the working directory.
    
    Args:
        code: Python code to execute
        environment: Name of the Python environment to use (default if custom path provided, otherwise system)
        save_as: Optional filename to save the code before execution (useful for future reference)
    """
    environments = get_python_environments()
    
    # Use default environment if a custom path was provided, otherwise use system
    if environment == "default" and not any(e["name"] == "default" for e in environments):
        environment = "system"
        
    # Find the requested environment
    env = next((e for e in environments if e["name"] == environment), None)
    if not env:
        return f"Environment '{environment}' not found. Available environments: {', '.join(e['name'] for e in environments)}"
    
    # Optionally save the code to a file
    if save_as:
        save_path = WORKING_DIR / save_as
        
        # Ensure filename has .py extension
        if not save_path.suffix == '.py':
            save_path = save_path.with_suffix('.py')
            
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w') as f:
                f.write(code)
        except Exception as e:
            return f"Error saving code to file: {str(e)}"
    
    # Execute the code
    result = execute_python_code(code, env["path"], WORKING_DIR)
    
    output = f"Execution in '{environment}' environment"
    if save_as:
        output += f" (saved to {save_as})"
    output += ":\n\n"
    
    if result["status"] == 0:
        output += "--- Output ---\n"
        if result["stdout"]:
            output += result["stdout"]
        else:
            output += "(No output)\n"
    else:
        output += f"--- Error (status code: {result['status']}) ---\n"
        if result["stderr"]:
            output += result["stderr"]
        else:
            output += "(No error message)\n"
        
        if result["stdout"]:
            output += "\n--- Output ---\n"
            output += result["stdout"]
    
    return output

@mcp.tool()
def install_package(
    package_name: str,
    environment: str = "default",
    upgrade: bool = False
) -> str:
    """
    Install a Python package in the specified environment.
    
    Args:
        package_name: Name of the package to install
        environment: Name of the Python environment (default if custom path provided, otherwise system)
        upgrade: Whether to upgrade the package if already installed (default: False)
    """
    environments = get_python_environments()
    
    # Use default environment if a custom path was provided, otherwise use system
    if environment == "default" and not any(e["name"] == "default" for e in environments):
        environment = "system"
        
    # Find the requested environment
    env = next((e for e in environments if e["name"] == environment), None)
    if not env:
        return f"Environment '{environment}' not found. Available environments: {', '.join(e['name'] for e in environments)}"
    
    # Build the pip command
    cmd = [env["path"], "-m", "pip", "install"]
    
    if upgrade:
        cmd.append("--upgrade")
    
    cmd.append(package_name)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            return f"Successfully {'upgraded' if upgrade else 'installed'} {package_name} in {environment} environment."
        else:
            return f"Error installing {package_name}:\n{result.stderr}"
    except Exception as e:
        return f"Error installing package: {str(e)}"

@mcp.tool()
def write_python_file(
    file_path: str,
    content: str,
    overwrite: bool = False
) -> str:
    """
    Write content to a Python file in the working directory or system-wide if allowed.
    
    Args:
        file_path: Path to the file to write (relative to working directory or absolute if system access is enabled)
        content: Content to write to the file
        overwrite: Whether to overwrite the file if it exists (default: False)
    """
    # Handle path based on security settings
    path = Path(file_path)
    if path.is_absolute():
        if not is_path_allowed(path):
            security_status = "DISABLED" if not ALLOW_SYSTEM_ACCESS else "ENABLED, but this path is not allowed"
            return f"For security reasons, you can only write files inside the working directory: {WORKING_DIR} (System-wide access is {security_status})"
    else:
        # Make path relative to working directory if it's not already
        path = WORKING_DIR / path
    
    # Check if the file exists
    if path.exists() and not overwrite:
        return f"File '{path}' already exists. Use overwrite=True to replace it."
    
    try:
        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to file
        with open(path, 'w') as f:
            f.write(content)
        
        return f"Successfully wrote to {path}."
    except Exception as e:
        return f"Error writing to file: {str(e)}"

@mcp.tool()
def run_python_file(
    file_path: str,
    environment: str = "default",
    arguments: Optional[List[str]] = None
) -> str:
    """
    Execute a Python file and return the result.
    
    Args:
        file_path: Path to the Python file to execute (relative to working directory or absolute if system access is enabled)
        environment: Name of the Python environment to use (default if custom path provided, otherwise system)
        arguments: List of command-line arguments to pass to the script
    """
    # Handle path based on security settings
    path = Path(file_path)
    if path.is_absolute():
        if not is_path_allowed(path):
            security_status = "DISABLED" if not ALLOW_SYSTEM_ACCESS else "ENABLED, but this path is not allowed"
            return f"For security reasons, you can only run files inside the working directory: {WORKING_DIR} (System-wide access is {security_status})"
    else:
        # Make path relative to working directory if it's not already
        path = WORKING_DIR / path
    
    if not path.exists():
        return f"File '{path}' not found."
    
    environments = get_python_environments()
    
    # Use default environment if a custom path was provided, otherwise use system
    if environment == "default" and not any(e["name"] == "default" for e in environments):
        environment = "system"
        
    # Find the requested environment
    env = next((e for e in environments if e["name"] == environment), None)
    if not env:
        return f"Environment '{environment}' not found. Available environments: {', '.join(e['name'] for e in environments)}"
    
    # Build the command
    cmd = [env["path"], str(path)]
    
    if arguments:
        cmd.extend(arguments)
    
    try:
        # Run the command with working directory set properly
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=False,
            cwd=WORKING_DIR
        )
        
        output = f"Execution of '{path}' in '{environment}' environment:\n\n"
        
        if result.returncode == 0:
            output += "--- Output ---\n"
            if result.stdout:
                output += result.stdout
            else:
                output += "(No output)\n"
        else:
            output += f"--- Error (status code: {result.returncode}) ---\n"
            if result.stderr:
                output += result.stderr
            else:
                output += "(No error message)\n"
            
            if result.stdout:
                output += "\n--- Output ---\n"
                output += result.stdout
        
        return output
    except Exception as e:
        return f"Error executing file: {str(e)}"

# ============================================================================
# Prompts
# ============================================================================

@mcp.prompt()
def python_function_template(description: str) -> str:
    """Generate a template for a Python function with docstring."""
    return f"""
Please create a Python function based on this description:

{description}

Include:
- Type hints
- Docstring with parameters, return value, and examples
- Error handling where appropriate
- Comments for complex logic
"""

@mcp.prompt()
def refactor_python_code(code: str) -> str:
    """Help refactor Python code for better readability and performance."""
    return f"""
Please refactor this Python code to improve:
- Readability
- Performance
- Error handling
- Code structure

Original code:
```python
{code}
```

Please explain the changes you made and why they improve the code.
"""

@mcp.prompt()
def debug_python_error(code: str, error_message: str) -> str:
    """Help debug a Python error."""
    return f"""
I'm getting this error when running the following Python code:

```python
{code}
```

Error message:
```
{error_message}
```

Please help me debug this error by:
1. Explaining what the error means
2. Identifying the cause of the error
3. Suggesting fixes to resolve the error
"""

# Run the server when executed directly
if __name__ == "__main__":
    mcp.run()