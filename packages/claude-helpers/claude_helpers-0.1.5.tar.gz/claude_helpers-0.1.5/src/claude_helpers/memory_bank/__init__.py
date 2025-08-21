"""Memory-Bank module for structured development workflows."""

import json
import os
from pathlib import Path
from typing import Optional

__version__ = "1.0.1"


def get_memory_bank_binding() -> Optional[dict]:
    """Get Memory-Bank binding information from current project.
    
    This function provides unified Memory-Bank detection across all components:
    - MCP servers
    - Skeleton generator
    - CLI commands
    
    Returns:
        Dict with memory_bank_name, memory_bank_path if bound, None otherwise
    """
    # Method 1: Environment variable (preferred for sub-agents and MCP servers)
    env_path = os.getenv('MEMORY_BANK_PATH')
    if env_path:
        path = Path(env_path)
        if path.exists() and _is_valid_memory_bank(path):
            return {
                "memory_bank_name": path.name,
                "memory_bank_path": path,
                "source": "environment"
            }
    
    # Method 2: Project binding via .helpers/memory_bank.json (primary method)
    helpers_dir = Path.cwd() / ".helpers"
    binding_file = helpers_dir / "memory_bank.json"
    
    if binding_file.exists():
        try:
            with open(binding_file, 'r') as f:
                binding = json.load(f)
            
            memory_bank_path = Path(binding['memory_bank_path'])
            if memory_bank_path.exists() and _is_valid_memory_bank(memory_bank_path):
                return {
                    "memory_bank_name": binding.get('memory_bank_name', memory_bank_path.name),
                    "memory_bank_path": memory_bank_path,
                    "source": "project_binding"
                }
        except Exception:
            pass
    
    # Method 3: Legacy .claude/memory-bank-binding.txt support
    claude_binding = Path.cwd() / ".claude" / "memory-bank-binding.txt"
    if claude_binding.exists():
        try:
            with open(claude_binding, 'r') as f:
                path = Path(f.read().strip())
                if path.exists() and _is_valid_memory_bank(path):
                    return {
                        "memory_bank_name": path.name,
                        "memory_bank_path": path,
                        "source": "legacy_binding"
                    }
        except Exception:
            pass
    
    return None


def get_memory_bank_path() -> Optional[Path]:
    """Get Memory-Bank path only (convenience function).
    
    Returns:
        Path to Memory-Bank root if bound, None otherwise
    """
    binding = get_memory_bank_binding()
    return binding['memory_bank_path'] if binding else None


def _is_valid_memory_bank(path: Path) -> bool:
    """Check if directory contains valid Memory-Bank structure."""
    # Memory-Bank directories should have these key folders
    memory_bank_indicators = ["product", "architecture", "implementation", "progress"]
    return any((path / indicator).exists() for indicator in memory_bank_indicators)