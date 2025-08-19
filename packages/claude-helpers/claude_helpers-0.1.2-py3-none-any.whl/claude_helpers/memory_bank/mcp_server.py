"""MCP server for Memory-Bank agent operations."""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastmcp import FastMCP

from .models import FeatureState, JournalEntry


# Create MCP server instance
mcp = FastMCP("Memory-Bank Agent Tools")


def _get_memory_bank_path() -> Optional[Path]:
    """Get Memory-Bank path from current working directory."""
    # Look for .helpers/memory_bank.json in current directory
    helpers_dir = Path.cwd() / ".helpers"
    binding_file = helpers_dir / "memory_bank.json"
    
    if binding_file.exists():
        try:
            with open(binding_file, 'r') as f:
                binding = json.load(f)
            return Path(binding['memory_bank_path'])
        except Exception:
            pass
    
    return None


@mcp.tool(name="current-state") 
def current_state(feature_name: str) -> str:
    """Get current workflow state for a feature.
    
    Args:
        feature_name: Name of the feature to check
        
    Returns:
        JSON string with current state including active role, epic, task and status
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    state_file = memory_bank_path / "work" / "Sessions" / feature_name / "state.yaml"
    
    if not state_file.exists():
        return json.dumps({
            "feature": feature_name,
            "status": "not_found",
            "message": f"No active session for feature '{feature_name}'"
        })
    
    try:
        with open(state_file, 'r') as f:
            state_data = yaml.safe_load(f)
        
        result = {
            "feature": feature_name,
            "active_role": state_data.get("active_role", "owner"),
            "current_epic": state_data.get("current_epic"),
            "current_task": state_data.get("current_task"),
            "status": state_data.get("status", "planning"),
            "last_updated": state_data.get("last_updated")
        }
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": f"Failed to read state: {e}"})


@mcp.tool(name="current-progress")
def current_progress() -> str:
    """Get current project progress overview.
    
    Returns:
        JSON string with progress summary including completion status and active work
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    progress_file = memory_bank_path / "work" / "progress.md"
    
    if not progress_file.exists():
        return json.dumps({
            "status": "no_progress",
            "message": "No progress tracking initialized"
        })
    
    try:
        content = progress_file.read_text()
        
        # Parse YAML header if exists
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                yaml_header = yaml.safe_load(parts[1])
                markdown_content = parts[2].strip()
            else:
                yaml_header = {}
                markdown_content = content
        else:
            yaml_header = {}
            markdown_content = content
        
        result = {
            "last_updated": yaml_header.get("datetime"),
            "summary": yaml_header.get("summary", ""),
            "content": markdown_content[:1000],  # First 1000 chars
            "full_path": str(progress_file)
        }
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": f"Failed to read progress: {e}"})


