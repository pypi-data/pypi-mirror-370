"""Memory-Bank structure management."""

from pathlib import Path
from datetime import datetime
from typing import List
import yaml


# Memory-Bank structure definition with validation criteria
MEMORY_BANK_STRUCTURE = {
    'project/product-context.md': {
        'validation': [
            'Has YAML header with datetime?',
            'Contains business intent section?',
            'Defines target audience?',
            'Lists constraints?'
        ]
    },
    'project/project-brief.md': {
        'validation': [
            'Has YAML header with datetime?',
            'Defines project goals?',
            'Sets boundaries?',
            'Contains KPIs?'
        ]
    },
    'design/design-context.md': {
        'validation': [
            'Maps features and boundaries?',
            'Defines components and interfaces?',
            'Shows dependencies graph?',
            'Each feature has clear context boundary?'
        ]
    },
    'design/design-validation.md': {
        'validation': [
            'Lists E2E criteria for features?',
            'All criteria measurable?',
            'DoD clearly defined?'
        ]
    },
    'design/TechContext/code-style.md': {
        'validation': [
            'Has YAML header with datetime?',
            'Defines coding standards?',
            'Lists naming conventions?',
            'Specifies formatting rules?'
        ]
    },
    'design/TechContext/system-patterns.md': {
        'validation': [
            'Has YAML header with datetime?',
            'Documents architectural patterns?',
            'Lists design principles?',
            'Defines integration patterns?'
        ]
    },
    'work/progress.md': {
        'validation': [
            'Aggregates all milestone timestamps?',
            'Shows completion percentage?',
            'Current state accurate?'
        ]
    },
    'work/project-changes-log.md': {
        'validation': [
            'All changes have datetime?',
            'Changes linked to features/epics?',
            'Author role specified?'
        ]
    }
}

# Directories to create (without files)
MEMORY_BANK_DIRS = [
    'project',
    'design',
    'design/TechContext',
    'design/features',
    'work',
    'work/Sessions'
]


