"""CLI commands for Memory-Bank module."""

import click
import json
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from ..config import get_global_config, save_global_config, check_config, MemoryBankProject, MemoryBankConfig
from .models import ProjectBinding
from .structure import create_release_based_structure, create_memory_bank_claude_md, create_pm_claude_md, create_pm_slash_commands

console = Console()


@click.group()
def memory_bank():
    """Memory-Bank management for structured development workflows."""
    pass


@memory_bank.command()
def spawn_structure():
    """Create/recreate Memory-Bank directory structure."""
    
    if not check_config():
        console.print(Panel.fit(
            "Global configuration required first.\nRun: claude-helpers setup",
            style="red"
        ))
        return
    
    # Check if memory-bank already exists
    current_dir = Path.cwd()
    
    # Check for existing structure
    if any((current_dir / folder).exists() for folder in ["product", "architecture", "implementation", "progress"]):
        console.print(Panel.fit(
            "Memory-Bank structure already exists in current directory",
            style="yellow"
        ))
        if not Confirm.ask("Do you want to recreate it?"):
            return
    
    # Interactive dialog for project setup
    console.print("\n[bold cyan]Memory-Bank Initialization[/bold cyan]")
    
    # Get project name
    project_name = Prompt.ask(
        "Enter project name (no spaces, English letters)",
        default=current_dir.name.replace(" ", "-").lower()
    )
    
    # Validate project name
    if " " in project_name or not project_name.replace("-", "").replace("_", "").isalnum():
        console.print("[red]Invalid project name. Use only letters, numbers, hyphens and underscores.[/red]")
        return
    
    # Create new release-based structure
    try:
        create_release_based_structure(current_dir, project_name)
        console.print(f"[green]✅ Created Memory-Bank structure in {current_dir}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to create structure: {e}[/red]")
        return
    
    
    # Save to global config
    config = get_global_config()
    
    # Initialize memory_bank config if not exists
    if not hasattr(config, 'memory_bank'):
        config.memory_bank = MemoryBankConfig()
    
    # Add project to config
    config.memory_bank.projects[project_name] = MemoryBankProject(
        name=project_name,
        path=current_dir,
        created_at=datetime.now()
    )
    
    save_global_config(config)
    console.print(f"[green]✅ Registered Memory-Bank '{project_name}' in global config[/green]")
    
    console.print(Panel.fit(
        f"Memory-Bank structure created successfully!\n\n"
        f"Next steps:\n"
        f"1. Run: claude-helpers memory-bank spawn-templates\n"
        f"2. Run: claude-helpers memory-bank spawn-prompts\n"
        f"3. Navigate to dev project and run: claude-helpers memory-bank init",
        style="green"
    ))


@memory_bank.command()
def spawn_templates():
    """Create/reset standard Memory-Bank templates."""
    
    current_dir = Path.cwd()
    
    # Check if we're in a Memory-Bank directory
    if not any((current_dir / folder).exists() for folder in ["product", "architecture", "implementation", "progress"]):
        console.print(Panel.fit(
            "Not in a Memory-Bank directory.\nRun: claude-helpers memory-bank spawn-structure first",
            style="red"
        ))
        return
    
    templates_dir = current_dir / "templates"
    
    if templates_dir.exists():
        console.print(f"[yellow]Templates directory already exists: {templates_dir}[/yellow]")
        if not Confirm.ask("Recreate/update templates?"):
            return
    
    console.print("\n[bold cyan]Creating Memory-Bank Templates[/bold cyan]")
    
    try:
        from .template_files import create_standard_templates
        create_standard_templates(templates_dir)
        console.print(f"[green]✅ Created standard templates in {templates_dir}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to create templates: {e}[/red]")
        return
    
    console.print(Panel.fit(
        "Templates created successfully!\n\n"
        "Templates include:\n"
        "• PM workflow prompts\n"
        "• Sub-agent definitions\n" 
        "• Slash command templates\n"
        "• Document templates",
        style="green"
    ))


