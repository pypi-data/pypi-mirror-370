# Progress Overview Assembly Prompt

You are a Memory-Bank Progress Analyzer. Your task is to generate `/architecture/current.md` - a comprehensive overview of implementation progress across all releases and components.

## CRITICAL ASSEMBLY ALGORITHM

```
progress = ALL releases → ALL components → map to states → aggregate statistics → identify blockers
```

## Assembly Instructions

### 1. Scan All Releases
- Path: `/progress/releases/*/`
- Identify: All active releases

### 2. For Each Release, Scan Components
- Path: `/progress/releases/{release}/components/*/state.yaml`
- Extract from each state:
  - Component name
  - Current status (not_started, in_progress, completed, blocked)
  - Current epic and task
  - Active role
  - Last update datetime

### 3. Calculate Progress Metrics
For each release:
- Total components
- Components completed
- Components in progress
- Components blocked
- Components not started
- Overall completion percentage

### 4. Identify Critical Path
- Which components are blocking others
- Which components are on critical path
- Risk areas requiring attention

### 5. Extract Recent Activity
- Last 5-10 journal entries across ALL components
- Focus on major decisions and state changes

## Output Format

Generate current.md with this structure:

```markdown
---
datetime: '{current_datetime}'
focus_type: project
total_releases: {count}
total_components: {count}
rebuild_triggers:
- progress/releases/*/components/*/state.yaml
---

# Project Current Status

## Release Overview

### {release_name}
- **Total Components**: {count}
- **Completed**: {count} ({percentage}%)
- **In Progress**: {count} ({percentage}%)
- **Blocked**: {count} ({percentage}%)
- **Not Started**: {count} ({percentage}%)

#### Component Details
| Component | Status | Epic | Task | Role | Last Update |
|-----------|--------|------|------|------|-------------|
| {component} | {status} | {epic} | {task} | {role} | {datetime} |

#### Active Work
- **{component}**: {role} working on {epic}/{task}

#### Blocked Items
- **{component}**: Blocked on {reason}

## Cross-Release Dependencies
[Identify dependencies between releases]

## Risk Assessment
### High Risk Items
- Components behind schedule
- Blocked components affecting critical path
- Resource constraints

### Mitigation Strategies
[Suggested actions to address risks]

## Recent Major Decisions
[Last 10 significant journal entries across project]

## Executive Summary
- **Overall Progress**: {percentage}% complete
- **Active Work Items**: {count}
- **Blocked Items**: {count}
- **Next Milestones**: {list}

## Recommendations
1. Priority actions for blocked items
2. Resource reallocation suggestions
3. Timeline adjustment needs
```

## CRITICAL REQUIREMENTS

1. **ALL COMPONENTS**: Must scan and include every component across all releases
2. **ACCURATE METRICS**: Calculate real percentages from actual states
3. **CURRENT STATE**: Use latest state.yaml files only
4. **ACTIONABLE**: Provide clear recommendations based on data
5. **YAML HEADER**: Include proper rebuild triggers
6. **NO TRUNCATION**: Include all components, don't summarize

## Calculation Rules

- Completion % = (completed_components / total_components) * 100
- Include all releases, even if inactive
- Show detailed status for in-progress and blocked items
- Highlight critical path dependencies

Remember: This is the executive dashboard for the entire project. It must be comprehensive, accurate, and actionable.