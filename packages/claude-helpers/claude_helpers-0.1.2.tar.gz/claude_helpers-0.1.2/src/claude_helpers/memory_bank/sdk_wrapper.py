"""Memory-Bank SDK wrapper for Claude Code operations."""

import asyncio
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional
from ..config import get_global_config


class MemoryBankHelper:
    """Helper class for Memory-Bank operations using Claude Code SDK."""
    
    def __init__(self, memory_bank_path: Path):
        self.memory_bank_path = Path(memory_bank_path)
        self.config = get_global_config()
    
    async def validate_structure(self, validate_path: Path) -> str:
        """Validate Memory-Bank structure and content at specified path."""
        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
        
        if not self.config.use_plan_mode and not self.config.anthropic_api_key:
            return "Error: Claude API key not configured and plan mode disabled. Run: claude-helpers setup"
        
        # Collect validation context
        validation_context = self._collect_validation_context(validate_path)
        
        # Create system prompt for validation
        system_prompt = f"""You are a Memory-Bank Structure Validator for the System Architect Agent workflow. 

CRITICAL: Analyze the provided Memory-Bank structure and content for consistency, completeness, and compliance with standards.

## Memory-Bank Structure Requirements:
1. All .md files must start with YAML header containing 'datetime'
2. Directory structure must follow Memory-Bank patterns
3. Content must be consistent with parent context
4. Validation criteria must be measurable and clear
5. Cross-references between files must be valid

## Your Task:
Provide detailed validation report with:
- **Structure Compliance Status**: Pass/Fail with details
- **Missing or Malformed Files**: Specific files that need attention
- **Content Consistency Issues**: Cross-reference problems, context misalignment
- **YAML Header Validation**: Missing or invalid datetime headers
- **Recommendations for Fixes**: Actionable steps to resolve issues

## Context:
- Path being validated: {validate_path}
- Memory-Bank root: {self.memory_bank_path}
- Focus on structural integrity and documentation standards
"""

        user_query = f"""Validate this Memory-Bank structure and content:

{validation_context}

Provide comprehensive validation report with specific recommendations for any issues found."""

        try:
            # Create options based on authentication mode
            client_options = ClaudeCodeOptions(
                system_prompt=system_prompt,
                allowed_tools=["Read", "Glob", "Grep"],  # Tools for structure analysis
                max_turns=3
            )
            
            # In plan mode, don't set API key - use existing Claude Code auth
            if not self.config.use_plan_mode and self.config.anthropic_api_key:
                import os
                os.environ['ANTHROPIC_API_KEY'] = self.config.anthropic_api_key
            
            async with ClaudeSDKClient(options=client_options) as client:
                await client.query(user_query)
                
                # Collect streaming response
                report_parts = []
                async for message in client.receive_response():
                    if hasattr(message, 'content'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                report_parts.append(block.text)
                    
                    if type(message).__name__ == "ResultMessage":
                        full_report = ''.join(report_parts)
                        return f"Memory-Bank Validation Report:\n\n{full_report}"
                
                # Fallback if no ResultMessage
                return f"Memory-Bank Validation Report:\n\n{''.join(report_parts)}"
                
        except Exception as e:
            return f"Validation failed: {e}"
    
    async def rebuild_progress(self) -> str:
        """Rebuild and update project progress aggregation."""
        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
        
        if not self.config.use_plan_mode and not self.config.anthropic_api_key:
            return "Error: Claude API key not configured and plan mode disabled. Run: claude-helpers setup"
        
        # Collect progress data
        progress_data = self._collect_progress_data()
        
        system_prompt = f"""You are a Memory-Bank Progress Aggregator for the System Architect Agent workflow.

CRITICAL: Analyze session states, milestones, and work artifacts to rebuild comprehensive project progress summary.

## Your Tasks:
1. **Aggregate Completion Status** across all features/epics/tasks
2. **Identify Active Work** and current focus areas  
3. **Calculate Progress Metrics** and completion percentages
4. **Update Status Tracking** with current development state
5. **Ensure Consistency** between state files and milestone records

## Output Requirements:
Generate updated progress.md content with YAML header containing:
- **Overall Project Status**: Completion percentage and health
- **Feature-Level Breakdown**: Progress by feature with current state
- **Active Development Areas**: What's currently being worked on
- **Recent Achievements**: Latest milestones and completions
- **Next Priorities**: Upcoming work and blockers
- **Timeline Insights**: Progress velocity and projections

## Context:
Memory-Bank Path: {self.memory_bank_path}
Focus on factual progress aggregation from milestone data and session states.
"""

        user_query = f"""Rebuild progress aggregation for this Memory-Bank:

{progress_data}

Generate complete progress.md content with proper YAML header and comprehensive project status."""

        try:
            # Create options based on authentication mode
            client_options = ClaudeCodeOptions(
                system_prompt=system_prompt,
                allowed_tools=["Read", "Write", "Glob"],  # Tools for progress analysis
                max_turns=2
            )
            
            # In plan mode, don't set API key - use existing Claude Code auth
            if not self.config.use_plan_mode and self.config.anthropic_api_key:
                import os
                os.environ['ANTHROPIC_API_KEY'] = self.config.anthropic_api_key
            
            async with ClaudeSDKClient(options=client_options) as client:
                await client.query(user_query)
                
                # Collect streaming response
                progress_content = []
                async for message in client.receive_response():
                    if hasattr(message, 'content'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                progress_content.append(block.text)
                    
                    if type(message).__name__ == "ResultMessage":
                        full_content = ''.join(progress_content)
                        
                        # Update progress.md file
                        progress_file = self.memory_bank_path / "work" / "progress.md"
                        progress_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Ensure proper YAML header if not present
                        if not full_content.strip().startswith('---'):
                            timestamp = datetime.now()
                            full_content = f"""---
datetime: "{timestamp.isoformat()}"
type: "progress_summary" 
last_updated: "{timestamp.isoformat()}"
---

{full_content}
"""
                        
                        with open(progress_file, 'w') as f:
                            f.write(full_content)
                        
                        return f"Progress rebuilt and updated at: {progress_file}\n\nSummary:\n{full_content[:500]}..."
                
                # Fallback if no ResultMessage
                return f"Progress rebuild completed.\n\nContent:\n{''.join(progress_content)[:300]}..."
                
        except Exception as e:
            return f"Progress rebuild failed: {e}"
    
    async def rebuild_focus(self, release: str, component: str) -> str:
        """Rebuild current focus context for active release/component."""
        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
        
        if not self.config.use_plan_mode and not self.config.anthropic_api_key:
            return "Error: Claude API key not configured and plan mode disabled. Run: claude-helpers setup"
        
        # Collect focus data
        focus_data = self._collect_focus_data(release, component)
        
        component_text = f"release '{release}' component '{component}'"
        
        system_prompt = f"""You are a Memory-Bank Focus Rebuilder for the System Architect Agent workflow.

CRITICAL: Analyze current session states and recent activity to rebuild current-focus.md files for active features.

## Your Tasks:
1. **Analyze Session State** (current role, epic, task status)
2. **Review Recent Activity** (journal entries, milestones, decisions)
3. **Identify Active Context** (current priorities and focus areas)
4. **Update Focus Documents** with clear, actionable focus statements
5. **Ensure Alignment** between state.yaml and focus documentation

## Output Requirements:
Generate current-focus.md content with proper YAML header containing:
- **Current Work Focus**: What we're working on right now
- **Active Role Context**: Current agent role and responsibilities
- **Epic/Task Context**: Current epic and task being worked on
- **Key Decisions Made**: Recent important decisions and their rationale  
- **Current Constraints**: Blockers, dependencies, limitations
- **Next Steps**: Immediate priorities and action items
- **Context Links**: References to relevant design docs and requirements

## Target:
Rebuilding focus for {component_text} in Memory-Bank: {self.memory_bank_path}
"""

        user_query = f"""Rebuild focus context for {component_text} based on this session data:

{focus_data}

Generate updated current-focus.md content with clear focus statements and proper YAML headers."""

        try:
            # Create options based on authentication mode
            client_options = ClaudeCodeOptions(
                system_prompt=system_prompt,
                allowed_tools=["Read", "Write", "Glob"],  # Tools for focus analysis
                max_turns=2
            )
            
            # In plan mode, don't set API key - use existing Claude Code auth
            if not self.config.use_plan_mode and self.config.anthropic_api_key:
                import os
                os.environ['ANTHROPIC_API_KEY'] = self.config.anthropic_api_key
            
            async with ClaudeSDKClient(options=client_options) as client:
                await client.query(user_query)
                
                # Collect streaming response
                focus_content = []
                async for message in client.receive_response():
                    if hasattr(message, 'content'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                focus_content.append(block.text)
                    
                    if type(message).__name__ == "ResultMessage":
                        full_content = ''.join(focus_content)
                        
                        # Update focus files
                        updated_files = []
                        if feature:
                            # Update specific feature
                            focus_file = self.memory_bank_path / "work" / "Sessions" / feature / "current-focus.md"
                            if self._update_focus_file(focus_file, full_content):
                                updated_files.append(str(focus_file))
                        else:
                            # Update all active features based on content
                            sessions_dir = self.memory_bank_path / "work" / "Sessions"
                            if sessions_dir.exists():
                                for feature_dir in sessions_dir.iterdir():
                                    if feature_dir.is_dir():
                                        focus_file = feature_dir / "current-focus.md"
                                        if self._update_focus_file(focus_file, full_content):
                                            updated_files.append(str(focus_file))
                        
                        files_text = "\n".join(f"- {f}" for f in updated_files)
                        return f"Focus rebuilt for {len(updated_files)} features:\n{files_text}\n\nFocus Summary:\n{full_content[:300]}..."
                
                # Fallback if no ResultMessage
                return f"Focus rebuild completed.\n\nContent:\n{''.join(focus_content)[:300]}..."
                
        except Exception as e:
            return f"Focus rebuild failed: {e}"
    
    def _collect_validation_context(self, validate_path: Path) -> str:
        """Collect validation context from Memory-Bank structure."""
        context_parts = []
        
        try:
            # Add structure overview
            context_parts.append("=== DIRECTORY STRUCTURE ===")
            context_parts.append(self._get_directory_tree(validate_path))
            
            # Add file content samples
            context_parts.append("\n=== FILE CONTENT SAMPLES ===")
            
            for md_file in validate_path.rglob("*.md"):
                if md_file.stat().st_size < 5000:  # Only include small files
                    try:
                        with open(md_file, 'r') as f:
                            content = f.read()
                        context_parts.append(f"\n--- {md_file.relative_to(self.memory_bank_path)} ---")
                        context_parts.append(content[:1000] + ("..." if len(content) > 1000 else ""))
                    except Exception:
                        continue
            
            # Add YAML files
            for yaml_file in validate_path.rglob("*.yaml"):
                try:
                    with open(yaml_file, 'r') as f:
                        content = f.read()
                    context_parts.append(f"\n--- {yaml_file.relative_to(self.memory_bank_path)} ---")
                    context_parts.append(content)
                except Exception:
                    continue
                    
        except Exception as e:
            context_parts.append(f"Error collecting context: {e}")
        
        return "\n".join(context_parts)
    
    def _collect_progress_data(self) -> str:
        """Collect progress data from all sessions and milestones."""
        data_parts = []
        
        try:
            # Collect session states
            data_parts.append("=== SESSION STATES ===")
            sessions_dir = self.memory_bank_path / "work" / "Sessions"
            
            if sessions_dir.exists():
                for feature_dir in sessions_dir.iterdir():
                    if feature_dir.is_dir():
                        state_file = feature_dir / "state.yaml"
                        if state_file.exists():
                            try:
                                with open(state_file, 'r') as f:
                                    state_content = f.read()
                                data_parts.append(f"\n--- {feature_dir.name}/state.yaml ---")
                                data_parts.append(state_content)
                            except Exception:
                                continue
            
            # Collect milestone data
            data_parts.append("\n=== MILESTONES ===")
            if sessions_dir.exists():
                for feature_dir in sessions_dir.iterdir():
                    if feature_dir.is_dir():
                        milestones_dir = feature_dir / "Milestones"
                        if milestones_dir.exists():
                            for milestone_file in milestones_dir.glob("*.md"):
                                try:
                                    with open(milestone_file, 'r') as f:
                                        milestone_content = f.read()
                                    data_parts.append(f"\n--- {milestone_file.relative_to(self.memory_bank_path)} ---")
                                    data_parts.append(milestone_content[:500] + ("..." if len(milestone_content) > 500 else ""))
                                except Exception:
                                    continue
            
            # Add current progress file if exists
            progress_file = self.memory_bank_path / "work" / "progress.md"
            if progress_file.exists():
                try:
                    with open(progress_file, 'r') as f:
                        progress_content = f.read()
                    data_parts.append("\n=== CURRENT PROGRESS ===")
                    data_parts.append(progress_content)
                except Exception:
                    pass
                    
        except Exception as e:
            data_parts.append(f"Error collecting progress data: {e}")
        
        return "\n".join(data_parts)
    
    def _collect_focus_data(self, release: str, component: str) -> str:
        """Collect focus data from progress tracking and implementation status."""
        data_parts = []
        
        try:
            # New release-based structure paths
            progress_dir = self.memory_bank_path / "progress"
            implementation_dir = self.memory_bank_path / "implementation"
            
            data_parts.append(f"=== RELEASE: {release} COMPONENT: {component} ===")
            
            # Progress status for this component
            component_progress = progress_dir / release / f"{component}.md"
            if component_progress.exists():
                try:
                    with open(component_progress, 'r') as f:
                        progress_content = f.read()
                    data_parts.append("--- Component Progress ---")
                    data_parts.append(progress_content)
                except Exception:
                    pass
            
            # Implementation status
            implementation_path = implementation_dir / release / component
            if implementation_path.exists():
                data_parts.append("--- Implementation Structure ---")
                for item in implementation_path.iterdir():
                    if item.is_file():
                        data_parts.append(f"  {item.name}")
                    elif item.is_dir():
                        data_parts.append(f"  {item.name}/")
                        # List first level of subdirectories
                        for subitem in item.iterdir():
                            data_parts.append(f"    {subitem.name}")
            
            # Journal entries from progress directory
            journal_pattern = progress_dir / "project-changelog" / f"*{release}*{component}*.md"
            changelog_files = list(self.memory_bank_path.glob(str(journal_pattern)))
            
            if changelog_files:
                data_parts.append("--- Recent Changelog Entries ---")
                for changelog_file in sorted(changelog_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                    try:
                        with open(changelog_file, 'r') as f:
                            changelog_content = f.read()
                        data_parts.append(f"\n{changelog_file.name}:")
                        data_parts.append(changelog_content[:300] + ("..." if len(changelog_content) > 300 else ""))
                    except Exception:
                        continue
            
            # Check product specifications
            product_spec = self.memory_bank_path / "product" / f"{release}-{component}.md"
            if product_spec.exists():
                try:
                    with open(product_spec, 'r') as f:
                        spec_content = f.read()
                    data_parts.append("--- Product Specification ---")
                    data_parts.append(spec_content[:500] + ("..." if len(spec_content) > 500 else ""))
                except Exception:
                    pass
                        
        except Exception as e:
            data_parts.append(f"Error collecting focus data: {e}")
        
        return "\n".join(data_parts)
    
    def _update_focus_file(self, focus_file: Path, content: str) -> bool:
        """Update focus file with new content."""
        try:
            focus_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if content already has YAML header
            if content.strip().startswith('---'):
                # Content already has YAML header, use as-is
                focus_content = content
            else:
                # Add YAML header
                timestamp = datetime.now()
                focus_content = f"""---
datetime: "{timestamp.isoformat()}"
type: "current_focus"
feature: "{focus_file.parent.name}"
last_updated: "{timestamp.isoformat()}"
---

{content}
"""
            
            with open(focus_file, 'w') as f:
                f.write(focus_content)
            
            return True
        except Exception:
            return False
    
    def _get_directory_tree(self, path: Path, max_depth: int = 3, current_depth: int = 0) -> str:
        """Get directory tree representation."""
        if current_depth >= max_depth:
            return ""
        
        tree_parts = []
        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            
            for item in items:
                indent = "  " * current_depth
                if item.is_dir():
                    tree_parts.append(f"{indent}{item.name}/")
                    if current_depth < max_depth - 1:
                        subtree = self._get_directory_tree(item, max_depth, current_depth + 1)
                        if subtree:
                            tree_parts.append(subtree)
                else:
                    tree_parts.append(f"{indent}{item.name}")
                    
        except Exception:
            pass
        
        return "\n".join(tree_parts)