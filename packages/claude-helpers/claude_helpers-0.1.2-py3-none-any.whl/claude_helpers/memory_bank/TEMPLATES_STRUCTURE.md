# Memory-Bank Templates Structure

This document clarifies the different template directories and their purposes.

## Directory Structure

```
claude-helpers/src/claude_helpers/memory_bank/
├── prompts/                    # MCP Agent Prompts (system prompts for MCP tools)
│   ├── pm_focus_agent.md      # PM Focus Agent system prompt
│   ├── memory_bank_analyst.md # Memory-Bank Analyst system prompt
│   └── ...                    # Other MCP agent prompts
│
├── template_sources/           # Source Templates (for copying to Memory-Bank)
│   ├── pm-workflow/           # PM workflow templates
│   │   ├── claude-md-template.md     # Main PM Agent CLAUDE.md
│   │   ├── run-command-template.md   # /run command template
│   │   └── slash-commands/           # PM slash commands (/progress, /note, /role)
│   ├── sub-agents/            # Sub-agent definitions
│   │   ├── dev-specialist.md         # Dev sub-agent template
│   │   └── qa-specialist.md          # QA sub-agent template
│   └── mcp-prompts -> ../prompts     # Symlink to avoid duplication
│
└── templates/                  # Legacy artifact templates (preserved)
    ├── architecture/          # Architecture document templates
    ├── implementation/        # Implementation document templates
    ├── product/              # Product document templates
    └── prompts/              # Legacy prompts (different from MCP prompts)
```

## Memory-Bank Project Structure

When `spawn-templates` runs, it creates:

```
{memory-bank}/templates/
├── pm-workflow/              # Copied from template_sources/pm-workflow/
├── sub-agents/              # Copied from template_sources/sub-agents/
├── mcp-prompts/             # Copied from template_sources/mcp-prompts/ (symlinked to prompts/)
├── architecture/            # Preserved from existing templates/ (if exists)
├── implementation/          # Preserved from existing templates/ (if exists)
├── product/                # Preserved from existing templates/ (if exists)
└── prompts/                # Preserved from existing templates/ (if exists)
```

## Usage and Responsibilities

### 1. MCP Agent Prompts (`prompts/`)
**Purpose**: System prompts for MCP server agents
**Used by**: MCP server (`server.py`) via `_load_prompt_template()`
**Content**: AI agent instructions for processing MCP tool calls
**Examples**: 
- `pm_focus_agent.md` - Instructions for PM focus analysis
- `memory_bank_analyst.md` - Instructions for Memory-Bank queries

### 2. PM Workflow Templates (`template_sources/pm-workflow/`)
**Purpose**: Templates for PM Agent workflow in development projects
**Used by**: `memory-bank init` to copy to dev project
**Content**: CLAUDE.md and slash command templates for PM coordination
**Examples**:
- `claude-md-template.md` - Main PM Agent instructions
- `run-command-template.md` - /run command implementation

### 3. Sub-Agent Templates (`template_sources/sub-agents/`)
**Purpose**: Claude Code sub-agent definitions
**Used by**: `memory-bank init` to copy to dev project `.claude/agents/`
**Content**: Specialized agent definitions for dev/qa work
**Examples**:
- `dev-specialist.md` - Development sub-agent
- `qa-specialist.md` - QA sub-agent

### 4. Legacy Templates (`templates/`)
**Purpose**: Document templates for Memory-Bank artifacts
**Used by**: Memory-Bank structure creation and user customization
**Content**: Templates for architecture docs, implementation guides, etc.
**Status**: Preserved during `spawn-templates` to avoid destroying user work

## Commands and Template Usage

### `spawn-templates`
- Copies PM workflow templates from `template_sources/` to Memory-Bank
- **Preserves** existing artifact templates in Memory-Bank
- Only updates PM workflow, sub-agents, and MCP prompts

### `memory-bank init`
- Copies templates from Memory-Bank to development project
- Creates PM Agent CLAUDE.md from templates
- Sets up sub-agents and slash commands

### MCP Server
- Reads prompts from Memory-Bank `templates/mcp-prompts/` first
- Falls back to claude-helpers `prompts/` if not found
- Uses templates for AI agent instructions

## Best Practices

1. **Edit MCP prompts** in `prompts/` (they're the source of truth)
2. **Edit PM workflow** in `template_sources/pm-workflow/` 
3. **Preserve artifact templates** - don't delete Memory-Bank templates during updates
4. **Test template changes** by running `spawn-templates` in test Memory-Bank
5. **Version control** all template changes for team collaboration