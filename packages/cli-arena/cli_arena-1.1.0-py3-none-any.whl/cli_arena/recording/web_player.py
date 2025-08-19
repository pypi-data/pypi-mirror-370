"""
Web-based Terminal Recording Player

Interactive web player for asciinema recordings integrated with CLI Arena leaderboard.
"""

from __future__ import annotations

import json
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional

from .session_recorder import SessionRecorder, create_recording_index


ASCIINEMA_PLAYER_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CLI Arena - Terminal Recording: {recording_title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/asciinema-player@3.6.4/dist/bundle/asciinema-player.css" />
  <style>
    :root {{
      --primary-color: #3b82f6;
      --success-color: #10b981;
      --warning-color: #f59e0b;
      --error-color: #ef4444;
      --gray-50: #f9fafb;
      --gray-100: #f3f4f6;
      --gray-200: #e5e7eb;
      --gray-300: #d1d5db;
      --gray-500: #6b7280;
      --gray-700: #374151;
      --gray-900: #111827;
    }}
    
    body {{ 
      font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
      margin: 0;
      padding: 0;
      background: var(--gray-50);
      color: var(--gray-900);
      line-height: 1.6;
    }}
    
    .header {{
      background: white;
      border-bottom: 1px solid var(--gray-200);
      padding: 1rem 2rem;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }}
    
    .header h1 {{
      margin: 0;
      font-size: 1.8rem;
      font-weight: 600;
      color: var(--primary-color);
    }}
    
    .breadcrumb {{
      color: var(--gray-500);
      font-size: 0.9rem;
      margin-top: 0.25rem;
    }}
    
    .breadcrumb a {{
      color: var(--primary-color);
      text-decoration: none;
    }}
    
    .breadcrumb a:hover {{
      text-decoration: underline;
    }}
    
    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem;
    }}
    
    .recording-info {{
      background: white;
      border-radius: 8px;
      border: 1px solid var(--gray-200);
      padding: 1.5rem;
      margin-bottom: 2rem;
    }}
    
    .info-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
    }}
    
    .info-item {{
      text-align: center;
    }}
    
    .info-value {{
      font-size: 1.5rem;
      font-weight: 600;
      color: var(--primary-color);
      margin-bottom: 0.25rem;
    }}
    
    .info-label {{
      color: var(--gray-500);
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    
    .status-badge {{
      display: inline-block;
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.875rem;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    
    .status-success {{
      background: var(--success-color);
      color: white;
    }}
    
    .status-failure {{
      background: var(--error-color);
      color: white;
    }}
    
    .status-unknown {{
      background: var(--gray-300);
      color: var(--gray-700);
    }}
    
    .player-container {{
      background: white;
      border-radius: 8px;
      border: 1px solid var(--gray-200);
      padding: 2rem;
      margin-bottom: 2rem;
    }}
    
    .player-container h2 {{
      margin: 0 0 1.5rem 0;
      font-size: 1.5rem;
      font-weight: 600;
    }}
    
    #player {{
      width: 100%;
      max-width: 100%;
    }}
    
    .controls {{
      margin-top: 1rem;
      display: flex;
      gap: 1rem;
      align-items: center;
      flex-wrap: wrap;
    }}
    
    .control-button {{
      background: var(--primary-color);
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 500;
      transition: background 0.2s;
    }}
    
    .control-button:hover {{
      background: #2563eb;
    }}
    
    .control-button:disabled {{
      background: var(--gray-300);
      cursor: not-allowed;
    }}
    
    .speed-controls {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    
    .speed-button {{
      background: var(--gray-200);
      color: var(--gray-700);
      border: none;
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.875rem;
    }}
    
    .speed-button.active {{
      background: var(--primary-color);
      color: white;
    }}
    
    .download-section {{
      background: white;
      border-radius: 8px;
      border: 1px solid var(--gray-200);
      padding: 1.5rem;
    }}
    
    .download-section h3 {{
      margin: 0 0 1rem 0;
      font-size: 1.25rem;
      font-weight: 600;
    }}
    
    .download-links {{
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
    }}
    
    .download-link {{
      background: var(--gray-100);
      color: var(--gray-700);
      padding: 0.5rem 1rem;
      border-radius: 6px;
      text-decoration: none;
      font-weight: 500;
      transition: background 0.2s;
    }}
    
    .download-link:hover {{
      background: var(--gray-200);
    }}
    
    .error-message {{
      background: var(--error-color);
      color: white;
      padding: 1rem;
      border-radius: 6px;
      margin-bottom: 2rem;
    }}
    
    @media (max-width: 768px) {{
      .container {{ padding: 1rem; }}
      .info-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .controls {{ justify-content: center; }}
      .download-links {{ justify-content: center; }}
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>Terminal Recording Player</h1>
    <div class="breadcrumb">
      <a href="../../../leaderboard/">← Back to Leaderboard</a> / 
      <a href="../">{repository}</a> / 
      <a href="./">{task_id}</a> / 
      {agent_name}
    </div>
  </div>

  <div class="container">
    {error_section}
    
    <div class="recording-info">
      <div class="info-grid">
        <div class="info-item">
          <div class="info-value">{agent_name}</div>
          <div class="info-label">Agent</div>
        </div>
        <div class="info-item">
          <div class="info-value">{duration}</div>
          <div class="info-label">Duration</div>
        </div>
        <div class="info-item">
          <div class="info-value">
            <span class="status-badge {agent_status_class}">{agent_status}</span>
          </div>
          <div class="info-label">Agent Status</div>
        </div>
        <div class="info-item">
          <div class="info-value">
            <span class="status-badge {verify_status_class}">{verify_status}</span>
          </div>
          <div class="info-label">Verification</div>
        </div>
      </div>
    </div>

    {player_section}
    
    <div class="download-section">
      <h3>Download Recording</h3>
      <div class="download-links">
        {download_links}
      </div>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/asciinema-player@3.6.4/dist/bundle/asciinema-player.min.js"></script>
  <script>
    let player = null;
    
    function initializePlayer() {{
      const playerElement = document.getElementById('player');
      if (!playerElement) return;
      
      player = AsciinemaPlayer.create('{recording_url}', playerElement, {{
        cols: 120,
        rows: 30,
        autoPlay: false,
        loop: false,
        startAt: 0,
        speed: 1,
        theme: 'monokai',
        poster: 'npt:0:05'
      }});
    }}
    
    function playPause() {{
      if (player) {{
        player.getCurrentTime() > 0 ? player.pause() : player.play();
      }}
    }}
    
    function restart() {{
      if (player) {{
        player.seek(0);
      }}
    }}
    
    function setSpeed(speed) {{
      if (player) {{
        player.setSpeed(speed);
        
        // Update active speed button
        document.querySelectorAll('.speed-button').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[onclick="setSpeed(${{speed}})"]`).classList.add('active');
      }}
    }}
    
    // Initialize player when page loads
    window.addEventListener('DOMContentLoaded', initializePlayer);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {{
      if (e.target.tagName.toLowerCase() === 'input') return;
      
      switch(e.key) {{
        case ' ':
        case 'k':
          e.preventDefault();
          playPause();
          break;
        case 'r':
          restart();
          break;
        case '1':
          setSpeed(0.5);
          break;
        case '2':
          setSpeed(1);
          break;
        case '3':
          setSpeed(1.5);
          break;
        case '4':
          setSpeed(2);
          break;
      }}
    }});
  </script>
</body>
</html>
"""


class WebRecordingPlayer:
    """Web-based player for terminal recordings."""
    
    def __init__(self, recordings_dir: Path = Path("outputs/recordings")):
        self.recordings_dir = recordings_dir
        self.recorder = SessionRecorder(recordings_dir)
    
    def generate_player_html(self, 
                            recording_id: str,
                            base_url: str = "") -> Optional[str]:
        """Generate HTML player for a specific recording."""
        recording = self.recorder.get_recording(recording_id)
        if not recording:
            return None
        
        recording_path = Path(recording.file_path)
        
        # Check if recording file exists
        if not recording_path.exists():
            error_section = '<div class="error-message">❌ Recording file not found. The recording may have been moved or deleted.</div>'
            player_section = ""
            recording_url = ""
            download_links = ""
        else:
            error_section = ""
            
            # Generate player section
            player_section = f"""
            <div class="player-container">
              <h2>Terminal Session Recording</h2>
              <div id="player"></div>
              <div class="controls">
                <button class="control-button" onclick="playPause()">▶️ Play/Pause</button>
                <button class="control-button" onclick="restart()">⏮️ Restart</button>
                <div class="speed-controls">
                  <span>Speed:</span>
                  <button class="speed-button" onclick="setSpeed(0.5)">0.5x</button>
                  <button class="speed-button active" onclick="setSpeed(1)">1x</button>
                  <button class="speed-button" onclick="setSpeed(1.5)">1.5x</button>
                  <button class="speed-button" onclick="setSpeed(2)">2x</button>
                </div>
              </div>
            </div>
            """
            
            # Recording URL (relative to web root)
            recording_url = f"{base_url}/recordings/{recording.repository}/{recording.task_id}/{recording_path.name}"
            
            # Generate download links
            download_links = f'<a href="{recording_url}" class="download-link" download>📥 Download .cast</a>'
            
            # Check for compressed version
            compressed_path = recording_path.with_suffix('.cast.gz')
            if compressed_path.exists():
                compressed_url = f"{base_url}/recordings/{recording.repository}/{recording.task_id}/{compressed_path.name}"
                download_links += f'<a href="{compressed_url}" class="download-link" download>📦 Download .cast.gz</a>'
            
            # Check for GIF version
            gif_path = recording_path.with_suffix('.gif')
            if gif_path.exists():
                gif_url = f"{base_url}/recordings/{recording.repository}/{recording.task_id}/{gif_path.name}"
                download_links += f'<a href="{gif_url}" class="download-link" download>🎞️ Download .gif</a>'
        
        # Format metadata
        duration = f"{recording.duration_seconds:.1f}s" if recording.duration_seconds else "Unknown"
        
        agent_status = "Success" if recording.agent_success else "Failed" if recording.agent_success is False else "Unknown"
        agent_status_class = "status-success" if recording.agent_success else "status-failure" if recording.agent_success is False else "status-unknown"
        
        verify_status = "Passed" if recording.verify_success else "Failed" if recording.verify_success is False else "Unknown"
        verify_status_class = "status-success" if recording.verify_success else "status-failure" if recording.verify_success is False else "status-unknown"
        
        recording_title = f"{recording.agent_name} - {recording.repository}/{recording.task_id}"
        
        return ASCIINEMA_PLAYER_HTML_TEMPLATE.format(
            recording_title=recording_title,
            repository=recording.repository,
            task_id=recording.task_id,
            agent_name=recording.agent_name,
            duration=duration,
            agent_status=agent_status,
            agent_status_class=agent_status_class,
            verify_status=verify_status,
            verify_status_class=verify_status_class,
            error_section=error_section,
            player_section=player_section,
            recording_url=recording_url,
            download_links=download_links
        )
    
    def generate_recordings_index_html(self, 
                                     repository: Optional[str] = None,
                                     task_id: Optional[str] = None) -> str:
        """Generate HTML index of recordings."""
        recordings = self.recorder.list_recordings(repository=repository, task_id=task_id)
        
        if repository and task_id:
            title = f"Recordings - {repository}/{task_id}"
            breadcrumb = f"<a href='../../../leaderboard/'>← Back to Leaderboard</a> / <a href='../'>{repository}</a> / {task_id}"
        elif repository:
            title = f"Recordings - {repository}"
            breadcrumb = f"<a href='../../leaderboard/'>← Back to Leaderboard</a> / {repository}"
        else:
            title = "All Recordings"
            breadcrumb = "<a href='../leaderboard/'>← Back to Leaderboard</a> / Recordings"
        
        recordings_html = ""
        for recording in recordings:
            duration = f"{recording.duration_seconds:.1f}s" if recording.duration_seconds else "Unknown"
            status_class = "status-success" if recording.verify_success else "status-failure" if recording.verify_success is False else "status-unknown"
            status_text = "✅ Passed" if recording.verify_success else "❌ Failed" if recording.verify_success is False else "❓ Unknown"
            
            recordings_html += f"""
            <tr>
                <td><a href="{recording.recording_id}/">{recording.agent_name}</a></td>
                <td>{recording.repository}</td>
                <td>{recording.task_id}</td>
                <td>{duration}</td>
                <td><span class="status-badge {status_class}">{status_text}</span></td>
                <td>{recording.start_time[:19].replace('T', ' ')}</td>
            </tr>
            """
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        /* Same CSS styles as player template */
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="breadcrumb">{breadcrumb}</div>
    </div>
    <div class="container">
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Agent</th>
                        <th>Repository</th>
                        <th>Task</th>
                        <th>Duration</th>
                        <th>Status</th>
                        <th>Recorded</th>
                    </tr>
                </thead>
                <tbody>
                    {recordings_html or '<tr><td colspan="6" style="text-align: center; color: #6b7280;">No recordings found</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>"""
    
    def build_web_interface(self, output_dir: Path = Path("outputs/web")) -> Dict[str, Any]:
        """Build complete web interface for recordings."""
        recordings_web_dir = output_dir / "recordings"
        recordings_web_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate recordings index
        index = create_recording_index(self.recordings_dir)
        
        # Create main recordings index
        with open(recordings_web_dir / "index.html", "w") as f:
            f.write(self.generate_recordings_index_html())
        
        # Create JSON index for API access
        with open(recordings_web_dir / "index.json", "w") as f:
            json.dump(index, f, indent=2)
        
        # Create individual recording pages
        recordings_created = 0
        for recording in self.recorder.list_recordings():
            # Create directory structure
            recording_dir = recordings_web_dir / recording.repository / recording.task_id / recording.recording_id
            recording_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate player HTML
            player_html = self.generate_player_html(recording.recording_id, base_url="../../../")
            if player_html:
                with open(recording_dir / "index.html", "w") as f:
                    f.write(player_html)
                recordings_created += 1
        
        # Copy recording files for web access
        recordings_copied = 0
        for recording_file in self.recordings_dir.glob("*/*/*.cast*"):
            rel_path = recording_file.relative_to(self.recordings_dir)
            web_file = recordings_web_dir / rel_path
            web_file.parent.mkdir(parents=True, exist_ok=True)
            
            if not web_file.exists():
                import shutil
                shutil.copy2(recording_file, web_file)
                recordings_copied += 1
        
        return {
            "recordings_index": str(recordings_web_dir / "index.html"),
            "recordings_json": str(recordings_web_dir / "index.json"),
            "total_recordings": len(index["recordings"]),
            "recording_pages_created": recordings_created,
            "recording_files_copied": recordings_copied,
            "repositories": list(index["repositories"].keys()),
            "agents": list(index["agents"].keys())
        }