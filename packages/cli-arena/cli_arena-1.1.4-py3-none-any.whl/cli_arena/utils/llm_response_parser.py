"""
Shared parser for extracting commands from LLM responses.
Used by all agents to standardize command extraction.
"""

import json
import re
from typing import List, Optional


def parse_llm_response_for_commands(content: str) -> List[str]:
    """
    Extract commands from LLM response content.
    Handles multiple formats:
    1. JSON in code blocks (```json...```)
    2. Raw JSON objects
    3. JSON with surrounding text
    
    Args:
        content: The raw LLM response text
        
    Returns:
        List of command strings to execute
    """
    commands = []
    
    # First, try to extract from code blocks
    if '```json' in content:
        # Find JSON code block
        start = content.find('```json') + 7
        end = content.find('```', start)
        if end > start:
            try:
                data = json.loads(content[start:end].strip())
                if isinstance(data, dict) and 'commands' in data:
                    commands = data['commands']
                    return commands if isinstance(commands, list) else []
            except (json.JSONDecodeError, KeyError):
                pass
    
    # Try to find raw JSON object
    if content.strip().startswith('{'):
        try:
            data = json.loads(content.strip())
            if isinstance(data, dict) and 'commands' in data:
                commands = data['commands']
                return commands if isinstance(commands, list) else []
        except json.JSONDecodeError:
            pass
    
    # Try to extract JSON object from mixed text
    # Look for {"commands": [...]} pattern
    json_patterns = [
        r'\{"commands"\s*:\s*\[[^\]]*\]\}',  # Escaped braces
        r'{"commands"\s*:\s*\[[^\]]*\]}',     # Normal braces
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        for match in matches:
            try:
                # Clean up the match
                cleaned = match.replace('\\n', '\n').replace('\\"', '"')
                data = json.loads(cleaned)
                if isinstance(data, dict) and 'commands' in data:
                    commands = data['commands']
                    if isinstance(commands, list) and commands:
                        return commands
            except (json.JSONDecodeError, KeyError):
                continue
    
    # More aggressive: find any JSON-like structure with "commands"
    # This handles cases where JSON is embedded in text
    json_start = content.find('{"commands"')
    if json_start >= 0:
        # Try to find the matching closing brace
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i in range(json_start, len(content)):
            char = content[i]
            
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\' and i + 1 < len(content):
                escape_next = True
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        try:
                            json_str = content[json_start:i+1]
                            data = json.loads(json_str)
                            if isinstance(data, dict) and 'commands' in data:
                                commands = data['commands']
                                if isinstance(commands, list):
                                    return commands
                        except json.JSONDecodeError:
                            pass
                        break
    
    # If all else fails, try to find array-like structures after "commands":
    # This is a last resort for badly formatted responses
    commands_match = re.search(r'"commands"\s*:\s*\[(.*?)\]', content, re.DOTALL)
    if commands_match:
        try:
            # Extract the array content and parse individual commands
            array_content = commands_match.group(1)
            # Split by commas not inside quotes
            import csv
            reader = csv.reader([array_content])
            for row in reader:
                commands = [cmd.strip().strip('"').strip("'") for cmd in row if cmd.strip()]
                if commands:
                    return commands
        except:
            pass
    
    return []


def create_parser_script() -> str:
    """
    Create a standalone Python parser script that can be embedded in bash.
    This is used when the parser needs to run inside Docker containers.
    
    Returns:
        Python script as a string
    """
    return '''#!/usr/bin/env python3
import json
import sys
import re

content = sys.stdin.read()

# Try code blocks first
if '```json' in content:
    start = content.find('```json') + 7
    end = content.find('```', start)
    if end > start:
        try:
            data = json.loads(content[start:end].strip())
            if 'commands' in data:
                for cmd in data['commands']:
                    print(cmd)
                sys.exit(0)
        except:
            pass

# Try raw JSON
if content.strip().startswith('{'):
    try:
        data = json.loads(content.strip())
        if 'commands' in data:
            for cmd in data['commands']:
                print(cmd)
            sys.exit(0)
    except:
        pass

# Try to find JSON object with commands
import re
patterns = [
    r'\\{"commands"\\s*:\\s*\\[[^\\]]*\\]\\}',
    r'{"commands"\\s*:\\s*\\[[^\\]]*\\]}'
]

for pattern in patterns:
    matches = re.findall(pattern, content, re.DOTALL)
    for match in matches:
        try:
            data = json.loads(match)
            if 'commands' in data:
                for cmd in data['commands']:
                    print(cmd)
                sys.exit(0)
        except:
            continue

# Find JSON starting with {"commands"
json_start = content.find('{"commands"')
if json_start >= 0:
    brace_count = 0
    for i in range(json_start, len(content)):
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                try:
                    data = json.loads(content[json_start:i+1])
                    if 'commands' in data:
                        for cmd in data['commands']:
                            print(cmd)
                        sys.exit(0)
                except:
                    pass
                break
'''