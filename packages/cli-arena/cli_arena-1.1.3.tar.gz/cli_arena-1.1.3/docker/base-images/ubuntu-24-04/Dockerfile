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

# Install coding agents globally - use latest versions
RUN npm install -g @anthropic-ai/claude-code@latest @google/gemini-cli

# Install aider
RUN curl -LsSf https://aider.chat/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install Cursor CLI (if available)
RUN curl -fsSL https://cursor.com/install -o /tmp/cursor_install.sh || true \
    && bash /tmp/cursor_install.sh || true \
    && rm -f /tmp/cursor_install.sh || true

# Create symlinks for easier access
RUN ln -sf /usr/bin/claude /usr/local/bin/claude-code
RUN ln -sf /usr/local/bin/gemini /usr/local/bin/gemini-cli

# Install OpenAI Codex CLI globally as well
RUN npm install -g @openai/codex

# Provide a global Python virtualenv to avoid PEP 668 issues in child images
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

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