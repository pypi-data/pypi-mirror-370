# Pingcord

Pingcord is a Python package that allows you to send shell command output or file content to Discord using webhooks. It is designed to make it easy to share command results or file contents directly to a Discord channel.

## Features

-   Send shell command output to Discord.
-   Send file content to Discord.
-   Supports Markdown templates for formatting messages.
-   Syntax highlighting for code blocks.
-   Configurable via a YAML configuration file.

## Installation

You can install Pingcord using pip:

```bash
pip install pingcord
```

## Usage

Pingcord can be used via the command line. Below are some examples of how to use it:

### Send Command Output

```bash
pingcord -w <webhook_url> -c <command>
```

Example:

```bash
pingcord -w https://discord.com/api/webhooks/... -c ls
```

### Send File Content

```bash
pingcord -w <webhook_url> -f <file_path>
```

Example:

```bash
pingcord -w https://discord.com/api/webhooks/... -f example.txt
```

### Use a Markdown Template

You can use a Markdown template file to format your message. Use `${output}` in the template to insert the command output or file content.

```bash
pingcord -w <webhook_url> -t <template_file> -c <command>
```

### Syntax Highlighting

Add syntax highlighting to your message by specifying a language:

```bash
pingcord -w <webhook_url> -s <language> -c <command>
```

Example:

```bash
pingcord -w https://discord.com/api/webhooks/... -s python -c "cat script.py"
```

### Configuration File

You can create a configuration file at `~/.pingcord` to store default values for the webhook URL, template, and syntax highlighting. The file should be in YAML format:

```yaml
webhook: https://discord.com/api/webhooks/...
template: /path/to/template.md
syntax: bash
```

## Requirements

-   Python 3.7 or higher
-   `requests` library

## Installation for Development

To install the package for development, clone the repository and run:

```bash
pip install -e .
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Created by [theo_vdml](https://github.com/theo-vdml).