@memory_bank.command()
def spawn_prompts():
    """Create/reset PM workflow prompts and sub-agents."""
    
    current_dir = Path.cwd()
    
    # Check if we're in a Memory-Bank directory with templates
    templates_dir = current_dir / "templates"
    if not templates_dir.exists():
        console.print(Panel.fit(
            "Templates not found.\nRun: claude-helpers memory-bank spawn-templates first",
            style="red"
        ))
        return
    
    console.print("\n[bold cyan]Creating PM Workflow Components[/bold cyan]")
    
    # Get project name from existing structure or ask
    project_name = None
    vision_file = current_dir / "product" / "vision.md"
    if vision_file.exists():
        import re
        content = vision_file.read_text()
        match = re.search(r'Project:\s*(.+)', content)
        if match:
            project_name = match.group(1).strip()
    
    if not project_name:
        project_name = Prompt.ask(
            "Enter project name for PM workflow",
            default=current_dir.name.replace(" ", "-").lower()
        )
    
    try:
        # Create PM workflow files
        from .workflow import create_pm_workflow, create_sub_agents
        
        # Create PM workflow CLAUDE.md template
        create_pm_workflow(current_dir, project_name)
        console.print("[green]✅ Created PM workflow CLAUDE.md template[/green]")
        
        # Create sub-agent definitions
        create_sub_agents(templates_dir, project_name)
        console.print("[green]✅ Created sub-agent definitions[/green]")
        
    except Exception as e:
        console.print(f"[red]Failed to create PM workflow: {e}[/red]")
        return
    
    console.print(Panel.fit(
        "PM workflow components created!\n\n"
        "Created:\n"
        "• PM workflow CLAUDE.md template\n"
        "• Sub-agent definitions (dev, qa, owner)\n"
        "• Slash command templates\n\n"
        "Next: Run memory-bank init in your development project",
        style="green"
    ))


