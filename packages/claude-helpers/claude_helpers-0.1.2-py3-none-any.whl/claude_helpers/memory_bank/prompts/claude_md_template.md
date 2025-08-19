# CLAUDE.md

This repository contains a Memory-Bank structure for managing development workflows and project documentation.

## Project Overview

**Project Name**: {project_name}

## Memory-Bank Repository Structure

The project uses a release-based Memory-Bank organization:

```
{project_name}/
├── /product           # Business requirements, user stories, feature specifications
├── /architecture      # System design, technical architecture, API specifications  
├── /implementation    # Code organization, development details, sprint tracking
├── /progress          # Project status, milestones, development journals
└── /templates         # Reusable templates and examples
```

## Development Context

### Key Directories
- **product/**: Contains product vision, requirements, and user story definitions
- **architecture/**: Technical specifications, system design, and component architecture
- **implementation/**: Development progress organized by releases and components
- **progress/**: Current status tracking, project journals, and milestone records

### Workflow Integration

This Memory-Bank integrates with claude-helpers for:
- PM workflow orchestration via MCP tools
- Progress tracking and focus management
- Cross-component development coordination

### MCP Tools Available

When working with this project, you have access to Memory-Bank MCP tools:
- `get-focus` - Get current focus for release/component
- `get-progress` - Get progress status for release/component  
- `turn-role` - Switch agent role (pm/dev/qa/owner)
- `note-journal` - Add journal entries
- `ask-memory-bank` - Query project documentation

### Usage Guidelines

1. **Release-based Development**: Work is organized by releases (01-pre-alpha, 02-alpha, etc.)
2. **Component Focus**: Each release contains components that can be developed independently
3. **Role-based Workflows**: Use PM/Dev/QA roles for different types of work
4. **Documentation First**: Always update relevant documentation when making changes

## Project-Specific Context

*Generated: {timestamp}*
*Claude-helpers Memory-Bank v1.0*