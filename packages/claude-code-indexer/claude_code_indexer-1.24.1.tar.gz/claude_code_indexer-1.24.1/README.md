# Claude Code Indexer (cci)

A powerful code indexing tool that uses graph databases to analyze and understand code structure. Built specifically for Claude Code assistant workflows.

**🚀 Quick tip:** Use `cci` instead of `claude-code-indexer` for all commands!

## Features

- 📊 **Graph-based code analysis** using Ensmallen library
- 🔍 **Intelligent node ranking** based on importance and centrality
- 💾 **SQLite database** for persistent storage
- 🎯 **Relevance tagging** for different code entity types
- 📈 **Network analysis** with PageRank and centrality measures
- 🚀 **Easy CLI interface** for quick setup and usage
- 🤖 **MCP Integration** for direct Claude Desktop/Code support (v1.3.0+, Claude Code v1.14.0+)
- 🔬 **Multi-keyword search** with AND/OR logic (v1.3.0+)
- 📂 **Project-based indexing** for MCP with separate databases (v1.4.0+)
- 🚫 **Smart ignore patterns** - auto-ignores node_modules, .git, etc (v1.5.0+)
- 📝 **Respects .gitignore** and .dockerignore files (v1.5.0+)
- 🌐 **Multi-language support** - Python, JavaScript, TypeScript (v1.6.0+), Java (v1.10.0+), AutoIt (v1.11.0+)
- 🏠 **Centralized storage** - All data in ~/.claude-code-indexer/ (v1.7.0+)
- ⚡ **High-performance memory cache** - 10-100x faster with 100MB LRU cache (v1.12.0+)
- 🏗️ **Infrastructure detection** - Auto-detects databases, APIs, cloud services, DevOps tools (v1.13.0+)
- 🎯 **Professional CLI** - App name and version header on all commands (v1.13.0+)
- 🔄 **Automatic database migrations** - Seamless schema updates with backup/rollback (v1.14.0+)
- 🧠 **LLM Memory Storage** - LLMs can store and retrieve their own analysis, insights, and context (v1.21.2+)

## Installation

### From PyPI (Recommended)

```bash
# Basic installation
pip install claude-code-indexer

# With MCP support for Claude Desktop/Code
pip install 'claude-code-indexer[mcp]'

# After installation, use 'cci' for all commands!
```

### From Source

```bash
git clone https://github.com/anthropics/claude-code-indexer.git
cd claude-code-indexer
pip install -e .
```

### Updating

The package includes auto-update functionality:

```bash
# Check for updates
cci update --check-only

# Update to latest version
cci update

# Sync CLAUDE.md with latest template
cci sync
```

Updates will also be checked automatically when you run any command.

## What's New in v1.13.0

### 🎯 Enhanced User Experience
- **App Name & Version Display** - All CLI commands now show a professional header
- **Infrastructure Detection** - Automatically detects and tags databases, APIs, cloud services, and DevOps tools
- **GitHub Actions CI/CD** - Complete test automation with multi-platform support

### 🏗️ Infrastructure Tagging
The indexer now detects and tags infrastructure components:
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis, SQLite
- **APIs**: REST endpoints, GraphQL, gRPC, WebSocket
- **Message Queues**: Kafka, RabbitMQ, SQS, Celery
- **Cloud Services**: AWS, Azure, GCP, Docker, Kubernetes
- **DevOps Tools**: CI/CD, monitoring, deployment configurations
- **Environment Profiles**: production, staging, development

## What's New in v1.5.0

### 🚫 Smart Ignore Patterns

The indexer now automatically ignores common non-source directories:
- **Dependencies**: node_modules/, vendor/, packages/, bower_components/
- **Build outputs**: build/, dist/, target/, *.egg-info/
- **Version control**: .git/, .svn/, .hg/
- **Python**: __pycache__/, *.pyc, venv/, .env/
- **IDE**: .idea/, .vscode/, *.swp
- **And many more...**

### 📝 .gitignore Support

Automatically respects patterns from:
- `.gitignore` - Git ignore patterns
- `.dockerignore` - Docker ignore patterns
- Custom patterns via CLI or MCP

## Quick Start

### 1. Initialize in your project

```bash
cd your-project
cci init  # Short and sweet!
```

This will:
- Create or update your `CLAUDE.md` file with indexing instructions
- Initialize project in centralized storage (`~/.claude-code-indexer/`)
- No local database files created in your project

