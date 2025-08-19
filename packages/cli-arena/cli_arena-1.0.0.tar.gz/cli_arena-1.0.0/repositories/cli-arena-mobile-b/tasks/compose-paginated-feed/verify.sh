#!/usr/bin/env bash
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; BLUE='\033[0;34m'; NC='\033[0m'
echo -e "${BLUE}🔥 CLI Arena Verification: compose-paginated-feed${NC}"

if [ -d "/repo" ]; then REPO_ROOT="/repo"; else REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; fi
TASK_DIR="$REPO_ROOT/tasks/compose-paginated-feed"
APP_MAIN_DIR="$REPO_ROOT/app/src/main/java/com/project/saturn"
APP_TEST_DIR="$REPO_ROOT/app/src/test/java/com/project/saturn"

MISSING=()
if ! find "$APP_MAIN_DIR" -name 'FeedViewModel.kt' | grep -q .; then MISSING+=("FeedViewModel.kt"); fi
if ! find "$APP_MAIN_DIR" -name 'FeedScreen.kt' | grep -q .; then MISSING+=("FeedScreen.kt"); fi
if [ ${#MISSING[@]} -gt 0 ]; then echo -e "${RED}❌ Missing:${NC} ${MISSING[*]}"; exit 1; fi
echo -e "${GREEN}✅ Required source files present${NC}"

cd "$REPO_ROOT"; chmod +x ./gradlew || true
mkdir -p "$APP_TEST_DIR"
cp -f "$TASK_DIR/tests"/*.kt "$APP_TEST_DIR/" 2>/dev/null || true

echo -e "${BLUE}🧪 Running Gradle unit tests...${NC}"
set +e
./gradlew test --no-daemon --stacktrace > /tmp/gradle_test_output.txt 2>&1
CODE=$?
set -e
cat /tmp/gradle_test_output.txt || true

if [ $CODE -ne 0 ]; then echo -e "${RED}❌ Gradle tests failed${NC}"; exit 1; fi
echo -e "${GREEN}✅ Tests passed. compose-paginated-feed implemented correctly.${NC}"
exit 0
