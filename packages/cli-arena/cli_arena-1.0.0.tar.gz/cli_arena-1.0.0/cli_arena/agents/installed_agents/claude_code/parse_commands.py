#!/usr/bin/env python3
"""
Simple script to parse JSON commands from Claude output.
"""

import json
import sys

def parse_commands(claude_output):
    """Parse commands from Claude output."""
    try:
        # Remove markdown code blocks if present
        content = claude_output
        if '```json' in content:
            start = content.find('```json') + 7
            end = content.find('```', start)
            if end > start:
                content = content[start:end].strip()
        
        data = json.loads(content)
        if 'commands' in data:
            return data['commands']
    except:
        pass
    return []

if __name__ == "__main__":
    claude_output = sys.stdin.read()
    commands = parse_commands(claude_output)
    for cmd in commands:
        print(cmd) 