def create_memory_bank_structure(base_path: Path, project_name: str) -> None:
    """Create Memory-Bank directory structure with empty files."""
    
    # Create base directory
    memory_bank_path = base_path / "memory-bank"
    memory_bank_path.mkdir(exist_ok=True)
    
    # Create metadata file
    meta_file = memory_bank_path / ".memory-bank-meta.yaml"
    meta_data = {
        'version': '1.0',
        'created_at': datetime.now().isoformat(),
        'project_name': project_name,
        'description': f'Memory-Bank repository for {project_name}'
    }
    
    with open(meta_file, 'w') as f:
        yaml.dump(meta_data, f, default_flow_style=False)
    
    # Create directories
    for dir_path in MEMORY_BANK_DIRS:
        (memory_bank_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create empty files with minimal YAML headers
    for file_path in MEMORY_BANK_STRUCTURE.keys():
        full_path = memory_bank_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file with minimal YAML header
        yaml_header = f"""---
datetime: {datetime.now().isoformat()}
type: {file_path.split('/')[-1].replace('.md', '')}
---

"""
        full_path.write_text(yaml_header)


def validate_memory_bank_path(path: Path) -> bool:
    """Check if path contains valid Memory-Bank structure."""
    
    # Check for metadata file
    meta_file = path / ".memory-bank-meta.yaml"
    if not meta_file.exists():
        return False
    
    # Check for required directories
    for dir_path in ['project', 'design', 'work']:
        if not (path / dir_path).is_dir():
            return False
    
    return True


def get_validation_criteria(artifact_path: str) -> List[str]:
    """Get validation criteria for specific artifact."""
    
    if artifact_path in MEMORY_BANK_STRUCTURE:
        return MEMORY_BANK_STRUCTURE[artifact_path]['validation']
    return []


def create_release_based_structure(base_path: Path, project_name: str) -> None:
    """Create new release-based Memory-Bank structure."""
    
    # Create main directories
    directories = [
        "product",
        "architecture",
        "architecture/tech-context",
        "implementation",
        "progress",
        "progress/project-changelog",
        "templates",
        "templates/product",
        "templates/architecture", 
        "templates/implementation",
        "templates/implementation/component",
        "templates/implementation/epic",
        "templates/implementation/release",
        "templates/implementation/task",
    ]
    
    for dir_path in directories:
        (base_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Copy templates from our templates directory
    import shutil
    templates_src = Path(__file__).parent / "templates"
    templates_dst = base_path / "templates"
    
    if templates_src.exists():
        # Copy all template files
        for template_file in templates_src.rglob("*"):
            if template_file.is_file():
                rel_path = template_file.relative_to(templates_src)
                dst_file = templates_dst / rel_path
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(template_file, dst_file)
    
    # Create initial structure files with proper datetime headers
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Create README.md
    readme_content = f"""# Memory Bank Repository

## Structure Index

```
{project_name}/
├── README.md
├── CLAUDE.md
│
├── product/
│   ├── vision.md
│   └── releases/
│       └── {{01-release-name}}.md
│
├── architecture/
│   ├── current.md
│   ├── tech-context/
│   │   ├── code-style.md
│   │   └── system-patterns.md
│   └── releases/
│       └── {{01-release-name}}/
│           ├── overview.md
│           └── components/
│               └── {{component-name-01}}.md
│
├── implementation/
│   └── releases/
│       └── {{01-release-name}}/
│           ├── index.md
│           ├── qa.md
│           └── components/
│               └── {{01-component-name}}/
│                   ├── index.md
│                   ├── qa.md
│                   └── epics/
│                       └── {{epic-01}}/
│                           ├── index.md
│                           ├── qa.md
│                           └── tasks/
│                               └── {{task-01}}/
│                                   ├── dev.md
│                                   └── qa.md
│
├── progress/
│   ├── project-changelog/
│   │   └── {{001-change-description}}.md
│   └── releases/
│       └── {{01-release-name}}/
│           └── components/
│               └── {{01-component-name}}/
│                   ├── current-focus.md
│                   ├── state.yaml
│                   └── epics/
│                       └── {{epic-01}}/
│                           └── journal.md
│
└── templates/
    ├── product/
    │   ├── vision-template.md
    │   ├── vision-example.md
    │   ├── release-template.md
    │   └── release-example.md
    ├── architecture/
    │   ├── component-template.md
    │   ├── component-example.md
    │   ├── overview-template.md
    │   └── overview-example.md
    └── implementation/
        ├── component/
        │   ├── component-index-template.md
        │   ├── component-index-example.md
        │   ├── component-qa-template.md
        │   └── component-qa-example.md
        ├── epic/
        │   ├── epic-index-template.md
        │   ├── epic-index-example.md
        │   ├── epic-qa-template.md
        │   └── epic-qa-example.md
        ├── release/
        │   ├── release-index-template.md
        │   ├── release-index-example.md
        │   ├── release-qa-template.md
        │   └── release-qa-example.md
        └── task/
            ├── task-dev-template.md
            ├── task-dev-example.md
            ├── task-qa-template.md
            └── task-qa-example.md
```

## Naming Conventions

| Type | Format | Example |
|------|--------|---------|
| Release | `01-{{name}}` | `01-pre-alpha` |
| Epic | `epic-{{nn}}` | `epic-01` |
| Task | `task-{{nn}}` | `task-01` |
| Component | `{{nn}}-{{name}}` | `01-core-api` |
| Changelog | `{{nnn}}-{{desc}}` | `001-initial-setup` |
"""
    
    (base_path / "README.md").write_text(readme_content)


def create_pm_claude_md(project_name: str) -> str:
    """Create PM-specific CLAUDE.md content based on template."""
    
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Load PM template from file
    template_path = Path(__file__).parent / "prompts" / "pm_claude_md_template.md"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Replace placeholders
        return template_content.format(
            project_name=project_name,
            timestamp=timestamp
        )
    except Exception:
        # Fallback if template file is missing
        return f"""# CLAUDE.md - PM Workflow

PM Agent for {project_name}

Generated: {timestamp}
Claude-helpers Memory-Bank PM Workflow v1.0
"""


def create_memory_bank_claude_md(project_name: str) -> str:
    """Create CLAUDE.md content based on memory-bank template."""
    
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Load template from file
    template_path = Path(__file__).parent / "prompts" / "claude_md_template.md"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Replace placeholders
        return template_content.format(
            project_name=project_name,
            timestamp=timestamp
        )
    except Exception:
        # Fallback if template file is missing
        return f"""# CLAUDE.md

Memory-Bank structure for {project_name}

Generated: {timestamp}
Claude-helpers Memory-Bank v1.0
"""


def create_pm_slash_commands(commands_dir: Path, project_name: str) -> None:
    """Create PM workflow slash commands for Claude Code from templates."""
    
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    # Command templates mapping
    commands = {
        "run.md": "pm_run_command.md",
        "role.md": "pm_role_command.md", 
        "note.md": "pm_note_command.md",
        "progress.md": "pm_progress_command.md"
    }
    
    # Create each command from template
    for cmd_file, template_file in commands.items():
        try:
            # Load template
            template_path = Path(__file__).parent / "prompts" / template_file
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Replace project name placeholder
            cmd_content = template_content.format(project_name=project_name)
            
            # Write command file
            cmd_path = commands_dir / cmd_file
            cmd_path.write_text(cmd_content)
            
        except Exception:
            # Fallback if template missing
            cmd_path = commands_dir / cmd_file
            cmd_path.write_text(f"""---
description: "Memory-Bank workflow command"
---

# {cmd_file.replace('.md', '').title()} Command

Use Memory-Bank MCP tools for {project_name} workflow.
""")
    
