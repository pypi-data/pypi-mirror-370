#!/usr/bin/env bash
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
echo -e "${BLUE}🔍 Verifying Sanskrit-to-Math Translator Cloud Function...${NC}"

if [ -d "/repo" ]; then REPO_DIR="/repo"; else REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; fi
SRC_DIR="$REPO_DIR/src"; TASK_DIR="$REPO_DIR/tasks/sanskrit-to-math-translator-cloud-function"
MOD="sanskrit_to_math_translator_cloud_function"

total=0; pass=0
check(){ total=$((total+1)); if eval "$2"; then echo -e "${GREEN}✅ $1${NC}"; pass=$((pass+1)); else echo -e "${RED}❌ $1${NC}"; return 1; fi }
check_out(){ total=$((total+1)); out=$(eval "$2" 2>&1 || true); if echo "$out" | grep -q "$3"; then echo -e "${GREEN}✅ $1${NC}"; pass=$((pass+1)); else echo -e "${RED}❌ $1${NC}"; echo "$out"; return 1; fi }

check "task test present" "test -f '$TASK_DIR/test_sanskrit_to_math_translator_cloud_function.py'"
if [ -f "$REPO_DIR/requirements.txt" ]; then python3 -m pip install -r "$REPO_DIR/requirements.txt" >/dev/null 2>&1 || true; fi

check "module files present" "test -f '$SRC_DIR/$MOD/cli.py' && test -f '$SRC_DIR/$MOD/models.py'"
check "module importable" "cd '$SRC_DIR' && python3 -c 'import $MOD.cli; import $MOD.models'"
check_out "CLI help works" "cd '$SRC_DIR' && python3 -m $MOD.cli --help" "Usage\|usage:"

# Minimal functional CLI flow
check_out "deploy to aws" "cd '$SRC_DIR' && python3 -m $MOD.cli deploy --provider aws" "Function deployed to"
check_out "status shows deployed" "cd '$SRC_DIR' && python3 -m $MOD.cli status --provider aws" "Status for\|deployed"
check_out "translate returns math" "cd '$SRC_DIR' && python3 -m $MOD.cli translate --sanskrit 'त्रयः गुणाः'" "3\|translation\|math"

check "pytest passes" "cd '$REPO_DIR' && python3 -m pytest '$TASK_DIR' -q --tb=no >/dev/null 2>&1"

echo -e "\n${BLUE}📊 Summary${NC}"
echo "Total: $total  Passed: $pass  Failed: $((total-pass))"
if [ "$pass" -eq "$total" ]; then echo -e "${GREEN}🎉 All checks passed!${NC}"; exit 0; else echo -e "${RED}❌ Some checks failed.${NC}"; exit 1; fi
