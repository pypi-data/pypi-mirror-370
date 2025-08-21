"""Project skeleton generator."""

import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

BUILT_IN_TEMPLATES = {
    "python-basic": "Basic Python project with uv, tests, and Clean Architecture structure"
}


def get_available_templates() -> dict[str, str]:
    """Get all available templates: built-in + Memory-Bank templates."""
    
    templates = BUILT_IN_TEMPLATES.copy()
    
    # Method 1: Check for Memory-Bank binding via .helpers (preferred)
    from ..memory_bank import get_memory_bank_binding
    
    binding = get_memory_bank_binding()
    if binding:
        memory_bank_root = binding['memory_bank_path']
        memory_bank_skeletons = memory_bank_root / "templates" / "skeletons"
        
        if memory_bank_skeletons.exists() and memory_bank_skeletons.is_dir():
            # Scan for Memory-Bank skeleton templates
            for template_dir in memory_bank_skeletons.iterdir():
                if template_dir.is_dir() and not template_dir.name.startswith('.'):
                    template_name = template_dir.name
                    
                    # Read description from README.md or use default
                    description = _get_template_description(template_dir)
                    
                    # Add to available templates (Memory-Bank templates can override built-in)
                    templates[template_name] = f"{description} (Memory-Bank: {binding['memory_bank_name']})"
    
    # Method 2: Fallback - search up directory tree (legacy behavior)
    else:
        memory_bank_root = _find_memory_bank_root()
        
        if memory_bank_root:
            memory_bank_skeletons = memory_bank_root / "templates" / "skeletons"
            
            if memory_bank_skeletons.exists() and memory_bank_skeletons.is_dir():
                # Scan for Memory-Bank skeleton templates
                for template_dir in memory_bank_skeletons.iterdir():
                    if template_dir.is_dir() and not template_dir.name.startswith('.'):
                        template_name = template_dir.name
                        
                        # Read description from README.md or use default
                        description = _get_template_description(template_dir)
                        
                        # Add to available templates (Memory-Bank templates can override built-in)
                        templates[template_name] = f"{description} (Memory-Bank: found)"
    
    return templates


def _find_memory_bank_root() -> Path | None:
    """Find Memory-Bank root directory by searching up the directory tree."""
    
    current = Path.cwd().resolve()
    
    # Search up to root directory
    while current != current.parent:
        # Check if this directory contains Memory-Bank structure
        if _is_memory_bank_directory(current):
            return current
        current = current.parent
    
    # Check root directory
    if _is_memory_bank_directory(current):
        return current
    
    return None


def _is_memory_bank_directory(path: Path) -> bool:
    """Check if directory contains Memory-Bank structure."""
    
    # Memory-Bank directories should have these key folders
    memory_bank_indicators = ["product", "architecture", "implementation", "progress"]
    
    return any((path / indicator).exists() for indicator in memory_bank_indicators)


def _get_template_description(template_dir: Path) -> str:
    """Extract template description from README.md or use default."""
    
    readme_file = template_dir / "README.md"
    if readme_file.exists():
        try:
            content = readme_file.read_text(encoding='utf-8')
            # Look for first line starting with description patterns
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Use first non-header line as description
                    return line[:80] + ('...' if len(line) > 80 else '')
            
            # If no suitable line, use template name
            return f"Custom {template_dir.name} template"
        except:
            pass
    
    return f"Custom {template_dir.name} template"


