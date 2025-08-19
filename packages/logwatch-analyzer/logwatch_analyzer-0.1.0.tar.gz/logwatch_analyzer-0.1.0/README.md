# LogWatch Analyzer

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

## First-Time Setup

After installation, you need a configuration file. The package comes with a default one. It's recommended to copy it to your user configuration directory to customize it.

1.  **Create the configuration directory:**
    ```bash
    mkdir -p ~/.config/logwatch
    ```

2.  **Copy the default configuration file.** You can get the default config from the project's GitHub repository or by running the following command after installation to find the package path and copy it:
    ```bash
    # This is an example, the exact path may vary
    python -c "import os, shutil, importlib.resources; src = importlib.resources.files('logwatch_cli').joinpath('config.yaml'); shutil.copy(src, '~/.config/logwatch/config.yaml')"
    echo "Configuration file copied to ~/.config/logwatch/config.yaml"
    ```
    Now you can edit `~/.config/logwatch/config.yaml` to add your own tasks or change LLM providers.

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