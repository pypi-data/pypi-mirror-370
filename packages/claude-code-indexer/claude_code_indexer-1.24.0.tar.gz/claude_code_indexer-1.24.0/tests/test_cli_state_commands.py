#!/usr/bin/env python3
"""
Tests for CLI state management commands
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

from claude_code_indexer.cli import cli


class TestCLIStateCommands:
    """Test suite for state management CLI commands"""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner"""
        return CliRunner()
    
    @pytest.fixture
    def temp_project(self):
        """Create temporary project directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "test_project"
            project_path.mkdir()
            
            # Create test files
            (project_path / "main.py").write_text("print('hello')")
            (project_path / "utils.py").write_text("def helper(): pass")
            
            yield project_path
    
    @patch('claude_code_indexer.cli.CodebaseStateManager')
    def test_state_capture_command(self, mock_manager_class, runner, temp_project):
        """Test 'cci state capture' command"""
        # Setup mock
        mock_manager = Mock()
        mock_manager.capture_state.return_value = {
            "timestamp": "2025-01-01T10:00:00",
            "project_path": str(temp_project),
            "stats": {"total_files": 10, "total_lines": 500},
            "git": {"branch": "main", "commit": "abc123"}
        }
        mock_manager_class.return_value = mock_manager
        
        # Run command
        result = runner.invoke(cli, ['state', 'capture', '--project', str(temp_project)])
        
        assert result.exit_code == 0
        assert "State captured" in result.output
        assert "Files: 10" in result.output
        assert "Lines: 500" in result.output
        assert "main @ abc123" in result.output
    
    @patch('claude_code_indexer.cli.CodebaseStateManager')
    def test_state_begin_command(self, mock_manager_class, runner):
        """Test 'cci state begin' command"""
        # Setup mock
        mock_manager = Mock()
        mock_manager.track_task.return_value = "task_20250101_100000"
        mock_manager_class.return_value = mock_manager
        
        # Run command
        result = runner.invoke(cli, [
            'state', 'begin', 
            '--task', 'Test task description'
        ])
        
        assert result.exit_code == 0
        assert "Task started" in result.output
        assert "task_20250101_100000" in result.output
        assert "Test task description" in result.output
        assert "cci state complete --id task_20250101_100000" in result.output
    
    @patch('claude_code_indexer.cli.CodebaseStateManager')
    def test_state_complete_command(self, mock_manager_class, runner):
        """Test 'cci state complete' command"""
        # Setup mock
        mock_manager = Mock()
        mock_manager.complete_task.return_value = {
            "files_added": ["new_file.py"],
            "files_modified": ["main.py", "utils.py"],
            "files_removed": ["old_file.py"]
        }
        mock_manager_class.return_value = mock_manager
        
        # Run command
        result = runner.invoke(cli, [
            'state', 'complete',
            '--id', 'task_20250101_100000'
        ])
        
        assert result.exit_code == 0
        assert "Task Changes Summary" in result.output
        assert "Files Added" in result.output
        assert "Files Modified" in result.output
        assert "Files Removed" in result.output
        assert "Task task_20250101_100000 completed successfully" in result.output
    
    @patch('claude_code_indexer.cli.CodebaseStateManager')
    def test_state_complete_invalid_task(self, mock_manager_class, runner):
        """Test completing non-existent task"""
        # Setup mock
        mock_manager = Mock()
        mock_manager.complete_task.side_effect = ValueError("Task not found")
        mock_manager_class.return_value = mock_manager
        
        # Run command
        result = runner.invoke(cli, [
            'state', 'complete',
            '--id', 'invalid_task'
        ])
        
        assert result.exit_code == 0
        assert "Error: Task not found" in result.output
    
    @patch('claude_code_indexer.cli.CodebaseStateManager')
    def test_state_diff_command(self, mock_manager_class, runner):
        """Test 'cci state diff' command"""
        # Setup mock
        mock_manager = Mock()
        mock_manager.diff_from_last.return_value = {
            "files_added": ["new1.py", "new2.py"],
            "files_modified": ["mod1.py", "mod2.py", "mod3.py"],
            "files_removed": ["old1.py"]
        }
        mock_manager_class.return_value = mock_manager
        
        # Run command
        result = runner.invoke(cli, ['state', 'diff'])
        
        assert result.exit_code == 0
        assert "State Differences" in result.output
        assert "Added" in result.output
        assert "Modified" in result.output
        assert "Removed" in result.output
    
    @patch('claude_code_indexer.cli.CodebaseStateManager')
    def test_state_diff_no_previous(self, mock_manager_class, runner):
        """Test diff with no previous state"""
        # Setup mock
        mock_manager = Mock()
        mock_manager.diff_from_last.return_value = None
        mock_manager_class.return_value = mock_manager
        
        # Run command
        result = runner.invoke(cli, ['state', 'diff'])
        
        assert result.exit_code == 0
        assert "No previous state to compare with" in result.output
    
    @patch('claude_code_indexer.cli.CodebaseStateManager')
    def test_state_tasks_command(self, mock_manager_class, runner):
        """Test 'cci state tasks' command"""
        # Setup mock
        mock_manager = Mock()
        mock_manager.get_task_history.return_value = [
            {
                "id": "task_001",
                "description": "First task with a very long description that should be truncated",
                "status": "completed",
                "created_at": "2025-01-01T10:00:00"
            },
            {
                "id": "task_002",
                "description": "Second task",
                "status": "in_progress",
                "created_at": "2025-01-01T11:00:00"
            }
        ]
        mock_manager_class.return_value = mock_manager
        
        # Run command
        result = runner.invoke(cli, ['state', 'tasks'])
        
        assert result.exit_code == 0
        assert "Recent Tasks" in result.output
        assert "task_001" in result.output
        assert "task_002" in result.output
        assert "completed" in result.output
        assert "in_progress" in result.output
        assert "..." in result.output  # Truncated description
    
    @patch('claude_code_indexer.cli.CodebaseStateManager')
    def test_state_tasks_empty(self, mock_manager_class, runner):
        """Test tasks command with no tasks"""
        # Setup mock
        mock_manager = Mock()
        mock_manager.get_task_history.return_value = []
        mock_manager_class.return_value = mock_manager
        
        # Run command
        result = runner.invoke(cli, ['state', 'tasks'])
        
        assert result.exit_code == 0
        assert "No tasks found" in result.output
    
    @patch('claude_code_indexer.cli.CodebaseStateManager')
    def test_state_export_json(self, mock_manager_class, runner):
        """Test 'cci state export --format json' command"""
        # Setup mock
        mock_manager = Mock()
        mock_manager.export_state.return_value = json.dumps({
            "timestamp": "2025-01-01T10:00:00",
            "project_path": "/test/path",
            "stats": {"total_files": 10}
        }, indent=2)
        mock_manager_class.return_value = mock_manager
        
        # Run command in isolated filesystem
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['state', 'export', '--format', 'json'])
            
            assert result.exit_code == 0
            assert "State exported to codebase_state_" in result.output
            
            # Check file was created
            json_files = list(Path('.').glob('codebase_state_*.json'))
            assert len(json_files) == 1
    
    @patch('claude_code_indexer.cli.CodebaseStateManager')
    def test_state_export_summary(self, mock_manager_class, runner):
        """Test 'cci state export --format summary' command"""
        # Setup mock
        mock_manager = Mock()
        mock_manager.export_state.return_value = """