@memory_bank.command()
def setup_mcp():
    """Setup MCP server configuration for current project."""
    
    if not check_config():
        console.print(Panel.fit(
            "Global configuration required first.\nRun: claude-helpers setup",
            style="red"
        ))
        return
    
    current_dir = Path.cwd()
    project_name = Prompt.ask(
        "Enter project name for MCP server",
        default=current_dir.name.replace(" ", "-").lower()
    )
    
    # Validate project name
    if " " in project_name or not project_name.replace("-", "").replace("_", "").isalnum():
        console.print("[red]Invalid project name. Use only letters, numbers, hyphens and underscores.[/red]")
        return
    
    console.print(f"\n[bold cyan]Setting up MCP server for '{project_name}'[/bold cyan]")
    
    server_name = f"memory-bank-{project_name}"
    
    # Load current config
    config = get_global_config()
    if not hasattr(config, 'memory_bank'):
        config.memory_bank = MemoryBankConfig()
    
    # Check if MCP server already exists
    import subprocess
    server_exists = False
    try:
        result = subprocess.run(['claude', 'mcp', 'list'], capture_output=True, text=True)
        server_exists = server_name in result.stdout
    except Exception:
        pass
    
    if server_exists:
        console.print(f"[yellow]MCP server '{server_name}' already exists[/yellow]")
        if not Confirm.ask("Update MCP server configuration?"):
            return
        
        # Remove existing server
        try:
            subprocess.run(['claude', 'mcp', 'remove', server_name], check=True)
            console.print(f"[green]Removed existing server '{server_name}'[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to remove existing server: {e}[/red]")
            return
    
    # Add MCP server in Project scope for better sub-agent inheritance
    mcp_config_obj = {
        "type": "stdio",
        "command": "claude-helpers", 
        "args": ["memory-bank-mcp"]
    }
    
    success = False
    try:
        # Create .mcp.json in current directory for project-scoped MCP
        mcp_config = {
            "servers": {
                server_name: mcp_config_obj
            }
        }
        
        mcp_file = current_dir / ".mcp.json"
        with open(mcp_file, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        console.print(f"[green]✅ Created project-scoped MCP server in .mcp.json[/green]")
        console.print("[yellow]Note: Commit .mcp.json to version control for team sharing[/yellow]")
        success = True
        
    except Exception as e:
        console.print(f"[red]Failed to create .mcp.json: {e}[/red]")
        # Fallback to user scope
        try:
            subprocess.run([
                'claude', 'mcp', 'add-json', 
                server_name,
                json.dumps(mcp_config_obj)
            ], check=True)
            
            console.print(f"[green]✅ Added user-scoped MCP server '{server_name}'[/green]")
            success = True
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to setup MCP server: {e}[/red]")
            console.print("[yellow]Manual setup:[/yellow]")
            console.print(f"claude mcp add-json {server_name} '{json.dumps(mcp_config_obj)}'")
            return
    
    # Save MCP server to config
    if success:
        config.memory_bank.mcp_servers[server_name] = project_name
        save_global_config(config)
        console.print(f"[green]✅ Registered MCP server '{server_name}' in global config[/green]")
    
    console.print(Panel.fit(
        f"MCP server configured successfully!\n\n"
        f"Server name: {server_name}\n"
        f"Project: {project_name}\n"
        f"Command: claude-helpers memory-bank-mcp\n\n"
        f"The server provides PM workflow tools:\n"
        f"• get-pm-focus\n"
        f"• get-progress\n"
        f"• turn-role\n"
        f"• note-journal",
        style="green"
    ))


@memory_bank.command()
def init():
    """Bind current project to Memory-Bank with release-based structure."""
    
    if not check_config():
        console.print(Panel.fit(
            "Global configuration required first.\nRun: claude-helpers setup",
            style="red"
        ))
        return
    
    config = get_global_config()
    
    # Check if memory_bank config exists
    if not hasattr(config, 'memory_bank') or not config.memory_bank.projects:
        console.print(Panel.fit(
            "No Memory-Banks found.\nRun: claude-helpers memory-bank spawn",
            style="yellow"
        ))
        return
    
    # Check if .helpers exists
    helpers_dir = Path.cwd() / ".helpers"
    if not helpers_dir.exists():
        console.print(Panel.fit(
            "Project not initialized.\nRun: claude-helpers init",
            style="yellow"
        ))
        return
    
    # Interactive binding
    console.print("\n[bold cyan]Memory-Bank Binding[/bold cyan]")
    
    if not Confirm.ask("Bind/rebind Memory-Bank to this project?"):
        console.print("Cancelled")
        return
    
    # List available Memory-Banks
    console.print("\n[bold]Available Memory-Banks:[/bold]")
    projects = list(config.memory_bank.projects.keys())
    
    for i, name in enumerate(projects, 1):
        project = config.memory_bank.projects[name]
        console.print(f"{i}. {name} - {project.path}")
    
    # Choose Memory-Bank
    choice = Prompt.ask(
        "Select Memory-Bank number",
        choices=[str(i) for i in range(1, len(projects) + 1)]
    )
    
    selected_name = projects[int(choice) - 1]
    selected_project = config.memory_bank.projects[selected_name]
    
    # Validate Memory-Bank path exists with new structure
    memory_bank_path = Path(selected_project.path)
    required_dirs = ["product", "architecture", "implementation", "progress"]
    
    if not all((memory_bank_path / d).exists() for d in required_dirs):
        console.print(f"[red]Memory-Bank at {memory_bank_path} has invalid release-based structure[/red]")
        console.print(f"Required directories: {', '.join(required_dirs)}")
        return
    
    # Save binding to .helpers
    binding_file = helpers_dir / "memory_bank.json"
    binding = ProjectBinding(
        memory_bank_name=selected_name,
        memory_bank_path=selected_project.path,
        bound_at=datetime.now()
    )
    
    with open(binding_file, 'w') as f:
        json.dump(binding.model_dump(mode='json'), f, indent=2, default=str)
    
    console.print(f"[green]✅ Bound to Memory-Bank '{selected_name}'[/green]")
    
    # MCP server setup - check if Claude MCP server actually exists
    expected_server_name = f"memory-bank-{selected_name}"
    
    # Check if MCP server exists in Claude (not just our config tracking)
    import subprocess
    claude_server_exists = False
    try:
        result = subprocess.run(['claude', 'mcp', 'list'], capture_output=True, text=True)
        claude_server_exists = expected_server_name in result.stdout
    except Exception:
        pass
    
    if claude_server_exists:
        console.print(f"[green]✅ MCP server '{expected_server_name}' already exists in Claude[/green]")
        
        # Update our tracking if needed
        if expected_server_name not in config.memory_bank.mcp_servers:
            config.memory_bank.mcp_servers[expected_server_name] = selected_name
            save_global_config(config)
            console.print(f"[green]✅ Updated MCP server tracking in global config[/green]")
    else:
        console.print(f"[yellow]⚠️  No MCP server found for project '{selected_name}'[/yellow]")
        if Confirm.ask(f"Create MCP server '{expected_server_name}' in Claude?"):
            mcp_config_obj = {
                "type": "stdio",
                "command": "claude-helpers", 
                "args": ["memory-bank-mcp"]
            }
            
            try:
                subprocess.run([
                    'claude', 'mcp', 'add-json', 
                    expected_server_name,
                    json.dumps(mcp_config_obj)
                ], check=True)
                
                # Save to config
                config.memory_bank.mcp_servers[expected_server_name] = selected_name
                save_global_config(config)
                
                console.print(f"[green]✅ Created MCP server '{expected_server_name}' in Claude[/green]")
            except subprocess.CalledProcessError as e:
                console.print(f"[red]Failed to create MCP server: {e}[/red]")
                console.print(f"[yellow]Manual setup: claude mcp add-json {expected_server_name} '{json.dumps(mcp_config_obj)}'[/yellow]")
                console.print(f"[yellow]Or run: claude-helpers memory-bank setup-mcp[/yellow]")
    
    # PM Workflow Setup from Memory-Bank templates
    console.print("\n[bold cyan]PM Workflow Configuration[/bold cyan]")
    
    # Check if Memory-Bank has templates
    templates_dir = memory_bank_path / "templates"
    if not templates_dir.exists():
        console.print(f"[yellow]No templates found in Memory-Bank.\nRun: claude-helpers memory-bank spawn-templates in {memory_bank_path}[/yellow]")
        console.print("Skipping PM workflow setup")
    else:
        # Check if CLAUDE.md exists
        claude_md_path = Path.cwd() / "CLAUDE.md"
        if claude_md_path.exists():
            console.print(f"[yellow]⚠️  CLAUDE.md already exists[/yellow]")
            if not Confirm.ask("Overwrite existing CLAUDE.md with PM workflow?"):
                console.print("Skipping CLAUDE.md creation")
            else:
                # Copy from Memory-Bank templates
                from .workflow import copy_templates_to_project
                copy_templates_to_project(memory_bank_path, Path.cwd(), selected_name)
                console.print("[green]✅ Created PM workflow CLAUDE.md from Memory-Bank templates[/green]")
        else:
            # Ask about creating PM CLAUDE.md
            if Confirm.ask("Create PM workflow from Memory-Bank templates?"):
                from .workflow import copy_templates_to_project
                copy_templates_to_project(memory_bank_path, Path.cwd(), selected_name)
                console.print("[green]✅ Created PM workflow from Memory-Bank templates[/green]")
        
        # Ask about /run command setup
        if Confirm.ask("Setup /run command and sub-agents?"):
            # This is already handled by copy_templates_to_project
            console.print("[green]✅ Created /run command and sub-agents from templates[/green]")
    
    console.print(Panel.fit(
        f"Memory-Bank binding complete!\n\n"
        f"Structure: {memory_bank_path}\n"
        f"MCP tools: get-pm-focus, get-progress, turn-role, note-journal\n"
        f"Usage: Use /run command or PM slash commands in Claude Code\n"
        f"Start with: /run \"release-name\" \"component-name\"",
        style="green"
    ))


@memory_bank.command()
def remove_mcp():
    """Remove MCP server configuration."""
    
    if not check_config():
        console.print(Panel.fit(
            "Global configuration required first.\nRun: claude-helpers setup",
            style="red"
        ))
        return
    
    config = get_global_config()
    if not hasattr(config, 'memory_bank') or not config.memory_bank.mcp_servers:
        console.print("[yellow]No MCP servers configured[/yellow]")
        return
    
    console.print("\n[bold cyan]Remove MCP Server[/bold cyan]")
    
    # List configured MCP servers
    servers = list(config.memory_bank.mcp_servers.keys())
    console.print("\n[bold]Configured MCP servers:[/bold]")
    for i, server_name in enumerate(servers, 1):
        project_name = config.memory_bank.mcp_servers[server_name]
        console.print(f"{i}. {server_name} -> {project_name}")
    
    # Choose server to remove
    choice = Prompt.ask(
        "Select server number to remove",
        choices=[str(i) for i in range(1, len(servers) + 1)]
    )
    
    server_to_remove = servers[int(choice) - 1]
    project_name = config.memory_bank.mcp_servers[server_to_remove]
    
    if not Confirm.ask(f"Remove MCP server '{server_to_remove}' for project '{project_name}'?"):
        console.print("Cancelled")
        return
    
    # Remove from Claude MCP
    import subprocess
    try:
        subprocess.run(['claude', 'mcp', 'remove', server_to_remove], check=True)
        console.print(f"[green]✅ Removed MCP server '{server_to_remove}' from Claude[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to remove from Claude: {e}[/red]")
        console.print("[yellow]You may need to remove manually[/yellow]")
    
    # Remove from config
    del config.memory_bank.mcp_servers[server_to_remove]
    save_global_config(config)
    console.print(f"[green]✅ Removed '{server_to_remove}' from global config[/green]")
    
    console.print(Panel.fit(
        f"MCP server '{server_to_remove}' removed successfully!\n\n"
        f"Project '{project_name}' is no longer configured for MCP access.\n"
        f"You can recreate it with: claude-helpers memory-bank setup-mcp",
        style="green"
    ))


@memory_bank.command()
def list_mcp():
    """List configured MCP servers."""
    
    if not check_config():
        console.print(Panel.fit(
            "Global configuration required first.\nRun: claude-helpers setup",
            style="red"
        ))
        return
    
    config = get_global_config()
    if not hasattr(config, 'memory_bank') or not config.memory_bank.mcp_servers:
        console.print("[yellow]No MCP servers configured[/yellow]")
        console.print("Run: claude-helpers memory-bank setup-mcp")
        return
    
    console.print("\n[bold cyan]Configured MCP Servers[/bold cyan]\n")
    
    import subprocess
    # Get actual Claude MCP status
    claude_servers = set()
    try:
        result = subprocess.run(['claude', 'mcp', 'list'], capture_output=True, text=True)
        claude_servers = set(line.split(':')[0].strip() for line in result.stdout.split('\n') if ':' in line)
    except Exception:
        pass
    
    for server_name, project_name in config.memory_bank.mcp_servers.items():
        status = "✓ Active" if server_name in claude_servers else "✗ Missing"
        status_color = "green" if server_name in claude_servers else "red"
        
        console.print(f"[bold]{server_name}[/bold] -> {project_name}")
        console.print(f"  Status: [{status_color}]{status}[/{status_color}]")
        console.print()
    
    if any(server not in claude_servers for server in config.memory_bank.mcp_servers.keys()):
        console.print("[yellow]Some servers are missing from Claude configuration.[/yellow]")
        console.print("Run: claude-helpers memory-bank setup-mcp to recreate missing servers")


@memory_bank.command()
def agent_mcp():
    """Run MCP server for Memory-Bank agent operations."""
    
    if not check_config():
        console.print("[red]Global configuration required[/red]")
        sys.exit(1)
    
    # Check if Memory-Bank is bound to current project
    helpers_dir = Path.cwd() / ".helpers"
    binding_file = helpers_dir / "memory_bank.json"
    
    if not binding_file.exists():
        console.print("[red]Memory-Bank not bound to current project. Run: claude-helpers memory-bank init[/red]")
        sys.exit(1)
    
    # Import and run MCP server
    from .server import run_mcp_server
    run_mcp_server()


@memory_bank.command()
@click.argument('project_name')
@click.argument('operation', type=click.Choice(['rebuild-progress', 'rebuild-focus', 'validate-structure']))
@click.option('--release', help='Release name for rebuild-focus operation')
@click.option('--component', help='Component name for rebuild-focus operation')
@click.option('--path', help='Path for validate-structure operation')
def helper(project_name: str, operation: str, release: str = None, component: str = None, path: str = None):
    """Memory-Bank helper using Claude Code SDK."""
    
    if not check_config():
        console.print("[red]Global configuration required[/red]")
        return
    
    config = get_global_config()
    
    # Find Memory-Bank
    if not hasattr(config, 'memory_bank') or project_name not in config.memory_bank.projects:
        console.print(f"[red]Memory-Bank '{project_name}' not found[/red]")
        return
    
    project = config.memory_bank.projects[project_name]
    
    # Validate Memory-Bank path with new structure
    memory_bank_path = Path(project.path)
    required_dirs = ["product", "architecture", "implementation", "progress"]
    
    if not all((memory_bank_path / d).exists() for d in required_dirs):
        console.print(f"[red]Memory-Bank at {memory_bank_path} has invalid release-based structure[/red]")
        return
    
    # TODO: Implement operations using Task tool for Claude Code SDK
    console.print(f"[yellow]Operation '{operation}' not yet implemented with new SDK[/yellow]")
    console.print("Available operations will be implemented using Claude Code Task tool")
    return