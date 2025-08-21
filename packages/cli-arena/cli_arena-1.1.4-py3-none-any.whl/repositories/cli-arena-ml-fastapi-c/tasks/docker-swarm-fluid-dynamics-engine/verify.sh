#!/usr/bin/env bash
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
echo -e "${BLUE}🔍 Verifying Docker Swarm Fluid Dynamics Engine...${NC}"

if [ -d "/repo" ]; then REPO_DIR="/repo"; else REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; fi
SRC_DIR="$REPO_DIR/src"; TASK_DIR="$REPO_DIR/tasks/docker-swarm-fluid-dynamics-engine"
MOD="docker_swarm_fluid_dynamics_engine"

total=0; pass=0
check(){ total=$((total+1)); if eval "$2"; then echo -e "${GREEN}✅ $1${NC}"; pass=$((pass+1)); else echo -e "${RED}❌ $1${NC}"; return 1; fi }
check_out(){ total=$((total+1)); out=$(eval "$2" 2>&1 || true); if echo "$out" | grep -q "$3"; then echo -e "${GREEN}✅ $1${NC}"; pass=$((pass+1)); else echo -e "${RED}❌ $1${NC}"; echo "$out"; return 1; fi }

check "task test present" "test -f '$TASK_DIR/test_docker_swarm_fluid_dynamics_engine.py'"
if [ -f "$REPO_DIR/requirements.txt" ]; then python3 -m pip install -r "$REPO_DIR/requirements.txt" >/dev/null 2>&1 || true; fi

check "module files present" "test -f '$SRC_DIR/$MOD/cli.py' && test -f '$SRC_DIR/$MOD/models.py'"
check "module importable" "cd '$SRC_DIR' && python3 -c 'import $MOD.cli; import $MOD.models'"
check_out "CLI help works" "cd '$SRC_DIR' && python3 -m $MOD.cli --help" "Usage\|usage:"

# Minimal functional CLI flow
TMP_DIR="$TASK_DIR/.tmp_cli"; rm -rf "$TMP_DIR" && mkdir -p "$TMP_DIR"
cat > "$TMP_DIR/input.json" << 'EOF'
{"param":1.0, "viscosity":0.89, "velocity":2.5, "geometry":"pipe", "boundary":"no-slip"}
EOF
check_out "run starts simulation" "cd '$SRC_DIR' && python3 -m $MOD.cli run --input '$TMP_DIR/input.json'" "Simulation started. Job ID:"
JOB_ID=$(cd "$SRC_DIR" && python3 -m $MOD.cli run --input "$TMP_DIR/input.json" | awk -F 'Job ID:' '{print $2}' | xargs || true)
check_out "status returns for job" "cd '$SRC_DIR' && python3 -m $MOD.cli status --job-id '${JOB_ID:-job1}'" "Status for job"
check_out "scale engine" "cd '$SRC_DIR' && python3 -m $MOD.cli scale --replicas 2" "Engine scaled to 2 replicas"

check "pytest passes" "cd '$REPO_DIR' && python3 -m pytest '$TASK_DIR' -q --tb=no >/dev/null 2>&1"

echo -e "\n${BLUE}📊 Summary${NC}"
echo "Total: $total  Passed: $pass  Failed: $((total-pass))"
if [ "$pass" -eq "$total" ]; then echo -e "${GREEN}🎉 All checks passed!${NC}"; exit 0; else echo -e "${RED}❌ Some checks failed.${NC}"; exit 1; fi
