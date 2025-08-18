"""Tests for file utilities and FileNode"""
import pytest
from pathlib import Path
from vtree.main import FileNode, FileTree
import tempfile
import os


class TestFileNode:
    """Test FileNode dataclass"""
    
    def test_file_node_creation(self):
        """Test creating a FileNode"""
        path = Path("/tmp/test.txt")
        node = FileNode(path=path, is_dir=False, size=100)
        
        assert node.path == path
        assert node.is_dir is False
        assert node.size == 100
        assert node.children is None
    
    def test_directory_node_creation(self):
        """Test creating a directory FileNode"""
        path = Path("/tmp/testdir")
        node = FileNode(path=path, is_dir=True)
        
        assert node.path == path
        assert node.is_dir is True
        assert node.size is None
        assert node.children is None


class TestFileTreeUtilities:
    """Test FileTree utility methods"""
    
    def test_format_size(self):
        """Test file size formatting"""
        # Create a minimal FileTree instance
        tree = FileTree(Path("/tmp"), show_hidden=False)
        
        # Test various size formats
        assert tree.format_size(None) == ""
        assert tree.format_size(100) == " [dim](100 B)[/dim]"
        assert tree.format_size(1024) == " [dim](1.0 KB)[/dim]"
        assert tree.format_size(1536) == " [dim](1.5 KB)[/dim]"
        assert tree.format_size(1048576) == " [dim](1.0 MB)[/dim]"
        assert tree.format_size(1073741824) == " [dim](1.0 GB)[/dim]"
    
    def test_should_ignore(self):
        """Test ignore patterns"""
        tree = FileTree(Path("/tmp"), show_hidden=False)
        
        # Test hidden files
        assert tree.should_ignore(Path(".hidden")) is True
        # Note: .gitignore, .env.example, .github are only shown when show_hidden is True
        assert tree.should_ignore(Path("regular_file.txt")) is False
        
        # Test ignore patterns
        assert tree.should_ignore(Path("__pycache__")) is True
        assert tree.should_ignore(Path("node_modules")) is True
        assert tree.should_ignore(Path(".venv")) is True
        assert tree.should_ignore(Path("dist")) is True
        assert tree.should_ignore(Path("build")) is True
        
        # Test normal files
        assert tree.should_ignore(Path("main.py")) is False
        assert tree.should_ignore(Path("README.md")) is False
    
    def test_should_ignore_with_hidden_shown(self):
        """Test ignore patterns with hidden files shown"""
        tree = FileTree(Path("/tmp"), show_hidden=True)
        
        # Hidden files should not be ignored when show_hidden is True
        assert tree.should_ignore(Path(".hidden")) is False
        assert tree.should_ignore(Path(".config")) is False
        
        # But development artifacts should still be ignored
        assert tree.should_ignore(Path("__pycache__")) is True
        assert tree.should_ignore(Path("node_modules")) is True


class TestFileSystemIntegration:
    """Integration tests with real file system"""
    
    def test_get_file_size(self):
        """Test getting file size safely"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Hello, World!")
            temp_path = Path(f.name)
        
        try:
            tree = FileTree(Path("/tmp"), show_hidden=False)
            size = tree.get_file_size(temp_path)
            assert size == 13  # "Hello, World!" is 13 bytes
            
            # Test with directory
            assert tree.get_file_size(Path("/tmp")) is None
            
            # Test with non-existent file
            assert tree.get_file_size(Path("/tmp/non_existent_file.txt")) is None
        finally:
            os.unlink(temp_path)
    
    def test_populate_tree_structure(self):
        """Test tree population with a temporary directory structure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create test structure
            (tmppath / "file1.txt").write_text("content1")
            (tmppath / "file2.py").write_text("content2")
            subdir = tmppath / "subdir"
            subdir.mkdir()
            (subdir / "file3.txt").write_text("content3")
            
            # Create tree
            tree = FileTree(tmppath, show_hidden=False, show_files_inline=True)
            
            # Check root
            assert tree.root.data["path"] == tmppath
            assert tree.root.data["type"] == "dir"
            
            # The tree should have been populated
            assert len(tree.root.children) > 0