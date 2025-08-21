---
description: "PM Agent: Check progress status for release/component"
---

# Progress Command

Check component progress and coordinate next steps: $ARGUMENTS

## Required Format
`/progress "release-name" "component-name"`

**If no arguments provided**: Ask Owner to specify release and component.

## PM Agent Process

### 1. Parse Arguments
Extract release and component from $ARGUMENTS:
- If missing: Ask "Please specify: /progress 'release-name' 'component-name'"
- Validate release and component exist in Memory-Bank

### 2. Get Current Status
Use `get-progress(release, component)` MCP tool to check:
- Current development status and completion level
- Active work and assigned sub-agents
- Recent progress updates and milestones
- Identified blockers or issues

### 3. Get Detailed Context
Use `get-focus(release, component)` if needed for:
- Component requirements and objectives
- Dependencies and constraints
- Quality gates and acceptance criteria

### 4. Assess Situation
Analyze progress information to determine:
- **On Track**: Progress meeting expectations and timeline
- **At Risk**: Potential delays or quality concerns
- **Blocked**: Impediments preventing progress
- **Complete**: Ready for next phase or release

### 5. Report to Owner
Provide comprehensive status update:

**Progress Summary**:
- Current completion status and milestones achieved
- Active work being performed by sub-agents
- Recent accomplishments and next steps planned

**Timeline Assessment**:
- Progress against planned timeline
- Risk assessment for on-time delivery
- Revised estimates if needed

**Quality Status**:
- Implementation quality indicators
- Testing progress and results
- Acceptance criteria validation status

**Blockers and Risks**:
- Current impediments and impact assessment
- Mitigation actions being taken
- Owner decisions or input needed

### 6. Coordinate Next Steps
Based on status, take appropriate PM actions:

**If progress is on track**:
- Continue monitoring and support sub-agents
- Prepare for next phase transitions
- Address any emerging risks proactively

**If at risk or blocked**:
- Investigate root causes with sub-agents
- Develop mitigation plans with Owner input
- Adjust timeline or scope if necessary
- Escalate critical issues requiring Owner decisions

### 7. Document Review
Use `note-journal(release, component, status_review, "pm")` to record:
- Progress assessment and findings
- Decisions made and actions taken
- Timeline or scope adjustments
- Follow-up actions scheduled

## Owner Communication Focus

**Clear Status Reporting**:
- Objective assessment of current state
- Realistic timeline and completion estimates
- Specific accomplishments and remaining work
- Clear identification of risks or issues

**Actionable Information**:
- Specific Owner decisions needed
- Resource or priority trade-offs required
- Scope or timeline change recommendations
- Risk mitigation options for consideration

**Proactive Management**:
- Early identification of potential issues
- Preventive actions being taken
- Alternative approaches if problems arise
- Regular communication cadence maintained

Remember: You are providing Owner with comprehensive visibility into component progress while actively managing risks and coordinating sub-agent work to ensure successful delivery.

Project: {project_name}