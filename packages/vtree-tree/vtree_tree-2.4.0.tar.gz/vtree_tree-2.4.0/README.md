# vtree-tree

A modern Python CLI application that provides a full-screen, interactive file tree viewer for the terminal. Built with Textual TUI framework and Rich for terminal formatting.

[![PyPI version](https://badge.fury.io/py/vtree-tree.svg)](https://badge.fury.io/py/vtree-tree)
[![Python](https://img.shields.io/pypi/pyversions/vtree-tree.svg)](https://pypi.org/project/vtree-tree/)

## Features

- 🌳 **Interactive file tree** - Navigate with mouse and keyboard
- 📁 **Dual view modes** - Toggle between inline files and separate file panel
- 📋 **Clipboard integration** - Copy paths with a single keystroke
- 🎨 **Clean interface** - Modern terminal-style dark theme without file type icons for better readability
- 👁️ **Hidden file toggle** - Show/hide dotfiles and system files
- 📊 **File details** - Human-readable file sizes and modification dates
- ⚡ **Smart filtering** - Automatically ignores common development artifacts (.git, __pycache__, node_modules, etc.)
- 🖱️ **Mouse support** - Full mouse navigation and selection
- 🔄 **Real-time browsing** - Refresh capability for dynamic file system viewing
- ✏️ **Built-in file editor** - Edit text files directly within vtree with syntax highlighting
- 🗑️ **Safe file operations** - Delete files and folders with confirmation prompts
- ↩️ **Undo system** - Undo deletions and edits with full file recovery
- 🎯 **Multi-selection** - Select multiple files/folders using Cmd+Click or Ctrl+Click

## Installation

```bash
pip install vtree-tree
```

## Usage

```bash
# View current directory
vtree

# View specific directory
vtree /path/to/directory

# Development - run from source
python3 -m vtree.main [path]

# Get help
vtree --help
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` / `Ctrl+C` | Quit |
| `r` | Refresh tree |
| `f` | Toggle hidden files |
| `p` | Toggle file panel mode |
| `c` | Copy current path to clipboard |
| `d` | Delete selected files/folders |
| `e` | Edit selected file in built-in editor |
| `Ctrl+Z` / `Cmd+Z` | Undo last action (delete/edit) |
| `h` / `?` | Toggle help panel |
| `↑↓←→` | Navigate tree |
| `Cmd+Click` / `Ctrl+Click` | Multi-select files/folders |
| `y` | Confirm deletion |
| `n` | Cancel deletion |

## View Modes

### Inline Mode (Default)
Files and directories are shown together in a traditional tree structure.

### Panel Mode
Press `p` to toggle panel mode where:
- Left panel shows the directory tree
- Right panel shows files in the selected directory with details (size, date)
- Perfect for browsing large directories with detailed file information

## Copy to Clipboard

Press `c` to copy the current path to your clipboard:
- **On a folder**: Copies the folder path
- **On a file**: Copies the complete file path

Great for quickly navigating in terminal sessions:
```bash
vtree
# Press 'c' on desired folder/file
cd # Paste path here (for folders) or use file path directly
```

## File Operations

### Editing Files
Press `e` on any text file to open it in the built-in editor:
- **Ctrl+S**: Save changes
- **Esc**: Cancel and close editor
- Supports syntax highlighting and handles various encodings
- Automatically creates undo points for edited files

### Deleting Files & Folders
Press `d` to delete selected items:
- Shows confirmation dialog with file count for folders
- Press `y` to confirm deletion or `n` to cancel
- Supports multi-selection - delete multiple items at once
- All deletions can be undone with **Ctrl+Z** / **Cmd+Z**

### Undo System
Press **Ctrl+Z** / **Cmd+Z** to undo the last action:
- Restores deleted files and folders completely
- Reverts file edits to their previous content
- Maintains up to 50 undo actions in history
- Automatic cleanup of temporary backup files

## Requirements

- Python 3.8+
- Works on macOS, Linux, and Windows
- Terminal with color support

## Architecture

Built with a clean, modular architecture:

- **VTreeApp**: Main Textual application class that orchestrates the UI
- **FileTree**: Custom Tree widget that handles file system navigation and display
- **FileListPanel**: DataTable showing files with size and date information  
- **InfoPanel**: Shows details about selected files/directories  
- **HelpPanel**: Displays keyboard shortcuts
- **FileNode**: Data class for representing file system entries

## Dependencies

- `textual` - Modern TUI framework
- `rich` - Terminal formatting and colors
- `click` - Command-line interface

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.