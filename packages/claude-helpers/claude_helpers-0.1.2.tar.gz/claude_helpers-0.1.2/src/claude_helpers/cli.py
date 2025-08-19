"""CLI interface for Claude Helpers."""

import click
from rich.console import Console
from rich.panel import Panel

from .config import check_config

console = Console()


@click.group()
@click.version_option()
def cli():
    """Claude Helpers - Voice and HIL tools for Claude Code."""
    pass


@cli.command()
def setup():
    """Configure global settings (API keys, audio devices, providers)."""
    from .config import setup_global_config
    setup_global_config()


@cli.command()
@click.option('--update', is_flag=True, help='Update existing project configuration')
def init(update):
    """Initialize current project for Claude Code integration."""
    from .config import setup_project_interactive
    
    if not check_config():
        console.print(Panel.fit(
            "Global configuration required first.\nRun: claude-helpers setup",
            style="red"
        ))
        return
    
    setup_project_interactive(update_mode=update)


@cli.command()
def voice():
    """Record voice and output transcription."""
    if not check_config():
        console.print(Panel.fit(
            "Global configuration not found.\nPlease run: claude-helpers init",
            style="red"
        ))
        return
    
    from .voice import voice_command
    voice_command()


@cli.command("ask", hidden=True)
@click.option('--voice', is_flag=True, help='Request voice input instead of text')
@click.option('--duration', type=int, default=30, help='Max recording duration in seconds')
@click.option('--timeout', type=int, default=300, help='Max wait time for response')
@click.argument('question', nargs=-1, required=True)
def _internal_ask(voice, duration, timeout, question):
    """Internal ask command for MCP server use only."""
    from .hil.core import ask_human_hil, voice_input_hil
    
    question_text = " ".join(question)
    
    try:
        if voice:
            result = voice_input_hil(question_text, timeout, duration)
        else:
            result = ask_human_hil(question_text, timeout)
        
        print(result)
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


@cli.group(invoke_without_command=True)
@click.option('--dir', '-d', type=click.Path(exists=True), 
              help='Project directory to watch (same as "listen start")')
@click.pass_context
def listen(ctx, dir):
    """Human-in-the-loop listener commands.
    
    When called without subcommand, starts the listener (same as "listen start").
    """
    if ctx.invoked_subcommand is None:
        # No subcommand provided, run default "start" behavior
        from pathlib import Path
        
        if not check_config():
            console.print(Panel.fit(
                "Global configuration not found.\nPlease run: claude-helpers init",
                style="red"
            ))
            return
        
        from .hil.listener import listen_command
        
        # Determine directory
        if dir:
            helpers_dir = Path(dir) / ".helpers"
        else:
            helpers_dir = Path.cwd() / ".helpers"
        
        # Check if project is initialized
        if not helpers_dir.exists():
            console.print(Panel.fit(
                "Project not initialized.\nPlease run: claude-helpers init --project-only",
                style="yellow"
            ))
            return
        
        # Start listener
        listen_command(helpers_dir)


@listen.command("start")
@click.option('--dir', '-d', type=click.Path(exists=True), 
              help='Project directory to watch')
def listen_start(dir):
    """Start human-in-the-loop listener."""
    from pathlib import Path
    
    if not check_config():
        console.print(Panel.fit(
            "Global configuration not found.\nPlease run: claude-helpers init",
            style="red"
        ))
        return
    
    from .hil.listener import listen_command
    
    # Determine directory
    if dir:
        helpers_dir = Path(dir) / ".helpers"
    else:
        helpers_dir = Path.cwd() / ".helpers"
    
    # Check if project is initialized
    if not helpers_dir.exists():
        console.print(Panel.fit(
            "Project not initialized.\nPlease run: claude-helpers init --project-only",
            style="yellow"
        ))
        return
    
    # Start listener
    listen_command(helpers_dir)


@listen.command("test")
def listen_test():
    """Test HIL system with a simulated question."""
    if not check_config():
        console.print(Panel.fit(
            "Global configuration not found.\nPlease run: claude-helpers init",
            style="red"
        ))
        return
    
    # Run test (no project directory needed - uses temp)
    from .hil.test import test_hil_system
    test_hil_system()


@cli.command()
def mcp_server():
    """Run as MCP stdio server for Claude Code integration."""
    import sys
    
    if not check_config():
        console.print("[red]Global configuration required. Run: claude-helpers setup[/red]", file=sys.stderr)
        sys.exit(1)
    
    from .mcp.server import run_mcp_server
    run_mcp_server()


@cli.command()
def memory_bank_mcp():
    """Run Memory-Bank MCP stdio server for Claude Code integration."""
    from .memory_bank.server import run_mcp_server
    run_mcp_server()


# Import memory_bank group at module level to register it
from .memory_bank.commands import memory_bank
cli.add_command(memory_bank)


