#!/bin/bash

echo "🔑 Setting up Claude Code API Key"
echo "=================================="

# Check if API key is provided as argument
if [ -n "$1" ]; then
    API_KEY="$1"
    echo "Using provided API key (first 20 chars): ${API_KEY:0:20}..."
else
    echo "Please provide your Anthropic API key as an argument:"
    echo "Usage: $0 'sk-ant-api03-...'"
    echo ""
    echo "To get your API key:"
    echo "1. Go to https://console.anthropic.com/"
    echo "2. Navigate to API Keys"
    echo "3. Copy your API key"
    echo "4. Run: $0 'your-api-key-here'"
    exit 1
fi

# Validate API key format
if [[ ! "$API_KEY" =~ ^sk-ant-api03-[A-Za-z0-9_-]+$ ]]; then
    echo "❌ Invalid API key format. Should start with 'sk-ant-api03-'"
    exit 1
fi

# Create ~/.claude directory if it doesn't exist
mkdir -p ~/.claude

# Update the API key file
echo "echo \"$API_KEY\"" > ~/.claude/anthropic_key.sh
chmod +x ~/.claude/anthropic_key.sh

# Update settings.json
cat > ~/.claude/settings.json << EOF
{
  "apiKeyHelper": "~/.claude/anthropic_key.sh"
}
EOF

echo "✅ API key setup complete!"
echo "📁 Files created:"
echo "   ~/.claude/anthropic_key.sh"
echo "   ~/.claude/settings.json"
echo ""
echo "🔍 Testing API key..."
if ~/.claude/anthropic_key.sh | grep -q "sk-ant-api03-"; then
    echo "✅ API key is properly configured!"
else
    echo "❌ API key test failed"
    exit 1
fi

echo ""
echo "🚀 You can now test Claude Code with:"
echo "   python3 test_cli_arena.py" 