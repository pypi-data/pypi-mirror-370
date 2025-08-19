"""GOD Mode: Autonomous Multi-Agent Execution System (BETA)."""
import asyncio
import json
import time
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

try:
    from .tmux_orchestrator import TmuxOrchestrator, start_god_mode_tmux, attach_god_mode_tmux
    TMUX_AVAILABLE = True
except ImportError:
    TMUX_AVAILABLE = False
    TmuxOrchestrator = None

console = Console()


class GodModeOrchestrator:
    """Orchestrates autonomous multi-agent execution."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".god-mode"
        self.audit_log_path = self.config_path / "audit.log"
        self.config_file = self.config_path / "config.yaml"
        self.enabled = False
        self.token_usage = {"total": 0, "by_agent": {}}
        self.use_claude_mcp = os.environ.get('GOD_MODE_USE_MCP', 'true').lower() == 'true'
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Ensure GOD mode directories exist."""
        self.config_path.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self._create_default_config()
            
    def _create_default_config(self):
        """Create default GOD mode configuration."""
        default_config = {
            "enabled": False,
            "auto_accept": True,
            "vibecode_mode": True,
            "agents": {
                "architect": {
                    "role": "Planning and task decomposition",
                    "model": "claude-opus-4"
                },
                "developer": {
                    "role": "Code implementation",
                    "model": "claude-sonnet-4"
                }
            },
            "safety": {
                "forbidden_operations": [
                    "rm -rf /",
                    "DROP DATABASE",
                    "DELETE FROM users"
                ],
                "max_tokens_per_session": 100000,
                "require_confirmation": [
                    "production deployment",
                    "database migration"
                ]
            }
        }
        
        with open(self.config_file, 'w') as f:
            import yaml
            yaml.dump(default_config, f, default_flow_style=False)
    
    def _log_action(self, agent: str, action: str, result: str, tokens: int = 0):
        """Log all GOD mode actions for audit trail."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "action": action,
            "result": result,
            "tokens": tokens
        }
        
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
            
        self.token_usage["total"] += tokens
        self.token_usage["by_agent"][agent] = self.token_usage["by_agent"].get(agent, 0) + tokens
    
    async def enable(self):
        """Enable GOD mode with all safety checks."""
        console.print(Panel.fit(
            "[bold yellow]⚡ GOD MODE ACTIVATION ⚡[/bold yellow]\n\n"
            "[red]WARNING: This mode enables autonomous execution![/red]\n"
            "- Auto-accept ALL operations\n"
            "- Vibecode mode always ON\n"
            "- Multi-agent coordination active\n\n"
            "[cyan]Safety features:[/cyan]\n"
            "- Audit logging to ~/.god-mode/audit.log\n"
            "- Emergency stop: god-mode --stop\n"
            "- Token usage tracking\n",
            title="GOD Mode (BETA)",
            border_style="yellow"
        ))
        
        if click.confirm("Enable GOD mode?", default=False):
            self.enabled = True
            self._log_action("system", "GOD_MODE_ENABLED", "User confirmed activation")
            
            # Update config
            import yaml
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            config["enabled"] = True
            with open(self.config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
                
            console.print("[bold green]✓ GOD mode activated![/bold green]")
            console.print("[yellow]Use 'god-mode --stop' for emergency shutdown[/yellow]")
            
            # Show initial status
            await self.status()
        else:
            console.print("[red]GOD mode activation cancelled[/red]")
    
    async def disable(self):
        """Disable GOD mode."""
        self.enabled = False
        self._log_action("system", "GOD_MODE_DISABLED", "User initiated shutdown")
        
        # Update config
        import yaml
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)
        config["enabled"] = False
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
            
        console.print("[bold red]✓ GOD mode deactivated[/bold red]")
    
    async def status(self):
        """Show GOD mode status and statistics."""
        import yaml
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Status table
        status_table = Table(title="GOD Mode Status", show_header=True)
        status_table.add_column("Setting", style="cyan")
        status_table.add_column("Value", style="green")
        
        status_table.add_row("Enabled", "✓ Yes" if config["enabled"] else "✗ No")
        status_table.add_row("Auto-accept", "✓ Yes" if config["auto_accept"] else "✗ No")
        status_table.add_row("Vibecode mode", "✓ Yes" if config["vibecode_mode"] else "✗ No")
        status_table.add_row("Config path", str(self.config_path))
        
        console.print(status_table)
        
        # Token usage
        if self.token_usage["total"] > 0:
            token_table = Table(title="Token Usage", show_header=True)
            token_table.add_column("Agent", style="cyan")
            token_table.add_column("Tokens", style="yellow")
            
            for agent, tokens in self.token_usage["by_agent"].items():
                token_table.add_row(agent, f"{tokens:,}")
            token_table.add_row("[bold]Total[/bold]", f"[bold]{self.token_usage['total']:,}[/bold]")
            
            console.print(token_table)
    
    def _execute_via_claude_mcp(self, task: str, agent: str) -> Tuple[bool, str]:
        """Execute task by creating a proxy request for the current Claude session."""
        console.print(f"[cyan]🤖 Creating proxy request for Claude MCP session...[/cyan]")
        
        # Check if CCI MCP server is running
        mcp_check = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, 
            text=True
        )
        
        if "mcp_persistent_server" not in mcp_check.stdout:
            console.print("[yellow]⚠️  CCI MCP server not running. Starting it...[/yellow]")
            # Start MCP server in background
            subprocess.Popen(
                ["python", "-m", "claude_code_indexer.mcp_persistent_server", 
                 "--port", "8765", "--protocol", "websocket"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(2)  # Wait for server to start
        
        # Create a proxy request file that the current Claude session can execute
        proxy_request = {
            "type": "god_mode_proxy_request",
            "task": task,
            "agent": agent,
            "timestamp": datetime.now().isoformat(),
            "instructions": "Please execute this task using available MCP tools and return results"
        }
        
        # Save proxy request
        proxy_file = Path(".god_mode_proxy_request.json")
        
        try:
            with open(proxy_file, 'w') as f:
                json.dump(proxy_request, f, indent=2)
            
            console.print(f"[green]✓ Proxy request created: {proxy_file}[/green]")
            console.print("[cyan]🔄 Forwarding to current Claude session...[/cyan]")
            
            # Signal to the user that they should execute the task
            console.print("\n" + "="*60)
            console.print("[bold yellow]GOD MODE PROXY REQUEST[/bold yellow]")
            console.print("="*60)
            console.print(f"\n[bold]Task:[/bold] {task}")
            console.print(f"[bold]Agent:[/bold] {agent}")
            console.print("\n[cyan]The current Claude session should now execute this task using MCP tools.[/cyan]")
            console.print("[dim]Waiting for execution results...[/dim]")
            console.print("="*60 + "\n")
            
            # Create a result file path
            result_file = Path(".god_mode_proxy_result.json")
            
            # Wait for result file (with timeout)
            timeout = 300  # 5 minutes
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if result_file.exists():
                    # Read the result
                    with open(result_file, 'r') as f:
                        result = json.load(f)
                    
                    # Clean up
                    result_file.unlink()
                    
                    if result.get("success"):
                        return True, result.get("output", "Task completed successfully")
                    else:
                        return False, result.get("error", "Unknown error")
                
                time.sleep(2)  # Check every 2 seconds
            
            # If no result after timeout, fallback
            console.print("[yellow]⚠️  No response from Claude session, using direct execution[/yellow]")
            return self._execute_cci_directly(task)
                
        except Exception as e:
            return False, f"Error creating proxy request: {e}"
        finally:
            # Clean up proxy request file
            if proxy_file.exists():
                proxy_file.unlink()
                
    def _execute_cci_directly(self, task: str) -> Tuple[bool, str]:
        """Fallback to direct CCI execution when MCP is not available."""
        try:
            results = []
            
            # Parse task to determine which CCI commands to run
            task_lower = task.lower()
            
            if "index" in task_lower:
                cmd = ["python", "-m", "claude_code_indexer.cli", "index", "."]
                result = subprocess.run(cmd, capture_output=True, text=True)
                results.append(f"Indexing: {'Success' if result.returncode == 0 else 'Failed'}")
            
            if "stat" in task_lower or "analyz" in task_lower:
                cmd = ["python", "-m", "claude_code_indexer.cli", "stats"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    results.append(f"Statistics:\n{result.stdout}")
            
            if "important" in task_lower or "function" in task_lower:
                cmd = ["python", "-m", "claude_code_indexer.cli", "query", "--important", "--limit", "5"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    results.append(f"Important functions:\n{result.stdout}")
                    
            if "insight" in task_lower or "health" in task_lower:
                cmd = ["python", "-m", "claude_code_indexer.cli", "insights"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    results.append(f"Insights:\n{result.stdout}")
            
            if results:
                return True, "\n\n".join(results)
            else:
                # Default: run stats and query
                cmd_stats = ["python", "-m", "claude_code_indexer.cli", "stats"]
                result_stats = subprocess.run(cmd_stats, capture_output=True, text=True)
                
                cmd_query = ["python", "-m", "claude_code_indexer.cli", "query", "--important", "--limit", "3"]
                result_query = subprocess.run(cmd_query, capture_output=True, text=True)
                
                output = []
                if result_stats.returncode == 0:
                    output.append(result_stats.stdout)
                if result_query.returncode == 0:
                    output.append(result_query.stdout)
                    
                return True, "\n".join(output) if output else "No results"
                
        except Exception as e:
            return False, f"Error executing CCI commands: {e}"
    
    async def simulate_multi_agent(self, task: str):
        """Simulate basic multi-agent execution (POC)."""
        # Load config to check if enabled
        if self.config_file.exists():
            import yaml
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
                self.enabled = config.get("enabled", False)
        
        if not self.enabled:
            console.print("[red]GOD mode is not enabled. Run 'god-mode --enable' first.[/red]")
            return
            
        console.print(Panel.fit(f"[bold]Task:[/bold] {task}", title="Multi-Agent Execution", border_style="cyan"))
        
        # Show MCP mode status
        if self.use_claude_mcp:
            console.print("[bold cyan]🚀 Using Claude MCP for execution[/bold cyan]")
        else:
            console.print("[yellow]⚠️  Claude MCP disabled, using simulation mode[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            if self.use_claude_mcp:
                # Execute via Claude MCP
                mcp_task = progress.add_task("[cyan]Executing via Claude MCP...", total=100)
                
                success, result = self._execute_via_claude_mcp(task, "general-purpose")
                progress.update(mcp_task, completed=100)
                
                if success:
                    console.print(Panel(result[:500] + "..." if len(result) > 500 else result, 
                                      title="Claude MCP Execution Result", 
                                      border_style="green"))
                    self._log_action("claude_mcp", "EXECUTE_TASK", "Success", tokens=1000)
                else:
                    console.print(Panel(f"[red]Error: {result}[/red]", 
                                      title="Claude MCP Execution Failed", 
                                      border_style="red"))
                    self._log_action("claude_mcp", "EXECUTE_TASK", f"Failed: {result}", tokens=0)
                    
                    # Fallback to simulation
                    console.print("[yellow]Falling back to simulation mode...[/yellow]")
                    await self._run_simulation(task, progress)
            else:
                # Run simulation mode
                await self._run_simulation(task, progress)
    
    async def _run_simulation(self, task: str, progress):
        """Run simulation mode when MCP is not available."""
        # Architect phase
        architect_task = progress.add_task("[cyan]Architect analyzing task...", total=100)
        await asyncio.sleep(2)  # Simulate API call
        progress.update(architect_task, completed=100)
        
        plan = f"1. Parse requirements\n2. Design solution\n3. Implement code\n4. Test implementation"
        self._log_action("architect", "CREATE_PLAN", plan, tokens=150)
        
        console.print(Panel(plan, title="Architect's Plan", border_style="blue"))
        
        # Developer phase
        dev_task = progress.add_task("[green]Developer implementing...", total=100)
        await asyncio.sleep(3)  # Simulate API call
        progress.update(dev_task, completed=100)
        
        implementation = "Code implementation completed (simulation)"
        self._log_action("developer", "IMPLEMENT_CODE", implementation, tokens=300)
        
        console.print(Panel(implementation, title="Developer's Implementation", border_style="green"))
        
        console.print("[bold green]✓ Multi-agent task completed![/bold green]")
        await self.status()


@click.group(name="god-mode")
def god_mode_group():
    """GOD Mode: Autonomous Multi-Agent Execution (BETA)."""
    pass


@god_mode_group.command(name="enable")
def enable_god_mode():
    """Enable GOD mode for autonomous execution."""
    orchestrator = GodModeOrchestrator()
    asyncio.run(orchestrator.enable())


@god_mode_group.command(name="disable")
def disable_god_mode():
    """Disable GOD mode (emergency stop)."""
    orchestrator = GodModeOrchestrator()
    asyncio.run(orchestrator.disable())


@god_mode_group.command(name="stop")
def stop_god_mode():
    """Emergency stop for GOD mode (alias for disable)."""
    orchestrator = GodModeOrchestrator()
    asyncio.run(orchestrator.disable())


@god_mode_group.command(name="status")
def god_mode_status():
    """Show GOD mode status and statistics."""
    orchestrator = GodModeOrchestrator()
    asyncio.run(orchestrator.status())


@god_mode_group.command(name="execute")
@click.argument("task", required=True)
def execute_task(task: str):
    """Execute a task using multi-agent coordination."""
    orchestrator = GodModeOrchestrator()
    asyncio.run(orchestrator.simulate_multi_agent(task))


@god_mode_group.command(name="start")
@click.option("--wait-time", default=300, help="Wait time between iterations in seconds (default: 300)")
@click.option("--max-issues", default=2, help="Maximum issues to process per iteration (default: 2)")
@click.option("--tmux", is_flag=True, help="Use tmux interface for multi-pane monitoring")
def start_continuous_loop(wait_time: int, max_issues: int, tmux: bool):
    """Start the continuous improvement loop.
    
    This runs the GOD Mode continuous improvement system that:
    - Monitors GitHub issues
    - Selects appropriate agents for each task
    - Implements improvements autonomously
    - Creates new improvement suggestions
    - Continues until interrupted (Ctrl+C)
    """
    import subprocess
    import sys
    
    # Check if tmux mode requested
    if tmux:
        if not TMUX_AVAILABLE:
            console.print("[red]Tmux integration module not available[/red]")
            return
        
        orchestrator = start_god_mode_tmux(wait_for_attach=True)
        if orchestrator:
            console.print("[green]✓ GOD Mode tmux interface started![/green]")
        return
    
    console.print(Panel.fit(
        "[bold yellow]🚀 Starting GOD Mode Continuous Improvement Loop[/bold yellow]\n\n"
        "[cyan]This will:[/cyan]\n"
        "• Monitor GitHub issues continuously\n"
        "• Select appropriate agents for tasks\n"
        "• Implement improvements autonomously\n"
        "• Create new improvement ideas\n"
        f"• Wait {wait_time}s between iterations\n"
        f"• Process up to {max_issues} issues per iteration\n\n"
        "[yellow]Press Ctrl+C to stop gracefully[/yellow]",
        title="GOD Mode Continuous Loop",
        border_style="green"
    ))
    
    # Check if the script exists
    script_path = Path(__file__).parent.parent.parent / "scripts" / "god_mode_continuous_loop.py"
    if not script_path.exists():
        console.print(f"[red]Error: Continuous loop script not found at {script_path}[/red]")
        return
    
    # Update environment variables for the script
    env = dict(sys.environ)
    env["GOD_MODE_WAIT_TIME"] = str(wait_time)
    env["GOD_MODE_MAX_ISSUES"] = str(max_issues)
    
    try:
        # Run the continuous improvement loop
        subprocess.run([sys.executable, str(script_path)], env=env)
    except KeyboardInterrupt:
        console.print("\n[yellow]Continuous improvement loop stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error running continuous loop: {e}[/red]")


@god_mode_group.command(name="tmux")
@click.option("--attach", is_flag=True, help="Attach to existing GOD mode tmux session")
@click.option("--kill", is_flag=True, help="Kill the GOD mode tmux session")
@click.option("--status", is_flag=True, help="Show tmux session status")
def manage_tmux(attach: bool, kill: bool, status: bool):
    """Manage GOD mode tmux sessions."""
    if not TMUX_AVAILABLE:
        console.print("[red]Tmux integration module not available[/red]")
        return
    
    orchestrator = TmuxOrchestrator()
    
    if kill:
        orchestrator.kill_session()
        return
    
    if status:
        if orchestrator.session_exists():
            console.print(f"[green]✓ GOD mode session '{orchestrator.session_name}' is active[/green]")
            status_report = orchestrator.get_status_report() if orchestrator.layout_created else {}
            if status_report:
                console.print("\nAgent Status:")
                for agent, info in status_report.get('agents', {}).items():
                    state = "🟢 Active" if info.get('active') else "⭕ Idle"
                    console.print(f"  {agent}: {state}")
        else:
            console.print("[yellow]No GOD mode tmux session found[/yellow]")
        return
    
    if attach:
        attach_god_mode_tmux()
    else:
        # Default: start new session
        start_god_mode_tmux(wait_for_attach=True)


@god_mode_group.command(name="agent")
@click.argument("agent_name", required=True)
@click.argument("task", required=True)
@click.option("--tmux", is_flag=True, help="Execute in tmux session")
def execute_agent_task(agent_name: str, task: str, tmux: bool):
    """Execute a task with a specific agent."""
    if tmux and TMUX_AVAILABLE:
        orchestrator = TmuxOrchestrator()
        if not orchestrator.session_exists():
            console.print("[yellow]No tmux session found. Starting one...[/yellow]")
            orchestrator = start_god_mode_tmux(wait_for_attach=False)
            if not orchestrator:
                return
        
        task_id = orchestrator.execute_agent_task(agent_name, task)
        console.print(f"[green]✓ Task queued for {agent_name}: {task_id}[/green]")
        console.print(f"[cyan]Run 'tmux attach -t {orchestrator.session_name}' to monitor[/cyan]")
    else:
        # Fallback to regular execution
        orchestrator = GodModeOrchestrator()
        asyncio.run(orchestrator.simulate_multi_agent(f"[{agent_name}] {task}"))


@god_mode_group.command(name="dashboard")
@click.option("--port", default=None, type=int, help="API server port (default: random)")
@click.option("--no-browser", is_flag=True, help="Don't open browser automatically")
def launch_dashboard(port: Optional[int], no_browser: bool):
    """Launch the GOD Mode Web Dashboard with random ports."""
    import subprocess
    import webbrowser
    import json
    from pathlib import Path
    
    # Check if dashboard is already running
    urls_file = Path.home() / '.god-mode' / 'dashboard_urls.json'
    if urls_file.exists():
        try:
            with open(urls_file, 'r') as f:
                urls = json.load(f)
            
            console.print(Panel.fit(
                "[yellow]⚠️  Dashboard already running![/yellow]\n\n"
                f"[cyan]Dashboard URL:[/cyan] {urls['dashboard_url']}\n"
                f"[cyan]API URL:[/cyan] {urls['api_url']}\n"
                f"[dim]Started at: {urls['started_at']}[/dim]",
                title="Existing Dashboard",
                border_style="yellow"
            ))
            
            if not no_browser:
                webbrowser.open(urls['dashboard_url'])
            return
        except:
            # File might be corrupted, continue with launch
            pass
    
    console.print(Panel.fit(
        "[bold cyan]🚀 Launching GOD Mode Web Dashboard[/bold cyan]\n\n"
        "[yellow]Features:[/yellow]\n"
        "• Auto-selects random available ports\n"
        "• Claude Code subagent integration\n"
        "• Real-time task monitoring\n"
        "• WebSocket live updates\n\n"
        "[green]The dashboard will open automatically![/green]\n"
        "[dim]Press Ctrl+C to stop[/dim]",
        title="Web Dashboard",
        border_style="cyan"
    ))
    
    # Start the dashboard launcher script
    launcher_path = Path(__file__).parent.parent / "domains" / "web" / "start_dashboard.py"
    
    if not launcher_path.exists():
        console.print(f"[red]Dashboard launcher not found at {launcher_path}[/red]")
        return
    
    try:
        # Prepare command
        cmd = [sys.executable, str(launcher_path)]
        
        # Add arguments
        if port:
            cmd.extend(['--backend-port', str(port)])
        if no_browser:
            cmd.extend(['--no-browser'])
        
        # Run the launcher
        subprocess.run(cmd)
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error launching dashboard: {e}[/red]")