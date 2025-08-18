#!/usr/bin/env python3
"""
vtree - A modern, interactive terminal-based file tree viewer with file panel support
"""

import os
import sys
import subprocess
import configparser
import time
import shutil
import tempfile
import json
import uuid
from pathlib import Path
from typing import List, Optional, Set, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Tree, Footer, Header, Static, Label, DataTable, TextArea
from textual.binding import Binding
from textual.reactive import reactive
from textual.widget import Widget
from textual.message import Message
from textual.events import Click
from textual.screen import ModalScreen
from textual import events
from rich.text import Text
import click

# Import IPC functionality
from .ipc import IPCClient, IPCCommand


@dataclass
class FileNode:
    path: Path
    is_dir: bool
    size: Optional[int] = None
    children: Optional[List['FileNode']] = None


class ActionType(Enum):
    """Types of actions that can be undone"""
    DELETE_FILE = "delete_file"
    DELETE_FOLDER = "delete_folder"
    EDIT_FILE = "edit_file"
    CREATE_FILE = "create_file"
    RENAME = "rename"


@dataclass
class UndoAction:
    """Represents a single undoable action"""
    id: str
    action_type: ActionType
    timestamp: datetime
    original_path: Path
    backup_path: Optional[Path] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class UndoManager:
    """Manages undo operations with temporary file storage"""
    
    def __init__(self, max_undo_history: int = 50):
        self.max_undo_history = max_undo_history
        self.undo_stack: List[UndoAction] = []
        self.temp_dir = Path(tempfile.mkdtemp(prefix="vtree_undo_"))
        self.metadata_file = self.temp_dir / "undo_metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """Load existing undo metadata if available"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    # Reconstruct undo stack from metadata
                    for item in data.get('undo_stack', []):
                        action = UndoAction(
                            id=item['id'],
                            action_type=ActionType(item['action_type']),
                            timestamp=datetime.fromisoformat(item['timestamp']),
                            original_path=Path(item['original_path']),
                            backup_path=Path(item['backup_path']) if item.get('backup_path') else None,
                            metadata=item.get('metadata', {})
                        )
                        self.undo_stack.append(action)
            except Exception:
                # If metadata is corrupted, start fresh
                self.undo_stack = []
    
    def _save_metadata(self):
        """Save undo metadata to disk"""
        data = {
            'undo_stack': [
                {
                    'id': action.id,
                    'action_type': action.action_type.value,
                    'timestamp': action.timestamp.isoformat(),
                    'original_path': str(action.original_path),
                    'backup_path': str(action.backup_path) if action.backup_path else None,
                    'metadata': action.metadata
                }
                for action in self.undo_stack
            ]
        }
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_delete_action(self, path: Path) -> str:
        """Add a delete action to the undo stack"""
        action_id = str(uuid.uuid4())
        backup_path = self.temp_dir / action_id
        
        
        try:
            if path.is_dir():
                # Backup entire directory
                shutil.copytree(path, backup_path, symlinks=True)
                action_type = ActionType.DELETE_FOLDER
            else:
                # Backup single file
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, backup_path)
                action_type = ActionType.DELETE_FILE
            
            action = UndoAction(
                id=action_id,
                action_type=action_type,
                timestamp=datetime.now(),
                original_path=path,
                backup_path=backup_path,
                metadata={
                    'size': path.stat().st_size if path.is_file() else None,
                    'permissions': oct(path.stat().st_mode)
                }
            )
            
            self.undo_stack.append(action)
            self._trim_stack()
            self._save_metadata()
            
            return action_id
            
        except Exception as e:
            # Clean up backup if something went wrong
            try:
                if backup_path.exists():
                    if backup_path.is_dir():
                        shutil.rmtree(backup_path)
                    else:
                        backup_path.unlink()
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors
            raise e
    
    def add_edit_action(self, path: Path, original_content: str) -> str:
        """Add an edit action to the undo stack"""
        action_id = str(uuid.uuid4())
        backup_path = self.temp_dir / action_id
        
        # Save original content
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        action = UndoAction(
            id=action_id,
            action_type=ActionType.EDIT_FILE,
            timestamp=datetime.now(),
            original_path=path,
            backup_path=backup_path,
            metadata={
                'original_size': len(original_content),
                'encoding': 'utf-8'
            }
        )
        
        self.undo_stack.append(action)
        self._trim_stack()
        self._save_metadata()
        
        return action_id
    
    def undo_last(self) -> Optional[UndoAction]:
        """Undo the last action and return it"""
        if not self.undo_stack:
            return None
        
        action = self.undo_stack.pop()
        
        
        try:
            if action.action_type in [ActionType.DELETE_FILE, ActionType.DELETE_FOLDER]:
                # Restore deleted file/folder
                if action.backup_path and action.backup_path.exists():
                    if action.original_path.exists():
                        # Target already exists - clean up backup and skip
                        try:
                            if action.backup_path.is_dir():
                                shutil.rmtree(action.backup_path)
                            else:
                                action.backup_path.unlink()
                        except (OSError, PermissionError):
                            pass  # Ignore cleanup errors
                        self._save_metadata()
                        return None
                    
                    # Ensure parent directory exists
                    action.original_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if action.action_type == ActionType.DELETE_FOLDER:
                        shutil.copytree(action.backup_path, action.original_path, symlinks=True)
                    else:
                        shutil.copy2(action.backup_path, action.original_path)
                    
                    # Clean up backup
                    try:
                        if action.backup_path.is_dir():
                            shutil.rmtree(action.backup_path)
                        else:
                            action.backup_path.unlink()
                    except (OSError, PermissionError):
                        pass  # Ignore cleanup errors
            
            elif action.action_type == ActionType.EDIT_FILE:
                # Restore original file content
                if action.backup_path and action.backup_path.exists():
                    with open(action.backup_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    
                    with open(action.original_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                    
                    # Clean up backup
                    try:
                        action.backup_path.unlink()
                    except (OSError, PermissionError):
                        pass  # Ignore cleanup errors
            
            self._save_metadata()
            return action
            
        except Exception as e:
            # If undo failed, put the action back on the stack
            self.undo_stack.append(action)
            self._save_metadata()
            raise e
    
    def _trim_stack(self):
        """Trim the undo stack to max size"""
        while len(self.undo_stack) > self.max_undo_history:
            old_action = self.undo_stack.pop(0)
            # Clean up old backup files
            if old_action.backup_path and old_action.backup_path.exists():
                try:
                    if old_action.backup_path.is_dir():
                        shutil.rmtree(old_action.backup_path)
                    else:
                        old_action.backup_path.unlink()
                except (OSError, PermissionError):
                    pass  # Ignore cleanup errors for old backups
    
    def get_undo_info(self) -> List[str]:
        """Get human-readable info about available undos"""
        info = []
        for action in reversed(self.undo_stack[-10:]):  # Show last 10
            if action.action_type == ActionType.DELETE_FILE:
                info.append(f"Delete file: {action.original_path.name}")
            elif action.action_type == ActionType.DELETE_FOLDER:
                info.append(f"Delete folder: {action.original_path.name}")
            elif action.action_type == ActionType.EDIT_FILE:
                info.append(f"Edit file: {action.original_path.name}")
        return info
    
    def cleanup(self):
        """Clean up all temporary files"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)


class FileTree(Tree):
    """Custom Tree widget for file system navigation."""
    
    def __init__(self, root_path: Path, show_hidden: bool = False, show_files_inline: bool = True, settings: dict = None, *args, **kwargs):
        # Initialize with the root path name as the tree label
        super().__init__(f"[bold blue]{root_path.name}[/bold blue]", *args, **kwargs)
        self.root_path = root_path
        self.show_hidden = show_hidden
        self.show_files_inline = show_files_inline
        self.settings = settings or {}
        self.ignore_patterns = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            '.venv', 'venv', '.DS_Store', '.idea', '.vscode',
            'dist', 'build', '.egg-info'
        }
        self.changed_items = {}  # Track changed items
        self.selected_nodes = set()  # Track multi-selected nodes
        self.ipc_client = IPCClient()  # Initialize IPC client
        self.populate_tree()
    
    def should_ignore(self, path: Path) -> bool:
        """Check if a file/directory should be ignored"""
        name = path.name
        
        # Hidden files/dirs (starting with .)
        if name.startswith('.') and not self.show_hidden:
            if name not in {'.gitignore', '.env.example', '.github'}:
                return True
        
        # Check ignore patterns
        if any(pattern in name for pattern in self.ignore_patterns):
            return True
            
        return False
    
    def on_click(self, event: Click) -> None:
        """Handle click events for multi-selection"""        
        # Check if cmd/ctrl key is pressed for multi-selection
        if event.ctrl or event.meta:
            # Get the currently highlighted/selected node from the tree
            cursor_node = self.cursor_node
            if cursor_node and cursor_node.data:
                path_str = str(cursor_node.data["path"])
                
                # Don't select the root directory
                if cursor_node.data["path"] == self.root_path:
                    return
                
                # Toggle selection
                if path_str in self.selected_nodes:
                    self.selected_nodes.remove(path_str)
                else:
                    self.selected_nodes.add(path_str)
                
                # Refresh to show selection changes
                self.refresh_tree()
                event.prevent_default()
                event.stop()
        else:
            # Regular click - clear all selections unless clicking on already selected item
            cursor_node = self.cursor_node
            if cursor_node and cursor_node.data:
                path_str = str(cursor_node.data["path"])
                # Only clear selections if clicking on a non-selected item
                if path_str not in self.selected_nodes and self.selected_nodes:
                    self.selected_nodes.clear()
                    self.refresh_tree()
            elif self.selected_nodes:
                # Clicked on empty space - clear selections
                self.selected_nodes.clear()
                self.refresh_tree()
    
    def get_selected_paths(self) -> List[Path]:
        """Get list of selected file/folder paths"""
        return [Path(path_str) for path_str in self.selected_nodes]
    
    def clear_selection(self):
        """Clear all selected items"""
        self.selected_nodes.clear()
        self.refresh_tree()
    
    def get_file_size(self, path: Path) -> Optional[int]:
        """Get file size safely"""
        try:
            return path.stat().st_size if path.is_file() else None
        except (OSError, PermissionError):
            return None
    
    def format_size(self, size: Optional[int]) -> str:
        """Format file size in human readable format"""
        if size is None:
            return ""
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size_float = float(size)
        unit_index = 0
        
        while size_float >= 1024 and unit_index < len(units) - 1:
            size_float /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f" [dim]({int(size_float)} {units[unit_index]})[/dim]"
        else:
            return f" [dim]({size_float:.1f} {units[unit_index]})[/dim]"
    
    
    def populate_tree(self):
        """Populate the tree with file system data"""
        self.clear()
        
        # Set data on root node
        self.root.data = {"path": self.root_path, "type": "dir"}
        
        # Add children directly to root
        self._vtree_add_children(self.root, self.root_path)
        
        # Force expand the root node immediately
        self.root.expand()
        self.root.expanded = True
    
    def _vtree_add_children(self, parent_node, parent_path: Path, max_depth: int = 5, current_depth: int = 0):
        """Recursively add children to tree nodes"""
        if current_depth >= max_depth:
            return
        
        try:
            # Get all items and sort: directories first, then files, both alphabetically
            items = list(parent_path.iterdir())
            items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for item in items:
                if self.should_ignore(item):
                    continue
                
                name = item.name
                
                # Check if this item is changed
                is_changed = name in self.changed_items
                # Check if this is a hidden file
                is_hidden = name.startswith('.')
                
                if item.is_dir():
                    # Check if any child is changed
                    has_changed_child = self._has_changed_child(item)
                    
                    # Check if this item is selected
                    is_selected = str(item) in self.selected_nodes
                    
                    if is_selected:
                        label = f"[bold white on blue]{name}[/bold white on blue]"
                    elif is_changed or has_changed_child:
                        fg = self.settings.get("changed_file_fg", "white")
                        bg = self.settings.get("changed_file_bg", "dark_red")
                        label = f"[{fg} on {bg}][bold]{name}[/bold][/{fg} on {bg}]"
                    elif is_hidden:
                        color = self.settings.get("hidden_file_color", "#4a4a4a")
                        label = f"[{color}]{name}[/{color}]"
                    else:
                        label = f"[bold yellow]{name}[/bold yellow]"
                    
                    node_data = {"path": item, "type": "dir"}
                    child_node = parent_node.add(label, data=node_data)
                    
                    # Add children recursively
                    self._vtree_add_children(child_node, item, max_depth, current_depth + 1)
                elif self.show_files_inline:
                    size_str = self.format_size(self.get_file_size(item))
                    
                    # Check if this item is selected
                    is_selected = str(item) in self.selected_nodes
                    
                    if is_selected:
                        label = f"[bold white on blue]{name}{size_str}[/bold white on blue]"
                    elif is_changed:
                        fg = self.settings.get("changed_file_fg", "white")
                        bg = self.settings.get("changed_file_bg", "dark_red")
                        label = f"[{fg} on {bg}]{name}{size_str}[/{fg} on {bg}]"
                    elif is_hidden:
                        color = self.settings.get("hidden_file_color", "#4a4a4a")
                        label = f"[{color}]{name}{size_str}[/{color}]"
                    else:
                        label = f"{name}{size_str}"
                    
                    node_data = {"path": item, "type": "file", "size": self.get_file_size(item)}
                    parent_node.add_leaf(label, data=node_data)
                    
        except PermissionError:
            parent_node.add_leaf("❌ [red]Permission denied[/red]")
    
    def refresh_tree(self, show_hidden: bool = None, show_files_inline: bool = None):
        """Refresh the tree display"""
        if show_hidden is not None:
            self.show_hidden = show_hidden
        if show_files_inline is not None:
            self.show_files_inline = show_files_inline
        self.populate_tree()
    
    def _has_changed_child(self, directory: Path) -> bool:
        """Check if directory has any changed children (recursive)"""
        try:
            for item in directory.iterdir():
                if item.name in self.changed_items:
                    return True
                if item.is_dir() and self._has_changed_child(item):
                    return True
        except (OSError, PermissionError):
            pass
        return False
    
    def send_cd_to_shell(self, directory_path: Path) -> bool:
        """Send cd command to external shell via IPC"""
        if self.ipc_client.is_available():
            return self.ipc_client.send_cd_command(str(directory_path))
        return False
    
    def key_ctrl_d(self) -> None:
        """Handle Ctrl+D key press to cd to selected directory in external shell"""
        cursor_node = self.cursor_node
        if cursor_node and cursor_node.data:
            path = cursor_node.data["path"]
            if path.is_dir():
                success = self.send_cd_to_shell(path)
                app = self.app
                if success:
                    # Show feedback
                    app.notify(f"Sent 'cd {path}' to shell", severity="information")
                else:
                    app.notify("Shell integration not available", severity="warning")


class InfoPanel(Static):
    """Information panel showing details about selected file/directory"""
    
    def __init__(self, *args, **kwargs):
        super().__init__("", *args, **kwargs)
        self.border_title = "Info"
        # Lazy import flag for Pillow
        self._pillow_available: Optional[bool] = None
        # Supported raster image extensions for preview
        self._image_exts: Set[str] = {
            ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tif", ".tiff", ".webp"
        }
    
    def update_info(self, path: Path, file_type: str, size: Optional[int] = None):
        """Update the info panel with file/directory information"""
        info_text = Text()
        
        # More compact format
        info_text.append(f"📍 {path.name}", style="bold cyan")
        
        if file_type == "file" and size is not None:
            size_str = self._format_size(size)
            info_text.append(f" ({size_str})", style="dim")
        
        info_text.append(f" • {file_type.title()}", style="yellow")
        info_text.append(f" • {path.parent}", style="dim")
        
        # Attempt low-res color image preview when selecting an image file
        if file_type == "file" and self._is_previewable_image(path):
            preview_text = self._render_image_preview_color(path)
            if preview_text is None:
                # Fallback to grayscale ASCII if color preview not available
                preview = self._render_image_preview(path)
                if preview:
                    info_text.append("\n\n")
                    info_text.append(preview, style="dim")
            else:
                info_text.append("\n\n")
                # Append the pre-styled Text content
                try:
                    info_text.append_text(preview_text)  # rich >= 13
                except Exception:
                    # Fallback: concatenate string (will lose colors)
                    info_text.append(str(preview_text))
        
        self.update(info_text)
    
    def _format_size(self, size: int) -> str:
        """Format file size in human readable format"""
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size_float = float(size)
        unit_index = 0
        
        while size_float >= 1024 and unit_index < len(units) - 1:
            size_float /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size_float)} {units[unit_index]}"
        else:
            return f"{size_float:.1f} {units[unit_index]}"

    def _is_previewable_image(self, path: Path) -> bool:
        """Check if the given path is an image we can preview."""
        try:
            if not path.is_file():
                return False
        except Exception:
            return False
        suffix = path.suffix.lower()
        return suffix in self._image_exts

    def _ensure_pillow(self) -> bool:
        """Detect if Pillow is available (cached)."""
        if self._pillow_available is not None:
            return self._pillow_available
        try:
            import PIL  # type: ignore
            from PIL import Image  # noqa: F401
            self._pillow_available = True
        except Exception:
            self._pillow_available = False
        return self._pillow_available

    def _render_image_preview(self, path: Path, max_width: int = 40, max_height: int = 12) -> Optional[str]:
        """Render a tiny ASCII grayscale preview of the image.

        Returns a multi-line string or None if unavailable.
        """
        if not self._ensure_pillow():
            return None
        try:
            from PIL import Image
            # Open image (first frame for GIFs)
            with Image.open(path) as im:
                try:
                    im.seek(0)
                except Exception:
                    pass
                im = im.convert("L")  # grayscale

                # Aspect ratio correction: terminal characters are ~2x taller than wide
                orig_w, orig_h = im.size
                if orig_w == 0 or orig_h == 0:
                    return None
                target_w = min(max_width, orig_w)
                # scale height with a factor ~0.5 to compensate character aspect
                scaled_h = int(orig_h * (target_w / orig_w) * 0.5)
                target_h = max(1, min(max_height, scaled_h))
                if target_w < 1 or target_h < 1:
                    return None
                im = im.resize((target_w, target_h))

                # Map grayscale to ASCII ramp
                ramp = " .'`^,:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
                ramp_len = len(ramp)
                pixels = im.getdata()
                lines = []
                for y in range(target_h):
                    row_chars = []
                    offset = y * target_w
                    for x in range(target_w):
                        p = pixels[offset + x]
                        idx = int((p / 255) * (ramp_len - 1))
                        row_chars.append(ramp[idx])
                    # Slightly stretch horizontally for better proportions
                    line = ''.join(ch * 1 for ch in row_chars)
                    lines.append(line)
                return "\n".join(lines)
        except Exception:
            return None

    def _render_image_preview_color(self, path: Path, max_width: int = 36, max_lines: int = 12) -> Optional[Text]:
        """Render a low-res color preview using half-block characters.

        Each character cell represents two vertical pixels (upper = fg, lower = bg).
        Returns a Rich Text instance or None.
        """
        if not self._ensure_pillow():
            return None
        try:
            from PIL import Image
            with Image.open(path) as im:
                # Use first frame and convert to RGBA for consistent handling
                try:
                    im.seek(0)
                except Exception:
                    pass
                im = im.convert("RGBA")

                orig_w, orig_h = im.size
                if orig_w == 0 or orig_h == 0:
                    return None

                # Determine target width within constraints
                target_w = min(max_width, orig_w)
                # We need 2 image rows per text row
                # Compute scaled height (in image pixels) preserving aspect ratio and compensating char aspect (0.5)
                scaled_h_float = orig_h * (target_w / orig_w) * 0.5
                target_lines = max(1, min(max_lines, int(scaled_h_float)))
                target_h = target_lines * 2

                if target_w < 1 or target_h < 2:
                    return None

                # Resize using a fast but decent filter
                im = im.resize((target_w, target_h))

                # Background color for alpha compositing (match app theme #252526)
                bg_rgb = (0x25, 0x25, 0x26)

                def blend_rgba(px):
                    r, g, b, a = px
                    if a == 255:
                        return (r, g, b)
                    alpha = a / 255.0
                    br, bgc, bb = bg_rgb
                    return (
                        int(r * alpha + br * (1 - alpha)),
                        int(g * alpha + bgc * (1 - alpha)),
                        int(b * alpha + bb * (1 - alpha)),
                    )

                pixels = im.load()
                out = Text()
                half_block = "▀"  # upper half block: fg = upper pixel, bg = lower pixel
                for y in range(0, target_h, 2):
                    # Build one text row
                    for x in range(target_w):
                        upper = blend_rgba(pixels[x, y])
                        lower = blend_rgba(pixels[x, y + 1])
                        upper_hex = f"#{upper[0]:02x}{upper[1]:02x}{upper[2]:02x}"
                        lower_hex = f"#{lower[0]:02x}{lower[1]:02x}{lower[2]:02x}"
                        out.append(half_block, style=f"{upper_hex} on {lower_hex}")
                    out.append("\n")
                # Remove trailing newline
                if len(out) and out.plain.endswith("\n"):
                    try:
                        out = out[:-1]
                    except Exception:
                        pass
                return out
        except Exception:
            return None


class FileListPanel(DataTable):
    """Panel showing files in the selected directory"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = "Files"
        self.zebra_stripes = True
        self.cursor_type = "row"
        self.add_columns("Name", "Size", "Modified")
        self.selected_files = set()  # Track selected files in this panel
        self.current_directory = None
    
    def update_files(self, directory_path: Path):
        """Update the file list with files from the given directory"""
        self.clear()
        self.selected_files.clear()  # Clear selections when switching directories
        self.current_directory = directory_path
        
        if not directory_path.is_dir():
            return
        
        # Get app's changed items and settings for styling
        app = self.app
        changed_items = getattr(app, '_changed_items', {})
        settings = getattr(app, '_settings', {})
        
        try:
            items = []
            for item in directory_path.iterdir():
                if item.is_file():
                    try:
                        stat = item.stat()
                        size = stat.st_size
                        modified = datetime.fromtimestamp(stat.st_mtime)
                        items.append((item.name, size, modified, item))
                    except (OSError, PermissionError):
                        items.append((item.name, 0, datetime.now(), item))
            
            # Sort by name
            items.sort(key=lambda x: x[0].lower())
            
            for name, size, modified, file_path in items:
                size_str = self._format_size(size)
                date_str = modified.strftime("%Y-%m-%d %H:%M")
                
                # Check if this file is in the changed items
                is_changed = name in changed_items
                is_hidden = name.startswith('.')
                
                # Apply styling similar to tree view
                if is_changed:
                    fg = settings.get("changed_file_fg", "white")
                    bg = settings.get("changed_file_bg", "dark_red")
                    styled_name = f"[{fg} on {bg}]{name}[/{fg} on {bg}]"
                    styled_size = f"[{fg} on {bg}]{size_str}[/{fg} on {bg}]"
                    styled_date = f"[{fg} on {bg}]{date_str}[/{fg} on {bg}]"
                elif is_hidden:
                    color = settings.get("hidden_file_color", "#4a4a4a")
                    styled_name = f"[{color}]{name}[/{color}]"
                    styled_size = f"[{color}]{size_str}[/{color}]"
                    styled_date = f"[{color}]{date_str}[/{color}]"
                else:
                    styled_name = name
                    styled_size = size_str
                    styled_date = date_str
                
                self.add_row(styled_name, styled_size, styled_date)
                
        except PermissionError:
            self.add_row("Permission denied", "", "")
    
    def _format_size(self, size: int) -> str:
        """Format file size in human readable format"""
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size_float = float(size)
        unit_index = 0
        
        while size_float >= 1024 and unit_index < len(units) - 1:
            size_float /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size_float)} {units[unit_index]}"
        else:
            return f"{size_float:.1f} {units[unit_index]}"
    
    def on_click(self, event: Click) -> None:
        """Handle click events for multi-selection in file panel"""
        if not self.current_directory:
            return
            
        # Get the row that was clicked
        try:
            coordinate = self.cursor_coordinate
            if coordinate is None:
                return
            
            row_index = coordinate.row
            if row_index >= len(self.rows):
                return
            
            # Get the filename from the first column
            filename = str(self.get_cell_at(coordinate.replace(column=0)))
            if filename == "Permission denied":
                return
            
            file_path = self.current_directory / filename
            
            # Check if cmd/ctrl key is pressed for multi-selection
            if event.ctrl or event.meta:
                # Toggle selection
                if filename in self.selected_files:
                    self.selected_files.remove(filename)
                else:
                    self.selected_files.add(filename)
            else:
                # Regular click - clear previous selections and select this file
                self.selected_files.clear()
                self.selected_files.add(filename)
            
            # Update visual indicators (we'll handle this with styling later)
            event.prevent_default()
            event.stop()
            
        except Exception:
            # If anything goes wrong, just ignore the click
            pass
    
    def get_selected_file_paths(self) -> List[Path]:
        """Get list of selected file paths"""
        if not self.current_directory:
            return []
        return [self.current_directory / filename for filename in self.selected_files]
    
    def clear_selection(self):
        """Clear all selected files"""
        self.selected_files.clear()
    
    def key_d(self) -> None:
        """Handle 'd' key press in file panel"""
        # Forward the delete action to the main app
        self.app.action_delete_selected()
    
    def key_r(self) -> None:
        """Handle 'r' key press in file panel - refresh"""
        self.app.action_refresh()
    
    def key_c(self) -> None:
        """Handle 'c' key press in file panel - copy path"""
        self.app.action_copy_path()
    
    def key_f(self) -> None:
        """Handle 'f' key press in file panel - toggle hidden files"""
        self.app.action_toggle_hidden()
    
    def key_p(self) -> None:
        """Handle 'p' key press in file panel - toggle file panel"""
        self.app.action_toggle_file_panel()
    
    def key_h(self) -> None:
        """Handle 'h' key press in file panel - toggle help"""
        self.app.action_toggle_help()
    
    def key_question_mark(self) -> None:
        """Handle '?' key press in file panel - toggle help"""
        self.app.action_toggle_help()
    
    def key_y(self) -> None:
        """Handle 'y' key press in file panel - confirm deletion"""
        self.app.key_y()
    
    def key_n(self) -> None:
        """Handle 'n' key press in file panel - cancel deletion"""
        self.app.key_n()
    
    def key_e(self) -> None:
        """Handle 'e' key press in file panel - edit file"""
        self.app.action_edit_file()


