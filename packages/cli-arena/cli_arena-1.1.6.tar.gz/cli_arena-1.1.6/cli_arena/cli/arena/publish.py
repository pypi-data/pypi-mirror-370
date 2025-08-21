"""CLI commands for publishing datasets to CLI Arena registry."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from cli_arena.registry.publisher import RegistryPublisher, DatasetMetadata


def cmd_scan_tasks(args) -> int:
    """Scan repository for tasks and display metadata."""
    repo_path = Path(args.repo_path)
    if not repo_path.exists():
        print(f"ERROR: Repository path not found: {repo_path}")
        return 1
    
    publisher = RegistryPublisher()
    tasks = publisher.scan_repository_tasks(repo_path)
    
    if not tasks:
        print("ERROR: No tasks found in repository")
        return 1
    
    print(f"SEARCH: Found {len(tasks)} tasks in {repo_path.name}:")
    print("-" * 60)
    
    for task in tasks:
        print(f"🔹 {task.task_id}")
        print(f"   Name: {task.name}")
        print(f"   Description: {task.description}")
        print(f"   Category: {task.category}")
        print(f"   Difficulty: {task.difficulty}")
        if task.tags:
            print(f"   Tags: {', '.join(task.tags)}")
        print()
    
    return 0


def cmd_create_dataset(args) -> int:
    """Create dataset metadata from repository."""
    repo_path = Path(args.repo_path)
    if not repo_path.exists():
        print(f"ERROR: Repository path not found: {repo_path}")
        return 1
    
    publisher = RegistryPublisher()
    
    try:
        dataset = publisher.create_dataset(
            repo_path=repo_path,
            name=args.name,
            version=args.version,
            description=args.description,
            repository_url=args.repository_url
        )
        
        # Validate dataset
        issues = publisher.validate_dataset(dataset, repo_path)
        if issues:
            print("⚠️  Dataset validation issues:")
            for issue in issues:
                print(f"   • {issue}")
            print()
        
        # Save dataset metadata
        output_file = Path(args.output or f"{args.name}-{args.version}-dataset.json")
        with open(output_file, 'w') as f:
            import json
            json.dump(dataset.dict(), f, indent=2, default=str)
        
        print(f"SUCCESS: Created dataset metadata: {output_file}")
        print(f"STATS: Dataset: {dataset.name} v{dataset.version}")
        print(f"NOTE: Description: {dataset.description}")
        print(f"COUNT: Tasks: {len(dataset.tasks)}")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Failed to create dataset: {e}")
        return 1


def cmd_validate_dataset(args) -> int:
    """Validate dataset for publishing."""
    repo_path = Path(args.repo_path)
    dataset_file = Path(args.dataset_file)
    
    if not repo_path.exists():
        print(f"ERROR: Repository path not found: {repo_path}")
        return 1
    
    if not dataset_file.exists():
        print(f"ERROR: Dataset file not found: {dataset_file}")
        return 1
    
    try:
        # Load dataset metadata
        import json
        with open(dataset_file, 'r') as f:
            dataset_data = json.load(f)
        
        dataset = DatasetMetadata(**dataset_data)
        
        # Validate
        publisher = RegistryPublisher()
        issues = publisher.validate_dataset(dataset, repo_path)
        
        if not issues:
            print("SUCCESS: Dataset validation passed")
            return 0
        
        print("ERROR: Dataset validation failed:")
        for issue in issues:
            print(f"   • {issue}")
        
        return 1
        
    except Exception as e:
        print(f"ERROR: Validation error: {e}")
        return 1


def cmd_package_dataset(args) -> int:
    """Package dataset for distribution."""
    repo_path = Path(args.repo_path)
    dataset_file = Path(args.dataset_file)
    
    if not repo_path.exists():
        print(f"ERROR: Repository path not found: {repo_path}")
        return 1
    
    if not dataset_file.exists():
        print(f"ERROR: Dataset file not found: {dataset_file}")
        return 1
    
    try:
        # Load dataset metadata
        import json
        with open(dataset_file, 'r') as f:
            dataset_data = json.load(f)
        
        dataset = DatasetMetadata(**dataset_data)
        
        # Package
        publisher = RegistryPublisher()
        output_path = Path(args.output) if args.output else None
        package_path = publisher.package_dataset(dataset, repo_path, output_path)
        
        print(f"SUCCESS: Packaged dataset: {package_path}")
        print(f"📦 Size: {package_path.stat().st_size / 1024 / 1024:.1f} MB")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Packaging error: {e}")
        return 1


def cmd_publish_local(args) -> int:
    """Publish dataset to local registry."""
    repo_path = Path(args.repo_path)
    dataset_file = Path(args.dataset_file)
    
    if not repo_path.exists():
        print(f"ERROR: Repository path not found: {repo_path}")
        return 1
    
    if not dataset_file.exists():
        print(f"ERROR: Dataset file not found: {dataset_file}")
        return 1
    
    try:
        # Load dataset metadata
        import json
        with open(dataset_file, 'r') as f:
            dataset_data = json.load(f)
        
        dataset = DatasetMetadata(**dataset_data)
        
        # Publish to local registry
        registry_path = Path(args.registry_path) if args.registry_path else None
        publisher = RegistryPublisher(local_registry_path=registry_path)
        
        success = publisher.publish_to_local_registry(dataset, repo_path)
        return 0 if success else 1
        
    except Exception as e:
        print(f"ERROR: Publishing error: {e}")
        return 1


def cmd_publish_remote(args) -> int:
    """Publish dataset to remote CLI Arena registry."""
    repo_path = Path(args.repo_path)
    dataset_file = Path(args.dataset_file)
    
    if not repo_path.exists():
        print(f"ERROR: Repository path not found: {repo_path}")
        return 1
    
    if not dataset_file.exists():
        print(f"ERROR: Dataset file not found: {dataset_file}")
        return 1
    
    if not args.api_key:
        print("ERROR: API key required for remote publishing")
        print("   Use --api-key or set CLI_ARENA_API_KEY environment variable")
        return 1
    
    try:
        # Load dataset metadata
        import json
        with open(dataset_file, 'r') as f:
            dataset_data = json.load(f)
        
        dataset = DatasetMetadata(**dataset_data)
        
        # Publish to remote registry
        publisher = RegistryPublisher(
            registry_url=args.registry_url,
            api_key=args.api_key
        )
        
        success = publisher.publish_to_remote_registry(dataset, repo_path)
        return 0 if success else 1
        
    except Exception as e:
        print(f"ERROR: Publishing error: {e}")
        return 1


def cmd_list_registry(args) -> int:
    """List datasets in local registry."""
    try:
        registry_path = Path(args.registry_path) if args.registry_path else None
        publisher = RegistryPublisher(local_registry_path=registry_path)
        
        datasets = publisher.list_local_datasets()
        
        if not datasets:
            print("📭 No datasets in local registry")
            return 0
        
        print(f"REGISTRY: Local Registry ({len(datasets)} datasets):")
        print("-" * 60)
        
        for dataset in datasets:
            print(f"📦 {dataset['name']} v{dataset['version']}")
            if dataset.get('description'):
                print(f"   {dataset['description']}")
            print(f"   Repository: {dataset.get('github_url', 'N/A')}")
            print(f"   Branch: {dataset.get('branch', 'N/A')}")
            print()
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Error listing registry: {e}")
        return 1


def cmd_remove_dataset(args) -> int:
    """Remove dataset from local registry."""
    try:
        registry_path = Path(args.registry_path) if args.registry_path else None
        publisher = RegistryPublisher(local_registry_path=registry_path)
        
        success = publisher.remove_from_local_registry(args.name, args.version)
        return 0 if success else 1
        
    except Exception as e:
        print(f"ERROR: Error removing dataset: {e}")
        return 1


def setup_publish_parser(parent_parser) -> argparse.ArgumentParser:
    """Set up the publish command parser."""
    parser = parent_parser.add_parser(
        'publish',
        help='Dataset publishing commands',
        description='Publish and manage CLI Arena datasets'
    )
    
    subparsers = parser.add_subparsers(dest='publish_command', help='Publishing commands')
    
    # Scan tasks command
    scan_parser = subparsers.add_parser('scan', help='Scan repository for tasks')
    scan_parser.add_argument('repo_path', help='Path to repository directory')
    scan_parser.set_defaults(func=cmd_scan_tasks)
    
    # Create dataset command
    create_parser = subparsers.add_parser('create', help='Create dataset metadata')
    create_parser.add_argument('repo_path', help='Path to repository directory')
    create_parser.add_argument('name', help='Dataset name')
    create_parser.add_argument('version', help='Dataset version (semantic versioning)')
    create_parser.add_argument('--description', help='Dataset description')
    create_parser.add_argument('--repository-url', help='Repository URL')
    create_parser.add_argument('--output', help='Output file for dataset metadata')
    create_parser.set_defaults(func=cmd_create_dataset)
    
    # Validate dataset command
    validate_parser = subparsers.add_parser('validate', help='Validate dataset')
    validate_parser.add_argument('repo_path', help='Path to repository directory')
    validate_parser.add_argument('dataset_file', help='Path to dataset metadata file')
    validate_parser.set_defaults(func=cmd_validate_dataset)
    
    # Package dataset command
    package_parser = subparsers.add_parser('package', help='Package dataset for distribution')
    package_parser.add_argument('repo_path', help='Path to repository directory')
    package_parser.add_argument('dataset_file', help='Path to dataset metadata file')
    package_parser.add_argument('--output', help='Output package path')
    package_parser.set_defaults(func=cmd_package_dataset)
    
    # Publish local command
    local_parser = subparsers.add_parser('local', help='Publish to local registry')
    local_parser.add_argument('repo_path', help='Path to repository directory')
    local_parser.add_argument('dataset_file', help='Path to dataset metadata file')
    local_parser.add_argument('--registry-path', help='Path to local registry file')
    local_parser.set_defaults(func=cmd_publish_local)
    
    # Publish remote command
    remote_parser = subparsers.add_parser('remote', help='Publish to remote registry')
    remote_parser.add_argument('repo_path', help='Path to repository directory')
    remote_parser.add_argument('dataset_file', help='Path to dataset metadata file')
    remote_parser.add_argument('--api-key', help='API key for remote registry')
    remote_parser.add_argument('--registry-url', help='Remote registry URL')
    remote_parser.set_defaults(func=cmd_publish_remote)
    
    # List registry command
    list_parser = subparsers.add_parser('list', help='List datasets in local registry')
    list_parser.add_argument('--registry-path', help='Path to local registry file')
    list_parser.set_defaults(func=cmd_list_registry)
    
    # Remove dataset command
    remove_parser = subparsers.add_parser('remove', help='Remove dataset from local registry')
    remove_parser.add_argument('name', help='Dataset name')
    remove_parser.add_argument('version', help='Dataset version')
    remove_parser.add_argument('--registry-path', help='Path to local registry file')
    remove_parser.set_defaults(func=cmd_remove_dataset)
    
    return parser