@cli.command()
def status():
    """Check environment status and readiness for Claude Code integration."""
    from pathlib import Path
    from rich.table import Table
    from rich.text import Text
    import subprocess
    import shutil
    
    console.print("\n[bold]🔍 Claude Helpers Environment Status[/bold]")
    
    # Create status table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Component", style="white")
    table.add_column("Status", justify="center")
    table.add_column("Details", style="dim")
    
    # Check global configuration
    try:
        config_ok = check_config()
        if config_ok:
            table.add_row("Global Config", "✅ OK", "Configuration loaded successfully")
        else:
            table.add_row("Global Config", "❌ ERROR", "Run: claude-helpers init --global-only")
    except Exception as e:
        table.add_row("Global Config", "❌ ERROR", f"Error: {e}")
    
    # Check project setup
    helpers_dir = Path.cwd() / ".helpers"
    claude_dir = Path.cwd() / ".claude"
    
    if helpers_dir.exists():
        table.add_row("Project HIL", "✅ OK", f"HIL directory: {helpers_dir}")
    else:
        table.add_row("Project HIL", "⚠️  MISSING", "Run: claude-helpers init --project-only")
    
    # Check what features are enabled
    commands_dir = claude_dir / "commands"
    voice_command = commands_dir / "voice.md"
    hil_rules_command = commands_dir / "init-hil-rules.md"
    
    enabled_features = []
    
    if voice_command.exists():
        enabled_features.append("Voice instructions (/voice)")
        table.add_row("Voice Command", "✅ ENABLED", "/voice slash command configured")
    
    if hil_rules_command.exists():
        enabled_features.append("HIL rules (init-hil-rules)")
        table.add_row("HIL Rules", "✅ ENABLED", "init-hil-rules command available")
    
    # Check MCP integration
    try:
        import subprocess
        result = subprocess.run(["claude", "mcp", "list"], capture_output=True, text=True)
        if result.returncode == 0 and ("claude-helpers-hil" in result.stdout or "ask-human" in result.stdout):
            enabled_features.append("MCP ask-question tool")
            table.add_row("MCP Integration", "✅ ENABLED", "ask-question tool registered")
        else:
            table.add_row("MCP Integration", "⚪ DISABLED", "ask-question tool not registered")
    except Exception:
        table.add_row("MCP Integration", "❓ UNKNOWN", "Cannot check MCP status")
    
    if not enabled_features:
        table.add_row("Features", "⚪ NONE", "No features configured")
    
# .claudeignore check removed - this file doesn't exist in Claude Code API
    
    # Check CLAUDE.md (optional)
    claude_md = Path.cwd() / "CLAUDE.md"
    if claude_md.exists():
        claude_md_content = claude_md.read_text()
        start_marker = "<!-- CLAUDE HELPERS HIL START -->"
        end_marker = "<!-- CLAUDE HELPERS HIL END -->"
        
        if start_marker in claude_md_content and end_marker in claude_md_content:
            table.add_row("CLAUDE.md", "✅ HIL DOCS", "Contains HIL integration docs")
        else:
            table.add_row("CLAUDE.md", "⚪ BASIC", "File exists, no HIL docs")
    else:
        table.add_row("CLAUDE.md", "⚪ NOT SET", "No CLAUDE.md file in project")
    
    # Check if listener is running (basic check)
    try:
        result = subprocess.run(["pgrep", "-f", "claude-helpers listen"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            table.add_row("HIL Listener", "✅ RUNNING", f"PID: {result.stdout.strip()}")
        else:
            table.add_row("HIL Listener", "⚠️  NOT RUNNING", "Start: claude-helpers listen")
    except Exception:
        table.add_row("HIL Listener", "❓ UNKNOWN", "Cannot check process status")
    
    # Check dependencies
    deps = {
        "sounddevice": "Audio recording",
        "openai": "Voice transcription", 
        "watchdog": "File monitoring",
        "rich": "UI components"
    }
    
    missing_deps = []
    for dep, desc in deps.items():
        try:
            __import__(dep)
            table.add_row(f"Dependency: {dep}", "✅ OK", desc)
        except ImportError:
            table.add_row(f"Dependency: {dep}", "❌ MISSING", f"{desc} - install with uv")
            missing_deps.append(dep)
    
    console.print(table)
    
    # System status summary
    console.print(f"\n[bold]📋 System Status:[/bold]")
    
    if not config_ok:
        console.print("🔧 [yellow]Setup needed[/yellow]: Run [cyan]claude-helpers setup[/cyan] to configure global settings")
    
    if not helpers_dir.exists():
        console.print("🔧 [yellow]Setup needed[/yellow]: Run [cyan]claude-helpers init[/cyan] to initialize project")
    
    if missing_deps:
        console.print(f"🔧 [red]Dependencies missing[/red]: {', '.join(missing_deps)}")
    
    # Check overall readiness
    basic_ready = config_ok and helpers_dir.exists() and not missing_deps
    features_ready = len(enabled_features) > 0
    
    if basic_ready:
        console.print("\n✅ [green]Core system ready![/green]")
        
        if features_ready:
            console.print(f"✅ [green]Features enabled:[/green] {', '.join(enabled_features)}")
            
            # Show usage for enabled features
            console.print("\n[bold]🚀 Usage:[/bold]")
            if "Voice instructions (/voice)" in enabled_features:
                console.print("• Use [cyan]/voice[/cyan] in Claude Code when you want to give instructions via voice")
            if "MCP ask-question tool" in enabled_features:
                console.print("• Claude Code has [cyan]ask-question[/cyan] MCP tool for all HIL interactions")
                console.print("• Human can respond via text or voice (they choose in UI)")
            
            # Check if listener is needed
            listener_needed = any("Voice" in f or "MCP" in f for f in enabled_features)
            if listener_needed:
                listener_running = False
                try:
                    result = subprocess.run(["pgrep", "-f", "claude-helpers listen"], capture_output=True, text=True)
                    listener_running = result.returncode == 0
                except:
                    pass
                
                if listener_running:
                    console.print("• [green]HIL listener is running[/green] ✅")
                else:
                    console.print("• [yellow]Start HIL listener:[/yellow] [cyan]claude-helpers listen[/cyan]")
        else:
            console.print("⚪ [dim]No features configured - run[/dim] [cyan]claude-helpers init[/cyan] [dim]to add features[/dim]")
    else:
        console.print("\n🔧 [yellow]Setup required for full functionality[/yellow]")