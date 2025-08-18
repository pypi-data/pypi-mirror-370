#!/usr/bin/env python3
"""
IPC module for vtree - handles inter-process communication with shell sessions
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class IPCCommand:
    """Represents a command to send to external shell"""
    action: str  # "cd", "open", "edit", etc.
    path: str    # File/directory path
    editor: Optional[str] = None  # Optional editor command
    args: Optional[Dict[str, Any]] = None  # Additional arguments


class IPCClient:
    """Client for sending commands to external shell sessions"""
    
    def __init__(self, pipe_path: Optional[str] = None):
        """Initialize IPC client with optional custom pipe path"""
        if pipe_path:
            self.pipe_path = Path(pipe_path)
        else:
            # Use /tmp/vtree_ipc as default pipe path
            self.pipe_path = Path("/tmp/vtree_ipc")
    
    def is_available(self) -> bool:
        """Check if IPC pipe is available for communication"""
        return self.pipe_path.exists() and self.pipe_path.is_fifo()
    
    def send_command(self, command: IPCCommand) -> bool:
        """Send a command to the external shell session"""
        if not self.is_available():
            return False
        
        try:
            # Convert command to JSON
            command_json = json.dumps(asdict(command))
            
            # Send to named pipe (non-blocking write)
            with open(self.pipe_path, 'w', encoding='utf-8') as pipe:
                pipe.write(command_json + '\n')
                pipe.flush()
            
            return True
        except (OSError, IOError, json.JSONEncodeError):
            return False
    
    def send_cd_command(self, directory: str) -> bool:
        """Convenience method to send a cd command"""
        command = IPCCommand(action="cd", path=directory)
        return self.send_command(command)
    
    def send_open_command(self, file_path: str, editor: Optional[str] = None) -> bool:
        """Convenience method to send an open file command"""
        command = IPCCommand(action="open", path=file_path, editor=editor)
        return self.send_command(command)
    
    def send_edit_command(self, file_path: str, editor: Optional[str] = None) -> bool:
        """Convenience method to send an edit file command"""
        command = IPCCommand(action="edit", path=file_path, editor=editor)
        return self.send_command(command)


def get_default_pipe_path() -> Path:
    """Get the default pipe path for vtree IPC"""
    return Path("/tmp/vtree_ipc")


def create_pipe_if_needed(pipe_path: Optional[Path] = None) -> bool:
    """Create named pipe if it doesn't exist"""
    if pipe_path is None:
        pipe_path = get_default_pipe_path()
    
    if pipe_path.exists():
        return True
    
    try:
        os.mkfifo(str(pipe_path))
        return True
    except (OSError, PermissionError):
        return False


def cleanup_pipe(pipe_path: Optional[Path] = None) -> bool:
    """Clean up named pipe"""
    if pipe_path is None:
        pipe_path = get_default_pipe_path()
    
    try:
        if pipe_path.exists():
            pipe_path.unlink()
        return True
    except (OSError, PermissionError):
        return False