Codebase State Summary
======================
Project: /test/path
Total Files: 10
Total Lines: 500
"""
        mock_manager_class.return_value = mock_manager
        
        # Run command
        result = runner.invoke(cli, ['state', 'export', '--format', 'summary'])
        
        assert result.exit_code == 0
        assert "Codebase State Summary" in result.output
        assert "Total Files: 10" in result.output
    
    @patch('claude_code_indexer.cli.CodebaseStateManager')
    def test_state_validate_valid(self, mock_manager_class, runner):
        """Test 'cci state validate' with valid state"""
        # Setup mock
        mock_manager = Mock()
        mock_manager.validate_state.return_value = {
            "valid": True
        }
        mock_manager_class.return_value = mock_manager
        
        # Run command
        result = runner.invoke(cli, ['state', 'validate'])
        
        assert result.exit_code == 0
        assert "Codebase state is valid and consistent" in result.output
    
    @patch('claude_code_indexer.cli.CodebaseStateManager')
    def test_state_validate_invalid(self, mock_manager_class, runner):
        """Test 'cci state validate' with invalid state"""
        # Setup mock
        mock_manager = Mock()
        mock_manager.validate_state.return_value = {
            "valid": False,
            "reason": "Files have been modified",
            "unexpected_changes": ["file1.py", "file2.py", "file3.py"]
        }
        mock_manager_class.return_value = mock_manager
        
        # Run command
        result = runner.invoke(cli, ['state', 'validate'])
        
        assert result.exit_code == 0
        assert "State validation failed" in result.output
        assert "Files have been modified" in result.output
        assert "Unexpected changes detected" in result.output
        assert "file1.py" in result.output
    
    @patch('claude_code_indexer.cli.CodebaseStateManager')
    def test_state_commands_with_project_option(self, mock_manager_class, runner):
        """Test state commands with --project option"""
        mock_manager = Mock()
        mock_manager.capture_state.return_value = {
            "timestamp": "2025-01-01T10:00:00",
            "project_path": "/custom/path",
            "stats": {"total_files": 5, "total_lines": 100},
            "git": {"branch": "dev", "commit": "xyz789"}
        }
        mock_manager_class.return_value = mock_manager
        
        # Test with custom project path
        result = runner.invoke(cli, [
            'state', 'capture',
            '--project', '/custom/path'
        ])
        
        assert result.exit_code == 0
        mock_manager_class.assert_called_with('/custom/path')


class TestCLIEnhancedQuery:
    """Test enhanced query with state awareness"""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    @patch('os.path.exists')
    @patch('claude_code_indexer.cli.get_storage_manager')
    @patch('claude_code_indexer.cli.get_code_graph_indexer')
    @patch('claude_code_indexer.cli.CodebaseStateManager')
    def test_query_with_state(self, mock_state_manager_class, mock_indexer_class, mock_storage, mock_exists, runner):
        """Test 'cci query --with-state' command"""
        # Setup mocks
        mock_storage_instance = Mock()
        mock_storage_instance.get_project_from_cwd.return_value = Path('/test/project')
        mock_storage.return_value = mock_storage_instance
        
        # Create the mock indexer instance
        mock_indexer = Mock()
        mock_indexer.query_important_nodes.return_value = [
            {
                "name": "TestClass",
                "node_type": "class",
                "importance_score": 0.8,
                "relevance_tags": ["important"],
                "path": "/test/file.py"
            }
        ]
        # Mock the class to return our mock instance
        mock_indexer_class_obj = Mock(return_value=mock_indexer)
        mock_indexer_class.return_value = mock_indexer_class_obj
        
        mock_state_manager = Mock()
        mock_state_manager.get_current_state.return_value = {
            "timestamp": "2025-01-01T10:00:00",
            "stats": {"total_files": 100, "total_lines": 5000}
        }
        mock_state_manager.get_active_tasks.return_value = [
            {"id": "task_001", "description": "Active task 1"},
            {"id": "task_002", "description": "Active task 2"}
        ]
        mock_state_manager_class.return_value = mock_state_manager
        
        # Mock database exists
        mock_exists.return_value = True
        
        # Create mock database file
        with runner.isolated_filesystem():
            # Use current directory in isolated filesystem
            test_db = Path('test.db')
            test_db.touch()
            mock_indexer.db_path = str(test_db.absolute())
            
            # Run command
            result = runner.invoke(cli, ['query', '--important', '--with-state'])
            
            assert result.exit_code == 0
            assert "Codebase State:" in result.output
            assert "Total files: 100" in result.output
            assert "Total lines: 5,000" in result.output
            assert "Active Tasks (2):" in result.output
            assert "task_001" in result.output
    
    @patch('os.path.exists')
    @patch('claude_code_indexer.cli.get_storage_manager')
    @patch('claude_code_indexer.cli.get_code_graph_indexer')
    @patch('claude_code_indexer.cli.CodebaseStateManager')
    def test_query_with_task_id(self, mock_state_manager_class, mock_indexer_class, mock_storage, mock_exists, runner):
        """Test 'cci query --task-id' command"""
        # Setup mocks
        mock_storage_instance = Mock()
        mock_storage_instance.get_project_from_cwd.return_value = Path('/test/project')
        mock_storage.return_value = mock_storage_instance
        
        # Create the mock indexer instance
        mock_indexer = Mock()
        mock_indexer.query_important_nodes.return_value = []
        # Mock the class to return our mock instance
        mock_indexer_class_obj = Mock(return_value=mock_indexer)
        mock_indexer_class.return_value = mock_indexer_class_obj
        
        mock_state_manager = Mock()
        mock_state_manager.get_task.return_value = {
            "id": "task_001",
            "description": "Test task",
            "status": "in_progress",
            "created_at": "2025-01-01T10:00:00",
            "changes": {
                "files_modified": ["file1.py", "file2.py"],
                "files_added": ["new_file.py"]
            }
        }
        mock_state_manager_class.return_value = mock_state_manager
        
        # Mock database exists
        mock_exists.return_value = True
        
        # Create mock database file
        with runner.isolated_filesystem():
            # Use current directory in isolated filesystem
            test_db = Path('test.db')
            test_db.touch()
            mock_indexer.db_path = str(test_db.absolute())
            
            # Run command
            result = runner.invoke(cli, ['query', '--task-id', 'task_001'])
            
            assert result.exit_code == 0
            assert "Task Information" in result.output
            assert "Test task" in result.output
            assert "in_progress" in result.output
            assert "Files affected by this task:" in result.output
            assert "file1.py" in result.output
            assert "new_file.py" in result.output


class TestCLIIndexWithTaskTracking:
    """Test index command with task tracking"""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    @patch('claude_code_indexer.cli.get_code_graph_indexer')
    @patch('claude_code_indexer.cli.CodebaseStateManager')
    def test_index_with_track_task(self, mock_state_manager_class, mock_indexer_class, runner):
        """Test 'cci index --track-task' command"""
        # Setup mocks
        mock_state_manager = Mock()
        mock_state_manager.track_task.return_value = "task_20250101_100000"
        mock_state_manager_class.return_value = mock_state_manager
        
        mock_indexer = Mock()
        mock_indexer.index_directory.return_value = {
            "total_files": 10,
            "total_nodes": 50
        }
        mock_indexer_class.return_value = mock_indexer
        
        with runner.isolated_filesystem():
            # Create test directory
            Path('test_dir').mkdir()
            
            # Run command
            result = runner.invoke(cli, [
                'index', 'test_dir',
                '--track-task', 'Index with new feature'
            ])
            
            # Should track task
            mock_state_manager.track_task.assert_called_once()
            call_args = mock_state_manager.track_task.call_args[0][0]
            assert call_args["description"] == "Index with new feature"
            
            assert "Tracking task: task_20250101_100000" in result.output