"""Cross-platform utilities for Claude Helpers."""

import platform
import shutil
from pathlib import Path
from typing import List


def get_platform() -> str:
    """Get current platform.
    
    Returns:
        'macos', 'linux', or 'unsupported'
    """
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    else:
        return "unsupported"


def get_config_dir() -> Path:
    """Get platform-appropriate config directory.
    
    Returns:
        Path to configuration directory
    """
    current_platform = get_platform()
    
    if current_platform == "macos":
        return Path.home() / "Library" / "Application Support" / "claude-helpers"
    elif current_platform == "linux":
        return Path.home() / ".config" / "claude-helpers"
    else:
        # Fallback for unsupported platforms
        return Path.home() / ".claude-helpers"


def get_dialog_tools() -> List[str]:
    """Get available dialog tools for current platform.
    
    Returns:
        List of available dialog tools in priority order
    """
    current_platform = get_platform()
    available_tools = []
    
    if current_platform == "macos":
        # macOS dialog tools in preference order
        if shutil.which("osascript"):
            available_tools.append("osascript")
    
    elif current_platform == "linux":
        # Linux dialog tools in preference order
        dialog_candidates = ["zenity", "kdialog", "dialog", "whiptail"]
        for tool in dialog_candidates:
            if shutil.which(tool):
                available_tools.append(tool)
    
    return available_tools