#!/usr/bin/env python3
"""
Comprehensive test suite for Rust parser
"""
import pytest
import tempfile
import os
from pathlib import Path

from claude_code_indexer.parsers.rust_parser import RustParser
from claude_code_indexer.parsers.base_parser import ParseResult


class TestRustParser:
    """Test suite for Rust parser functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.parser = RustParser()
    
    def test_file_extension_support(self):
        """Test that parser recognizes Rust file extensions"""
        assert self.parser.can_parse("test.rs")
        assert self.parser.can_parse("main.rs")
        assert self.parser.can_parse("lib.rs")
        assert not self.parser.can_parse("test.py")
        assert not self.parser.can_parse("script.js")
        assert not self.parser.can_parse("code.cpp")
    
    def test_supported_extensions(self):
        """Test supported extensions list"""
        extensions = self.parser.get_supported_extensions()
        assert ".rs" in extensions
        assert len(extensions) == 1
    
    def test_simple_function_parsing(self):
        """Test parsing of simple Rust functions"""
        rust_code = '''
        use std::collections::HashMap;
        
        fn main() {
            println!("Hello, world!");
        }
        
        fn add(a: i32, b: i32) -> i32 {
            a + b
        }
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
            f.write(rust_code)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            assert result.success
            assert result.language == "rust"
            
            # Check for expected nodes
            functions = [n for n in result.nodes.values() if n.node_type == 'function']
            imports = [n for n in result.nodes.values() if n.node_type == 'import']
            files = [n for n in result.nodes.values() if n.node_type == 'file']
            
            assert len(functions) >= 2
            function_names = [f.name for f in functions]
            assert 'main' in function_names
            assert 'add' in function_names
            
            assert len(imports) >= 1
            import_names = [i.name for i in imports]
            assert any('std::collections::HashMap' in name for name in import_names)
            
            assert len(files) == 1
            
        finally:
            os.unlink(temp_file)
    
    def test_struct_and_impl_parsing(self):
        """Test parsing of structs and impl blocks"""
        rust_code = '''
        #[derive(Debug)]
        struct Person {
            name: String,
            age: u32,
        }
        
        impl Person {
            fn new(name: String, age: u32) -> Self {
                Person { name, age }
            }
            
            fn greet(&self) {
                println!("Hello, my name is {}", self.name);
            }
            
            fn get_age(&self) -> u32 {
                self.age
            }
        }
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
            f.write(rust_code)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            assert result.success
            assert result.language == "rust"
            
            # Check for structs (classes)
            classes = [n for n in result.nodes.values() if n.node_type == 'class']
            assert len(classes) >= 1
            class_names = [c.name for c in classes]
            assert 'Person' in class_names
            
            # Check for methods and functions (impl block functions are categorized differently)
            functions = [n for n in result.nodes.values() if n.node_type in ['function', 'method']]
            function_names = [f.name for f in functions]
            assert 'new' in function_names
            assert 'greet' in function_names
            assert 'get_age' in function_names
            
        finally:
            os.unlink(temp_file)
    
    def test_trait_parsing(self):
        """Test parsing of traits (interfaces)"""
        rust_code = '''
        trait Display {
            fn fmt(&self) -> String;
            fn print(&self) {
                println!("{}", self.fmt());
            }
        }
        
        trait Clone {
            fn clone(&self) -> Self;
        }
        
        struct Point {
            x: i32,
            y: i32,
        }
        
        impl Display for Point {
            fn fmt(&self) -> String {
                format!("({}, {})", self.x, self.y)
            }
        }
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
            f.write(rust_code)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            assert result.success
            assert result.language == "rust"
            
            # Check for traits (interfaces)
            interfaces = [n for n in result.nodes.values() if n.node_type == 'interface']
            interface_names = [i.name for i in interfaces]
            assert 'Display' in interface_names
            assert 'Clone' in interface_names
            
            # Check for structs
            classes = [n for n in result.nodes.values() if n.node_type == 'class']
            class_names = [c.name for c in classes]
            assert 'Point' in class_names
            
        finally:
            os.unlink(temp_file)
    
    def test_enum_parsing(self):
        """Test parsing of enums"""
        rust_code = '''
        enum Status {
            Active,
            Inactive,
            Pending,
        }
        
        enum Result<T, E> {
            Ok(T),
            Err(E),
        }
        
        enum Message {
            Quit,
            Move { x: i32, y: i32 },
            Write(String),
            ChangeColor(i32, i32, i32),
        }
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
            f.write(rust_code)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            assert result.success
            assert result.language == "rust"
            
            # Check for enums (classes)
            classes = [n for n in result.nodes.values() if n.node_type == 'class']
            class_names = [c.name for c in classes]
            assert 'Status' in class_names
            assert 'Result' in class_names
            assert 'Message' in class_names
            
        finally:
            os.unlink(temp_file)
    
    def test_module_parsing(self):
        """Test parsing of modules"""
        rust_code = '''
        mod network {
            pub fn connect() -> bool {
                true
            }
            
            mod tcp {
                pub fn send_data(data: &str) {
                    println!("Sending: {}", data);
                }
            }
        }
        
        mod utils;
        
        pub mod public_module {
            pub struct Config {
                pub host: String,
                pub port: u16,
            }
        }
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
            f.write(rust_code)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            assert result.success
            assert result.language == "rust"
            
            # Check for modules
            modules = [n for n in result.nodes.values() if n.node_type == 'module']
            module_names = [m.name for m in modules]
            assert 'network' in module_names
            assert 'utils' in module_names
            assert 'public_module' in module_names
            
            # Check for functions within modules
            functions = [n for n in result.nodes.values() if n.node_type == 'function']
            function_names = [f.name for f in functions]
            assert 'connect' in function_names
            assert 'send_data' in function_names
            
        finally:
            os.unlink(temp_file)
    
    def test_use_statements_parsing(self):
        """Test parsing of use statements (imports)"""
        rust_code = '''
        use std::collections::HashMap;
        use std::io::{self, Write};
        use std::fs::File;
        use serde::{Serialize, Deserialize};
        use crate::network::tcp;
        use super::parent_module;
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
            f.write(rust_code)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            assert result.success
            assert result.language == "rust"
            
            # Check for imports
            imports = [n for n in result.nodes.values() if n.node_type == 'import']
            import_names = [i.name for i in imports]
            
            # Should find various import patterns
            assert len(imports) >= 4
            assert any('std::collections::HashMap' in name for name in import_names)
            assert any('std::fs::File' in name for name in import_names)
            
        finally:
            os.unlink(temp_file)
    
    def test_async_function_parsing(self):
        """Test parsing of async functions"""
        rust_code = '''
        use tokio;
        
        async fn main() {
            let result = fetch_data().await;
            println!("Result: {:?}", result);
        }
        
        async fn fetch_data() -> Result<String, Box<dyn std::error::Error>> {
            let response = reqwest::get("https://api.example.com/data").await?;
            let text = response.text().await?;
            Ok(text)
        }
        
        pub async fn process_batch(items: Vec<String>) -> Vec<String> {
            let mut results = Vec::new();
            for item in items {
                let processed = process_item(item).await;
                results.push(processed);
            }
            results
        }
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
            f.write(rust_code)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            assert result.success
            assert result.language == "rust"
            
            # Check for async functions
            functions = [n for n in result.nodes.values() if n.node_type == 'function']
            function_names = [f.name for f in functions]
            
            assert 'main' in function_names
            assert 'fetch_data' in function_names
            assert 'process_batch' in function_names
            
        finally:
            os.unlink(temp_file)
    
    def test_complex_rust_application(self):
        """Test parsing of complex Rust application with multiple constructs"""
        rust_code = '''
        use std::collections::HashMap;
        use std::fmt::Display;
        use serde::{Serialize, Deserialize};
        
        #[derive(Debug, Serialize, Deserialize)]
        pub struct User {
            pub id: u64,
            pub name: String,
            pub email: String,
        }
        
        #[derive(Debug)]
        pub enum UserError {
            NotFound,
            InvalidEmail,
            DatabaseError(String),
        }
        
        pub trait UserRepository {
            async fn find_by_id(&self, id: u64) -> Result<User, UserError>;
            async fn save(&self, user: &User) -> Result<(), UserError>;
        }
        
        pub struct InMemoryUserRepository {
            users: HashMap<u64, User>,
        }
        
        impl InMemoryUserRepository {
            pub fn new() -> Self {
                Self {
                    users: HashMap::new(),
                }
            }
        }
        
        impl UserRepository for InMemoryUserRepository {
            async fn find_by_id(&self, id: u64) -> Result<User, UserError> {
                self.users.get(&id)
                    .cloned()
                    .ok_or(UserError::NotFound)
            }
            
            async fn save(&self, user: &User) -> Result<(), UserError> {
                if !is_valid_email(&user.email) {
                    return Err(UserError::InvalidEmail);
                }
                // Implementation would go here
                Ok(())
            }
        }
        
        fn is_valid_email(email: &str) -> bool {
            email.contains('@') && email.contains('.')
        }
        
        pub mod utils {
            pub fn hash_password(password: &str) -> String {
                format!("hashed_{}", password)
            }
            
            pub fn generate_id() -> u64 {
                rand::random()
            }
        }
        
        #[tokio::main]
        async fn main() -> Result<(), Box<dyn std::error::Error>> {
            let repo = InMemoryUserRepository::new();
            
            let user = User {
                id: utils::generate_id(),
                name: "John Doe".to_string(),
                email: "john@example.com".to_string(),
            };
            
            repo.save(&user).await?;
            let found_user = repo.find_by_id(user.id).await?;
            
            println!("Found user: {:?}", found_user);
            Ok(())
        }
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
            f.write(rust_code)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            assert result.success
            assert result.language == "rust"
            
            # Count node types
            node_counts = {}
            for node in result.nodes.values():
                node_counts[node.node_type] = node_counts.get(node.node_type, 0) + 1
            
            # Verify expected node types and minimum counts
            assert node_counts.get('function', 0) >= 6  # Multiple functions including async
            assert node_counts.get('class', 0) >= 3     # User, InMemoryUserRepository, UserError
            assert node_counts.get('interface', 0) >= 1 # UserRepository trait
            assert node_counts.get('import', 0) >= 3    # Multiple use statements
            assert node_counts.get('module', 0) >= 1    # utils module
            assert node_counts.get('file', 0) == 1      # Single file node
            
            # Check specific constructs
            classes = [n for n in result.nodes.values() if n.node_type == 'class']
            class_names = [c.name for c in classes]
            assert 'User' in class_names
            assert 'UserError' in class_names
            assert 'InMemoryUserRepository' in class_names
            
            interfaces = [n for n in result.nodes.values() if n.node_type == 'interface']
            interface_names = [i.name for i in interfaces]
            assert 'UserRepository' in interface_names
            
            functions = [n for n in result.nodes.values() if n.node_type == 'function']
            function_names = [f.name for f in functions]
            assert 'main' in function_names
            assert 'is_valid_email' in function_names
            
            modules = [n for n in result.nodes.values() if n.node_type == 'module']
            module_names = [m.name for m in modules]
            assert 'utils' in module_names
            
            # Check relationships
            assert len(result.relationships) > 0
            
        finally:
            os.unlink(temp_file)
    
    def test_empty_file(self):
        """Test parsing of empty Rust file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
            f.write("")
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            assert result.success
            assert result.language == "rust"
            # Should have at least a file node
            assert len(result.nodes) >= 1
            file_nodes = [n for n in result.nodes.values() if n.node_type == 'file']
            assert len(file_nodes) == 1
            
        finally:
            os.unlink(temp_file)
    
    def test_malformed_rust_file(self):
        """Test handling of malformed Rust syntax"""
        rust_code = '''
        fn unclosed_function( {
            let incomplete_statement
        
        struct UnclosedStruct {
            field: String
        
        use invalid::path::;
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
            f.write(rust_code)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            # Parser should still succeed but with limited nodes
            # Since we're using regex fallback, it should be robust
            assert result.success
            # Should still extract what it can parse
            assert len(result.nodes) > 0
            
        finally:
            os.unlink(temp_file)
    
    def test_generic_types_parsing(self):
        """Test parsing of generic types and functions"""
        rust_code = '''
        struct Container<T> {
            value: T,
        }
        
        impl<T> Container<T> {
            fn new(value: T) -> Self {
                Container { value }
            }
            
            fn get(&self) -> &T {
                &self.value
            }
        }
        
        fn process<T: Display>(item: T) -> String {
            format!("Processing: {}", item)
        }
        
        enum Option<T> {
            Some(T),
            None,
        }
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
            f.write(rust_code)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            assert result.success
            assert result.language == "rust"
            
            # Check for generic types
            classes = [n for n in result.nodes.values() if n.node_type == 'class']
            class_names = [c.name for c in classes]
            assert 'Container' in class_names
            assert 'Option' in class_names
            
            functions = [n for n in result.nodes.values() if n.node_type == 'function']
            function_names = [f.name for f in functions]
            assert 'new' in function_names
            assert 'get' in function_names
            assert 'process' in function_names
            
        finally:
            os.unlink(temp_file)
    
    def test_nonexistent_file(self):
        """Test handling of nonexistent file"""
        result = self.parser.parse_file("nonexistent_file.rs")
        assert not result.success
        assert result.error_message is not None
        assert "Could not read file" in result.error_message
    
    def test_binary_file_detection(self):
        """Test handling of binary files with .rs extension"""
        # Create a file with binary content
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.rs', delete=False) as f:
            f.write(b'\x00\x01\x02\x03\x04\x05')
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            assert not result.success
            assert result.error_message is not None
            assert "Binary file detected" in result.error_message
            
        finally:
            os.unlink(temp_file)
    
    def test_relationships_creation(self):
        """Test that parser creates proper relationships between nodes"""
        rust_code = '''
        mod network {
            pub struct Client {
                host: String,
            }
            
            impl Client {
                pub fn connect(&self) -> bool {
                    true
                }
            }
        }
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
            f.write(rust_code)
            temp_file = f.name
        
        try:
            result = self.parser.parse_file(temp_file)
            
            assert result.success
            assert len(result.relationships) > 0
            
            # Check relationship types
            relationship_types = [r.relationship_type for r in result.relationships]
            assert 'contains' in relationship_types
            
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])