#!/usr/bin/env python3
"""
LLM Feedback Tool - Simple feedback submission system for tools
"""

import json
import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests
from enum import Enum

class FeedbackType(Enum):
    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    QUESTION = "question"
    PRAISE = "praise"

class FeedbackPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FeedbackStatus(Enum):
    NEW = "new"
    REVIEWED = "reviewed"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    WONT_FIX = "wont_fix"

class LocalFeedbackStore:
    """Local SQLite storage for feedback (fallback when API is unavailable)"""
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path.home() / ".claude-code-indexer" / "feedback.db"
        
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the feedback database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                tool_name TEXT NOT NULL,
                tool_version TEXT,
                feedback_type TEXT NOT NULL,
                priority TEXT DEFAULT 'medium',
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                context TEXT,
                llm_model TEXT,
                user_id TEXT,
                session_id TEXT,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced BOOLEAN DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feedback_tool 
            ON feedback(tool_name)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feedback_status 
            ON feedback(status)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feedback_synced 
            ON feedback(synced)
        ''')
        
        conn.commit()
        conn.close()
    
    def save_feedback(self, feedback: Dict[str, Any]) -> str:
        """Save feedback to local database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        feedback_id = feedback.get('id', self._generate_id())
        
        cursor.execute('''
            INSERT OR REPLACE INTO feedback 
            (id, tool_name, tool_version, feedback_type, priority, title, 
             description, context, llm_model, user_id, session_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback_id,
            feedback['tool_name'],
            feedback.get('tool_version'),
            feedback['feedback_type'],
            feedback.get('priority', 'medium'),
            feedback['title'],
            feedback['description'],
            json.dumps(feedback.get('context', {})),
            feedback.get('llm_model'),
            feedback.get('user_id'),
            feedback.get('session_id'),
            feedback.get('status', 'new')
        ))
        
        conn.commit()
        conn.close()
        
        return feedback_id
    
    def get_unsynced_feedback(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get feedback that hasn't been synced to cloud"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM feedback 
            WHERE synced = 0 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        feedback_list = []
        for row in rows:
            feedback = dict(zip(columns, row))
            if feedback.get('context'):
                try:
                    feedback['context'] = json.loads(feedback['context'])
                except:
                    pass
            feedback_list.append(feedback)
        
        return feedback_list
    
    def mark_as_synced(self, feedback_ids: List[str]):
        """Mark feedback as synced to cloud"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.executemany(
            'UPDATE feedback SET synced = 1 WHERE id = ?',
            [(fid,) for fid in feedback_ids]
        )
        
        conn.commit()
        conn.close()
    
    def _generate_id(self) -> str:
        """Generate unique feedback ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]

class FeedbackClient:
    """Client for submitting feedback to cloud service"""
    
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_url = api_url or "https://feedback.claude-tools.workers.dev"
        self.api_key = api_key
        self.local_store = LocalFeedbackStore()
        self.session_id = self._generate_session_id()
    
    def submit_feedback(
        self,
        tool_name: str,
        title: str,
        description: str,
        feedback_type: str = "improvement",
        priority: str = "medium",
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Submit feedback about a tool
        
        Args:
            tool_name: Name of the tool (e.g., "claude-code-indexer")
            title: Short title of the feedback
            description: Detailed description
            feedback_type: Type of feedback (bug, feature, improvement, question, praise)
            priority: Priority level (low, medium, high, critical)
            context: Additional context (error logs, environment, etc.)
            **kwargs: Additional metadata
        
        Returns:
            Response with feedback ID and status
        """
        
        feedback = {
            'tool_name': tool_name,
            'title': title,
            'description': description,
            'feedback_type': feedback_type,
            'priority': priority,
            'context': context or {},
            'session_id': self.session_id,
            'created_at': datetime.now().isoformat(),
            **kwargs
        }
        
        # Add LLM information if available
        import os
        if 'ANTHROPIC_MODEL' in os.environ:
            feedback['llm_model'] = os.environ['ANTHROPIC_MODEL']
        
        # Save locally first
        feedback_id = self.local_store.save_feedback(feedback)
        feedback['id'] = feedback_id
        
        # Try to sync to cloud
        try:
            response = self._sync_to_cloud([feedback])
            if response and response.get('success'):
                self.local_store.mark_as_synced([feedback_id])
                return {
                    'success': True,
                    'feedback_id': feedback_id,
                    'message': 'Feedback submitted successfully',
                    'synced': True
                }
        except Exception as e:
            # If cloud sync fails, still return success (stored locally)
            pass
        
        return {
            'success': True,
            'feedback_id': feedback_id,
            'message': 'Feedback saved locally (will sync later)',
            'synced': False
        }
    
    def sync_pending_feedback(self) -> Dict[str, Any]:
        """Sync any pending local feedback to cloud"""
        unsynced = self.local_store.get_unsynced_feedback()
        
        if not unsynced:
            return {'success': True, 'message': 'No pending feedback to sync'}
        
        try:
            response = self._sync_to_cloud(unsynced)
            if response and response.get('success'):
                synced_ids = [f['id'] for f in unsynced]
                self.local_store.mark_as_synced(synced_ids)
                return {
                    'success': True,
                    'synced_count': len(synced_ids),
                    'message': f'Synced {len(synced_ids)} feedback items'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to sync feedback'
            }
        
        return {
            'success': False,
            'message': 'Failed to sync feedback'
        }
    
    def _sync_to_cloud(self, feedback_items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Sync feedback to cloud service"""
        if not self.api_url:
            return None
        
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        try:
            response = requests.post(
                f"{self.api_url}/api/feedback/batch",
                json={'feedback': feedback_items},
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return None
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return str(uuid.uuid4())[:8]

# Global feedback client instance
_feedback_client = None

def get_feedback_client() -> FeedbackClient:
    """Get or create global feedback client"""
    global _feedback_client
    if _feedback_client is None:
        _feedback_client = FeedbackClient()
    return _feedback_client

def submit_tool_feedback(
    title: str,
    description: str,
    feedback_type: str = "improvement",
    priority: str = "medium",
    tool_name: str = "claude-code-indexer",
    **kwargs
) -> Dict[str, Any]:
    """
    Quick function to submit feedback about a tool
    
    Example:
        submit_tool_feedback(
            title="Search function needs escaping",
            description="The search_code function fails when searching for 'marketplace'",
            feedback_type="bug",
            priority="high",
            context={'error': 'no such column: marketplace'}
        )
    """
    client = get_feedback_client()
    return client.submit_feedback(
        tool_name=tool_name,
        title=title,
        description=description,
        feedback_type=feedback_type,
        priority=priority,
        **kwargs
    )