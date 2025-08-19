"""Data models for Memory-Bank module."""

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from pydantic import BaseModel, Field



class ProjectBinding(BaseModel):
    """Project binding to Memory-Bank."""
    
    memory_bank_name: str
    memory_bank_path: Path
    bound_at: datetime


class FeatureState(BaseModel):
    """Feature development state."""
    
    feature_name: str
    current_epic: Optional[str] = None
    current_task: Optional[str] = None
    active_role: str = "owner"  # owner/PM/dev/QA
    status: str = "planning"  # planning/development/validation/completed
    last_updated: datetime


class JournalEntry(BaseModel):
    """Development journal entry."""
    
    datetime: datetime
    role: str
    feature: str
    epic: Optional[str] = None
    task: Optional[str] = None
    content: str
    entry_type: str = "note"  # note/milestone