### 2. Index your codebase

```bash
# Index current directory
cci index .

# Index specific directory
cci index /path/to/your/code

# Index with custom patterns
cci index . --patterns "*.py,*.js,*.ts"

# Index with custom ignore patterns
cci index . --custom-ignore "tests/" --custom-ignore "*.test.py"

# See what will be ignored before indexing
cci index . --show-ignored
```

### 3. Query your code

```bash
# Show most important code entities
cci query --important

# Show all entities of specific type
cci query --type class

# Search for specific terms (single keyword)
cci search UserModel

# Search with multiple keywords (OR logic)
cci search auth user login

# Search with multiple keywords (AND logic - must match all)
cci search database connection --mode all

# View indexing statistics
cci stats
```

### 4. Manage projects

```bash
# List all indexed projects
cci projects

# Remove a project's index
cci remove project-name

# Clean up orphaned projects
cci clean

# Query a specific project
cci query --important --project /path/to/project
```

## CLI Commands

### `init`
Initialize Claude Code Indexer in current directory.

```bash
cci init [--force]
```

Options:
- `--force`: Overwrite existing configuration

### `index`
Index source code in specified directory.

```bash
cci index PATH [options]
```

Options:
- `--patterns`: File patterns to index (default: "*.py")
- `--db`: Database file path (default: centralized storage)
- `--force`: Force re-index all files (ignore cache)
- `--workers`: Number of parallel workers (default: auto)
- `--no-cache`: Disable caching
- `--custom-ignore`: Additional ignore patterns (can be used multiple times)
- `--show-ignored`: Show what patterns are being ignored

### `query`
Query indexed code entities.

```bash
cci query [options]
```

Options:
- `--important`: Show only important nodes
- `--type`: Filter by node type (file, class, method, function)
- `--limit`: Maximum number of results (default: 20)
- `--db`: Database file path (default: centralized storage)
- `--project`: Project name/path to query (default: current directory)

### `search`
Search for code entities by name. Supports multiple keywords.

```bash
cci search TERMS... [options]
```

Options:
- `--mode`: Search mode - 'any' (OR logic) or 'all' (AND logic) (default: 'any')
- `--limit`: Maximum number of results (default: 20)
- `--db`: Database file path

Examples:
```bash
# Single keyword
cci search auth

# Multiple keywords (match any)
cci search auth user login

# Multiple keywords (must match all)
cci search database connection --mode all
```

### `stats`
Show indexing statistics.

```bash
cci stats [options]
```

Options:
- `--db`: Database file path (default: centralized storage)
- `--cache`: Show cache statistics
- `--project`: Project name/path for stats (default: current directory)

### `projects`
List all indexed projects.

```bash
cci projects [--all]
```

Options:
- `--all`: Show all projects including non-existent

### `remove`
Remove an indexed project.

```bash
cci remove PROJECT [--force]
```

Options:
- `--force`: Force removal without confirmation

### `clean`
Clean up orphaned project indexes.

```bash
cci clean
```

### `migrate`
Manage database schema migrations.

```bash
# Check and apply migrations
cci migrate

# Show what would be migrated without applying changes
cci migrate --dry-run

# Migrate to a specific version
cci migrate --target-version 1.6.0

# Force migration even if database appears corrupted
cci migrate --force
```

The migration system:
- Automatically detects current database version
- Creates backups before migration
- Rolls back on failure
- Preserves all existing data
- Supports incremental upgrades through multiple versions

### `background`
Manage background indexing service for automatic updates.

```bash
# Start the background service
cci background start

# Stop the background service
cci background stop

# Check service status
cci background status

# Set indexing interval for current project (in seconds)
cci background set-interval --interval 600  # 10 minutes

# Set default interval for all projects
cci background set-interval --interval 300  # 5 minutes (default)

# Disable background indexing for a project
cci background set-interval --project /path/to/project --interval -1

# Enable/disable the service globally
cci background config --enable
cci background config --disable
```

Background indexing automatically keeps your code indexes up-to-date:
- Default interval: 300 seconds (5 minutes)
- Configure per-project or global intervals
- Runs as a daemon process
- Only re-indexes when files have changed
- Set interval to -1 to disable for specific projects

## Database Schema

The tool creates a SQLite database with the following structure:

### code_nodes
Stores information about code entities.

