# Agent Development Flow Rules

## Core Development Philosophy

### 🎯 Iterative Epic-Based Development

**CRITICAL RULE**: Work strictly by epics, then by tasks within each epic. No jumping between epics or skipping tasks.

#### Epic Progression Rules
1. **Complete Epic Before Next**: Epic must be 100% functional before moving to next
2. **All Tasks Required**: Every task in epic must pass acceptance criteria
3. **Integration Testing**: Each epic must integrate with previous epics successfully
4. **No Partial Completion**: Half-working features are worse than no features

#### Task Progression Rules
1. **Sequential Execution**: Tasks within epic executed in dependency order
2. **Atomic Completion**: Each task fully completed before next task
3. **Test-Driven Validation**: All acceptance criteria met before task considered done
4. **Documentation Updated**: Code changes require corresponding documentation updates

### 🔍 Quality Gates

#### Before Starting Any Task
- [ ] Previous task acceptance criteria fully met
- [ ] All tests passing for current epic components  
- [ ] No blocking issues from previous work
- [ ] Clear understanding of task requirements

#### Before Completing Any Task
- [ ] All acceptance criteria verified
- [ ] Test commands executed successfully
- [ ] Code follows project standards
- [ ] Documentation updated (if applicable)
- [ ] Integration with existing components tested

#### Before Moving to Next Epic
- [ ] All epic tasks completed
- [ ] Epic-level integration tests passing
- [ ] Performance benchmarks met
- [ ] Cross-platform compatibility verified
- [ ] Epic fully functional end-to-end

### 🚫 Forbidden Actions

#### Code Quality Violations
- **NO BULLSHIT CODE**: No placeholder, dummy, or "temporary" implementations
- **NO OVER-ENGINEERING**: No features beyond defined requirements
- **NO COPY-PASTE**: Every line must serve the specific purpose
- **NO MAGIC NUMBERS**: All constants clearly defined and documented
- **NO SILENT FAILURES**: All errors must be handled explicitly

#### Development Process Violations
- **NO EPIC JUMPING**: Cannot work on Epic 3 while Epic 2 incomplete
- **NO TASK SKIPPING**: Cannot skip "boring" tasks for "interesting" ones
- **NO PARTIAL COMMITS**: Cannot commit half-working functionality
- **NO ASSUMPTION TESTING**: Cannot assume tests pass without running them

#### Architecture Violations
- **NO TIGHT COUPLING**: Components must be independently testable
- **NO GLOBAL STATE**: Avoid global variables and singleton patterns
- **NO PLATFORM ASSUMPTIONS**: Code must work on Linux AND macOS
- **NO DEPENDENCY BLOAT**: Only essential dependencies allowed

### ✅ Required Development Standards

#### Code Quality Requirements
```python
# GOOD: Clear, simple, testable
def create_question(self, agent_id: str, question: str) -> str:
    """Create HIL question and return message ID."""
    message_id = self._generate_message_id()
    # Implementation...
    return message_id

# BAD: Complex, unclear, untestable
def do_stuff(self, *args, **kwargs):
    # Some magic happens here...
    return "something"
```

#### Architecture Requirements
- **Single Responsibility**: Each class/function has one clear purpose
- **Dependency Injection**: Dependencies passed explicitly, not hidden
- **Interface Segregation**: Small, focused interfaces
- **Clear Boundaries**: Distinct separation between systems

#### Testing Requirements
- **Critical Tests Only**: Test essential functionality, not implementation details
- **Fast Execution**: Tests run quickly for rapid feedback
- **Clear Assertions**: Test failures clearly indicate what broke
- **Platform Coverage**: Tests verify cross-platform compatibility

### 📝 Development Journal Rules

#### Context Tracking in current-context.md
Every development session must update the context file with:

1. **Current Epic/Task**: What specifically is being worked on
2. **Key Decisions**: Architecture choices and reasoning
3. **Discovered Issues**: Problems found and how they were solved
4. **Integration Points**: How current work connects to other components
5. **Next Steps**: What needs to happen next

#### Required Journal Entries
- **Before Starting Work**: Current state and goals
- **After Each Task**: Results, issues, learnings
- **After Each Epic**: Integration status and handoff notes
- **When Blocked**: Detailed problem description and attempted solutions

### 🌐 Communication Standards

#### Code and Documentation Language
- **All Code**: English comments, variable names, function names
- **All Documentation**: English (README, docstrings, error messages)
- **All Commit Messages**: English with clear, descriptive messages
- **All API Interfaces**: English naming and documentation

