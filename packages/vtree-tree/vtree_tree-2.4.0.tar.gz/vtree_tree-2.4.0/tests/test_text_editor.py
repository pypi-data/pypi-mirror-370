"""Tests for text editor functionality"""
import pytest
from pathlib import Path
import tempfile
from unittest.mock import Mock, patch, MagicMock
from vtree.main import VTreeApp


class TestTextEditing:
    """Test text file detection and editing features"""
    
    def test_is_text_file_by_extension(self):
        """Test text file detection by extension"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = VTreeApp(tmpdir)
            
            # Common text files
            assert app._is_text_file(Path("test.txt")) is True
            assert app._is_text_file(Path("script.py")) is True
            assert app._is_text_file(Path("config.json")) is True
            assert app._is_text_file(Path("page.html")) is True
            assert app._is_text_file(Path("style.css")) is True
            assert app._is_text_file(Path("README.md")) is True
            assert app._is_text_file(Path(".gitignore")) is True
            
            # Programming languages
            assert app._is_text_file(Path("main.c")) is True
            assert app._is_text_file(Path("app.js")) is True
            assert app._is_text_file(Path("Main.java")) is True
            assert app._is_text_file(Path("server.go")) is True
            assert app._is_text_file(Path("lib.rs")) is True
            
            # Binary files (should return False)
            assert app._is_text_file(Path("image.jpg")) is False
            assert app._is_text_file(Path("video.mp4")) is False
            assert app._is_text_file(Path("archive.zip")) is False
    
    def test_is_text_file_by_content(self):
        """Test text file detection by content analysis"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = VTreeApp(tmpdir)
            
            # Create a text file without extension
            text_file = Path(tmpdir) / "textfile"
            text_file.write_text("This is plain text content\nWith multiple lines")
            assert app._is_text_file(text_file) is True
            
            # Create a binary file without extension
            binary_file = Path(tmpdir) / "binaryfile"
            binary_file.write_bytes(b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09')
            assert app._is_text_file(binary_file) is False
            
            # Empty file should be considered text
            empty_file = Path(tmpdir) / "emptyfile"
            empty_file.touch()
            assert app._is_text_file(empty_file) is True
    
    def test_is_text_file_mixed_content(self):
        """Test text file detection with mixed content"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app = VTreeApp(tmpdir)
            
            # File with mostly text but some binary
            mixed_file = Path(tmpdir) / "mixed"
            content = b"Hello World\n" * 50 + b'\x00\x01\x02'  # Mostly text
            mixed_file.write_bytes(content)
            
            # Should still be considered text if >70% printable
            assert app._is_text_file(mixed_file) is True


class TestFileSystemUtils:
    """Test file system utility functions"""
    
    def test_get_file_system_state(self):
        """Test getting file system state for change detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir).resolve()  # Use resolved path
            app = VTreeApp(str(tmppath))
            
            # Create test structure
            (tmppath / "file1.txt").write_text("content")
            subdir = tmppath / "subdir"
            subdir.mkdir()
            (subdir / "file2.txt").write_text("content2")
            
            # Get state
            state = app._get_file_system_state(tmppath, max_depth=2)
            
            # Check state contains files
            assert any("file1.txt" in key for key in state.keys())
            assert any("file2.txt" in key for key in state.keys())
            
            # Check state info
            for path, info in state.items():
                assert "mtime" in info
                assert "size" in info
                assert "is_dir" in info
                assert "path" in info