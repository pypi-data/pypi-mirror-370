#!/usr/bin/env python3
"""
Automatic Error Tracker for LLM Tools
Automatically creates GitHub issues for errors with data sanitization
"""

import os
import re
import json
import hashlib
import traceback
import subprocess
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import sqlite3

class DataSanitizer:
    """Sanitize sensitive data before sending to GitHub"""
    
    # Patterns to detect and remove sensitive data
    # ORDER MATTERS: More specific patterns must come before more general ones
    SENSITIVE_PATTERNS = [
        # IP Addresses (MUST come before phone numbers)
        (r'\b(\d{1,3}\.\d{1,3})\.\d{1,3}\.\d{1,3}\b', lambda m: f'{m.group(1)}.XXX.XXX'),
        
        # API Keys and Tokens
        (r'[aA][pP][iI][-_]?[kK][eE][yY]\s*[:=]\s*["\']?([A-Za-z0-9-_]{6,})["\']?', 'API_KEY_REDACTED'),
        (r'sk-[a-zA-Z0-9-_]{20,}', 'API_KEY_REDACTED'),  # OpenAI style keys
        (r'[tT][oO][kK][eE][nN]\s*[:=]\s*["\']?([A-Za-z0-9-_]{6,})["\']?', 'TOKEN_REDACTED'),
        (r'[sS][eE][cC][rR][eE][tT]\s*[:=]\s*["\']?([A-Za-z0-9-_]{6,})["\']?', 'SECRET_REDACTED'),
        (r'[bB][eE][aA][rR][eE][rR]\s+([A-Za-z0-9-_]{20,})', 'BEARER_TOKEN_REDACTED'),
        
        # AWS Keys
        (r'AKIA[0-9A-Z]{16}', 'AWS_ACCESS_KEY_REDACTED'),
        (r'aws_secret_access_key\s*=\s*["\']?([A-Za-z0-9/+=]{40})["\']?', 'AWS_SECRET_REDACTED'),
        
        # URLs with credentials
        (r'https?://[^:]+:([^@]+)@', 'https://USER:PASS_REDACTED@'),
        
        # Email addresses (keep domain for context)
        (r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', lambda m: f'USER_REDACTED@{m.group(2)}'),
        
        # File paths with usernames
        (r'/[hH]ome/([^/]+)/', '/home/USER/'),
        (r'/[uU]sers/([^/]+)/', '/Users/USER/'),
        (r'C:\\[uU]sers\\([^\\]+)\\', r'C:\\Users\\USER\\'),
        
        # SSH Keys
        (r'-----BEGIN [A-Z]+ PRIVATE KEY-----[\s\S]+?-----END [A-Z]+ PRIVATE KEY-----', 'PRIVATE_KEY_REDACTED'),
        
        # Credit card numbers
        (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', 'CREDIT_CARD_REDACTED'),
        
        # Phone numbers (MUST come after IP addresses and credit cards)
        (r'\b\+[1-9]\d{6,14}\b', 'PHONE_REDACTED'),  # International format with +
        (r'\b[1-9]\d{9,14}\b', 'PHONE_REDACTED'),    # Long numbers without dots
        
        # Database connection strings
        (r'(mongodb|postgresql|mysql|redis)://[^:]+:([^@]+)@', lambda m: f'{m.group(1)}://USER:PASS_REDACTED@'),
    ]
    
    @classmethod
    def sanitize(cls, text: str) -> str:
        """Remove sensitive data from text"""
        if not text:
            return text
            
        sanitized = text
        for pattern, replacement in cls.SENSITIVE_PATTERNS:
            if callable(replacement):
                # Use lambda function for replacement
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
            else:
                # Use string replacement
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize a dictionary"""
        if not isinstance(data, dict):
            return data
            
        sanitized = {}
        for key, value in data.items():
            # Sanitize the key
            safe_key = cls.sanitize(str(key)) if isinstance(key, str) else key
            
            # Sanitize the value
            if isinstance(value, str):
                sanitized[safe_key] = cls.sanitize(value)
            elif isinstance(value, dict):
                sanitized[safe_key] = cls.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[safe_key] = [
                    cls.sanitize_dict(item) if isinstance(item, dict)
                    else cls.sanitize(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                sanitized[safe_key] = value
                
        return sanitized


class ErrorTracker:
    """Track and report errors to GitHub Issues"""
    
    def __init__(self, repo: Optional[str] = None, local_only: bool = False):
        """
        Initialize error tracker
        
        Args:
            repo: GitHub repository (owner/repo format)
            local_only: If True, only log locally without creating GitHub issues
        """
        self.repo = repo or os.environ.get('GITHUB_ERROR_REPO', 'claude-ai/claude-code-indexer')
        self.local_only = local_only
        self.db_path = Path.home() / '.claude-code-indexer' / 'error_tracking.db'
        self._init_db()
        
    def _init_db(self):
        """Initialize local error database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS errors (
                id TEXT PRIMARY KEY,
                error_hash TEXT NOT NULL,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                stack_trace TEXT,
                context TEXT,
                count INTEGER DEFAULT 1,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                github_issue_number INTEGER,
                github_issue_url TEXT,
                status TEXT DEFAULT 'new'
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_error_hash 
            ON errors(error_hash)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_status 
            ON errors(status)
        ''')
        
        conn.commit()
        conn.close()
    
    def track_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        tool_name: str = "claude-code-indexer",
        function_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track an error and optionally create GitHub issue
        
        Args:
            error: The exception that occurred
            context: Additional context about the error
            tool_name: Name of the tool where error occurred
            function_name: Function where error occurred
            
        Returns:
            Dict with tracking result
        """
        # Get error details
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()
        
        # Sanitize all data
        error_message = DataSanitizer.sanitize(error_message)
        stack_trace = DataSanitizer.sanitize(stack_trace)
        
        if context:
            context = DataSanitizer.sanitize_dict(context)
        
        # Create error hash for deduplication
        error_hash = self._create_error_hash(error_type, error_message, stack_trace)
        
        # Check if error already exists
        existing = self._get_existing_error(error_hash)
        
        if existing:
            # Update existing error
            self._update_error_count(error_hash)
            return {
                'success': True,
                'error_id': existing['id'],
                'status': 'updated',
                'count': existing['count'] + 1,
                'github_issue': existing.get('github_issue_url')
            }
        
        # Save new error locally
        error_id = self._save_error(
            error_hash=error_hash,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            context=context
        )
        
        # Create GitHub issue if not local only
        github_issue = None
        if not self.local_only:
            github_issue = self._create_github_issue(
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
                context=context,
                tool_name=tool_name,
                function_name=function_name
            )
            
            if github_issue:
                self._update_github_info(error_id, github_issue)
        
        return {
            'success': True,
            'error_id': error_id,
            'status': 'new',
            'github_issue': github_issue.get('html_url') if github_issue else None
        }
    
    def _create_error_hash(self, error_type: str, error_message: str, stack_trace: str) -> str:
        """Create unique hash for error deduplication"""
        # Extract key parts of stack trace (file names and line numbers)
        trace_lines = []
        for line in stack_trace.split('\n'):
            if 'File "' in line and 'test_error_tracker.py' not in line:
                # Skip test file lines, extract actual code file paths and line numbers
                match = re.search(r'File "([^"]+)", line (\d+)', line)
                if match:
                    # Use relative path if possible
                    file_path = match.group(1)
                    if '/claude_code_indexer/' in file_path:
                        file_path = file_path.split('/claude_code_indexer/')[-1]
                    # Only include actual source files, not test files
                    if not any(x in file_path for x in ['test_', '/test/', 'tests/']):
                        trace_lines.append(f"{file_path}:{match.group(2)}")
        
        # Create hash from error signature - focus on error type and message, not context
        # This allows same errors from different calls to be deduplicated
        signature = f"{error_type}:{error_message}:{':'.join(trace_lines[:2])}"
        return hashlib.md5(signature.encode()).hexdigest()[:16]
    
    def _get_existing_error(self, error_hash: str) -> Optional[Dict[str, Any]]:
        """Check if error already exists in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM errors WHERE error_hash = ?
        ''', (error_hash,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = ['id', 'error_hash', 'error_type', 'error_message', 
                      'stack_trace', 'context', 'count', 'first_seen', 
                      'last_seen', 'github_issue_number', 'github_issue_url', 'status']
            return dict(zip(columns, row))
        
        return None
    
    def _save_error(self, **kwargs) -> str:
        """Save error to local database"""
        error_id = hashlib.md5(f"{kwargs['error_hash']}:{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO errors (id, error_hash, error_type, error_message, stack_trace, context)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            error_id,
            kwargs['error_hash'],
            kwargs['error_type'],
            kwargs['error_message'],
            kwargs['stack_trace'],
            json.dumps(kwargs['context']) if kwargs.get('context') else None
        ))
        
        conn.commit()
        conn.close()
        
        return error_id
    
    def _update_error_count(self, error_hash: str):
        """Update error occurrence count"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE errors 
            SET count = count + 1, 
                last_seen = CURRENT_TIMESTAMP
            WHERE error_hash = ?
        ''', (error_hash,))
        
        conn.commit()
        conn.close()
    
    def _create_github_issue(
        self,
        error_type: str,
        error_message: str,
        stack_trace: str,
        context: Optional[Dict[str, Any]],
        tool_name: str,
        function_name: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Create GitHub issue for error"""
        try:
            # Prepare issue title
            title = f"[Auto-Error] {error_type}: {error_message[:60]}"
            if len(error_message) > 60:
                title += "..."
            
            # Prepare issue body
            body = f"""## 🚨 Automatic Error Report

This issue was automatically created by the error tracking system.

### Error Details
- **Type**: `{error_type}`
- **Tool**: `{tool_name}`
- **Function**: `{function_name or 'Unknown'}`
- **Time**: {datetime.now().isoformat()}

### Error Message
```
{error_message}
```

### Stack Trace
<details>
<summary>Click to expand</summary>

```python
{stack_trace}
```
</details>

### Context
<details>
<summary>Additional context</summary>

```json
{json.dumps(context, indent=2) if context else 'No additional context'}
```
</details>

### Environment
- Python Version: {self._get_python_version()}
- OS: {self._get_os_info()}
- Tool Version: {self._get_tool_version()}

---
*This issue was automatically generated. All sensitive data has been sanitized.*
"""
            
            # Add labels
            labels = ['bug', 'auto-reported']
            if 'critical' in error_message.lower() or 'fatal' in error_message.lower():
                labels.append('priority:high')
            
            # Create issue using GitHub CLI
            cmd = [
                'gh', 'issue', 'create',
                '--repo', self.repo,
                '--title', title,
                '--body', body,
                '--label', ','.join(labels)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse issue URL from output
                issue_url = result.stdout.strip()
                issue_number = issue_url.split('/')[-1]
                
                return {
                    'number': int(issue_number),
                    'html_url': issue_url
                }
            else:
                print(f"Failed to create GitHub issue: {result.stderr}")
                
        except Exception as e:
            print(f"Error creating GitHub issue: {e}")
        
        return None
    
    def _update_github_info(self, error_id: str, github_issue: Dict[str, Any]):
        """Update database with GitHub issue info"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE errors 
            SET github_issue_number = ?,
                github_issue_url = ?,
                status = 'reported'
            WHERE id = ?
        ''', (
            github_issue['number'],
            github_issue['html_url'],
            error_id
        ))
        
        conn.commit()
        conn.close()
    
    def _get_python_version(self) -> str:
        """Get Python version"""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def _get_os_info(self) -> str:
        """Get OS information"""
        import platform
        return f"{platform.system()} {platform.release()}"
    
    def _get_tool_version(self) -> str:
        """Get tool version"""
        try:
            from claude_code_indexer import __version__
            return __version__
        except:
            return "Unknown"
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total errors
        cursor.execute('SELECT COUNT(*) FROM errors')
        total = cursor.fetchone()[0]
        
        # Unique errors
        cursor.execute('SELECT COUNT(DISTINCT error_hash) FROM errors')
        unique = cursor.fetchone()[0]
        
        # Reported to GitHub
        cursor.execute('SELECT COUNT(*) FROM errors WHERE github_issue_number IS NOT NULL')
        reported = cursor.fetchone()[0]
        
        # Most common errors
        cursor.execute('''
            SELECT error_type, error_message, SUM(count) as total
            FROM errors
            GROUP BY error_hash
            ORDER BY total DESC
            LIMIT 5
        ''')
        
        common = []
        for row in cursor.fetchall():
            common.append({
                'type': row[0],
                'message': row[1][:100],
                'count': row[2]
            })
        
        conn.close()
        
        return {
            'total_errors': total,
            'unique_errors': unique,
            'reported_to_github': reported,
            'most_common': common
        }


# Global error tracker instance
_error_tracker = None

def get_error_tracker() -> ErrorTracker:
    """Get or create global error tracker"""
    global _error_tracker
    if _error_tracker is None:
        _error_tracker = ErrorTracker()
    return _error_tracker

def track_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    tool_name: str = "claude-code-indexer",
    function_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick function to track an error
    
    Example:
        try:
            # Some code that might fail
            result = risky_operation()
        except Exception as e:
            track_error(e, context={'input': data}, function_name='risky_operation')
            raise
    """
    tracker = get_error_tracker()
    return tracker.track_error(error, context, tool_name, function_name)


# Decorator for automatic error tracking
def auto_track_errors(tool_name: str = "claude-code-indexer"):
    """
    Decorator to automatically track errors in functions
    
    Example:
        @auto_track_errors()
        def my_function(arg1, arg2):
            # Function code
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Track the error
                context = {
                    'args': str(args)[:500],  # Limit size
                    'kwargs': str(kwargs)[:500]
                }
                track_error(
                    e,
                    context=context,
                    tool_name=tool_name,
                    function_name=func.__name__
                )
                # Re-raise the error
                raise
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    return decorator