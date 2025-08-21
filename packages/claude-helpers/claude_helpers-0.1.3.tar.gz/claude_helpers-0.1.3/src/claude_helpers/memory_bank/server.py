"""MCP server for Memory-Bank agent operations."""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional
from difflib import get_close_matches
from fastmcp import FastMCP
import asyncio
import os

from .models import FeatureState, JournalEntry
import re


def _extract_yaml_datetime(file_path: Path) -> Optional[float]:
    """Extract datetime from YAML header and convert to timestamp."""
    if not file_path.exists():
        return None
    
    try:
        content = file_path.read_text()
        if not content.startswith('---\n'):
            return None
            
        # Find end of YAML header
        yaml_end = content.find('\n---\n', 4)
        if yaml_end == -1:
            return None
            
        yaml_content = content[4:yaml_end]
        yaml_data = yaml.safe_load(yaml_content)
        
        if 'datetime' in yaml_data:
            dt_str = yaml_data['datetime']
            # Parse as UTC and convert to local timestamp for comparison with file mtime
            dt_utc = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            # Convert UTC to local time for proper comparison with file system timestamps
            import time
            return dt_utc.timestamp() + time.timezone
    except Exception:
        pass
    
    return None


def _paginate_content(content: str, page: int, page_size_tokens: int = 20000) -> dict:
    """Paginate content with smart section-based splitting.
    
    Args:
        content: Full content to paginate
        page: Page number (1-indexed)
        page_size_tokens: Approximate tokens per page
        
    Returns:
        Dict with content and pagination metadata
    """
    if not content or not content.strip():
        return {
            "content": "",
            "pagination": {
                "current_page": 1,
                "total_pages": 1,
                "has_more": False,
                "total_size": "0KB",
                "page_size": "0KB"
            }
        }
    
    # Rough estimation: 1 token ≈ 4 characters
    chars_per_page = page_size_tokens * 4
    
    # Split content by logical boundaries (markdown headers)
    # Split on h1 (# ) and h2 (## ) headers to keep sections together
    sections = re.split(r'\n(?=##? )', content)
    
    # Rebuild sections with proper formatting
    formatted_sections = []
    for i, section in enumerate(sections):
        if i == 0:
            formatted_sections.append(section)
        else:
            formatted_sections.append('\n' + section)
    
    # Group sections into pages
    pages = []
    current_page = ""
    
    for section in formatted_sections:
        # Check if adding this section would exceed page size
        if len(current_page + section) > chars_per_page and current_page:
            # Current page is full, start new page
            pages.append(current_page.strip())
            current_page = section
        else:
            # Add section to current page
            current_page += section
    
    # Add the last page if it has content
    if current_page.strip():
        pages.append(current_page.strip())
    
    # Handle empty content
    if not pages:
        pages = [""]
    
    total_pages = len(pages)
    
    # Validate page number
    if page < 1:
        page = 1
    elif page > total_pages:
        return {
            "content": "",
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "has_more": False,
                "total_size": f"{len(content) // 1024}KB",
                "page_size": "0KB",
                "error": f"Page {page} does not exist. Total pages: {total_pages}"
            }
        }
    
    # Get the requested page (convert to 0-indexed)
    page_content = pages[page - 1]
    
    return {
        "content": page_content,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "has_more": page < total_pages,
            "total_size": f"{len(content) // 1024}KB",
            "page_size": f"{len(page_content) // 1024}KB",
            "next_page_hint": f"Use page={page + 1} to continue reading" if page < total_pages else None
        }
    }


def _create_yaml_header(focus_type: str, **metadata) -> str:
    """Create YAML header for focus files."""
    header_data = {
        'datetime': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'focus_type': focus_type,
        **metadata
    }
    
    yaml_content = yaml.dump(header_data, default_flow_style=False, sort_keys=False)
    return f"---\n{yaml_content}---\n\n"


def _safe_load_state_yaml(state_file: Path) -> dict:
    """Safely load state.yaml handling multiple documents."""
    if not state_file.exists():
        return {}
    
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by document separators and get the last non-empty document
        documents = content.split('---')
        
        # Find the last document that contains actual state data
        for doc in reversed(documents):
            doc = doc.strip()
            if doc and not doc.startswith('datetime:'):
                # Try to parse this document
                try:
                    state_data = yaml.safe_load(doc)
                    if isinstance(state_data, dict) and state_data:
                        return state_data
                except:
                    continue
        
        # Fallback: try to load the entire content as one document
        try:
            state_data = yaml.safe_load(content)
            if isinstance(state_data, dict):
                return state_data
        except:
            pass
            
        return {}
        
    except Exception:
        return {}


