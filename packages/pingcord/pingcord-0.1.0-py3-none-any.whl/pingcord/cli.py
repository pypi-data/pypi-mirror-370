#! /usr/bin/env python3

import argparse
import subprocess
import sys
import requests
from string import Template
from pathlib import Path
import yaml

CONFIG_FILE = Path.home() / '.pingcord'

def load_config():
    # Load the configuration from the YAML file
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f)
    return {}

def run_command(command_list):
    # Run shell command and return output
    try:
        result = subprocess.run(
            command_list,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()
    
def split_message(message, limit=2000):
    # Split a string into chunks of at most `limit` characters
    lines = message.splitlines(keepends=True)
    chunks = []
    current = ""
    
    for line in lines:
        if len(current) + len(line) > limit:
            if current:
                chunks.append(current)
            # If a single line is longer than limit, split it
            while len(line) > limit:
                chunks.append(line[:limit])
                line = line[limit:]
            current = line
        else:
            current += line
    if current:
        chunks.append(current)
    return chunks

    
def send_to_discord(webhook, template_content, syntax, content):
    
    if template_content and "${output}" in template_content:
        before, after = template_content.split("${output}", 1)
    else:
        before, after = "", ""
        
    chunk_limit = 1999 - len(before) - len(after)
    if chunk_limit <= 1000:
        print("❌ Template too long for Discord message limit, template must not exceed 1000 characters.", file=sys.stderr)
        sys.exit(1)
            
    # Send a message to Discord, splitting it into multiple messages if longer than 2000 characters.
    # Provides clear terminal feedback.
    chunks = split_message(content, limit=chunk_limit)
    
    if len(chunks) > 1:
        print(f"⚠️ Message is too long for Discord, splitting into {len(chunks)} parts...")

    for i, chunk in enumerate(chunks, start=1):
        try:
            message = format_output(chunk, syntax)
            if template_content:
                if len(chunks) == 1:
                    message = Template(template_content).safe_substitute(output=message)
                elif i == 1:
                    message = before + message
                elif i == len(chunks):
                    message = message + after
                else:
                    message = message
            else:
                message = message

            response = requests.post(webhook, json={"content": message})
            response.raise_for_status()
            if len(chunks) == 1:
                print(f"✅ Message sent to Discord !")
            elif i < len(chunks):
                print(f"✅ Part {i} sent successfully... continuing")
            else:
                print(f"✅ Part {i} sent successfully, full message delivered!")
        except requests.RequestException as e:
            print(f"❌ Failed to send part {i}: {e}, aborting!", file=sys.stderr)
            sys.exit(1)
    
def format_output(output, syntax=None):
    if syntax:
        output = f"```{syntax}\n{output}\n```"
    return output

def main():
    defaults = load_config()
    
    parser = argparse.ArgumentParser(description="Send shell command output or file content to Discord using webhooks.")
    parser.add_argument(
        '-w', '--webhook', 
        help='Discord webhook URL',
        metavar='<discord-webhook>'
    )
    parser.add_argument(
        '-t', '--template', 
        help="Markdown template file, use ${output} to insert command output",
        metavar='template.md',
        type=Path
    )
    parser.add_argument(
        '-s', '--syntax', 
        help='Syntax highlighting for code block',
        metavar='<language>'
    )
    parser.add_argument(
        '-q', '--quiet', 
        action='store_true', 
        help="Suppress printing the original command output"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-c', '--command', 
        nargs=argparse.REMAINDER,
        help='Shell command to run',
        metavar='<shell-command>'
    )
    group.add_argument(
        '-f', '--file', 
        type=Path, 
        help='File to read and send content from',
        metavar='<file>'
    )

    args = parser.parse_args()
    
    webhook = args.webhook or defaults.get('webhook')
    template = args.template or defaults.get('template')
    syntax = args.syntax or defaults.get('syntax')
    
    if not webhook:
        print("No webhook provided and no default found in ~/.pingcord.", file=sys.stderr)
        sys.exit(1)

    if template:
        template_path = Path(template).expanduser()
        if not template_path.exists():
            print(f"Template file '{template}' not found.", file=sys.stderr)
            sys.exit(1)
        template_content = template_path.read_text()
    else:
        template_content = None
        
    if args.file:
        if not args.file.exists():
            print(f"File '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)
        command_output = args.file.read_text().strip()
    elif args.command:
        command_output = run_command(args.command)
    elif not sys.stdin.isatty():
        command_output = sys.stdin.read().strip()
    else:
        print("No input provided (no command, file, or piped input).", file=sys.stderr)
        sys.exit(1)

    # formatted_output = format_output(command_output, syntax)

    if not args.quiet:
        print(command_output.strip(), end="\n\n")

    send_to_discord(webhook, template_content, syntax, command_output)