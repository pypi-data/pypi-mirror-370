# diff-size, linter invocation, test-pass summary

import subprocess

def compute_diff_size(old_dir: str, new_dir: str) -> int:
    """Compute the size of the diff between two directories"""
    proc = subprocess.run(["diff", "-qr", old_dir, new_dir], capture_output=True, text=True)
    return len(proc.stdout.splitlines())

def lint_score(repo_path: str) -> float:
    proc = subprocess.run(["flake8", repo_path, "--exit-zero", "--statistics"], capture_output=True, text=True)
    warnings = sum(int(line.split()[0]) for line in proc.stdout.splitlines() if line)
    return max(0.0, 1.0 - warnings / 100.0)