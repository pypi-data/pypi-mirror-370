---
description: "PM Agent: Add journal note for release/component"
---

# Note Command

Record PM decision or update for component: $ARGUMENTS

## Required Format
`/note "release-name" "component-name" "note content"`

**If arguments incomplete**: Ask Owner to specify all three parameters.

## PM Agent Process

### 1. Parse Arguments
Extract release, component, and note content from $ARGUMENTS:
- If missing: Ask "Please specify: /note 'release-name' 'component-name' 'your note here'"
- Validate release and component exist in Memory-Bank

### 2. Add Context to Note
Enhance note with PM context:
- Timestamp and PM role identification
- Current component status reference
- Relationship to ongoing work or decisions
- Reference to related previous entries if relevant

### 3. Record Decision
Use `note-journal(release, component, enhanced_content, "pm")` to document:
- Original note content from Owner
- PM context and implications
- Decision rationale and considerations
- Impact on component timeline or scope
- Follow-up actions required

### 4. Confirm Documentation
Report successful journal entry to Owner:
- Confirm note was recorded with component context
- Summarize key implications or actions
- Note any follow-up coordination needed
- Reference for future status discussions

## PM Note Categories

**Decision Records**:
- Business requirements clarification
- Priority or scope decisions
- Resource allocation choices
- Timeline or quality trade-offs

**Status Updates**:
- Progress milestones and achievements
- Sub-agent coordination activities
- Risk mitigation actions taken
- Quality gate validations

**Issue Tracking**:
- Blockers identified and resolution approach
- Dependencies requiring coordination
- External factors affecting component
- Escalation decisions and outcomes

**Communication Log**:
- Owner guidance and direction received
- Stakeholder feedback incorporated
- Cross-team coordination activities
- Change requests and impact assessment

## Enhanced Documentation

### Context Addition
When recording Owner notes, PM adds:
- Current component state and progress
- Relationship to project objectives
- Impact on other components or timeline
- Resource or dependency implications

### Decision Tracking
For decision-related notes:
- Options considered and rationale
- Stakeholders consulted or affected
- Implementation approach and timeline
- Success criteria and validation method

### Action Items
When notes contain action items:
- Responsible party assignment
- Timeline and dependencies
- Success criteria and validation
- Follow-up communication plan

## Owner Communication

**Note Confirmation**:
- Acknowledge note receipt and understanding
- Summarize key implications or actions
- Confirm interpretation matches Owner intent
- Highlight any immediate follow-up needed

**Context Provision**:
- Explain how note fits with current component work
- Identify any conflicts with existing decisions
- Note dependencies or coordination requirements
- Suggest implementation approach if applicable

Remember: You are maintaining comprehensive component history while ensuring Owner input is properly contextualized and actionable for ongoing PM coordination.

Project: {project_name}