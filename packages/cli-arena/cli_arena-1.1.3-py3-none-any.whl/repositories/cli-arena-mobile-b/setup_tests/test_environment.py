#!/usr/bin/env python3
"""
Setup Tests for CLI Arena Mobile Repository

These tests verify that the testing environment is properly configured
and that basic functionality works before agent evaluation begins.

These are NOT agent task tests - those are in tasks/*/tests/
"""

import pytest
import subprocess
import sys
import os
from pathlib import Path


def test_python_environment():
    """Test that Python environment is working correctly."""
    assert sys.version_info >= (3, 10), "Python 3.10+ required"


def test_repository_structure():
    """Test that repository has expected structure."""
    repo_root = Path(__file__).parent.parent
    
    # Check for required files
    assert (repo_root / "tasks").exists(), "tasks directory should exist"
    
    # Check that tasks directory has content
    tasks_dir = repo_root / "tasks"
    task_dirs = [d for d in tasks_dir.iterdir() if d.is_dir()]
    assert len(task_dirs) > 0, "Should have at least one task"


def test_basic_arithmetic():
    """Test that basic arithmetic works (sanity check)."""
    assert 2 + 2 == 4, "Basic arithmetic should work"
    assert 10 * 5 == 50, "Multiplication should work"
    assert 100 / 4 == 25, "Division should work"


def test_file_operations():
    """Test that file operations work correctly."""
    test_file = Path("test_setup_tmp.txt")
    try:
        # Test file creation
        test_file.write_text("test content")
        assert test_file.exists(), "File should be created"
        assert test_file.read_text() == "test content", "File content should match"
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


def test_mobile_environment():
    """Test that mobile development environment is accessible."""
    # Check for common mobile development tools
    tools_to_check = ["java", "javac", "adb"]
    
    for tool in tools_to_check:
        try:
            result = subprocess.run([tool, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {tool} is available")
        except FileNotFoundError:
            print(f"⚠️ {tool} not available (this is normal in some environments)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 