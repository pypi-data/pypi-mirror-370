"""Core HIL functions for MCP server integration."""

import json
import time
import os
from pathlib import Path
from typing import Optional


class HILError(Exception):
    """HIL operation error."""
    pass


def find_helpers_directory() -> Path:
    """Find .helpers directory in current working directory."""
    helpers_dir = Path.cwd() / ".helpers"
    if not helpers_dir.exists():
        raise HILError("Project not initialized. Run: claude-helpers init")
    return helpers_dir


def ask_human_hil(question: str, timeout: int = 300) -> str:
    """
    Ask a text question to human via HIL system.
    
    Args:
        question: The question to ask
        timeout: Maximum wait time in seconds
        
    Returns:
        Human's answer as string
        
    Raises:
        HILError: If HIL system is not available or timeout
    """
    helpers_dir = find_helpers_directory()
    
    # Create directories
    questions_dir = helpers_dir / "questions"
    answers_dir = helpers_dir / "answers"
    questions_dir.mkdir(exist_ok=True)
    answers_dir.mkdir(exist_ok=True)
    
    # Generate unique agent ID
    agent_id = f"mcp_{os.getpid()}_{int(time.time() * 1000000) % 1000000}"
    
    # Create question data
    question_data = {
        "type": "text",
        "agent_id": agent_id,
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "prompt": question,
        "timeout": timeout,
        "metadata": {
            "source": "mcp_server",
            "require_confirmation": True
        }
    }
    
    # Write question file
    question_file = questions_dir / f"{agent_id}.json"
    answer_file = answers_dir / f"{agent_id}.json"
    
    try:
        question_file.write_text(json.dumps(question_data, indent=2))
        
        # Wait for answer
        start_time = time.time()
        while not answer_file.exists():
            if time.time() - start_time > timeout:
                # Cleanup and raise error
                if question_file.exists():
                    question_file.unlink()
                raise HILError(f"Timeout: No response received within {timeout} seconds")
            
            time.sleep(0.5)
        
        # Read answer
        try:
            answer_data = json.loads(answer_file.read_text())
            answer_text = answer_data.get("answer", "")
        except json.JSONDecodeError:
            # Fallback to raw text
            answer_text = answer_file.read_text().strip()
        
        # Check for errors
        if answer_text.startswith("ERROR:"):
            raise HILError(answer_text)
        
        # Cleanup
        if question_file.exists():
            question_file.unlink()
        if answer_file.exists():
            answer_file.unlink()
            
        return answer_text
        
    except Exception as e:
        # Cleanup on any error
        if question_file.exists():
            question_file.unlink()
        if answer_file.exists():
            answer_file.unlink()
        
        if isinstance(e, HILError):
            raise
        else:
            raise HILError(f"HIL system error: {e}")


def voice_input_hil(prompt: str, duration: int = 30, timeout: int = 300) -> str:
    """
    Get voice input from human via HIL system.
    
    Args:
        prompt: The prompt for voice input
        duration: Maximum recording duration in seconds
        timeout: Maximum wait time in seconds
        
    Returns:
        Transcribed voice input as string
        
    Raises:
        HILError: If HIL system is not available or timeout
    """
    helpers_dir = find_helpers_directory()
    
    # Create directories
    questions_dir = helpers_dir / "questions"
    answers_dir = helpers_dir / "answers"
    questions_dir.mkdir(exist_ok=True)
    answers_dir.mkdir(exist_ok=True)
    
    # Generate unique agent ID
    agent_id = f"mcp_voice_{os.getpid()}_{int(time.time() * 1000000) % 1000000}"
    
    # Create question data
    question_data = {
        "type": "voice",
        "agent_id": agent_id,
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "prompt": prompt,
        "timeout": timeout,
        "metadata": {
            "source": "mcp_server",
            "max_duration": duration,
            "fallback_to_text": True,
            "require_confirmation": True
        }
    }
    
    # Write question file
    question_file = questions_dir / f"{agent_id}.json"
    answer_file = answers_dir / f"{agent_id}.json"
    
    try:
        question_file.write_text(json.dumps(question_data, indent=2))
        
        # Wait for answer
        start_time = time.time()
        while not answer_file.exists():
            if time.time() - start_time > timeout:
                # Cleanup and raise error
                if question_file.exists():
                    question_file.unlink()
                raise HILError(f"Timeout: No voice input received within {timeout} seconds")
            
            time.sleep(0.5)
        
        # Read answer
        try:
            answer_data = json.loads(answer_file.read_text())
            answer_text = answer_data.get("answer", "")
        except json.JSONDecodeError:
            # Fallback to raw text
            answer_text = answer_file.read_text().strip()
        
        # Check for errors
        if answer_text.startswith("ERROR:"):
            raise HILError(answer_text)
        
        # Cleanup
        if question_file.exists():
            question_file.unlink()
        if answer_file.exists():
            answer_file.unlink()
            
        return answer_text
        
    except Exception as e:
        # Cleanup on any error
        if question_file.exists():
            question_file.unlink()
        if answer_file.exists():
            answer_file.unlink()
        
        if isinstance(e, HILError):
            raise
        else:
            raise HILError(f"HIL voice system error: {e}")