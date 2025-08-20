"""CLI Arena Registry Publishing System

This module provides tools for publishing tasks and datasets to the CLI Arena registry,
making CLI Arena independent from Terminal-Bench registry infrastructure.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel, Field, validator

from .client import RegistryRow
from .manager import load_registry, save_registry


class TaskMetadata(BaseModel):
    """Metadata for a single task."""
    task_id: str
    name: str
    description: str
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard|expert)$")
    category: str
    tags: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    timeout_seconds: int = Field(default=300, ge=30, le=3600)
    verification_method: str = Field(default="script")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DatasetMetadata(BaseModel):
    """Metadata for a complete dataset."""
    name: str
    version: str
    description: Optional[str] = None
    cli_arena_version: str = ">=0.1.0"
    repository_url: str
    maintainer_email: Optional[str] = None
    license: str = Field(default="MIT")
    tasks: List[TaskMetadata]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('version')
    def validate_version(cls, v):
        """Validate version format (semantic versioning)."""
        import re
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
        if not re.match(pattern, v):
            raise ValueError('Version must follow semantic versioning (x.y.z)')
        return v


class RegistryPublisher:
    """Publisher for CLI Arena registry."""
    
    DEFAULT_REGISTRY_URL = "https://api.cli-arena.dev/registry"
    DEFAULT_REGISTRY_FILE = Path("outputs/registry.json")
    
    def __init__(self, 
                 registry_url: Optional[str] = None,
                 local_registry_path: Optional[Path] = None,
                 api_key: Optional[str] = None):
        self.registry_url = registry_url or self.DEFAULT_REGISTRY_URL
        self.local_registry_path = local_registry_path or self.DEFAULT_REGISTRY_FILE
        self.api_key = api_key
    
    def scan_repository_tasks(self, repo_path: Path) -> List[TaskMetadata]:
        """Scan a repository directory for tasks and extract metadata."""
        tasks = []
        tasks_dir = repo_path / "tasks"
        
        if not tasks_dir.exists():
            return tasks
        
        for task_dir in tasks_dir.iterdir():
            if not task_dir.is_dir():
                continue
            
            task_metadata = self._extract_task_metadata(task_dir)
            if task_metadata:
                tasks.append(task_metadata)
        
        return sorted(tasks, key=lambda t: t.task_id)
    
    def _extract_task_metadata(self, task_dir: Path) -> Optional[TaskMetadata]:
        """Extract metadata from a single task directory."""
        task_yaml = task_dir / "task.yaml"
        
        if not task_yaml.exists():
            # Create basic metadata from directory structure
            return TaskMetadata(
                task_id=task_dir.name,
                name=task_dir.name.replace("-", " ").replace("_", " ").title(),
                description=f"Task: {task_dir.name}",
                category="general"
            )
        
        try:
            import yaml
            with open(task_yaml, 'r') as f:
                config = yaml.safe_load(f) or {}
            
            # Extract metadata from YAML config
            return TaskMetadata(
                task_id=task_dir.name,
                name=config.get("name", task_dir.name.replace("-", " ").title()),
                description=config.get("description", f"Task: {task_dir.name}"),
                difficulty=config.get("difficulty", "medium"),
                category=config.get("category", "general"),
                tags=config.get("tags", []),
                dependencies=config.get("dependencies", []),
                timeout_seconds=config.get("timeout_seconds", 300),
                verification_method=config.get("verification_method", "script")
            )
            
        except Exception as e:
            print(f"Warning: Could not parse task.yaml for {task_dir.name}: {e}")
            return None
    
    def create_dataset(self, repo_path: Path, name: str, version: str, 
                      description: Optional[str] = None,
                      repository_url: Optional[str] = None) -> DatasetMetadata:
        """Create dataset metadata from a repository."""
        
        # Auto-detect repository URL if not provided
        if not repository_url:
            repository_url = self._detect_repository_url(repo_path)
        
        # Scan tasks
        tasks = self.scan_repository_tasks(repo_path)
        
        if not tasks:
            raise ValueError(f"No valid tasks found in {repo_path}")
        
        return DatasetMetadata(
            name=name,
            version=version,
            description=description or f"CLI Arena dataset: {name}",
            repository_url=repository_url,
            tasks=tasks
        )
    
    def _detect_repository_url(self, repo_path: Path) -> str:
        """Detect repository URL from git configuration."""
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return f"file://{repo_path.absolute()}"
    
    def validate_dataset(self, dataset: DatasetMetadata, repo_path: Path) -> List[str]:
        """Validate dataset for completeness and correctness."""
        issues = []
        
        # Check repository structure
        tasks_dir = repo_path / "tasks"
        if not tasks_dir.exists():
            issues.append("No tasks directory found")
            return issues
        
        # Validate each task
        for task in dataset.tasks:
            task_dir = tasks_dir / task.task_id
            if not task_dir.exists():
                issues.append(f"Task directory not found: {task.task_id}")
                continue
            
            # Check for required files
            required_files = ["verify.sh"]
            for req_file in required_files:
                if not (task_dir / req_file).exists():
                    issues.append(f"Missing {req_file} in task {task.task_id}")
            
            # Check for solution file (recommended but not required)
            if not (task_dir / "solution.sh").exists():
                issues.append(f"Warning: No solution.sh in task {task.task_id} (recommended)")
        
        return issues
    
    def package_dataset(self, dataset: DatasetMetadata, repo_path: Path, 
                       output_path: Optional[Path] = None) -> Path:
        """Package dataset into a distributable format."""
        
        if output_path is None:
            output_path = Path(f"{dataset.name}-{dataset.version}.zip")
        
        # Create temporary directory for packaging
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            dataset_dir = temp_path / dataset.name
            dataset_dir.mkdir()
            
            # Copy metadata
            metadata_file = dataset_dir / "dataset.json"
            with open(metadata_file, 'w') as f:
                json.dump(dataset.dict(), f, indent=2, default=str)
            
            # Copy tasks directory
            tasks_source = repo_path / "tasks"
            if tasks_source.exists():
                import shutil
                shutil.copytree(tasks_source, dataset_dir / "tasks")
            
            # Copy other relevant files
            for file_name in ["README.md", "requirements.txt", "Dockerfile", "docker-compose.yml"]:
                source_file = repo_path / file_name
                if source_file.exists():
                    import shutil
                    shutil.copy2(source_file, dataset_dir / file_name)
            
            # Create zip package
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in dataset_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_path)
                        zipf.write(file_path, arcname)
        
        return output_path
    
    def publish_to_local_registry(self, dataset: DatasetMetadata, repo_path: Path) -> bool:
        """Publish dataset to local registry file."""
        try:
            # Get current git commit info
            commit_hash = self._get_git_commit_hash(repo_path)
            branch = self._get_git_branch(repo_path)
            
            # Create registry entry
            registry_entry = RegistryRow(
                name=dataset.name,
                version=dataset.version,
                description=dataset.description,
                terminal_bench_version=">=0.1.0",  # CLI Arena compatibility
                github_url=dataset.repository_url,
                dataset_path="tasks",
                branch=branch,
                commit_hash=commit_hash,
                task_id_subset=[task.task_id for task in dataset.tasks]
            )
            
            # Load existing registry
            registry_path = self.local_registry_path
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            
            entries = load_registry(registry_path)
            
            # Update or add entry
            updated = False
            for i, entry in enumerate(entries):
                if (entry.get("name") == dataset.name and 
                    entry.get("version") == dataset.version):
                    entries[i] = registry_entry.dict()
                    updated = True
                    break
            
            if not updated:
                entries.append(registry_entry.dict())
            
            # Save registry
            save_registry(registry_path, entries)
            
            print(f"✅ Published {dataset.name} v{dataset.version} to local registry")
            return True
            
        except Exception as e:
            print(f"❌ Failed to publish to local registry: {e}")
            return False
    
    def publish_to_remote_registry(self, dataset: DatasetMetadata, repo_path: Path) -> bool:
        """Publish dataset to remote CLI Arena registry."""
        if not self.api_key:
            print("❌ API key required for remote registry publishing")
            return False
        
        try:
            # Package dataset
            package_path = self.package_dataset(dataset, repo_path)
            
            # Upload to registry
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            with open(package_path, 'rb') as f:
                files = {"dataset": f}
                data = {
                    "name": dataset.name,
                    "version": dataset.version,
                    "description": dataset.description or "",
                    "repository_url": dataset.repository_url
                }
                
                response = requests.post(
                    f"{self.registry_url}/publish",
                    headers=headers,
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    print(f"✅ Published {dataset.name} v{dataset.version} to remote registry")
                    return True
                else:
                    print(f"❌ Remote registry error: {response.status_code} {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Failed to publish to remote registry: {e}")
            return False
    
    def _get_git_commit_hash(self, repo_path: Path) -> str:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "head"
    
    def _get_git_branch(self, repo_path: Path) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip() or "main"
        except subprocess.CalledProcessError:
            return "main"
    
    def list_local_datasets(self) -> List[Dict[str, Any]]:
        """List datasets in local registry."""
        if not self.local_registry_path.exists():
            return []
        
        return load_registry(self.local_registry_path)
    
    def remove_from_local_registry(self, name: str, version: str) -> bool:
        """Remove dataset from local registry."""
        try:
            registry_path = self.local_registry_path
            entries = load_registry(registry_path)
            
            # Filter out the specified dataset
            filtered_entries = [
                entry for entry in entries
                if not (entry.get("name") == name and entry.get("version") == version)
            ]
            
            if len(filtered_entries) == len(entries):
                print(f"❌ Dataset {name} v{version} not found in registry")
                return False
            
            save_registry(registry_path, filtered_entries)
            print(f"✅ Removed {name} v{version} from local registry")
            return True
            
        except Exception as e:
            print(f"❌ Failed to remove from registry: {e}")
            return False