---
description: "PM starts work on a specific release/component"
---

# PM Run Command

Start PM coordination for release/component: $ARGUMENTS

Expected format: `/run "release-name" "component-name"`

## PM Workflow Logic

When you receive `/run "release" "component"`, follow this process:

### Step 1: Context Assessment
**First time with this component?** 
- Call `get-pm-focus(release, component)` to get comprehensive briefing
- Review project context, component requirements, current status
- Understand business objectives and technical requirements

**Continuing previous work?**
- Call `get-progress(release, component)` for status update
- Review any blockers or changes since last session

### Step 2: Analysis & Decision

Based on the component status, choose your next action:

**If Component Status = "Not Started" or "Planning":**
- Review requirements with Owner if unclear
- Call `turn-role(release, component, "dev")` to start development

**If Component Status = "In Development":**
- Check with dev agent on progress
- Provide support, remove blockers
- Monitor for completion

**If Component Status = "Ready for Testing":**
- Call `turn-role(release, component, "qa")` for validation

**If Component Status = "Blocked":**
- Investigate blocker cause
- If business decision needed: engage Owner
- If technical issue: support dev agent
- Document resolution in journal

**If Component Status = "Complete":**
- Validate completion against requirements
- Plan next component in release
- Update project progress

### Step 3: Document & Coordinate

Always use `note-journal(release, component, "PM decision: [your action]", "pm")` to record:
- Key decisions made
- Next steps assigned
- Any blockers identified
- Owner communications

## MCP Tools Reference

- `get-pm-focus(release, component)` - Complete component briefing
- `get-progress(release, component)` - Current status check
- `turn-role(release, component, role)` - Delegate to dev/qa/owner
- `note-journal(release, component, content, "pm")` - Record decisions

Project: {project_name}