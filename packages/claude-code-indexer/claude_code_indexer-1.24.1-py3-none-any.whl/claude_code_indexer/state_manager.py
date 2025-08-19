"""
Codebase State Manager - Single Source of Truth for Project State
"""
import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import sqlite3

import logging

logger = logging.getLogger(__name__)


class CodebaseStateManager:
    """Manages codebase state as single source of truth"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.storage_base = Path.home() / ".claude-code-indexer"
        self.project_hash = self._get_project_hash()
        self.project_storage = self.storage_base / "projects" / self.project_hash
        self._ensure_storage()
        
    def _get_project_hash(self) -> str:
        """Generate unique hash for project path"""
        return hashlib.sha256(str(self.project_path).encode()).hexdigest()[:16]
    
    def _ensure_storage(self):
        """Ensure storage directories exist"""
        self.project_storage.mkdir(parents=True, exist_ok=True)
        (self.project_storage / "history").mkdir(exist_ok=True)
        
    def _get_state_path(self) -> Path:
        """Get path to current state file"""
        return self.project_storage / "state.json"
    
    def _get_tasks_path(self) -> Path:
        """Get path to tasks file"""
        return self.project_storage / "tasks.json"
    
    def _get_git_commit(self) -> Optional[str]:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def _get_git_branch(self) -> Optional[str]:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def _hash_file(self, file_path: Path) -> str:
        """Generate hash for a single file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        except Exception:
            return ""
    
    def _hash_all_files(self) -> Dict[str, str]:
        """Hash all source files in project"""
        file_hashes = {}
        
        # Common source file patterns
        patterns = [
            "**/*.py", "**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx",
            "**/*.java", "**/*.cpp", "**/*.c", "**/*.h", "**/*.go",
            "**/*.rs", "**/*.rb", "**/*.php", "**/*.swift", "**/*.kt"
        ]
        
        for pattern in patterns:
            for file_path in self.project_path.glob(pattern):
                # Skip common ignore directories
                if any(part in file_path.parts for part in [
                    'node_modules', '.git', '__pycache__', 'dist', 'build',
                    '.venv', 'venv', '.env'
                ]):
                    continue
                    
                relative_path = file_path.relative_to(self.project_path)
                file_hashes[str(relative_path)] = self._hash_file(file_path)
                
        return file_hashes
    
    def _get_index_version(self) -> Optional[str]:
        """Get current index database version"""
        db_path = self.project_storage / "code_index.db"
        if db_path.exists():
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM metadata WHERE key='version'")
                result = cursor.fetchone()
                conn.close()
                return result[0] if result else None
            except Exception:
                pass
        return None
    
    def _get_codebase_stats(self) -> Dict:
        """Get basic codebase statistics"""
        stats = {
            "total_files": 0,
            "total_lines": 0,
            "languages": {}
        }
        
        file_hashes = self._hash_all_files()
        stats["total_files"] = len(file_hashes)
        
        # Count lines and detect languages
        for file_path in file_hashes.keys():
            full_path = self.project_path / file_path
            ext = Path(file_path).suffix
            
            if ext not in stats["languages"]:
                stats["languages"][ext] = {"files": 0, "lines": 0}
            
            stats["languages"][ext]["files"] += 1
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    stats["total_lines"] += lines
                    stats["languages"][ext]["lines"] += lines
            except Exception:
                pass
                
        return stats
    
    def capture_state(self) -> Dict:
        """Capture current codebase state"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "git": {
                "commit": self._get_git_commit(),
                "branch": self._get_git_branch()
            },
            "files": self._hash_all_files(),
            "index_version": self._get_index_version(),
            "stats": self._get_codebase_stats()
        }
        
        # Save to history
        history_file = self.project_storage / "history" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(history_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        # Update current state
        with open(self._get_state_path(), 'w') as f:
            json.dump(state, f, indent=2)
            
        logger.info(f"State captured for {self.project_path}")
        return state
    
    def get_current_state(self) -> Optional[Dict]:
        """Get current saved state"""
        state_path = self._get_state_path()
        if state_path.exists():
            with open(state_path, 'r') as f:
                return json.load(f)
        return None
    
    def get_state_history(self, limit: int = 10) -> List[Dict]:
        """Get state history"""
        history_dir = self.project_storage / "history"
        history_files = sorted(history_dir.glob("*.json"), reverse=True)[:limit]
        
        history = []
        for file_path in history_files:
            with open(file_path, 'r') as f:
                history.append(json.load(f))
                
        return history
    
    def _find_modified_files(self, state1: Dict, state2: Dict) -> Set[str]:
        """Find files that were modified between two states"""
        modified = set()
        
        files1 = state1.get("files", {})
        files2 = state2.get("files", {})
        
        # Check files that exist in both states
        for file_path in set(files1.keys()) & set(files2.keys()):
            if files1[file_path] != files2[file_path]:
                modified.add(file_path)
                
        return modified
    
    def compare_states(self, state1: Dict, state2: Dict) -> Dict:
        """Compare two codebase states"""
        files1 = set(state1.get("files", {}).keys())
        files2 = set(state2.get("files", {}).keys())
        
        return {
            "files_added": list(files2 - files1),
            "files_removed": list(files1 - files2),
            "files_modified": list(self._find_modified_files(state1, state2)),
            "stats_before": state1.get("stats", {}),
            "stats_after": state2.get("stats", {}),
            "time_delta": state2["timestamp"] if state2 else None
        }
    
    def diff_from_last(self) -> Optional[Dict]:
        """Get diff from last captured state"""
        current_state = self.capture_state()
        history = self.get_state_history(limit=2)
        
        if len(history) >= 2:
            return self.compare_states(history[1], current_state)
        return None
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        import uuid
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_suffix = str(uuid.uuid4())[:8]
        return f"task_{timestamp}_{unique_suffix}"
    
    def _load_tasks(self) -> List[Dict]:
        """Load existing tasks"""
        tasks_path = self._get_tasks_path()
        if tasks_path.exists():
            with open(tasks_path, 'r') as f:
                return json.load(f)
        return []
    
    def _save_tasks(self, tasks: List[Dict]):
        """Save tasks to file"""
        with open(self._get_tasks_path(), 'w') as f:
            json.dump(tasks, f, indent=2)
    
    def track_task(self, task: Dict) -> str:
        """Track a development task"""
        task_id = self._generate_task_id()
        
        task_entry = {
            "id": task_id,
            "description": task.get("description", ""),
            "created_at": datetime.now().isoformat(),
            "state_before": self.capture_state(),
            "status": "in_progress",
            "changes": []
        }
        
        tasks = self._load_tasks()
        tasks.append(task_entry)
        self._save_tasks(tasks)
        
        logger.info(f"Task {task_id} started: {task.get('description', '')}")
        return task_id
    
    def complete_task(self, task_id: str) -> Dict:
        """Mark task as complete and capture changes"""
        tasks = self._load_tasks()
        
        for task in tasks:
            if task["id"] == task_id:
                # Capture final state
                state_after = self.capture_state()
                
                # Calculate changes
                changes = self.compare_states(task["state_before"], state_after)
                
                # Update task
                task["state_after"] = state_after
                task["changes"] = changes
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
                
                self._save_tasks(tasks)
                logger.info(f"Task {task_id} completed")
                return changes
                
        raise ValueError(f"Task {task_id} not found")
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get specific task by ID"""
        tasks = self._load_tasks()
        for task in tasks:
            if task["id"] == task_id:
                return task
        return None
    
    def get_active_tasks(self) -> List[Dict]:
        """Get all active tasks"""
        tasks = self._load_tasks()
        return [t for t in tasks if t["status"] == "in_progress"]
    
    def get_task_history(self, limit: int = 10) -> List[Dict]:
        """Get task history"""
        tasks = self._load_tasks()
        # Sort by created_at descending
        tasks.sort(key=lambda x: x["created_at"], reverse=True)
        return tasks[:limit]
    
    def export_state(self, format: str = "json") -> str:
        """Export current state in specified format"""
        state = self.capture_state()
        
        if format == "json":
            return json.dumps(state, indent=2)
        elif format == "summary":
            summary = f"""
Codebase State Summary
======================
Project: {state['project_path']}
Timestamp: {state['timestamp']}
Git Commit: {state['git']['commit'][:8] if state['git']['commit'] else 'N/A'}
Git Branch: {state['git']['branch'] or 'N/A'}

Statistics:
-----------
Total Files: {state['stats']['total_files']}
Total Lines: {state['stats']['total_lines']:,}

Languages:
"""
            for ext, info in state['stats']['languages'].items():
                summary += f"  {ext}: {info['files']} files, {info['lines']:,} lines\n"
                
            return summary
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def validate_state(self) -> Dict:
        """Validate current codebase state against saved state"""
        saved_state = self.get_current_state()
        if not saved_state:
            return {"valid": False, "reason": "No saved state found"}
        
        current_files = self._hash_all_files()
        saved_files = saved_state.get("files", {})
        
        # Check for unexpected changes
        unexpected_changes = []
        for file_path, current_hash in current_files.items():
            if file_path in saved_files and saved_files[file_path] != current_hash:
                unexpected_changes.append(file_path)
        
        return {
            "valid": len(unexpected_changes) == 0,
            "unexpected_changes": unexpected_changes,
            "last_state_time": saved_state["timestamp"]
        }