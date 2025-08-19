# DockerManager

import docker
import docker.errors
import logging
from pathlib import Path
import tempfile
import os
import tarfile
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class DockerManager:
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize Docker client with enhanced connection handling for macOS.
        """
        try:
            # First, try the default method which usually works best
            try:
                self.client = docker.from_env(timeout=30)
                self.client.ping()
                logger.info("Successfully connected to Docker using default configuration")
                return
            except Exception as e:
                logger.debug(f"Default connection failed: {str(e)}")
            
            # List of possible socket paths to try
            socket_paths = [
                # Docker Desktop socket (most common on macOS)
                os.path.expanduser('~/Library/Containers/com.docker.docker/Data/docker-cli.sock'),
                # Standard Docker socket
                '/var/run/docker.sock',
                # User-specific Docker socket
                os.path.expanduser('~/.docker/run/docker.sock'),
                # Alternative Docker Desktop paths
                os.path.expanduser('~/Library/Containers/com.docker.docker/Data/docker.raw.sock'),
                '/Users/Shared/Docker/docker.sock',
            ]
            
            # Try each socket path with different configurations
            for socket_path in socket_paths:
                if not os.path.exists(socket_path):
                    continue
                    
                # Try different client configurations
                client_configs = [
                    {'base_url': f'unix://{socket_path}', 'timeout': 30},
                    {'base_url': f'unix://{socket_path}', 'version': 'auto', 'timeout': 30},
                    {'base_url': f'unix://{socket_path}', 'version': '1.41', 'timeout': 30},
                ]
                
                for config in client_configs:
                    try:
                        self.client = docker.DockerClient(**config)
                        # Test the connection with a simple ping
                        self.client.ping()
                        logger.info(f"Successfully connected to Docker using socket: {socket_path} with config: {config}")
                        return
                    except Exception as e:
                        logger.debug(f"Failed to connect using {socket_path} with config {config}: {str(e)}")
                        continue
            
            # Try connecting via TCP (if Docker Desktop is configured for it)
            try:
                self.client = docker.DockerClient(base_url='tcp://localhost:2376', timeout=30)
                self.client.ping()
                logger.info("Successfully connected to Docker via TCP")
                return
            except Exception as e:
                logger.debug(f"TCP connection failed: {str(e)}")
            
            # Last resort: try to use docker command directly via subprocess
            try:
                import subprocess
                result = subprocess.run(['docker', 'version'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    logger.warning("Docker CLI is working but SDK connection failed. Using fallback mode.")
                    # Create a minimal client that will work for basic operations
                    self.client = self._create_fallback_client()
                    return
            except Exception as e:
                logger.debug(f"Docker CLI test failed: {str(e)}")
            
            # If all methods failed, provide detailed error information
            error_msg = self._generate_detailed_error_message(socket_paths)
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {str(e)}")
            raise RuntimeError(f"Failed to initialize Docker client: {str(e)}")
    
    def _generate_detailed_error_message(self, socket_paths):
        """Generate a detailed error message with troubleshooting info"""
        error_parts = [
            "Failed to connect to Docker daemon.",
            "\nTroubleshooting steps:",
            "1. Ensure Docker Desktop is running and fully started",
            "2. Check Docker Desktop settings -> Advanced -> 'Allow the default Docker socket to be used'",
            "3. Try restarting Docker Desktop",
            "4. Check if you can run 'docker ps' in terminal",
        ]
        
        # Add socket information
        error_parts.append("\nSocket information:")
        for path in socket_paths:
            if os.path.exists(path):
                try:
                    stat = os.stat(path)
                    error_parts.append(f"  ✓ {path} (permissions: {oct(stat.st_mode)[-3:]}, owner: {stat.st_uid})")
                except Exception:
                    error_parts.append(f"  ? {path} (cannot read stats)")
            else:
                error_parts.append(f"  ✗ {path} (does not exist)")
        
        # Add process information
        try:
            import subprocess
            result = subprocess.run(['docker', 'version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                error_parts.append("\n✓ Docker CLI is working")
            else:
                error_parts.append(f"\n✗ Docker CLI failed: {result.stderr}")
        except Exception as e:
            error_parts.append(f"\n✗ Cannot run docker command: {str(e)}")
        
        return "\n".join(error_parts)
    
    def _create_fallback_client(self):
        """Create a fallback client that uses subprocess calls for essential operations"""
        import subprocess
        import tempfile
        import json
        
        class FallbackDockerClient:
            def __init__(self):
                self.images = FallbackImageManager()
                self.containers = FallbackContainerManager()
            
            def ping(self):
                result = subprocess.run(['docker', 'version'], capture_output=True, timeout=5)
                if result.returncode != 0:
                    raise Exception("Docker is not accessible")
                return True
        
        class FallbackImageManager:
            def build(self, path, tag, **kwargs):
                """Build Docker image using subprocess"""
                cmd = ['docker', 'build', '-t', tag, str(path)]
                if kwargs.get('rm', True):
                    cmd.append('--rm')
                if kwargs.get('forcerm', False):
                    cmd.append('--force-rm')
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                if result.returncode != 0:
                    raise docker.errors.BuildError(result.stderr, build_logs=[])
                
                # Return a mock image object
                class MockImage:
                    def __init__(self, tag):
                        self.id = tag
                        self.tags = [tag]
                
                return MockImage(tag), []
            
            def get(self, image_tag):
                """Check if image exists"""
                result = subprocess.run(['docker', 'image', 'inspect', image_tag], 
                                      capture_output=True, timeout=10)
                if result.returncode != 0:
                    raise docker.errors.ImageNotFound(f"Image '{image_tag}' not found")
                return MockImage(image_tag)
            
            def list(self):
                """List all images"""
                result = subprocess.run(['docker', 'images', '--format', 'json'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    return []
                
                images = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            img_data = json.loads(line)
                            images.append(MockImage(f"{img_data['Repository']}:{img_data['Tag']}"))
                        except:
                            pass
                return images
        
        class MockImage:
            def __init__(self, tag):
                self.id = tag
                self.tags = [tag] if tag else []
        
        class FallbackContainerManager:
            def run(self, image, command=None, **kwargs):
                """Run container using subprocess"""
                cmd = ['docker', 'run']
                
                # Handle common kwargs
                if kwargs.get('detach', False):
                    cmd.append('-d')
                if kwargs.get('tty', False):
                    cmd.append('-t')
                if kwargs.get('stdin_open', False):
                    cmd.append('-i')
                if kwargs.get('remove', False):
                    cmd.append('--rm')
                
                # Working directory
                if 'working_dir' in kwargs:
                    cmd.extend(['-w', kwargs['working_dir']])
                
                # Environment variables
                if 'environment' in kwargs:
                    for key, value in kwargs['environment'].items():
                        cmd.extend(['-e', f'{key}={value}'])
                
                # Volumes
                if 'volumes' in kwargs:
                    for host_path, container_config in kwargs['volumes'].items():
                        if isinstance(container_config, dict):
                            container_path = container_config['bind']
                            cmd.extend(['-v', f'{host_path}:{container_path}'])
                
                cmd.append(image)
                if command:
                    if isinstance(command, list):
                        cmd.extend(command)
                    else:
                        cmd.extend(['sh', '-c', command])
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    raise docker.errors.ContainerError(
                        container=None, 
                        exit_status=result.returncode, 
                        command=command,
                        image=image, 
                        stderr=result.stderr.encode()
                    )
                
                if kwargs.get('detach', False):
                    container_id = result.stdout.strip()
                    return FallbackContainer(container_id)
                else:
                    return result.stdout.encode()
            
            def get(self, container_id):
                """Get container by ID"""
                return FallbackContainer(container_id)
        
        class FallbackContainer:
            def __init__(self, container_id):
                self.id = container_id
            
            def exec_run(self, cmd, **kwargs):
                """Execute command in container"""
                exec_cmd = ['docker', 'exec']
                
                if kwargs.get('workdir'):
                    exec_cmd.extend(['-w', kwargs['workdir']])
                
                if kwargs.get('environment'):
                    for key, value in kwargs['environment'].items():
                        exec_cmd.extend(['-e', f'{key}={value}'])
                
                if kwargs.get('user'):
                    exec_cmd.extend(['-u', kwargs['user']])
                
                exec_cmd.append(self.id)
                if isinstance(cmd, list):
                    exec_cmd.extend(cmd)
                else:
                    exec_cmd.extend(['sh', '-c', cmd])
                
                result = subprocess.run(exec_cmd, capture_output=True, text=True, timeout=30)
                
                # Return format similar to docker SDK
                class ExecResult:
                    def __init__(self, exit_code, output):
                        self.exit_code = exit_code
                        if kwargs.get('demux', False):
                            # Return tuple for demux
                            self.output = (output.encode() if output else b'', b'')
                        else:
                            self.output = output.encode() if output else b''
                
                return ExecResult(result.returncode, result.stdout)
            
            def stop(self, timeout=10):
                """Stop container"""
                try:
                    subprocess.run(['docker', 'stop', self.id], timeout=timeout, check=False)
                except subprocess.TimeoutExpired:
                    # Force kill if stop times out
                    subprocess.run(['docker', 'kill', self.id], timeout=5, check=False)
            
            def remove(self):
                """Remove container"""
                subprocess.run(['docker', 'rm', self.id], timeout=10)
            
            def put_archive(self, path, data):
                """Put archive in container (simplified)"""
                # This is a complex operation, for now just raise not implemented
                raise NotImplementedError("put_archive not implemented in fallback client")
            
            def get_archive(self, path):
                """Get archive from container (simplified)"""
                # This is a complex operation, for now just raise not implemented
                raise NotImplementedError("get_archive not implemented in fallback client")
        
        return FallbackDockerClient()
    
    def build_image(self, dockerfile_dir: Path, tag: str) -> str:
        """Build a Docker image from a Dockerfile"""
        if not (dockerfile_dir / "Dockerfile").exists():
            raise FileNotFoundError(f"Dockerfile not found in {dockerfile_dir}")
            
        try:
            logger.info(f"Building Docker image with tag: {tag}")
            image, build_logs = self.client.images.build(
                path=str(dockerfile_dir),
                tag=tag,
                rm=True,
                forcerm=True
            )
            return image.id
        except docker.errors.BuildError as e:
            logger.error(f"Failed to build Docker image: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error building Docker image: {str(e)}")
            raise
    
    def run_container(
        self, 
        image_tag: str, 
        command: str, 
        workdir: str = "/workspace",
        volumes: Optional[Dict[str, Dict[str, str]]] = None,
        max_attempts: int = 5,
        required_successes: int = 1
    ) -> Dict[str, str]:
        """Run a command in a container with retry logic and pass@k functionality.
        
        Args:
            image_tag: Docker image tag to use
            command: Command(s) to run (can be multi-line)
            workdir: Working directory in the container
            volumes: Volume mappings for the container
            max_attempts: Maximum number of attempts to run the commands (default: 5)
            required_successes: Number of successful runs required (pass@k) (default: 1)
            
        Returns:
            Dict containing stdout, stderr, exit_code, and attempt information
        """
        try:
            logger.info(f"Running command in container with max_attempts={max_attempts}, required_successes={required_successes}: {command}")
            
            # Split commands by newlines and filter out empty lines
            commands = [cmd.strip() for cmd in command.split('\n') if cmd.strip()]
            
            # If no valid commands, return early
            if not commands:
                return {
                    "stdout": "", 
                    "stderr": "No commands provided", 
                    "exit_code": 1,
                    "attempts": 0,
                    "successful_attempts": 0,
                    "max_attempts_reached": False
                }
            
            # Track results across attempts
            all_attempts = []
            successful_attempts = 0
            
            # Only show attempt info if we're actually making multiple attempts
            for attempt in range(1, max_attempts + 1):
                if max_attempts > 1:
                    logger.info(f"Attempt {attempt}/{max_attempts}")
                attempt_stdout = []
                attempt_stderr = []
                attempt_success = True
                
                # Run each command in sequence
                for cmd in commands:
                    try:
                        # Run the command with shell=True to handle shell syntax
                        result = self.client.containers.run(
                            image_tag,
                            f'/bin/sh -c "{cmd}"',
                            working_dir=workdir,
                            volumes=volumes or {},
                            remove=True,
                            stdout=True,
                            stderr=True
                        )
                        
                        # Command succeeded
                        output = result.decode('utf-8', errors='replace')
                        attempt_stdout.append(output)
                        
                    except docker.errors.ContainerError as e:
                        # Command failed, capture the error
                        error_output = e.stderr.decode('utf-8', errors='replace') if e.stderr else str(e)
                        attempt_stderr.append(f"Command failed with exit code {getattr(e, 'exit_status', 'unknown')}: {error_output}")
                        attempt_success = False
                        break
                        
                    except Exception as e:
                        attempt_stderr.append(f"Unexpected error: {str(e)}")
                        attempt_success = False
                        break
                
                # Record attempt results
                attempt_result = {
                    "attempt_number": attempt,
                    "stdout": '\n'.join(attempt_stdout),
                    "stderr": '\n'.join(attempt_stderr),
                    "success": attempt_success
                }
                all_attempts.append(attempt_result)
                
                # Update success count
                if attempt_success:
                    successful_attempts += 1
                    logger.info(f"Attempt {attempt} succeeded ({successful_attempts}/{required_successes} required)")
                    
                    # Check if we have enough successful attempts
                    if successful_attempts >= required_successes:
                        if max_attempts > 1 or required_successes > 1:
                            logger.info(f"Reached required {required_successes} successful attempts")
                        break
                else:
                    if max_attempts > 1 or required_successes > 1:
                        logger.warning(f"Attempt {attempt} failed: {attempt_result['stderr']}")
                    
                    # If we can't possibly reach required_successes, exit early
                    remaining_attempts = max_attempts - attempt
                    if (successful_attempts + remaining_attempts) < required_successes and (max_attempts > 1 or required_successes > 1):
                        logger.warning("Not enough remaining attempts to reach required_successes")
                        break
            
            # Determine final status
            max_attempts_reached = (attempt >= max_attempts)
            overall_success = (successful_attempts >= required_successes)
            
            # Combine results from all attempts
            combined_stdout = '\n'.join([a['stdout'] for a in all_attempts if a['stdout']])
            combined_stderr = '\n'.join([a['stderr'] for a in all_attempts if a['stderr']])
            
            return {
                "stdout": combined_stdout,
                "stderr": combined_stderr,
                "exit_code": 0 if overall_success else 1,
                "attempts": len(all_attempts),
                "successful_attempts": successful_attempts,
                "required_successes": required_successes,
                "max_attempts_reached": max_attempts_reached,
                "all_attempts": all_attempts
            }
            
        except docker.errors.ContainerError as e:
            # Handle container error with proper attribute access
            error_info = {
                "success": False,
                "error": f"Container failed with exit code {getattr(e, 'exit_status', 'unknown')}"
            }
            # Safely get stdout/stderr if they exist
            if hasattr(e, 'container'):
                try:
                    logs = e.container.logs()
                    error_info["logs"] = logs.decode('utf-8', errors='replace')
                except Exception as log_err:
                    error_info["logs_error"] = str(log_err)
            return error_info
        
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1
            }
    
    def copy_to_container(self, container_id: str, src_path: Path, dest_path: str) -> bool:
        """Copy files to a running container"""
        if not src_path.exists():
            logger.error(f"Source path does not exist: {src_path}")
            return False
            
        try:
            container = self.client.containers.get(container_id)
            with tempfile.NamedTemporaryFile(delete=False) as f:
                with tarfile.open(fileobj=f, mode='w') as tar:
                    tar.add(str(src_path), arcname=os.path.basename(dest_path))
            
                with open(f.name, 'rb') as f:
                    container.put_archive(os.path.dirname(dest_path), f.read())
            
            return True
        except Exception as e:
            logger.error(f"Failed to copy to container: {str(e)}")
            return False
        finally:
            if 'f' in locals() and os.path.exists(f.name):
                os.unlink(f.name)