def _ensure_component_state(memory_bank_path: Path, release: str, component: str) -> dict:
    """Ensure component has valid state.yaml, create default if missing."""
    state_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "state.yaml"
    
    # Try to load existing state
    state_data = _safe_load_state_yaml(state_file)
    
    # If no valid state found, create default
    if not state_data:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        state_data = {
            "release": release,
            "component": component,
            "status": "not_started",
            "current_epic": "epic-01",
            "current_task": "task-01",
            "active_role": "owner",
            "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        # Save default state
        with open(state_file, 'w') as f:
            yaml.dump(state_data, f, default_flow_style=False)
    
    return state_data


# Create MCP server instance
mcp = FastMCP("Memory-Bank Agent Tools")


def _get_memory_bank_path() -> Optional[Path]:
    """Get Memory-Bank path from environment variable or binding files."""
    import os
    
    # Method 1: Environment variable (preferred for sub-agents)
    env_path = os.getenv('MEMORY_BANK_PATH')
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path
    
    # Method 2: Look for binding in current working directory
    helpers_dir = Path.cwd() / ".helpers"
    binding_file = helpers_dir / "memory_bank.json"
    
    if binding_file.exists():
        try:
            with open(binding_file, 'r') as f:
                binding = json.load(f)
            return Path(binding['memory_bank_path'])
        except Exception:
            pass
    
    # Method 3: Look for .claude/memory-bank-binding.txt (alternative)
    claude_binding = Path.cwd() / ".claude" / "memory-bank-binding.txt"
    if claude_binding.exists():
        try:
            with open(claude_binding, 'r') as f:
                path = Path(f.read().strip())
                if path.exists():
                    return path
        except Exception:
            pass
    
    return None


@mcp.tool(name="get-focus")
def get_focus(release: str, component: str, page: int = 1) -> str:
    """Get current focus for release/component with pagination support.
    
    Args:
        release: Release name (e.g. "01-pre-alpha")
        component: Component name (e.g. "01-core-api")
        page: Page number for pagination (default: 1)
        
    Returns:
        JSON string with focus content and pagination metadata
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    # Validate release/component structure
    validation = _validate_release_component_structure(memory_bank_path, release, component)
    if not validation["valid"]:
        error_message = _format_validation_error(validation, release, component)
        return json.dumps({
            "error": "Invalid release/component specification",
            "message": error_message
        })
    
    focus_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "current-focus.md"
    
    # Check if focus exists and is current
    if not focus_file.exists() or _focus_needs_rebuild(memory_bank_path, release, component, focus_file):
        # Rebuild focus based on current state
        state_data = _ensure_component_state(memory_bank_path, release, component)
        current_epic = state_data.get("current_epic", "epic-01")
        current_task = state_data.get("current_task", "task-01")
        active_role = state_data.get("active_role", "owner")
        
        _create_role_focus(memory_bank_path, release, component, current_epic, current_task, active_role)
    
    try:
        with open(focus_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply pagination to focus content
        paginated = _paginate_content(content, page)
        
        return json.dumps({
            "release": release,
            "component": component,
            "content": paginated["content"],
            "pagination": paginated["pagination"]
        })
        
    except Exception as e:
        return json.dumps({"error": f"Failed to read focus: {e}"})


@mcp.tool(name="get-progress")
def get_progress(release: str, component: str) -> str:
    """Get detailed progress for release/component - now with architecture/current.md auto-rebuild.
    
    Args:
        release: Release name (e.g. "01-pre-alpha")
        component: Component name (e.g. "01-core-api")
        
    Returns:
        JSON string with detailed component progress
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    try:
        # NEW: Auto-rebuild architecture/current.md if needed
        if _architecture_current_needs_rebuild(memory_bank_path):
            _rebuild_architecture_current(memory_bank_path)
        
        # Validate release/component structure
        validation = _validate_release_component_structure(memory_bank_path, release, component)
        if not validation["valid"]:
            error_message = _format_validation_error(validation, release, component)
            return json.dumps({
                "error": "Invalid release/component specification", 
                "message": error_message
            })
        
        # Ensure component has valid state
        state_data = _ensure_component_state(memory_bank_path, release, component)
        
        # Get epics progress
        epics_dir = memory_bank_path / "progress" / "releases" / release / "components" / component / "epics"
        epics_info = []
        
        if epics_dir.exists():
            for epic_dir in epics_dir.iterdir():
                if epic_dir.is_dir():
                    journal_file = epic_dir / "journal.md"
                    epic_status = "planned"
                    
                    if journal_file.exists():
                        epic_status = "in_progress"
                        # Check if completed - could look at journal entries
                    
                    epics_info.append({
                        "epic_id": epic_dir.name,
                        "status": epic_status
                    })
        
        return json.dumps({
            "release": release,
            "component": component,
            "state": state_data,
            "epics": epics_info,
            "project_overview": "See updated /architecture/current.md for full project status and cross-component view"
        })
        
    except Exception as e:
        return json.dumps({"error": f"Failed to get progress: {e}"})


@mcp.tool(name="note-journal") 
def note_journal(release: str, component: str, content: str, role: str) -> str:
    """Add journal entry for release/component.
    
    Args:
        release: Release name (e.g. "01-pre-alpha")
        component: Component name (e.g. "01-core-api")
        content: Journal note content
        role: Agent role (pm/dev/qa/owner)
        
    Returns:
        JSON string with confirmation
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    try:
        # Find current epic from state
        state_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "state.yaml"
        current_epic = "epic-01"  # default
        
        if state_file.exists():
            state_data = _safe_load_state_yaml(state_file)
            current_epic = state_data.get('current_epic', 'epic-01')
        
        # Add to epic journal
        journal_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "epics" / current_epic / "journal.md"
        journal_file.parent.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now()
        entry = f"\n---\n## {timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {role.upper()}\n\n{content}\n"
        
        # Append to journal
        with open(journal_file, 'a') as f:
            f.write(entry)
        
        return json.dumps({
            "success": True,
            "release": release,
            "component": component,
            "epic": current_epic,
            "timestamp": timestamp.isoformat()
        })
        
    except Exception as e:
        return json.dumps({"error": f"Failed to add journal entry: {e}"})


@mcp.tool(name="turn-role")
def turn_role(release: str, component: str, role: str) -> str:
    """Switch active role for release/component.
    
    Args:
        release: Release name (e.g. "01-pre-alpha")  
        component: Component name (e.g. "01-core-api")
        role: New role (qa/dev/owner)
        
    Returns:
        JSON string with confirmation and next steps
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    if role not in ['qa', 'dev', 'owner']:
        return json.dumps({"error": f"Invalid role: {role}. Must be qa, dev, or owner"})
    
    try:
        # Update state.yaml
        state_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing state or create new
        if state_file.exists():
            state_data = _safe_load_state_yaml(state_file) or {}
        else:
            state_data = {
                "release": release,
                "component": component,
                "current_epic": "epic-01",
                "current_task": "task-01",
                "status": "in_progress"
            }
        
        # Update role and status
        state_data["active_role"] = role
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Start work if delegating to dev/qa
        if role in ['dev', 'qa'] and state_data.get("status") == "not_started":
            state_data["status"] = "in_progress"
        
        # Save state as single YAML document
        state_data["datetime"] = timestamp
        with open(state_file, 'w') as f:
            yaml.dump(state_data, f, default_flow_style=False)
        
        # Get current epic/task for focus generation
        current_epic = state_data.get("current_epic", "epic-01")
        current_task = state_data.get("current_task", "task-01")
        
        # Generate and save focus for the new role
        _create_role_focus(memory_bank_path, release, component, current_epic, current_task, role)
        
        # Generate task-specific focus for the new role
        task_focus = _generate_task_focus(memory_bank_path, release, component, current_epic, current_task, role)
        
        # Collect full context for sub-agent
        full_context = _collect_release_component_context(memory_bank_path, release, component)
        
        # Generate sub-agent focus instructions
        sub_agent_instructions = _generate_sub_agent_instructions(
            memory_bank_path, release, component, current_epic, current_task, role, full_context
        )
        
        response = {
            "success": True,
            "release": release,
            "component": component,
            "new_role": role,
            "current_epic": current_epic,
            "current_task": current_task,
            "status": state_data.get("status"),
            "message": f"Role switched to {role}. Now working on {current_epic}/{current_task}",
            "task_focus": task_focus,
            "sub_agent_instructions": sub_agent_instructions,
            "next_pm_action": f"After delegation: Call {role} sub-agent to begin work on {current_epic}/{current_task}"
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to turn role: {e}"})


@mcp.tool(name="get-pm-focus")
def get_pm_focus(release: str, component: str) -> str:
    """Get comprehensive PM focus context - now with caching and auto-rebuild.
    
    Args:
        release: Release name (e.g. "01-pre-alpha") 
        component: Component name (e.g. "01-core-api")
        
    Returns:
        JSON string with PM briefing and context
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    try:
        # NEW: Check if PM focus cache needs rebuild
        if _pm_focus_needs_rebuild(memory_bank_path, release, component):
            _create_pm_focus(memory_bank_path, release, component)
        
        # Validate release/component structure
        validation = _validate_release_component_structure(memory_bank_path, release, component)
        if not validation["valid"]:
            error_message = _format_validation_error(validation, release, component)
            return json.dumps({
                "error": "Invalid release/component specification",
                "message": error_message,
                "available_releases": validation["available_releases"],
                "available_components": validation["available_components"]
            })
        
        # Return cached PM focus
        pm_focus_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "pm-focus.md"
        
        if pm_focus_file.exists():
            return json.dumps({
                "release": release,
                "component": component,
                "pm_focus": pm_focus_file.read_text(),
                "architecture_current": "See /architecture/current.md for full project overview"
            })
        else:
            # Fallback to original logic if cache creation failed
            return json.dumps({"error": "PM focus file not found after rebuild attempt"})
            
    except Exception as e:
        return json.dumps({"error": f"Failed to get PM focus: {e}"})
        
    # Original fallback logic (unreachable but keeping for completeness)
    try:
        # Collect comprehensive context for this specific release/component
        context_data = _collect_release_component_context(memory_bank_path, release, component)
        
        # Load PM focus agent prompt
        system_prompt = _load_prompt_template("pm_focus_agent.md", {
            "memory_bank_path": memory_bank_path,
            "release": release,
            "component": component
        })

        user_query = f"""Analyze release "{release}" component "{component}" and provide PM focus briefing.

Release/Component Context:
{context_data}

Generate comprehensive PM briefing with project context, component status, progress assessment, and actionable next steps."""

        # Use dynamic PM focus analysis based on current progress and state
        analysis_result = _dynamic_pm_focus_analysis(memory_bank_path, release, component)
        
        return json.dumps({
            "release": release,
            "component": component,
            "pm_briefing": analysis_result,
            "source": "pm-focus-agent",
            "memory_bank_path": str(memory_bank_path)
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to get PM focus: {e}",
            "release": release,
            "component": component
        })


@mcp.tool(name="current-task")
def current_task(release: str, component: str, page: int = 1) -> str:
    """Get current task context and details with pagination support.
    
    Args:
        release: Release name (e.g. "01-pre-alpha")
        component: Component name (e.g. "01-core-api")
        page: Page number for pagination (default: 1)
        
    Returns:
        JSON string with current task details and pagination metadata
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    try:
        # Get current state
        state_data = _ensure_component_state(memory_bank_path, release, component)
        current_epic = state_data.get("current_epic", "epic-01")
        current_task_id = state_data.get("current_task", "task-01")
        
        # Load task details - corrected path structure
        task_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "epics" / current_epic / "tasks" / current_task_id / "dev.md"
        
        task_content = "Task file not found"
        if task_file.exists():
            task_content = task_file.read_text()
        
        # Apply pagination to task content
        paginated = _paginate_content(task_content, page)
        
        return json.dumps({
            "release": release,
            "component": component,
            "epic": current_epic,
            "task": current_task_id,
            "content": paginated["content"],
            "pagination": paginated["pagination"],
            "source": f"implementation/releases/{release}/components/{component}/epics/{current_epic}/tasks/{current_task_id}/dev.md"
        })
        
    except Exception as e:
        return json.dumps({"error": f"Failed to get current task: {e}"})


@mcp.tool(name="current-epic")
def current_epic(release: str, component: str, page: int = 1) -> str:
    """Get current epic context and overview with pagination support.
    
    Args:
        release: Release name (e.g. "01-pre-alpha")
        component: Component name (e.g. "01-core-api")
        page: Page number for pagination (default: 1)
        
    Returns:
        JSON string with current epic details and pagination metadata
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    try:
        # Get current state
        state_data = _ensure_component_state(memory_bank_path, release, component)
        current_epic_id = state_data.get("current_epic", "epic-01")
        
        # Load epic details - corrected path structure
        epic_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "epics" / current_epic_id / "index.md"
        
        epic_content = "Epic file not found"
        if epic_file.exists():
            epic_content = epic_file.read_text()
        
        # Apply pagination to epic content
        paginated = _paginate_content(epic_content, page)
        
        return json.dumps({
            "release": release,
            "component": component,
            "epic": current_epic_id,
            "content": paginated["content"],
            "pagination": paginated["pagination"],
            "source": f"implementation/releases/{release}/components/{component}/epics/{current_epic_id}/index.md"
        })
        
    except Exception as e:
        return json.dumps({"error": f"Failed to get current epic: {e}"})


@mcp.tool(name="current-component")
def current_component(release: str, component: str, page: int = 1) -> str:
    """Get current component context and architecture with pagination support.
    
    Args:
        release: Release name (e.g. "01-pre-alpha")
        component: Component name (e.g. "01-core-api")
        page: Page number for pagination (default: 1)
        
    Returns:
        JSON string with component architecture details and pagination metadata
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    try:
        # Load component architecture
        component_file = memory_bank_path / "architecture" / "releases" / release / "components" / f"{component}.md"
        
        component_content = "Component file not found"
        if component_file.exists():
            component_content = component_file.read_text()
        
        # Apply pagination to component content
        paginated = _paginate_content(component_content, page)
        
        return json.dumps({
            "release": release,
            "component": component,
            "content": paginated["content"],
            "pagination": paginated["pagination"],
            "source": f"architecture/releases/{release}/components/{component}.md"
        })
        
    except Exception as e:
        return json.dumps({"error": f"Failed to get current component: {e}"})


@mcp.tool(name="validate-project-structure")
def validate_project_structure(release: str, component: str, file_path: str, purpose: str) -> str:
    """Validate if file/directory creation follows project structure standards.
    
    Args:
        release: Release name (e.g., "02-alpha")
        component: Component name (e.g., "01-modus-id")
        file_path: Path to file/directory being created/modified
        purpose: Intended purpose or description of the file/directory
    
    Returns:
        Validation result and suggestions for project structure adherence
    """
    try:
        memory_bank_path = _get_memory_bank_path()
        if not memory_bank_path:
            return json.dumps({
                "error": "Memory-Bank not configured. Run: claude-helpers memory-bank init"
            })
        
        # Try SDK extraction first (only works in Claude Code environment)
        prompt_file = memory_bank_path / "templates" / "mcp-prompts" / "validate_project_structure.md"
        
        if prompt_file.exists():
            try:
                prompt_template = prompt_file.read_text()
                prompt = prompt_template.format(
                    release=release,
                    component=component,
                    file_path=file_path,
                    purpose=purpose
                )
                
                # Add Memory-Bank context paths
                prompt += f"\n\nMemory-Bank paths:\n"
                prompt += f"- Architecture: {memory_bank_path}/architecture/releases/{release}/components/{component}.md\n"
                prompt += f"- Implementation: {memory_bank_path}/implementation/releases/{release}/components/{component}/\n"
                prompt += f"- Code Standards: {memory_bank_path}/architecture/tech-context/code-standards.md\n"
                prompt += f"- Project Structure: {memory_bank_path}/architecture/tech-context/project-structure.md"
                
                # Task tool only available in Claude Code, not MCP
                result = Task(
                    description=f"Validate project structure for {file_path}",
                    prompt=prompt,
                    subagent_type="general-purpose"
                )
                
                if result and len(result.strip()) < 3000:
                    return result.strip()
                else:
                    raise Exception("Task result too large or empty")
                    
            except Exception as e:
                # Fallback to simple validation if SDK fails
                return _fallback_structure_validation(memory_bank_path, release, component, file_path, purpose)
        else:
            return _fallback_structure_validation(memory_bank_path, release, component, file_path, purpose)
        
    except Exception as e:
        return json.dumps({
            "error": f"Validation failed: {e}",
            "file_path": file_path,
            "suggestion": "Check that Memory-Bank is properly configured and file path is valid"
        })


@mcp.tool(name="ask-memory-bank")
def ask_memory_bank(query: str) -> str:
    """Intelligent semantic search and analysis across Memory-Bank content using internal agent.
    
    Args:
        query: Search query or question in any language
        
    Returns:
        JSON string with comprehensive analysis and relevant information
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    try:
        # Use internal agent with Claude SDK for intelligent search
        from claude_helpers.config import get_global_config
        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
        import asyncio
        
        config = get_global_config()
        
        # Collect comprehensive context from Memory-Bank
        context_data = _collect_comprehensive_context(memory_bank_path, query)
        
        # Load system prompt from file
        system_prompt = _load_prompt_template("memory_bank_analyst.md", {
            "memory_bank_path": memory_bank_path
        })

        user_query = f"""Query: "{query}"

Memory-Bank Content:
{context_data}

Please analyze this query and provide a comprehensive, intelligent response using the Memory-Bank content above. Focus on accuracy and include specific file references for your sources."""

        # Execute with internal agent
        async def run_agent():
            try:
                client_options = ClaudeCodeOptions(
                    system_prompt=system_prompt,
                    allowed_tools=["Read", "Glob"],
                    max_turns=1
                )
                
                # In plan mode, don't set API key - use existing Claude Code auth
                if not config.use_plan_mode and config.anthropic_api_key:
                    import os
                    os.environ['ANTHROPIC_API_KEY'] = config.anthropic_api_key
                
                async with ClaudeSDKClient(options=client_options) as client:
                    response = await client.run(user_query)
                    return response
                    
            except Exception as e:
                return f"Agent analysis failed: {e}"
        
        # For now, use enhanced fallback search with smart analysis
        # TODO: Implement proper async agent integration
        agent_response = _enhanced_fallback_analysis(memory_bank_path, query, context_data)
        
        return json.dumps({
            "query": query,
            "response": agent_response,
            "source": "memory-bank-agent",
            "memory_bank_path": str(memory_bank_path)
        })
        
    except Exception as e:
        # Fallback to simple search if agent fails
        return _fallback_simple_search(memory_bank_path, query, str(e))


@mcp.tool(name="update-task-status")
def update_task_status(release: str, component: str, epic: str, task: str, status: str) -> str:
    """Update task status in component state.
    
    Args:
        release: Release name
        component: Component name
        epic: Epic ID (e.g. "epic-01")
        task: Task ID (e.g. "task-01")
        status: New status (pending/in_progress/completed)
        
    Returns:
        JSON confirmation
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    try:
        # Update state file
        state_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "state.yaml"
        
        if state_file.exists():
            state_data = _safe_load_state_yaml(state_file) or {}
        else:
            state_data = {}
        
        # Update task status (simplified - just track current task)
        if status == "completed":
            state_data["last_completed_task"] = f"{epic}/{task}"
        
        state_data["current_epic"] = epic
        state_data["current_task"] = task
        state_data["task_status"] = status
        
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        state_data["datetime"] = timestamp
        
        with open(state_file, 'w') as f:
            yaml.dump(state_data, f, default_flow_style=False)
        
        return json.dumps({
            "success": True,
            "release": release,
            "component": component,
            "epic": epic,
            "task": task,
            "status": status
        })
        
    except Exception as e:
        return json.dumps({"error": f"Failed to update task status: {e}"})


@mcp.tool(name="next-task")
def next_task(release: str, component: str) -> str:
    """Move to next task within current epic.
    
    Args:
        release: Release name (e.g. "01-pre-alpha")
        component: Component name (e.g. "01-core-api")
        
    Returns:
        JSON string with next task information
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    try:
        # Get current state
        state_data = _ensure_component_state(memory_bank_path, release, component)
        current_epic = state_data.get("current_epic", "epic-01")
        current_task = state_data.get("current_task", "task-01")
        
        # Parse current task number
        try:
            task_num = int(current_task.split("-")[1])
            next_task_num = task_num + 1
            next_task_id = f"task-{next_task_num:02d}"
        except:
            next_task_id = "task-02"
        
        # Check if next task exists
        task_dir = memory_bank_path / "implementation" / "releases" / release / "components" / component / "epics" / current_epic / "tasks" / next_task_id
        
        if not task_dir.exists():
            # No more tasks in this epic
            return json.dumps({
                "release": release,
                "component": component,
                "current_epic": current_epic,
                "current_task": current_task,
                "next_task": None,
                "epic_complete": True,
                "message": f"All tasks completed in {current_epic}. Use next-epic to move to next epic."
            })
        
        # Update state to next task
        state_data["current_task"] = next_task_id
        state_data["datetime"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Save updated state
        state_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "state.yaml"
        with open(state_file, 'w') as f:
            yaml.dump(state_data, f, default_flow_style=False)
        
        return json.dumps({
            "release": release,
            "component": component,
            "current_epic": current_epic,
            "previous_task": current_task,
            "current_task": next_task_id,
            "epic_complete": False,
            "message": f"Moved to {next_task_id} in {current_epic}"
        })
        
    except Exception as e:
        return json.dumps({"error": f"Failed to move to next task: {e}"})


@mcp.tool(name="next-epic")
def next_epic(release: str, component: str) -> str:
    """Move to next epic within component.
    
    Args:
        release: Release name (e.g. "01-pre-alpha")
        component: Component name (e.g. "01-core-api")
        
    Returns:
        JSON string with next epic information
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    try:
        # Get current state
        state_data = _ensure_component_state(memory_bank_path, release, component)
        current_epic = state_data.get("current_epic", "epic-01")
        
        # Parse current epic number
        try:
            epic_num = int(current_epic.split("-")[1])
            next_epic_num = epic_num + 1
            next_epic_id = f"epic-{next_epic_num:02d}"
        except:
            next_epic_id = "epic-02"
        
        # Check if next epic exists
        epic_dir = memory_bank_path / "implementation" / "releases" / release / "components" / component / "epics" / next_epic_id
        
        if not epic_dir.exists():
            # No more epics - component complete
            return json.dumps({
                "release": release,
                "component": component,
                "current_epic": current_epic,
                "next_epic": None,
                "component_complete": True,
                "message": f"All epics completed in component {component}. Component is ready for final review."
            })
        
        # Move to first task of next epic
        state_data["current_epic"] = next_epic_id
        state_data["current_task"] = "task-01"
        state_data["datetime"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Save updated state
        state_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "state.yaml"
        with open(state_file, 'w') as f:
            yaml.dump(state_data, f, default_flow_style=False)
        
        return json.dumps({
            "release": release,
            "component": component,
            "previous_epic": current_epic,
            "current_epic": next_epic_id,
            "current_task": "task-01",
            "component_complete": False,
            "message": f"Moved to {next_epic_id}, starting with task-01"
        })
        
    except Exception as e:
        return json.dumps({"error": f"Failed to move to next epic: {e}"})


def _load_prompt_template(template_name: str, variables: dict) -> str:
    """Load prompt template from Memory-Bank templates or fallback to claude-helpers."""
    
    memory_bank_path = variables.get('memory_bank_path')
    
    # First try Memory-Bank templates (preferred)
    if memory_bank_path:
        memory_bank_template = Path(memory_bank_path) / "templates" / "mcp-prompts" / template_name
        if memory_bank_template.exists():
            try:
                with open(memory_bank_template, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                # Replace variables
                return template_content.format(**variables)
            except Exception:
                pass
    
    # Fallback to claude-helpers template sources directory  
    fallback_template = Path(__file__).parent / "template_sources" / "mcp-prompts" / template_name
    if fallback_template.exists():
        try:
            with open(fallback_template, 'r', encoding='utf-8') as f:
                template_content = f.read()
            # Replace variables
            return template_content.format(**variables)
        except Exception:
            pass
    
    # Final fallback if no template files found
    return f"""You are a Memory-Bank Documentation Analyst.
    
Analyze the provided content and answer queries directly and comprehensively.
Memory-Bank Path: {variables.get('memory_bank_path', 'Unknown')}
Template: {template_name} (not found - using fallback)
"""


def _collect_release_component_context(memory_bank_path: Path, release: str, component: str) -> str:
    """Collect specific context for release/component analysis."""
    context_parts = []
    
    try:
        # 1. Project context from product/
        product_dir = memory_bank_path / "product"
        if product_dir.exists():
            context_parts.append("=== PROJECT CONTEXT ===")
            
            # Vision and general product info
            vision_file = product_dir / "vision.md"
            if vision_file.exists():
                try:
                    with open(vision_file, 'r', encoding='utf-8') as f:
                        vision_content = f.read()
                    context_parts.append(f"--- {vision_file.relative_to(memory_bank_path)} ---")
                    context_parts.append(vision_content[:1500])  # More content for PM context
                except Exception:
                    pass
            
            # Release-specific product requirements
            release_product = product_dir / "releases" / f"{release}.md"
            if release_product.exists():
                try:
                    with open(release_product, 'r', encoding='utf-8') as f:
                        release_content = f.read()
                    context_parts.append(f"--- {release_product.relative_to(memory_bank_path)} ---")
                    context_parts.append(release_content)
                except Exception:
                    pass
        
        # 2. Architecture context for the component
        arch_dir = memory_bank_path / "architecture"
        if arch_dir.exists():
            context_parts.append("\n=== ARCHITECTURE CONTEXT ===")
            
            # Release architecture
            release_arch_dir = arch_dir / "releases" / release
            if release_arch_dir.exists():
                # Component architecture
                component_arch = release_arch_dir / "components" / f"{component}.md"
                if component_arch.exists():
                    try:
                        with open(component_arch, 'r', encoding='utf-8') as f:
                            comp_arch_content = f.read()
                        context_parts.append(f"--- {component_arch.relative_to(memory_bank_path)} ---")
                        context_parts.append(comp_arch_content)
                    except Exception:
                        pass
                
                # Release overview
                release_overview = release_arch_dir / "overview.md"
                if release_overview.exists():
                    try:
                        with open(release_overview, 'r', encoding='utf-8') as f:
                            overview_content = f.read()
                        context_parts.append(f"--- {release_overview.relative_to(memory_bank_path)} ---")
                        context_parts.append(overview_content)
                    except Exception:
                        pass
        
        # 3. Implementation status and progress
        impl_dir = memory_bank_path / "implementation"
        if impl_dir.exists():
            context_parts.append("\n=== IMPLEMENTATION STATUS ===")
            
            # Component implementation details
            component_impl = impl_dir / "releases" / release / "components" / component
            if component_impl.exists():
                # Component index
                comp_index = component_impl / "index.md"
                if comp_index.exists():
                    try:
                        with open(comp_index, 'r', encoding='utf-8') as f:
                            impl_content = f.read()
                        context_parts.append(f"--- {comp_index.relative_to(memory_bank_path)} ---")
                        context_parts.append(impl_content)
                    except Exception:
                        pass
                
                # QA requirements
                comp_qa = component_impl / "qa.md"
                if comp_qa.exists():
                    try:
                        with open(comp_qa, 'r', encoding='utf-8') as f:
                            qa_content = f.read()
                        context_parts.append(f"--- {comp_qa.relative_to(memory_bank_path)} ---")
                        context_parts.append(qa_content[:800])
                    except Exception:
                        pass
        
        # 4. Current progress and state
        progress_dir = memory_bank_path / "progress"
        if progress_dir.exists():
            context_parts.append("\n=== CURRENT PROGRESS ===")
            
            # Component progress tracking
            component_progress = progress_dir / "releases" / release / "components" / component
            if component_progress.exists():
                # Current focus
                focus_file = component_progress / "current-focus.md"
                if focus_file.exists():
                    try:
                        with open(focus_file, 'r', encoding='utf-8') as f:
                            focus_content = f.read()
                        context_parts.append(f"--- {focus_file.relative_to(memory_bank_path)} ---")
                        context_parts.append(focus_content)
                    except Exception:
                        pass
                
                # State file
                state_file = component_progress / "state.yaml"
                if state_file.exists():
                    try:
                        with open(state_file, 'r', encoding='utf-8') as f:
                            state_content = f.read()
                        context_parts.append(f"--- {state_file.relative_to(memory_bank_path)} ---")
                        context_parts.append(state_content)
                    except Exception:
                        pass
        
        if not context_parts:
            return f"No specific context found for release '{release}' component '{component}'"
        
        return "\n".join(context_parts)
        
    except Exception as e:
        return f"Error collecting release/component context: {e}"


def _dynamic_pm_focus_analysis(memory_bank_path: Path, release: str, component: str) -> str:
    """Dynamic PM focus analysis based on real progress, journal, and state."""
    
    # Collect all current data
    state_data = _ensure_component_state(memory_bank_path, release, component)
    progress_data = _collect_progress_data(memory_bank_path, release, component)
    journal_data = _collect_journal_data(memory_bank_path, release, component)
    
    # Analyze current situation
    current_situation = _analyze_current_situation(state_data, progress_data, journal_data)
    
    # Determine PM continuation strategy
    continuation_strategy = _determine_pm_continuation(state_data, progress_data, journal_data, current_situation)
    
    # Generate dynamic focus
    focus_parts = []
    
    # Header with current context
    focus_parts.append(f"# PM Dynamic Focus: {release}/{component}")
    focus_parts.append(f"**Last Updated**: {state_data.get('datetime', 'Unknown')}")
    focus_parts.append(f"**Active Role**: {state_data.get('active_role', 'owner')}")
    focus_parts.append(f"**Status**: {state_data.get('status', 'not_started')}")
    focus_parts.append(f"**Current Work**: {state_data.get('current_epic', 'epic-01')}/{state_data.get('current_task', 'task-01')}")
    
    # Current situation analysis
    focus_parts.append("\n## Current Situation Analysis")
    focus_parts.append(f"**State**: {current_situation['state_summary']}")
    focus_parts.append(f"**Progress**: {current_situation['progress_summary']}")
    focus_parts.append(f"**Recent Activity**: {current_situation['recent_activity']}")
    
    if current_situation['blockers']:
        focus_parts.append(f"**⚠️ Blockers**: {current_situation['blockers']}")
    
    # PM Continuation Strategy
    focus_parts.append("\n## PM Continuation Strategy")
    focus_parts.append(f"**Next Action**: {continuation_strategy['next_action']}")
    focus_parts.append(f"**Reasoning**: {continuation_strategy['reasoning']}")
    focus_parts.append(f"**Command**: `{continuation_strategy['command']}`")
    
    if continuation_strategy['sub_agent_focus']:
        focus_parts.append(f"**Sub-Agent Focus**: {continuation_strategy['sub_agent_focus']}")
    
    if continuation_strategy['focus_switch']:
        focus_parts.append(f"**Focus Switch**: {continuation_strategy['focus_switch']}")
    
    # Work Continuity
    focus_parts.append("\n## Work Continuity")
    for step in continuation_strategy['continuity_steps']:
        focus_parts.append(f"- {step}")
    
    # Context for return
    if continuation_strategy['return_context']:
        focus_parts.append("\n## Return Context")
        focus_parts.append(continuation_strategy['return_context'])
    
    return "\n".join(focus_parts)


def _collect_progress_data(memory_bank_path: Path, release: str, component: str) -> dict:
    """Collect progress data for component."""
    
    progress_data = {
        "epics": {},
        "completed_tasks": [],
        "current_work": {},
        "blockers": []
    }
    
    # Check epic/task structure and progress
    impl_dir = memory_bank_path / "implementation" / "releases" / release / "components" / component / "epics"
    if impl_dir.exists():
        for epic_dir in impl_dir.iterdir():
            if epic_dir.is_dir() and epic_dir.name.startswith('epic-'):
                epic_id = epic_dir.name
                epic_progress = {
                    "tasks": [],
                    "completed": 0,
                    "total": 0
                }
                
                tasks_dir = epic_dir / "tasks"
                if tasks_dir.exists():
                    for task_dir in tasks_dir.iterdir():
                        if task_dir.is_dir() and task_dir.name.startswith('task-'):
                            task_id = task_dir.name
                            epic_progress["tasks"].append(task_id)
                            epic_progress["total"] += 1
                
                progress_data["epics"][epic_id] = epic_progress
    
    return progress_data


def _collect_journal_data(memory_bank_path: Path, release: str, component: str) -> list:
    """Collect recent journal entries for component."""
    
    journal_entries = []
    
    # Look for journal files in progress directory
    progress_dir = memory_bank_path / "progress" / "releases" / release / "components" / component
    if progress_dir.exists():
        journal_files = list(progress_dir.glob("journal-*.md"))
        journal_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Get last 5 journal entries
        for journal_file in journal_files[:5]:
            try:
                with open(journal_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract timestamp and content
                lines = content.split('\n')
                timestamp = journal_file.stem.replace('journal-', '')
                entry_content = '\n'.join(lines[2:]) if len(lines) > 2 else content
                
                journal_entries.append({
                    "timestamp": timestamp,
                    "content": entry_content[:200],  # Keep it concise
                    "file": str(journal_file.relative_to(memory_bank_path))
                })
            except Exception:
                pass
    
    return journal_entries


def _analyze_current_situation(state_data: dict, progress_data: dict, journal_data: list) -> dict:
    """Analyze current situation from all available data."""
    
    current_epic = state_data.get('current_epic', 'epic-01')
    current_task = state_data.get('current_task', 'task-01')
    active_role = state_data.get('active_role', 'owner')
    status = state_data.get('status', 'not_started')
    
    # State summary
    if status == "not_started":
        state_summary = f"Component not started, needs initial planning and delegation"
    elif status == "in_progress" and active_role == "dev":
        state_summary = f"Development in progress on {current_epic}/{current_task}"
    elif status == "in_progress" and active_role == "qa":
        state_summary = f"QA testing in progress on {current_epic}/{current_task}"
    elif status == "completed":
        state_summary = f"Component completed, ready for final review"
    else:
        state_summary = f"Status: {status}, Active role: {active_role}"
    
    # Progress summary
    total_epics = len(progress_data["epics"])
    if total_epics > 0:
        epic_info = progress_data["epics"].get(current_epic, {})
        total_tasks = epic_info.get("total", 0)
        progress_summary = f"{current_epic} has {total_tasks} tasks, currently on {current_task}"
    else:
        progress_summary = "No implementation structure found - needs planning"
    
    # Recent activity from journal
    if journal_data:
        latest_entry = journal_data[0]
        recent_activity = f"Last activity: {latest_entry['content'][:100]}..."
    else:
        recent_activity = "No recent journal entries"
    
    # Check for blockers (simple heuristics)
    blockers = []
    if status == "in_progress" and len(journal_data) == 0:
        blockers.append("No recent activity - team may be blocked")
    
    return {
        "state_summary": state_summary,
        "progress_summary": progress_summary,
        "recent_activity": recent_activity,
        "blockers": ", ".join(blockers) if blockers else None
    }


def _determine_pm_continuation(state_data: dict, progress_data: dict, journal_data: list, situation: dict) -> dict:
    """Determine how PM should continue work."""
    
    current_epic = state_data.get('current_epic', 'epic-01')
    current_task = state_data.get('current_task', 'task-01')
    active_role = state_data.get('active_role', 'owner')
    status = state_data.get('status', 'not_started')
    release = state_data.get('release', '')
    component = state_data.get('component', '')
    
    continuation = {
        "next_action": "",
        "reasoning": "",
        "command": "",
        "sub_agent_focus": None,
        "focus_switch": None,
        "continuity_steps": [],
        "return_context": None
    }
    
    if status == "not_started" and active_role == "owner":
        # PM needs to delegate
        continuation.update({
            "next_action": "Delegate to development team to begin work",
            "reasoning": "Component not started, PM should delegate to dev team",
            "command": f"turn-role('{release}', '{component}', 'dev')",
            "continuity_steps": [
                "1. Review component requirements and scope",
                "2. Delegate to dev team with clear task focus",
                "3. Monitor initial development progress",
                "4. Be ready to remove blockers"
            ]
        })
    
    elif status == "in_progress" and active_role == "dev":
        # Check if should continue monitoring or intervene
        if situation['blockers']:
            continuation.update({
                "next_action": "Intervene to resolve blockers for dev team",
                "reasoning": f"Dev team appears blocked: {situation['blockers']}",
                "command": f"get-progress('{release}', '{component}')",
                "sub_agent_focus": f"Support dev team working on {current_epic}/{current_task}",
                "continuity_steps": [
                    "1. Get detailed progress status",
                    "2. Identify specific blockers",
                    "3. Resolve blockers or escalate",
                    "4. Re-engage dev team with clear path forward"
                ]
            })
        else:
            continuation.update({
                "next_action": "Monitor dev team progress and provide support",
                "reasoning": "Development in progress, PM should monitor and support",
                "command": f"get-progress('{release}', '{component}')",
                "sub_agent_focus": f"Monitor dev team working on {current_epic}/{current_task}",
                "continuity_steps": [
                    "1. Review development progress",
                    "2. Check if dev team needs support",
                    "3. Prepare for QA handoff when ready",
                    "4. Plan next epic/task work"
                ],
                "return_context": f"When dev completes {current_task}, use next-task or next-epic to advance, then consider QA handoff"
            })
    
    elif status == "in_progress" and active_role == "qa":
        # Monitor QA or prepare for next work
        continuation.update({
            "next_action": "Monitor QA testing and prepare for completion",
            "reasoning": "QA testing in progress, PM should monitor and plan next steps",
            "command": f"get-progress('{release}', '{component}')",
            "sub_agent_focus": f"Monitor QA team testing {current_epic}/{current_task}",
            "continuity_steps": [
                "1. Review QA testing progress",
                "2. Address any issues found",
                "3. Plan next task/epic when testing passes",
                "4. Consider component completion or next work"
            ],
            "return_context": f"When QA completes {current_task}, use next-task or next-epic, or delegate back to dev for next work"
        })
    
    elif status == "completed":
        # Component complete, plan next
        continuation.update({
            "next_action": "Validate completion and plan next component",
            "reasoning": "Component marked complete, PM should validate and plan next work",
            "command": f"get-progress('{release}', '{component}')",
            "focus_switch": "Consider switching focus to next component in release",
            "continuity_steps": [
                "1. Validate all acceptance criteria met",
                "2. Review final deliverables",
                "3. Plan next component work",
                "4. Archive current component context"
            ]
        })
    
    else:
        # Unclear state - gather information
        continuation.update({
            "next_action": "Gather current status and clarify next steps",
            "reasoning": f"Unclear state: status={status}, role={active_role}",
            "command": f"get-progress('{release}', '{component}')",
            "continuity_steps": [
                "1. Get detailed component status",
                "2. Review recent activity and progress",
                "3. Clarify current work and ownership",
                "4. Re-establish clear direction"
            ]
        })
    
    return continuation


def _enhanced_pm_focus_analysis(memory_bank_path: Path, release: str, component: str, context_data: str, system_prompt: str, user_query: str) -> str:
    """Enhanced PM focus analysis with actionable instructions."""
    
    # Get REAL component state from state.yaml
    state_data = _ensure_component_state(memory_bank_path, release, component)
    
    # Extract project information
    project_name = _extract_project_name(context_data)
    component_purpose = _extract_component_purpose(context_data, component)
    current_state = _determine_component_state_from_data(state_data)
    
    # Determine immediate action based on real state
    immediate_action = _determine_immediate_action(current_state, release, component, state_data)
    
    # Generate focused PM instructions
    briefing_parts = []
    
    # Header
    briefing_parts.append(f"# PM Focus: {release} / {component}")
    
    # Current Situation
    briefing_parts.append("\n## Current Situation")
    briefing_parts.append(f"**Project**: {project_name}")
    briefing_parts.append(f"**Component Purpose**: {component_purpose}")
    briefing_parts.append(f"**Current State**: {current_state}")
    
    # Key context
    briefing_parts.append("\n## What You Need to Know")
    key_context = _extract_key_context(context_data, release, component)
    if key_context:
        briefing_parts.extend(key_context)
    else:
        briefing_parts.append("This component requires initial analysis and planning.")
    
    # Immediate action
    briefing_parts.append("\n## Immediate Action Required")
    briefing_parts.append(f"**Do This Now**: {immediate_action['action']}")
    briefing_parts.append(f"**Use This Command**: {immediate_action['command']}")
    briefing_parts.append(f"**Expected Outcome**: {immediate_action['outcome']}")
    
    # Context for decision
    briefing_parts.append("\n## Context for Decision")
    briefing_parts.append(f"**Why This Action**: {immediate_action['reasoning']}")
    briefing_parts.append(f"**What Comes Next**: {immediate_action['next_steps']}")
    briefing_parts.append(f"**Watch Out For**: {immediate_action['watch_out']}")
    
    # Dependencies
    dependencies = _extract_dependencies(context_data, component)
    briefing_parts.append("\n## Component Dependencies")
    if dependencies:
        briefing_parts.extend(dependencies)
    else:
        briefing_parts.append("No specific dependencies identified for this component.")
    
    return "\n".join(briefing_parts)


def _extract_project_name(context_data: str) -> str:
    """Extract project name from context."""
    lines = context_data.split('\n')
    for line in lines:
        if 'project:' in line.lower() or 'vision:' in line.lower():
            # Try to extract project name
            if '—' in line or '-' in line:
                parts = line.split('—' if '—' in line else '-')
                if len(parts) > 0:
                    return parts[0].strip().replace('*', '').replace('#', '')
    return "Memory-Bank project"


def _extract_component_purpose(context_data: str, component: str) -> str:
    """Extract component purpose from context."""
    lines = context_data.split('\n')
    component_lower = component.lower()
    
    for i, line in enumerate(lines):
        if component_lower in line.lower() and len(line) > 20:
            # Found a line about this component
            if '—' in line or ':' in line:
                return line.strip().replace('*', '').replace('#', '')
    
    return f"Component {component} in the system"


def _determine_component_state_from_data(state_data: dict) -> str:
    """Determine current state of component from real state.yaml data."""
    
    status = state_data.get("status", "not_started")
    active_role = state_data.get("active_role", "owner")
    current_epic = state_data.get("current_epic", "epic-01")
    current_task = state_data.get("current_task", "task-01")
    
    if status == "completed":
        return "Complete - ready for validation"
    elif status == "in_progress":
        if active_role == "dev":
            return f"In development - {current_epic}/{current_task}"
        elif active_role == "qa":
            return f"In testing - {current_epic}/{current_task}"
        elif active_role == "owner":
            return f"Awaiting owner input - {current_epic}/{current_task}"
        else:
            return f"In progress - {current_epic}/{current_task}"
    elif status == "blocked":
        return f"Blocked - {current_epic}/{current_task}"
    elif status == "not_started":
        return "Not started - needs planning"
    else:
        return f"Unknown state ({status}) - needs assessment"


def _determine_component_state(context_data: str, release: str, component: str) -> str:
    """Legacy function - kept for compatibility."""
    context_lower = context_data.lower()
    
    if 'completed' in context_lower or 'done' in context_lower:
        return "Complete - ready for validation"
    elif 'in progress' in context_lower or 'development' in context_lower:
        return "In active development"
    elif 'testing' in context_lower or 'qa' in context_lower:
        return "In testing/QA phase"
    elif 'planning' in context_lower or 'design' in context_lower:
        return "In planning/design phase"
    else:
        return "Initial state - needs assessment"


def _determine_immediate_action(state: str, release: str, component: str, state_data: dict = None) -> dict:
    """Determine immediate action based on component state."""
    
    # Use state_data for accurate analysis when available
    if state_data:
        status = state_data.get("status", "not_started")
        active_role = state_data.get("active_role", "owner")
        current_epic = state_data.get("current_epic")
        current_task = state_data.get("current_task")
        
        if status == "completed":
            return {
                "action": "Validate component completion and plan next component",
                "command": f"get-progress('{release}', '{component}')",
                "outcome": "Confirmation of completion status and readiness for next work",
                "reasoning": "Component is marked as completed in state.yaml",
                "next_steps": "If validated, plan next component or coordinate with QA for final sign-off",
                "watch_out": "Ensure all acceptance criteria are met before marking truly complete"
            }
        elif status == "in_progress" and active_role == "dev":
            return {
                "action": f"Monitor dev sub-agent work on {current_epic}/{current_task}",
                "command": f"get-progress('{release}', '{component}')",
                "outcome": "Current development status and identification of any blockers",
                "reasoning": f"Component delegated to dev team (active role: {active_role})",
                "next_steps": "Coordinate with dev sub-agent, resolve blockers, prepare for QA handoff when epic completes",
                "watch_out": "Monitor for scope creep or technical roadblocks",
                "sub_agent_action": f"Call dev sub-agent to work on {current_epic}/{current_task}"
            }
        elif status == "in_progress" and active_role == "qa":
            return {
                "action": f"Monitor QA sub-agent testing of {current_epic}/{current_task}",
                "command": f"get-progress('{release}', '{component}')",
                "outcome": "QA testing progress and any issues found",
                "reasoning": f"Component delegated to QA team (active role: {active_role})",
                "next_steps": "Coordinate with QA sub-agent, be ready to address any findings",
                "watch_out": "Be prepared for potential rework if issues are found",
                "sub_agent_action": f"Call qa sub-agent to test {current_epic}/{current_task}"
            }
        elif status == "not_started" or not current_epic:
            if active_role == "owner":
                return {
                    "action": "Define requirements and delegate to development team",
                    "command": f"turn-role('{release}', '{component}', 'dev')",
                    "outcome": "Development team will begin implementation work on epic-01/task-01",
                    "reasoning": "Component hasn't started yet - needs to begin development",
                    "next_steps": "Ensure dev team has clear requirements for first epic",
                    "watch_out": "Don't start development without clear requirements"
                }
            else:
                return {
                    "action": f"Component delegated to {active_role} but not started - monitor and support",
                    "command": f"get-progress('{release}', '{component}')",
                    "outcome": "Understanding of current delegation status and team needs",
                    "reasoning": f"Component delegated to {active_role} but status still 'not_started'",
                    "next_steps": f"Check if {active_role} team needs support to begin work",
                    "watch_out": "Team may need clearer requirements or unblocking"
                }
        else:
            return {
                "action": f"Review component status and provide guidance (status: {status}, role: {active_role})",
                "command": f"get-progress('{release}', '{component}')",
                "outcome": "Understanding of current component state and next actions",
                "reasoning": f"Component status unclear: {status}, active role: {active_role}",
                "next_steps": "Clarify component state and determine appropriate next actions",
                "watch_out": "Ensure clear ownership and progress tracking"
            }
    
    # Fallback to text-based analysis if no state_data
    if "Complete" in state:
        return {
            "action": "Validate component completion and plan next component",
            "command": f"get-progress('{release}', '{component}')",
            "outcome": "Confirmation of completion status and readiness for next work",
            "reasoning": "Component appears complete, need to verify before moving on",
            "next_steps": "If validated, plan next component or coordinate with QA for final sign-off",
            "watch_out": "Ensure all acceptance criteria are met before marking truly complete"
        }
    elif "development" in state:
        return {
            "action": "Check development progress and remove any blockers",
            "command": f"get-progress('{release}', '{component}')",
            "outcome": "Current development status and identification of any blockers",
            "reasoning": "Component is in active development, PM should monitor progress",
            "next_steps": "Support dev team, resolve blockers, prepare for QA handoff",
            "watch_out": "Monitor for scope creep or technical roadblocks"
        }
    elif "testing" in state:
        return {
            "action": "Coordinate with QA and monitor testing progress",
            "command": f"turn-role('{release}', '{component}', 'qa')",
            "outcome": "QA team will take ownership of component testing",
            "reasoning": "Component is ready for testing, QA should take the lead",
            "next_steps": "Monitor QA progress, be ready to address any findings",
            "watch_out": "Be prepared for potential rework if issues are found"
        }
    elif "planning" in state:
        return {
            "action": "Review requirements and delegate to development team",
            "command": f"turn-role('{release}', '{component}', 'dev')",
            "outcome": "Development team will begin implementation work",
            "reasoning": "Planning is done, ready to start development",
            "next_steps": "Monitor development startup, ensure clear requirements",
            "watch_out": "Ensure dev team has all needed requirements and dependencies"
        }
    else:
        return {
            "action": "Gather complete component context and requirements",
            "command": f"ask-memory-bank('requirements for {component} in {release}')",
            "outcome": "Understanding of component requirements and dependencies",
            "reasoning": "Component needs initial analysis before work can begin",
            "next_steps": "Define requirements, plan architecture, delegate to appropriate team",
            "watch_out": "Don't start development without clear requirements"
        }


def _generate_task_focus(memory_bank_path: Path, release: str, component: str, epic: str, task: str, role: str) -> dict:
    """Generate task-specific focus context for the assigned role."""
    
    # Look for task-specific documentation
    task_dir = memory_bank_path / "implementation" / "releases" / release / "components" / component / "epics" / epic / "tasks" / task
    epic_dir = memory_bank_path / "implementation" / "releases" / release / "components" / component / "epics" / epic
    component_dir = memory_bank_path / "implementation" / "releases" / release / "components" / component
    
    task_focus = {
        "epic": epic,
        "task": task,
        "role": role,
        "focus_summary": f"No specific task documentation found. Working on {epic}/{task}",
        "key_files": [],
        "next_actions": [],
        "acceptance_criteria": []
    }
    
    # Try to find task documentation
    if task_dir.exists():
        task_focus["task_exists"] = True
        task_focus["focus_summary"] = f"Task {task} in {epic} - check task documentation for specific requirements"
        
        # Look for common task files
        for filename in ["README.md", "requirements.md", "acceptance-criteria.md", "implementation.md"]:
            file_path = task_dir / filename
            if file_path.exists():
                task_focus["key_files"].append(str(file_path.relative_to(memory_bank_path)))
    
    elif epic_dir.exists():
        task_focus["task_exists"] = False  
        task_focus["focus_summary"] = f"Epic {epic} exists but task {task} not yet defined. May need to create task structure."
        
        # Look for epic-level documentation
        epic_readme = epic_dir / "README.md"
        if epic_readme.exists():
            task_focus["key_files"].append(str(epic_readme.relative_to(memory_bank_path)))
    
    else:
        task_focus["task_exists"] = False
        task_focus["focus_summary"] = f"Neither task nor epic structure exists. Component may need implementation planning."
        
        # Look for component-level documentation
        comp_readme = component_dir / "README.md"
        if comp_readme.exists():
            task_focus["key_files"].append(str(comp_readme.relative_to(memory_bank_path)))
    
    # Role-specific guidance
    if role == "dev":
        task_focus["next_actions"] = [
            f"Review task requirements in {epic}/{task}",
            "Check implementation documentation and acceptance criteria",
            "Begin development work",
            "Update progress using update-task-status when complete"
        ]
        if not task_focus["task_exists"]:
            task_focus["next_actions"] = [
                "Review component and epic requirements",
                "Create task structure if needed",
                "Define implementation approach",
                "Begin development work"
            ]
    
    elif role == "qa":
        task_focus["next_actions"] = [
            f"Review completed implementation for {epic}/{task}",
            "Check against acceptance criteria",
            "Run tests and validation",
            "Report issues or mark task complete"
        ]
        if not task_focus["task_exists"]:
            task_focus["next_actions"] = [
                "Review what was implemented",
                "Define test approach for the component",
                "Create test cases if needed",
                "Validate functionality"
            ]
    
    else:  # owner role
        task_focus["next_actions"] = [
            f"Monitor progress on {epic}/{task}",
            "Support active team (dev/qa)",
            "Remove blockers",
            "Plan next tasks/epics"
        ]
    
    return task_focus


def _generate_sub_agent_instructions(memory_bank_path: Path, release: str, component: str, epic: str, task: str, role: str, context: str) -> dict:
    """Generate comprehensive instructions for sub-agent work."""
    
    instructions = {
        "role": role,
        "focus_scope": f"{release}/{component}/{epic}/{task}",
        "context_summary": _extract_context_summary(context, release, component),
        "task_requirements": _extract_task_requirements(memory_bank_path, release, component, epic, task),
        "work_instructions": [],
        "success_criteria": [],
        "tools_to_use": []
    }
    
    if role == "dev":
        instructions["work_instructions"] = [
            f"Focus on implementing {epic}/{task} for component {component}",
            "Review component architecture and requirements",
            "Check existing implementation patterns in the project",
            "Implement according to acceptance criteria",
            "Use update-task-status to track progress",
            "When task complete, use next-task to move forward"
        ]
        instructions["success_criteria"] = [
            "Task implementation meets acceptance criteria",
            "Code follows project conventions",
            "Implementation is tested and working",
            "Documentation is updated if needed"
        ]
        instructions["tools_to_use"] = [
            "get-progress - to check current status",
            "update-task-status - to update task progress",
            "next-task - to move to next task when complete",
            "ask-memory-bank - to query requirements or context"
        ]
    
    elif role == "qa":
        instructions["work_instructions"] = [
            f"Test and validate {epic}/{task} implementation",
            "Review what was implemented against requirements",
            "Create test cases if they don't exist",
            "Run functional and integration tests",
            "Validate acceptance criteria are met",
            "Report issues or mark task complete"
        ]
        instructions["success_criteria"] = [
            "All acceptance criteria validated",
            "No critical bugs found",
            "Implementation works as specified",
            "Edge cases are handled properly"
        ]
        instructions["tools_to_use"] = [
            "get-progress - to check what was implemented",
            "update-task-status - to update testing status",
            "next-task - to move to next task when testing complete",
            "ask-memory-bank - to query requirements or test strategies"
        ]
    
    else:  # owner role
        instructions["work_instructions"] = [
            f"Oversee progress on {epic}/{task}",
            "Monitor team progress and remove blockers",
            "Ensure clear requirements and priorities",
            "Coordinate between teams when needed",
            "Plan next work when current task completes"
        ]
        instructions["success_criteria"] = [
            "Team has clear requirements and priorities",
            "No blockers preventing progress",
            "Work progresses according to plan",
            "Quality standards are maintained"
        ]
        instructions["tools_to_use"] = [
            "get-progress - to monitor team progress",
            "turn-role - to delegate to appropriate teams",
            "get-pm-focus - to get comprehensive status",
            "ask-memory-bank - to research requirements or decisions"
        ]
    
    return instructions


def _extract_context_summary(context: str, release: str, component: str) -> str:
    """Extract key context summary for sub-agent focus."""
    
    lines = context.split('\n')
    summary_parts = []
    
    # Look for key sections
    current_section = ""
    for line in lines:
        if line.startswith('# ') or line.startswith('## '):
            current_section = line.strip('# ')
        elif 'vision' in current_section.lower() and line.strip() and not line.startswith('---'):
            if len(' '.join(summary_parts)) < 300:  # Keep summary concise
                summary_parts.append(line.strip())
    
    if summary_parts:
        return ' '.join(summary_parts)
    else:
        return f"Working on {component} component in {release} release. See full context for details."


def _extract_task_requirements(memory_bank_path: Path, release: str, component: str, epic: str, task: str) -> list:
    """Extract specific requirements for the current task."""
    
    requirements = []
    
    # Check task-specific requirements
    task_dir = memory_bank_path / "implementation" / "releases" / release / "components" / component / "epics" / epic / "tasks" / task
    if task_dir.exists():
        req_file = task_dir / "requirements.md"
        if req_file.exists():
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Extract bullet points or numbered items
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('- ') or line.startswith('* ') or line.startswith('1. '):
                        requirements.append(line)
            except Exception:
                pass
    
    # Fallback to epic or component requirements
    if not requirements:
        epic_dir = memory_bank_path / "implementation" / "releases" / release / "components" / component / "epics" / epic
        if epic_dir.exists():
            epic_req = epic_dir / "README.md"
            if epic_req.exists():
                requirements.append(f"See epic requirements: {epic_req.relative_to(memory_bank_path)}")
        
        comp_dir = memory_bank_path / "implementation" / "releases" / release / "components" / component
        if comp_dir.exists():
            comp_req = comp_dir / "README.md"
            if comp_req.exists():
                requirements.append(f"See component requirements: {comp_req.relative_to(memory_bank_path)}")
    
    if not requirements:
        requirements.append(f"No specific requirements found for {epic}/{task}. Check component documentation.")
    
    return requirements


def _validate_release_component_structure(memory_bank_path: Path, release: str, component: str) -> dict:
    """Validate that release/component exists in Memory-Bank structure."""
    
    validation = {
        "valid": True,
        "errors": [],
        "suggestions": [],
        "available_releases": [],
        "available_components": []
    }
    
    # Check if releases exist
    releases_dir = memory_bank_path / "implementation" / "releases"
    if not releases_dir.exists():
        validation["valid"] = False
        validation["errors"].append("No releases directory found in Memory-Bank structure")
        return validation
    
    # Get available releases
    available_releases = []
    for item in releases_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            available_releases.append(item.name)
    
    validation["available_releases"] = sorted(available_releases)
    
    # Check if requested release exists
    release_dir = releases_dir / release
    if not release_dir.exists():
        validation["valid"] = False
        validation["errors"].append(f"Release '{release}' not found")
        
        # Suggest similar releases
        matches = get_close_matches(release, available_releases, n=3, cutoff=0.6)
        if matches:
            validation["suggestions"].append(f"Did you mean one of: {', '.join(matches)}?")
        else:
            validation["suggestions"].append(f"Available releases: {', '.join(available_releases)}")
        
        return validation
    
    # Check components in release
    components_dir = release_dir / "components"
    if not components_dir.exists():
        validation["valid"] = False
        validation["errors"].append(f"No components directory found in release '{release}'")
        return validation
    
    # Get available components
    available_components = []
    for item in components_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            available_components.append(item.name)
    
    validation["available_components"] = sorted(available_components)
    
    # Check if requested component exists
    component_dir = components_dir / component
    if not component_dir.exists():
        validation["valid"] = False
        validation["errors"].append(f"Component '{component}' not found in release '{release}'")
        
        # Suggest similar components
        matches = get_close_matches(component, available_components, n=3, cutoff=0.6)
        if matches:
            validation["suggestions"].append(f"Did you mean one of: {', '.join(matches)}?")
        else:
            validation["suggestions"].append(f"Available components in {release}: {', '.join(available_components)}")
    
    return validation


def _format_validation_error(validation: dict, release: str, component: str) -> str:
    """Format validation error message for user."""
    
    error_parts = [
        f"❌ Invalid release/component specification: {release}/{component}",
        ""
    ]
    
    # Add specific errors
    for error in validation["errors"]:
        error_parts.append(f"Error: {error}")
    
    error_parts.append("")
    
    # Add suggestions
    for suggestion in validation["suggestions"]:
        error_parts.append(f"💡 {suggestion}")
    
    error_parts.append("")
    
    # Add available options
    if validation["available_releases"]:
        error_parts.append("📁 Available releases:")
        for rel in validation["available_releases"]:
            error_parts.append(f"  - {rel}")
    
    if validation["available_components"]:
        error_parts.append(f"\n📦 Available components in {release}:")
        for comp in validation["available_components"]:
            error_parts.append(f"  - {comp}")
    
    error_parts.extend([
        "",
        "Please specify a valid release/component combination.",
        "Example: /run 01-pre-alpha 01-core-api"
    ])
    
    return "\n".join(error_parts)


def _focus_needs_rebuild(memory_bank_path: Path, release: str, component: str, focus_file: Path) -> bool:
    """Check if focus needs rebuilding based on state changes or staleness."""
    
    if not focus_file.exists():
        return True
    
    # CRITICAL: Check if current role in state matches focus role
    state_data = _ensure_component_state(memory_bank_path, release, component)
    current_role = state_data.get("active_role", "owner")
    
    # Read existing focus to check role
    if focus_file.exists():
        focus_content = focus_file.read_text()
        # Check if focus was created for different role
        if f"# {current_role.title()} Focus:" not in focus_content:
            return True  # Role mismatch - needs rebuild
    
    # Get focus datetime from YAML header
    focus_datetime = _extract_yaml_datetime(focus_file)
    if not focus_datetime:
        return True  # No datetime in header - needs rebuild
    
    # Check if focus is older than state.yaml 
    state_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "state.yaml"
    if state_file.exists() and state_file.stat().st_mtime > focus_datetime:
        return True
    
    # Check if focus is older than recent journal entries
    epics_dir = memory_bank_path / "progress" / "releases" / release / "components" / component / "epics"
    if epics_dir.exists():
        for epic_dir in epics_dir.iterdir():
            if epic_dir.is_dir():
                journal_file = epic_dir / "journal.md"
                if journal_file.exists() and journal_file.stat().st_mtime > focus_datetime:
                    return True
    
    # Check if focus is older than 1 hour (staleness check)
    import time
    if time.time() - focus_datetime > 3600:  # 1 hour
        return True
    
    return False


def _collect_all_component_states(memory_bank_path: Path) -> list:
    """Collect all component states across the entire project."""
    all_states = []
    
    progress_dir = memory_bank_path / "progress" / "releases"
    if not progress_dir.exists():
        return all_states
    
    for release_dir in progress_dir.iterdir():
        if release_dir.is_dir():
            release = release_dir.name
            components_dir = release_dir / "components"
            if components_dir.exists():
                for component_dir in components_dir.iterdir():
                    if component_dir.is_dir():
                        component = component_dir.name
                        state_file = component_dir / "state.yaml"
                        if state_file.exists():
                            state_data = _safe_load_state_yaml(state_file)
                            state_data.update({
                                'release': release,
                                'component': component
                            })
                            all_states.append(state_data)
    
    return all_states


def _get_all_state_files(memory_bank_path: Path) -> list:
    """Get list of all state.yaml files for rebuild trigger tracking."""
    state_files = []
    
    progress_dir = memory_bank_path / "progress" / "releases"
    if not progress_dir.exists():
        return state_files
    
    for release_dir in progress_dir.iterdir():
        if release_dir.is_dir():
            components_dir = release_dir / "components"
            if components_dir.exists():
                for component_dir in components_dir.iterdir():
                    if component_dir.is_dir():
                        state_file = component_dir / "state.yaml"
                        if state_file.exists():
                            rel_path = state_file.relative_to(memory_bank_path)
                            state_files.append(str(rel_path))
    
    return state_files


def _architecture_current_needs_rebuild(memory_bank_path: Path) -> bool:
    """Check if architecture/current.md needs rebuilding."""
    
    current_file = memory_bank_path / "architecture" / "current.md"
    
    if not current_file.exists():
        return True
    
    # Get current.md datetime from YAML header
    current_datetime = _extract_yaml_datetime(current_file)
    if not current_datetime:
        return True
    
    # Check ALL state.yaml files across project
    progress_dir = memory_bank_path / "progress" / "releases"
    if not progress_dir.exists():
        return False
    
    for release_dir in progress_dir.iterdir():
        if release_dir.is_dir():
            components_dir = release_dir / "components"
            if components_dir.exists():
                for component_dir in components_dir.iterdir():
                    if component_dir.is_dir():
                        state_file = component_dir / "state.yaml"
                        if state_file.exists():
                            if state_file.stat().st_mtime > current_datetime:
                                return True
    
    return False


def _rebuild_architecture_current(memory_bank_path: Path) -> None:
    """Rebuild architecture/current.md from all project states - with SDK fallback."""
    
    # Direct hardcoded implementation (no broken SDK)
    
    # Collect all component states
    all_states = _collect_all_component_states(memory_bank_path)
    
    # Create YAML header for architecture/current.md
    yaml_header = _create_yaml_header(
        focus_type="project",
        rebuild_triggers=_get_all_state_files(memory_bank_path),
        total_components=len(all_states)
    )
    
    # Generate project overview content
    current_content = [yaml_header]
    current_content.extend([
        "# Project Current Status",
        "",
        "## Release Overview"
    ])
    
    # Group by release
    releases = {}
    for state in all_states:
        release = state['release']
        if release not in releases:
            releases[release] = []
        releases[release].append(state)
    
    # Generate release summaries
    for release, components in releases.items():
        in_progress = [c for c in components if c.get('status') == 'in_progress']
        completed = [c for c in components if c.get('status') == 'completed']
        not_started = [c for c in components if c.get('status') == 'not_started']
        
        current_content.extend([
            f"### {release}",
            f"- **Total Components**: {len(components)}",
            f"- **In Progress**: {len(in_progress)}",
            f"- **Completed**: {len(completed)}",
            f"- **Not Started**: {len(not_started)}",
            ""
        ])
    
    # Active work section
    current_content.extend([
        "## Active Development",
        ""
    ])
    
    active_components = [s for s in all_states if s.get('status') == 'in_progress']
    if active_components:
        for comp in active_components:
            role = comp.get('active_role', 'owner')
            epic = comp.get('current_epic', 'unknown')
            task = comp.get('current_task', 'unknown') 
            current_content.append(f"- **{comp['release']}/{comp['component']}** ({role}): {epic}/{task}")
    else:
        current_content.append("- No active development currently")
    
    # Dependencies & Blockers section (basic implementation)
    current_content.extend([
        "",
        "## Dependencies & Blockers", 
        "- Cross-component dependencies: Review component architecture files",
        "- Active blockers: Check component journal entries for latest status"
    ])
    
    # Status summary
    total_components = len(all_states)
    if total_components > 0:
        progress_percent = int((len([s for s in all_states if s.get('status') == 'completed']) / total_components) * 100)
        current_content.extend([
            "",
            f"## Overall Progress",
            f"- **{progress_percent}%** complete ({len([s for s in all_states if s.get('status') == 'completed'])}/{total_components} components)",
            f"- **{len(active_components)}** components in active development"
        ])
    
    # Write to file
    current_file = memory_bank_path / "architecture" / "current.md"
    current_file.parent.mkdir(parents=True, exist_ok=True)
    current_file.write_text("\n".join(current_content))


def _pm_focus_needs_rebuild(memory_bank_path: Path, release: str, component: str) -> bool:
    """Check if PM focus needs rebuilding for specific component."""
    
    pm_focus_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "pm-focus.md"
    
    if not pm_focus_file.exists():
        return True
    
    # Get PM focus datetime from YAML header
    pm_focus_datetime = _extract_yaml_datetime(pm_focus_file)
    if not pm_focus_datetime:
        return True
    
    # Check triggers: state.yaml, journal entries, architecture/current.md
    triggers = [
        memory_bank_path / "progress" / "releases" / release / "components" / component / "state.yaml",
        memory_bank_path / "architecture" / "current.md"
    ]
    
    # Add all journal files for this component
    epics_dir = memory_bank_path / "progress" / "releases" / release / "components" / component / "epics"
    if epics_dir.exists():
        for epic_dir in epics_dir.iterdir():
            if epic_dir.is_dir():
                journal_file = epic_dir / "journal.md"
                if journal_file.exists():
                    triggers.append(journal_file)
    
    # Check if any trigger is newer than PM focus
    for trigger_file in triggers:
        if trigger_file.exists() and trigger_file.stat().st_mtime > pm_focus_datetime:
            return True
    
    return False


def _create_pm_focus(memory_bank_path: Path, release: str, component: str) -> None:
    """Create PM focus cache for specific component - with SDK fallback."""
    
    # Direct hardcoded implementation (no broken SDK)
    
    # Get current state for context
    state_data = _ensure_component_state(memory_bank_path, release, component)
    
    # Create YAML header for PM focus
    yaml_header = _create_yaml_header(
        focus_type="pm",
        release=release,
        component=component,
        rebuild_triggers=["state.yaml", "epic/journal.md", "architecture/current.md"]
    )
    
    focus_parts = [yaml_header]
    
    # Main PM focus header
    focus_parts.extend([
        f"# PM Focus: {release}/{component}",
        f"**Component**: {component}",
        f"**Release**: {release}",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ])
    
    # Current status section
    status = state_data.get('status', 'not_started')
    active_role = state_data.get('active_role', 'owner')
    current_epic = state_data.get('current_epic', 'epic-01')
    current_task = state_data.get('current_task', 'task-01')
    
    focus_parts.extend([
        "## Current Status",
        f"- **Status**: {status}",
        f"- **Active Role**: {active_role}",
        f"- **Current Work**: {current_epic}/{current_task}",
        ""
    ])
    
    # PM Analysis - reuse existing logic from get_pm_focus
    pm_analysis = _generate_pm_focus_analysis(memory_bank_path, release, component, state_data)
    focus_parts.extend([
        "## PM Analysis & Next Actions",
        pm_analysis,
        ""
    ])
    
    # Journal summary - recent entries
    journal_summary = _extract_recent_journal_summary(memory_bank_path, release, component)
    if journal_summary:
        focus_parts.extend([
            "## Recent Activity",
            journal_summary,
            ""
        ])
    
    # Context links
    focus_parts.extend([
        "## Context Links",
        f"- Architecture: See `/architecture/releases/{release}/components/{component}.md`",
        f"- Current Progress: Use `get-progress('{release}', '{component}')` for details",
        f"- Project Overview: See updated `/architecture/current.md`"
    ])
    
    # Write PM focus cache
    pm_focus_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "pm-focus.md"
    pm_focus_file.parent.mkdir(parents=True, exist_ok=True)
    pm_focus_file.write_text("\n".join(focus_parts))


def _generate_pm_focus_analysis(memory_bank_path: Path, release: str, component: str, state_data: dict) -> str:
    """Generate PM analysis section for focus (reuses existing logic)."""
    
    # This reuses the existing PM focus generation logic but formats it for cache
    status = state_data.get('status', 'not_started')
    active_role = state_data.get('active_role', 'owner')
    current_epic = state_data.get('current_epic', 'epic-01')
    current_task = state_data.get('current_task', 'task-01')
    
    analysis_parts = []
    
    if status == 'not_started':
        analysis_parts.extend([
            "**Recommended Action**: Analyze component readiness and delegate appropriately",
            f"**Next Steps**: Verify requirements clarity, then delegate to appropriate team",
            f"**Command**: `turn-role('{release}', '{component}', 'dev')` when requirements are clear"
        ])
    elif status == 'in_progress' and active_role == 'dev':
        analysis_parts.extend([
            f"**Recommended Action**: Monitor dev progress and remove blockers",
            "**Next Steps**: Support dev team, resolve blockers, prepare for QA handoff when ready",
            f"**Command**: `get-progress('{release}', '{component}')` for progress updates"
        ])
    elif status == 'in_progress' and active_role == 'qa':
        analysis_parts.extend([
            f"**Recommended Action**: Monitor QA progress and address findings",
            "**Next Steps**: Support QA team, resolve any issues found, prepare for completion",
            f"**Command**: `get-progress('{release}', '{component}')` for testing updates"
        ])
    elif status == 'completed':
        analysis_parts.extend([
            "**Recommended Action**: Validate completion and plan next component",
            "**Next Steps**: Final review and move to next component work",
            f"**Command**: `get-progress('{release}', '{component}')` to validate"
        ])
    else:
        analysis_parts.extend([
            f"**Status**: {status} (role: {active_role})",
            "**Recommended Action**: Clarify current state and next steps",
            f"**Command**: `get-progress('{release}', '{component}')` for clarity"
        ])
    
    return "\n".join(f"- {part}" for part in analysis_parts)


def _extract_recent_journal_summary(memory_bank_path: Path, release: str, component: str) -> str:
    """Extract recent journal entries for PM focus."""
    
    journal_parts = []
    
    # Check epic journals for recent activity
    epics_dir = memory_bank_path / "progress" / "releases" / release / "components" / component / "epics"
    if epics_dir.exists():
        for epic_dir in epics_dir.iterdir():
            if epic_dir.is_dir():
                journal_file = epic_dir / "journal.md"
                if journal_file.exists():
                    # Get last few entries (simple implementation)
                    journal_content = journal_file.read_text()
                    lines = journal_content.split('\n')
                    recent_lines = [line for line in lines[-10:] if line.strip()]  # Last 10 non-empty lines
                    if recent_lines:
                        journal_parts.extend([
                            f"### {epic_dir.name}",
                            *recent_lines[-5:],  # Last 5 lines
                            ""
                        ])
    
    return "\n".join(journal_parts) if journal_parts else "No recent journal activity"


def _create_role_focus(memory_bank_path: Path, release: str, component: str, epic: str, task: str, role: str) -> None:
    """Create focused context for specific role on task - with SDK fallback."""
    
    # Direct hardcoded implementation (improved version)
    
    # Create YAML header for agent focus
    yaml_header = _create_yaml_header(
        focus_type="agent",
        role=role,
        release=release,
        component=component,
        epic=epic,
        task=task,
        rebuild_triggers=["state.yaml", "epic/journal.md"]
    )
    
    focus_parts = [yaml_header]
    
    # Main header
    focus_parts.append(f"# {role.title()} Focus: {release}/{component}/{epic}/{task}")
    focus_parts.append(f"**Role**: {role}")
    focus_parts.append(f"**Focus**: {epic}/{task}")
    focus_parts.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Basic Project Context (product - related only)
    project_context = _extract_project_context(memory_bank_path, component, epic, task)
    if project_context:
        focus_parts.append("\n## Project Context")
        focus_parts.append(project_context)
    
    # 2. Release Context (FULL)
    release_file = memory_bank_path / "product" / "releases" / f"{release}.md"
    if release_file.exists():
        try:
            with open(release_file, 'r', encoding='utf-8') as f:
                release_content = f.read()
            focus_parts.append("\n## Architecture Context")
            focus_parts.append("**Release Specification**:")
            focus_parts.append(release_content)
        except Exception:
            focus_parts.append("\n## Architecture Context")
            focus_parts.append("**Release Specification**: [Error reading file]")
    
    # 3. Component Architecture (SDK filtered)
    arch_context = _extract_architecture_context(memory_bank_path, release, component, epic, task)
    if arch_context:
        focus_parts.append(arch_context)
    
    # 4. Component Implementation Context (brief)
    impl_context = _extract_implementation_context(memory_bank_path, release, component)
    if impl_context:
        focus_parts.append("\n## Implementation Context")
        focus_parts.append(impl_context)
    
    # 5. Standards Context (smart extraction based on task context)
    standards_context = _smart_extract_standards(memory_bank_path, role, epic, task)
    if standards_context:
        focus_parts.append("\n## Standards and Guidelines")
        focus_parts.append(standards_context)
    
    # 6. Epic Context (FULL - not distilled)
    epic_full = _get_full_epic_content(memory_bank_path, release, component, epic, role)
    if epic_full:
        focus_parts.append("\n## Epic Overview (Full)")
        focus_parts.append(epic_full)
    
    # 7. Task Context (FULL - not distilled)
    task_full = _get_full_task_content(memory_bank_path, release, component, epic, task, role)
    if task_full:
        focus_parts.append("\n## Current Task (Full)")
        focus_parts.append(task_full)
    
    # 8. Journal Context (related and chronologic only)
    journal_context = _extract_journal_context(memory_bank_path, release, component, epic, task)
    if journal_context:
        focus_parts.append("\n## Recent Progress")
        focus_parts.append(journal_context)
    
    # Role-specific instructions
    role_instructions = _get_role_instructions(role, epic, task)
    focus_parts.append(f"\n## {role.title()} Instructions")
    focus_parts.append(role_instructions)
    
    # Save focus
    focus_content = "\n".join(focus_parts)
    focus_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "current-focus.md"
    focus_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(focus_file, 'w', encoding='utf-8') as f:
        f.write(focus_content)


def _extract_implementation_context(memory_bank_path: Path, release: str, component: str) -> str:
    """Extract brief implementation context for the component."""
    
    impl_file = memory_bank_path / "implementation" / "releases" / release / "components" / f"{component}.md"
    
    if not impl_file.exists():
        return ""
    
    try:
        content = impl_file.read_text()
        # Get first meaningful section only (brief overview)
        lines = content.split('\n')
        result_lines = []
        line_count = 0
        
        for line in lines:
            # Skip YAML frontmatter
            if line.startswith('---'):
                continue
            
            # Add non-empty lines
            if line.strip():
                result_lines.append(line)
                line_count += 1
                
            # Stop after ~20 meaningful lines
            if line_count > 20:
                break
        
        if result_lines:
            return '\n'.join(result_lines) + "\n\n*[See full implementation details in epic/task sections below]*"
        else:
            return ""
    except Exception:
        return ""


def _smart_extract_standards(memory_bank_path: Path, role: str, epic: str, task: str) -> str:
    """Smart extraction of standards based on role and task context."""
    
    if role == "dev":
        standards_file = memory_bank_path / "architecture" / "tech-context" / "code-standards.md"
        standards_type = "code"
    elif role == "qa":
        standards_file = memory_bank_path / "architecture" / "tech-context" / "testing-standards.md"
        standards_type = "testing"
    else:
        return ""  # PM doesn't need standards
    
    if not standards_file.exists():
        return f"No {standards_type} standards available"
    
    try:
        # Try SDK extraction first (only works in Claude Code environment)
        prompt_file = memory_bank_path / "templates" / "mcp-prompts" / "extract_standards_context.md"
        
        if prompt_file.exists():
            prompt_template = prompt_file.read_text()
            prompt = prompt_template.format(
                standards_type=standards_type,
                standards_type_title=standards_type.title(),
                epic=epic,
                task=task
            )
            prompt += f"\n\nThe {standards_type} standards file is located at: {standards_file}"
            
            # Task tool only available in Claude Code, not MCP
            result = Task(
                description=f"Extract {standards_type} standards for {epic}/{task}",
                prompt=prompt,
                subagent_type="general-purpose"
            )
            
            if result and len(result.strip()) < 3000:
                return result.strip()
        
    except:
        pass  # Expected in MCP environment
    
    # Smart fallback - analyze document and extract relevant sections
    try:
        content = standards_file.read_text()
        return _smart_analyze_and_extract(content, epic, task, standards_type)
    except Exception as e:
        return f"Error reading {standards_type} standards: {e}"


def _smart_analyze_and_extract(content: str, epic: str, task: str, doc_type: str) -> str:
    """Smart content extraction based on document structure and task context."""
    
    # Parse document structure
    sections = _parse_document_sections(content)
    
    # Determine relevant sections based on task context
    task_context = f"{epic} {task}".lower()
    relevant_sections = []
    
    # Always include core sections
    core_keywords = {
        "code": ["error handling", "security", "core philosophy", "important note"],
        "testing": ["test strategy", "quality gates", "core principles"]
    }
    
    # Task-specific keywords
    context_keywords = []
    if any(word in task_context for word in ["docker", "localstack", "aws", "cognito", "service", "external"]):
        context_keywords.extend(["external service", "configuration", "integration", "aws", "docker"])
    if any(word in task_context for word in ["api", "fastapi", "web", "endpoint", "rest"]):
        context_keywords.extend(["api", "web framework", "fastapi", "endpoint", "rest"])
    if any(word in task_context for word in ["database", "db", "sql", "postgres", "migration"]):
        context_keywords.extend(["database", "migration", "sql", "postgres", "state management"])
    if any(word in task_context for word in ["test", "testing", "pytest", "unit", "integration"]):
        context_keywords.extend(["testing", "pytest", "unit test", "integration test"])
    
    # Find relevant sections
    for section_title, section_content in sections.items():
        section_lower = section_title.lower()
        
        # Check if section is core
        if doc_type in core_keywords:
            if any(keyword in section_lower for keyword in core_keywords[doc_type]):
                relevant_sections.append((section_title, section_content, "core"))
                continue
        
        # Check if section matches context
        if any(keyword in section_lower for keyword in context_keywords):
            relevant_sections.append((section_title, section_content, "context"))
    
    # Build result
    result_parts = []
    
    # Add core sections first
    for title, content, relevance in relevant_sections:
        if relevance == "core":
            result_parts.append(f"### {title}")
            # Limit content size
            if len(content) > 800:
                content = content[:800] + "..."
            result_parts.append(content)
    
    # Add context-specific sections
    for title, content, relevance in relevant_sections:
        if relevance == "context":
            result_parts.append(f"### {title}")
            # Limit content size
            if len(content) > 600:
                content = content[:600] + "..."
            result_parts.append(content)
    
    # If no specific sections found, return first important parts
    if not result_parts and sections:
        for i, (title, content) in enumerate(list(sections.items())[:3]):
            result_parts.append(f"### {title}")
            if len(content) > 500:
                content = content[:500] + "..."
            result_parts.append(content)
    
    result = "\n\n".join(result_parts) if result_parts else "No relevant standards identified"
    
    # Final size limit
    if len(result) > 3000:
        result = result[:3000] + "\n\n*[Additional standards available in full documentation]*"
    
    return result


def _parse_document_sections(content: str) -> dict:
    """Parse markdown document into sections."""
    sections = {}
    current_section = None
    current_content = []
    
    lines = content.split('\n')
    
    for line in lines:
        # Check for section header (## or ###)
        if line.startswith('## '):
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            # Start new section
            current_section = line[3:].strip()
            current_content = []
        elif line.startswith('### ') and current_section:
            # Subsection - include in current section
            current_content.append(line)
        elif current_section:
            # Add content to current section
            current_content.append(line)
    
    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections


def _get_full_epic_content(memory_bank_path: Path, release: str, component: str, epic: str, role: str) -> str:
    """Get FULL epic content - not distilled."""
    
    content_parts = []
    
    # Main epic overview (index.md in implementation)
    epic_index_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "epics" / epic / "index.md"
    if epic_index_file.exists():
        try:
            content = epic_index_file.read_text()
            # Skip YAML frontmatter
            lines = content.split('\n')
            start_idx = 0
            if lines[0].startswith('---'):
                for i in range(1, len(lines)):
                    if lines[i].startswith('---'):
                        start_idx = i + 1
                        break
            
            epic_content = '\n'.join(lines[start_idx:])
            content_parts.append("**Epic Overview**:")
            content_parts.append(epic_content)
        except Exception as e:
            content_parts.append(f"Error reading epic index: {e}")
    
    # Role-specific epic content (implementation perspective)
    role_epic_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "epics" / epic / f"{role}.md"
    if role_epic_file.exists():
        try:
            content = role_epic_file.read_text()
            # Skip YAML frontmatter
            lines = content.split('\n')
            start_idx = 0
            if lines[0].startswith('---'):
                for i in range(1, len(lines)):
                    if lines[i].startswith('---'):
                        start_idx = i + 1
                        break
            
            role_content = '\n'.join(lines[start_idx:])
            content_parts.append(f"\n**Epic {role.title()} Instructions**:")
            content_parts.append(role_content)
        except Exception as e:
            content_parts.append(f"Error reading role epic: {e}")
    
    return '\n'.join(content_parts) if content_parts else ""


def _get_full_task_content(memory_bank_path: Path, release: str, component: str, epic: str, task: str, role: str) -> str:
    """Get FULL task content - not distilled."""
    
    content_parts = []
    
    # Role-specific task content (main content)
    task_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "epics" / epic / "tasks" / task / f"{role}.md"
    if task_file.exists():
        try:
            content = task_file.read_text()
            # Skip YAML frontmatter
            lines = content.split('\n')
            start_idx = 0
            if lines[0].startswith('---'):
                for i in range(1, len(lines)):
                    if lines[i].startswith('---'):
                        start_idx = i + 1
                        break
            
            task_content = '\n'.join(lines[start_idx:])
            content_parts.append(f"**Task {role.title()} Instructions**:")
            content_parts.append(task_content)
        except Exception as e:
            content_parts.append(f"Error reading task: {e}")
    
    # General task description if exists
    general_task_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "epics" / epic / "tasks" / f"{task}.md"
    if general_task_file.exists() and general_task_file != task_file:
        try:
            content = general_task_file.read_text()
            # Skip YAML frontmatter
            lines = content.split('\n')
            start_idx = 0
            if lines[0].startswith('---'):
                for i in range(1, len(lines)):
                    if lines[i].startswith('---'):
                        start_idx = i + 1
                        break
            
            general_content = '\n'.join(lines[start_idx:])
            content_parts.append("\n**Task General Description**:")
            content_parts.append(general_content)
        except Exception as e:
            content_parts.append(f"Error reading general task: {e}")
    
    return '\n'.join(content_parts) if content_parts else ""




def _extract_epic_context(memory_bank_path: Path, release: str, component: str, epic: str, role: str) -> str:
    """Extract epic context with role perspective."""
    
    context_parts = []
    
    # Epic overview
    epic_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "epics" / epic / "index.md"
    if epic_file.exists():
        try:
            with open(epic_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            context_parts.append("**Epic Overview**:")
            # Extract COMPLETE content (skip yaml frontmatter)
            lines = content.split('\n')
            
            # Find the end of YAML frontmatter
            start_idx = 0
            if lines[0].startswith('---'):
                # Look for the closing ---
                for i in range(1, len(lines)):
                    if lines[i].startswith('---'):
                        start_idx = i + 1
                        break
            
            # Add all content after YAML frontmatter
            for line in lines[start_idx:]:
                context_parts.append(line)
        except Exception:
            pass
    
    # Role-specific epic context
    role_epic_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "epics" / epic / f"{role}.md"
    if role_epic_file.exists():
        try:
            with open(role_epic_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            context_parts.append(f"\n**Epic {role.title()} Context**:")
            lines = content.split('\n')
            # Get COMPLETE content, skip yaml
            content_lines = [line for line in lines if not line.startswith('---')]
            context_parts.extend(content_lines)
        except Exception:
            pass
    
    return '\n'.join(context_parts) if context_parts else ""


def _extract_task_context(memory_bank_path: Path, release: str, component: str, epic: str, task: str, role: str) -> str:
    """Extract main task context and explanation."""
    
    context_parts = []
    
    # Role-specific task context
    task_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "epics" / epic / "tasks" / task / f"{role}.md"
    if task_file.exists():
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            context_parts.append(f"**Task {role.title()} Context**:")
            # This is the main context - include more detail
            lines = content.split('\n')
            content_lines = [line for line in lines if not line.startswith('---')]
            context_parts.extend(content_lines)
        except Exception:
            pass
    
    return '\n'.join(context_parts) if context_parts else ""


def _extract_journal_context(memory_bank_path: Path, release: str, component: str, epic: str, task: str) -> str:
    """Extract related chronological journal entries."""
    
    context_parts = []
    
    # Get recent journal entries for this component
    journal_dir = memory_bank_path / "progress" / "releases" / release / "components" / component
    if journal_dir.exists():
        journal_files = list(journal_dir.glob("journal-*.md"))
        journal_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for journal_file in journal_files[:3]:  # Last 3 entries
            try:
                with open(journal_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if related to current epic/task
                if epic in content or task in content:
                    timestamp = journal_file.stem.replace('journal-', '')
                    context_parts.append(f"**{timestamp}**:")
                    # Extract content after yaml frontmatter
                    lines = content.split('\n')
                    content_started = False
                    for line in lines:
                        if line.startswith('---') and content_started:
                            break
                        if line.startswith('---'):
                            content_started = True
                            continue
                        if content_started and line.strip():
                            context_parts.append(line)
                    context_parts.append("")  # Spacing between entries
            except Exception:
                pass
    
    return '\n'.join(context_parts) if context_parts else ""


def _get_role_instructions(role: str, epic: str, task: str) -> str:
    """Get role-specific instructions for current task."""
    
    if role == "dev":
        return f"""**Development Focus**: {epic}/{task}

**Your Objectives**:
1. Understand task requirements and acceptance criteria
2. Review architectural constraints and dependencies
3. Implement functionality according to specifications
4. Write tests and ensure quality standards
5. Document technical decisions and progress

**Next Steps**:
1. Review task requirements and technical constraints
2. Implement the required functionality following architecture guidelines
3. Write and run tests to validate implementation
4. Update progress via `memory-bank - note-journal()`
5. Report completion to PM when implementation is ready for QA"""

    elif role == "qa":
        return f"""**Quality Assurance Focus**: {epic}/{task}

**Your Objectives**:
1. Review implemented functionality against requirements
2. Create and execute test cases
3. Validate acceptance criteria are met
4. Document any issues or defects found
5. Ensure quality standards before sign-off

**Next Steps**:
1. Use `memory-bank - get-progress()` to understand what was implemented
2. Design test strategy and test cases covering functional and edge cases
3. Execute testing and validation systematically
4. Update progress via `memory-bank - note-journal()`
5. Report test results and quality status to PM for sign-off"""

    else:  # owner
        return f"""**Owner Oversight**: {epic}/{task}

**Your Objectives**:
1. Monitor progress and remove blockers
2. Ensure alignment with business requirements
3. Coordinate between dev and QA teams
4. Make prioritization decisions
5. Plan next steps and roadmap

**Next Steps**:
1. Use `memory-bank - get-progress()` to check team progress
2. Support active team (dev/qa) with decisions
3. Plan next tasks/epics when current work completes"""


def _extract_key_context(context_data: str, release: str, component: str) -> list:
    """Extract key context information for PM decision making."""
    context = []
    lines = context_data.split('\n')
    
    for line in lines:
        line = line.strip()
        if any(keyword in line.lower() for keyword in ['requirement', 'dependency', 'blocker', 'deadline', 'priority']):
            if len(line) > 15:
                context.append(f"- {line}")
    
    return context[:3]  # Top 3 most relevant


def _extract_dependencies(context_data: str, component: str) -> list:
    """Extract component dependencies."""
    deps = []
    lines = context_data.split('\n')
    
    for line in lines:
        line = line.strip()
        if 'depends' in line.lower() or 'dependency' in line.lower():
            if len(line) > 15:
                deps.append(f"- {line}")
    
    return deps[:2]  # Top 2 dependencies


def _extract_project_info(context_data: str) -> list:
    """Extract project information for PM briefing."""
    info = []
    lines = context_data.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if any(marker in line.lower() for marker in ['project:', 'vision:', 'цель:', 'goal:']):
            info.append(f"- {line}")
        elif line.startswith('- ') and any(word in line.lower() for word in ['цель', 'vision', 'goal', 'audience']):
            info.append(line)
    
    return info[:3]  # Top 3 most relevant


def _extract_progress_info(context_data: str, release: str, component: str) -> list:
    """Extract progress information for PM briefing.""" 
    info = []
    lines = context_data.split('\n')
    
    for line in lines:
        line = line.strip()
        if any(marker in line.lower() for marker in ['status:', 'progress:', 'completed:', 'in progress:', 'pending:']):
            info.append(f"- {line}")
        elif any(word in line.lower() for word in ['завершено', 'completed', 'done', 'в работе', 'in progress']):
            info.append(f"- Status: {line}")
    
    if not info:
        info.append(f"- Status: Component {component} in release {release} requires status assessment")
    
    return info[:4]  # Top 4 most relevant


def _extract_architecture_info(context_data: str, component: str) -> list:
    """Extract architecture information for PM briefing."""
    info = []
    lines = context_data.split('\n')
    
    for line in lines:
        line = line.strip()
        if any(marker in line.lower() for marker in ['purpose:', 'цель:', 'architecture:', 'component:', 'dependencies:']):
            info.append(f"- {line}")
        elif component.lower() in line.lower() and len(line) > 20:
            info.append(f"- {line}")
    
    return info[:3]  # Top 3 most relevant


def _collect_comprehensive_context(memory_bank_path: Path, query: str) -> str:
    """Collect comprehensive context from all Memory-Bank sources."""
    context_parts = []
    query_lower = query.lower()
    
    # Priority sources based on query type
    sources = [
        ("product", ["vision.md", "releases"]),
        ("architecture", ["*.md", "releases", "tech-context"]),
        ("implementation", ["releases"]),
        ("progress", ["project-changelog", "releases"]),
        ("templates", ["*.md"])
    ]
    
    for source_type, patterns in sources:
        source_dir = memory_bank_path / source_type
        if not source_dir.exists():
            continue
        
        context_parts.append(f"\n=== {source_type.upper()} CONTENT ===")
        
        # Collect files from this source
        files_found = 0
        for pattern in patterns:
            if pattern == "releases":
                # Special handling for releases subdirectory
                releases_dir = source_dir / "releases"
                if releases_dir.exists():
                    for release_file in releases_dir.rglob("*.md"):
                        try:
                            with open(release_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Include if query keywords match or if it's a key file
                            if (query_lower in content.lower() or 
                                any(key in release_file.name.lower() for key in ['vision', 'overview', 'index'])):
                                
                                context_parts.append(f"\n--- {release_file.relative_to(memory_bank_path)} ---")
                                context_parts.append(content[:1000] + ("..." if len(content) > 1000 else ""))
                                files_found += 1
                                
                        except Exception:
                            continue
            else:
                # Regular file pattern search
                for file_path in source_dir.rglob(pattern):
                    if file_path.is_file() and file_path.suffix == '.md':
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Include if query keywords match or if it's a key file
                            if (query_lower in content.lower() or 
                                any(key in file_path.name.lower() for key in ['vision', 'overview', 'index'])):
                                
                                context_parts.append(f"\n--- {file_path.relative_to(memory_bank_path)} ---")
                                context_parts.append(content[:1000] + ("..." if len(content) > 1000 else ""))
                                files_found += 1
                                
                        except Exception:
                            continue
        
        if files_found == 0:
            # If no specific matches, include key overview files anyway
            key_files = ["vision.md", "overview.md", "index.md", "README.md"]
            for key_file in key_files:
                key_path = source_dir / key_file
                if key_path.exists():
                    try:
                        with open(key_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        context_parts.append(f"\n--- {key_path.relative_to(memory_bank_path)} ---")
                        context_parts.append(content[:800] + ("..." if len(content) > 800 else ""))
                        break
                    except Exception:
                        continue
    
    return "\n".join(context_parts)


def _enhanced_fallback_analysis(memory_bank_path: Path, query: str, context_data: str) -> str:
    """Enhanced analysis without async - smart rule-based processing."""
    query_lower = query.lower()
    
    # Detect query type
    query_type = "general"
    if any(word in query_lower for word in ['что такое', 'что это', 'define', 'vision', 'цель', 'аудитория']):
        query_type = "product"
    elif any(word in query_lower for word in ['архитектура', 'как работает', 'api', 'technical', 'система']):
        query_type = "technical"
    elif any(word in query_lower for word in ['статус', 'прогресс', 'что делается', 'progress', 'планы']):
        query_type = "progress"
    elif any(word in query_lower for word in ['как использовать', 'настроить', 'развернуть', 'how to', 'setup']):
        query_type = "howto"
    
    # Extract relevant sections from context
    sections = context_data.split("=== ")
    relevant_content = []
    
    for section in sections:
        if not section.strip():
            continue
            
        section_lower = section.lower()
        
        # Check if section is relevant to query (universal keywords)
        if (query_lower in section_lower or 
            any(keyword in section_lower for keyword in ['vision', 'overview', 'readme', 'introduction', 'summary'])):
            
            # Extract meaningful content
            lines = section.split('\n')
            content_lines = []
            
            for line in lines:
                if line.strip() and not line.startswith('---'):
                    content_lines.append(line.strip())
            
            if content_lines:
                relevant_content.append('\n'.join(content_lines[:20]))  # First 20 lines
    
    # Generate intelligent response based on query type and content
    if query_type == "product" and relevant_content:
        response = _generate_product_response(query, relevant_content)
    elif query_type == "technical" and relevant_content:
        response = _generate_technical_response(query, relevant_content)
    elif query_type == "progress" and relevant_content:
        response = _generate_progress_response(query, relevant_content)
    elif relevant_content:
        response = _generate_general_response(query, relevant_content)
    else:
        response = f"К сожалению, информация по запросу '{query}' не найдена в Memory-Bank."
    
    return response


def _generate_product_response(query: str, content_sections: list) -> str:
    """Generate universal product-focused response."""
    relevant_snippets = []
    query_words = query.lower().split()
    
    for section in content_sections:
        lines = section.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('---'):
                continue
                
            # Include lines that match query words or seem like definitions
            line_lower = line.lower()
            if (any(word in line_lower for word in query_words) or 
                ('—' in line and len(line) > 20) or
                line.startswith('- ') or line.startswith('* ')):
                relevant_snippets.append(line)
    
    if relevant_snippets:
        response = f"**Product Information:**\n\n"
        response += '\n'.join(relevant_snippets[:8])
        response += f"\n\n*Source: product documentation*"
    else:
        response = f"Product information available in Memory-Bank documentation."
    
    return response


def _generate_technical_response(query: str, content_sections: list) -> str:
    """Generate universal technical-focused response."""
    technical_info = []
    query_words = query.lower().split()
    
    for section in content_sections:
        lines = section.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('---'):
                continue
                
            line_lower = line.lower()
            if (any(word in line_lower for word in query_words) and
                any(tech_word in line_lower for tech_word in ['api', 'system', 'architecture', 'component', 'service'])):
                technical_info.append(line)
    
    if technical_info:
        response = f"**Technical Information:**\n\n"
        response += '\n'.join(technical_info[:6])
        response += f"\n\n*Source: architecture/implementation documentation*"
    else:
        response = f"Technical details available in architecture/ and implementation/ directories."
    
    return response


def _generate_progress_response(query: str, content_sections: list) -> str:
    """Generate universal progress-focused response."""
    progress_info = []
    query_words = query.lower().split()
    
    for section in content_sections:
        lines = section.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('---'):
                continue
                
            line_lower = line.lower()
            if (any(word in line_lower for word in query_words) and
                any(progress_word in line_lower for progress_word in ['status', 'progress', 'completed', 'working', 'development'])):
                progress_info.append(line)
    
    if progress_info:
        response = f"**Progress Information:**\n\n"
        response += '\n'.join(progress_info[:6])
        response += f"\n\n*Source: progress tracking documentation*"
    else:
        response = f"Progress information available in progress/ and journal directories."
    
    return response


def _generate_general_response(query: str, content_sections: list) -> str:
    """Generate universal general response."""
    relevant_snippets = []
    query_words = query.lower().split()
    
    for section in content_sections:
        lines = section.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('---'):
                continue
                
            if any(word in line.lower() for word in query_words) and len(line) > 15:
                relevant_snippets.append(line)
    
    if relevant_snippets:
        response = f"**Information found:**\n\n"
        response += '\n'.join(relevant_snippets[:6])
        response += f"\n\n*Source: Memory-Bank documentation*"
    else:
        response = f"No specific information found for '{query}' in current Memory-Bank."
    
    return response


def _fallback_simple_search(memory_bank_path: Path, query: str, error_msg: str) -> str:
    """Fallback simple search if agent fails."""
    try:
        results = []
        query_lower = query.lower()
        
        # Search all markdown files
        for md_file in memory_bank_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if query_lower in content.lower():
                    results.append({
                        "file": str(md_file.relative_to(memory_bank_path)),
                        "snippet": content[:300] + "..." if len(content) > 300 else content
                    })
            except Exception:
                continue
        
        return json.dumps({
            "query": query,
            "fallback_reason": f"Agent failed: {error_msg}",
            "results": results[:5],
            "total_found": len(results)
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Both agent and fallback search failed: {e}",
            "query": query
        })


def _distill_code_standards_OLD(content: str, epic: str = "", task: str = "") -> str:
    """DEPRECATED - replaced by smart extraction."""
    
    # Task-aware section selection
    essential_patterns = []
    
    # Always include these core sections
    core_patterns = [
        r"## Error Handling.*?(?=\n## [A-Z]|\Z)",
        r"## Security.*?(?=\n## [A-Z]|\Z)"
    ]
    
    # Add task-specific patterns based on keywords in epic/task
    task_context = f"{epic} {task}".lower()
    
    if any(word in task_context for word in ["docker", "localstack", "aws", "cognito", "service"]):
        essential_patterns.extend([
            r"## External Service Integration.*?(?=\n## [A-Z]|\Z)",
            r"## Configuration Management.*?(?=\n## [A-Z]|\Z)",
            r"## Technology Stack Reference.*?(?=\n## [A-Z]|\Z)"
        ])
    
    if any(word in task_context for word in ["api", "fastapi", "web", "endpoint"]):
        essential_patterns.extend([
            r"## API Design.*?(?=\n## [A-Z]|\Z)",
            r"## Web Framework.*?(?=\n## [A-Z]|\Z)"
        ])
    
    if any(word in task_context for word in ["test", "testing", "pytest"]):
        essential_patterns.extend([
            r"## Testing.*?(?=\n## [A-Z]|\Z)",
            r"## Testable.*?(?=\n## [A-Z]|\Z)"
        ])
    
    if any(word in task_context for word in ["database", "db", "sql", "postgres"]):
        essential_patterns.extend([
            r"## Database.*?(?=\n## [A-Z]|\Z)",
            r"## State Management.*?(?=\n## [A-Z]|\Z)"
        ])
    
    # Add core patterns
    essential_patterns.extend(core_patterns)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_patterns = []
    for pattern in essential_patterns:
        if pattern not in seen:
            unique_patterns.append(pattern)
            seen.add(pattern)
    
    distilled_parts = []
    
    for pattern in unique_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            # Clean up the match and limit length
            clean_match = match.strip()
            if len(clean_match) > 800:
                # Take first 800 chars and try to end at sentence
                truncated = clean_match[:800]
                last_period = truncated.rfind('.')
                if last_period > 600:  # If there's a sentence ending
                    clean_match = truncated[:last_period + 1] + "..."
                else:
                    clean_match = truncated + "..."
            distilled_parts.append(clean_match)
    
    # If no specific patterns found, extract first few headers
    if not distilled_parts:
        lines = content.split('\n')
        current_section = []
        section_count = 0
        
        for line in lines:
            if line.startswith('##') and section_count < 3:
                if current_section:
                    distilled_parts.append('\n'.join(current_section))
                current_section = [line]
                section_count += 1
            elif current_section and len('\n'.join(current_section)) < 600:
                current_section.append(line)
        
        if current_section:
            distilled_parts.append('\n'.join(current_section))
    
    result = '\n\n'.join(distilled_parts) if distilled_parts else "No key standards identified"
    
    # Final safety limit - max 2000 chars total
    if len(result) > 2000:
        result = result[:2000] + "...\n\n*[Additional standards available in full documentation]*"
    
    return result


def _distill_testing_standards_OLD(content: str, epic: str = "", task: str = "") -> str:
    """DEPRECATED - replaced by smart extraction."""
    
    # Task-aware section selection for testing
    essential_patterns = []
    
    # Always include these core testing sections
    core_patterns = [
        r"## Test Strategy.*?(?=##|\Z)",
        r"## Quality Gates.*?(?=##|\Z)"
    ]
    
    # Add task-specific patterns based on keywords in epic/task
    task_context = f"{epic} {task}".lower()
    
    if any(word in task_context for word in ["unit", "unittest", "component"]):
        essential_patterns.extend([
            r"## Unit Testing.*?(?=##|\Z)",
            r"## Test Types.*?(?=##|\Z)"
        ])
    
    if any(word in task_context for word in ["integration", "api", "service", "docker"]):
        essential_patterns.extend([
            r"## Integration Testing.*?(?=##|\Z)",
            r"## API Testing.*?(?=##|\Z)"
        ])
    
    if any(word in task_context for word in ["e2e", "end-to-end", "browser", "ui"]):
        essential_patterns.extend([
            r"## End-to-End.*?(?=##|\Z)",
            r"## UI Testing.*?(?=##|\Z)"
        ])
    
    if any(word in task_context for word in ["performance", "load", "stress"]):
        essential_patterns.extend([
            r"## Performance Testing.*?(?=##|\Z)",
            r"## Load Testing.*?(?=##|\Z)"
        ])
    
    # Add core patterns
    essential_patterns.extend(core_patterns)
    
    # Remove duplicates
    seen = set()
    unique_patterns = []
    for pattern in essential_patterns:
        if pattern not in seen:
            unique_patterns.append(pattern)
            seen.add(pattern)
    
    distilled_parts = []
    
    for pattern in unique_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            clean_match = match.strip()
            if len(clean_match) > 800:
                truncated = clean_match[:800]
                last_period = truncated.rfind('.')
                if last_period > 600:
                    clean_match = truncated[:last_period + 1] + "..."
                else:
                    clean_match = truncated + "..."
            distilled_parts.append(clean_match)
    
    # Fallback to first few sections if no patterns found
    if not distilled_parts:
        lines = content.split('\n')
        current_section = []
        section_count = 0
        
        for line in lines:
            if line.startswith('##') and section_count < 3:
                if current_section:
                    distilled_parts.append('\n'.join(current_section))
                current_section = [line]
                section_count += 1
            elif current_section and len('\n'.join(current_section)) < 600:
                current_section.append(line)
        
        if current_section:
            distilled_parts.append('\n'.join(current_section))
    
    result = '\n\n'.join(distilled_parts) if distilled_parts else "No key testing standards identified"
    
    # Final safety limit
    if len(result) > 2000:
        result = result[:2000] + "...\n\n*[Additional testing standards available in full documentation]*"
    
    return result


def _distill_project_vision_OLD(content: str, component: str) -> str:
    """DEPRECATED - replaced by smart extraction."""
    
    # Extract key sections from vision - non-overlapping patterns
    essential_patterns = [
        r"## 1\. Vision.*?(?=##|\Z)",
        r"## 2\. Почему сейчас.*?(?=##|\Z)",
        r"## 3\. Для кого.*?(?=##|\Z)",
        r"## 5\. Ценность.*?(?=##|\Z)"
    ]
    
    distilled_parts = []
    
    for pattern in essential_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            clean_match = match.strip()
            # Limit each section to avoid bloat
            if len(clean_match) > 500:
                truncated = clean_match[:500]
                last_period = truncated.rfind('.')
                if last_period > 300:
                    clean_match = truncated[:last_period + 1] + "..."
                else:
                    clean_match = truncated + "..."
            distilled_parts.append(clean_match)
    
    # If no patterns found, extract first meaningful paragraphs
    if not distilled_parts:
        lines = content.split('\n')
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('---') and not line.startswith('datetime'):
                meaningful_lines.append(line)
                if len('\n'.join(meaningful_lines)) > 800:
                    break
        
        if meaningful_lines:
            distilled_parts.append('\n'.join(meaningful_lines[:10]))  # First 10 meaningful lines
    
    result = '\n\n'.join(distilled_parts) if distilled_parts else "No key vision identified"
    
    # Final safety limit - max 1500 chars for vision
    if len(result) > 1500:
        result = result[:1500] + "...\n\n*[Complete vision available in product documentation]*"
    
    return result


# SDK-based intelligent extraction functions
def _extract_project_context(memory_bank_path: Path, component: str, epic: str, task: str) -> str:
    """Extract project vision context through Claude Code SDK filtering."""
    vision_file = memory_bank_path / "product" / "vision.md"
    
    if not vision_file.exists():
        return "No project vision available"
    
    try:
        # Load prompt template from Memory-Bank
        prompt_file = memory_bank_path / "templates" / "mcp-prompts" / "extract_project_context.md"
        
        if prompt_file.exists():
            # Read and customize prompt template
            prompt_template = prompt_file.read_text()
            
            # Replace placeholders with actual values
            prompt = prompt_template.format(
                component=component,
                epic=epic,
                task=task
            )
            
            # Add working directory context
            prompt += f"\n\nThe project vision file is located at: {vision_file}"
            
            # Call Task tool with general-purpose agent
            result = Task(
                description=f"Extract project context for {component}/{epic}/{task}",
                prompt=prompt,
                subagent_type="general-purpose"
            )
            
            # Extract result from Task response
            if result and len(result.strip()) < 3000:  # Reasonable size check
                return result.strip()
            else:
                # Fallback if result is too large or empty
                raise Exception("Task result too large or empty")
        else:
            # Fallback if no prompt template
            raise Exception("No prompt template found")
        
    except Exception as e:
        # Fallback to hardcoded distillation if SDK fails
        try:
            vision_content = vision_file.read_text()
            # Fallback to simple truncation
            return vision_content[:1500] + "..." if len(vision_content) > 1500 else vision_content
        except Exception:
            return "Project vision not available"


def _extract_architecture_context(memory_bank_path: Path, release: str, component: str, epic: str, task: str) -> str:
    """Extract architecture context through Claude Code SDK filtering."""
    arch_file = memory_bank_path / "architecture" / "releases" / release / "components" / f"{component}.md"
    
    if not arch_file.exists():
        return "No component architecture available"
    
    try:
        # Load prompt template from Memory-Bank
        prompt_file = memory_bank_path / "templates" / "mcp-prompts" / "extract_architecture_context.md"
        
        if prompt_file.exists():
            # Read and customize prompt template
            prompt_template = prompt_file.read_text()
            
            # Replace placeholders with actual values
            prompt = prompt_template.format(
                release=release,
                component=component,
                epic=epic,
                task=task
            )
            
            # Add working directory context
            prompt += f"\n\nThe component architecture file is located at: {arch_file}"
            
            # Call Task tool with general-purpose agent
            result = Task(
                description=f"Extract architecture context for {component}/{epic}/{task}",
                prompt=prompt,
                subagent_type="general-purpose"
            )
            
            # Extract result from Task response
            if result and len(result.strip()) < 3500:  # Reasonable size check
                return result.strip()
            else:
                # Fallback if result is too large or empty
                raise Exception("Task result too large or empty")
        else:
            # Fallback if no prompt template
            raise Exception("No prompt template found")
        
    except Exception as e:
        # Fallback to returning first reasonable chunk if SDK fails
        try:
            arch_content = arch_file.read_text()
            lines = arch_content.split('\n')
            key_lines = []
            for line in lines[:50]:  # First 50 lines as fallback
                if line.strip():
                    key_lines.append(line)
            
            fallback = '\n'.join(key_lines)
            if len(fallback) > 2000:
                fallback = fallback[:2000] + "..."
            
            return fallback
        except Exception:
            return "Component architecture not available"


def _extract_standards_context(memory_bank_path: Path, standards_type: str, epic: str, task: str) -> str:
    """Extract standards context through Claude Code SDK filtering."""
    standards_file = memory_bank_path / "architecture" / "tech-context" / f"{standards_type}-standards.md"
    
    if not standards_file.exists():
        return f"No {standards_type} standards available"
    
    try:
        # Load prompt template from Memory-Bank
        prompt_file = memory_bank_path / "templates" / "mcp-prompts" / "extract_standards_context.md"
        
        if prompt_file.exists():
            # Read and customize prompt template
            prompt_template = prompt_file.read_text()
            
            # Replace placeholders with actual values
            prompt = prompt_template.format(
                standards_type=standards_type,
                standards_type_title=standards_type.title(),
                epic=epic,
                task=task
            )
            
            # Add working directory context
            prompt += f"\n\nThe {standards_type} standards file is located at: {standards_file}"
            
            # Call Task tool with general-purpose agent
            result = Task(
                description=f"Extract {standards_type} standards for {epic}/{task}",
                prompt=prompt,
                subagent_type="general-purpose"
            )
            
            # Extract result from Task response
            if result and len(result.strip()) < 3000:  # Reasonable size check
                return result.strip()
            else:
                # Fallback if result is too large or empty
                raise Exception("Task result too large or empty")
        else:
            # Fallback if no prompt template
            raise Exception("No prompt template found")
        
    except Exception as e:
        # Fallback to existing distillation functions
        try:
            standards_content = standards_file.read_text()
            # Use smart extraction as fallback
            return _smart_analyze_and_extract(standards_content, epic, task, standards_type)
        except Exception:
            return f"{standards_type.title()} standards not available"


def _fallback_structure_validation(memory_bank_path: Path, release: str, component: str, file_path: str, purpose: str) -> str:
    """Fallback project structure validation without SDK."""
    
    try:
        # Basic validation based on common patterns
        validation_result = {
            "file_path": file_path,
            "purpose": purpose,
            "valid": True,
            "suggestions": [],
            "warnings": []
        }
        
        # Read project structure standards if available
        structure_file = memory_bank_path / "architecture" / "tech-context" / "project-structure.md"
        standards_available = structure_file.exists()
        
        # Basic structure validation
        if "/" in file_path:
            parts = file_path.split("/")
            root_dir = parts[0]
            
            # Check common structure patterns
            if root_dir in ["src", "tests", "scripts", "migrations"]:
                validation_result["suggestions"].append(f"✅ {root_dir}/ follows standard project structure")
                
                # Additional checks for specific directories
                if root_dir == "tests" and len(parts) > 1:
                    test_type = parts[1]
                    if test_type in ["unit", "integration", "e2e"]:
                        validation_result["suggestions"].append(f"✅ Test type '{test_type}' follows testing pyramid")
                    else:
                        validation_result["warnings"].append(f"⚠️  Consider organizing tests in unit/integration/e2e directories")
                
                if root_dir == "src" and len(parts) > 1:
                    if parts[1] in ["domain", "application", "infrastructure", "api"]:
                        validation_result["suggestions"].append(f"✅ '{parts[1]}' follows Clean Architecture layers")
            else:
                validation_result["warnings"].append(f"⚠️  '{root_dir}' is not a standard project directory")
        
        # File extension checks
        if file_path.endswith(".py"):
            if "test_" in file_path or file_path.endswith("_test.py"):
                if "tests/" not in file_path:
                    validation_result["warnings"].append("⚠️  Test files should be in tests/ directory")
            elif file_path.endswith("config.py"):
                validation_result["suggestions"].append("✅ Configuration file follows naming convention")
        
        # Purpose-based validation
        purpose_lower = purpose.lower()
        if "test" in purpose_lower and "tests/" not in file_path:
            validation_result["warnings"].append("⚠️  Test files should be placed in tests/ directory")
        
        if "api" in purpose_lower or "endpoint" in purpose_lower:
            if "api/" not in file_path and "src/" in file_path:
                validation_result["suggestions"].append("💡 Consider placing API endpoints in src/api/ directory")
        
        # Add context about available standards
        if standards_available:
            validation_result["note"] = f"Full project structure guidelines available in Memory-Bank: {structure_file.relative_to(memory_bank_path)}"
        
        return json.dumps(validation_result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Fallback validation failed: {e}",
            "file_path": file_path,
            "valid": False,
            "suggestion": "Basic validation unavailable - check Memory-Bank configuration"
        })


def run_mcp_server():
    """Run the MCP server with stdio transport."""
    mcp.run()  # Default transport is stdio