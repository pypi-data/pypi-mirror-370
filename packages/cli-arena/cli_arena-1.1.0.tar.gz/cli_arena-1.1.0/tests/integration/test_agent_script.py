#!/usr/bin/env python3
import subprocess
import tempfile
import os
from pathlib import Path

# Mimic the agent's Docker execution
repo_dir = Path("repositories/sanity_test")
container_name = f"test_agent_script_{os.getpid()}"
image_tag = f"test-agent-script:{os.getpid()}"

# 1. Build Docker image
print(f"Building Docker image from {repo_dir}")
build_cmd = ["docker", "build", "-t", image_tag, str(repo_dir)]
build_proc = subprocess.run(build_cmd, capture_output=True, text=True, timeout=300)
if build_proc.returncode != 0:
    print(f"Build failed: {build_proc.stderr}")
    exit(1)

# 2. Create instruction file
with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as f:
    f.write("Create a test file in tests/unit/")
    instruction_file = f.name

# 3. Run container with exact same command as agent
run_cmd = [
    "docker", "run", "--rm",
    "-v", f"{repo_dir.absolute()}:/repo",
    "-v", f"{instruction_file}:/tmp/instruction.txt",
    "--name", container_name,
    "--workdir", "/repo",
    "--entrypoint", "/bin/bash",
    "python:3.10-slim",
    "-c", """
set -e
cd /repo
echo "Creating test file..."
mkdir -p tests/unit
echo 'def test_simple():' > tests/unit/test_agent_script.py
echo '    assert True' >> tests/unit/test_agent_script.py
echo "File created at: $(pwd)/tests/unit/test_agent_script.py"
ls -la tests/unit/
sync
sleep 2
echo "=== TASK COMPLETED ==="
sync
"""
]

print(f"Running container: {container_name}")
print(f"Command: {' '.join(run_cmd)}")
run_proc = subprocess.run(run_cmd, capture_output=True, text=True, timeout=120)

print("STDOUT:", run_proc.stdout)
print("STDERR:", run_proc.stderr)
print("Return code:", run_proc.returncode)

# Cleanup
os.unlink(instruction_file)
subprocess.run(["docker", "rmi", image_tag], capture_output=True)

# Check if file exists
test_file = repo_dir / "tests" / "unit" / "test_agent_script.py"
print(f"Checking for file: {test_file}")
print(f"File exists: {test_file.exists()}")
if test_file.exists():
    print(f"File contents: {test_file.read_text()}") 