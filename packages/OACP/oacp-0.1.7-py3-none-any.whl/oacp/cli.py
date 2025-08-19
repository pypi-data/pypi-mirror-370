"""CLI interface for OACP."""

import json
import os
import platform
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Confirm, Prompt

from .trace import TraceReader, TraceWriter
from .storage import create_storage
from .context import get_config
from .events import EventBase, VoteDecision
from .errors import OacpStorageError

app = typer.Typer(name="oacp", help="OACP CLI for trace management and analysis")
console = Console()

# Create separate Typer apps for subcommands
logs_app = typer.Typer(help="Log management commands")
env_app = typer.Typer(help="Environment setup commands")
app.add_typer(logs_app, name="logs")
app.add_typer(env_app, name="env")


@logs_app.command("tail")
def tail_logs(
    run_id: str = typer.Option(..., "--run-id", help="Run ID to tail"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines to show"),
    event_type: Optional[str] = typer.Option(None, "--type", help="Filter by event type"),
):
    """Tail logs for a specific run."""
    config = get_config()
    storage = create_storage(config["storage_uri"])
    reader = TraceReader(storage)
    
    try:
        events = list(reader.read_run(run_id))
        
        if not events:
            console.print(f"[red]No events found for run: {run_id}[/red]")
            return
        
        # Filter by event type if specified
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        # Show last N events
        recent_events = events[-lines:] if len(events) > lines else events
        
        for event in recent_events:
            _print_event(event)
        
        if follow:
            console.print("[yellow]Following logs... (Ctrl+C to stop)[/yellow]")
            last_count = len(events)
            
            try:
                while True:
                    time.sleep(1)
                    current_events = list(reader.read_run(run_id))
                    
                    # Apply filter
                    if event_type:
                        current_events = [e for e in current_events if e.event_type == event_type]
                    
                    if len(current_events) > last_count:
                        new_events = current_events[last_count:]
                        for event in new_events:
                            _print_event(event)
                        last_count = len(current_events)
                        
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped following logs.[/yellow]")
                
    except Exception as e:
        console.print(f"[red]Error reading logs: {e}[/red]")
    finally:
        reader.close()


@logs_app.command("timeline")
def timeline(
    run_id: str = typer.Option(..., "--run-id", help="Run ID to show timeline for"),
    format: str = typer.Option("table", "--format", help="Output format (table, json)"),
    event_type: Optional[str] = typer.Option(None, "--type", help="Filter by event type"),
):
    """Show timeline view of events for a run."""
    config = get_config()
    storage = create_storage(config["storage_uri"])
    reader = TraceReader(storage)
    
    try:
        events = list(reader.read_run(run_id))
        
        if not events:
            console.print(f"[red]No events found for run: {run_id}[/red]")
            return
        
        # Filter by event type if specified
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if format == "json":
            output = [event.model_dump() for event in events]
            console.print_json(json.dumps(output, default=str, indent=2))
        else:
            _print_timeline_table(events)
            
    except Exception as e:
        console.print(f"[red]Error reading timeline: {e}[/red]")
    finally:
        reader.close()


@app.command("replay")
def replay(
    run_id: str = typer.Option(..., "--run-id", help="Run ID to replay"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show replay plan without executing"),
    start_from: Optional[str] = typer.Option(None, "--start-from", help="Start replay from specific event ID"),
):
    """Replay a run deterministically."""
    config = get_config()
    storage = create_storage(config["storage_uri"])
    reader = TraceReader(storage)
    
    try:
        events = list(reader.read_run(run_id))
        
        if not events:
            console.print(f"[red]No events found for run: {run_id}[/red]")
            return
        
        # Filter events if start_from is specified
        if start_from:
            start_index = next(
                (i for i, e in enumerate(events) if e.event_id == start_from),
                None
            )
            if start_index is None:
                console.print(f"[red]Event ID {start_from} not found in run[/red]")
                return
            events = events[start_index:]
        
        console.print(f"[blue]Replay plan for run: {run_id}[/blue]")
        
        # Group events by node for better visualization
        nodes = {}
        for event in events:
            node_id = getattr(event, 'node_id', 'system')
            if node_id not in nodes:
                nodes[node_id] = []
            nodes[node_id].append(event)
        
        # Show replay plan
        table = Table(title="Replay Plan")
        table.add_column("Step", justify="right", style="cyan")
        table.add_column("Node ID", style="magenta")
        table.add_column("Event Type", style="green")
        table.add_column("Timestamp", style="blue")
        table.add_column("Details", style="white")
        
        step = 1
        for node_id, node_events in nodes.items():
            for event in node_events:
                details = _event_summary(event)
                table.add_row(
                    str(step),
                    node_id[:20],  # Truncate long node IDs
                    event.event_type,
                    event.timestamp.strftime("%H:%M:%S.%f")[:-3],
                    details
                )
                step += 1
        
        console.print(table)
        
        if dry_run:
            console.print(f"[yellow]Dry run complete. {len(events)} events would be replayed.[/yellow]")
        else:
            console.print("[red]Actual replay execution not implemented yet.[/red]")
            console.print("[dim]This would require re-executing the original graph with recorded inputs.[/dim]")
            
    except Exception as e:
        console.print(f"[red]Error during replay: {e}[/red]")
    finally:
        reader.close()


@app.command("list")
def list_runs(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of runs to show"),
    status: Optional[str] = typer.Option(None, "--status", help="Filter by run status"),
):
    """List recent runs."""
    config = get_config()
    
    try:
        storage = create_storage(config["storage_uri"])
        
        if config["storage_uri"].startswith("file://"):
            _list_file_runs(storage, limit, status)
        else:
            _list_db_runs(storage, limit, status)
            
    except Exception as e:
        console.print(f"[red]Error listing runs: {e}[/red]")


def _list_file_runs(storage, limit: int, status: Optional[str]):
    """List runs from file storage."""
    config = get_config()
    path = Path(config["storage_uri"][7:])
    
    if not path.exists():
        console.print("[red]No log directory found.[/red]")
        return
    
    log_files = list(path.glob("*.jsonl"))
    log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    table = Table(title="Recent Runs")
    table.add_column("Run ID", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Last Modified", style="blue")
    table.add_column("Size", justify="right", style="green")
    table.add_column("Events", justify="right", style="magenta")
    table.add_column("Nodes", justify="right", style="yellow")
    
    for log_file in log_files[:limit]:
        run_id = log_file.stem
        stat = log_file.stat()
        
        # Analyze run
        run_status, event_count, node_count = _analyze_run_file(log_file)
        
        # Filter by status if specified
        if status and run_status != status:
            continue
        
        # Style status
        status_style = {
            "completed": "green",
            "failed": "red", 
            "cancelled": "yellow",
            "running": "blue",
        }.get(run_status, "white")
        
        table.add_row(
            run_id,
            f"[{status_style}]{run_status}[/{status_style}]",
            datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            f"{stat.st_size:,} bytes",
            str(event_count),
            str(node_count)
        )
    
    console.print(table)


def _list_db_runs(storage, limit: int, status: Optional[str]):
    """List runs from database storage."""
    # This would query the database for run metadata
    console.print("[yellow]Database run listing not yet implemented.[/yellow]")
    console.print("[dim]Would query for run summaries and metadata.[/dim]")


def _analyze_run_file(log_file: Path) -> tuple[str, int, int]:
    """Analyze a run log file and return status, event count, and node count."""
    event_count = 0
    nodes = set()
    run_status = "running"  # Default
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    event_count += 1
                    try:
                        event_data = json.loads(line)
                        # Track unique nodes
                        if 'node_id' in event_data:
                            nodes.add(event_data['node_id'])
                        
                        # Check for run summary to get final status
                        if event_data.get('event_type') == 'RunSummary':
                            run_status = event_data.get('status', 'completed')
                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass
    
    return run_status, event_count, len(nodes)


@app.command("stats")
def show_stats(
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Show stats for specific run"),
    days: int = typer.Option(7, "--days", help="Show stats for last N days"),
):
    """Show statistics and metrics."""
    config = get_config()
    
    if run_id:
        _show_run_stats(run_id, config)
    else:
        _show_global_stats(days, config)


def _show_run_stats(run_id: str, config: dict):
    """Show detailed statistics for a specific run."""
    storage = create_storage(config["storage_uri"])
    reader = TraceReader(storage)
    
    try:
        events = list(reader.read_run(run_id))
        
        if not events:
            console.print(f"[red]No events found for run: {run_id}[/red]")
            return
        
        # Calculate statistics
        stats = _calculate_run_stats(events)
        
        # Display stats in panels
        console.print(Panel(f"[bold]Run Statistics: {run_id}[/bold]"))
        
        # Overview stats
        overview_table = Table(title="Overview")
        overview_table.add_column("Metric", style="cyan")
        overview_table.add_column("Value", style="green")
        
        overview_table.add_row("Total Events", str(stats['total_events']))
        overview_table.add_row("Unique Nodes", str(stats['unique_nodes']))
        overview_table.add_row("Total Votes", str(stats['total_votes']))
        overview_table.add_row("Consensus Reached", str(stats['consensus_reached']))
        overview_table.add_row("Conflicts Raised", str(stats['conflicts_raised']))
        overview_table.add_row("Retries", str(stats['retries']))
        
        if stats['duration_ms']:
            overview_table.add_row("Duration", f"{stats['duration_ms']/1000:.2f}s")
        
        console.print(overview_table)
        
        # Event type breakdown
        if stats['event_types']:
            event_table = Table(title="Event Types")
            event_table.add_column("Event Type", style="magenta")
            event_table.add_column("Count", style="green")
            
            for event_type, count in sorted(stats['event_types'].items()):
                event_table.add_row(event_type, str(count))
            
            console.print(event_table)
        
    except Exception as e:
        console.print(f"[red]Error calculating stats: {e}[/red]")
    finally:
        reader.close()


def _show_global_stats(days: int, config: dict):
    """Show global statistics across all runs."""
    console.print(f"[yellow]Global statistics for last {days} days not yet implemented.[/yellow]")
    console.print("[dim]Would aggregate stats across all runs in the time period.[/dim]")


def _calculate_run_stats(events: list[EventBase]) -> dict:
    """Calculate statistics for a run."""
    stats = {
        'total_events': len(events),
        'unique_nodes': len(set(getattr(e, 'node_id', None) for e in events if hasattr(e, 'node_id'))),
        'total_votes': len([e for e in events if e.event_type == 'VoteCast']),
        'consensus_reached': len([e for e in events if e.event_type == 'DecisionFinalized' and getattr(e, 'approved', False)]),
        'conflicts_raised': len([e for e in events if e.event_type == 'ConflictRaised']),
        'retries': len([e for e in events if e.event_type == 'RetryScheduled']),
        'event_types': {},
        'duration_ms': None,
    }
    
    # Count event types
    for event in events:
        event_type = event.event_type
        stats['event_types'][event_type] = stats['event_types'].get(event_type, 0) + 1
    
    # Calculate duration if we have start and end
    if events:
        start_time = min(e.timestamp for e in events)
        end_time = max(e.timestamp for e in events)
        stats['duration_ms'] = int((end_time - start_time).total_seconds() * 1000)
    
    return stats


@app.command("config")
def show_config():
    """Show current OACP configuration."""
    config = get_config()
    
    table = Table(title="OACP Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Source", style="dim")
    
    # Show key configuration values
    for key, value in config.items():
        if key == "redact_keys":
            value = ", ".join(value)
        elif key in ["signing_key"] and value:
            value = "*" * 8  # Redact sensitive values
        
        source = "env" if key.upper() in ["OACP_" + k.upper() for k in config.keys()] else "default"
        table.add_row(key, str(value), source)
    
    console.print(table)


@app.command("serve")
def serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload for development"),
):
    """Start OACP web dashboard and API server."""
    try:
        from .web import serve as web_serve
        web_serve(host=host, port=port, reload=reload)
    except ImportError:
        console.print("[red]FastAPI and uvicorn required for web dashboard.[/red]")
        console.print("Install with: [cyan]pip install 'oacp[web]'[/cyan]")
        return
    except Exception as e:
        console.print(f"[red]Error starting web server: {e}[/red]")


@env_app.command("setup")
def setup_environment(
    global_config: bool = typer.Option(False, "--global", help="Setup global OACP environment"),
    storage_path: Optional[str] = typer.Option(None, "--storage", help="Custom storage path"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing configuration"),
):
    """Setup OACP environment variables and configuration."""
    console.print("🚀 [bold]OACP Environment Setup[/bold]")
    console.print()
    
    # Determine config location
    if global_config:
        if platform.system() == "Windows":
            config_dir = Path(os.environ.get("APPDATA", "")) / "oacp"
        else:
            config_dir = Path.home() / ".config" / "oacp"
    else:
        config_dir = Path.cwd() / ".oacp"
    
    config_file = config_dir / "config.json"
    env_file = config_dir / ".env"
    
    # Create config directory
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if config already exists
    if config_file.exists() and not force:
        if not Confirm.ask(f"Configuration already exists at {config_file}. Overwrite?"):
            console.print("[yellow]Setup cancelled.[/yellow]")
            return
    
    # Interactive setup
    console.print("[cyan]📋 Configuration Setup[/cyan]")
    
    # Storage configuration
    if not storage_path:
        storage_options = {
            "1": "File-based (logs/)",
            "2": "SQLite database",
            "3": "PostgreSQL",
            "4": "Custom path"
        }
        
        console.print("\n[bold]Choose storage backend:[/bold]")
        for key, desc in storage_options.items():
            console.print(f"  {key}. {desc}")
        
        choice = Prompt.ask("Select option", choices=list(storage_options.keys()), default="1")
        
        if choice == "1":
            storage_path = "file://logs"
        elif choice == "2":
            storage_path = "sqlite://oacp.db"
        elif choice == "3":
            db_url = Prompt.ask("PostgreSQL URL", default="postgresql://user:pass@localhost/oacp")
            storage_path = db_url
        elif choice == "4":
            storage_path = Prompt.ask("Custom storage path")
    
    # Create configuration
    config = {
        "storage_uri": storage_path,
        "default_timeout": 30,
        "max_retries": 3,
        "enable_adaptive_prompting": True,
        "redact_keys": ["password", "token", "key", "secret"],
        "log_level": "INFO"
    }
    
    # Write configuration
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Create environment file
    env_content = f"""# OACP Environment Configuration
# Generated by: oacp env setup
OACP_STORAGE_URI={storage_path}
OACP_LOG_LEVEL=INFO
OACP_ENABLE_ADAPTIVE_PROMPTING=true
OACP_MAX_RETRIES=3
OACP_DEFAULT_TIMEOUT=30

# Add your API keys here:
# OPENAI_API_KEY=your_openai_key
# ANTHROPIC_API_KEY=your_anthropic_key
# GOOGLE_API_KEY=your_google_key
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    console.print(f"✅ [green]Configuration saved to:[/green] {config_file}")
    console.print(f"✅ [green]Environment template saved to:[/green] {env_file}")
    
    # Show next steps
    console.print("\n[bold]🎯 Next Steps:[/bold]")
    console.print(f"1. Add API keys to: {env_file}")
    
    if global_config:
        console.print("2. Global OACP configuration is now active")
    else:
        console.print("2. Load environment in your project:")
        console.print(f"   [dim]source {env_file}[/dim]  # Linux/Mac")
        console.print(f"   [dim]Get-Content {env_file} | ForEach-Object {{$env:($_.Split('=')[0])=$_.Split('=')[1]}}[/dim]  # Windows PowerShell")
    
    console.print("3. Test with: [cyan]oacp config[/cyan]")
    console.print("4. Start using OACP in your code!")


@env_app.command("status")
def environment_status():
    """Show current environment status and configuration."""
    console.print("🔍 [bold]OACP Environment Status[/bold]")
    console.print()
    
    # Check if OACP is properly installed
    try:
        import oacp
        version = getattr(oacp, '__version__', 'unknown')
        console.print(f"✅ [green]OACP installed:[/green] v{version}")
    except ImportError:
        console.print("❌ [red]OACP not installed[/red]")
        return
    
    # Check environment variables
    env_vars = [
        "OACP_STORAGE_URI",
        "OACP_LOG_LEVEL", 
        "OACP_ENABLE_ADAPTIVE_PROMPTING",
        "OACP_MAX_RETRIES",
        "OACP_DEFAULT_TIMEOUT",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY"
    ]
    
    table = Table(title="Environment Variables")
    table.add_column("Variable", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Value", style="dim")
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            if "key" in var.lower() or "token" in var.lower():
                display_value = f"{value[:8]}..." if len(value) > 8 else value
            else:
                display_value = value
            table.add_row(var, "[green]✓ Set[/green]", display_value)
        else:
            table.add_row(var, "[yellow]✗ Not Set[/yellow]", "-")
    
    console.print(table)
    
    # Check configuration files
    console.print("\n[bold]📁 Configuration Files:[/bold]")
    
    config_locations = []
    
    # Global config
    if platform.system() == "Windows":
        global_config = Path(os.environ.get("APPDATA", "")) / "oacp" / "config.json"
    else:
        global_config = Path.home() / ".config" / "oacp" / "config.json"
    
    # Local config
    local_config = Path.cwd() / ".oacp" / "config.json"
    
    config_locations = [
        ("Global", global_config),
        ("Local", local_config)
    ]
    
    for name, path in config_locations:
        if path.exists():
            console.print(f"✅ [green]{name}:[/green] {path}")
        else:
            console.print(f"❌ [dim]{name}:[/dim] {path} (not found)")
    
    # Show current active config
    try:
        config = get_config()
        console.print(f"\n[bold]📋 Active Configuration:[/bold]")
        active_table = Table()
        active_table.add_column("Setting", style="cyan")
        active_table.add_column("Value", style="green")
        
        for key, value in config.items():
            if "key" in key.lower():
                value = "*" * 8 if value else "Not Set"
            active_table.add_row(key, str(value))
        
        console.print(active_table)
        
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")


@env_app.command("init")
def init_project(
    name: Optional[str] = typer.Option(None, "--name", help="Project name"),
    template: str = typer.Option("basic", "--template", help="Project template (basic, research, multi-agent)"),
):
    """Initialize a new OACP project."""
    if not name:
        name = Prompt.ask("Project name")
    
    project_dir = Path(name)
    
    if project_dir.exists():
        if not Confirm.ask(f"Directory '{name}' already exists. Continue?"):
            console.print("[yellow]Project initialization cancelled.[/yellow]")
            return
    
    project_dir.mkdir(exist_ok=True)
    
    console.print(f"🚀 [bold]Initializing OACP project: {name}[/bold]")
    
    # Create project structure
    (project_dir / "agents").mkdir(exist_ok=True)
    (project_dir / "logs").mkdir(exist_ok=True)
    (project_dir / ".oacp").mkdir(exist_ok=True)
    
    # Create basic files based on template
    if template == "basic":
        _create_basic_template(project_dir, name)
    elif template == "research":
        _create_research_template(project_dir, name)
    elif template == "multi-agent":
        _create_multiagent_template(project_dir, name)
    else:
        console.print(f"[red]Unknown template: {template}[/red]")
        return
    
    console.print(f"✅ [green]Project '{name}' initialized successfully![/green]")
    console.print(f"\n[bold]Next steps:[/bold]")
    console.print(f"1. cd {name}")
    console.print("2. pip install -r requirements.txt")
    console.print("3. oacp env setup")
    console.print("4. Edit your agents and run main.py")


def _create_basic_template(project_dir: Path, name: str):
    """Create basic project template."""
    # main.py
    main_content = f'''"""
{name} - Basic OACP Project
"""

from oacp import with_oacp, DecisionContract, VotingStrategy
import os

# Set up your LLM client here
# from openai import OpenAI
# client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@with_oacp(
    role="processor",
    contract=DecisionContract(
        voting_strategy=VotingStrategy.MAJORITY,
        min_votes=2,
        timeout_seconds=30
    ),
    adaptive_prompting=True
)
def process_task(task_description: str):
    """Process a task with OACP governance."""
    
    # Your LLM processing logic here
    # response = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[{{"role": "user", "content": task_description}}]
    # )
    # return response.choices[0].message.content
    
    # For demo purposes:
    return f"Processed: {{task_description}}"

if __name__ == "__main__":
    print("🚀 Running {name}")
    result = process_task("Analyze the benefits of renewable energy")
    print("Result:", result)
'''
    
    with open(project_dir / "main.py", 'w') as f:
        f.write(main_content)
    
    # requirements.txt
    requirements = """oacp>=0.1.4
openai>=1.0.0
python-dotenv>=1.0.0
"""
    
    with open(project_dir / "requirements.txt", 'w') as f:
        f.write(requirements)
    
    # .env template
    env_template = """# API Keys
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here

# OACP Configuration
OACP_STORAGE_URI=file://logs
OACP_LOG_LEVEL=INFO
"""
    
    with open(project_dir / ".env", 'w') as f:
        f.write(env_template)
    
    # README.md
    readme = f"""# {name}

Basic OACP project for AI governance and consensus.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment:
   ```bash
   oacp env setup
   ```

3. Add your API keys to `.env`

4. Run the project:
   ```bash
   python main.py
   ```

## OACP Features

- ✅ Consensus voting
- ✅ Adaptive prompting  
- ✅ Audit trails
- ✅ Error handling
"""
    
    with open(project_dir / "README.md", 'w') as f:
        f.write(readme)


def _create_research_template(project_dir: Path, name: str):
    """Create research team template."""
    console.print("[dim]Research template not yet implemented.[/dim]")


def _create_multiagent_template(project_dir: Path, name: str):
    """Create multi-agent template.""" 
    console.print("[dim]Multi-agent template not yet implemented.[/dim]")


def _print_event(event: EventBase):
    """Print a single event in a formatted way."""
    timestamp = event.timestamp.strftime("%H:%M:%S.%f")[:-3]
    event_id = event.event_id[:8]
    
    style_map = {
        "TaskStart": "bold green",
        "NodeStart": "green",
        "NodeResult": "blue", 
        "VoteCast": "yellow",
        "ConflictRaised": "red",
        "DecisionFinalized": "cyan",
        "RetryScheduled": "magenta",
        "RunSummary": "bold blue",
    }
    
    style = style_map.get(event.event_type, "white")
    
    console.print(
        f"[dim]{timestamp}[/dim] "
        f"[{style}]{event.event_type}[/{style}] "
        f"[dim]{event_id}[/dim] "
        f"{_event_summary(event)}"
    )


def _event_summary(event: EventBase) -> str:
    """Generate a summary string for an event."""
    summary_parts = []
    
    # Add node info if available
    if hasattr(event, 'node_id') and event.node_id:
        summary_parts.append(f"node={event.node_id[:12]}")
        
        if hasattr(event, 'role') and event.role:
            summary_parts.append(f"role={event.role}")
    
    # Event-specific details
    if event.event_type == "VoteCast":
        summary_parts.append(f"voter={getattr(event, 'voter_id', 'unknown')}")
        summary_parts.append(f"decision={getattr(event, 'decision', 'unknown')}")
        if hasattr(event, 'reason') and event.reason:
            summary_parts.append(f'reason="{event.reason[:30]}..."' if len(event.reason) > 30 else f'reason="{event.reason}"')
            
    elif event.event_type == "NodeResult":
        success = getattr(event, 'success', True)
        summary_parts.append(f"success={success}")
        if hasattr(event, 'duration_ms') and event.duration_ms:
            summary_parts.append(f"duration={event.duration_ms}ms")
        if not success and hasattr(event, 'error') and event.error:
            summary_parts.append(f'error="{event.error[:50]}..."' if len(event.error) > 50 else f'error="{event.error}"')
            
    elif event.event_type == "ConflictRaised":
        summary_parts.append(f"votes={getattr(event, 'votes_cast', 0)}")
        summary_parts.append(f"approvals={getattr(event, 'approvals', 0)}")
        summary_parts.append(f"rejections={getattr(event, 'rejections', 0)}")
        
    elif event.event_type == "DecisionFinalized":
        approved = getattr(event, 'approved', False)
        summary_parts.append(f"approved={approved}")
        summary_parts.append(f"strategy={getattr(event, 'consensus_strategy', 'unknown')}")
        
    elif event.event_type == "RetryScheduled":
        summary_parts.append(f"attempt={getattr(event, 'attempt_number', 0)}")
        summary_parts.append(f"backoff={getattr(event, 'backoff_ms', 0)}ms")
        
    elif event.event_type == "RunSummary":
        summary_parts.append(f"status={getattr(event, 'status', 'unknown')}")
        summary_parts.append(f"events={getattr(event, 'total_events', 0)}")
        summary_parts.append(f"nodes={getattr(event, 'total_nodes', 0)}")
    
    return " ".join(summary_parts)


def _print_timeline_table(events: list[EventBase]):
    """Print events in a timeline table format."""
    table = Table(title="Event Timeline")
    table.add_column("Time", style="dim")
    table.add_column("Event", style="bold")
    table.add_column("Node", style="cyan")
    table.add_column("Details", style="white")
    
    for event in events:
        timestamp = event.timestamp.strftime("%H:%M:%S.%f")[:-3]
        node_id = getattr(event, 'node_id', '')
        if node_id:
            node_id = node_id[:12] + "..." if len(node_id) > 12 else node_id
        details = _event_summary(event)
        
        table.add_row(timestamp, event.event_type, node_id, details)
    
    console.print(table)


if __name__ == "__main__":
    app()