"""Tests for UndoManager functionality"""
import pytest
from pathlib import Path
import tempfile
import shutil
from vtree.main import UndoManager, ActionType, UndoAction
from datetime import datetime


class TestUndoManager:
    """Test the UndoManager class"""
    
    def test_undo_manager_creation(self):
        """Test creating an UndoManager"""
        manager = UndoManager(max_undo_history=10)
        
        assert manager.max_undo_history == 10
        assert len(manager.undo_stack) == 0
        assert manager.temp_dir.exists()
        
        # Cleanup
        manager.cleanup()
        assert not manager.temp_dir.exists()
    
    def test_add_delete_file_action(self):
        """Test adding a delete file action"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Hello, World!")
            
            manager = UndoManager()
            action_id = manager.add_delete_action(test_file)
            
            # Check action was added
            assert len(manager.undo_stack) == 1
            action = manager.undo_stack[0]
            assert action.id == action_id
            assert action.action_type == ActionType.DELETE_FILE
            assert action.original_path == test_file
            assert action.backup_path.exists()
            
            # Check backup content
            with open(action.backup_path, 'r') as f:
                assert f.read() == "Hello, World!"
            
            # Cleanup
            manager.cleanup()
    
    def test_add_delete_folder_action(self):
        """Test adding a delete folder action"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test directory with files
            test_dir = Path(tmpdir) / "testdir"
            test_dir.mkdir()
            (test_dir / "file1.txt").write_text("File 1")
            (test_dir / "file2.txt").write_text("File 2")
            
            manager = UndoManager()
            action_id = manager.add_delete_action(test_dir)
            
            # Check action was added
            assert len(manager.undo_stack) == 1
            action = manager.undo_stack[0]
            assert action.action_type == ActionType.DELETE_FOLDER
            assert action.backup_path.exists()
            assert (action.backup_path / "file1.txt").exists()
            assert (action.backup_path / "file2.txt").exists()
            
            # Cleanup
            manager.cleanup()
    
    def test_add_edit_action(self):
        """Test adding an edit action"""
        manager = UndoManager()
        test_path = Path("/tmp/test.txt")
        original_content = "Original content"
        
        action_id = manager.add_edit_action(test_path, original_content)
        
        # Check action was added
        assert len(manager.undo_stack) == 1
        action = manager.undo_stack[0]
        assert action.action_type == ActionType.EDIT_FILE
        assert action.original_path == test_path
        
        # Check backup content
        with open(action.backup_path, 'r') as f:
            assert f.read() == original_content
        
        # Cleanup
        manager.cleanup()
    
    def test_undo_delete_file(self):
        """Test undoing a file deletion"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and delete a file
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Hello, World!")
            
            manager = UndoManager()
            manager.add_delete_action(test_file)
            
            # Actually delete the file
            test_file.unlink()
            assert not test_file.exists()
            
            # Undo the deletion
            action = manager.undo_last()
            assert action is not None
            assert test_file.exists()
            assert test_file.read_text() == "Hello, World!"
            
            # Cleanup
            manager.cleanup()
    
    def test_undo_delete_folder(self):
        """Test undoing a folder deletion"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and delete a directory
            test_dir = Path(tmpdir) / "testdir"
            test_dir.mkdir()
            (test_dir / "file1.txt").write_text("File 1")
            
            manager = UndoManager()
            manager.add_delete_action(test_dir)
            
            # Actually delete the directory
            shutil.rmtree(test_dir)
            assert not test_dir.exists()
            
            # Undo the deletion
            action = manager.undo_last()
            assert action is not None
            assert test_dir.exists()
            assert (test_dir / "file1.txt").exists()
            assert (test_dir / "file1.txt").read_text() == "File 1"
            
            # Cleanup
            manager.cleanup()
    
    def test_undo_edit_file(self):
        """Test undoing a file edit"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file
            test_file = Path(tmpdir) / "test.txt"
            original_content = "Original content"
            test_file.write_text(original_content)
            
            manager = UndoManager()
            manager.add_edit_action(test_file, original_content)
            
            # Edit the file
            test_file.write_text("New content")
            
            # Undo the edit
            action = manager.undo_last()
            assert action is not None
            assert test_file.read_text() == original_content
            
            # Cleanup
            manager.cleanup()
    
    def test_max_undo_history(self):
        """Test that undo stack is trimmed to max size"""
        manager = UndoManager(max_undo_history=3)
        
        # Add 5 actions
        for i in range(5):
            path = Path(f"/tmp/test{i}.txt")
            manager.add_edit_action(path, f"Content {i}")
        
        # Should only have 3 actions
        assert len(manager.undo_stack) == 3
        
        # Check that oldest actions were removed
        paths = [action.original_path.name for action in manager.undo_stack]
        assert "test2.txt" in paths
        assert "test3.txt" in paths
        assert "test4.txt" in paths
        
        # Cleanup
        manager.cleanup()
    
    def test_undo_empty_stack(self):
        """Test undoing with empty stack"""
        manager = UndoManager()
        
        action = manager.undo_last()
        assert action is None
        
        # Cleanup
        manager.cleanup()
    
    def test_get_undo_info(self):
        """Test getting human-readable undo information"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = UndoManager()
            
            # Create actual files for delete actions
            file1 = Path(tmpdir) / "file1.txt"
            file1.write_text("content1")
            
            folder1 = Path(tmpdir) / "folder1"
            folder1.mkdir()
            
            # Add various actions
            manager.add_delete_action(file1)
            manager.add_delete_action(folder1)
            manager.add_edit_action(Path(tmpdir) / "file2.txt", "content")
            
            info = manager.get_undo_info()
            
            assert len(info) == 3
            assert "Edit file: file2.txt" in info[0]
            assert "Delete folder: folder1" in info[1]
            assert "Delete file: file1.txt" in info[2]
            
            # Cleanup
            manager.cleanup()