class HelpPanel(Static):
    """Help panel showing keyboard shortcuts"""
    
    def __init__(self, *args, **kwargs):
        super().__init__("", *args, **kwargs)
        self.border_title = "Help"
        
        help_text = Text()
        
        # Basic shortcuts
        shortcuts = [
            ("q/Ctrl+C", "Quit"),
            ("r", "Refresh"),
            ("f", "Hidden files"),
            ("p", "File panel"),
            ("c", "Copy path"),
            ("d", "Delete"),
            ("e", "Edit"),
            ("Ctrl+Z/Cmd+Z", "Undo"),
            ("Ctrl+D", "Shell CD"),
            ("h/?", "Help"),
            ("↑↓←→", "Navigate"),
            ("Cmd+Click", "Multi-select"),
        ]
        
        for i, (key, desc) in enumerate(shortcuts):
            if i > 0:
                help_text.append(" • ")
            help_text.append(f"{key}", style="bold cyan")
            help_text.append(f": {desc}", style="dim")
        
        # Add shell integration info
        help_text.append("\n\n")
        help_text.append("Shell Integration:", style="bold yellow")
        help_text.append("\n1. Source: ", style="dim")
        help_text.append("source scripts/vtree-shell-listener.sh", style="cyan")
        help_text.append("\n2. Start: ", style="dim")
        help_text.append("vtree_start_listener", style="cyan")
        help_text.append("\n3. Use ", style="dim")
        help_text.append("Ctrl+D", style="bold cyan")
        help_text.append(" to cd to selected directory", style="dim")
        
        self.update(help_text)