def create_skeleton(template_name: str, project_name: str = None, here: bool = False):
    """Create project skeleton from template."""
    
    # Get all available templates
    available_templates = get_available_templates()
    
    # Validate template
    if template_name not in available_templates:
        console.print(f"[red]Template '{template_name}' not found.[/red]")
        console.print("[cyan]Available templates:[/cyan]")
        for name, desc in available_templates.items():
            console.print(f"  • [bold]{name}[/bold]: {desc}")
        return
    
    # Handle --here flag
    if here:
        target_dir = Path.cwd()
        project_name = target_dir.name.lower().replace(" ", "-")
        
        # Validate derived project name
        if not _validate_project_name(project_name):
            console.print(f"[red]Current directory name '{target_dir.name}' is not a valid project name.[/red]")
            console.print("[red]Directory name should use lowercase letters, numbers, hyphens only.[/red]")
            return
        
        # Check if current directory is empty
        if any(target_dir.iterdir()):
            console.print("[yellow]Current directory is not empty.[/yellow]")
            if not Confirm.ask("Create skeleton files here anyway?"):
                return
    else:
        # Get project name for new directory
        if not project_name:
            project_name = Prompt.ask(
                "Enter project name (lowercase, hyphens allowed)",
                default=Path.cwd().name.lower().replace(" ", "-")
            )
        
        # Validate project name
        if not _validate_project_name(project_name):
            console.print("[red]Invalid project name. Use lowercase letters, numbers, hyphens only.[/red]")
            return
        
        # Check target directory
        target_dir = Path.cwd() / project_name
        
        if target_dir.exists():
            if any(target_dir.iterdir()):
                console.print(f"[yellow]Directory '{target_dir}' exists and is not empty.[/yellow]")
                if not Confirm.ask("Continue anyway?"):
                    return
    
    # Create skeleton
    console.print(f"\n[bold cyan]Creating {template_name} skeleton: {project_name}[/bold cyan]")
    
    try:
        _create_from_template(template_name, target_dir, project_name)
        next_steps = []
        if here:
            next_steps = [
                "1. uv sync",
                "2. uv run pytest"
            ]
        else:
            next_steps = [
                f"1. cd {project_name}",
                "2. uv sync", 
                "3. uv run pytest"
            ]
        
        console.print(Panel.fit(
            f"✅ Project skeleton created successfully!\n\n"
            f"Location: {target_dir}\n"
            f"Template: {available_templates[template_name]}\n\n"
            f"Next steps:\n" + "\n".join(next_steps),
            style="green"
        ))
    except Exception as e:
        console.print(f"[red]Failed to create skeleton: {e}[/red]")


def _validate_project_name(name: str) -> bool:
    """Validate project name follows Python package naming conventions."""
    import re
    return bool(re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', name)) or len(name) == 1


def _create_from_template(template_name: str, target_dir: Path, project_name: str):
    """Create project from template."""
    
    # Find template directory - check Memory-Bank first, then built-in
    template_dir = None
    
    # Method 1: Check Memory-Bank binding first (preferred)
    from ..memory_bank import get_memory_bank_binding
    
    binding = get_memory_bank_binding()
    if binding:
        memory_bank_template = binding['memory_bank_path'] / "templates" / "skeletons" / template_name
        if memory_bank_template.exists() and memory_bank_template.is_dir():
            template_dir = memory_bank_template
    
    # Method 2: Check legacy Memory-Bank search if binding not found
    if not template_dir:
        memory_bank_root = _find_memory_bank_root()
        if memory_bank_root:
            memory_bank_template = memory_bank_root / "templates" / "skeletons" / template_name
            if memory_bank_template.exists() and memory_bank_template.is_dir():
                template_dir = memory_bank_template
    
    # Method 3: Check built-in templates if not found in Memory-Bank
    if not template_dir:
        built_in_template = Path(__file__).parent / "templates" / template_name
        if built_in_template.exists() and built_in_template.is_dir():
            template_dir = built_in_template
    
    if not template_dir:
        raise FileNotFoundError(f"Template directory not found: {template_name}")
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy template files
    for item in template_dir.rglob("*"):
        if item.is_file():
            # Calculate relative path and replace placeholders in path
            rel_path = item.relative_to(template_dir)
            rel_path_str = str(rel_path)
            rel_path_str = _replace_placeholders(rel_path_str, project_name)
            target_file = target_dir / rel_path_str
            
            # Create parent directories
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Read template content
            content = item.read_text(encoding='utf-8')
            
            # Replace placeholders in content
            content = _replace_placeholders(content, project_name)
            
            # Write to target
            target_file.write_text(content, encoding='utf-8')


def _replace_placeholders(content: str, project_name: str) -> str:
    """Replace template placeholders with actual values."""
    
    # Generate Python package name (replace hyphens with underscores)
    package_name = project_name.replace("-", "_")
    
    replacements = {
        "{{PROJECT_NAME}}": project_name,
        "{{PACKAGE_NAME}}": package_name,
        "{{PROJECT_TITLE}}": project_name.replace("-", " ").title(),
        "{{PACKAGE_NAME|upper}}": package_name.upper(),
    }
    
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    
    return content