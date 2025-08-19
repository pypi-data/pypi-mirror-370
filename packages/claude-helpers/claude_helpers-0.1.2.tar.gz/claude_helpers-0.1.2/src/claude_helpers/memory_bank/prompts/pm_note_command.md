---
description: "Add journal note for release/component"
---

# Note Command

Add focused journal note for release/component: $ARGUMENTS

## Required Format
`/note "release-name" "component-name" "note content"`

**If arguments incomplete**: Ask user to specify all three parameters.

## Process
1. **Parse Arguments**: Extract release, component, and note content from $ARGUMENTS
2. **If Missing**: Ask "Please specify: /note 'release-name' 'component-name' 'your note here'"
3. **Add Context**: Include current role and timestamp in journal entry
4. **Record**: Use `note-journal(release, component, content, role)` MCP tool
5. **Confirm**: Report successful journal entry for the specific component

## Note Content Guidelines
- Be specific to the component's current work
- Include role context (PM decision, dev update, qa finding, owner input)
- Reference specific epics/tasks if relevant
- Note any blockers or dependencies for this component

## Scope Focus
- Journal entry applies only to specified release/component
- Creates audit trail for component-specific decisions
- Maintains component work history

Project: {project_name}