@mcp.tool(name="note-journal")
def note_journal(
    role: str,
    content: str,
    feature: str,
    epic: Optional[str] = None,
    task: Optional[str] = None
) -> str:
    """Add a journal entry for current session.
    
    Args:
        role: Agent role (owner/PM/dev/QA)
        content: Journal note content
        feature: Feature name
        epic: Optional epic ID
        task: Optional task ID
        
    Returns:
        JSON string with confirmation of journal entry creation
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    try:
        # Create session directory if needed
        session_dir = memory_bank_path / "work" / "Sessions" / feature / "Journal"
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create journal entry
        timestamp = datetime.now()
        filename = f"{timestamp.strftime('%Y%m%d-%H%M%S')}-note.md"
        journal_file = session_dir / filename
        
        # Build YAML header
        yaml_header = {
            "datetime": timestamp.isoformat(),
            "role": role,
            "feature": feature,
            "entry_type": "note"
        }
        
        if epic:
            yaml_header["epic"] = epic
        if task:
            yaml_header["task"] = task
        
        # Write journal file
        file_content = "---\n"
        file_content += yaml.dump(yaml_header, default_flow_style=False)
        file_content += "---\n\n"
        file_content += content
        
        journal_file.write_text(file_content)
        
        # Update state file
        state_file = memory_bank_path / "work" / "Sessions" / feature / "state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = yaml.safe_load(f) or {}
        else:
            state = {}
        
        state.update({
            "feature": feature,
            "active_role": role,
            "last_updated": timestamp.isoformat()
        })
        
        if epic:
            state["current_epic"] = epic
        if task:
            state["current_task"] = task
        
        with open(state_file, 'w') as f:
            yaml.dump(state, f, default_flow_style=False)
        
        result = {
            "status": "success",
            "journal_file": str(journal_file),
            "timestamp": timestamp.isoformat()
        }
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": f"Failed to create journal entry: {e}"})


@mcp.tool(name="note-milestone")
def note_milestone(
    feature: str,
    scope: str,
    report: str = ""
) -> str:
    """Record a milestone achievement.
    
    Args:
        feature: Feature name
        scope: Milestone scope (task/epic/feature)
        report: Optional validation report
        
    Returns:
        JSON string with confirmation of milestone recording
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    try:
        # Create session directory if needed
        session_dir = memory_bank_path / "work" / "Sessions" / feature / "Journal"
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create milestone entry
        timestamp = datetime.now()
        filename = f"{timestamp.strftime('%Y%m%d-%H%M%S')}-milestone.md"
        milestone_file = session_dir / filename
        
        # Build YAML header
        yaml_header = {
            "datetime": timestamp.isoformat(),
            "feature": feature,
            "scope": scope,
            "entry_type": "milestone"
        }
        
        # Write milestone file
        file_content = "---\n"
        file_content += yaml.dump(yaml_header, default_flow_style=False)
        file_content += "---\n\n"
        file_content += f"# Milestone: {scope} completed\n\n"
        
        if report:
            file_content += report
        
        milestone_file.write_text(file_content)
        
        # Update progress.md
        progress_file = memory_bank_path / "work" / "progress.md"
        
        if progress_file.exists():
            progress_content = progress_file.read_text()
        else:
            progress_content = f"""---
datetime: {timestamp.isoformat()}
---

# Project Progress

"""
        
        # Append milestone to progress
        progress_content += f"\n## {timestamp.strftime('%Y-%m-%d %H:%M')} - {feature}/{scope} completed\n"
        
        progress_file.write_text(progress_content)
        
        result = {
            "status": "success",
            "milestone_file": str(milestone_file),
            "scope": scope,
            "timestamp": timestamp.isoformat()
        }
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": f"Failed to create milestone: {e}"})


@mcp.tool(name="search")
def search(query: str) -> str:
    """Search Memory-Bank for relevant information.
    
    Args:
        query: Search query
        
    Returns:
        JSON string with search results from Memory-Bank
    """
    memory_bank_path = _get_memory_bank_path()
    if not memory_bank_path:
        return json.dumps({"error": "Memory-Bank not bound to current project"})
    
    # For now, return simple file-based search results
    try:
        results = []
        # Simple search through markdown files
        for md_file in memory_bank_path.glob("**/*.md"):
            try:
                content = md_file.read_text()
                if query.lower() in content.lower():
                    results.append({
                        "file": str(md_file.relative_to(memory_bank_path)),
                        "snippet": content[:200] + "..." if len(content) > 200 else content
                    })
            except Exception:
                continue
        
        return json.dumps({
            "status": "success",
            "results": results[:5]  # Limit to 5 results
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })


def run_memory_bank_mcp_server():
    """Run Memory-Bank MCP server with stdio transport."""
    # Debug: log startup info to stderr so it doesn't interfere with MCP protocol
    import sys
    print(f"Memory-Bank MCP starting from: {Path.cwd()}", file=sys.stderr)
    
    memory_bank_path = _get_memory_bank_path()
    if memory_bank_path:
        print(f"Found Memory-Bank at: {memory_bank_path}", file=sys.stderr)
    else:
        print("No Memory-Bank binding found in current directory", file=sys.stderr)
        # Don't exit - server should still work for tools that don't need Memory-Bank
    
    try:
        print("Starting FastMCP server...", file=sys.stderr)
        tools = mcp._tool_manager._tools
        print(f"Registered tools: {list(tools.keys())}", file=sys.stderr)
        sys.stderr.flush()  # Ensure all debug output is written before starting server
        
        # Use the same approach as HIL server
        mcp.run()  # Default transport is stdio
    except KeyboardInterrupt:
        print("MCP server interrupted", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"MCP server error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)