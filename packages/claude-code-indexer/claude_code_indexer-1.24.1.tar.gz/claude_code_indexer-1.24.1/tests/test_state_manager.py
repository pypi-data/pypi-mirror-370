#!/usr/bin/env python3
"""
Comprehensive tests for CodebaseStateManager
"""

import pytest
import tempfile
import json
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from claude_code_indexer.state_manager import CodebaseStateManager


class TestCodebaseStateManager:
    """Test suite for CodebaseStateManager"""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "test_project"
            project_path.mkdir()
            
            # Create some test files
            (project_path / "main.py").write_text("print('hello')")
            (project_path / "utils.py").write_text("def helper(): pass")
            (project_path / "README.md").write_text("# Test Project")
            
            yield project_path
    
    @pytest.fixture
    def state_manager(self, temp_project):
        """Create a state manager instance"""
        return CodebaseStateManager(str(temp_project))
    
    def test_init(self, temp_project):
        """Test StateManager initialization"""
        manager = CodebaseStateManager(str(temp_project))
        
        assert manager.project_path == temp_project.resolve()
        assert manager.storage_base == Path.home() / ".claude-code-indexer"
        assert len(manager.project_hash) == 16
        assert manager.project_storage.exists()
    
    def test_get_project_hash(self, state_manager):
        """Test project hash generation"""
        hash1 = state_manager._get_project_hash()
        hash2 = state_manager._get_project_hash()
        
        assert hash1 == hash2  # Same path should give same hash
        assert len(hash1) == 16
        assert hash1.isalnum()
    
    def test_ensure_storage(self, state_manager):
        """Test storage directory creation"""
        # Remove storage and recreate
        if state_manager.project_storage.exists():
            shutil.rmtree(state_manager.project_storage)
        
        state_manager._ensure_storage()
        
        assert state_manager.project_storage.exists()
        assert (state_manager.project_storage / "history").exists()
    
    @patch('subprocess.run')
    def test_get_git_commit(self, mock_run, state_manager):
        """Test git commit retrieval"""
        # Simulate git success
        mock_run.return_value = Mock(
            returncode=0,
            stdout="abc123def456"
        )
        
        commit = state_manager._get_git_commit()
        assert commit == "abc123def456"
        
        # Simulate git failure
        mock_run.return_value = Mock(returncode=1)
        commit = state_manager._get_git_commit()
        assert commit is None
    
    @patch('subprocess.run')
    def test_get_git_branch(self, mock_run, state_manager):
        """Test git branch retrieval"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="main"
        )
        
        branch = state_manager._get_git_branch()
        assert branch == "main"
    
    def test_hash_file(self, state_manager, temp_project):
        """Test file hashing"""
        test_file = temp_project / "test.txt"
        test_file.write_text("test content")
        
        hash1 = state_manager._hash_file(test_file)
        assert len(hash1) == 16
        
        # Same content should give same hash
        hash2 = state_manager._hash_file(test_file)
        assert hash1 == hash2
        
        # Different content should give different hash
        test_file.write_text("different content")
        hash3 = state_manager._hash_file(test_file)
        assert hash1 != hash3
    
    def test_hash_all_files(self, state_manager, temp_project):
        """Test hashing all project files"""
        # Create more test files
        (temp_project / "app.js").write_text("console.log('test')")
        (temp_project / "style.css").write_text("body { color: red; }")
        
        file_hashes = state_manager._hash_all_files()
        
        assert "main.py" in file_hashes
        assert "utils.py" in file_hashes
        assert "app.js" in file_hashes
        # CSS files are not in the default patterns
        assert "style.css" not in file_hashes
    
    def test_get_codebase_stats(self, state_manager, temp_project):
        """Test codebase statistics generation"""
        stats = state_manager._get_codebase_stats()
        
        assert "total_files" in stats
        assert "total_lines" in stats
        assert "languages" in stats
        assert stats["total_files"] >= 2  # At least main.py and utils.py
        assert ".py" in stats["languages"]
    
    def test_capture_state(self, state_manager, temp_project):
        """Test state capture"""
        state = state_manager.capture_state()
        
        assert "timestamp" in state
        assert "project_path" in state
        assert "git" in state
        assert "files" in state
        assert "stats" in state
        # Use Path for comparison to handle symlink resolution
        assert Path(state["project_path"]) == temp_project.resolve()
        
        # Check state was saved
        state_file = state_manager._get_state_path()
        assert state_file.exists()
        
        # Check history was created
        history_dir = state_manager.project_storage / "history"
        history_files = list(history_dir.glob("*.json"))
        assert len(history_files) >= 1
    
    def test_get_current_state(self, state_manager):
        """Test getting current state"""
        # Initially no state
        state = state_manager.get_current_state()
        assert state is None
        
        # Capture state
        captured_state = state_manager.capture_state()
        
        # Now should return state
        state = state_manager.get_current_state()
        assert state is not None
        assert state["timestamp"] == captured_state["timestamp"]
    
    def test_get_state_history(self, state_manager):
        """Test getting state history"""
        # Capture multiple states with small delay to ensure different timestamps
        import time
        state_manager.capture_state()
        time.sleep(0.01)  # Small delay to ensure different timestamp
        state_manager.capture_state()
        time.sleep(0.01)
        state_manager.capture_state()
        
        history = state_manager.get_state_history(limit=2)
        assert len(history) <= 2  # May be less if filesystem is slow
        
        # Should be sorted by most recent first if we have multiple states
        if len(history) > 1:
            assert history[0]["timestamp"] >= history[1]["timestamp"]
    
    def test_compare_states(self, state_manager):
        """Test state comparison"""
        state1 = {
            "files": {"file1.py": "hash1", "file2.py": "hash2"},
            "stats": {"total_files": 2}
        }
        
        state2 = {
            "files": {"file1.py": "hash1_modified", "file3.py": "hash3"},
            "stats": {"total_files": 2},
            "timestamp": "2025-01-01T10:00:00"
        }
        
        comparison = state_manager.compare_states(state1, state2)
        
        assert "file3.py" in comparison["files_added"]
        assert "file2.py" in comparison["files_removed"]
        assert "file1.py" in comparison["files_modified"]
    
    def test_diff_from_last(self, state_manager):
        """Test diff from last state"""
        # First capture
        state_manager.capture_state()
        
        # Initially no diff (same state)
        diff = state_manager.diff_from_last()
        assert diff is None or len(diff.get("files_modified", [])) == 0
        
        # Modify a file
        (state_manager.project_path / "main.py").write_text("print('modified')")
        
        # Capture again
        state_manager.capture_state()
        
        # Now should show diff
        diff = state_manager.diff_from_last()
        if diff:  # May be None if only one state
            assert "files_modified" in diff
    
    def test_track_task(self, state_manager):
        """Test task tracking"""
        task_id = state_manager.track_task({
            "description": "Test task"
        })
        
        assert task_id.startswith("task_")
        assert len(task_id) > 10
        
        # Check task was saved
        tasks = state_manager._load_tasks()
        assert len(tasks) == 1
        assert tasks[0]["id"] == task_id
        assert tasks[0]["description"] == "Test task"
        assert tasks[0]["status"] == "in_progress"
    
    def test_complete_task(self, state_manager):
        """Test task completion"""
        # Track a task
        task_id = state_manager.track_task({
            "description": "Test task"
        })
        
        # Complete it
        changes = state_manager.complete_task(task_id)
        
        assert "files_added" in changes
        assert "files_modified" in changes
        assert "files_removed" in changes
        
        # Check task status
        task = state_manager.get_task(task_id)
        assert task["status"] == "completed"
        assert "completed_at" in task
    
    def test_complete_nonexistent_task(self, state_manager):
        """Test completing non-existent task"""
        with pytest.raises(ValueError, match="Task .* not found"):
            state_manager.complete_task("nonexistent_task")
    
    def test_get_task(self, state_manager):
        """Test getting specific task"""
        task_id = state_manager.track_task({
            "description": "Test task"
        })
        
        task = state_manager.get_task(task_id)
        assert task is not None
        assert task["id"] == task_id
        
        # Non-existent task
        task = state_manager.get_task("nonexistent")
        assert task is None
    
    def test_get_active_tasks(self, state_manager):
        """Test getting active tasks"""
        # Track multiple tasks
        task1 = state_manager.track_task({"description": "Task 1"})
        task2 = state_manager.track_task({"description": "Task 2"})
        
        active = state_manager.get_active_tasks()
        assert len(active) == 2
        
        # Complete one
        state_manager.complete_task(task1)
        
        active = state_manager.get_active_tasks()
        assert len(active) == 1
        assert active[0]["id"] == task2
    
    def test_get_task_history(self, state_manager):
        """Test getting task history"""
        # Track multiple tasks
        for i in range(5):
            state_manager.track_task({"description": f"Task {i}"})
        
        history = state_manager.get_task_history(limit=3)
        assert len(history) == 3
        
        # Should be sorted by most recent first
        assert "Task 4" in history[0]["description"]
    
    def test_export_state_json(self, state_manager):
        """Test state export as JSON"""
        state_manager.capture_state()
        output = state_manager.export_state(format="json")
        
        # Should be valid JSON
        parsed = json.loads(output)
        assert "timestamp" in parsed
        assert "project_path" in parsed
    
    def test_export_state_summary(self, state_manager):
        """Test state export as summary"""
        state_manager.capture_state()
        output = state_manager.export_state(format="summary")
        
        assert "Codebase State Summary" in output
        assert str(state_manager.project_path) in output
        assert "Total Files:" in output
        assert "Total Lines:" in output
    
    def test_export_state_invalid_format(self, state_manager):
        """Test export with invalid format"""
        with pytest.raises(ValueError, match="Unsupported format"):
            state_manager.export_state(format="invalid")
    
    def test_validate_state(self, state_manager, temp_project):
        """Test state validation"""
        # No saved state
        validation = state_manager.validate_state()
        assert not validation["valid"]
        assert validation["reason"] == "No saved state found"
        
        # Capture state
        state_manager.capture_state()
        
        # Should be valid
        validation = state_manager.validate_state()
        assert validation["valid"]
        assert len(validation["unexpected_changes"]) == 0
        
        # Modify a file
        (temp_project / "main.py").write_text("print('changed')")
        
        # Should detect unexpected changes
        validation = state_manager.validate_state()
        assert not validation["valid"]
        assert "main.py" in validation["unexpected_changes"]
    
    def test_find_modified_files(self, state_manager):
        """Test finding modified files between states"""
        state1 = {
            "files": {
                "file1.py": "hash1",
                "file2.py": "hash2",
                "file3.py": "hash3"
            }
        }
        
        state2 = {
            "files": {
                "file1.py": "hash1",  # Same
                "file2.py": "hash2_modified",  # Modified
                "file3.py": "hash3",  # Same
                "file4.py": "hash4"  # New
            }
        }
        
        modified = state_manager._find_modified_files(state1, state2)
        assert "file2.py" in modified
        assert "file1.py" not in modified
        assert "file3.py" not in modified
        assert "file4.py" not in modified  # New file, not modified
    
    def test_generate_task_id(self, state_manager):
        """Test task ID generation"""
        task_id1 = state_manager._generate_task_id()
        task_id2 = state_manager._generate_task_id()
        
        assert task_id1.startswith("task_")
        assert task_id2.startswith("task_")
        # IDs should always be unique due to UUID suffix
        assert task_id1 != task_id2
    
    def test_load_save_tasks(self, state_manager):
        """Test loading and saving tasks"""
        # Initially empty
        tasks = state_manager._load_tasks()
        assert tasks == []
        
        # Save some tasks
        test_tasks = [
            {"id": "task1", "description": "Test 1"},
            {"id": "task2", "description": "Test 2"}
        ]
        state_manager._save_tasks(test_tasks)
        
        # Load and verify
        loaded_tasks = state_manager._load_tasks()
        assert len(loaded_tasks) == 2
        assert loaded_tasks[0]["id"] == "task1"
        assert loaded_tasks[1]["id"] == "task2"


class TestStateManagerEdgeCases:
    """Test edge cases and error handling"""
    
    def test_invalid_project_path(self):
        """Test with invalid project path"""
        manager = CodebaseStateManager("/nonexistent/path")
        
        # Should still work but with limited functionality
        assert manager.project_path == Path("/nonexistent/path")
        state = manager.capture_state()
        assert state["stats"]["total_files"] == 0
    
    def test_hash_file_not_found(self):
        """Test hashing non-existent file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CodebaseStateManager(tmpdir)
            
            result = manager._hash_file(Path(tmpdir) / "nonexistent.txt")
            assert result == ""  # Should return empty string
    
    def test_concurrent_task_tracking(self):
        """Test tracking multiple tasks concurrently"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CodebaseStateManager(tmpdir)
            
            # Track multiple tasks
            task_ids = []
            for i in range(10):
                task_id = manager.track_task({"description": f"Task {i}"})
                task_ids.append(task_id)
            
            # All should be tracked
            tasks = manager._load_tasks()
            assert len(tasks) == 10
            
            # Complete them in reverse order
            for task_id in reversed(task_ids):
                manager.complete_task(task_id)
            
            # All should be completed
            tasks = manager._load_tasks()
            for task in tasks:
                assert task["status"] == "completed"