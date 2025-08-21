# Record every shell command + stdout/stderr

import json
from datetime import datetime
from pathlib import Path
import os
from typing import Dict, Any, Optional





class InteractionLogger:
    """
    Enhanced interaction logger for CLI-arena Claude agent.
    
    Provides session management and structured logging for agent interactions,
    command executions, and task progress.
    """
    
    def __init__(self, logs_dir: str = "logs"):
        """
        Initialize the interaction logger.
        
        Args:
            logs_dir: Directory to store log files
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def start_session(self, session_id: str, repo_name: str, task_name: str) -> None:
        """
        Start a new logging session.
        
        Args:
            session_id: Unique session identifier
            repo_name: Repository name
            task_name: Task name
        """
        session_info = {
            "session_id": session_id,
            "repo_name": repo_name,
            "task_name": task_name,
            "start_time": datetime.utcnow().isoformat(),
            "log_file": self.logs_dir / f"{session_id}.jsonl"
        }
        
        self.active_sessions[session_id] = session_info
        
        # Log session start
        self._write_log_entry(session_id, {
            "type": "session_start",
            "timestamp": session_info["start_time"],
            "session_id": session_id,
            "repo_name": repo_name,
            "task_name": task_name
        })
    
    def end_session(self, session_id: str) -> None:
        """
        End a logging session.
        
        Args:
            session_id: Session identifier to end
        """
        if session_id not in self.active_sessions:
            return
        
        end_time = datetime.utcnow().isoformat()
        
        # Log session end
        self._write_log_entry(session_id, {
            "type": "session_end",
            "timestamp": end_time,
            "session_id": session_id
        })
        
        # Remove from active sessions
        del self.active_sessions[session_id]
    
    def log_interaction(self, session_id: str, interaction_type: str, data: Any) -> None:
        """
        Log an interaction during the session.
        
        Args:
            session_id: Session identifier
            interaction_type: Type of interaction (e.g., 'claude_response', 'command_execution')
            data: Interaction data (can be string, dict, etc.)
        """
        if session_id not in self.active_sessions:
            # Auto-start session if it doesn't exist
            self.start_session(session_id, "unknown", "unknown")
        
        log_entry = {
            "type": interaction_type,
        "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "data": data
        }
        
        self._write_log_entry(session_id, log_entry)
    
    def log_command_execution(
        self, 
        session_id: str, 
        command: str, 
        stdout: str, 
        stderr: str, 
        exit_code: int,
        execution_time: float
    ) -> None:
        """
        Log command execution details.
        
        Args:
            session_id: Session identifier
            command: Command that was executed
            stdout: Standard output
            stderr: Standard error
            exit_code: Command exit code
            execution_time: Execution time in seconds
        """
        self.log_interaction(session_id, "command_execution", {
        "command": command,
        "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "execution_time": execution_time,
            "success": exit_code == 0
        })
    
    def log_claude_response(self, session_id: str, prompt: str, response: str, iteration: int = None) -> None:
        """
        Log Claude model response.
        
        Args:
            session_id: Session identifier
            prompt: Prompt sent to Claude
            response: Claude's response
            iteration: Iteration number (if applicable)
        """
        self.log_interaction(session_id, "claude_response", {
            "prompt_length": len(prompt),
            "response": response,
            "response_length": len(response),
            "iteration": iteration
        })
    
    def log_validation_result(
        self, 
        session_id: str, 
        validation_success: bool, 
        validation_message: str,
        metrics: Dict[str, Any] = None
    ) -> None:
        """
        Log validation results.
        
        Args:
            session_id: Session identifier
            validation_success: Whether validation passed
            validation_message: Validation message
            metrics: Additional validation metrics
        """
        self.log_interaction(session_id, "validation_result", {
            "success": validation_success,
            "message": validation_message,
            "metrics": metrics or {}
        })
    
    def log_error(self, session_id: str, error_type: str, error_message: str, context: Dict[str, Any] = None) -> None:
        """
        Log error information.
        
        Args:
            session_id: Session identifier
            error_type: Type of error
            error_message: Error message
            context: Additional error context
        """
        self.log_interaction(session_id, "error", {
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {}
        })
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session information or None if not found
        """
        return self.active_sessions.get(session_id)
    
    def get_log_file_path(self, session_id: str) -> Optional[Path]:
        """
        Get the log file path for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Path to log file or None if session not found
        """
        session_info = self.active_sessions.get(session_id)
        if session_info:
            return session_info["log_file"]
        
        # Check if log file exists for completed session
        log_file = self.logs_dir / f"{session_id}.jsonl"
        if log_file.exists():
            return log_file
        
        return None
    
    def _write_log_entry(self, session_id: str, entry: Dict[str, Any]) -> None:
        """
        Write a log entry to the session's log file.
        
        Args:
            session_id: Session identifier
            entry: Log entry data
        """
        log_file = self.logs_dir / f"{session_id}.jsonl"
        
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            # Fallback: write to a general error log
            error_log = self.logs_dir / "logger_errors.log"
            with open(error_log, "a", encoding="utf-8") as f:
                f.write(f"{datetime.utcnow().isoformat()} - Error writing log for {session_id}: {str(e)}\n")
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up old log files.
        
        Args:
            max_age_hours: Maximum age of log files to keep
            
        Returns:
            Number of files cleaned up
        """
        cleaned_count = 0
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        
        for log_file in self.logs_dir.glob("*.jsonl"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    cleaned_count += 1
                except Exception:
                    pass  # Ignore cleanup errors
        
        return cleaned_count