```sql
CREATE TABLE code_nodes (
    id INTEGER PRIMARY KEY,
    node_type TEXT,           -- 'file', 'class', 'method', 'function', 'import'
    name TEXT,                -- Entity name
    path TEXT,                -- File path
    summary TEXT,             -- Description
    importance_score REAL,    -- 0.0 to 1.0
    relevance_tags TEXT,      -- JSON array of tags
    created_at TIMESTAMP
);
```

### relationships
Stores relationships between code entities.

```sql
CREATE TABLE relationships (
    source_id INTEGER,
    target_id INTEGER,
    relationship_type TEXT,   -- 'imports', 'contains', 'calls', 'inherits'
    weight REAL,
    created_at TIMESTAMP
);
```

## Integration with Claude Code

After running `cci init`, your `CLAUDE.md` file will include:

- Complete setup instructions
- Database schema documentation
- CLI command reference
- Usage examples for Claude Code workflows

## MCP Integration for Claude Desktop/Code (v1.3.0+)

Direct integration with Claude Desktop and Claude Code using Model Context Protocol:

**Claude Desktop**: Supported since v1.3.0
**Claude Code**: Supported since v1.14.0

### Quick Setup

```bash
# Install with MCP support
pip install 'claude-code-indexer[mcp]'

# Auto-configure Claude Desktop/Code (auto-detects which is installed)
cci mcp install

# Check status
cci mcp status
```

### MCP Tools Available

Once installed, Claude Desktop or Claude Code can directly use:

#### Core Tools
- **index_codebase(project_path, workers=4, force=False, custom_ignore=[])**: Index Python projects
- **get_project_stats(project_path)**: View code statistics and overview
- **query_important_code(project_path, limit=20, node_type=None)**: Find important components
- **search_code(project_path, terms, limit=10, mode="any")**: Multi-keyword search
- **manage_cache(project_path, action, days=30)**: Control indexing cache

#### New in v1.5.0
- **get_ignore_patterns(project_path)**: View active ignore patterns
- **list_indexed_projects()**: List all indexed projects

### Configuration Paths

The MCP installer automatically detects and configures the appropriate Claude app:

**Claude Desktop**:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Claude Code**:
- macOS: `~/Library/Application Support/Claude Code/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude Code\claude_desktop_config.json`
- Linux: `~/.config/Claude Code/claude_desktop_config.json`

### MCP Usage Examples

```python
# Index a project (ignores node_modules, .git, etc automatically)
index_codebase("/path/to/project")

# Index with custom ignore patterns
index_codebase("/path/to/project", custom_ignore=["tests/", "*.test.py"])

# Search with multiple keywords
search_code("/path/to/project", "auth user login", mode="all")

# Check what's being ignored
get_ignore_patterns("/path/to/project")
```

### LLM Memory Storage (v1.21.2+)

The revolutionary LLM Memory Storage system allows Claude and other LLMs to store and retrieve their own analysis, insights, and context as persistent memory attached to code nodes.

#### Memory Tools
- **store_llm_memory()**: Store analysis, insights, TODOs, warnings as persistent memory
- **get_llm_memories()**: Retrieve stored memories with flexible filtering
- **search_llm_memories()**: Search through memory content
- **get_node_memory_summary()**: Comprehensive memory overview per code node

#### Memory Types
- `analysis`: Architectural analysis, design pattern detection
- `insight`: Security insights, performance observations  
- `todo`: Action items, improvement suggestions
- `warning`: Code quality issues, potential problems
- `context`: Background information, business logic explanations

#### Example Usage
```python
# Store architectural insight
store_llm_memory(
    project_path=".",
    node_id=42,
    memory_type="analysis",
    content="This UserService follows repository pattern with dependency injection.",
    tags=["architecture", "repository-pattern", "di"]
)

# Retrieve all memories for a node
get_llm_memories(project_path=".", node_id=42)

# Search for security-related memories
search_llm_memories(project_path=".", search_term="security")
```

#### Benefits for LLMs
- **Persistent Understanding**: Build knowledge across sessions
- **Cumulative Learning**: Each interaction adds to understanding
- **Context Retention**: Remember previous analysis and decisions
- **Consistent Quality**: Apply learned patterns to new code

See [LLM_MEMORY_GUIDE.md](LLM_MEMORY_GUIDE.md) for complete documentation.

### MCP Integration Benefits

