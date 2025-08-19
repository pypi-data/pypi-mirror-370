#!/usr/bin/env python3
"""Test MCP server security fixes for SQL injection and FTS5 issues."""

import tempfile
import sqlite3
import json
import hashlib
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
from claude_code_indexer.mcp_server import search_code, project_manager
from claude_code_indexer.storage_manager import get_storage_manager


def create_test_db(db_path):
    """Create a test database with FTS5 support."""
    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create main table
    cursor.execute('''
        CREATE TABLE code_nodes (
            id INTEGER PRIMARY KEY,
            name TEXT,
            node_type TEXT,
            path TEXT,
            summary TEXT,
            importance_score REAL,
            relevance_tags TEXT
        )
    ''')
    
    # Create FTS5 virtual table
    cursor.execute('''
        CREATE VIRTUAL TABLE code_nodes_fts USING fts5(
            name,
            path,
            summary,
            content=code_nodes,
            content_rowid=id
        )
    ''')
    
    # Insert test data
    test_data = [
        (1, 'marketplace_module', 'module', '/src/marketplace.py', 'Marketplace functionality', 0.8, '[]'),
        (2, 'user_auth', 'function', '/src/auth.py', 'User authentication', 0.9, '[]'),
        (3, 'database_connection', 'class', '/src/db.py', 'Database connection handler', 0.7, '[]'),
        (4, 'search_products', 'function', '/src/marketplace.py', 'Search marketplace products', 0.6, '[]'),
    ]
    
    for row in test_data:
        cursor.execute('INSERT INTO code_nodes VALUES (?, ?, ?, ?, ?, ?, ?)', row)
        # Also insert into FTS5 table
        cursor.execute('INSERT INTO code_nodes_fts(rowid, name, path, summary) VALUES (?, ?, ?, ?)', 
                      (row[0], row[1], row[3], row[4]))
    
    conn.commit()
    conn.close()


def setup_test_project(tmp_path):
    """Setup test project with correct storage structure."""
    storage = get_storage_manager()
    # Use same logic as storage_manager.get_project_id
    project_id = hashlib.md5(str(tmp_path.resolve()).encode()).hexdigest()[:12]
    project_dir = storage.projects_dir / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    db_path = project_dir / "code_index.db"
    create_test_db(db_path)
    return project_dir, db_path


class TestMCPServerSecurity:
    """Test security fixes in MCP server."""
    
    def test_marketplace_search(self, tmp_path):
        """Test that searching for 'marketplace' doesn't cause SQL errors."""
        # Setup test project with correct storage structure
        project_dir, db_path = setup_test_project(tmp_path)
        
        # Test searching for 'marketplace' (the problematic term)
        result = search_code(str(tmp_path), "marketplace", limit=10, use_fts=True)
        
        # Should return results without SQL errors
        assert "marketplace_module" in result or "Search marketplace products" in result
        assert "no such column" not in result.lower()  # The original error
    
    def test_sql_injection_prevention(self, tmp_path):
        """Test that SQL injection attempts are blocked."""
        # Setup test project with correct storage structure
        project_dir, db_path = setup_test_project(tmp_path)
        
        # Test various SQL injection attempts
        injection_attempts = [
            "'; DROP TABLE code_nodes; --",
            "marketplace OR 1=1",
            "marketplace; DELETE FROM code_nodes",
            "marketplace/*comment*/",
            "marketplace--comment",
        ]
        
        for injection in injection_attempts:
            result = search_code(str(tmp_path), injection, limit=10)
            # Should be blocked
            assert "❌ Invalid search term detected" in result or "No results found" in result
    
    def test_fts5_special_characters(self, tmp_path):
        """Test that FTS5 special characters are properly escaped."""
        # Setup test project with correct storage structure
        project_dir, db_path = setup_test_project(tmp_path)
        
        # Test special FTS5 characters that should be escaped
        special_terms = [
            "AND",
            "OR",
            "NOT",
            "auth*",
            "database-connection",
            "search+products",
            "(marketplace)",
        ]
        
        for term in special_terms:
            result = search_code(str(tmp_path), term, limit=10, use_fts=True)
            # Should not cause errors
            assert "no such column" not in result.lower()
            assert "syntax error" not in result.lower()
    
    def test_long_search_terms(self, tmp_path):
        """Test that overly long search terms are rejected."""
        # Setup test project with correct storage structure
        project_dir, db_path = setup_test_project(tmp_path)
        
        # Test with a very long search term
        long_term = "a" * 101  # Over 100 character limit
        result = search_code(str(tmp_path), long_term, limit=10)
        
        # Should be rejected
        assert "❌ Search term too long" in result
    
    def test_mixed_mode_search(self, tmp_path):
        """Test both 'any' and 'all' search modes with safe terms."""
        # Setup test project with correct storage structure
        project_dir, db_path = setup_test_project(tmp_path)
        
        # Test 'any' mode
        result_any = search_code(str(tmp_path), "marketplace auth", mode="any", limit=10, use_fts=True)
        assert "marketplace_module" in result_any or "user_auth" in result_any
        
        # Test 'all' mode  
        result_all = search_code(str(tmp_path), "marketplace products", mode="all", limit=10, use_fts=True)
        # Should find items with both terms
        assert "search_products" in result_all.lower() or "No results found" in result_all


if __name__ == "__main__":
    pytest.main([__file__, "-v"])