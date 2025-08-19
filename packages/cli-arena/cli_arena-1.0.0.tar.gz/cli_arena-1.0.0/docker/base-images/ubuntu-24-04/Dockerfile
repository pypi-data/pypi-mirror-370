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

# Set working directory
WORKDIR /app