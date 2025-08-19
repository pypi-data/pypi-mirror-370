#!/usr/bin/env bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔥 CLI Arena Verification: cli-metadata-transformer${NC}"
echo "=================================================="

# Resolve task dir
if [ -d "/repo" ]; then REPO_ROOT="/repo"; else REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; fi
TASK_DIR="$REPO_ROOT/tasks/cli-metadata-transformer"
cd "$TASK_DIR"

# Ensure test script executable and run it
chmod +x tests/test_transformer.sh || true

echo -e "${BLUE}🧪 Running task test suite...${NC}"
set +e
OUT=$(bash tests/test_transformer.sh 2>&1)
CODE=$?
set -e
echo "$OUT"

if [ $CODE -ne 0 ]; then
  echo -e "${RED}❌ Verification failed (tests reported failure)${NC}"
  exit 1
fi

echo -e "${GREEN}✅ Verification passed. Metadata transformer behaves correctly.${NC}"
exit 0
