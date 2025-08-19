---
description: "Switch agent role in Memory-Bank workflow"
---

# Role Switch Command

Switch to specific role for release/component: $ARGUMENTS

## Required Format
`/role "role" "release-name" "component-name"`

**If arguments incomplete**: Ask user to specify all three parameters.

## Available Roles
- **pm**: Project coordination, progress tracking, resource management
- **dev**: Implementation, technical decisions, code development  
- **qa**: Testing, validation, quality assurance
- **owner**: Business requirements, acceptance criteria, prioritization

## Process
1. **Parse Arguments**: Extract role, release, and component from $ARGUMENTS
2. **If Missing**: Ask "Please specify: /role 'role' 'release-name' 'component-name'"
3. **Validate Role**: Ensure role is one of: pm, dev, qa, owner
4. **Execute Switch**: Use `turn-role(release, component, role)` MCP tool
5. **Confirm**: Report successful role switch for the specific component

## Scope Focus
- Role switch applies only to specified release/component
- Document role change in component's journal
- Provide role-specific context for the component

Project: {project_name}