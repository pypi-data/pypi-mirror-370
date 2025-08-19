"""Tmux integration for GOD Mode multi-agent orchestration."""
import subprocess
import shutil
import time
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime

from rich.console import Console

console = Console()


class TmuxOrchestrator:
    """Orchestrate GOD Mode agents using tmux for parallel execution and monitoring."""
    
    def __init__(self, session_name: str = "god-mode"):
        self.session_name = session_name
        self.panes: Dict[str, str] = {}
        self.layout_created = False
        self.output_dir = Path("/tmp/god-mode-outputs")
        self.output_dir.mkdir(exist_ok=True)
        
    def check_tmux_available(self) -> bool:
        """Check if tmux is installed and available."""
        return shutil.which('tmux') is not None
    
    def session_exists(self) -> bool:
        """Check if GOD mode tmux session already exists."""
        try:
            result = subprocess.run(
                ['tmux', 'has-session', '-t', self.session_name],
                capture_output=True
            )
            return result.returncode == 0
        except:
            return False
    
    def create_session(self) -> bool:
        """Create new tmux session for GOD mode."""
        try:
            if self.session_exists():
                console.print(f"[yellow]Session '{self.session_name}' already exists[/yellow]")
                return True
                
            # Create new detached session
            subprocess.run([
                'tmux', 'new-session', '-d', '-s', self.session_name,
                '-n', 'control'  # Name first window 'control'
            ], check=True)
            
            console.print(f"[green]✓ Created tmux session '{self.session_name}'[/green]")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to create tmux session: {e}[/red]")
            return False
    
    def create_layout(self) -> bool:
        """Create the 6-pane layout for GOD mode."""
        try:
            # Start with the main window
            self.panes['control'] = f"{self.session_name}:control.0"
            
            # Create horizontal split for status (30% right)
            subprocess.run([
                'tmux', 'split-window', '-h', '-p', '30',
                '-t', self.session_name
            ], check=True)
            self.panes['status'] = f"{self.session_name}:control.1"
            
            # Select left pane and split vertically for architect
            subprocess.run([
                'tmux', 'select-pane', '-t', f"{self.session_name}:control.0"
            ], check=True)
            subprocess.run([
                'tmux', 'split-window', '-v', '-p', '66',
                '-t', self.session_name
            ], check=True)
            self.panes['architect'] = f"{self.session_name}:control.2"
            
            # Split architect pane for developer
            subprocess.run([
                'tmux', 'split-window', '-v', '-p', '50',
                '-t', f"{self.session_name}:control.2"
            ], check=True)
            self.panes['developer'] = f"{self.session_name}:control.3"
            
            # Select right pane and split for audit trail
            subprocess.run([
                'tmux', 'select-pane', '-t', f"{self.session_name}:control.1"
            ], check=True)
            subprocess.run([
                'tmux', 'split-window', '-v', '-p', '66',
                '-t', self.session_name
            ], check=True)
            self.panes['audit'] = f"{self.session_name}:control.4"
            
            # Split audit pane for MCP server
            subprocess.run([
                'tmux', 'split-window', '-v', '-p', '50',
                '-t', f"{self.session_name}:control.4"
            ], check=True)
            self.panes['mcp'] = f"{self.session_name}:control.5"
            
            # Initialize each pane with a title
            self._initialize_panes()
            
            self.layout_created = True
            console.print("[green]✓ Created 6-pane layout[/green]")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to create layout: {e}[/red]")
            return False
    
    def _initialize_panes(self):
        """Initialize each pane with appropriate content."""
        pane_configs = {
            'control': {
                'title': '🎮 GOD Mode Control Panel',
                'command': 'echo "GOD Mode Control Panel initialized"; echo "Type commands here..."'
            },
            'status': {
                'title': '📊 Agent Status Monitor',
                'command': 'watch -n 1 "echo Agent Status; date"'
            },
            'architect': {
                'title': '🏗️ Architect Agent',
                'command': 'echo "Architect Agent Ready"; echo "Waiting for tasks..."'
            },
            'developer': {
                'title': '💻 Developer Agent', 
                'command': 'echo "Developer Agent Ready"; echo "Waiting for implementation tasks..."'
            },
            'audit': {
                'title': '📝 Audit Trail',
                'command': f'tail -f {self.output_dir}/audit.log 2>/dev/null || echo "Audit trail started..."'
            },
            'mcp': {
                'title': '🔌 MCP Server',
                'command': 'echo "MCP Server Monitor"; echo "Checking server status..."'
            }
        }
        
        for pane_name, config in pane_configs.items():
            if pane_name in self.panes:
                # Clear pane and set title
                self.send_command(pane_name, 'clear')
                self.send_command(pane_name, f'echo "\\033[1;36m{config["title"]}\\033[0m"')
                self.send_command(pane_name, 'echo "' + "="*50 + '"')
                self.send_command(pane_name, config['command'])
    
    def send_command(self, pane: str, command: str) -> bool:
        """Send command to specific pane."""
        try:
            pane_id = self.panes.get(pane, pane)
            subprocess.run([
                'tmux', 'send-keys', '-t', pane_id, command, 'Enter'
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def capture_output(self, pane: str, lines: int = 50) -> str:
        """Capture output from specific pane."""
        try:
            pane_id = self.panes.get(pane, pane)
            result = subprocess.run([
                'tmux', 'capture-pane', '-t', pane_id, '-p', '-S', f'-{lines}'
            ], capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError:
            return ""
    
    def write_to_pane(self, pane: str, content: str):
        """Write content directly to pane (replacing current content)."""
        # Clear pane first
        self.send_command(pane, 'clear')
        
        # Write content line by line
        for line in content.split('\n'):
            # Escape special characters
            escaped_line = line.replace('"', '\\"').replace('$', '\\$')
            self.send_command(pane, f'echo "{escaped_line}"')
    
    async def monitor_pane(self, pane: str, callback: Callable[[str], None], interval: float = 1.0):
        """Monitor pane output and call callback on changes."""
        last_output = ""
        pane_id = self.panes.get(pane, pane)
        
        while True:
            try:
                current_output = self.capture_output(pane)
                if current_output != last_output:
                    callback(current_output)
                    last_output = current_output
                await asyncio.sleep(interval)
            except Exception as e:
                console.print(f"[red]Error monitoring pane {pane}: {e}[/red]")
                await asyncio.sleep(interval * 2)
    
    def attach_session(self):
        """Attach to the GOD mode tmux session."""
        try:
            subprocess.run(['tmux', 'attach-session', '-t', self.session_name])
        except subprocess.CalledProcessError:
            console.print("[red]Failed to attach to session[/red]")
    
    def kill_session(self):
        """Kill the GOD mode tmux session."""
        try:
            subprocess.run(['tmux', 'kill-session', '-t', self.session_name], check=True)
            console.print(f"[yellow]Killed tmux session '{self.session_name}'[/yellow]")
        except subprocess.CalledProcessError:
            pass  # Session might not exist
    
    def execute_agent_task(self, agent: str, task: str) -> str:
        """Execute a task in the specified agent's pane."""
        if agent not in self.panes:
            return f"Unknown agent: {agent}"
        
        # Create unique task ID
        task_id = f"{agent}_{int(time.time())}"
        output_file = self.output_dir / f"{task_id}.json"
        
        # Prepare task command
        task_data = {
            'task_id': task_id,
            'agent': agent,
            'task': task,
            'timestamp': datetime.now().isoformat()
        }
        
        # Write task file
        with open(output_file, 'w') as f:
            json.dump(task_data, f)
        
        # Send command to agent pane
        if agent == 'architect':
            command = f'echo "\\n🏗️ Task: {task}"; echo "Planning..."; sleep 2; echo "✓ Plan created"'
        elif agent == 'developer':
            command = f'echo "\\n💻 Task: {task}"; echo "Implementing..."; sleep 3; echo "✓ Implementation complete"'
        else:
            command = f'echo "\\n📋 Task: {task}"; echo "Processing..."; sleep 1; echo "✓ Done"'
        
        self.send_command(agent, command)
        return task_id
    
    def get_status_report(self) -> Dict[str, any]:
        """Generate status report for all agents."""
        status = {
            'session': self.session_name,
            'agents': {},
            'timestamp': datetime.now().isoformat()
        }
        
        for agent, pane_id in self.panes.items():
            # Capture last 10 lines from each pane
            output = self.capture_output(agent, lines=10)
            status['agents'][agent] = {
                'pane_id': pane_id,
                'last_output': output.strip().split('\n')[-3:] if output else [],
                'active': bool(output and not output.endswith('Waiting for tasks...'))
            }
        
        return status
    
    def update_status_pane(self):
        """Update the status pane with current agent states."""
        status = self.get_status_report()
        
        # Format status display
        status_lines = [
            "📊 Agent Status Monitor",
            "=" * 50,
            f"Session: {status['session']}",
            f"Updated: {datetime.now().strftime('%H:%M:%S')}",
            "",
            "Agents:"
        ]
        
        for agent, info in status['agents'].items():
            if agent != 'status':  # Don't show status pane itself
                state = "🟢 Active" if info['active'] else "⭕ Idle"
                status_lines.append(f"  {agent}: {state}")
                if info['last_output']:
                    status_lines.append(f"    └─ {info['last_output'][-1][:40]}...")
        
        # Write to status pane
        self.write_to_pane('status', '\n'.join(status_lines))


# Convenience functions for CLI integration
def start_god_mode_tmux(wait_for_attach: bool = True):
    """Start GOD mode with tmux interface."""
    orchestrator = TmuxOrchestrator()
    
    if not orchestrator.check_tmux_available():
        console.print("[red]Tmux is not installed. Please install tmux first.[/red]")
        console.print("[yellow]Ubuntu/Debian: sudo apt-get install tmux[/yellow]")
        console.print("[yellow]macOS: brew install tmux[/yellow]")
        return None
    
    # Create session and layout
    if orchestrator.create_session():
        if orchestrator.create_layout():
            console.print("[green]✓ GOD Mode tmux interface ready![/green]")
            console.print(f"[cyan]Run 'tmux attach -t {orchestrator.session_name}' to connect[/cyan]")
            
            if wait_for_attach:
                console.print("\n[yellow]Attaching to session in 2 seconds...[/yellow]")
                time.sleep(2)
                orchestrator.attach_session()
            
            return orchestrator
    
    return None


def attach_god_mode_tmux():
    """Attach to existing GOD mode tmux session."""
    orchestrator = TmuxOrchestrator()
    
    if orchestrator.session_exists():
        orchestrator.attach_session()
    else:
        console.print("[red]No GOD mode session found.[/red]")
        console.print("[yellow]Run 'claude-code-indexer god-mode start --tmux' first[/yellow]")