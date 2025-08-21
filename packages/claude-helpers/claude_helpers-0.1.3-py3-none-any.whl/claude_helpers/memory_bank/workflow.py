"""Memory-Bank PM workflow management."""

from pathlib import Path
from datetime import datetime
from typing import Dict


def create_pm_workflow(memory_bank_dir: Path, project_name: str) -> None:
    """Create PM workflow CLAUDE.md template in Memory-Bank."""
    
    from .templates import PM_CLAUDE_MD_TEMPLATE
    
    templates_dir = memory_bank_dir / "templates" / "pm-workflow"
    claude_md_template = templates_dir / "claude-md-template.md"
    
    if claude_md_template.exists():
        content = claude_md_template.read_text()
        
        # Replace template variables
        content = content.format(
            project_name=project_name,
            timestamp=datetime.now().isoformat() + "Z",
            memory_bank_path=str(memory_bank_dir)
        )
        
        # Save to Memory-Bank root as template
        pm_claude_md = memory_bank_dir / "templates" / "CLAUDE.md.template"
        with open(pm_claude_md, 'w') as f:
            f.write(content)


def create_sub_agents(templates_dir: Path, project_name: str) -> None:
    """Create sub-agent definitions in Memory-Bank templates."""
    
    sub_agents_dir = templates_dir / "sub-agents"
    
    # Sub-agent configurations
    sub_agents = {
        "pm-coordinator.md": {
            "name": "pm-coordinator",
            "description": f"Project Manager for {project_name} Memory-Bank coordination",
            "tools": ["get-pm-focus", "get-progress", "turn-role", "note-journal", "ask-memory-bank"]
        },
        "dev-specialist.md": {
            "name": "dev-specialist", 
            "description": f"Development specialist for {project_name} component implementation",
            "tools": ["get-focus", "get-progress", "note-journal", "ask-memory-bank"]
        },
        "qa-specialist.md": {
            "name": "qa-specialist",
            "description": f"Quality Assurance specialist for {project_name} component validation", 
            "tools": ["get-focus", "get-progress", "note-journal", "ask-memory-bank"]
        },
        "business-owner.md": {
            "name": "business-owner",
            "description": f"Business Owner for {project_name} requirements and priorities",
            "tools": ["get-focus", "get-progress", "note-journal", "ask-memory-bank"]
        }
    }
    
    # Create each sub-agent file
    for filename, config in sub_agents.items():
        agent_file = sub_agents_dir / filename
        if agent_file.exists():
            # Update project name in existing template
            content = agent_file.read_text()
            content = content.replace("{project_name}", project_name)
            content = content.replace("{memory_bank_path}", str(templates_dir.parent))
            
            with open(agent_file, 'w') as f:
                f.write(content)


def copy_templates_to_project(memory_bank_path: Path, project_dir: Path, project_name: str) -> None:
    """Copy Memory-Bank templates to development project."""
    
    templates_dir = memory_bank_path / "templates"
    
    # Copy PM workflow CLAUDE.md
    claude_template = templates_dir / "pm-workflow" / "claude-md-template.md"
    if claude_template.exists():
        content = claude_template.read_text()
        
        # Replace project-specific variables
        content = content.replace("{project_name}", project_name)
        content = content.replace("{memory_bank_path}", str(memory_bank_path))
        
        claude_md = project_dir / "CLAUDE.md"
        with open(claude_md, 'w') as f:
            f.write(content)
    
    # Copy slash commands
    commands_dir = project_dir / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    slash_commands_dir = templates_dir / "pm-workflow" / "slash-commands"
    if slash_commands_dir.exists():
        import shutil
        
        for command_file in slash_commands_dir.glob("*.md"):
            content = command_file.read_text()
            content = content.replace("{project_name}", project_name)
            
            dest_file = commands_dir / command_file.name
            with open(dest_file, 'w') as f:
                f.write(content)
    
    # Copy /run command
    run_template = templates_dir / "pm-workflow" / "run-command-template.md"
    if run_template.exists():
        content = run_template.read_text()
        content = content.replace("{project_name}", project_name)
        content = content.replace("{memory_bank_path}", str(memory_bank_path))
        
        run_command = commands_dir / "run.md"
        with open(run_command, 'w') as f:
            f.write(content)
    
    # Copy sub-agents to project
    sub_agents_dir = project_dir / ".claude" / "agents"
    sub_agents_dir.mkdir(parents=True, exist_ok=True)
    
    source_agents_dir = templates_dir / "sub-agents"
    if source_agents_dir.exists():
        for agent_file in source_agents_dir.glob("*.md"):
            content = agent_file.read_text()
            content = content.replace("{project_name}", project_name)
            content = content.replace("{memory_bank_path}", str(memory_bank_path))
            
            dest_file = sub_agents_dir / agent_file.name
            with open(dest_file, 'w') as f:
                f.write(content)


def update_mcp_prompts(memory_bank_path: Path) -> None:
    """Update MCP prompts in Memory-Bank to use templates."""
    
    # Update server.py to use template files instead of hardcoded prompts
    prompts_dir = memory_bank_path / "templates" / "mcp-prompts"
    
    # This would be called during spawn-prompts to ensure MCP uses template files
    # The actual server.py modification would read from these template files
    pass