class FileEditModal(ModalScreen):
    """Modal screen for editing text files"""
    
    BINDINGS = [
        Binding("i", "enter_edit_mode", "Edit"),
        Binding("ctrl+s", "save_file", "Save"),
        Binding("escape", "close_modal", "Cancel"),
        Binding("ctrl+c", "close_modal", "Cancel", show=False),
    ]
    
    def __init__(self, file_path: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_path = file_path
        self.original_content = ""
        self.file_encoding = "utf-8"
        
    def compose(self) -> ComposeResult:
        """Create the modal layout"""
        with Container(id="edit-modal-container"):
            yield Static(f"Editing: {self.file_path.name}", id="edit-title")
            yield TextArea(id="edit-text-area", read_only=True)
            yield Static("Press 'i' to edit • Ctrl+S: Save • Esc: Cancel", id="edit-help")
    
    def on_mount(self) -> None:
        """Load file content when modal opens"""
        self.load_file()
        text_area = self.query_one(TextArea)
        text_area.focus()
        # Ensure TextArea starts in read-only mode
        text_area.read_only = True
    
    def load_file(self) -> None:
        """Load file content with proper encoding detection"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            content = ""
            
            for encoding in encodings:
                try:
                    with open(self.file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    self.file_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
            else:
                # If all encodings fail, try reading as binary and decode with errors='replace'
                with open(self.file_path, 'rb') as f:
                    binary_content = f.read()
                content = binary_content.decode('utf-8', errors='replace')
                self.file_encoding = 'utf-8'
            
            self.original_content = content
            text_area = self.query_one(TextArea)
            text_area.text = content
            
        except Exception as e:
            self.notify(f"Error loading file: {e}", severity="error")
            self.dismiss()
    
    def action_enter_edit_mode(self) -> None:
        """Enter edit mode by making TextArea editable"""
        text_area = self.query_one(TextArea)
        text_area.read_only = False
        # Update help text to show we're now in edit mode
        help_static = self.query_one("#edit-help")
        help_static.update("Editing mode • Ctrl+S: Save • Esc: Cancel")
    
    def action_save_file(self) -> None:
        """Save the file with current content"""
        try:
            text_area = self.query_one(TextArea)
            content = text_area.text
            
            # Add undo action if content changed
            if content != self.original_content and hasattr(self.app, 'undo_manager'):
                self.app.undo_manager.add_edit_action(self.file_path, self.original_content)
            
            # Save with the same encoding as original (or utf-8 if detection failed)
            with open(self.file_path, 'w', encoding=self.file_encoding, newline='') as f:
                f.write(content)
            
            self.notify(f"File saved: {self.file_path.name}", severity="information")
            self.dismiss(True)  # Return True to indicate file was saved
            
        except Exception as e:
            self.notify(f"Error saving file: {e}", severity="error")
    
    def action_close_modal(self) -> None:
        """Close modal without saving"""
        text_area = self.query_one(TextArea)
        if text_area.text != self.original_content:
            # Content has changed, show confirmation (for now just close)
            # TODO: Add confirmation dialog
            pass
        self.dismiss(False)  # Return False to indicate file was not saved


class VTreeApp(App):
    """A Textual app for displaying project trees."""
    
    CSS = """
    Screen {
        background: #1e1e1e;
        color: #d4d4d4;
    }
    
    #tree-container {
        height: 1fr;
        border: solid #3e3e3e;
        border-title-color: #808080;
    }
    
    #file-list-container {
        height: 1fr;
        max-height: 50%;
        border: solid #3e3e3e;
        border-title-color: #808080;
        margin-top: 1;
        background: #252526;
    }
    
    #info-container {
        height: auto;
        /* Increase to allow image previews */
        max-height: 18;
        border: solid #3e3e3e;
        border-title-color: #808080;
        margin-top: 1;
        background: #252526;
    }
    
    .hidden {
        display: none;
    }
    
    FileTree {
        height: 100%;
        background: #252526;
        color: #d4d4d4;
        scrollbar-color: #424242;
        scrollbar-color-hover: #4ec9b0;
    }
    
    InfoPanel {
        height: auto;
        padding: 1;
        background: #252526;
        color: #d4d4d4;
    }
    
    HelpPanel {
        height: auto;
        padding: 1;
        background: #252526;
        color: #808080;
    }
    
    FileListPanel {
        height: 100%;
        background: #252526;
        color: #d4d4d4;
    }
    
    DataTable > .datatable--header {
        background: #2d2d30;
        color: #cccccc;
    }
    
    DataTable > .datatable--cursor {
        background: #094771;
        color: #4ec9b0;
    }
    
    Tree > .tree--cursor {
        background: #094771;
        color: #4ec9b0;
    }
    
    Tree > .tree--highlight {
        background: #2a2d2e;
    }
    
    Header {
        background: #2d2d30;
        color: #cccccc;
    }
    
    Footer {
        background: #2d2d30;
        color: #808080;
    }
    
    /* File Edit Modal Styling */
    FileEditModal {
        align: center middle;
    }
    
    #edit-modal-container {
        width: 80%;
        height: 80%;
        background: #1e1e1e;
        border: solid #4ec9b0;
        border-title-color: #4ec9b0;
    }
    
    #edit-title {
        height: auto;
        padding: 1;
        background: #2d2d30;
        color: #4ec9b0;
        text-align: center;
    }
    
    #edit-text-area {
        height: 1fr;
        background: #1e1e1e;
        color: #d4d4d4;
        border: none;
        scrollbar-color: #424242;
        scrollbar-color-hover: #4ec9b0;
    }
    
    #edit-help {
        height: auto;
        padding: 1;
        background: #2d2d30;
        color: #808080;
        text-align: center;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("h,question_mark", "toggle_help", "Help"),
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("f", "toggle_hidden", "Hidden Files"),
        Binding("p", "toggle_file_panel", "File Panel"),
        Binding("c", "copy_path", "Copy Path"),
        Binding("d", "delete_selected", "Delete"),
        Binding("e", "edit_file", "Edit"),
        Binding("ctrl+z,cmd+z", "undo", "Undo"),
        Binding("ctrl+d", "shell_cd", "Shell CD"),
    ]

    show_help = reactive(False)
    show_hidden = reactive(False)
    show_file_panel = reactive(False)
    current_selection = reactive(None)

    def __init__(self, root_path: str = "."):
        super().__init__()
        self.root_path = Path(root_path).resolve()
        self.title = f"vtree - {self.root_path.name}"
        self.sub_title = str(self.root_path)
        self._file_system_state = {}
        self._poll_timer = None
        self._changed_items = {}  # Track changed items with timestamps
        self._change_timers = {}  # Track timers for reverting colors
        self._settings = self._load_settings()
        self.undo_manager = UndoManager()  # Initialize undo manager
        # Initialize IPC client with configured pipe path
        pipe_path = self._settings.get("shell_pipe_path", "/tmp/vtree_ipc")
        self.ipc_client = IPCClient(pipe_path)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        
        with Vertical():
            tree_container = Container(id="tree-container")
            tree_container.border_title = "Folders"
            tree_container.add_class("tree-container")
            with tree_container:
                yield FileTree(self.root_path, self.show_hidden, show_files_inline=not self.show_file_panel, settings=self._settings, id="file-tree")
            
            file_list_container = Container(id="file-list-container", classes="hidden" if not self.show_file_panel else "")
            file_list_container.border_title = "Files"
            with file_list_container:
                yield FileListPanel(id="file-list-panel")
            
            with Container(id="info-container"):
                yield InfoPanel(id="info-panel")
                yield HelpPanel(id="help-panel", classes="hidden" if not self.show_help else "")
        
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts."""
        # Apply loaded settings
        self.show_hidden = self._settings["show_hidden"]
        self.show_file_panel = self._settings["show_file_panel"]
        
        tree = self.query_one(FileTree)
        tree.focus()
        
        # Update tree with loaded settings
        tree.refresh_tree(self.show_hidden, not self.show_file_panel)
        
        # Show/hide file panel based on settings
        if self.show_file_panel:
            file_list_container = self.query_one("#file-list-container")
            file_list_container.remove_class("hidden")
            file_list_panel = self.query_one(FileListPanel)
            file_list_panel.update_files(self.root_path)
        
        # Start polling for file system changes
        self._start_file_system_polling()

    def on_unmount(self) -> None:
        """Called when app shuts down."""
        # Clean up undo manager temporary files
        if hasattr(self, 'undo_manager'):
            self.undo_manager.cleanup()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle tree node selection."""
        self._update_current_selection(event.node)
    
    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        """Handle tree node highlighting (keyboard navigation)."""
        self._update_current_selection(event.node)
    
    def _update_current_selection(self, node) -> None:
        """Update current selection from tree node."""
        if node and node.data:
            path = node.data["path"]
            file_type = node.data["type"]
            size = node.data.get("size")
            
            # Store current selection for copy functionality and actions
            self.current_selection = {"path": path, "type": file_type}
            
            # Update info panel
            info_panel = self.query_one(InfoPanel)
            info_panel.update_info(path, file_type, size)
            
            # Update file list panel if it's visible and we selected a directory
            if self.show_file_panel and file_type == "dir":
                file_list_panel = self.query_one(FileListPanel)
                file_list_panel.update_files(path)

    def on_data_table_row_selected(self, event) -> None:
        """Handle file list panel row selection"""
        if self.show_file_panel:
            file_list_panel = self.query_one(FileListPanel)
            if file_list_panel.current_directory:
                try:
                    # Use the event's cursor_row to get the filename
                    if hasattr(event, 'cursor_row') and event.cursor_row < len(file_list_panel.rows):
                        # Get the filename from the first column of the selected row
                        row_data = file_list_panel.get_row_at(event.cursor_row)
                        if row_data and len(row_data) > 0:
                            # Strip rich markup from filename
                            filename_raw = str(row_data[0])
                            import re
                            filename = re.sub(r'\[/?[^\]]*\]', '', filename_raw).strip()
                            if filename != "Permission denied" and filename:
                                file_path = file_list_panel.current_directory / filename
                                if file_path.exists() and file_path.is_file():
                                    # Update current selection to this file
                                    self.current_selection = {"path": file_path, "type": "file"}
                                    # Update info panel
                                    info_panel = self.query_one(InfoPanel)
                                    try:
                                        size = file_path.stat().st_size
                                        info_panel.update_info(file_path, "file", size)
                                    except (OSError, PermissionError):
                                        info_panel.update_info(file_path, "file", None)
                except Exception as e:
                    # If the above doesn't work, try cursor_coordinate approach as fallback
                    try:
                        if file_list_panel.cursor_coordinate is not None:
                            filename_raw = str(file_list_panel.get_cell_at(file_list_panel.cursor_coordinate.replace(column=0)))
                            import re
                            filename = re.sub(r'\[/?[^\]]*\]', '', filename_raw).strip()
                            if filename != "Permission denied" and filename:
                                file_path = file_list_panel.current_directory / filename
                                if file_path.exists() and file_path.is_file():
                                    self.current_selection = {"path": file_path, "type": "file"}
                    except Exception:
                        pass

    def action_refresh(self) -> None:
        """Refresh the file tree."""
        tree = self.query_one(FileTree)
        tree.refresh_tree(self.show_hidden)

    def action_toggle_help(self) -> None:
        """Toggle the help panel."""
        self.show_help = not self.show_help
        help_panel = self.query_one(HelpPanel)
        
        if self.show_help:
            help_panel.remove_class("hidden")
        else:
            help_panel.add_class("hidden")

    def action_toggle_hidden(self) -> None:
        """Toggle showing hidden files."""
        self.show_hidden = not self.show_hidden
        tree = self.query_one(FileTree)
        tree.refresh_tree(self.show_hidden)
        # Save settings when changed
        self._save_settings()

    def action_toggle_file_panel(self) -> None:
        """Toggle the file list panel."""
        self.show_file_panel = not self.show_file_panel
        file_list_container = self.query_one("#file-list-container")
        tree = self.query_one(FileTree)
        
        if self.show_file_panel:
            file_list_container.remove_class("hidden")
            tree.refresh_tree(show_files_inline=False)
            # Also update the file list panel with root directory files
            file_list_panel = self.query_one(FileListPanel)
            file_list_panel.update_files(self.root_path)
        else:
            file_list_container.add_class("hidden")
            tree.refresh_tree(show_files_inline=True)
        
        # Save settings when changed
        self._save_settings()

    def action_copy_path(self) -> None:
        """Copy the current path to clipboard."""
        if not self.current_selection:
            return
        
        path = self.current_selection["path"]
        file_type = self.current_selection["type"]
        
        # For files, copy the parent directory path
        # For folders, copy the folder path itself
        if file_type == "file":
            copy_path = str(path.parent)
        else:
            copy_path = str(path)
        
        try:
            # Try to copy to clipboard using pbcopy (macOS) or xclip (Linux)
            if sys.platform == "darwin":
                subprocess.run(["pbcopy"], input=copy_path, text=True, check=True)
            elif sys.platform.startswith("linux"):
                subprocess.run(["xclip", "-selection", "clipboard"], input=copy_path, text=True, check=True)
            else:
                # Fallback: print the path for manual copying
                self.bell()
                return
            
            # Visual feedback - update info panel with copied path message
            info_panel = self.query_one(InfoPanel)
            from rich.text import Text
            feedback_text = Text()
            feedback_text.append("Path copied to clipboard: ", style="bold green")
            feedback_text.append(copy_path, style="dim")
            info_panel.update(feedback_text)
            
            # Reset to normal info after delay
            def reset_info():
                if self.current_selection:
                    path = self.current_selection["path"]
                    file_type = self.current_selection["type"]
                    size = None
                    if file_type == "file":
                        try:
                            size = path.stat().st_size
                        except (OSError, PermissionError):
                            pass
                    info_panel.update_info(path, file_type, size)
            
            self.set_timer(2.0, reset_info)
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # If clipboard copy fails, just ring the bell
            self.bell()

    def action_edit_file(self) -> None:
        """Open file edit modal for the selected file."""
        # Get the file to edit (similar logic to delete_selected)
        tree = self.query_one(FileTree)
        selected_paths = tree.get_selected_paths()
        file_to_edit = None
        
        # If we're in file panel mode and nothing is multi-selected, try to get the current file
        if not selected_paths and self.show_file_panel:
            file_list_panel = self.query_one(FileListPanel)
            if file_list_panel.current_directory and file_list_panel.cursor_coordinate is not None:
                try:
                    # Get the currently highlighted file directly
                    row_index = file_list_panel.cursor_coordinate.row
                    if 0 <= row_index < len(file_list_panel.rows):
                        row_data = file_list_panel.get_row_at(row_index)
                        if row_data and len(row_data) > 0:
                            # Strip rich markup from filename to get the actual filename
                            filename_raw = str(row_data[0])
                            # Remove rich markup patterns like [color]text[/color] to get plain filename
                            import re
                            filename = re.sub(r'\[/?[^\]]*\]', '', filename_raw).strip()
                            if filename != "Permission denied" and filename:
                                file_path = file_list_panel.current_directory / filename
                                if file_path.exists() and file_path.is_file():
                                    file_to_edit = file_path
                except Exception:
                    # Fallback: try using get_cell_at method
                    try:
                        filename_raw = str(file_list_panel.get_cell_at(file_list_panel.cursor_coordinate.replace(column=0)))
                        # Remove rich markup patterns to get plain filename
                        import re
                        filename = re.sub(r'\[/?[^\]]*\]', '', filename_raw).strip()
                        if filename != "Permission denied" and filename:
                            file_path = file_list_panel.current_directory / filename
                            if file_path.exists() and file_path.is_file():
                                file_to_edit = file_path
                    except Exception:
                        pass
        
        # If nothing from file panel, check selected paths
        if not file_to_edit and selected_paths:
            # Only edit if exactly one file is selected
            if len(selected_paths) == 1 and selected_paths[0].is_file():
                file_to_edit = selected_paths[0]
        
        # If still nothing, try current selection
        if not file_to_edit and self.current_selection:
            path = self.current_selection["path"]
            if path.is_file():
                file_to_edit = path
        
        if not file_to_edit:
            self.notify("No file selected for editing", severity="warning")
            return
        
        # Check if it's a text file (basic heuristic)
        if not self._is_text_file(file_to_edit):
            self.notify(f"Cannot edit binary file: {file_to_edit.name}", severity="warning")
            return
        
        # Open the edit modal
        def handle_edit_result(result):
            if result:  # File was saved
                # Refresh views to show any changes
                self.action_refresh()
                if self.show_file_panel:
                    file_list_panel = self.query_one(FileListPanel)
                    if file_list_panel.current_directory:
                        file_list_panel.update_files(file_list_panel.current_directory)
        
        self.push_screen(FileEditModal(file_to_edit), handle_edit_result)
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if a file is likely a text file"""
        # Check common text file extensions
        text_extensions = {
            '.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml',
            '.md', '.rst', '.conf', '.cfg', '.ini', '.log', '.sh', '.bash',
            '.sql', '.csv', '.tsv', '.env', '.gitignore', '.dockerfile',
            '.c', '.cpp', '.h', '.hpp', '.java', '.kt', '.swift', '.go',
            '.rs', '.php', '.rb', '.pl', '.r', '.scala', '.clj', '.hs',
            '.lua', '.vim', '.el', '.lisp', '.ml', '.fs', '.pas', '.ada',
            '.tsx', '.jsx', '.ts', '.vue', '.svelte', '.dart', '.nim'
        }
        
        if file_path.suffix.lower() in text_extensions:
            return True
        
        # For files without extensions or unknown extensions, try to detect
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)  # Read first 1KB
            
            # Check if it contains mostly printable characters
            if not chunk:
                return True  # Empty file is editable
            
            # Count printable characters
            printable_chars = sum(1 for byte in chunk if 32 <= byte <= 126 or byte in [9, 10, 13])
            ratio = printable_chars / len(chunk)
            
            return ratio > 0.7  # If >70% printable, consider it text
            
        except Exception:
            return False

    def action_undo(self) -> None:
        """Undo the last action"""
        try:
            if not self.undo_manager.undo_stack:
                self.notify("Nothing to undo", severity="information")
                return
                
            action = self.undo_manager.undo_last()
            if action:
                # Show success message
                info_panel = self.query_one(InfoPanel)
                from rich.text import Text
                undo_text = Text()
                
                if action.action_type == ActionType.DELETE_FILE:
                    undo_text.append(f"📄 Restored: {action.original_path.name}", style="bold green")
                elif action.action_type == ActionType.DELETE_FOLDER:
                    undo_text.append(f"📁 Restored: {action.original_path.name}", style="bold green")
                elif action.action_type == ActionType.EDIT_FILE:
                    undo_text.append(f"✏️ Reverted: {action.original_path.name}", style="bold green")
                
                info_panel.update(undo_text)
                
                # Refresh the tree
                self.action_refresh()
                
                # Also refresh the file panel if visible
                if self.show_file_panel:
                    file_list_panel = self.query_one(FileListPanel)
                    if file_list_panel.current_directory:
                        file_list_panel.update_files(file_list_panel.current_directory)
                
                # Set timer to restore normal info
                def restore_info():
                    if self.current_selection:
                        path = self.current_selection["path"]
                        # Check if path still exists after undo
                        if path.exists():
                            file_type = self.current_selection["type"]
                            size = None
                            if file_type == "file":
                                try:
                                    size = path.stat().st_size
                                except (OSError, PermissionError):
                                    pass
                            info_panel.update_info(path, file_type, size)
                        else:
                            # Path doesn't exist, clear info
                            info_panel.update("")
                
                self.set_timer(3.0, restore_info)
            else:
                # Undo failed or no action was returned
                self.notify("Could not undo action", severity="warning")
                
        except Exception as e:
            self.notify(f"Undo failed: {str(e)}", severity="error")
    
    def action_delete_selected(self) -> None:
        """Delete selected files/folders with confirmation."""
        tree = self.query_one(FileTree)
        selected_paths = tree.get_selected_paths()
        
        # If nothing is multi-selected, use current selection
        if not selected_paths and self.current_selection:
            path = self.current_selection["path"]
            # Don't allow deletion of the root directory
            if path == self.root_path:
                return
            selected_paths = [path]
        
        if not selected_paths:
            return
        
        # Remove duplicates
        selected_paths = list(set(selected_paths))
        
        # Show confirmation dialog
        self._show_delete_confirmation(selected_paths)
    
    def _show_delete_confirmation(self, paths: List[Path]) -> None:
        """Show delete confirmation dialog"""
        if len(paths) == 1:
            path = paths[0]
            if path.is_dir():
                # Count files in directory
                try:
                    file_count = sum(1 for _ in path.rglob('*') if _.is_file())
                    if file_count > 0:
                        message = f"This folder contains {file_count} files. Are you sure you want to delete this folder?"
                    else:
                        message = "Are you sure you want to delete this folder?"
                except (OSError, PermissionError):
                    message = "Are you sure you want to delete this folder?"
            else:
                message = "Are you sure you want to delete this file?"
        else:
            message = f"Are you sure you want to delete {len(paths)} files?"
        
        # Create simple confirmation using the info panel
        info_panel = self.query_one(InfoPanel)
        from rich.text import Text
        confirm_text = Text()
        confirm_text.append("DELETE CONFIRMATION\n", style="bold red")
        confirm_text.append(message + "\n", style="yellow")
        confirm_text.append("Press 'y' to confirm, 'n' to cancel", style="dim")
        info_panel.update(confirm_text)
        
        # Store paths for confirmation
        self._pending_deletion = paths
        
        # Enable confirmation mode
        self._awaiting_delete_confirmation = True
    
    def key_y(self) -> None:
        """Confirm deletion"""
        if hasattr(self, '_awaiting_delete_confirmation') and self._awaiting_delete_confirmation:
            self._awaiting_delete_confirmation = False
            if hasattr(self, '_pending_deletion'):
                self._perform_deletion(self._pending_deletion)
                delattr(self, '_pending_deletion')
    
    def key_n(self) -> None:
        """Cancel deletion"""
        if hasattr(self, '_awaiting_delete_confirmation') and self._awaiting_delete_confirmation:
            self._awaiting_delete_confirmation = False
            if hasattr(self, '_pending_deletion'):
                delattr(self, '_pending_deletion')
            
            # Restore info panel
            if self.current_selection:
                path = self.current_selection["path"]
                file_type = self.current_selection["type"]
                size = None
                if file_type == "file":
                    try:
                        size = path.stat().st_size
                    except (OSError, PermissionError):
                        pass
                info_panel = self.query_one(InfoPanel)
                info_panel.update_info(path, file_type, size)
    
    def _perform_deletion(self, paths: List[Path]) -> None:
        """Actually delete the files/folders"""
        deleted_count = 0
        failed_deletions = []
        
        for path in paths:
            try:
                # Add to undo manager before deleting
                undo_id = self.undo_manager.add_delete_action(path)
                
                # Perform the actual deletion
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                deleted_count += 1
                
            except (OSError, PermissionError) as e:
                failed_deletions.append((path.name, str(e)))
                # If deletion failed, we should remove the undo action that was just added
                # This is tricky because we need to identify the specific action
                # For now, let's just leave it as it will be cleaned up eventually
        
        # Clear selections from both tree and file panel
        tree = self.query_one(FileTree)
        tree.clear_selection()
        
        if self.show_file_panel:
            file_list_panel = self.query_one(FileListPanel)
            file_list_panel.clear_selection()
        
        # Show result in info panel
        info_panel = self.query_one(InfoPanel)
        from rich.text import Text
        result_text = Text()
        
        if deleted_count > 0:
            result_text.append(f"✓ Deleted {deleted_count} item(s)", style="bold green")
        
        if failed_deletions:
            if deleted_count > 0:
                result_text.append("\n")
            result_text.append(f"✗ Failed to delete {len(failed_deletions)} item(s):", style="bold red")
            for name, error in failed_deletions[:3]:  # Show first 3 errors
                result_text.append(f"\n  {name}: {error}", style="red")
            if len(failed_deletions) > 3:
                result_text.append(f"\n  ... and {len(failed_deletions) - 3} more", style="red")
        
        info_panel.update(result_text)
        
        # Refresh both the tree and file panel
        self.action_refresh()
        
        # Also refresh the file panel if it's visible
        if self.show_file_panel:
            file_list_panel = self.query_one(FileListPanel)
            if file_list_panel.current_directory:
                # Refresh the file panel with its current directory
                file_list_panel.update_files(file_list_panel.current_directory)
        
        # Set timer to restore normal info panel
        def restore_info():
            # Clear current selection if it was deleted
            if self.current_selection:
                path = self.current_selection["path"]
                if not path.exists():
                    # File was deleted, clear the selection
                    self.current_selection = None
                    info_panel.update("")
                else:
                    # File still exists, show its info
                    file_type = self.current_selection["type"]
                    size = None
                    if file_type == "file":
                        try:
                            size = path.stat().st_size
                        except (OSError, PermissionError):
                            pass
                    info_panel.update_info(path, file_type, size)
        
        self.set_timer(3.0, restore_info)
    
    def _get_file_system_state(self, path: Path, max_depth: int = 3, current_depth: int = 0) -> dict:
        """Get current state of the file system for change detection"""
        state = {}
        if current_depth >= max_depth:
            return state
            
        try:
            for item in path.iterdir():
                # Skip ignored patterns
                if any(pattern in item.name for pattern in ['.git', '__pycache__', 'node_modules', '.venv', '.DS_Store']):
                    continue
                
                try:
                    stat = item.stat()
                    relative_path = str(item.relative_to(self.root_path))
                    state[relative_path] = {
                        'mtime': stat.st_mtime,
                        'size': stat.st_size if item.is_file() else 0,
                        'is_dir': item.is_dir(),
                        'path': item
                    }
                    
                    # Recursively scan subdirectories
                    if item.is_dir():
                        subdir_state = self._get_file_system_state(item, max_depth, current_depth + 1)
                        state.update(subdir_state)
                        
                except (OSError, PermissionError):
                    pass
        except (OSError, PermissionError):
            pass
        return state
    
    def _start_file_system_polling(self):
        """Start polling the file system for changes"""
        # Get initial state
        self._file_system_state = self._get_file_system_state(self.root_path)
        
        # Schedule periodic checks
        self._poll_timer = self.set_interval(3.0, self._check_file_system_changes)
    
    def _check_file_system_changes(self):
        """Check for file system changes and refresh if needed"""
        current_state = self._get_file_system_state(self.root_path)
        
        # Find what has changed
        changed_items = set()
        
        # Check for modified or new items
        for name, info in current_state.items():
            if name not in self._file_system_state:
                # New item
                changed_items.add(name)
            elif info != self._file_system_state.get(name):
                # Modified item
                changed_items.add(name)
        
        # Check for deleted items
        for name in self._file_system_state:
            if name not in current_state:
                # Item was deleted - remove from changed tracking
                if name in self._changed_items:
                    del self._changed_items[name]
                if name in self._change_timers:
                    # Just remove the timer reference, let it expire naturally
                    del self._change_timers[name]
        
        # Update state and track changes
        if current_state != self._file_system_state:
            self._file_system_state = current_state
            
            # Mark new/modified items as changed
            current_time = time.time()
            for item_path in changed_items:
                # Store by filename for display purposes (but keep full path info)
                if '/' in item_path:
                    filename = item_path.split('/')[-1]
                else:
                    filename = item_path
                    
                self._changed_items[filename] = current_time
                # Set timer to revert color
                if filename in self._change_timers:
                    # Remove old timer reference, let it expire naturally
                    del self._change_timers[filename]
                timer = self.set_timer(
                    self._settings["file_notify_timer"], 
                    lambda f=filename: self._revert_item_color(f)
                )
                self._change_timers[filename] = timer
            
            # Show notification in info panel
            if changed_items:
                self._show_modification_notification()
            
            # Get the currently expanded nodes
            tree = self.query_one(FileTree)
            expanded_paths = self._get_expanded_paths(tree.root)
            
            # Refresh the tree with change information
            tree.changed_items = self._changed_items.copy()
            tree.refresh_tree(self.show_hidden, not self.show_file_panel)
            
            # Restore expanded state
            self._restore_expanded_paths(tree.root, expanded_paths)
            
            # Update file panel if visible
            if self.show_file_panel:
                file_list_panel = self.query_one(FileListPanel)
                if file_list_panel.current_directory:
                    file_list_panel.update_files(file_list_panel.current_directory)
    
    def _get_expanded_paths(self, node, paths=None):
        """Recursively get all expanded node paths"""
        if paths is None:
            paths = set()
        
        # Check if node is expanded using is_expanded property
        try:
            if hasattr(node, 'is_expanded') and node.is_expanded and node.data and node.data.get("path"):
                paths.add(str(node.data["path"]))
        except AttributeError:
            # For root node or nodes without is_expanded
            if node.data and node.data.get("path"):
                paths.add(str(node.data["path"]))
        
        # Safely iterate over children
        if hasattr(node, 'children'):
            for child in node.children:
                self._get_expanded_paths(child, paths)
        
        return paths
    
    def _restore_expanded_paths(self, node, expanded_paths):
        """Recursively restore expanded state of nodes"""
        if node.data and node.data.get("path"):
            path_str = str(node.data["path"])
            if path_str in expanded_paths:
                try:
                    node.expand()
                except AttributeError:
                    # Node might not have expand method
                    pass
        
        # Safely iterate over children
        if hasattr(node, 'children'):
            for child in node.children:
                self._restore_expanded_paths(child, expanded_paths)
    
    def _load_settings(self) -> dict:
        """Load settings from .vtree.conf or create default"""
        config_file = self.root_path / ".vtree.conf"
        settings = {
            "file_notify_timer": 120,  # Default 2 minutes
            "show_hidden": False,
            "show_file_panel": False,
            "theme": "dark",
            "hidden_file_color": "#4a4a4a",
            "changed_file_bg": "dark_red",
            "changed_file_fg": "white",
            "shell_integration_enabled": True,
            "shell_pipe_path": "/tmp/vtree_ipc",
            "default_editor": "",  # Empty means auto-detect
        }
        
        if not config_file.exists():
            # Create default config file
            self._create_default_config(config_file)
        
        try:
            config = configparser.ConfigParser()
            config.read(config_file)
            
            if "settings" in config:
                # Load all settings with type conversion
                for key, default_value in settings.items():
                    if key in config["settings"]:
                        if isinstance(default_value, bool):
                            settings[key] = config["settings"].getboolean(key)
                        elif isinstance(default_value, int):
                            settings[key] = config["settings"].getint(key)
                        else:
                            settings[key] = config["settings"][key]
        except Exception:
            # Fall back to defaults on any error
            pass
        
        return settings
    
    def _create_default_config(self, config_file: Path):
        """Create default .vtree.conf file"""
        config = configparser.ConfigParser()
        config["settings"] = {
            "file_notify_timer": "120",  # 2 minutes in seconds
            "show_hidden": "false",
            "show_file_panel": "false", 
            "theme": "dark",
            "hidden_file_color": "#4a4a4a",
            "changed_file_bg": "dark_red",
            "changed_file_fg": "white",
            "shell_integration_enabled": "true",
            "shell_pipe_path": "/tmp/vtree_ipc",
            "default_editor": "",
        }
        
        try:
            with open(config_file, 'w') as f:
                f.write("# VTree Configuration File\n")
                f.write("# Customize your vtree experience\n\n")
                f.write("# file_notify_timer: Time in seconds to show changed files (default: 120)\n")
                f.write("# show_hidden: Show hidden files by default (true/false)\n")
                f.write("# show_file_panel: Start with file panel mode (true/false)\n")
                f.write("# theme: Color theme (dark/light)\n")
                f.write("# hidden_file_color: Color for hidden files (hex color)\n")
                f.write("# changed_file_bg: Background color for changed files\n")
                f.write("# changed_file_fg: Text color for changed files\n")
                f.write("# shell_integration_enabled: Enable shell integration (true/false)\n")
                f.write("# shell_pipe_path: Path to named pipe for shell communication\n")
                f.write("# default_editor: Default editor command (empty = auto-detect)\n\n")
                config.write(f)
        except Exception:
            pass
    
    def _save_settings(self):
        """Save current settings to .vtree.conf"""
        config_file = self.root_path / ".vtree.conf"
        config = configparser.ConfigParser()
        
        # First, reload current config from disk to preserve manual edits
        if config_file.exists():
            try:
                config.read(config_file)
            except Exception:
                pass
        
        # Ensure settings section exists
        if "settings" not in config:
            config["settings"] = {}
        
        # Only update the settings that we manage programmatically
        config["settings"]["show_hidden"] = str(self.show_hidden).lower()
        config["settings"]["show_file_panel"] = str(self.show_file_panel).lower()
        
        # For other settings, use current values from self._settings only if they don't exist in config
        if "file_notify_timer" not in config["settings"]:
            config["settings"]["file_notify_timer"] = str(self._settings["file_notify_timer"])
        if "theme" not in config["settings"]:
            config["settings"]["theme"] = self._settings["theme"]
        if "hidden_file_color" not in config["settings"]:
            config["settings"]["hidden_file_color"] = self._settings["hidden_file_color"]
        if "changed_file_bg" not in config["settings"]:
            config["settings"]["changed_file_bg"] = self._settings["changed_file_bg"]
        if "changed_file_fg" not in config["settings"]:
            config["settings"]["changed_file_fg"] = self._settings["changed_file_fg"]
        
        try:
            with open(config_file, 'w') as f:
                f.write("# VTree Configuration File\n")
                f.write("# Customize your vtree experience\n\n")
                f.write("# file_notify_timer: Time in seconds to show changed files (default: 120)\n")
                f.write("# show_hidden: Show hidden files by default (true/false)\n")
                f.write("# show_file_panel: Start with file panel mode (true/false)\n")
                f.write("# theme: Color theme (dark/light)\n")
                f.write("# hidden_file_color: Color for hidden files (hex color)\n")
                f.write("# changed_file_bg: Background color for changed files\n")
                f.write("# changed_file_fg: Text color for changed files\n")
                f.write("# shell_integration_enabled: Enable shell integration (true/false)\n")
                f.write("# shell_pipe_path: Path to named pipe for shell communication\n")
                f.write("# default_editor: Default editor command (empty = auto-detect)\n\n")
                config.write(f)
        except Exception:
            pass
    
    def _revert_item_color(self, item_name: str):
        """Revert item color back to normal after timer expires"""
        if item_name in self._changed_items:
            del self._changed_items[item_name]
        if item_name in self._change_timers:
            del self._change_timers[item_name]
        
        # Refresh tree to update colors
        tree = self.query_one(FileTree)
        expanded_paths = self._get_expanded_paths(tree.root)
        tree.changed_items = self._changed_items.copy()
        tree.refresh_tree(self.show_hidden, not self.show_file_panel)
        self._restore_expanded_paths(tree.root, expanded_paths)
        
        # Also refresh the file panel if it's visible to show standard colors
        if self.show_file_panel:
            file_list_panel = self.query_one(FileListPanel)
            if file_list_panel.current_directory:
                file_list_panel.update_files(file_list_panel.current_directory)
    
    def _show_modification_notification(self):
        """Show notification about modified files"""
        info_panel = self.query_one(InfoPanel)
        notification_text = Text()
        notification_text.append("⚠️  Modified files present in the project tree", style="bold yellow on dark_red")
        info_panel.update(notification_text)
        
        # Set timer to restore normal info (let old timer expire naturally)
        if hasattr(self, '_notification_timer'):
            self._notification_timer = None
        
        self._notification_timer = self.set_timer(
            self._settings["file_notify_timer"],
            self._restore_info_panel
        )
    
    def _restore_info_panel(self):
        """Restore info panel to show current selection"""
        if self.current_selection:
            path = self.current_selection["path"]
            file_type = self.current_selection["type"]
            size = None
            if file_type == "file":
                try:
                    size = path.stat().st_size
                except (OSError, PermissionError):
                    pass
            info_panel = self.query_one(InfoPanel)
            info_panel.update_info(path, file_type, size)
    
    def action_shell_cd(self) -> None:
        """Send cd command to external shell for the current selection"""
        # Check if shell integration is enabled
        if not self._settings.get("shell_integration_enabled", True):
            self.notify("Shell integration is disabled in settings", severity="warning")
            return
            
        if not self.current_selection:
            self.notify("No directory selected", severity="warning")
            return
        
        path = self.current_selection["path"]
        
        # For files, cd to parent directory; for directories, cd to the directory itself
        if path.is_file():
            target_path = path.parent
        else:
            target_path = path
        
        # Send the cd command
        if self.ipc_client.is_available():
            success = self.ipc_client.send_cd_command(str(target_path))
            if success:
                self.notify(f"Sent 'cd {target_path}' to shell", severity="information")
            else:
                self.notify("Failed to send command to shell", severity="error")
        else:
            pipe_path = self._settings.get("shell_pipe_path", "/tmp/vtree_ipc")
            self.notify(f"Shell integration not available. Start listener: source scripts/vtree-shell-listener.sh && vtree_start_listener", severity="warning")


@click.command()
@click.argument('path', default='.', type=click.Path(exists=True))
def main(path: str):
    """
    vtree - A modern, interactive terminal-based file tree viewer
    
    PATH: Directory to display (default: current directory)
    """
    try:
        app = VTreeApp(path)
        app.run()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()