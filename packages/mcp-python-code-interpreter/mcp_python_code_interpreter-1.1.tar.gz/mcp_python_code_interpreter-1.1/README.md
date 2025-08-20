[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/yzfly-mcp-python-interpreter-badge.png)](https://mseep.ai/app/yzfly-mcp-python-interpreter)

# MCP Python Interpreter

A Model Context Protocol (MCP) server that allows LLMs to interact with Python environments, read and write files, execute Python code, and manage development workflows.

## Features

- **Environment Management**: List and use different Python environments (system and conda)
- **Code Execution**: Run Python code or scripts in any available environment
- **Package Management**: List installed packages and install new ones
- **File Operations**: 
  - Read files of any type (text, source code, binary)
  - Write text and binary files
- **Python Prompts**: Templates for common Python tasks like function creation and debugging

## Installation

You can install the MCP Python Interpreter using pip:

```bash
pip install mcp-python-interpreter
```

Or with uv:

```bash
uv install mcp-python-interpreter
```

## Usage with Claude Desktop

1. Install [Claude Desktop](https://claude.ai/download)
2. Open Claude Desktop, click on menu, then Settings
3. Go to Developer tab and click "Edit Config"
4. Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-python-interpreter": {
        "command": "uvx",
        "args": [
            "mcp-python-interpreter",
            "--dir",
            "/path/to/your/work/dir",
            "--python-path",
            "/path/to/your/python"
        ],
        "env": {
            "MCP_ALLOW_SYSTEM_ACCESS": 0
        },
    }
  }
}
```

For Windows:

```json
{
  "mcpServers": {
    "python-interpreter": {
      "command": "uvx",
      "args": [
        "mcp-python-interpreter",
        "--dir",
        "C:\\path\\to\\your\\working\\directory",
        "--python-path",
        "/path/to/your/python"
      ],
        "env": {
            "MCP_ALLOW_SYSTEM_ACCESS": 0
        }
    }
  }
}
```

5. Restart Claude Desktop
6. You should now see the MCP tools icon in the chat interface

The `--dir` parameter is **required** and specifies where all files will be saved and executed. This helps maintain security by isolating the MCP server to a specific directory.

### Prerequisites

- Make sure you have `uv` installed. If not, install it using:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- For Windows:
  ```powershell
  powershell -ExecutionPolicy Bypass -Command "iwr -useb https://astral.sh/uv/install.ps1 | iex"
  ```

## Available Tools

The Python Interpreter provides the following tools:

### Environment and Package Management
- **list_python_environments**: List all available Python environments (system and conda)
- **list_installed_packages**: List packages installed in a specific environment
- **install_package**: Install a Python package in a specific environment

### Code Execution
- **run_python_code**: Execute Python code in a specific environment
- **run_python_file**: Execute a Python file in a specific environment

### File Operations
- **read_file**: Read contents of any file type, with size and safety limits
  - Supports text files with syntax highlighting
  - Displays hex representation for binary files
- **write_file**: Create or overwrite files with text or binary content
- **write_python_file**: Create or overwrite a Python file specifically
- **list_directory**: List Python files in a directory

## Available Resources

- **python://environments**: List all available Python environments
- **python://packages/{env_name}**: List installed packages for a specific environment
- **python://file/{file_path}**: Get the content of a Python file
- **python://directory/{directory_path}**: List all Python files in a directory

## Prompts

- **python_function_template**: Generate a template for a Python function
- **refactor_python_code**: Help refactor Python code
- **debug_python_error**: Help debug a Python error

## Example Usage

Here are some examples of what you can ask Claude to do with this MCP server:

- "Show me all available Python environments on my system"
- "Run this Python code in my conda-base environment: print('Hello, world!')"
- "Create a new Python file called 'hello.py' with a function that says hello"
- "Read the contents of my 'data.json' file"
- "Write a new configuration file with these settings..."
- "List all packages installed in my system Python environment"
- "Install the requests package in my system Python environment"
- "Run data_analysis.py with these arguments: --input=data.csv --output=results.csv"

## File Handling Capabilities

The MCP Python Interpreter now supports comprehensive file operations:
- Read text and binary files up to 1MB
- Write text and binary files
- Syntax highlighting for source code files
- Hex representation for binary files
- Strict file path security (only within the working directory)

## Security Considerations

This MCP server has access to your Python environments and file system. Key security features include:
- Isolated working directory
- File size limits
- Prevented writes outside the working directory
- Explicit overwrite protection

Always be cautious about running code or file operations that you don't fully understand.

## License

MIT
