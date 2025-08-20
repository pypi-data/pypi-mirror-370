"""
CLI Arena Session Recording System

Comprehensive terminal session recording and replay system that captures agent
interactions, integrates with the harness, and provides web-based playback.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dataclasses import dataclass, asdict


@dataclass
class RecordingMetadata:
    """Metadata for a terminal session recording."""
    agent_name: str
    repository: str
    task_id: str
    recording_id: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    agent_success: Optional[bool] = None
    verify_success: Optional[bool] = None
    exit_code: Optional[int] = None
    file_path: str = ""
    file_size: Optional[int] = None
    format_version: str = "2"
    cli_arena_version: str = "1.0.0"


class SessionRecorder:
    """Enhanced session recorder for CLI Arena with harness integration."""
    
    def __init__(self, 
                 base_output_dir: Path = Path("outputs/recordings"),
                 enable_recording: bool = True,
                 compress_recordings: bool = True):
        self.base_output_dir = base_output_dir
        self.enable_recording = enable_recording
        self.compress_recordings = compress_recordings
        self.current_recording: Optional[RecordingMetadata] = None
        
        # Ensure output directory exists
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
    
    def start_recording(self, 
                       agent_name: str,
                       repository: str, 
                       task_id: str,
                       recording_id: Optional[str] = None) -> Optional[RecordingMetadata]:
        """Start a new terminal session recording."""
        if not self.enable_recording:
            return None
        
        if recording_id is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            recording_id = f"{agent_name}_{repository}_{task_id}_{timestamp}"
        
        # Create recording directory structure
        recording_dir = self.base_output_dir / repository / task_id
        recording_dir.mkdir(parents=True, exist_ok=True)
        
        # Define recording file path
        recording_file = recording_dir / f"{recording_id}.cast"
        
        # Create metadata
        self.current_recording = RecordingMetadata(
            agent_name=agent_name,
            repository=repository,
            task_id=task_id,
            recording_id=recording_id,
            start_time=datetime.now(timezone.utc).isoformat(),
            file_path=str(recording_file)
        )
        
        return self.current_recording
    
    def stop_recording(self,
                      agent_success: Optional[bool] = None,
                      verify_success: Optional[bool] = None,
                      exit_code: Optional[int] = None) -> Optional[RecordingMetadata]:
        """Stop the current recording and finalize metadata."""
        if not self.current_recording:
            return None
        
        recording = self.current_recording
        recording.end_time = datetime.now(timezone.utc).isoformat()
        recording.agent_success = agent_success
        recording.verify_success = verify_success
        recording.exit_code = exit_code
        
        # Calculate duration
        if recording.start_time and recording.end_time:
            start = datetime.fromisoformat(recording.start_time)
            end = datetime.fromisoformat(recording.end_time)
            recording.duration_seconds = (end - start).total_seconds()
        
        # Get file size if file exists
        recording_path = Path(recording.file_path)
        if recording_path.exists():
            recording.file_size = recording_path.stat().st_size
            
            # Compress if enabled
            if self.compress_recordings and recording.file_size > 1024:  # Only compress if > 1KB
                self._compress_recording(recording_path)
        
        # Save metadata
        self._save_metadata(recording)
        
        self.current_recording = None
        return recording
    
    def _compress_recording(self, recording_path: Path) -> bool:
        """Compress recording using gzip."""
        try:
            import gzip
            import shutil
            
            compressed_path = recording_path.with_suffix('.cast.gz')
            
            with open(recording_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Update file path in current recording
            if self.current_recording:
                self.current_recording.file_path = str(compressed_path)
            
            # Remove original file
            recording_path.unlink()
            
            return True
        except Exception as e:
            print(f"Warning: Failed to compress recording {recording_path}: {e}")
            return False
    
    def _save_metadata(self, recording: RecordingMetadata):
        """Save recording metadata to JSON file."""
        recording_path = Path(recording.file_path)
        metadata_path = recording_path.with_suffix('.json')
        
        try:
            with open(metadata_path, 'w') as f:
                json.dump(asdict(recording), f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save recording metadata: {e}")
    
    def list_recordings(self, 
                       repository: Optional[str] = None,
                       task_id: Optional[str] = None,
                       agent_name: Optional[str] = None) -> List[RecordingMetadata]:
        """List available recordings with optional filtering."""
        recordings = []
        
        # Find all metadata files
        if repository and task_id:
            search_dir = self.base_output_dir / repository / task_id
            pattern = "*.json"
        elif repository:
            search_dir = self.base_output_dir / repository
            pattern = "*/*.json"
        else:
            search_dir = self.base_output_dir
            pattern = "*/*/*.json"
        
        if not search_dir.exists():
            return recordings
        
        for metadata_file in search_dir.glob(pattern):
            try:
                with open(metadata_file) as f:
                    data = json.load(f)
                
                recording = RecordingMetadata(**data)
                
                # Apply filters
                if agent_name and recording.agent_name != agent_name:
                    continue
                
                recordings.append(recording)
                
            except Exception as e:
                print(f"Warning: Failed to load recording metadata {metadata_file}: {e}")
        
        # Sort by start time (newest first)
        recordings.sort(key=lambda r: r.start_time, reverse=True)
        return recordings
    
    def get_recording(self, recording_id: str) -> Optional[RecordingMetadata]:
        """Get a specific recording by ID."""
        recordings = self.list_recordings()
        for recording in recordings:
            if recording.recording_id == recording_id:
                return recording
        return None
    
    def cleanup_old_recordings(self, keep_days: int = 30) -> int:
        """Clean up recordings older than specified days."""
        if keep_days <= 0:
            return 0
        
        cutoff_time = time.time() - (keep_days * 24 * 60 * 60)
        cleaned_count = 0
        
        for recording_file in self.base_output_dir.glob("*/*/*.cast*"):
            try:
                if recording_file.stat().st_mtime < cutoff_time:
                    recording_file.unlink()
                    
                    # Also remove metadata file
                    metadata_file = recording_file.with_suffix('.json')
                    if metadata_file.exists():
                        metadata_file.unlink()
                    
                    cleaned_count += 1
            except Exception as e:
                print(f"Warning: Failed to cleanup recording {recording_file}: {e}")
        
        return cleaned_count


class AsciinemaIntegration:
    """Integration with asciinema for recording and playback."""
    
    @staticmethod
    def is_asciinema_available() -> bool:
        """Check if asciinema is available."""
        try:
            subprocess.run(['asciinema', '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    @staticmethod
    def start_recording_process(output_path: Path, 
                               command: Optional[str] = None,
                               title: Optional[str] = None,
                               env: Optional[Dict[str, str]] = None) -> subprocess.Popen:
        """Start asciinema recording process."""
        cmd = ['asciinema', 'rec', '--stdin', str(output_path)]
        
        if title:
            cmd.extend(['--title', title])
        
        if command:
            cmd.extend(['--command', command])
        
        # Merge environment variables
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
        
        return subprocess.Popen(cmd, env=full_env, stdin=subprocess.PIPE)
    
    @staticmethod
    def get_recording_info(recording_path: Path) -> Dict[str, Any]:
        """Get information from asciinema recording."""
        if not recording_path.exists():
            return {}
        
        try:
            with open(recording_path) as f:
                # First line should be header
                first_line = f.readline().strip()
                if first_line.startswith('{'):
                    header = json.loads(first_line)
                    return header
        except Exception as e:
            print(f"Warning: Failed to parse recording header: {e}")
        
        return {}
    
    @staticmethod
    def convert_to_gif(recording_path: Path, 
                      output_path: Optional[Path] = None,
                      width: int = 80, 
                      height: int = 24) -> Optional[Path]:
        """Convert asciinema recording to animated GIF."""
        if output_path is None:
            output_path = recording_path.with_suffix('.gif')
        
        try:
            # Check if asciicast2gif is available
            subprocess.run(['asciicast2gif', '--help'], 
                         capture_output=True, check=True)
            
            cmd = [
                'asciicast2gif',
                '-w', str(width),
                '-h', str(height),
                str(recording_path),
                str(output_path)
            ]
            
            subprocess.run(cmd, check=True)
            return output_path
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: asciicast2gif not available for GIF conversion")
            return None


def create_recording_index(recordings_dir: Path) -> Dict[str, Any]:
    """Create an index of all recordings for web interface."""
    recorder = SessionRecorder(recordings_dir)
    recordings = recorder.list_recordings()
    
    # Group by repository and task
    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_recordings": len(recordings),
        "repositories": {},
        "agents": {},
        "recordings": []
    }
    
    for recording in recordings:
        # Add to repository index
        if recording.repository not in index["repositories"]:
            index["repositories"][recording.repository] = {
                "tasks": {},
                "total_recordings": 0
            }
        
        repo_data = index["repositories"][recording.repository]
        repo_data["total_recordings"] += 1
        
        if recording.task_id not in repo_data["tasks"]:
            repo_data["tasks"][recording.task_id] = []
        
        repo_data["tasks"][recording.task_id].append({
            "recording_id": recording.recording_id,
            "agent_name": recording.agent_name,
            "start_time": recording.start_time,
            "duration_seconds": recording.duration_seconds,
            "agent_success": recording.agent_success,
            "verify_success": recording.verify_success
        })
        
        # Add to agent index
        if recording.agent_name not in index["agents"]:
            index["agents"][recording.agent_name] = 0
        index["agents"][recording.agent_name] += 1
        
        # Add to recordings list
        index["recordings"].append(asdict(recording))
    
    return index