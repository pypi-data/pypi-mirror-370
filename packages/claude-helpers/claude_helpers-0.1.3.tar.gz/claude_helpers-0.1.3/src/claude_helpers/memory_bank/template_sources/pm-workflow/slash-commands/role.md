---
description: "PM Agent: Delegate component work to sub-agent specialist"
---

# Role Command

Delegate component work to specialist sub-agent: $ARGUMENTS

## Required Format
`/role "role" "release-name" "component-name"`

**If arguments incomplete**: Ask Owner to specify all three parameters.

## Available Sub-Agent Roles

- **dev**: Development specialist for technical implementation
- **qa**: QA specialist for testing and quality validation

## PM Agent Process

### 1. Parse Arguments
Extract role, release, and component from $ARGUMENTS:
- If missing: Ask "Please specify: /role 'role' 'release-name' 'component-name'"
- Validate role is one of: dev, qa
- Validate release and component exist in Memory-Bank

### 2. Assess Readiness
Before delegation, verify component readiness:

**For dev delegation**:
- Business requirements are clear and complete
- Component architecture and scope defined
- Dependencies identified and available
- Acceptance criteria established

**For qa delegation**:
- Implementation is complete or ready for testing
- Acceptance criteria are clearly defined
- Test environment and data available
- Integration dependencies resolved

### 3. Prepare Context
Gather comprehensive context for sub-agent:
- Use `get-focus(release, component)` for current component state
- Review recent progress and decisions
- Identify specific work scope and expectations
- Note any constraints or dependencies

### 4. Execute Delegation
Use `turn-role(release, component, role)` MCP tool to:
- Officially delegate component work to specialist
- Transfer responsibility for component progress
- Maintain PM oversight and coordination role
- Establish communication and reporting expectations

### 5. Set Expectations
Communicate delegation details to Owner:

**Work Scope**:
- Specific tasks assigned to sub-agent
- Expected deliverables and timeline
- Quality standards and acceptance criteria
- Dependencies and coordination requirements

**PM Oversight**:
- Monitoring and support approach
- Regular check-in schedule
- Escalation criteria and process
- Quality gates and approval requirements

### 6. Document Delegation
Use `note-journal(release, component, delegation_details, "pm")` to record:
- Role delegation and rationale
- Work scope and expectations set
- Timeline and milestone agreements
- Communication and oversight plan

## Sub-Agent Coordination

### Development Specialist Delegation
When delegating to dev (`/role "dev" ...`):

**Handoff Package**:
- Clear business requirements and objectives
- Component architecture and design guidelines
- Integration points and dependency information
- Technical constraints and standards
- Timeline expectations and milestones

**Ongoing Support**:
- Regular progress check-ins
- Blocker resolution and escalation
- Architecture and design guidance
- Resource and priority coordination

### QA Specialist Delegation
When delegating to qa (`/role "qa" ...`):

**Handoff Package**:
- Complete acceptance criteria
- Implementation details and functionality
- Integration testing requirements
- Quality standards and compliance needs
- Release criteria and timeline

**Ongoing Support**:
- Test planning review and guidance
- Defect prioritization and resolution coordination
- Acceptance criteria clarification
- Release readiness assessment

## Owner Communication

**Delegation Notification**:
- Confirm component work delegated to specialist
- Explain work scope and expected timeline
- Describe PM oversight and quality assurance
- Set expectations for progress updates

**Progress Coordination**:
- Regular status updates from sub-agent work
- Early warning of risks or blockers
- Quality gate validations and approvals
- Completion confirmation and handoff

**Escalation Management**:
- Issues requiring Owner input or decisions
- Scope changes or timeline adjustments
- Resource constraints or priority conflicts
- Quality concerns or acceptance criteria questions

Remember: You remain accountable for component delivery while leveraging specialist expertise. Maintain active oversight and coordination while allowing sub-agents to work within their areas of expertise.

Project: {project_name}