- **Zero friction**: No need to type CLI commands in Claude Desktop
- **Auto-indexing**: Projects indexed when opened
- **Rich UI**: Visual code exploration
- **Session persistence**: Maintains context between chats
- **Memory Storage**: LLMs build persistent understanding over time

## Graph Analysis Features

### Node Importance Scoring
- **Degree centrality**: Based on number of connections
- **PageRank**: Overall importance in the dependency graph
- **Weighted scoring**: Combines multiple centrality measures

### Relevance Tags
- `structural`: Classes and main components
- `highly-used`: Entities with many incoming dependencies
- `complex`: Entities with many outgoing dependencies
- `test`: Test-related code
- `module`: File-level entities

### Advanced Analysis
- **Hub detection**: Find central components in your architecture
- **Dependency tracking**: Understand code relationships
- **Impact analysis**: Trace how changes propagate
- **Similarity detection**: Find related code patterns

## Performance & Caching

### Memory Cache (v1.12.0+)

Claude Code Indexer includes a high-performance memory cache that dramatically improves performance for frequently accessed data:

- **100MB LRU Memory Cache**: Keeps hot data in memory for instant access
- **10-100x Faster**: Memory cache hits complete in <1ms vs 10-50ms for disk
- **Automatic Management**: LRU eviction and TTL-based expiration
- **Entity-Specific Policies**: Different cache strategies per entity type

### Cache Statistics

View detailed cache performance metrics:

```bash
# Show cache statistics with project stats
cci stats --cache

# Standalone cache management
cci cache

# Clear old cache entries
cci cache --clear --days 7
```

### Performance Benchmarks

#### Real-World Performance
- **Indexing Speed**: 22.4 files/sec (fresh index)
- **Cache Speedup**: 64.6x faster on subsequent runs
- **LLM Enhancement**: 1,116 nodes/sec

## Development

### Running Tests

Tests can be run in parallel for faster execution:

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests in parallel (auto-detect CPU cores)
pytest -n auto

# Run tests in parallel with specific worker count
pytest -n 4

# Run tests sequentially (default)
pytest

# Run tests with coverage in parallel
pytest -n auto --cov=claude_code_indexer --cov-report=term
```

Parallel test execution is powered by `pytest-xdist` and can significantly speed up test runs on multi-core systems.

**Note**: Some tests may fail when run in parallel due to shared resources (e.g., database files, cache directories). If you encounter failures with parallel execution, try running tests sequentially or with fewer workers.
- **Memory Usage**: <100MB for thousands of files

#### Scalability
| Project Size | Files | Time | Speed | Cache Speedup |
|-------------|-------|------|-------|---------------|
| Small | 50 | 2.3s | 22 files/s | 10-20x |
| Medium | 500 | 9.0s | 55 files/s | 30-50x |
| Large | 2000 | 21.6s | 93 files/s | 50-100x |

See [PERFORMANCE_BENCHMARKS.md](PERFORMANCE_BENCHMARKS.md) for detailed analysis.

### Performance Tips

1. **First Run**: Initial indexing populates both disk and memory cache
2. **Subsequent Runs**: Unchanged files load from memory cache (instant)
3. **Memory Usage**: Default 100MB limit with automatic eviction
4. **TTL Policies**: Files (7 days), Functions (3 days), Imports (1 day)

## Examples

### Basic Usage

```python
from claude_code_indexer import CodeGraphIndexer

# Create indexer
indexer = CodeGraphIndexer("my_project.db")

# Index a directory
indexer.index_directory("./src")

# Query important nodes
important_nodes = indexer.query_important_nodes(min_score=0.5)
for node in important_nodes:
    print(f"{node['name']} ({node['node_type']}): {node['importance_score']}")
```

### Advanced Analysis

```python
# Get graph statistics
stats = indexer.get_stats()
print(f"Total nodes: {stats['total_nodes']}")
print(f"Node types: {stats['node_types']}")

# Build NetworkX graph for custom analysis
nx_graph = indexer.build_graph()
import networkx as nx
centrality = nx.betweenness_centrality(nx_graph)
```

## Requirements

- Python 3.8+
- ensmallen >= 0.8.0
- networkx >= 3.0
- pandas >= 1.5.0
- click >= 8.0.0
- rich >= 13.0.0

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- 📖 [Documentation](https://docs.anthropic.com/claude-code)
- 🐛 [Issues](https://github.com/claude-ai/code-indexer/issues)
- 💬 [Discussions](https://github.com/claude-ai/code-indexer/discussions)