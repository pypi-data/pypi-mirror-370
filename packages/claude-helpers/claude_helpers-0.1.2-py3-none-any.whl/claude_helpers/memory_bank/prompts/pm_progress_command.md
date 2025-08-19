---
description: "Check progress status for release/component"
---

# Progress Command

Check progress for specific release/component: $ARGUMENTS

## Required Format
`/progress "release-name" "component-name"`

**If no arguments provided**: Ask user to specify release and component.

## Process
1. **Parse Arguments**: Extract release and component from $ARGUMENTS
2. **If Missing**: Ask "Please specify: /progress 'release-name' 'component-name'"
3. **Get Status**: Use `get-progress(release, component)` MCP tool
4. **Get Focus**: Use `get-focus(release, component)` for current work context
5. **Report**: Provide focused status report for this specific component

## Scope Focus
- Only report on the specified release/component
- Include current epic/task context for this component
- Show blockers specific to this component
- Provide component-specific next steps

Project: {project_name}