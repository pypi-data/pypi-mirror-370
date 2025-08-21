FROM ubuntu:24.04

# Mark this image as preserved so harness pruning won't delete it
LABEL cli-arena.preserve=true

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tmux asciinema \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    python3-venv \
    sqlite3 \
    build-essential \
    pkg-config \
    libcairo2-dev \
    libpango1.0-dev \
    libjpeg-dev \
    libgif-dev \
    librsvg2-dev \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js v20 (better Web API support)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Install Terraform for DevOps tasks
RUN curl -fsSL https://releases.hashicorp.com/terraform/1.5.7/terraform_1.5.7_linux_amd64.zip -o /tmp/terraform.zip \
    && cd /tmp && unzip terraform.zip \
    && chmod +x terraform \
    && mv terraform /usr/local/bin/terraform \
    && rm -f /tmp/terraform.zip

# Install Go for DevOps repository support
RUN curl -fsSL https://golang.org/dl/go1.21.5.linux-amd64.tar.gz -o /tmp/go.tar.gz \
    && tar -C /usr/local -xzf /tmp/go.tar.gz \
    && rm -f /tmp/go.tar.gz
ENV PATH="/usr/local/go/bin:$PATH"

# Install aider (real tool for AI pair programming)
RUN curl -LsSf https://aider.chat/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Provide a global Python virtualenv to avoid PEP 668 issues in child images
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python packages for API access in the virtual environment
# Include all packages needed by agents and verification scripts
RUN /opt/venv/bin/pip install \
    anthropic \
    google-generativeai \
    openai \
    requests \
    PyYAML \
    python-dotenv \
    pytest \
    aiofiles \
    httpx

# Create claude-code CLI wrapper that matches what the agent expects
RUN cat > /usr/local/bin/claude-code << 'EOFCLAUDE' && chmod +x /usr/local/bin/claude-code
#!/opt/venv/bin/python3
import os
import sys
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--model', default='claude-3-opus-20240229')
parser.add_argument('--fallback-model', default='claude-3-sonnet-20240229')
parser.add_argument('--print', action='store_true')
args, _ = parser.parse_known_args()

# Read instruction from stdin
instruction = sys.stdin.read()

# Check for API key
api_key = os.environ.get('ANTHROPIC_API_KEY')
if not api_key:
    print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
    sys.exit(1)

try:
    from anthropic import Anthropic
    client = Anthropic(api_key=api_key)
    
    # Map model names to actual model IDs
    model_map = {
        'opus': 'claude-3-opus-20240229',
        'sonnet': 'claude-3-sonnet-20240229',
        'haiku': 'claude-3-haiku-20240307'
    }
    
    model_id = model_map.get(args.model, args.model)
    
    # Add JSON output instruction
    full_prompt = instruction + "\n\nReturn your response as raw JSON with a 'commands' array like: {\"commands\":[\"cmd1\",\"cmd2\"]}"
    
    message = client.messages.create(
        model=model_id,
        max_tokens=4000,
        messages=[{"role": "user", "content": full_prompt}]
    )
    
    print(message.content[0].text)
    
except Exception as e:
    # Try fallback model
    if args.fallback_model:
        try:
            model_id = model_map.get(args.fallback_model, args.fallback_model)
            message = client.messages.create(
                model=model_id,
                max_tokens=4000,
                messages=[{"role": "user", "content": full_prompt}]
            )
            print(message.content[0].text)
        except:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
EOFCLAUDE

# Create gemini CLI wrapper that matches what the agent expects
RUN cat > /usr/local/bin/gemini << 'EOFGEMINI' && chmod +x /usr/local/bin/gemini
#!/opt/venv/bin/python3
import os
import sys
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--prompt', help='Prompt text')
parser.add_argument('-y', action='store_true', help='Yes to all')
parser.add_argument('-m', '--model', default='gemini-1.5-flash')
args, _ = parser.parse_known_args()

# Get prompt from argument or stdin
if args.prompt:
    instruction = args.prompt
else:
    instruction = sys.stdin.read()

# Check for API key
api_key = os.environ.get('GEMINI_API_KEY', os.environ.get('GOOGLE_API_KEY'))
if not api_key:
    print("Error: GEMINI_API_KEY not set", file=sys.stderr)
    sys.exit(1)

try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel(args.model)
    
    # Add JSON output instruction
    full_prompt = instruction + "\n\nReturn your response as raw JSON with a 'commands' array like: {\"commands\":[\"cmd1\",\"cmd2\"]}"
    
    response = model.generate_content(full_prompt)
    print(response.text)
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
EOFGEMINI

# Note: OpenAI Codex agent doesn't use a CLI tool, it makes direct API calls
# But create a placeholder in case it's needed
RUN cat > /usr/local/bin/openai-codex << 'EOFOPENAI' && chmod +x /usr/local/bin/openai-codex
#!/opt/venv/bin/python3
import os
import sys
import json

print("OpenAI Codex CLI is not used - agent makes direct API calls", file=sys.stderr)
sys.exit(1)
EOFOPENAI

# Create symlinks for compatibility
RUN ln -sf /usr/local/bin/gemini /usr/local/bin/gemini-cli
RUN ln -sf /usr/local/bin/openai-codex /usr/local/bin/codex

# Note: CLI Arena source will be copied by repository Dockerfiles as needed
# Base image provides foundation tools and environment

# Keep Node options sane
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Add environment variables for easy access in containers
ENV ARENA_OS="ubuntu-24.04"
ENV ARENA_OS_NAME="Ubuntu 24.04 LTS"  
ENV ARENA_ARCH="x86_64"
ENV ARENA_CONTAINER="docker"

# Create environment info file for agents
RUN echo "# CLI Arena Environment Information" > /etc/arena-env && \
    echo "OS: Ubuntu 24.04 LTS" >> /etc/arena-env && \
    echo "Architecture: x86_64" >> /etc/arena-env && \
    echo "Container: Docker" >> /etc/arena-env && \
    echo "Python: $(python3 --version)" >> /etc/arena-env && \
    echo "Node: $(node --version)" >> /etc/arena-env && \
    echo "Go: $(go version | cut -d' ' -f3)" >> /etc/arena-env && \
    echo "Terraform: $(terraform version | head -1)" >> /etc/arena-env && \
    echo "Available tools: git, curl, wget, sqlite3, build-essential, tmux, asciinema, unzip" >> /etc/arena-env && \
    echo "Working directory: /app" >> /etc/arena-env && \
    echo "Python venv: /opt/venv" >> /etc/arena-env

# Add convenient command to display environment
RUN echo '#!/bin/bash' > /usr/local/bin/arena-env && \
    echo 'echo "🖥️  CLI Arena Environment Information"' >> /usr/local/bin/arena-env && \
    echo 'echo "=================================="' >> /usr/local/bin/arena-env && \
    echo 'cat /etc/arena-env' >> /usr/local/bin/arena-env && \
    chmod +x /usr/local/bin/arena-env

# Display environment info on container start
RUN echo 'echo -e "\\n🖥️  \\033[1;34mCLI Arena Environment\\033[0m"' >> /root/.bashrc && \
    echo 'echo -e "OS: \\033[0;32mUbuntu 24.04 LTS (x86_64)\\033[0m"' >> /root/.bashrc && \
    echo 'echo -e "Container: \\033[0;36mDocker\\033[0m"' >> /root/.bashrc && \
    echo 'echo -e "Working Dir: \\033[0;33m$(pwd)\\033[0m\\n"' >> /root/.bashrc

# Set working directory
WORKDIR /app