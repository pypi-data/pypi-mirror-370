# LogWatch Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

LogWatch Analyzer is a command-line tool to analyze system logs from `journalctl` on Linux systems. It uses a YAML configuration file to define specific analysis tasks and can leverage a Large Language Model (LLM) via Ollama, Gemini, or other providers for in-depth analysis and report generation.

## Features

- **Configurable Analysis**: Define which logs to analyze directly in the `config.yaml` file.
- **Specific Parsers**: Includes optimized parsers for common events like failed SSH logins and kernel errors.
- **LLM Integration**: Utilizes a Large Language Model for generic analysis and generating human-readable reports.
- **Flexible Output**: Displays results in formatted tables in the terminal or generates reports in Markdown format.
- **Simple CLI Interface**: Easy to use with arguments to list tasks, run specific ones, and set time windows.

## Installation

You can install LogWatch Analyzer from PyPI:

```bash
pip install logwatch-analyzer
```

## Configuration

To use LogWatch Analyzer, you need a `config.yaml` file. The script looks for this file in the following locations, in order of priority:

1.  `~/.config/logwatch/config.yaml` (Recommended for users)
2.  `config.yaml` in the current directory where you run the command.

Create the file in one of these locations. The recommended approach is to create a user-specific configuration:

```bash
mkdir -p ~/.config/logwatch
touch ~/.config/logwatch/config.yaml
```

Then, paste the following content into your `config.yaml` file and customize it to your needs.

```yaml
# Configuration file for LogWatch

# Section for LLM provider configuration
# NOTE: The model names provided below are examples. 
# Please replace them with the actual models you intend to use.
llm_providers:
  ollama:
    type: "ollama"
    api_url: "http://localhost:11434/api/generate"
    model: "gemma3:12b" # Example model

  gemma:
    type: "gemma"
    # The URL for Gemma-3-27b-it. Change it if you want to use another model.
    api_url: "https://generativelanguage.googleapis.com/v1beta/models/gemma-3-27b-it:generateContent"
    # The API key will be read from the environment variable specified here.
    api_key_env: "GEMINI_API_KEY"

  gemini:
    type: "gemini"
    # The URL for Gemini 1.5 Flash. Change it if you want to use another model.
    api_url: "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    # The API key will be read from the environment variable specified here.
    api_key_env: "GEMINI_API_KEY"

  openrouter:
    type: "openrouter"
    api_url: "https://openrouter.ai/api/v1/"
    # You can change the model here. Examples: "google/gemma-2-9b-it", "anthropic/claude-3-haiku"
    model: "qwen/qwen-2.5-coder-32b-instruct:free" # Example model
    api_key_env: "OPENROUTER_API_KEY"

# Choose which LLM provider to use from the ones defined above.
active_llm_provider: "gemini"


# Definition of log analysis tasks
logs:
  - name: "SSH Failed Logins"
    command: "journalctl -u sshd -p err -o json --no-pager --since '1 day ago'"
    parser: "ssh_parser"
    # Filters to ignore irrelevant logs (examples)
    filters:
      - "pam_unix(sshd:auth): authentication failure" # Often redundant if you only look at "Failed password"

  - name: "Sudo Usage"
    command: "journalctl /usr/bin/sudo -o json --no-pager --since '1 day ago'"
    parser: "llm_parser"
    filters:
      - "pam_unix(sudo:session): session opened for user root"
      - "pam_unix(sudo:session): session closed for user root"

  - name: "Kernel Errors"
    command: "journalctl -k -p err -o json --no-pager --since '1 day ago'"
    parser: "kernel_parser"
    filters: []

  - name: "General System Analysis"
    command: "journalctl -p err -o json --no-pager --since '1 hour ago'"
    parser: "llm_parser"
    filters: []
```

## Usage

The tool is available as the `logwatch` command.

### List all available tasks
To see a list of all tasks defined in your `config.yaml`:
```bash
logwatch --list
```

### Run a specific task
To execute a single analysis task:
```bash
logwatch --task "SSH Failed Logins"
```

### Run all tasks
To run all tasks in sequence:
```bash
logwatch
```

### Generate a Report File
For tasks that use the `llm_parser`, you can save the generated report to a Markdown file:
```bash
logwatch --task "Sudo Usage" --output report_sudo.md
```

### Override the Time Window
You can specify a different time range from the one in the configuration file on the fly:
```bash
logwatch --task "Kernel Errors" --since "2 hours ago"
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
