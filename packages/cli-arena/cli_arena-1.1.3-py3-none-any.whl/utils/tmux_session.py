class TmuxSession:
    """A tmux session running inside a Docker container."""
    
    _TMUX_COMPLETION_COMMAND = "; tmux wait -S done"
    
    def __init__(self, container, session_name: str, user: str = "root"):
        # Verifies tmux is installed in the container
        result = self.container.exec_run(["tmux", "-V"])
        if result.exit_code != 0:
            raise RuntimeError(
                "tmux is not installed in the container. "
                "Please install tmux in the container to run Terminal-Bench."
            )