#### Communication with Human
- **All Conversations**: Russian language
- **Status Reports**: Russian with technical details
- **Problem Discussions**: Russian for better understanding
- **Decision Clarifications**: Russian for nuanced explanations

### 🔧 Technical Implementation Rules

#### Error Handling Standards
```python
# REQUIRED: Explicit error handling with clear messages
try:
    result = api_call()
except APIError as e:
    logger.error(f"API call failed: {e}")
    raise UserFriendlyError(
        f"Unable to connect to transcription service. "
        f"Please check your internet connection and API key."
    ) from e

# FORBIDDEN: Silent failures or generic errors
try:
    result = api_call()
except:
    pass  # BAD: Silent failure
```

#### Configuration Management
- **Environment Variables**: Support for all config overrides
- **Validation**: All config values validated at startup
- **Defaults**: Sensible defaults for all optional settings
- **Documentation**: All config options clearly documented

#### Cross-Platform Compatibility
```python
# REQUIRED: Platform-aware implementation
def get_config_dir() -> Path:
    if platform.system() == 'Darwin':
        return Path.home() / 'Library' / 'Application Support' / 'claude-helpers'
    else:  # Linux
        return Path.home() / '.config' / 'claude-helpers'

# FORBIDDEN: Platform assumptions
config_dir = Path.home() / '.config' / 'claude-helpers'  # BAD: Linux only
```

### 🏗️ Architecture Enforcement

#### Component Boundaries
1. **Audio System**: Independent, no dependencies on other features
2. **Configuration System**: Foundation for all other systems
3. **Dialog System**: Independent UI abstraction
4. **HIL System**: Orchestrates other components
5. **CLI Interface**: Thin layer over core functionality

#### Integration Rules
- **Loose Coupling**: Components communicate through well-defined interfaces
- **Dependency Direction**: Higher-level components depend on lower-level ones
- **No Circular Dependencies**: Clear hierarchy of dependencies
- **Testable Interfaces**: All integration points have test doubles

### 📊 Progress Validation

#### Task Completion Criteria
Each task must demonstrate:
1. **Functional Requirement**: Feature works as specified
2. **Quality Requirement**: Code meets quality standards  
3. **Test Requirement**: All test commands pass
4. **Documentation Requirement**: Usage is documented
5. **Integration Requirement**: Works with existing components

#### Epic Completion Criteria
Each epic must demonstrate:
1. **End-to-End Functionality**: Complete user workflows work
2. **Performance Requirements**: Meets all benchmarks
3. **Error Handling**: Graceful failure in all error scenarios
4. **Cross-Platform**: Verified working on Linux and macOS
5. **User Experience**: Intuitive and helpful for end users

### 🚀 Release Readiness

#### Production Standards
- **Zero Critical Bugs**: No known issues that break core functionality
- **Complete Documentation**: All features documented with examples
- **Performance Verified**: All benchmarks met on target platforms
- **Security Reviewed**: No known vulnerabilities
- **User Tested**: Manual testing completed successfully

#### Maintenance Considerations
- **Clear Code Structure**: Easy for future developers to understand
- **Comprehensive Logging**: Debugging information available when needed
- **Upgrade Path**: Configuration and data migration considered
- **Backward Compatibility**: Changes don't break existing usage

## 🎯 Success Metrics

### Development Velocity
- **Task Completion Rate**: 1-2 tasks per day
- **Epic Integration Time**: < 1 day between epics
- **Bug Discovery Rate**: Issues found early in development
- **Test Coverage**: Critical functionality fully tested

### Code Quality Metrics  
- **Cyclomatic Complexity**: Functions remain simple and testable
- **Documentation Coverage**: All public APIs documented
- **Error Handling**: All failure modes explicitly handled
- **Platform Compatibility**: Zero platform-specific failures

### User Experience Metrics
- **Installation Success Rate**: > 95% on clean systems
- **First-Use Success**: New users can complete setup independently
- **Error Message Quality**: Users understand what went wrong
- **Performance**: Meets all defined response time targets

## ⚠️ Critical Checkpoints

### Daily Development Check
1. Are all previous tasks fully completed?
2. Are current changes tested and working?
3. Is the development journal updated?
4. Are there any blocking issues that need attention?

### Epic Transition Check
1. Does the completed epic work end-to-end?
2. Are all integration points verified?
3. Is the handoff to next epic clear?
4. Are there any architectural debt items to address?

### Release Readiness Check
1. Do all features work as designed?
2. Is documentation complete and accurate?
3. Are all quality gates satisfied?
4. Is the system ready for real-world usage?

---

**REMEMBER**: The goal is not just working software, but **production-ready, maintainable, user-friendly software** that real people can install and use successfully. Every decision should optimize for this outcome.